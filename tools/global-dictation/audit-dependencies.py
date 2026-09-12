#!/usr/bin/env python3
"""Query OSV for the exact locked public Cargo dependencies; never run Cargo."""
import argparse
import datetime
import json
from pathlib import Path
import tomllib
import urllib.request


def query(payload):
    request = urllib.request.Request(
        "https://api.osv.dev/v1/querybatch",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("OSV response exceeds the bounded audit size")
    return json.loads(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query-osv", action="store_true", required=True,
                        help="Send public package names and versions to OSV")
    args = parser.parse_args()
    packages = [p for p in tomllib.loads(Path(__file__).with_name("Cargo.lock").read_text())["package"]
                if p.get("source", "").startswith("registry+")]
    if any(len(p.get("checksum", "")) != 64 for p in packages):
        raise ValueError("A registry dependency lacks its locked checksum")
    requests = [{"package": {"ecosystem": "crates.io", "name": p["name"]}, "version": p["version"]}
                for p in packages]
    results = query({"queries": requests})["results"]
    if len(results) != len(packages):
        raise ValueError("OSV result count does not match the lockfile")
    findings = []
    for package, request, result in zip(packages, requests, results):
        advisories = list(result.get("vulns", []))
        pages = 0
        while result.get("next_page_token"):
            pages += 1
            if pages > 10:
                raise ValueError("OSV pagination exceeds the bounded audit limit")
            result = query({"queries": [{**request, "page_token": result["next_page_token"]}]})["results"][0]
            advisories.extend(result.get("vulns", []))
        if advisories:
            findings.append({"name": package["name"], "version": package["version"],
                             "advisories": sorted({v["id"] for v in advisories})})
    print(json.dumps({"status": "FAIL" if findings else "PASS",
                      "scope": "Known OSV advisories for locked dependencies; not a complete source audit",
                      "checkedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      "dependencyCount": len(packages), "findings": findings}, indent=2))
    return bool(findings)


if __name__ == "__main__":
    raise SystemExit(main())
