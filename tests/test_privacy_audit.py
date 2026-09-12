from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PrivacyAuditTests(unittest.TestCase):
    def test_feature_namespace_is_not_a_private_account_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/privacy-audit", root / "scripts/privacy-audit")
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            sample = root / "sample.txt"
            for content, expected in ((".codex-linux/build-info.json .codexLinuxReadAloudLabel", 0), ("~/" + ".co" + "dex/auth.json", 1), ("sk" + "-" + "a" * 32, 1), ("/ho" + "me/example/private", 1)):
                with self.subTest(content_type="fixture"):
                    sample.write_text(content, encoding="utf-8")
                    result = subprocess.run(["bash", str(root / "scripts/privacy-audit")], capture_output=True, text=True)
                    self.assertEqual(result.returncode, expected, result.stderr)
