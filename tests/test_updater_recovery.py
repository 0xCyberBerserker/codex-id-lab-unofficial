import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

INSTALLER = Path(__file__).resolve().parents[1] / "scripts/codex-lab-install"


class RecoveryTests(unittest.TestCase):
    def run_fixture(self, **values):
        return subprocess.run(["bash", str(INSTALLER)], env=dict(os.environ, **values),
                              capture_output=True, text=True, timeout=10)

    def test_exact_retained_identity_and_invalid_journal(self):
        with tempfile.TemporaryDirectory() as temporary:
            record = Path(temporary) / "state.json"
            state = {"schemaVersion": 1, "phase": "INSTALLING", "packageVersion": "26.908.40834-3", "sha256": "a" * 64}
            record.write_text(json.dumps(state))
            before = record.read_bytes()
            env = {"CODEX_LAB_RECOVERY_TEST": "1", "CODEX_LAB_TEST_RECOVERY_STATE": str(record)}
            result = self.run_fixture(**env)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout.splitlines(), [state["packageVersion"], state["sha256"]])
            self.assertEqual(record.read_bytes(), before)
            for key, value in (("phase", "INSTALLED"), ("sha256", "bad"), ("packageVersion", "../wrong"), ("schemaVersion", 2)):
                record.write_text(json.dumps(dict(state, **{key: value})))
                self.assertNotEqual(self.run_fixture(**env).returncode, 0)
            record.write_text("{truncated")
            self.assertNotEqual(self.run_fixture(**env).returncode, 0)
            record.write_text(json.dumps(state) + "\n" + json.dumps(state))
            self.assertNotEqual(self.run_fixture(**env).returncode, 0)
            record.unlink(); record.symlink_to(Path(temporary) / "absent")
            self.assertNotEqual(self.run_fixture(**env).returncode, 0)

    def test_changed_authenticated_candidate_rejected(self):
        env = {"CODEX_LAB_RECOVERY_MATCH_TEST": "1", "CODEX_LAB_TEST_RECOVERY_IDENTITY": "26.1.2-3",
               "CODEX_LAB_TEST_RECOVERY_SHA": "a" * 64, "CODEX_LAB_TEST_REMOTE_IDENTITY": "26.1.2-3",
               "CODEX_LAB_TEST_REMOTE_SHA": "a" * 64}
        self.assertEqual(self.run_fixture(**env).returncode, 0)
        self.assertNotEqual(self.run_fixture(**dict(env, CODEX_LAB_TEST_REMOTE_SHA="b" * 64)).returncode, 0)
        self.assertNotEqual(self.run_fixture(**dict(env, CODEX_LAB_TEST_REMOTE_IDENTITY="26.1.2-4")).returncode, 0)

    def test_pacman_lock_preserved_and_no_elevation(self):
        with tempfile.TemporaryDirectory() as temporary:
            lock = Path(temporary) / "pacman/db.lck"
            lock.parent.mkdir(); lock.write_text("owned by native manager")
            env = {"CODEX_LAB_MANAGER_RECOVERY_TEST": "1", "CODEX_LAB_TEST_MANAGER_KIND": "pkg.tar.zst",
                   "CODEX_LAB_TEST_DATABASE_ROOT": temporary}
            self.assertEqual(self.run_fixture(**env).stdout.strip(), "pacman-lock-review-required")
            self.assertEqual(lock.read_text(), "owned by native manager")
            lock.unlink()
            self.assertEqual(self.run_fixture(**env).stdout.strip(), "native-manager-validation-required")

    def test_dpkg_pending_denial_and_timeout_are_not_repaired(self):
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / "dpkg"
            env = {"CODEX_LAB_MANAGER_RECOVERY_TEST": "1", "CODEX_LAB_TEST_MANAGER_KIND": "deb",
                   "CODEX_LAB_TEST_DATABASE_ROOT": temporary, "PATH": temporary + ":/usr/bin"}
            for body, expected in (("echo pending; exit 0", "dpkg-review-required"),
                                   ("exit 1", "dpkg-review-required"),
                                   ("exit 0", "native-manager-validation-required")):
                fake.write_text('#!/bin/sh\n[ "$1" = --audit ] && [ "$2" = codex-id-lab-unofficial ] || exit 7\n' + body + "\n")
                fake.chmod(0o755)
                self.assertEqual(self.run_fixture(**env).stdout.strip(), expected)
            fake_timeout = Path(temporary) / "timeout"
            fake_timeout.write_text("#!/bin/sh\nexit 124\n")
            fake_timeout.chmod(0o755)
            self.assertEqual(self.run_fixture(**env).stdout.strip(), "dpkg-review-required")

    def test_recovery_cannot_silently_select_latest_or_version_override(self):
        for flags in (("--recover", "--check"), ("--recover", "--doctor"), ("--recover", "--version", "26.1.2-3")):
            result = subprocess.run(["bash", str(INSTALLER), *flags], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertIn("target comes from the journal", result.stderr)
