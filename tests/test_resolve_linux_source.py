import contextlib
import functools
import gzip
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESOLVER = ROOT / "scripts" / "resolve-linux-source"
PACKAGE_FILENAME = "pool/fixture/chatgpt_26.1.2_amd64.deb"


def run(command, **kwargs):
    return subprocess.run(command, check=True, text=True, capture_output=True, **kwargs)


def gpg(home, *arguments):
    return run(
        [
            "gpg",
            "--batch",
            "--homedir",
            str(home),
            "--pinentry-mode",
            "loopback",
            "--passphrase",
            "",
            *arguments,
        ]
    )


def create_signing_key(base, name):
    home = base / name.lower()
    home.mkdir(mode=0o700)
    gpg(home, "--quick-generate-key", f"{name} Fixture <{name.lower()}@fixture.invalid>", "ed25519", "cert", "1d")
    listing = gpg(home, "--with-colons", "--list-secret-keys").stdout
    primary = next(line.split(":")[9] for line in listing.splitlines() if line.startswith("fpr:"))
    gpg(home, "--quick-add-key", primary, "ed25519", "sign", "1d")
    fingerprints = [
        line.split(":")[9]
        for line in gpg(home, "--with-colons", "--list-secret-keys", primary).stdout.splitlines()
        if line.startswith("fpr:")
    ]
    return home, fingerprints[0], fingerprints[1]


def export_key(home, fingerprint):
    return subprocess.check_output(["gpg", "--batch", "--homedir", str(home), "--export", fingerprint])


class RecordingHandler(http.server.SimpleHTTPRequestHandler):
    requests = None

    def do_GET(self):
        self.requests.append(self.path)
        super().do_GET()

    def log_message(self, _format, *_args):
        pass


@contextlib.contextmanager
def serve(directory):
    requests = []
    RecordingHandler.requests = requests
    handler = functools.partial(RecordingHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class ResolveLinuxSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for command in ("curl", "dpkg-deb", "gpg", "gpgv"):
            if shutil.which(command) is None:
                raise RuntimeError(f"required test command is missing: {command}")
        cls.key_directory = tempfile.TemporaryDirectory()
        key_root = Path(cls.key_directory.name)
        cls.authorized_home, cls.authorized_primary, cls.authorized_signer = create_signing_key(
            key_root, "Authorized"
        )
        cls.unauthorized_home, cls.unauthorized_primary, cls.unauthorized_signer = create_signing_key(
            key_root, "Unauthorized"
        )
        cls.authorized_key = export_key(cls.authorized_home, cls.authorized_primary)
        cls.unauthorized_key = export_key(cls.unauthorized_home, cls.unauthorized_primary)

    @classmethod
    def tearDownClass(cls):
        cls.key_directory.cleanup()

    def make_repository(
        self,
        root,
        *,
        filename=PACKAGE_FILENAME,
        package_sha=None,
        package_size=None,
        include_index_checksum=True,
        signer_home=None,
        signer_fingerprint=None,
    ):
        package_path = root / PACKAGE_FILENAME
        package_path.parent.mkdir(parents=True)
        package_root = root / "package-root"
        (package_root / "DEBIAN").mkdir(parents=True)
        (package_root / "DEBIAN" / "control").write_text(
            "Package: chatgpt\n"
            "Version: 26.1.2\n"
            "Architecture: amd64\n"
            "Maintainer: Fixture <fixture@invalid>\n"
            "Description: Resolver fixture\n",
            encoding="utf-8",
        )
        run(["dpkg-deb", "--build", str(package_root), str(package_path)])
        package_bytes = package_path.read_bytes()
        package_sha = package_sha or hashlib.sha256(package_bytes).hexdigest()
        package_size = package_size or str(len(package_bytes))

        packages = (
            "Package: chatgpt\n"
            "Version: 26.1.2\n"
            "Architecture: amd64\n"
            f"Filename: {filename}\n"
            f"SHA256: {package_sha}\n"
            f"Size: {package_size}\n"
        ).encode()
        index_path = root / "dists/stable/main/binary-amd64/Packages.gz"
        index_path.parent.mkdir(parents=True)
        index_path.write_bytes(gzip.compress(packages, mtime=0))

        release = "Origin: Fixture\nSuite: stable\nSHA256:\n"
        if include_index_checksum:
            index_bytes = index_path.read_bytes()
            release += (
                f" {hashlib.sha256(index_bytes).hexdigest()} {len(index_bytes)} "
                "main/binary-amd64/Packages.gz\n"
            )
        release_path = root / "Release"
        release_path.write_text(release, encoding="utf-8")
        inrelease_path = root / "dists/stable/InRelease"
        signer_home = signer_home or self.authorized_home
        signer_fingerprint = signer_fingerprint or self.authorized_signer
        gpg(
            signer_home,
            "--yes",
            "--local-user",
            f"{signer_fingerprint}!",
            "--digest-algo",
            "SHA256",
            "--clearsign",
            "--output",
            str(inrelease_path),
            str(release_path),
        )
        return package_path, index_path, inrelease_path

    def resolve(self, root, trusted_key, expected_fingerprint=None):
        trusted_key_path = root / "trusted.gpg"
        trusted_key_path.write_bytes(trusted_key)
        output = root / "resolved.deb"
        env = os.environ.copy()
        env.update(
            {
                "CODEX_LAB_RESOLVER_TEST_MODE": "1",
                "CODEX_LAB_TEST_TRUSTED_KEY": str(trusted_key_path),
                "CODEX_LAB_TEST_EXPECTED_FINGERPRINT": expected_fingerprint or self.authorized_primary,
            }
        )
        with serve(root) as (base_url, requests):
            env["CODEX_LAB_TEST_REPO_BASE"] = base_url
            result = subprocess.run(
                [str(RESOLVER), "--output", str(output)],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
            )
        return result, output, requests

    def test_authorized_signing_subkey_and_concrete_package_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package_path, _, _ = self.make_repository(root)
            result, output, requests = self.resolve(root, self.authorized_key)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), package_path.read_bytes())
            self.assertIn(f"/{PACKAGE_FILENAME}", requests)
            self.assertFalse(any("/latest/" in request for request in requests))

    def test_key_bundle_cannot_authorize_an_additional_signer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repository(
                root,
                signer_home=self.unauthorized_home,
                signer_fingerprint=self.unauthorized_signer,
            )
            result, output, requests = self.resolve(root, self.authorized_key + self.unauthorized_key)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unauthorized primary key", result.stderr)
            self.assertFalse(output.exists())
            self.assertEqual(requests, [])

    def test_offline_cache_reverifies_signature_and_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repository(root)
            result, output, _ = self.resolve(root, self.authorized_key)
            self.assertEqual(result.returncode, 0, result.stderr)
            proof = json.loads(Path(str(output) + ".verification.json").read_text())
            env = dict(os.environ, CODEX_LAB_RESOLVER_TEST_MODE="1", CODEX_LAB_TEST_TRUSTED_KEY=str(root / "trusted.gpg"), CODEX_LAB_TEST_EXPECTED_FINGERPRINT=self.authorized_primary, CODEX_LAB_TEST_REPO_BASE=proof["sourceUrl"].split("/pool/", 1)[0])
            command = [str(RESOLVER), "--output", str(output), "--verify-cache"]
            cached = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertEqual(cached.returncode, 0, cached.stderr)
            original = output.read_bytes()
            output.write_bytes(original + b"tamper")
            altered = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertNotEqual(altered.returncode, 0)
            self.assertIn("cached source", altered.stderr)
            output.write_bytes(original)
            Path(str(output) + ".InRelease").write_text("invalid signature")
            invalid = subprocess.run(command, env=env, capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("signature verification", invalid.stderr)

    def test_metadata_discovery_does_not_download_package_until_needed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_repository(root)
            trusted_key = root / "trusted.gpg"
            trusted_key.write_bytes(self.authorized_key)
            output = root / "discovered.deb"
            with serve(root) as (base_url, requests):
                env = dict(os.environ, CODEX_LAB_RESOLVER_TEST_MODE="1", CODEX_LAB_TEST_TRUSTED_KEY=str(trusted_key), CODEX_LAB_TEST_EXPECTED_FINGERPRINT=self.authorized_primary, CODEX_LAB_TEST_REPO_BASE=base_url)
                command = [str(RESOLVER), "--output", str(output)]
                discovery = subprocess.run(command + ["--metadata-only"], env=env, capture_output=True, text=True)
                self.assertEqual(discovery.returncode, 0, discovery.stderr)
                self.assertFalse(output.exists())
                self.assertNotIn("/" + PACKAGE_FILENAME, requests)
                cached_download = subprocess.run(command + ["--download-from-cache"], env=env, capture_output=True, text=True)
                self.assertEqual(cached_download.returncode, 0, cached_download.stderr)
                self.assertTrue(output.is_file())
                self.assertEqual(requests.count("/dists/stable/InRelease"), 1)
                self.assertEqual(requests.count("/" + PACKAGE_FILENAME), 1)

    def test_damaged_inrelease_fails_before_package_download(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, _, inrelease_path = self.make_repository(root)
            inrelease_path.write_text(
                inrelease_path.read_text(encoding="utf-8").replace("Origin: Fixture", "Origin: Tampered"),
                encoding="utf-8",
            )
            result, output, requests = self.resolve(root, self.authorized_key)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("signature verification failed", result.stderr)
            self.assertFalse(output.exists())
            self.assertNotIn(f"/{PACKAGE_FILENAME}", requests)

    def test_altered_index_fails_before_package_download(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, index_path, _ = self.make_repository(root)
            index_path.write_bytes(index_path.read_bytes() + b"tampered")
            result, output, requests = self.resolve(root, self.authorized_key)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not match signed metadata", result.stderr)
            self.assertFalse(output.exists())
            self.assertNotIn(f"/{PACKAGE_FILENAME}", requests)

    def test_altered_package_fails_integrity_check(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package_path, _, _ = self.make_repository(root)
            package_path.write_bytes(package_path.read_bytes() + b"tampered")
            result, output, requests = self.resolve(root, self.authorized_key)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("package does not match signed repository metadata", result.stderr)
            self.assertFalse(output.exists())
            self.assertIn(f"/{PACKAGE_FILENAME}", requests)

    def test_missing_index_checksum_and_unsafe_filename_fail(self):
        cases = (
            ({"include_index_checksum": False}, "checksum is missing"),
            ({"filename": "../chatgpt.deb"}, "unsafe package filename"),
        )
        for options, expected_error in cases:
            with self.subTest(expected_error=expected_error), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.make_repository(root, **options)
                result, output, requests = self.resolve(root, self.authorized_key)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_error, result.stderr)
                self.assertFalse(output.exists())
                self.assertNotIn(f"/{PACKAGE_FILENAME}", requests)


if __name__ == "__main__":
    unittest.main()
