#!/usr/bin/env python3
"""Install an explicitly supplied local PNG as a native, unselected custom pet."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import sys
import zlib


MAX_SHEET_BYTES = 20 * 1024 * 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_version(data: bytes) -> int:
    if not data.startswith(PNG_MAGIC):
        raise ValueError("Expected a PNG sprite sheet.")
    version = None
    seen_data = False
    cursor = len(PNG_MAGIC)
    while cursor + 12 <= len(data):
        length, kind = struct.unpack_from(">I4s", data, cursor)
        end = cursor + 12 + length
        if end > len(data):
            break
        payload = data[cursor + 8:end - 4]
        if zlib.crc32(kind + payload) != struct.unpack_from(">I", data, end - 4)[0]:
            raise ValueError("Corrupt PNG chunk.")
        if kind == b"IHDR":
            if cursor != len(PNG_MAGIC) or length != 13:
                raise ValueError("Invalid PNG image header.")
            width, height = struct.unpack_from(">II", payload)
            version = {1872: 1, 2288: 2}.get(height) if width == 1536 else None
            if version is None:
                raise ValueError("Expected 1536 × 1872 (v1) or 1536 × 2288 (v2).")
        elif version is None:
            raise ValueError("Missing PNG image header.")
        elif kind == b"IDAT" and length:
            seen_data = True
        elif kind == b"IEND":
            if length == 0 and end == len(data) and seen_data:
                return version
            break
        cursor = end
    raise ValueError("Incomplete or invalid PNG sprite sheet.")


def import_pet(profile: Path, sheet: Path, pet_id: str, name: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", pet_id):
        raise ValueError("Use a simple lowercase ID, for example my-pet.")
    name = name.strip()
    if not name or len(name) > 80 or any(not char.isprintable() for char in name):
        raise ValueError("Use a printable name of 1 to 80 characters.")
    if not profile.is_absolute() or not profile.is_dir():
        raise ValueError("Select an existing absolute Codex profile directory.")

    fd = os.open(sheet, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= MAX_SHEET_BYTES:
            raise ValueError("Select a regular PNG file of at most 20 MiB.")
        data = stream.read(MAX_SHEET_BYTES + 1)
    if len(data) > MAX_SHEET_BYTES:
        raise ValueError("The PNG exceeds 20 MiB.")
    version = png_version(data)

    pets = profile / "pets"
    pets.mkdir(mode=0o700, exist_ok=True)
    info = pets.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
        raise ValueError("The pets directory must be a real user-owned directory without shared write access.")
    target = pets / pet_id
    target.mkdir(mode=0o700)
    try:
        with (target / "spritesheet.png").open("xb") as stream:
            stream.write(data)
        manifest = {"displayName": name, "spriteVersionNumber": version, "spritesheetPath": "spritesheet.png"}
        with (target / "manifest.tmp").open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, ensure_ascii=False)
        (target / "manifest.tmp").replace(target / "pet.json")
    except BaseException:
        shutil.rmtree(target)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("spritesheet", type=Path)
    args = parser.parse_args()
    try:
        import_pet(args.profile, args.spritesheet, args.id, args.name)
    except (ValueError, OSError) as error:
        print(f"codex-lab-pet-import: {error}", file=sys.stderr)
        return 1
    print(f"Installed custom:{args.id}; select it in Codex Settings → Pets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
