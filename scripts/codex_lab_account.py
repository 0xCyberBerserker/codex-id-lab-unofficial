"""Read-only app-server transport and account snapshot cache."""

from __future__ import annotations

import json
import os
import selectors
import subprocess
import time
from collections.abc import Callable
from typing import Any


class AccountClient:
    def __init__(self, command: list[str], cancelled: Callable[[], bool] | None = None) -> None:
        self.command = command
        self.cancelled = cancelled or (lambda: False)
        self.process: subprocess.Popen[bytes] | None = None
        self.selector = selectors.DefaultSelector()
        self.buffer = bytearray()
        self.next_id = 1
        self.notification: Callable[[str, dict[str, Any]], None] = lambda method, params: None

    def start(self, timeout: float = 12.0) -> None:
        self.process = subprocess.Popen(
            self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, bufsize=0,
        )
        assert self.process.stdout is not None and self.process.stderr is not None
        for stream in (self.process.stdout, self.process.stderr):
            os.set_blocking(stream.fileno(), False)
            self.selector.register(stream, selectors.EVENT_READ)
        self.request("initialize", {
            "clientInfo": {"name": "codex-id-lab-unofficial", "version": "1.0.0"},
            "capabilities": {"experimentalApi": True},
        }, timeout)
        self.send({"method": "initialized", "params": {}})

    def send(self, message: dict[str, Any]) -> None:
        if not self.process or not self.process.stdin:
            raise RuntimeError("App-server is disconnected")
        try:
            payload = memoryview(json.dumps(message, separators=(",", ":")).encode() + b"\n")
            while payload:
                written = self.process.stdin.write(payload)
                if not written:
                    raise BrokenPipeError("App-server write failed")
                payload = payload[written:]
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise RuntimeError("App-server is disconnected") from error

    def read_messages(self, timeout: float) -> list[dict[str, Any]]:
        if self.cancelled():
            raise RuntimeError("Codex usage read cancelled")
        if not self.process:
            raise RuntimeError("App-server is disconnected")
        messages = []
        for key, _ in self.selector.select(timeout):
            chunk = os.read(key.fd, 65536)
            if not chunk:
                self.selector.unregister(key.fileobj)
                if key.fileobj is self.process.stdout:
                    raise RuntimeError("App-server disconnected")
                continue
            if key.fileobj is self.process.stderr:
                continue  # Drain without retaining potentially sensitive diagnostics.
            self.buffer.extend(chunk)
            if len(self.buffer) > 4 * 1024 * 1024:
                raise RuntimeError("App-server frame exceeds the size limit")
            while b"\n" in self.buffer:
                line, _, remainder = self.buffer.partition(b"\n")
                self.buffer = bytearray(remainder)
                if not line.strip():
                    continue
                try:
                    message = json.loads(line)
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    raise RuntimeError("Invalid app-server JSON frame") from error
                if not isinstance(message, dict):
                    raise RuntimeError("Invalid app-server message")
                method = message.get("method")
                if method in {"account/updated", "account/rateLimits/updated"} and "id" not in message:
                    params = message.get("params")
                    self.notification(method, params if isinstance(params, dict) else {})
                elif "method" in message and "id" in message:
                    self.send({"id": message["id"], "error": {"code": -32601, "message": "Read-only companion does not handle this request"}})
                else:
                    messages.append(message)
        return messages

    def request(self, method: str, params: Any = None, timeout: float = 12.0) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            for message in self.read_messages(min(0.25, max(0, deadline - time.monotonic()))):
                if type(message.get("id")) is not int or message.get("id") != request_id:
                    continue
                if "error" in message:
                    code = (message.get("error") or {}).get("code", "unknown")
                    raise RuntimeError(f"App-server {method} failed (code {code})")
                result = message.get("result")
                if not isinstance(result, dict):
                    raise RuntimeError(f"Invalid app-server result for {method}")
                return result
        raise RuntimeError(f"App-server {method} timed out")

    def close(self) -> None:
        self.selector.close()
        if not self.process:
            return
        if self.process.stdin:
            self.process.stdin.close()
        if self.process.poll() is None:
            self.process.terminate()
        try:
            self.process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=1)
        for stream in (self.process.stdout, self.process.stderr):
            if stream:
                stream.close()


class AccountCache:
    def __init__(self) -> None:
        self.data: dict[str, Any] | None = None
        self.updated_at: float | None = None
        self.stale = True
        self.generation = 0

    def update(self, data: dict[str, Any], now: float | None = None) -> None:
        self.data = data
        self.updated_at = time.monotonic() if now is None else now
        self.stale = False

    def failed(self) -> None:
        self.stale = True

    def account_changed(self) -> None:
        self.generation += 1
        self.data = None
        self.updated_at = None
        self.stale = True

    def needs_refresh(self, now: float | None = None, max_age: float = 45.0) -> bool:
        current = time.monotonic() if now is None else now
        return self.data is None or self.stale or self.updated_at is None or current - self.updated_at >= max_age
