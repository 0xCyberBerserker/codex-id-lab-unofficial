"""Regression tests for the anonymous media probe's bounded debugging transport."""

import importlib.util
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("native_media_probe", Path(__file__).with_name("native_media_probe.py"))
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


class DebugPipeTests(unittest.TestCase):
    def setUp(self):
        self.reader, self.response_writer = os.pipe()
        self.request_reader, self.writer = os.pipe()
        self.pipe = PROBE.DebugPipe(self.reader, self.writer)

    def tearDown(self):
        self.pipe.selector.close()
        for descriptor in (self.reader, self.response_writer, self.request_reader, self.writer):
            if descriptor is not None:
                os.close(descriptor)

    def reply(self, value):
        os.write(self.response_writer, json.dumps(value).encode() + b"\0")

    def test_interleaved_events_buffered_replies_and_partial_writes(self):
        self.reply({"method": "Target.targetCreated", "params": {}})
        self.reply({"id": 1, "result": {"ready": True}})
        self.reply({"id": 2, "result": {"next": True}})
        original_write = os.write
        with patch.object(PROBE.os, "write", side_effect=lambda fd, data: original_write(fd, data[:4])):
            self.assertEqual(self.pipe.call("Runtime.evaluate", {"safe": True}, "fixture"), {"ready": True})
        request = json.loads(os.read(self.request_reader, 4096).rstrip(b"\0"))
        self.assertEqual(request, {"id": 1, "method": "Runtime.evaluate", "params": {"safe": True}, "sessionId": "fixture"})
        self.assertEqual(self.pipe.call("Target.getTargets"), {"next": True})

    def test_protocol_error_fails_closed(self):
        self.reply({"id": 1, "error": {"message": "fixture denied"}})
        with self.assertRaisesRegex(RuntimeError, "fixture denied"):
            self.pipe.call("Runtime.evaluate")

    def test_closed_pipe_fails_closed(self):
        os.close(self.response_writer)
        self.response_writer = None
        with self.assertRaisesRegex(RuntimeError, "pipe closed"):
            self.pipe.call("Target.getTargets")


if __name__ == "__main__":
    unittest.main()
