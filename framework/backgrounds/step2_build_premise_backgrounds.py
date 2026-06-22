
from __future__ import annotations

"""
Step 2 — build scenario-consistent backgrounds with premise.

This is the main repo-facing build script for IAM-coupled backgrounds.

It is config-driven and designed to replace the family of scenario-specific one-off scripts.
The example config is set to IMAGE / SSP2-M / PERF, but the same script can be used for:
- IMAGE / TIAM-UCL / REMIND / other supported IAMs
- SSP1-VLLO / SSP2-M / SSP5-H / other supported pathways
- PERF or MYOP
"""

import inspect
import os
import time
import traceback
from pathlib import Path

from _common import (
    TeeLogger,
    canonical_biosphere_name,
    derived_target_db_name,
    dump_json,
    ensure_dir,
    load_yaml,
    maybe_apply_uncertainty_shortcuts,
    pkgver,
    ts_utc,
)

def filter_kwargs_for_init(cls, kwargs: dict):
    sig = inspect.signature(cls.__init__)
    allowed = set(sig.parameters.keys())
    accepted = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    dropped = {k: v for k, v in kwargs.items() if k not in allowed}
    return accepted, dropped

def safe_delete_database(db_name: str, delete_vacuum_on_overwrite: bool):
    import bw2data as bw
    from bw2data import Database

    if db_name not in bw.databases:
        return
    db = Database(db_name)
    if hasattr(db, "delete"):
        sig = inspect.signature(db.delete)
        kwargs = {}
        if "vacuum" in sig.parameters:
            kwargs["vacuum"] = bool(delete_vacuum_on_overwrite)
        if "warn" in sig.parameters:
            kwargs["warn"] = False
        if "signal" in sig.parameters:
            kwargs["signal"] = True
        db.delete(**kwargs)
    if db_name in bw.databases:
        del bw.databases[db_name]

def require_iam_csv(model: str, pathway: str, directory: Path):
    expected = directory / f"{model.lower()}_{pathway}.csv"
    if not expected.exists():
        raise FileNotFoundError(f"Missing IAM CSV: {expected}")
    if expected.stat().st_size < 50_000:
        raise FileNotFoundError(f"IAM CSV looks too small/corrupt: {expected}")
    return expected

def build_one(cfg: dict) -> dict:
    cfg = maybe_apply_uncertainty_shortcuts(cfg)
    project_name = cfg["project"]["name"]
    source = cfg["source"]
    scenario = cfg["scenario"]
    premise_cfg = cfg["premise"]
    unc = cfg["uncertainty"]
    outputs = cfg["outputs"]

    os.environ["BRIGHTWAY2_DIR"] = cfg["project"]["brightway2_dir"]

    from bw2data import Database, projects
    from premise import NewDatabase

    projects.set_current(project_name)

    run_id = ts_utc().replace(":", "").replace(".", "")
    ensure_dir(Path(outputs["run_log_dir"]))
    ensure_dir(Path(outputs["manifests_dir"]))
    logfile = Path(outputs["run_log_dir"]) / f"step2_build_premise_{run_id}.log"
    logger = TeeLogger(logfile)

    model = scenario["model"]          # change in config: image / tiam-ucl / remind / ...
    pathway = scenario["pathway"]      # change in config: SSP2-M / SSP1-VLLO / SSP5-H / ...
    year = int(scenario["year"])
    foresight_mode = scenario["foresight_mode"]  # change in config: perf / myop
    foresight_bool = True if foresight_mode.lower() == "perf" else False

    biosphere_name = source.get("biosphere_name") or canonical_biosphere_name("3.10")
    target_db = outputs.get("target_db_name") or derived_target_db_name(model, pathway, year, foresight_mode)

    if target_db in __import__("bw2data").databases:
        if premise_cfg.get("overwrite_existing", False):
            logger.log(f"[overwrite] deleting existing target db: {target_db}")
            safe_delete_database(target_db, premise_cfg.get("delete_vacuum_on_overwrite", False))
        else:
            raise RuntimeError(f"Target DB already exists: {target_db}. Set overwrite_existing=true to replace.")

    iam_output_dir = Path(scenario["iam_output_dir"])
    iam_csv = require_iam_csv(model, pathway, iam_output_dir)

    logger.log(f"[cfg] project={project_name}")
    logger.log(f"[cfg] model={model} pathway={pathway} year={year} foresight_mode={foresight_mode}")
    logger.log(f"[cfg] target_db={target_db}")
    logger.log(f"[cfg] source_version={source['source_version']} biosphere={biosphere_name}")
    logger.log(f"[env] premise={pkgver('premise')} bw2data={pkgver('bw2data')} bw2io={pkgver('bw2io')}")

    source_kind = source["kind"].strip().lower()
    common_kwargs = dict(
        scenarios=[{"model": model, "pathway": pathway, "year": year, "filepath": str(iam_output_dir)}],
        key=os.environ.get(scenario.get("iam_key_env_var", "PREMISE_KEY"), "").strip() or None,
        source_version=str(source["source_version"]),
        system_model=source.get("system_model", "consequential"),
        biosphere_name=biosphere_name,
        keep_source_db_uncertainty=bool(unc.get("keep_source_db_uncertainty", False)),
        keep_imports_uncertainty=bool(unc.get("keep_imports_uncertainty", True)),
        use_absolute_efficiency=bool(premise_cfg.get("use_absolute_efficiency", False)),
        use_cached_database=bool(premise_cfg.get("use_cached_database", True)),
        use_cached_inventories=bool(premise_cfg.get("use_cached_inventories", True)),
        use_multiprocessing=bool(premise_cfg.get("use_multiprocessing", False)),
        quiet=bool(premise_cfg.get("quiet", False)),
        system_args={
            "range time": 2,
            "duration": 0,
            "foresight": foresight_bool,   # perf=True, myop=False
            "lead time": False,
            "capital replacement rate": False,
            "measurement": 0,
            "weighted slope start": 0.75,
            "weighted slope end": 1.00,
        },
    )

    if source_kind == "brightway":
        kwargs = dict(common_kwargs)
        kwargs["source_db"] = source["source_db"]
    elif source_kind == "ecospold":
        kwargs = dict(common_kwargs)
        kwargs["source_type"] = "ecospold"
        kwargs["source_file_path"] = str(Path(source["ecospold_datasets"]))
    else:
        raise ValueError(f"Unsupported source.kind: {source_kind}")

    filtered_kwargs, dropped = filter_kwargs_for_init(NewDatabase, kwargs)

    if premise_cfg.get("strict_require_system_args", True) and "system_args" in dropped:
        raise RuntimeError(
            "Installed premise.NewDatabase() does not accept system_args, so PERF/MYOP cannot be controlled as configured."
        )

    if unc.get("strict_require_uncertainty_support", False):
        missing_unc = [k for k in ("keep_source_db_uncertainty", "keep_imports_uncertainty") if k in dropped]
        if missing_unc:
            raise RuntimeError(f"Installed premise.NewDatabase() dropped uncertainty flags: {missing_unc}")

    if dropped:
        logger.log(f"[premise][info] dropped unsupported kwargs: {sorted(dropped.keys())}")

    t0 = time.perf_counter()
    ndb = NewDatabase(**filtered_kwargs)

    for sector in cfg["premise"]["sectors_to_update"]:
        logger.log(f"[update] sector={sector}")
        ndb.update(sector)

    logger.log(f"[write] writing Brightway DB: {target_db}")
    ndb.write_db_to_brightway(name=target_db)

    minutes = (time.perf_counter() - t0) / 60.0
    n_acts = len(Database(target_db))
    logger.log(f"[done] built {target_db} in {minutes:.2f} min | activities={n_acts}")
    logger.close()

    manifest = {
        "timestamp_utc": ts_utc(),
        "project": project_name,
        "target_db": target_db,
        "model": model,
        "pathway": pathway,
        "year": year,
        "foresight_mode": foresight_mode,
        "foresight_bool": foresight_bool,
        "iam_csv": str(iam_csv),
        "source_kind": source_kind,
        "source_version": source["source_version"],
        "biosphere_name": biosphere_name,
        "sectors_updated": cfg["premise"]["sectors_to_update"],
        "uncertainty": {
            "keep_source_db_uncertainty": bool(unc.get("keep_source_db_uncertainty", False)),
            "keep_imports_uncertainty": bool(unc.get("keep_imports_uncertainty", True)),
        },
        "env": {
            "premise": pkgver("premise"),
            "bw2data": pkgver("bw2data"),
            "bw2io": pkgver("bw2io"),
            "python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        },
        "activities": n_acts,
        "minutes": round(minutes, 3),
        "logfile": str(logfile),
    }
    manifest_path = Path(outputs["manifests_dir"]) / f"step2_build_manifest_{target_db}.json"
    dump_json(manifest_path, manifest)

    if n_acts < int(cfg["premise"].get("min_activity_count_ok", 15000)):
        print(f"[warning] activity count below threshold: {n_acts}")

    return manifest

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    manifest = build_one(load_yaml(args.config))
    print(f"[ok] wrote manifest: {Path(manifest['logfile']).with_suffix('.json')}")

if __name__ == "__main__":
    main()
