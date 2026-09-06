#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "codex-ui-companion.py"
SPEC = importlib.util.spec_from_file_location("codex_ui_companion", MODULE_PATH)
assert SPEC and SPEC.loader
companion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(companion)


class NormalizeAccountDataTest(unittest.TestCase):
    def test_normalizes_limits_without_scanning_sessions(self) -> None:
        usage = {
            "summary": {
                "lifetimeTokens": 1_500_000,
                "currentStreakDays": 3,
                "longestStreakDays": 8,
            },
            "dailyUsageBuckets": [
                {"startDate": "2026-09-04", "tokens": 10},
                {"startDate": "2026-09-05", "tokens": 20},
            ],
        }
        limits = {
            "rateLimitsByLimitId": {
                "codex_bengalfox": {
                    "limitName": "GPT-5.3-Codex-Spark",
                    "primary": {"usedPercent": 5, "windowDurationMins": 300, "resetsAt": 100},
                },
                "codex": {
                    "primary": {"usedPercent": 42, "windowDurationMins": 10080, "resetsAt": 200},
                },
            },
            "rateLimitResetCredits": {"availableCount": 2, "credits": [{"id": "not-exported"}]},
        }

        result = companion.normalize_account_data(usage, limits)

        self.assertEqual(result["limits"][0]["name"], "Codex")
        self.assertEqual(result["activity"]["latest_date"], "2026-09-05")
        self.assertEqual(result["activity"]["latest_tokens"], 20)
        self.assertEqual(result["reset_credits"], 2)
        self.assertNotIn("not-exported", str(result))


class CrashReportTest(unittest.TestCase):
    def test_excludes_core_content_environment_and_command_line(self) -> None:
        event = {
            "COREDUMP_COMM": "example",
            "COREDUMP_PID": "123",
            "COREDUMP_SIGNAL_NAME": "SIGSEGV",
            "COREDUMP_CMDLINE": "example --password top-secret",
            "COREDUMP_ENVIRON": "TOKEN=top-secret",
            "COREDUMP": "top-secret-binary-content",
        }

        report = companion.crash_report(
            event,
            detected_at=datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc),
        )

        self.assertIn("example", report)
        self.assertIn("SIGSEGV", report)
        self.assertNotIn("top-secret", report)
        self.assertNotIn("COREDUMP_CMDLINE", report)


class LocalIntegrationTest(unittest.TestCase):
    def test_finds_user_local_tessdata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"XDG_DATA_HOME": directory}):
                self.assertIsNone(companion.local_tessdata_directory())
                tessdata = Path(directory) / "codex-ui-linux-port" / "tessdata"
                tessdata.mkdir(parents=True)
                (tessdata / "spa.traineddata").write_bytes(b"test")
                self.assertEqual(companion.local_tessdata_directory(), tessdata)

    def test_socket_uses_shared_runtime_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"XDG_RUNTIME_DIR": directory}):
                expected = Path(directory) / "codex-ui-linux-port" / "companion.sock"
                self.assertEqual(companion.companion_socket_path(), str(expected))
                self.assertEqual(expected.parent.stat().st_mode & 0o777, 0o700)

    def test_usage_query_can_be_cancelled(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            command = Path(directory) / "codex"
            command.write_text("#!/bin/sh\nexec sleep 30\n", encoding="utf-8")
            command.chmod(0o755)
            with patch.dict(os.environ, {"CODEXUI_CODEX_COMMAND": str(command)}):
                with self.assertRaisesRegex(RuntimeError, "cancelled"):
                    companion.query_codex_account(timeout=5, cancelled=lambda: True)


if __name__ == "__main__":
    unittest.main()
