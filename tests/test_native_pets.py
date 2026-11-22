import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from codex_lab_pet import PNG_MAGIC, import_pet


def chunk(kind, payload):
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))


def sprite(width=1536, height=2288):
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return PNG_MAGIC + chunk(b"IHDR", header) + chunk(
        b"IDAT", zlib.compress(bytes((width * 4 + 1) * height))
    ) + chunk(b"IEND", b"")


class NativePetImportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.profile = self.root / "profile"
        self.profile.mkdir()
        self.sheet = self.root / "pet.png"
        self.sheet.write_bytes(sprite())

    def test_native_manifest_is_local_and_does_not_select_or_replace_anything(self):
        import_pet(self.profile, self.sheet, "new-pet", "New pet")
        entry = self.profile / "pets" / "new-pet"
        self.assertEqual((entry / "spritesheet.png").read_bytes(), self.sheet.read_bytes())
        self.assertEqual(json.loads((entry / "pet.json").read_text()), {
            "displayName": "New pet", "spriteVersionNumber": 2, "spritesheetPath": "spritesheet.png",
        })
        self.assertEqual(list(self.profile.iterdir()), [self.profile / "pets"])
        with self.assertRaises(FileExistsError):
            import_pet(self.profile, self.sheet, "new-pet", "Do not overwrite")
        self.assertEqual(json.loads((entry / "pet.json").read_text())["displayName"], "New pet")

    def test_bad_input_never_creates_a_record(self):
        for name, data in (("wrong-size", sprite(12, 12)), ("truncated", self.sheet.read_bytes()[:-1])):
            with self.subTest(name=name):
                invalid = self.root / name
                invalid.write_bytes(data)
                with self.assertRaises(ValueError):
                    import_pet(self.profile, invalid, "new-pet", "New pet")
        with self.assertRaises(ValueError):
            import_pet(self.profile, self.sheet, "../escape", "New pet")
        self.assertFalse((self.profile / "pets").exists())

    def test_rejects_redirected_file_or_pets_directory(self):
        redirected = self.root / "redirected"
        redirected.symlink_to(self.sheet)
        with self.assertRaises(OSError):
            import_pet(self.profile, redirected, "new-pet", "New pet")
        other = self.root / "other"
        other.mkdir()
        (self.profile / "pets").symlink_to(other, target_is_directory=True)
        with self.assertRaises(ValueError):
            import_pet(self.profile, self.sheet, "new-pet", "New pet")
        self.assertEqual(list(other.iterdir()), [])
