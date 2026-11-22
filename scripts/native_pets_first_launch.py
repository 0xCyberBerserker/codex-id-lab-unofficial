#!/usr/bin/env python3
"""Generate the local native pet before starting a prepared candidate."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from codex_lab_pet import import_pet


PET_ID = "null-signal-pirate"
SOURCE_SHA = "a816f7488c187ffe8b7f5d58319deb6cfa591f98c219ef06cbaf10d1f9f330db"


def ensure_native_pet(app: Path, profile: Path) -> bool:
    if not profile.is_absolute() or not profile.is_dir():
        raise ValueError("An existing absolute Codex profile is required")
    pets = profile / "pets"
    if pets.is_symlink():
        raise ValueError("The pets directory must not be a symlink")
    entry = pets / PET_ID
    if entry.is_symlink():
        raise ValueError("Custom pet entry must not be a symlink")
    if entry.exists():
        if not (entry / "pet.json").is_file() or not (entry / "spritesheet.png").is_file():
            raise ValueError("Existing custom pet entry is incomplete; it was not changed")
        return False

    helper = app / "share" / "native-pets"
    packaged = helper / "atlas.png"
    if packaged.exists():
        import_pet(profile, packaged, PET_ID, "Pirate Null")
        return True
    record = json.loads((helper / "source.json").read_text(encoding="utf-8"))
    offset, size = record["offset"], record["size"]
    if type(offset) is not int or type(size) is not int or offset < 8 or not 0 < size <= 20 * 1024 * 1024:
        raise ValueError("Invalid source atlas extent")
    with (app / "resources" / "app.asar").open("rb") as archive:
        archive.seek(offset)
        data = archive.read(size)
    if len(data) != size or sha256(data).hexdigest() != SOURCE_SHA:
        raise ValueError("Local Null Signal atlas failed verification")
    with tempfile.TemporaryDirectory(prefix="codex-native-pet-") as temporary:
        source = Path(temporary) / "stock.webp"
        atlas = Path(temporary) / "pirate.png"
        source.write_bytes(data)
        subprocess.run([helper / "export-pirate-sheet", source, atlas], check=True)
        import_pet(profile, atlas, PET_ID, "Pirate Null")
    return True


if __name__ == "__main__":
    try:
        if len(sys.argv) not in (2, 3):
            raise ValueError("Expected APP [PROFILE]")
        if len(sys.argv) == 3:
            profile = Path(sys.argv[2])
        else:
            profile = Path(os.environ.get("CODEX_HOME") or Path.home() / ("." + "codex")).expanduser().resolve()
            profile.mkdir(mode=0o700, parents=True, exist_ok=True)
        ensure_native_pet(Path(sys.argv[1]), profile)
    except (KeyError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"native pets: {error}", file=sys.stderr)
        raise SystemExit(1)
