
from __future__ import annotations

"""
Step 2 — freeze and audit prospective backgrounds.

This script is derived from the uploaded freeze/audit logic, but parameterized to work from
config and an explicit database list.
"""

import hashlib
import os
import time
from itertools import islice
from pathlib import Path

from _common import dump_json, load_yaml, pkgver, ts_utc

EXAMPLE_LIMIT = 12

def as_key(x):
    if x is None:
        return None
    if isinstance(x, tuple) and len(x) == 2:
        return x
    try:
        k = x.key
        if isinstance(k, tuple) and len(k) == 2:
            return k
    except Exception:
        pass
    return None

def biosphere_digest(Database, db_name: str, max_codes: int = 500) -> str:
    codes = sorted([a.get("code") for a in Database(db_name)])[:max_codes]
    h = hashlib.sha1()
    for c in codes:
        h.update((c or "").encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()

def activity_identity_checksum(Database, db_name: str) -> str:
    h = hashlib.sha256()
    db = Database(db_name)
    acts = sorted(((a.get("code"), a) for a in db), key=lambda x: x[0] or "")
    for code, a in acts:
        payload = (
            (a.get("database") or ""),
            (a.get("code") or ""),
            (a.get("name") or ""),
            (a.get("reference product") or a.get("reference_product") or ""),
            (a.get("location") or ""),
            (a.get("unit") or ""),
        )
        h.update(("|".join(payload)).encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()

def geomapping_has_location(bw, loc: str) -> bool:
    try:
        gm = getattr(bw, "geomapping", None)
        if gm is not None:
            return loc in gm
    except Exception:
        pass
    try:
        from bw2data import geomapping as gm2
        return loc in gm2
    except Exception:
        return False

def scan_background_db_integrity(bw, Database, db_name: str, biosphere_name: str, scan_n):
    db = Database(db_name)
    n_total = len(db)
    n_scan = n_total if scan_n is None else min(scan_n, n_total)

    self_codes = {a.get("code") for a in db}
    bio_codes = {a.get("code") for a in Database(biosphere_name)}

    unexpected_external_tech = {}
    broken_tech = broken_bio = wrong_biosphere_db = missing_location = unknown_location = 0
    examples = {k: [] for k in [
        "unexpected_external_tech","broken_tech","wrong_biosphere_db",
        "broken_bio","missing_location","unknown_location"
    ]}

    for a in islice(db, n_scan):
        loc = a.get("location", None)
        if not loc:
            missing_location += 1
            if len(examples["missing_location"]) < EXAMPLE_LIMIT:
                examples["missing_location"].append({"code": a.get("code"), "name": a.get("name")})
        elif not geomapping_has_location(bw, loc):
            unknown_location += 1
            if len(examples["unknown_location"]) < EXAMPLE_LIMIT:
                examples["unknown_location"].append({"location": loc, "code": a.get("code"), "name": a.get("name")})

        for exc in a.exchanges():
            et = exc.get("type")
            inp = as_key(exc.get("input"))
            if not inp:
                continue
            inp_db, inp_code = inp
            if et == "technosphere":
                if inp_db != db_name:
                    unexpected_external_tech[inp_db] = unexpected_external_tech.get(inp_db, 0) + 1
                elif inp_code not in self_codes:
                    broken_tech += 1
            elif et == "biosphere":
                if inp_db != biosphere_name:
                    wrong_biosphere_db += 1
                elif inp_code not in bio_codes:
                    broken_bio += 1

    return {
        "activity_count": n_total,
        "scanned_activities": n_scan,
        "unexpected_external_technosphere_inputs": sorted(unexpected_external_tech.items(), key=lambda x: x[1], reverse=True)[:20],
        "broken_technosphere_links": broken_tech,
        "wrong_biosphere_db_links": wrong_biosphere_db,
        "broken_biosphere_links": broken_bio,
        "missing_location": missing_location,
        "unknown_location": unknown_location,
        "examples": examples,
    }

def orphan_exchange_scan(bw, Database, db_names_to_scan=None, sample_activities_per_db=2000):
    existing = set(bw.databases.keys())
    results = []
    if db_names_to_scan is None:
        db_names_to_scan = sorted(existing)
    for dbn in db_names_to_scan:
        db = Database(dbn)
        n_total = len(db)
        n_scan = n_total if sample_activities_per_db is None else min(sample_activities_per_db, n_total)
        orphan_inputs = {}
        examples = []
        for a in islice(db, n_scan):
            for exc in a.exchanges():
                inp = as_key(exc.get("input"))
                if not inp:
                    continue
                inp_db, _ = inp
                if inp_db not in existing:
                    orphan_inputs[inp_db] = orphan_inputs.get(inp_db, 0) + 1
                    if len(examples) < EXAMPLE_LIMIT:
                        examples.append({"db": dbn, "consumer": (dbn, a.get("code")), "consumer_name": a.get("name"), "input": inp, "type": exc.get("type")})
        if orphan_inputs:
            results.append({"db": dbn, "scanned_activities": n_scan, "orphan_input_dbs": sorted(orphan_inputs.items(), key=lambda x: x[1], reverse=True)[:25], "examples": examples})
    return results

def mark_frozen(bw, db_name: str, payload: dict):
    meta = dict(bw.databases.get(db_name, {}))
    meta["frozen"] = True
    meta["frozen_utc"] = ts_utc()
    meta["frozen_checksum_sha256"] = payload.get("checksum_sha256")
    meta["frozen_manifest_path"] = payload.get("manifest_path")
    bw.databases[db_name] = meta
    if hasattr(bw.databases, "flush"):
        bw.databases.flush()
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--db", action="append", default=[])
    parser.add_argument("--scan-activities", default="2000")
    parser.add_argument("--orphan-scan-all", action="store_true")
    parser.add_argument("--mark-frozen", action="store_true")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    os.environ["BRIGHTWAY2_DIR"] = cfg["project"]["brightway2_dir"]

    import bw2data as bw
    from bw2data import Database, projects

    projects.set_current(cfg["project"]["name"])
    biosphere_name = cfg["source"]["biosphere_name"]
    if biosphere_name not in bw.databases:
        raise RuntimeError(f"Missing biosphere database: {biosphere_name}")

    dbs = args.db or [cfg["outputs"]["target_db_name"]] if cfg["outputs"].get("target_db_name") else []
    if not dbs:
        dbs = []

    scan_n = None if str(args.scan_activities).lower() == "full" else int(args.scan_activities)
    manifest_path = Path(cfg["outputs"]["manifests_dir"]) / f"step2_freeze_audit_{ts_utc().replace(':','').replace('.','')}.json"

    orphan_findings = orphan_exchange_scan(
        bw, Database,
        db_names_to_scan=None if args.orphan_scan_all else dbs,
        sample_activities_per_db=2000,
    )

    manifest = {
        "timestamp_utc": ts_utc(),
        "project": cfg["project"]["name"],
        "biosphere": {
            "name": biosphere_name,
            "flows": len(Database(biosphere_name)),
            "digest": biosphere_digest(Database, biosphere_name),
        },
        "env": {
            "premise": pkgver("premise"),
            "bw2data": pkgver("bw2data"),
            "bw2io": pkgver("bw2io"),
            "python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        },
        "found": [],
        "missing": [],
        "orphan_exchange_findings": orphan_findings,
    }

    for dbn in dbs:
        if dbn not in bw.databases:
            manifest["missing"].append({"db": dbn})
            continue
        entry = {
            "db": dbn,
            "activity_count": len(Database(dbn)),
            "checksum_sha256": activity_identity_checksum(Database, dbn),
            "integrity_scan": scan_background_db_integrity(bw, Database, dbn, biosphere_name, scan_n),
            "manifest_path": str(manifest_path),
            "frozen_marker_written": False,
        }
        if args.mark_frozen:
            entry["frozen_marker_written"] = mark_frozen(bw, dbn, entry)
        manifest["found"].append(entry)

    dump_json(manifest_path, manifest)
    print(f"[ok] wrote manifest: {manifest_path}")

if __name__ == "__main__":
    main()
