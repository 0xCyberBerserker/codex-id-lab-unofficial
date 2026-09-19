import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("feature_preferences", ROOT / "scripts/codex_lab_features.py")
features = importlib.util.module_from_spec(spec)
spec.loader.exec_module(features)


class FeaturePreferencesTests(unittest.TestCase):
    def test_preferences_preserved_and_requested_differs_from_installed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config/features.json"
            path.parent.mkdir()
            path.write_text(json.dumps({"enabled": [], "settings": {"read-aloud": {"voice": "es"}}, "customPreference": "preserve", "runtimePatches": False}))
            features.save_preferences(["read-aloud"], path)
            saved = features.read_preferences(path)
            self.assertEqual(saved["customPreference"], "preserve")
            self.assertEqual(saved["settings"]["read-aloud"], {"voice": "es"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            states = {state["id"]: state for state in features.feature_states(Path(temporary) / "app", path)}
            self.assertEqual(states["read-aloud"]["state"], "pending-rebuild")
            self.assertFalse(states["read-aloud"]["installed"])
            self.assertEqual(states["global-dictation"]["state"], "disabled")
            self.assertEqual(states["computer-use-linux"]["state"], "incompatible")
            features.save_preferences([], path)
            self.assertEqual(features.read_preferences(path)["settings"], saved["settings"])
            before = path.read_bytes()
            self.assertEqual(features.build_profile(path), {"enabled": [], "settings": {}, "runtimePatches": False})
            self.assertEqual(path.read_bytes(), before)
            features.save_preferences(["read-aloud"], path)
            self.assertEqual(features.build_profile(path)["settings"], {"read-aloud": {"voice": "es"}})
            self.assertNotIn("customPreference", features.build_profile(path))

    def test_invalid_selection_preserves_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "features.json"
            path.write_text('{"enabled":[],"settings":{}}')
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "Unknown"):
                features.save_preferences(["unknown"], path)
            self.assertEqual(path.read_bytes(), before)
