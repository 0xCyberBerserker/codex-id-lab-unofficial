import io
from pathlib import Path
import subprocess
import tarfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate-tar-ownership"


class PackageOwnershipTests(unittest.TestCase):
    def test_root_passes_and_user_ownership_fails(self):
        for uid, gid, expected in ((0, 0, 0), (1000, 0, 1), (0, 1000, 1)):
            with self.subTest(uid=uid, gid=gid):
                stream = io.BytesIO()
                with tarfile.open(fileobj=stream, mode="w") as archive:
                    member = tarfile.TarInfo("opt/runtime")
                    member.uid, member.gid, member.size = uid, gid, 7
                    archive.addfile(member, io.BytesIO(b"fixture"))
                result = subprocess.run([str(SCRIPT)], input=stream.getvalue(), capture_output=True)
                self.assertEqual(result.returncode, expected)

    def test_invalid_stream_fails(self):
        result = subprocess.run([str(SCRIPT)], input=b"not a tar", capture_output=True)
        self.assertNotEqual(result.returncode, 0)
