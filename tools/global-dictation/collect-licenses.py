#!/usr/bin/env python3
"""Collect locked Cargo registry license texts from a reviewed local cache."""
import argparse, hashlib, json, re, tarfile
from pathlib import Path
import tomllib

LICENSE_NAMES = re.compile(r"(?:^|/)(?:COPYING|LICENSE|NOTICE)(?:[-_.].*)?$", re.I)
MAX_CRATE = 64 * 1024 * 1024
MAX_TEXT = 4 * 1024 * 1024

def locked_packages(lockfile, metadata=None):
    data = tomllib.loads(Path(lockfile).read_text(encoding="utf-8"))
    packages = [p for p in data["package"] if p.get("source", "").startswith("registry+")]
    if metadata:
        graph = json.loads(Path(metadata).read_text(encoding="utf-8"))
        root = graph.get("resolve", {}).get("root")
        if not root: raise ValueError("metadata resolve.root is required")
        nodes = {n["id"]: n for n in graph["resolve"]["nodes"]}
        reachable, todo = set(), [root]
        while todo:
            node_id = todo.pop()
            if node_id in reachable: continue
            if node_id not in nodes: raise ValueError(f"metadata references unknown node {node_id}")
            reachable.add(node_id)
            node = nodes[node_id]
            if "deps" in node:
                todo.extend(d.get("pkg") or d.get("id") for d in node["deps"])
            else:
                todo.extend(node.get("dependencies", []))
        graph_packages = {p["id"]: p for p in graph.get("packages", [])}
        lock_ids = {(p["source"], p["name"], p["version"]): p for p in packages}
        selected = set()
        for node_id in reachable:
            gp = graph_packages.get(node_id)
            if not gp: raise ValueError(f"metadata package missing for reachable node: {node_id}")
            if (gp.get("source") or "").startswith("registry+"):
                identity = (gp["source"], gp["name"], gp["version"])
                if identity not in lock_ids:
                    raise ValueError(f"reachable registry package absent from lockfile: {node_id}")
                selected.add(identity)
        packages = [p for identity, p in lock_ids.items() if identity in selected]
    return packages

def crate_path(cache, package):
    matches = sorted(Path(cache).rglob(f"{package['name']}-{package['version']}.crate"))
    if len(matches) != 1:
        raise ValueError(f"expected one crate for {package['name']} {package['version']}, found {len(matches)}")
    return matches[0]

def safe_member(member, root):
    target = (root / member).resolve()
    return target == root or root in target.parents

def collect(package, crate):
    if crate.stat().st_size > MAX_CRATE:
        raise ValueError(f"crate exceeds size bound: {crate.name}")
    digest = hashlib.sha256(crate.read_bytes()).hexdigest()
    if digest != package.get("checksum"):
        raise ValueError(f"checksum mismatch for {package['name']} {package['version']}")
    with tarfile.open(crate, "r:*") as archive:
        members = archive.getmembers()
        root = Path("/tmp/license-root").resolve()
        if any(Path(m.name).is_absolute() or not safe_member(Path(m.name), root)
               or m.issym() or m.islnk() for m in members):
            raise ValueError(f"path traversal in {crate.name}")
        cargo = [m for m in members if m.name.count("/") == 1 and m.name.endswith("/Cargo.toml")]
        if len(cargo) != 1:
            raise ValueError(f"missing Cargo.toml for {crate.name}")
        metadata = tomllib.loads(archive.extractfile(cargo[0]).read().decode("utf-8"))
        info = metadata.get("package", {})
        license_id = info.get("license")
        if info.get("name") != package["name"] or info.get("version") != package["version"]:
            raise ValueError(f"Cargo metadata does not match lockfile for {crate.name}")
        if not license_id:
            raise ValueError(f"missing license metadata for {crate.name}")
        texts = []
        for member in sorted(members, key=lambda m: m.name):
            if member.isfile() and LICENSE_NAMES.search(member.name):
                if member.size > MAX_TEXT: raise ValueError(f"license text exceeds size bound for {crate.name}")
                texts.append((Path(member.name).name, archive.extractfile(member).read().decode("utf-8")))
        if not texts:
            raise ValueError(f"missing license text for {crate.name}")
    return {"name": package["name"], "version": package["version"], "checksum": digest,
            "license": license_id, "texts": texts}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, type=Path)
    ap.add_argument("--lockfile", type=Path, default=Path(__file__).with_name("Cargo.lock"))
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--metadata", type=Path, help="cargo metadata JSON for a target-filtered reachable graph")
    ap.add_argument("--target", help="target recorded with --metadata")
    args = ap.parse_args()
    if not args.cache.is_dir(): raise ValueError("cache directory does not exist")
    if args.metadata and not args.target: raise ValueError("--target is required with --metadata")
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError("refusing non-empty output directory")
    packages = locked_packages(args.lockfile, args.metadata)
    records = [collect(p, crate_path(args.cache, p)) for p in packages]
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []
    for record in records:
        filename = f"{record['name']}-{record['version']}.txt"
        body = "\n\n".join(f"===== {name} =====\n{text}" for name, text in record["texts"])
        (args.output / filename).write_text(body.rstrip() + "\n", encoding="utf-8")
        manifest.append({k: record[k] for k in ("name", "version", "checksum", "license")})
    manifest_doc = {"target": args.target,
                    "lockSha256": hashlib.sha256(args.lockfile.read_bytes()).hexdigest(),
                    "metadataSha256": hashlib.sha256(args.metadata.read_bytes()).hexdigest() if args.metadata else None,
                    "packages": manifest}
    included = {(p["name"], p["version"], p["checksum"]) for p in packages}
    manifest_doc["excludedPackages"] = [
        {"name": p["name"], "version": p["version"], "checksum": p["checksum"],
         "reason": "unreachable in supplied target-filtered graph"}
        for p in locked_packages(args.lockfile)
        if (p["name"], p["version"], p["checksum"]) not in included
    ]
    (args.output / "manifest.json").write_text(json.dumps(manifest_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"collected {len(records)} locked registry crates into {args.output}")

if __name__ == "__main__":
    main()
