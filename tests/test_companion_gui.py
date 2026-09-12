from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

try:
    from websockets.sync.server import unix_serve
except ImportError:
    unix_serve = None


ROOT = Path(__file__).resolve().parents[1]
SERVER = r'''
import json, sys
for line in sys.stdin:
    message = json.loads(line)
    if "id" not in message:
        continue
    if message["method"] == "initialize":
        response = {"id": message["id"], "result": {}}
    elif message["method"] == "account/rateLimits/read":
        response = {"id": message["id"], "result": {"rateLimits": {"limitId": "fixture", "primary": {"usedPercent": 12.5, "windowDurationMins": 17, "resetsAt": None}, "secondary": {"usedPercent": None}}}}
    else:
        response = {"id": message["id"], "error": {"code": -32601}}
    print(json.dumps(response), flush=True)
'''

THEMED_RUNNER = r'''
import os, runpy, sys
from PySide6 import QtWidgets
from PySide6.QtGui import QColor, QPalette
BaseApplication = QtWidgets.QApplication
class TestApplication(BaseApplication):
    def __init__(self, *args):
        super().__init__(*args)
        dark = os.environ["CODEX_LAB_TEST_PALETTE"] == "dark"
        palette = QPalette()
        background, foreground = ("#232629", "#eff0f1") if dark else ("#f2f2f2", "#202020")
        for role in (QPalette.Window, QPalette.Button, QPalette.Base, QPalette.AlternateBase):
            palette.setColor(role, QColor(background))
        for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
            palette.setColor(role, QColor(foreground))
        palette.setColor(QPalette.Highlight, QColor("#3daee9"))
        palette.setColor(QPalette.HighlightedText, QColor("#202020"))
        self.setPalette(palette)
QtWidgets.QApplication = TestApplication
sys.argv = sys.argv[1:]
sys.path.insert(0, os.path.dirname(sys.argv[0]))
runpy.run_path(sys.argv[0], run_name="__main__")
'''


@unittest.skipUnless(importlib.util.find_spec("PySide6"), "PySide6 GUI runtime unavailable")
class CompanionGuiTests(unittest.TestCase):
    @unittest.skipIf(unix_serve is None, "optional python-websockets unavailable")
    def test_actual_panel_attaches_to_private_shared_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            endpoint = str(Path(directory) / "app-server.sock")
            def handler(connection):
                for frame in connection:
                    message = json.loads(frame)
                    if "id" not in message:
                        continue
                    method = message["method"]
                    if method == "initialize":
                        result = {}
                    elif method == "thread/loaded/list":
                        result = {"data": ["private-thread-id"]}
                    elif method == "thread/read":
                        self.assertFalse(message["params"]["includeTurns"])
                        result = {"thread": {"id": "private-thread-id", "status": {"type": "active", "activeFlags": ["waitingOnApproval"]}, "preview": "private conversation"}}
                    elif method == "account/rateLimits/read":
                        result = {"rateLimits": {"primary": {"usedPercent": 12.5}}}
                    else:
                        connection.send(json.dumps({"id": message["id"], "error": {"code": -32601}}))
                        continue
                    connection.send(json.dumps({"id": message["id"], "result": result}))
            with unix_serve(handler, endpoint) as server:
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                env = dict(os.environ, QT_QPA_PLATFORM="offscreen", XDG_RUNTIME_DIR=directory,
                           CODEX_LAB_LANG="es", CODEX_LAB_SHARED_APP_SERVER_SOCKET=endpoint,
                           CODEX_LAB_CODEX_COMMAND="/does-not-exist", CODEX_LAB_TEST_MODE="1",
                           CODEX_LAB_TEST_DISABLE_CRASH_WATCHER="1", CODEX_LAB_TEST_GUI_REPORT="1",
                           CODEX_LAB_TEST_PALETTE="light", CODEX_LAB_TEST_QUIT_MS="600")
                try:
                    result = subprocess.run([sys.executable, "-c", THEMED_RUNNER, str(ROOT / "scripts/codex-lab-companion.py"), "panel"],
                                            env=env, text=True, capture_output=True, timeout=10)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    snapshot = json.loads(result.stdout.strip().splitlines()[-1])
                    self.assertIn("Hilos cargados: 1 · activos: 1 · atención: 1", snapshot["tasks"])
                    self.assertNotIn("private", snapshot["tasks"])
                    self.assertIn("87.5% restante", snapshot["remaining"])
                finally:
                    server.shutdown()
                    thread.join(2)

    def test_actual_feature_selector_isolated_and_localized(self) -> None:
        for locale_name, title in (("en", "Linux features"), ("es", "Funciones Linux"), ("ca", "Funcions Linux")):
            with self.subTest(locale=locale_name), tempfile.TemporaryDirectory() as directory:
                image = Path(directory) / "features.png"
                env = dict(os.environ, QT_QPA_PLATFORM="offscreen", XDG_RUNTIME_DIR=directory, XDG_CONFIG_HOME=directory + "/config", CODEX_LAB_LANG=locale_name, CODEX_LAB_CODEX_COMMAND=shlex.join([sys.executable, "-u", "-c", SERVER]), CODEX_LAB_TEST_MODE="1", CODEX_LAB_TEST_DISABLE_CRASH_WATCHER="1", CODEX_LAB_TEST_FEATURE_REPORT="1", CODEX_LAB_TEST_GUI_IMAGE=str(image), CODEX_LAB_TEST_PALETTE="dark", CODEX_LAB_TEST_QUIT_MS="600")
                result = subprocess.run([sys.executable, "-c", THEMED_RUNNER, str(ROOT / "scripts/codex-lab-companion.py"), "features"], env=env, text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                snapshot = json.loads(result.stdout.strip().splitlines()[-1])
                self.assertTrue(snapshot["visible"])
                self.assertEqual(snapshot["title"], title)
                rows = {row["name"]: row for row in snapshot["features"]}
                self.assertTrue(rows["feature_read-aloud"]["enabled"])
                self.assertTrue(rows["feature_global-dictation"]["enabled"])
                self.assertFalse(rows["feature_computer-use-linux"]["enabled"])
                self.assertFalse(any(row["checked"] for row in rows.values()))
                self.assertGreater(image.stat().st_size, 0)
                self.assertFalse((Path(directory) / "config").exists())

    def test_actual_offscreen_panel_with_isolated_fixture_provider(self) -> None:
        for locale_name, remaining, unknown in (
            ("en", "87.5% remaining", "Unavailable"),
            ("es", "87.5% restante", "No disponible"),
            ("ca", "87.5% restant", "No disponible"),
        ):
            for palette_name in ("light", "dark"):
                with self.subTest(locale=locale_name, palette=palette_name), tempfile.TemporaryDirectory() as directory:
                    image = Path(directory) / "panel.png"
                    env = os.environ.copy()
                    env.update({
                        "QT_QPA_PLATFORM": "offscreen",
                        "XDG_RUNTIME_DIR": directory,
                        "CODEX_LAB_LANG": locale_name,
                        "CODEX_LAB_CODEX_COMMAND": shlex.join([sys.executable, "-u", "-c", SERVER]),
                        "CODEX_LAB_TEST_MODE": "1",
                        "CODEX_LAB_TEST_DISABLE_CRASH_WATCHER": "1",
                        "CODEX_LAB_TEST_GUI_REPORT": "1",
                        "CODEX_LAB_TEST_PALETTE": palette_name,
                        "CODEX_LAB_TEST_GUI_IMAGE": str(image),
                        "CODEX_LAB_TEST_QUIT_MS": "600",
                    })
                    result = subprocess.run(
                        [sys.executable, "-c", THEMED_RUNNER, str(ROOT / "scripts/codex-lab-companion.py"), "panel"],
                        env=env, text=True, capture_output=True, timeout=10,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    snapshot = json.loads(result.stdout.strip().splitlines()[-1])
                    self.assertTrue(snapshot["visible"])
                    self.assertGreaterEqual(snapshot["width"], 360)
                    self.assertLessEqual(snapshot["width"], 420)
                    self.assertIn(remaining, snapshot["remaining"])
                    self.assertIn(unknown, snapshot["remaining"])
                    self.assertEqual(snapshot["locale"], locale_name)
                    self.assertEqual(snapshot["palette"]["window"], "#232629" if palette_name == "dark" else "#f2f2f2")
                    self.assertEqual(snapshot["palette"]["text"], "#eff0f1" if palette_name == "dark" else "#202020")
                    self.assertGreater(image.stat().st_size, 0)
                    if os.environ.get("CODEX_LAB_TEST_KEEP_GUI_IMAGES") == "1":
                        image_dir = ROOT / "build/qa"
                        image_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(image, image_dir / f"companion-{locale_name}-{palette_name}.png")


if __name__ == "__main__":
    unittest.main()
