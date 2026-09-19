#!/usr/bin/env python3
"""Probe only synthetic media in an anonymous, offline native runtime namespace."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import shutil
import subprocess
import sys
import time


class DebugPipe:
    def __init__(self, reader: int, writer: int):
        self.reader, self.writer = reader, writer
        self.buffer = b""
        self.sequence = 0
        self.selector = selectors.DefaultSelector()
        self.selector.register(reader, selectors.EVENT_READ)

    def call(self, method: str, params=None, session=None):
        self.sequence += 1
        message = {"id": self.sequence, "method": method, "params": params or {}}
        if session:
            message["sessionId"] = session
        pending = memoryview(json.dumps(message).encode() + b"\0")
        while pending:
            written = os.write(self.writer, pending)
            if written == 0:
                raise RuntimeError("Native debugging pipe write failed")
            pending = pending[written:]
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            while b"\0" in self.buffer:
                frame, self.buffer = self.buffer.split(b"\0", 1)
                if not frame:
                    continue
                response = json.loads(frame)
                if response.get("id") == self.sequence:
                    if "error" in response:
                        raise RuntimeError(response["error"])
                    return response.get("result", {})
            if not self.selector.select(max(0, deadline - time.monotonic())):
                break
            chunk = os.read(self.reader, 65536)
            if not chunk:
                raise RuntimeError("Native debugging pipe closed")
            self.buffer += chunk
            if len(self.buffer) > 4 * 1024 * 1024:
                raise RuntimeError("Native debugging frame exceeded its bound")
        raise TimeoutError(f"Native debugging timeout: {method}")


EXPRESSION = r"""(async () => {
  const media = navigator.mediaDevices;
  if (!media || typeof media.getUserMedia !== 'function')
    throw new Error('Media capture API unavailable');
  const selectable = devices => devices.filter(device =>
    device.kind === 'audioinput' && device.deviceId.length > 0 && device.deviceId !== 'default').length;
  const settingsAudioInputsBefore = selectable(await media.enumerateDevices());
  const stream = await media.getUserMedia({audio:true, video:false});
  try {
    const devices = await media.enumerateDevices();
    const recorder = new MediaRecorder(stream);
    let bytes = 0;
    recorder.ondataavailable = event => { bytes += event.data.size; };
    await new Promise((resolve, reject) => {
      recorder.onstop = resolve;
      recorder.onerror = reject;
      recorder.start();
      setTimeout(() => recorder.stop(), 500);
    });
    return {
      secureContext: isSecureContext,
      audioInputs: devices.filter(device => device.kind === 'audioinput').length,
      labeledAudioInputs: devices.filter(device => device.kind === 'audioinput' && device.label).length,
      settingsAudioInputsBefore,
      settingsAudioInputsAfter: selectable(devices),
      audioTracks: stream.getAudioTracks().length,
      videoTracks: stream.getVideoTracks().length,
      recorderBytes: bytes,
      syntheticOnly: true
    };
  } finally { stream.getTracks().forEach(track => track.stop()); }
})()"""


def inside_namespace():
    # Actual devices, account state, desktop sockets and network are inaccessible.
    assert not Path("/dev/snd").exists()
    assert not Path("/run/user").exists()
    for directory in ("home", "config", "data", "cache", "codex", "runtime"):
        Path("/tmp", directory).mkdir(mode=0o700)
    display = subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1024x768x24",
                                "-nolisten", "tcp", "-extension", "GLX"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process = None
    try:
        time.sleep(0.5)
        assert display.poll() is None, "Disposable display failed"
        input_reader, input_writer = os.pipe()
        output_reader, output_writer = os.pipe()

        def connect_pipes():
            os.dup2(input_reader, 3)
            os.dup2(output_writer, 4)
            os.set_inheritable(3, True)
            os.set_inheritable(4, True)

        with open("/tmp/native-runtime.log", "wb") as log:
            process = subprocess.Popen([
                "/tmp/candidate/ChatGPT", "--ozone-platform=x11",
                "--disable-dev-shm-usage", "--disable-gpu",
                "--use-fake-device-for-media-stream", "--remote-debugging-pipe",
                "--user-data-dir=/tmp/profile"],
                preexec_fn=connect_pipes, close_fds=False,
                stdin=subprocess.DEVNULL, stdout=log, stderr=log)
            os.close(input_reader)
            os.close(output_writer)
            pipe = DebugPipe(output_reader, input_writer)
            deadline = time.monotonic() + 45
            target = None
            while time.monotonic() < deadline:
                assert process.poll() is None, "Native runtime exited"
                targets = pipe.call("Target.getTargets").get("targetInfos", [])
                target = next((item for item in targets if item.get("type") == "page"
                               and item.get("url", "").startswith("app://")), None)
                if target:
                    break
                time.sleep(0.5)
            assert target is not None, "Trusted application page unavailable"
            session = pipe.call("Target.attachToTarget", {"targetId": target["targetId"],
                                                          "flatten": True})["sessionId"]
            result = pipe.call("Runtime.evaluate", {"expression": EXPRESSION,
                               "awaitPromise": True, "returnByValue": True}, session)
            assert "exceptionDetails" not in result, "Synthetic media evaluation failed"
            value = result.get("result", {}).get("value", {})
            assert value.get("secureContext") is True
            assert value.get("audioInputs", 0) > 0
            assert value.get("labeledAudioInputs", 0) > 0
            assert value.get("settingsAudioInputsAfter", 0) > 0
            assert value.get("audioTracks") == 1
            assert value.get("videoTracks") == 0
            assert value.get("recorderBytes", 0) > 0
            print(json.dumps(value), flush=True)
    except Exception:
        log_path = Path("/tmp/native-runtime.log")
        if log_path.exists():
            print(log_path.read_text(errors="replace")[-2500:], file=sys.stderr)
        raise
    finally:
        for child in (process, display):
            if child and child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)


def main():
    if sys.argv[1:] == ["--inside-namespace"]:
        inside_namespace()
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("app", type=Path)
    parser.add_argument("asar_sha256")
    args = parser.parse_args()
    for prerequisite in ("bwrap", "Xvfb", "timeout"):
        if not shutil.which(prerequisite):
            raise RuntimeError(f"Missing prerequisite: {prerequisite}")
    app = args.app.resolve(strict=True)
    archive = app / "resources/app.asar"
    assert not archive.is_symlink()
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == args.asar_sha256
    assert (app / "ChatGPT").is_file()
    result = subprocess.run([
        "timeout", "-k", "5s", "90s", "bwrap", "--unshare-all",
        "--die-with-parent", "--new-session", "--ro-bind", "/", "/",
        "--tmpfs", "/tmp", "--tmpfs", "/home", "--tmpfs", "/root",
        "--tmpfs", "/run", "--proc", "/proc", "--dev", "/dev",
        "--ro-bind", str(app), "/tmp/candidate",
        "--ro-bind", str(Path(__file__).resolve()), "/tmp/probe.py",
        "--clearenv", "--setenv", "PATH", "/usr/bin:/bin",
        "--setenv", "HOME", "/tmp/home", "--setenv", "DISPLAY", ":99",
        "--setenv", "LANG", "C.UTF-8", "--setenv", "XDG_CONFIG_HOME", "/tmp/config",
        "--setenv", "XDG_DATA_HOME", "/tmp/data", "--setenv", "XDG_CACHE_HOME", "/tmp/cache",
        "--setenv", "CODEX_HOME", "/tmp/codex", "--setenv", "XDG_RUNTIME_DIR", "/tmp/runtime",
        "/usr/bin/python3", "/tmp/probe.py", "--inside-namespace"], timeout=100)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
