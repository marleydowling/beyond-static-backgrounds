
from __future__ import annotations

"""
Step 2 — audit and (optionally) relink Canada-facing electricity and fuel inputs.

This script is intentionally conservative:
- DRY RUN by default
- writes planning CSVs
- does not mutate the DB unless --apply is passed

In the thesis workflow, Step 2 ultimately recorded a "no-action—aligned" outcome for the
frozen premise-generated backgrounds. This script is kept as a reusable audit helper.
"""

import csv
import os
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from _common import load_yaml, norm_region, norm_unit

ENERGY_RP_PATTERNS = [
    r"^electricity(,|\s|$)",
    r"^heat(,|\s|$)",
    r"^steam(,|\s|$)",
    r"^thermal energy(,|\s|$)",
    r"^natural gas(,|\s|$)",
    r"^hydrogen(,|\s|$)",
    r"^diesel(,|\s|$)", r"^gasoline(,|\s|$)",
    r"^light fuel oil(,|\s|$)", r"^heavy fuel oil(,|\s|$)",
    r"^refinery gas(,|\s|$)", r"^lpg(,|\s|$)",
    r"^biogas(,|\s|$)", r"^biomethane(,|\s|$)",
    r"^hard coal(,|\s|$)", r"^coke(,|\s|$)",
    r"^wood chips(,|\s|$)", r"^wood pellet(,|\s|$)", r"^wood briquette(,|\s|$)",
]
_energy_regexes = [re.compile(p, re.IGNORECASE) for p in ENERGY_RP_PATTERNS]

UNIT_MAP = {
    "kwh": "kilowatt hour",
    "kilowatt hour": "kilowatt hour",
    "mwh": "megawatt hour",
    "megawatt hour": "megawatt hour",
    "mj": "megajoule",
    "megajoule": "megajoule",
    "m3": "cubic meter",
    "cubic meter": "cubic meter",
    "normal cubic meter": "cubic meter",
    "kg": "kilogram",
    "kilogram": "kilogram",
}

GEO_PREF = ("NA", "RNA", "CAN", "USA", "GLO", "World", "RoW", "RER")

def _canon(s):
    s = unicodedata.normalize("NFKC", str(s or "")).strip()
    return re.sub(r"\s+", " ", s)

def is_roi(loc, roi_label, roi_matches, na_matches):
    return norm_region(loc, roi_label, set(roi_matches), set(na_matches)) == roi_label

def is_energy_carrier(rp):
    rp = _canon(rp)
    return bool(rp) and any(rgx.search(rp) for rgx in _energy_regexes)

def voltage_tag_from_name(name):
    n = _canon(name).lower()
    if "low voltage" in n: return "lv"
    if "medium voltage" in n: return "mv"
    if "high voltage" in n: return "hv"
    if "aluminium industry" in n: return "alu"
    return "na"

def write_csv(path, rows, headers=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        if not rows:
            fh.write("no records\n")
            return
        if headers is None:
            headers = list(rows[0].keys())
        w = csv.DictWriter(fh, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    rel = cfg["relink"]
    source_db_name = rel["source_db_name"]
    work_db_name = rel["work_db_name"]
    dry_run = (not args.apply) if "dry_run" in rel else (not args.apply)
    roi_label = rel["roi_label"]
    roi_matches = rel["roi_matches"]
    na_matches = rel["na_matches"]

    os.environ["BRIGHTWAY2_DIR"] = cfg["project"]["brightway2_dir"]

    from bw2data import Database, databases, projects
    projects.set_current(cfg["project"]["name"])

    if source_db_name not in databases:
        raise RuntimeError(f"Source DB not found: {source_db_name}")
    if work_db_name not in databases:
        raise RuntimeError(f"Work DB not found: {work_db_name}")

    work = Database(work_db_name)

    def load_ds(key):
        if not (isinstance(key, tuple) and len(key) == 2):
            return {}
        try:
            return Database(key[0]).get(key).as_dict()
        except Exception:
            return {}

    # 1) histogram of available locations
    by_loc = Counter()
    roi_rows = []
    for a in work:
        loc = a.get("location")
        by_loc[norm_region(loc, roi_label, set(roi_matches), set(na_matches))] += 1
        if is_roi(loc, roi_label, roi_matches, na_matches) and len(roi_rows) < 25:
            d = a.as_dict()
            roi_rows.append({
                "dataset_key": str(a.key),
                "name": d.get("name"),
                "location": d.get("location"),
                "reference_product": d.get("reference product"),
                "unit": d.get("unit"),
            })

    out_dir = Path(cfg["outputs"]["audit_output_dir"])
    write_csv(out_dir / "location_histogram.csv", [{"region": k, "count": v} for k, v in by_loc.most_common()])
    write_csv(out_dir / "roi_sample.csv", roi_rows)

    # 2) identify existing ROI energy signatures
    existing_roi = set()
    candidates = defaultdict(list)
    for a in work:
        d = a.as_dict()
        rp = d.get("reference product") or ""
        if not is_energy_carrier(rp):
            continue
        sig = (_canon(rp), norm_unit(d.get("unit") or "", UNIT_MAP), voltage_tag_from_name(d.get("name") or ""))
        loc_norm = norm_region(d.get("location"), roi_label, set(roi_matches), set(na_matches))
        if loc_norm == roi_label:
            existing_roi.add(sig)
        candidates[sig].append((a.key, d.get("location"), d.get("name")))

    # 3) find Canada consumers using non-ROI energy providers
    used_sigs = set()
    examples = []
    for act in work:
        ad = act.as_dict()
        if not is_roi(ad.get("location"), roi_label, roi_matches, na_matches):
            continue
        for exc in ad.get("exchanges", []):
            if exc.get("type") != "technosphere":
                continue
            sup = load_ds(exc.get("input"))
            rp = sup.get("reference product")
            if not is_energy_carrier(rp):
                continue
            sig = (_canon(rp), norm_unit(sup.get("unit") or "", UNIT_MAP), voltage_tag_from_name(sup.get("name") or ""))
            if not is_roi(sup.get("location"), roi_label, roi_matches, na_matches):
                used_sigs.add(sig)
                if len(examples) < 20:
                    examples.append({
                        "consumer_activity": ad.get("name"),
                        "consumer_loc": ad.get("location"),
                        "old_supplier_name": sup.get("name"),
                        "old_supplier_loc": sup.get("location"),
                        "ref_product": sig[0],
                        "unit": sig[1],
                        "voltage_tag": sig[2],
                    })

    plan = []
    for sig in sorted(used_sigs):
        if sig in existing_roi:
            continue
        cands = candidates.get(sig, [])
        if not cands:
            continue
        chosen = None
        for pref in GEO_PREF:
            for k, loc, nm in cands:
                if norm_region(loc, roi_label, set(roi_matches), set(na_matches)) == pref:
                    chosen = (k, loc, nm)
                    break
            if chosen:
                break
        if not chosen:
            chosen = cands[0]
        up_key, up_loc, up_name = chosen
        plan.append({
            "rp": sig[0],
            "unit": sig[1],
            "voltage_tag": sig[2],
            "new_location": roi_label,
            "new_name": up_name,
            "upstream_key": str(up_key),
            "upstream_location": up_loc,
            "upstream_db": up_key[0],
            "note": "1:1 pass-through; preserves pathway-region composition",
        })

    write_csv(out_dir / "relink_plan.csv", plan)
    write_csv(out_dir / "relink_examples.csv", examples)

    print(f"[ok] wrote audit pack to {out_dir}")
    if dry_run:
        print("[info] DRY RUN only: no DB writes were applied.")
    else:
        print("[warning] Apply-mode mutation is not yet implemented in this repo-safe version.")

if __name__ == "__main__":
    main()
