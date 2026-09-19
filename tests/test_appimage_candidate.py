import contextlib
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("appimage_candidate", str(ROOT / "scripts/build-appimage-candidate"))
builder = importlib.util.module_from_spec(importlib.util.spec_from_loader(loader.name, loader))
loader.exec_module(builder)
RUNTIME = os.environ.get("CODEX_LAB_TEST_APPIMAGE_RUNTIME")


class AppImageCandidateTests(unittest.TestCase):
    def test_wrong_runtime_rejected_before_build(self):
        with tempfile.TemporaryDirectory(prefix="codex-lab-appimage-reject-") as temporary:
            runtime = Path(temporary) / "runtime"
            runtime.write_bytes(b"not a verified executable")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                builder.verify_runtime(runtime)

    @unittest.skipUnless(RUNTIME and all(shutil.which(x) for x in ("gpg", "mksquashfs", "unsquashfs", "bwrap")), "Pinned signed runtime fixture and package tools unavailable")
    def test_real_appimage_format_fixture_execution_and_tamper(self):
        with tempfile.TemporaryDirectory(prefix="codex-lab-appimage-fixture-") as temporary:
            app = Path(temporary) / "app"
            (app / "share/icons/hicolor/scalable/apps").mkdir(parents=True)
            (app / "manifest.json").write_text(json.dumps({"buildProfile": "local-candidate", "featureProfile": "base", "packageVersion": "26.1.2-2", "buildRecipeSha256": "a" * 64}))
            (app / "share/codex-lab.desktop").write_text("[Desktop Entry]\nType=Application\nName=Fixture\nExec=AppRun\nIcon=codex-lab\n")
            (app / "share/icons/hicolor/scalable/apps/codex-lab.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
            (app / "ChatGPT").write_text('#!/bin/sh\nprintf "appimage-fixture:%s\\n" "$CODEX_ELECTRON_USER_DATA_PATH"\n')
            (app / "ChatGPT").chmod(0o755)
            image = Path(temporary) / "fixture.AppImage"
            with contextlib.redirect_stdout(io.StringIO()):
                manifest = builder.build(app, Path(RUNTIME), image)
            result = subprocess.run(["bwrap", "--unshare-all", "--die-with-parent", "--new-session", "--ro-bind", "/", "/",
                                     "--tmpfs", "/home", "--tmpfs", "/root", "--tmpfs", "/run", "--tmpfs", "/tmp",
                                     "--ro-bind", str(image), "/tmp/fixture.AppImage", "--proc", "/proc", "--dev", "/dev",
                                     "--clearenv", "--setenv", "PATH", "/usr/bin:/bin", "--setenv", "HOME", "/tmp",
                                     "/tmp/fixture.AppImage", "--appimage-extract-and-run"],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("appimage-fixture:/tmp/.config/codex-id-lab-unofficial/appimage", result.stdout)
            with image.open("ab") as stream:
                stream.write(b"tampered")
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                builder.validate(image, manifest)
            broken = Path(temporary) / "bad.AppImage"
            broken.write_bytes(Path(RUNTIME).read_bytes() + b"not a SquashFS filesystem")
            malformed = dict(manifest, size=broken.stat().st_size, sha256=hashlib.sha256(broken.read_bytes()).hexdigest())
            with self.assertRaises(subprocess.CalledProcessError):
                builder.validate(broken, malformed)
