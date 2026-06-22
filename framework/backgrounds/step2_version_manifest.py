
from __future__ import annotations

"""
Step 2 — clone a frozen background to a stable alias and write a lightweight version manifest.

Typical use:
- preserve the canonical build name from premise
- create a citable local alias if needed
- record counts, package versions, and checksums
"""

import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path

from _common import load_yaml, dump_json, pkgver, scenario_slug, mode_slug

def activity_identity_checksum(db):
    h = hashlib.sha256()
    acts = sorted(((a.get("code"), a) for a in db), key=lambda x: x[0] or "")
    for code, a in acts:
        payload = (
            a.get("database") or "",
            a.get("code") or "",
            a.get("name") or "",
            a.get("reference product") or a.get("reference_product") or "",
            a.get("location") or "",
            a.get("unit") or "",
        )
        h.update(("|".join(payload)).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()

def count_exchanges(db):
    acts = 0
    tech = bio = prod = 0
    for a in db:
        acts += 1
        tech += sum(1 for _ in a.technosphere())
        bio += sum(1 for _ in a.biosphere())
        prod += sum(1 for _ in a.production())
    return acts, {"technosphere": tech, "biosphere": bio, "production": prod}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--source-db", required=True)
    parser.add_argument("--target-db", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    os.environ["BRIGHTWAY2_DIR"] = cfg["project"]["brightway2_dir"]

    import bw2data as bw
    from bw2data import Database, projects

    projects.set_current(cfg["project"]["name"])

    if args.source_db not in bw.databases:
        raise RuntimeError(f"Source DB not found: {args.source_db}")

    if args.target_db in bw.databases:
        if not args.overwrite:
            raise RuntimeError(f"Target DB exists: {args.target_db}. Use --overwrite to replace.")
        Database(args.target_db).delete(warn=False)
        if args.target_db in bw.databases:
            del bw.databases[args.target_db]

    Database(args.source_db).copy(args.target_db)
    db = Database(args.target_db)
    acts, bytype = count_exchanges(db)

    manifest = {
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "project": projects.current,
        "database": args.target_db,
        "source_database": args.source_db,
        "versions": {
            "premise": pkgver("premise"),
            "bw2data": pkgver("bw2data"),
            "bw2io": pkgver("bw2io"),
            "python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "ecoinvent": str(cfg["source"]["source_version"]),
            "iam_model": cfg["scenario"]["model"],
        },
        "counts": {
            "activities": acts,
            "exchanges_total": sum(bytype.values()),
            "exchanges_by_type": bytype,
        },
        "checksum_sha256": activity_identity_checksum(db),
    }
    out_dir = Path(cfg["outputs"]["manifests_dir"])
    dump_json(out_dir / f"step2_version_manifest_{args.target_db}.json", manifest)
    print(f"[ok] version manifest written for {args.target_db}")

if __name__ == "__main__":
    main()
