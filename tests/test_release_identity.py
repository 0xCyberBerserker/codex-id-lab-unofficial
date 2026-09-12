import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "codex-lab-install"
BUILD_PACKAGES = ROOT / "scripts" / "build-packages"
CREATE_MANIFEST = ROOT / "scripts" / "create-release-manifest"
PAYLOAD_DIGEST = ROOT / "scripts" / "payload-digest"
VALIDATOR = ROOT / "scripts" / "validate-release-artifacts"
UPSTREAM_VERSION = "26.1.2"
REVISION = "2"
PACKAGE_VERSION = f"{UPSTREAM_VERSION}-{REVISION}"
PACKAGE_NAME = "codex-id-lab-unofficial"


class ReleaseDecisionTests(unittest.TestCase):
    def decision(self, installed, available, *, explicit=False, force=False):
        env = os.environ.copy()
        env.update(
            {
                "CODEX_LAB_INSTALL_IDENTITY_TEST": "1",
                "CODEX_LAB_TEST_INSTALLED_IDENTITY": installed,
                "CODEX_LAB_TEST_AVAILABLE_IDENTITY": available,
                "CODEX_LAB_TEST_EXPLICIT": "1" if explicit else "0",
                "CODEX_LAB_TEST_FORCE": "1" if force else "0",
            }
        )
        result = subprocess.run([str(INSTALLER)], env=env, text=True, capture_output=True, check=True)
        return result.stdout.strip()

    def test_new_packaging_revision_updates_same_upstream(self):
        self.assertEqual(self.decision("26.1.2-1", "26.1.2-2"), "install")

    def test_identical_tuple_is_current_unless_forced(self):
        self.assertEqual(self.decision("26.1.2-2", "26.1.2-2"), "current")
        self.assertEqual(self.decision("26.1.2-2", "26.1.2-2", force=True), "install")

    def test_downgrade_requires_explicit_version(self):
        self.assertEqual(self.decision("26.2.0-1", "26.1.2-2"), "downgrade-blocked")
        self.assertEqual(self.decision("26.2.0-1", "26.1.2-2", explicit=True), "downgrade")

    def test_debian_and_rpm_order_packaging_revisions(self):
        subprocess.run(["dpkg", "--compare-versions", "26.1.2-2", "gt", "26.1.2-1"], check=True)
        result = subprocess.check_output(
            ["rpm", "--eval", '%{lua:print(rpm.vercmp("26.1.2-2", "26.1.2-1"))}'],
            text=True,
        ).strip()
        self.assertEqual(result, "1")

    @unittest.skipUnless(shutil.which("vercmp"), "Arch vercmp is unavailable in this environment")
    def test_arch_orders_packaging_revisions(self):
        self.assertEqual(
            subprocess.check_output(["vercmp", "26.1.2-2", "26.1.2-1"], text=True).strip(),
            "1",
        )


class PayloadDigestTests(unittest.TestCase):
    def test_aur_output_cannot_make_recipe_hash_self_referential(self):
        with tempfile.TemporaryDirectory(prefix="codex-lab-recipe-fixture-") as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/build-recipe-sha", root / "scripts/build-recipe-sha")
            (root / "packaging/aur").mkdir(parents=True)
            aur = root / "packaging/aur/PKGBUILD"
            aur.write_text("sha256sums=('first')\n")
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            def fingerprint():
                return subprocess.check_output([str(root / "scripts/build-recipe-sha")], text=True).strip()
            first = fingerprint()
            aur.write_text("sha256sums=('final-package-digest')\n")
            self.assertEqual(fingerprint(), first)
            (root / "scripts/build-input").write_text("changed actual build input")
            self.assertNotEqual(fingerprint(), first)

    def test_digest_ignores_timestamps_and_detects_content_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = root / "payload"
            payload.mkdir()
            file_path = payload / "app.bin"
            file_path.write_bytes(b"version one")
            first = subprocess.check_output([str(PAYLOAD_DIGEST), str(payload)], text=True).strip()
            os.utime(file_path, (1_700_000_000, 1_700_000_000))
            second = subprocess.check_output([str(PAYLOAD_DIGEST), str(payload)], text=True).strip()
            self.assertEqual(first, second)
            file_path.write_bytes(b"version two")
            third = subprocess.check_output([str(PAYLOAD_DIGEST), str(payload)], text=True).strip()
            self.assertNotEqual(first, third)


class PackageIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for command in ("bsdtar", "dpkg-deb", "rpmbuild", "rpm"):
            if shutil.which(command) is None:
                raise RuntimeError(f"required test command is missing: {command}")

    def test_package_managers_and_manifests_share_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            pkgroot = base / "pkgroot"
            app = pkgroot / "opt/codex-id-lab-unofficial"
            source_root = base / "source-root"
            upstream = source_root / "usr/lib/chatgpt"
            (source_root / "DEBIAN").mkdir(parents=True)
            (upstream / "resources").mkdir(parents=True)
            (source_root / "DEBIAN/control").write_text(
                "\n".join(
                    (
                        "Package: chatgpt",
                        f"Version: {UPSTREAM_VERSION}",
                        "Architecture: amd64",
                        "Maintainer: fixture",
                        "Description: authenticated source fixture",
                        "",
                    )
                ),
                encoding="utf-8",
            )
            (upstream / "ChatGPT").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            (upstream / "ChatGPT").chmod(0o755)
            (upstream / "resources/codex").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            (upstream / "resources/codex").chmod(0o755)
            (upstream / "resources/app.asar").write_bytes(b"upstream asar fixture")
            shutil.copytree(upstream, app, copy_function=shutil.copy2)
            (app / "bin").mkdir(parents=True)
            (app / "share/systemd/user").mkdir(parents=True)
            (app / "share/icons/hicolor/scalable/apps").mkdir(parents=True)
            (app / "bin/codex-lab").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            (app / "bin/codex-lab").chmod(0o755)
            (app / "bin/codex-lab-tools").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            (app / "bin/codex-lab-tools").chmod(0o755)
            shutil.copy2(INSTALLER, app / "bin/codex-lab-install")
            (app / "bin/codex-lab-update").symlink_to("codex-lab-install")
            (app / "share/codex-lab.desktop").write_text("[Desktop Entry]\nType=Application\nName=Fixture\nExec=codex-lab\n", encoding="utf-8")
            (app / "share/codex-lab-tools.desktop").write_text("[Desktop Entry]\nType=Application\nName=Tools\nExec=codex-lab-tools\n", encoding="utf-8")
            (app / "share/systemd/user/codex-lab-companion.service").write_text("[Service]\nExecStart=/bin/true\n", encoding="utf-8")
            (app / "share/icons/hicolor/scalable/apps/codex-lab.svg").write_text("<svg xmlns=\"http://www.w3.org/2000/svg\"/>\n", encoding="utf-8")

            dist = base / "dist"
            source_name = f"chatgpt_{UPSTREAM_VERSION}_amd64.deb"
            source_package = base / source_name
            subprocess.run(
                ["dpkg-deb", "--build", str(source_root), str(source_package)],
                check=True,
                capture_output=True,
                text=True,
            )
            source_bytes = source_package.read_bytes()
            manifest = {
                "manifestVersion": 2,
                "version": UPSTREAM_VERSION,
                "upstreamVersion": UPSTREAM_VERSION,
                "packageVersion": PACKAGE_VERSION,
                "packagingRevision": int(REVISION),
                "architecture": "x86_64",
                "buildProfile": "release",
                "featureProfile": "base",
                "featureProfileSha256": hashlib.sha256(
                    (ROOT / "packaging/profiles/base.json").read_bytes()
                ).hexdigest(),
                "payloadSha256": subprocess.check_output(
                    [str(PAYLOAD_DIGEST), str(app)], text=True
                ).strip(),
                "commitSha": "a" * 40,
                "sourceArchiveFile": source_name,
                "sourceArchiveUrl": "https://fixture.invalid/chatgpt.deb",
                "sourceArchiveSha256": hashlib.sha256(source_bytes).hexdigest(),
                "buildRecipeSha256": "b" * 64,
                "generatedAtUtc": "2026-09-12T00:00:00Z",
                "sourcePlatform": "linux",
                "packageName": PACKAGE_NAME,
            }
            manifest_path = base / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            env = os.environ.copy()
            env["CODEX_LAB_DIST"] = str(dist)
            subprocess.run(
                [str(BUILD_PACKAGES), str(pkgroot), UPSTREAM_VERSION, REVISION, str(manifest_path)],
                cwd=ROOT,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            shutil.copy2(source_package, dist / source_name)
            subprocess.run(
                [str(CREATE_MANIFEST), str(manifest_path), str(dist), str(dist / "manifest.json")],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            def write_checksums():
                artifacts = sorted(
                    path for path in dist.iterdir() if path.suffix in {".deb", ".rpm", ".zst", ".json"}
                )
                (dist / "checksums.txt").write_text(
                    "".join(
                        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
                        for path in artifacts
                    ),
                    encoding="utf-8",
                )

            write_checksums()

            validation = subprocess.run(
                [str(VALIDATOR), str(dist), UPSTREAM_VERSION, REVISION],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

            arch_package = dist / f"{PACKAGE_NAME}-{UPSTREAM_VERSION}-{REVISION}-x86_64.pkg.tar.zst"
            deb_package = dist / f"{PACKAGE_NAME}_{UPSTREAM_VERSION}-{REVISION}_amd64.deb"
            rpm_package = dist / f"{PACKAGE_NAME}-{UPSTREAM_VERSION}-{REVISION}.x86_64.rpm"
            arch_metadata = subprocess.check_output(
                ["bsdtar", "-xOf", str(arch_package), ".PKGINFO"], text=True
            )
            self.assertIn(f"pkgver = {PACKAGE_VERSION}", arch_metadata)
            self.assertEqual(
                subprocess.check_output(["dpkg-deb", "-f", str(deb_package), "Version"], text=True).strip(),
                PACKAGE_VERSION,
            )
            self.assertEqual(
                subprocess.check_output(
                    ["rpm", "-qp", "--qf", "%{VERSION}-%{RELEASE}", str(rpm_package)],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ),
                PACKAGE_VERSION,
            )
            installed_manifest = subprocess.check_output(
                ["bsdtar", "-xOf", str(arch_package), "opt/codex-id-lab-unofficial/manifest.json"],
                text=True,
            )
            embedded = json.loads(installed_manifest)
            self.assertEqual(embedded["packageVersion"], PACKAGE_VERSION)
            self.assertNotIn("artifacts", embedded)

            external = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(external["artifacts"]), 4)
            arch_record = next(item for item in external["artifacts"] if item["name"] == arch_package.name)
            self.assertEqual(arch_record["sha256"], hashlib.sha256(arch_package.read_bytes()).hexdigest())
            self.assertEqual(arch_record["architecture"], "x86_64")

            original_arch_package = arch_package.read_bytes()
            arch_package.write_bytes(original_arch_package + b"tampered")
            invalid_digest = subprocess.run(
                [str(VALIDATOR), str(dist), UPSTREAM_VERSION, REVISION],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(invalid_digest.returncode, 0)
            self.assertIn("manifest SHA mismatch", invalid_digest.stderr)
            arch_package.write_bytes(original_arch_package)

            original_deb_package = deb_package.read_bytes()
            deb_package.write_bytes(b"arbitrary file with a deb extension")
            subprocess.run(
                [str(CREATE_MANIFEST), str(manifest_path), str(dist), str(dist / "manifest.json")],
                check=True,
                capture_output=True,
                text=True,
            )
            write_checksums()
            invalid_format = subprocess.run(
                [str(VALIDATOR), str(dist), UPSTREAM_VERSION, REVISION],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(invalid_format.returncode, 0)
            self.assertIn("Debian package", invalid_format.stderr)
            deb_package.write_bytes(original_deb_package)
            subprocess.run(
                [str(CREATE_MANIFEST), str(manifest_path), str(dist), str(dist / "manifest.json")],
                check=True,
                capture_output=True,
                text=True,
            )
            write_checksums()
            external = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))

            external["architecture"] = "aarch64"
            (dist / "manifest.json").write_text(json.dumps(external), encoding="utf-8")
            invalid = subprocess.run(
                [str(VALIDATOR), str(dist), UPSTREAM_VERSION, REVISION],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("manifest architecture mismatch", invalid.stderr)

            updated_revision = "3"
            updated_dist = base / "updated-dist"
            updated_manifest = dict(manifest)
            updated_manifest["packagingRevision"] = int(updated_revision)
            updated_manifest["packageVersion"] = f"{UPSTREAM_VERSION}-{updated_revision}"
            updated_manifest_path = base / "updated-manifest.json"
            updated_manifest_path.write_text(json.dumps(updated_manifest), encoding="utf-8")
            env["CODEX_LAB_DIST"] = str(updated_dist)
            subprocess.run(
                [str(BUILD_PACKAGES), str(pkgroot), UPSTREAM_VERSION, updated_revision, str(updated_manifest_path)],
                cwd=ROOT,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            deb_install_root = base / "deb-install-root"
            deb_install_root.mkdir()
            for package_path in (
                deb_package,
                updated_dist / f"{PACKAGE_NAME}_{UPSTREAM_VERSION}-{updated_revision}_amd64.deb",
            ):
                subprocess.run(
                    ["dpkg", "--force-not-root", "--force-depends", f"--root={deb_install_root}", "--install", str(package_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(
                subprocess.check_output(
                    ["dpkg-query", f"--admindir={deb_install_root / 'var/lib/dpkg'}", "--show", "--showformat=${Version}", PACKAGE_NAME],
                    text=True,
                ),
                f"{UPSTREAM_VERSION}-{updated_revision}",
            )
            subprocess.run(
                [str(deb_install_root / f"opt/{PACKAGE_NAME}/bin/codex-lab"), f"--user-data-dir={base / 'smoke-profile'}"],
                check=True,
            )

            def namespace_prefix():
                if os.geteuid() == 0:
                    return []
                if shutil.which("unshare") is None:
                    raise unittest.SkipTest("Disposable chroot requires an available user namespace")
                probe = subprocess.run(
                    ["unshare", "--user", "--map-root-user", "true"], capture_output=True
                )
                if probe.returncode != 0:
                    raise unittest.SkipTest("User namespaces are disabled in this environment")
                return ["unshare", "--user", "--map-root-user"]

            with self.subTest(manager="rpm-disposable-install"):
                rpm_install_root = base / "rpm-install-root"
                rpm_install_root.mkdir()
                rpm_base = namespace_prefix() + ["rpm", "--root", str(rpm_install_root), "--dbpath", "/var/lib/rpm"]
                subprocess.run(rpm_base + ["--initdb"], check=True, capture_output=True, text=True)
                for package_path in (
                    rpm_package,
                    updated_dist / f"{PACKAGE_NAME}-{UPSTREAM_VERSION}-{updated_revision}.x86_64.rpm",
                ):
                    rpm_install = subprocess.run(
                        rpm_base + ["--nodeps", "--noscripts", "--notriggers", "--nosignature", "--upgrade", str(package_path)],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(rpm_install.returncode, 0, rpm_install.stderr)
                self.assertEqual(
                    subprocess.check_output(rpm_base + ["--query", "--qf", "%{VERSION}-%{RELEASE}", PACKAGE_NAME], text=True),
                    f"{UPSTREAM_VERSION}-{updated_revision}",
                )
                subprocess.run(
                    [str(rpm_install_root / f"opt/{PACKAGE_NAME}/bin/codex-lab"), f"--user-data-dir={base / 'rpm-smoke-profile'}"],
                    check=True,
                )

            with self.subTest(manager="arch-disposable-install"):
                if shutil.which("pacman") is None:
                    raise unittest.SkipTest("Arch pacman is unavailable in this environment")
                arch_install_root = base / "arch-install-root"
                for relative in ("var/lib/pacman", "empty-hooks", "cache"):
                    (arch_install_root / relative).mkdir(parents=True, exist_ok=True)
                pacman_config = base / "fixture-pacman.conf"
                pacman_config.write_text(
                    f"[options]\nArchitecture = x86_64\nSigLevel = Never\nHookDir = {arch_install_root / 'empty-hooks'}\nCacheDir = {arch_install_root / 'cache'}\n",
                    encoding="utf-8",
                )
                pacman_base = namespace_prefix() + [
                    "pacman", "--config", str(pacman_config), "--root", str(arch_install_root),
                    "--dbpath", str(arch_install_root / "var/lib/pacman"),
                    "--logfile", str(arch_install_root / "pacman.log"),
                ]
                for package_path in (
                    arch_package,
                    updated_dist / f"{PACKAGE_NAME}-{UPSTREAM_VERSION}-{updated_revision}-x86_64.pkg.tar.zst",
                ):
                    arch_install = subprocess.run(
                        pacman_base + ["--noconfirm", "--nodeps", "--nodeps", "--noscriptlet", "--upgrade", str(package_path)],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(arch_install.returncode, 0, arch_install.stderr)
                self.assertEqual(
                    subprocess.check_output(pacman_base + ["--query", PACKAGE_NAME], text=True).strip(),
                    f"{PACKAGE_NAME} {UPSTREAM_VERSION}-{updated_revision}",
                )
                subprocess.run(
                    [str(arch_install_root / f"opt/{PACKAGE_NAME}/bin/codex-lab"), f"--user-data-dir={base / 'arch-smoke-profile'}"],
                    check=True,
                )


class PublicationContractTests(unittest.TestCase):
    def test_manifest_is_verified_before_installer_uses_identity(self):
        installer = INSTALLER.read_text(encoding="utf-8")
        verification = 'verify_attestation "$tmpdir/$manifest_asset_name"'
        identity = 'remote_upstream_version="$(jq -r'
        self.assertIn(verification, installer)
        self.assertLess(installer.index(verification), installer.index(identity))
        self.assertIn('--signer-workflow "$REPO/.github/workflows/release.yml"', installer)
        self.assertIn("--source-ref refs/heads/main", installer)

    def test_workflow_keeps_published_releases_immutable(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertNotIn("delete-asset", workflow)
        self.assertNotIn("--clobber", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("id-token: write", workflow)
        self.assertIn("attestations: write", workflow)
        self.assertIn("vars.CODEX_LAB_RELEASE_PROMOTION_ENABLED == 'true'", workflow)
        self.assertIn("--metadata-only", workflow)
        self.assertIn("SOURCE_SHA: ${{ steps.source.outputs.source_sha }}", workflow)
        self.assertIn("--download-from-cache", workflow)
        draft = workflow.index("--draft")
        attestation = workflow.index("actions/attest-build-provenance@")
        promotion = workflow.index("--draft=false")
        self.assertLess(draft, attestation)
        self.assertLess(attestation, promotion)


if __name__ == "__main__":
    unittest.main()
