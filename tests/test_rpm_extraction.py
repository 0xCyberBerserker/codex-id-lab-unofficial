import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("cpio"), "cpio is required")
class RpmExtractionTests(unittest.TestCase):
    def run_pipeline(self, archive, decoder_exit=0):
        line = next(line.strip() for line in
                    (ROOT / "scripts/validate-package").read_text().splitlines()
                    if line.strip().startswith('rpm2cpio "$PACKAGE"'))
        with tempfile.TemporaryDirectory() as temporary:
            directory = pathlib.Path(temporary)
            package = directory / "archive"
            package.write_bytes(archive)
            payload = directory / "payload"
            payload.mkdir()
            decoder = directory / "rpm2cpio"
            decoder.write_text('#!/bin/sh\ndd if="$1" bs=65536 status=none\n'
                               f'exit {decoder_exit}\n')
            decoder.chmod(0o700)
            environment = dict(os.environ, PATH=f"{directory}:/usr/bin:/bin",
                               PACKAGE=str(package), payload=str(payload))
            result = subprocess.run(
                ["bash", "-c", 'set -euo pipefail; fail() { exit 31; }; ' + line],
                env=environment, capture_output=True, timeout=10)
            content = (payload / "fixture").read_bytes() if (payload / "fixture").exists() else None
            return result.returncode, content

    def archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            (pathlib.Path(temporary) / "fixture").write_bytes(b"verified payload")
            result = subprocess.run(["cpio", "-o", "-H", "newc", "--quiet"],
                                    cwd=temporary, input=b"fixture\n",
                                    capture_output=True, check=True, timeout=10)
            return result.stdout

    def test_padding_is_drained_without_false_sigpipe(self):
        self.assertEqual(self.run_pipeline(self.archive() + bytes(1024 * 1024)),
                         (0, b"verified payload"))

    def test_decoder_failure_is_not_hidden(self):
        self.assertEqual(self.run_pipeline(self.archive(), decoder_exit=7)[0], 31)

    def test_invalid_archive_is_not_hidden(self):
        self.assertEqual(self.run_pipeline(b"invalid archive")[0], 31)
