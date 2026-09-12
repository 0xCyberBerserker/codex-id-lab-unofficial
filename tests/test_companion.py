#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "codex-lab-companion.py"
SPEC = importlib.util.spec_from_file_location("codex_ui_companion", MODULE_PATH)
assert SPEC and SPEC.loader
companion = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(MODULE_PATH.parent))
try:
    SPEC.loader.exec_module(companion)
finally:
    sys.path.pop(0)


class NormalizeAccountDataTest(unittest.TestCase):
    def test_missing_invalid_and_decimal_percentages(self) -> None:
        invalid_values = [None, True, "42", -1, 101, float("nan"), float("inf")]
        for value in invalid_values:
            with self.subTest(value=value):
                data = companion.normalize_account_data({}, {"rateLimits": {"limitId": "bucket", "primary": {"usedPercent": value, "windowDurationMins": 17}}})
                self.assertIsNone(data["limits"][0]["used_percent"])
                self.assertIsNone(data["limits"][0]["remaining_percent"])
                self.assertEqual(data["limits"][0]["bucket_id"], "bucket")
                self.assertEqual(data["limits"][0]["window_minutes"], 17)
        data = companion.normalize_account_data({}, {"rateLimits": {"primary": {"usedPercent": 42.25, "resetsAt": 1}}})
        self.assertEqual(data["limits"][0]["used_percent"], 42.25)
        self.assertEqual(data["limits"][0]["remaining_percent"], 57.75)
        self.assertIsNone(data["reset_credits"])
        self.assertEqual(data["tasks"]["status"], "desktop-provider-unavailable")

    def test_secondary_endpoint_failure_does_not_erase_limits(self) -> None:
        with patch.object(companion, "AccountClient") as client_class:
            client = client_class.return_value
            client.request.side_effect = [
                {"rateLimits": {"primary": {"usedPercent": 12.5}}},
                RuntimeError("unsupported secondary endpoint"),
            ]
            with patch.object(companion, "codex_command", return_value=["fixture"]):
                data = companion.query_codex_account()
            self.assertEqual(data["limits"][0]["remaining_percent"], 87.5)
            self.assertEqual(data["usage_status"], "unavailable")
            self.assertIsNone(data["activity"]["lifetime_tokens"])
            client.close.assert_called_once()

    def test_duplicate_account_snapshots_ignore_presentation_timestamps(self) -> None:
        first = companion.normalize_account_data({}, {"rateLimits": {"primary": {"usedPercent": 12.5}}})
        second = dict(first, updated_at=first["updated_at"] + 10)
        self.assertEqual(companion.account_snapshot_signature(first), companion.account_snapshot_signature(second))

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
    def test_locales_have_matching_keys(self) -> None:
        for locale_name in ("es", "ca"):
            self.assertEqual(set(companion.TEXT["en"]), set(companion.TEXT[locale_name]))
            with patch.dict(os.environ, {"CODEX_LAB_LANG": locale_name}):
                self.assertEqual(companion.language(), locale_name)

    def test_popup_geometry_clamps_monitor_edges_in_logical_coordinates(self) -> None:
        self.assertEqual(companion.popup_geometry((0, 0, 1920, 1080), (400, 480), (1919, 1079)), (1520, 599, 400, 480))
        self.assertEqual(companion.popup_geometry((-1280, 0, 1280, 720), (400, 480), (-1270, 10)), (-1280, 0, 400, 480))
        self.assertEqual(companion.popup_geometry((0, 0, 320, 240), (400, 480)), (0, 0, 320, 240))

    def test_finds_user_local_tessdata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"XDG_DATA_HOME": directory}):
                self.assertIsNone(companion.local_tessdata_directory())
                tessdata = Path(directory) / "codex-id-lab-unofficial" / "tessdata"
                tessdata.mkdir(parents=True)
                (tessdata / "spa.traineddata").write_bytes(b"test")
                self.assertEqual(companion.local_tessdata_directory(), tessdata)

    def test_socket_uses_shared_runtime_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"XDG_RUNTIME_DIR": directory}):
                expected = Path(directory) / "codex-id-lab-unofficial" / "companion.sock"
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
