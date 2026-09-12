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

def external_notice(package, license_id, manifest_path):
    manifest_path = Path(manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != 1 or not isinstance(data.get("notices"), list):
        raise ValueError("invalid external notice inventory")
    matches = [n for n in data["notices"] if n.get("name") == package["name"] and n.get("version") == package["version"]]
    if len(matches) != 1:
        raise ValueError("external notice must match exactly one locked package")
    notice = matches[0]
    if notice.get("checksum") != package["checksum"] or notice.get("license") != license_id:
        raise ValueError("external notice does not match locked checksum/license")
    source = notice.get("sourceUrl", "")
    if not re.fullmatch(r"https://raw\.githubusercontent\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/[0-9a-f]{40}/[A-Za-z0-9_./-]+", source):
        raise ValueError("external notice source must be commit-pinned")
    filename = notice.get("file", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", filename):
        raise ValueError("unsafe external notice filename")
    file = manifest_path.parent / filename
    if file.is_symlink() or not file.is_file() or file.stat().st_size > MAX_TEXT:
        raise ValueError("unsafe external notice file")
    text = file.read_bytes()
    if hashlib.sha256(text).hexdigest() != notice.get("sha256"):
        raise ValueError("external notice text digest mismatch")
    return text.decode("utf-8"), {k: notice[k] for k in ("sourceUrl", "sha256")}

def collect(package, crate, external=None):
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
        origin = None
        if not texts:
            if external is None:
                raise ValueError(f"missing license text for {crate.name}")
            text, origin = external_notice(package, license_id, external)
            vcs = [m for m in members if m.name.count("/") == 1 and m.name.endswith("/.cargo_vcs_info.json")]
            if len(vcs) != 1:
                raise ValueError("external notice requires locked crate VCS provenance")
            commit = json.loads(archive.extractfile(vcs[0]).read())["git"]["sha1"]
            repository = info.get("repository", "").rstrip("/").removesuffix(".git")
            prefix = repository.replace("https://github.com/", "https://raw.githubusercontent.com/") + f"/{commit}/"
            if not origin["sourceUrl"].startswith(prefix):
                raise ValueError("external notice does not match crate VCS repository/commit")
            texts.append(("UPSTREAM-LICENSE", text))
    return {"name": package["name"], "version": package["version"], "checksum": digest,
            "license": license_id, "texts": texts, "externalNotice": origin}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, type=Path)
    ap.add_argument("--lockfile", type=Path, default=Path(__file__).with_name("Cargo.lock"))
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--metadata", type=Path, help="cargo metadata JSON for a target-filtered reachable graph")
    ap.add_argument("--target", help="target recorded with --metadata")
    ap.add_argument("--external-notices", type=Path, help="reviewed commit-pinned local notices for crates missing texts; never downloaded")
    args = ap.parse_args()
    if not args.cache.is_dir(): raise ValueError("cache directory does not exist")
    if args.metadata and not args.target: raise ValueError("--target is required with --metadata")
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError("refusing non-empty output directory")
    packages = locked_packages(args.lockfile, args.metadata)
    records = [collect(p, crate_path(args.cache, p), args.external_notices) for p in packages]
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []
    for record in records:
        filename = f"{record['name']}-{record['version']}.txt"
        body = "\n\n".join(f"===== {name} =====\n{text}" for name, text in record["texts"])
        (args.output / filename).write_text(body.rstrip() + "\n", encoding="utf-8")
        manifest.append({k: record[k] for k in ("name", "version", "checksum", "license")})
        if record["externalNotice"]:
            manifest[-1]["externalNotice"] = record["externalNotice"]
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
