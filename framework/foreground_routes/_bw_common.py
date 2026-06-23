from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def configure_brightway(config_path: str | Path):
    cfg = load_yaml(config_path)
    bw_dir = cfg["project"]["brightway2_dir"]
    project_name = cfg["project"]["name"]
    os.environ["BRIGHTWAY2_DIR"] = str(bw_dir)

    import bw2data as bd

    bd.projects.set_current(project_name)
    return bd, cfg


def safe_delete_database(bd, db_name: str) -> None:
    if db_name in bd.databases:
        try:
            bd.Database(db_name).delete(warn=False)
        except Exception:
            pass
        try:
            bd.databases.pop(db_name, None)
        except Exception:
            pass


def make_dataset(
    db_name: str,
    code: str,
    name: str,
    reference_product: str = "unit",
    unit: str = "unit",
    location: str = "GLO",
    comment: str = "",
    extra: dict | None = None,
) -> dict:
    ds = {
        "name": name,
        "reference product": reference_product,
        "unit": unit,
        "location": location,
        "comment": comment,
        "exchanges": [
            {
                "input": (db_name, code),
                "amount": 1.0,
                "type": "production",
                "name": name,
                "product": reference_product,
                "unit": unit,
            }
        ],
    }
    if extra:
        ds.update(extra)
    return ds
