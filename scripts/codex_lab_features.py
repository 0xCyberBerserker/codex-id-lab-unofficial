"""Declarative feature preferences; never rebuild or modify an installed runtime."""

import json
import os
from pathlib import Path
import tempfile


def catalog():
    installed = Path(__file__).parent / "feature-catalog.json"
    if installed.is_file():
        return json.loads(installed.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1] / "linux-features"
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(root.glob("*/feature.json"))]


def preferences_path():
    return Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "codex-id-lab-unofficial/feature-preferences.json"


def read_preferences(path=None):
    path = path or preferences_path()
    if not path.exists():
        return {"enabled": [], "settings": {}, "runtimePatches": False}
    result = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(result, dict) or not isinstance(result.get("enabled"), list)
            or not all(isinstance(identifier, str) for identifier in result["enabled"])
            or not isinstance(result.get("settings", {}), dict)):
        raise ValueError("Invalid feature preferences; file preserved")
    return result


def build_profile(path=None):
    """Export only build inputs; retain disabled settings in preferences, not artifacts."""
    preferences = read_preferences(path)
    enabled = sorted(set(preferences["enabled"]))
    known = {feature["id"] for feature in catalog()}
    if not set(enabled).issubset(known):
        raise ValueError("Unknown feature ID; preferences preserved")
    settings = {identifier: value for identifier, value in preferences.get("settings", {}).items()
                if identifier in enabled}
    if not all(isinstance(value, dict) for value in settings.values()):
        raise ValueError("Invalid enabled feature settings; preferences preserved")
    return {"enabled": enabled, "settings": settings, "runtimePatches": bool(enabled)}


def save_preferences(enabled, path=None):
    path = path or preferences_path()
    previous = read_preferences(path)
    known = {feature["id"] for feature in catalog()}
    if not set(enabled).issubset(known):
        raise ValueError("Unknown feature ID; preferences preserved")
    previous.update(enabled=sorted(set(enabled)), runtimePatches=bool(enabled))
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix="features-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(previous, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def feature_states(app_dir=None, path=None):
    requested = set(read_preferences(path)["enabled"])
    app_dir = app_dir or Path(__file__).parent.parent
    info_path = Path(app_dir) / ".codex-linux/build-info.json"
    info = json.loads(info_path.read_text(encoding="utf-8")) if info_path.is_file() else {}
    installed = set(info.get("linuxFeatures", {}).get("enabled", []))
    return [dict(id=feature["id"], title=feature.get("title", feature["id"]),
                 requested=feature["id"] in requested, installed=feature["id"] in installed,
                 state="incompatible" if feature.get("lab", {}).get("blockedReason") else "pending-rebuild" if (feature["id"] in requested) != (feature["id"] in installed) else "enabled" if feature["id"] in installed else "disabled",
                 blocker=feature.get("lab", {}).get("blockedReason"), stability=feature.get("lab", {}).get("stability", "experimental"))
            for feature in catalog()]
