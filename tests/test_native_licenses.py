import hashlib, tarfile, json
from pathlib import Path
import importlib.util
import unittest

SPEC = importlib.util.spec_from_file_location("licenses", Path(__file__).parents[1] / "tools/global-dictation/collect-licenses.py")
licenses = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(licenses)

def crate(tmp_path, name="demo", cargo='license = "MIT"', text="MIT text"):
    root = tmp_path / f"{name}-1.0.0"; root.mkdir()
    (root / "Cargo.toml").write_text(f'[package]\nname="{name}"\nversion="1.0.0"\n{cargo}\n')
    (root / "LICENSE").write_text(text)
    out = tmp_path / f"{name}-1.0.0.crate"
    with tarfile.open(out, "w") as t: t.add(root, arcname=root.name)
    return out

def package(path):
    return {"name": path.name.rsplit("-", 2)[0], "version": "1.0.0", "checksum": hashlib.sha256(path.read_bytes()).hexdigest()}

class NativeLicenseTests(unittest.TestCase):
  def test_target_reachability_and_unknown_registry_fail_closed(self):
    root = Path(self._tmpdir.name)
    lock = root / "Cargo.lock"
    source = "registry+https://github.com/rust-lang/crates.io-index"
    lock.write_text(f'[[package]]\nname="demo"\nversion="1.0.0"\nsource="{source}"\nchecksum="hash"\n')
    metadata = root / "metadata.json"
    graph = {"resolve": {"root": "local", "nodes": [
        {"id": "local", "deps": [{"pkg": "registry-demo"}]},
        {"id": "registry-demo", "deps": []},
        {"id": "disconnected", "deps": []}]}, "packages": [
        {"id": "local", "source": None},
        {"id": "registry-demo", "name": "demo", "version": "1.0.0", "source": source}]}
    metadata.write_text(json.dumps(graph))
    self.assertEqual(len(licenses.locked_packages(lock, metadata)), 1)
    graph["resolve"]["nodes"][0]["deps"] = []
    metadata.write_text(json.dumps(graph))
    self.assertEqual(licenses.locked_packages(lock, metadata), [])
    graph["resolve"]["nodes"][0]["deps"] = [{"pkg": "registry-demo"}]
    graph["packages"][1]["version"] = "2.0.0"
    metadata.write_text(json.dumps(graph))
    with self.assertRaisesRegex(ValueError, "absent from lockfile"):
      licenses.locked_packages(lock, metadata)
    graph["resolve"]["root"] = None
    metadata.write_text(json.dumps(graph))
    with self.assertRaisesRegex(ValueError, "resolve.root"):
      licenses.locked_packages(lock, metadata)

  def test_success_and_checksum(self):
    tmp_path = Path(self._tmpdir.name)
    path = crate(tmp_path); result = licenses.collect(package(path), path)
    self.assertEqual(result["license"], "MIT"); self.assertEqual(result["texts"][0][1], "MIT text")
    bad = package(path); bad["checksum"] = "0" * 64
    with self.assertRaisesRegex(ValueError, "checksum"): licenses.collect(bad, path)

  def test_missing_metadata_or_license_fails(self):
    tmp_path = Path(self._tmpdir.name)
    path = crate(tmp_path, cargo=""); p = package(path)
    with self.assertRaisesRegex(ValueError, "license metadata"): licenses.collect(p, path)

  def test_path_traversal_guard(self):
    root = Path("/tmp/license-root").resolve()
    self.assertFalse(licenses.safe_member(Path("../escape"), root))

  def setUp(self):
    import tempfile
    self._tmpdir = tempfile.TemporaryDirectory()

  def tearDown(self):
    self._tmpdir.cleanup()
