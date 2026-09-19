import fcntl
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


INSTALLER = Path(__file__).resolve().parents[1] / "scripts/codex-lab-install"


class UpdateStateTests(unittest.TestCase):
    def test_profile_change_and_data_downgrade_require_explicit_choices(self):
        with tempfile.TemporaryDirectory(prefix="codex-lab-update-compat-") as temporary:
            installed, remote = Path(temporary) / "installed.json", Path(temporary) / "remote.json"
            installed.write_text(json.dumps({"featureProfile": "experimental", "featureProfileSha256": "a" * 64}))
            remote.write_text(json.dumps({"featureProfile": "base", "featureProfileSha256": "b" * 64}))
            before = installed.read_bytes()
            environment = dict(os.environ, CODEX_LAB_COMPATIBILITY_TEST="1", CODEX_LAB_TEST_INSTALLED_MANIFEST=str(installed), CODEX_LAB_TEST_REMOTE_MANIFEST=str(remote))
            def guard(**values):
                return subprocess.run(["bash", str(INSTALLER)], env=dict(environment, **values), capture_output=True, text=True, check=True).stdout.strip()
            self.assertEqual(guard(), "profile-change-blocked")
            self.assertEqual(guard(CODEX_LAB_TEST_ALLOW_PROFILE="1"), "explicit-profile-change")
            self.assertEqual(guard(CODEX_LAB_TEST_DECISION="downgrade", CODEX_LAB_TEST_ALLOW_PROFILE="1"), "data-downgrade-risk-blocked")
            self.assertEqual(guard(CODEX_LAB_TEST_DECISION="downgrade", CODEX_LAB_TEST_ALLOW_PROFILE="1", CODEX_LAB_TEST_ACCEPT_DATA="1"), "explicit-profile-change")
            self.assertEqual(installed.read_bytes(), before)
            installed.write_text("{truncated")
            self.assertEqual(guard(), "invalid-compatibility-metadata")

    def test_durable_transitions_and_sanitized_status(self):
        with tempfile.TemporaryDirectory(prefix="codex-lab-update-state-") as temporary:
            environment = dict(os.environ, HOME=temporary, XDG_STATE_HOME=temporary + "/state", XDG_CACHE_HOME=temporary + "/cache")
            for phase in ("VERIFIED", "DEFERRED", "INSTALLING", "CANCELLED_OR_FAILED", "INSTALLED"):
                result = subprocess.run(["bash", str(INSTALLER)], env=dict(environment, CODEX_LAB_UPDATE_STATE_TEST="1", CODEX_LAB_TEST_UPDATE_PHASE=phase, CODEX_LAB_TEST_UPDATE_IDENTITY="26.1.2-2", CODEX_LAB_TEST_UPDATE_DIGEST="a" * 64), capture_output=True, text=True, check=True)
                self.assertEqual(json.loads(result.stdout)["phase"], phase)
            directory = Path(environment["XDG_STATE_HOME"]) / "codex-id-lab-unofficial/updater"
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
            self.assertEqual((directory / "state.json").stat().st_mode & 0o777, 0o600)
            events = [json.loads(line) for line in (directory / "events.jsonl").read_text().splitlines()]
            self.assertEqual(len(events), 5)
            status = json.loads(subprocess.run(["bash", str(INSTALLER), "--status"], env=environment, capture_output=True, text=True, check=True).stdout)
            self.assertEqual(status["phase"], "INSTALLED")
            self.assertNotIn("token", status)

    def test_single_owner_and_symlink_rejection(self):
        with tempfile.TemporaryDirectory(prefix="codex-lab-update-lock-") as temporary:
            environment = dict(os.environ, HOME=temporary, XDG_STATE_HOME=temporary + "/state", XDG_CACHE_HOME=temporary + "/cache", CODEX_LAB_UPDATE_STATE_TEST="1", CODEX_LAB_TEST_UPDATE_PHASE="VERIFIED")
            directory = Path(environment["XDG_STATE_HOME"]) / "codex-id-lab-unofficial/updater"
            directory.mkdir(parents=True)
            with (directory / "lock").open("w") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                result = subprocess.run(["bash", str(INSTALLER)], env=environment, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("another updater", result.stderr)
            (directory / "lock").unlink()
            (directory / "lock").symlink_to(Path(temporary) / "protected")
            result = subprocess.run(["bash", str(INSTALLER)], env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(temporary) / "protected").exists())

    def test_status_without_state_is_read_only(self):
        with tempfile.TemporaryDirectory(prefix="codex-lab-update-empty-") as temporary:
            environment = dict(os.environ, HOME=temporary, XDG_STATE_HOME=temporary + "/state")
            result = subprocess.run(["bash", str(INSTALLER), "--status"], env=environment, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)["phase"], "NONE")
            self.assertFalse((Path(temporary) / "state").exists())
