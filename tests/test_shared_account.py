import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from codex_lab_account import SharedAccountClient, TaskAttention, read_loaded_tasks, task_status
sys.path.pop(0)

try:
    from websockets.sync.server import unix_serve
except ImportError:
    unix_serve = None


class TaskSnapshotTests(unittest.TestCase):
    def test_attention_notifications_deduplicate_transition_and_disconnect(self):
        store = TaskAttention()
        attention = {"status": "loaded-thread-snapshot", "items": [{"id": "fixture", "needs_attention": True}]}
        self.assertEqual(store.update(attention), 1)
        self.assertEqual(store.update(attention), 0)
        self.assertEqual(store.update({"status": "unavailable"}), 0)
        self.assertEqual(store.update(attention), 0)
        self.assertEqual(store.update({"status": "loaded-thread-snapshot", "items": []}), 0)
        self.assertEqual(store.update(attention), 0)
        self.assertEqual(store.update({"status": "loaded-thread-snapshot", "items": [{"id": "fixture", "needs_attention": False}]}), 0)
        self.assertEqual(store.update(attention), 1)
        self.assertEqual(TaskAttention().update(attention), 1)

    def test_metadata_allowlist_deduplication_and_attention(self):
        client = Mock()
        client.request.side_effect = [
            {"data": ["fixture", "fixture"], "nextCursor": "more"},
            {"thread": {"id": "fixture", "status": {"type": "active", "activeFlags": ["waitingOnApproval"]},
                        "preview": "private conversation", "cwd": "/private", "turns": ["private"]}},
        ]
        result = read_loaded_tasks(client)
        self.assertEqual(result["items"], [{"id": "fixture", "type": "active", "needs_attention": True}])
        self.assertTrue(result["truncated"])
        self.assertNotIn("private", json.dumps(result))
        self.assertEqual(client.request.call_args.args[0], "thread/read")
        self.assertEqual(client.request.call_args.args[1], {"threadId": "fixture", "includeTurns": False})

    def test_drift_and_wrong_target_fail_closed(self):
        for value in (None, {"type": "newState"}, {"type": "active", "activeFlags": ["newPermission"]}):
            with self.assertRaises(RuntimeError):
                task_status(value)
        client = Mock()
        client.request.side_effect = [{"data": ["fixture"]}, {"thread": {"id": "other", "status": {"type": "idle"}}}]
        with self.assertRaises(RuntimeError):
            read_loaded_tasks(client)


@unittest.skipIf(unix_serve is None, "optional python-websockets unavailable")
class SharedTransportTests(unittest.TestCase):
    def test_unix_fragmentation_notifications_denied_requests_and_no_authority_kill(self):
        with tempfile.TemporaryDirectory() as temporary:
            endpoint = str(Path(temporary) / "app-server.sock")
            denied = threading.Event()
            def handler(connection):
                initialized = False
                for frame in connection:
                    message = json.loads(frame)
                    method = message.get("method")
                    if "error" in message:
                        if message["id"] == "sensitive" and message["error"]["code"] == -32601:
                            denied.set()
                        continue
                    if method == "initialized":
                        initialized = True
                        continue
                    if method == "initialize":
                        result = {"userAgent": "fixture"}
                    elif initialized and method == "thread/loaded/list":
                        connection.send(json.dumps({"method": "thread/status/changed", "params": {"threadId": "fixture", "status": {"type": "idle"}}}))
                        connection.send(json.dumps({"id": "sensitive", "method": "item/commandExecution/requestApproval", "params": {"private": "discard"}}))
                        result = {"data": []}
                    else:
                        result = {"alive": True}
                    payload = json.dumps({"id": message["id"], "result": result})
                    connection.send([payload[:9], payload[9:]])
            with unix_serve(handler, endpoint) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                client = SharedAccountClient(endpoint)
                notifications = []
                client.notification = lambda method, params: notifications.append(method)
                try:
                    client.start(2)
                    self.assertEqual(read_loaded_tasks(client)["items"], [])
                    self.assertTrue(denied.wait(1))
                    self.assertEqual(notifications, ["thread/status/changed"])
                    self.assertIsNone(client.process)
                finally:
                    client.close()
                second = SharedAccountClient(endpoint)
                try:
                    second.start(2)
                    self.assertEqual(second.request("fixture/alive", timeout=2), {"alive": True})
                finally:
                    second.close()
                server.shutdown()
                thread.join(2)

    def test_unsafe_or_missing_endpoint_never_spawns_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "socket"
            path.write_text("not a socket")
            for target in (str(path), str(path.with_name("missing")), "relative.sock"):
                client = SharedAccountClient(target)
                try:
                    with self.assertRaisesRegex(RuntimeError, "unavailable or unsafe"):
                        client.start(1)
                    self.assertIsNone(client.process)
                finally:
                    client.close()

    @unittest.skipUnless(os.environ.get("CODEX_LAB_TEST_NATIVE_ISOLATED") == "1", "real native CLI requires explicit isolated runner")
    def test_real_native_anonymous_initialize_and_loaded_threads(self):
        with tempfile.TemporaryDirectory() as temporary:
            endpoint = Path(temporary) / "app-server.sock"
            profile = Path(temporary) / "codex"
            profile.mkdir(mode=0o700)
            process = subprocess.Popen([os.environ["CODEX_LAB_TEST_NATIVE_CLI"], "app-server", "--listen", f"unix://{endpoint}"],
                                       env=dict(os.environ, CODEX_HOME=str(profile)),
                                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            client = SharedAccountClient(str(endpoint))
            try:
                deadline = time.monotonic() + 5
                while not endpoint.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                client.start(3)
                self.assertEqual(read_loaded_tasks(client), {"status": "loaded-thread-snapshot", "items": [], "truncated": False})
                client.close()
                self.assertIsNone(process.poll())
            finally:
                client.close()
                process.terminate()
                try:
                    process.wait(2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(2)
