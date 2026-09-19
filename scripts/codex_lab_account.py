"""Read-only app-server transport and account snapshot cache."""

from __future__ import annotations

import json
import os
from pathlib import Path
import selectors
import stat
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
        self.initialize(timeout)

    def initialize(self, timeout: float) -> None:
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
                if self.dispatch(message):
                    messages.append(message)
        return messages

    def dispatch(self, message: dict[str, Any]) -> bool:
        method = message.get("method")
        if method in {"account/updated", "account/rateLimits/updated", "thread/status/changed"} and "id" not in message:
            params = message.get("params")
            self.notification(method, params if isinstance(params, dict) else {})
        elif "method" in message and "id" in message:
            self.send({"id": message["id"], "error": {"code": -32601, "message": "Read-only companion does not handle this request"}})
        else:
            return True
        return False

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


class SharedAccountClient(AccountClient):
    """Attach to one explicitly selected authority; never spawn or stop it."""

    def __init__(self, socket_path: str, cancelled: Callable[[], bool] | None = None) -> None:
        super().__init__([], cancelled)
        self.socket_path = socket_path
        self.connection: Any = None

    def start(self, timeout: float = 12.0) -> None:
        path = Path(self.socket_path)
        try:
            if not path.is_absolute() or path.resolve(strict=True) != path or len(os.fsencode(path)) > 107:
                raise ValueError("Invalid socket path")
            parent, endpoint = path.parent.stat(), path.lstat()
            if (parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) != 0o700 or
                    endpoint.st_uid != os.getuid() or not stat.S_ISSOCK(endpoint.st_mode)):
                raise ValueError("Unsafe socket ownership or directory")
        except (OSError, ValueError) as error:
            raise RuntimeError("Shared app-server socket is unavailable or unsafe") from error
        try:
            from websockets.sync.client import unix_connect
        except ImportError as error:
            raise RuntimeError("Shared bridge requires the optional python-websockets dependency") from error
        try:
            self.connection = unix_connect(
                str(path), uri="ws://localhost/rpc", proxy=None, compression=None,
                open_timeout=timeout, close_timeout=1, max_size=4 * 1024 * 1024, max_queue=16,
            )
            self.initialize(timeout)
        except Exception as error:
            self.close()
            raise RuntimeError("Shared app-server initialization failed") from error

    def send(self, message: dict[str, Any]) -> None:
        if not self.connection:
            raise RuntimeError("Shared app-server is disconnected")
        try:
            self.connection.send(json.dumps(message, separators=(",", ":")))
        except Exception as error:
            raise RuntimeError("Shared app-server is disconnected") from error

    def read_messages(self, timeout: float) -> list[dict[str, Any]]:
        if self.cancelled():
            raise RuntimeError("Codex usage read cancelled")
        if not self.connection:
            raise RuntimeError("Shared app-server is disconnected")
        try:
            frame = self.connection.recv(timeout=timeout)
        except TimeoutError:
            return []
        except Exception as error:
            raise RuntimeError("Shared app-server disconnected") from error
        try:
            message = json.loads(frame)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RuntimeError("Invalid shared app-server JSON frame") from error
        if not isinstance(message, dict):
            raise RuntimeError("Invalid shared app-server message")
        return [message] if self.dispatch(message) else []

    def close(self) -> None:
        self.selector.close()
        if self.connection:
            self.connection.close()
            self.connection = None


def task_status(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("type") not in {"idle", "active", "systemError", "notLoaded"}:
        raise RuntimeError("Unsupported thread status contract")
    flags = value.get("activeFlags", [])
    if not isinstance(flags, list) or any(flag not in {"waitingOnApproval", "waitingOnUserInput"} for flag in flags):
        raise RuntimeError("Unsupported thread attention contract")
    return {"type": value["type"], "needs_attention": value["type"] == "systemError" or bool(flags)}


def read_loaded_tasks(client: AccountClient, maximum: int = 32) -> dict[str, Any]:
    """Bounded metadata-only snapshot, not a list of all desktop activity."""
    if type(maximum) is not int or not 1 <= maximum <= 32:
        raise ValueError("Loaded-thread snapshot limit must be between 1 and 32")
    deadline = time.monotonic() + 5
    listing = client.request("thread/loaded/list", {"limit": maximum}, timeout=3)
    identifiers = listing.get("data")
    if not isinstance(identifiers, list) or any(not isinstance(item, str) or not item or len(item) > 256 for item in identifiers):
        raise RuntimeError("Unsupported loaded-thread contract")
    items = []
    for identifier in dict.fromkeys(identifiers[:maximum]):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("Loaded-thread snapshot timed out")
        result = client.request("thread/read", {"threadId": identifier, "includeTurns": False}, timeout=min(2, remaining))
        thread = result.get("thread")
        if not isinstance(thread, dict) or thread.get("id") != identifier:
            raise RuntimeError("Unsupported thread summary contract")
        items.append({"id": identifier, **task_status(thread.get("status"))})
    return {"status": "loaded-thread-snapshot", "items": items, "truncated": len(identifiers) > maximum or bool(listing.get("nextCursor"))}


class TaskAttention:
    """In-memory task transitions; unavailable snapshots do not invent resolution."""
    def __init__(self) -> None:
        self.previous: dict[str, bool] = {}

    def update(self, tasks: dict[str, Any]) -> int:
        if tasks.get("status") != "loaded-thread-snapshot":
            return 0
        current = {item["id"]: item["needs_attention"] for item in tasks["items"]}
        count = sum(needed and not self.previous.get(identifier, False) for identifier, needed in current.items())
        # ponytail: retain unseen tasks across bounded snapshots; account changes clear the store.
        self.previous.update(current)
        # ponytail: extreme churn resets dedup at 1024 entries; no private IDs are persisted.
        if len(self.previous) > 1024:
            self.previous = current
        return count
