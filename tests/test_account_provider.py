from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
try:
    from codex_lab_account import AccountCache, AccountClient
finally:
    sys.path.pop(0)


SERVER = r'''
import json, os, sys, time
initialized = False
for line in sys.stdin.buffer:
    message = json.loads(line)
    method = message.get("method")
    if method == "initialized":
        initialized = True
        continue
    if method == "initialize":
        response = {"id": message["id"], "result": {"userAgent": "fixture"}}
        payload = (json.dumps(response) + "\n").encode()
        os.write(1, payload[:9])
        os.write(2, b"diagnostic discarded\n" * 15000)
        time.sleep(0.02)
        os.write(1, payload[9:])
        continue
    if not initialized:
        response = {"id": message["id"], "error": {"code": -32000}}
    elif method == "account/rateLimits/read":
        quota = {"rateLimits": {"limitId": "fixture", "primary": {"usedPercent": 12.5, "windowDurationMins": 17}}}
        notification = {"method": "account/rateLimits/updated", "params": quota}
        os.write(1, (json.dumps(notification) + "\n" + json.dumps(notification) + "\n").encode())
        response = {"id": message["id"], "result": quota}
    else:
        response = {"id": message["id"], "error": {"code": -32601, "message": "private error must not be surfaced"}}
    os.write(1, (json.dumps(response) + "\n").encode())
'''


class TransportTests(unittest.TestCase):
    def test_fragmented_frames_interleaved_notifications_and_stderr(self) -> None:
        client = AccountClient([sys.executable, "-u", "-c", SERVER])
        notifications = []
        client.notification = lambda method, params: notifications.append((method, params))
        try:
            client.start(timeout=3)
            result = client.request("account/rateLimits/read", timeout=3)
            self.assertEqual(result["rateLimits"]["primary"]["usedPercent"], 12.5)
            self.assertEqual(len(notifications), 2)
            with self.assertRaisesRegex(RuntimeError, "account/usage/read failed.*-32601") as error:
                client.request("account/usage/read", timeout=3)
            self.assertNotIn("private error", str(error.exception))
        finally:
            client.close()

    def test_disconnect_is_explicit(self) -> None:
        client = AccountClient([sys.executable, "-u", "-c", "pass"])
        try:
            with self.assertRaisesRegex(RuntimeError, "disconnect"):
                client.start(timeout=1)
        finally:
            client.close()


class CacheTests(unittest.TestCase):
    def test_disconnect_preserves_stale_data_and_account_change_invalidates(self) -> None:
        cache = AccountCache()
        data = {"limits": [{"remaining_percent": 17.25, "resets_at": 1}]}
        cache.update(data, now=10)
        self.assertFalse(cache.needs_refresh(now=54))
        self.assertTrue(cache.needs_refresh(now=55))
        cache.failed()
        self.assertEqual(cache.data, data)
        self.assertTrue(cache.stale)
        self.assertEqual(cache.data["limits"][0]["remaining_percent"], 17.25)
        cache.account_changed()
        self.assertIsNone(cache.data)
        self.assertIsNone(cache.updated_at)
        self.assertTrue(cache.needs_refresh(now=56))


if __name__ == "__main__":
    unittest.main()
