
from __future__ import annotations

import json
import os
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import yaml


def ts_utc() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def dump_json(path: str | Path, payload: dict) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def pkgver(name: str) -> str:
    try:
        from importlib import metadata as importlib_metadata
        return importlib_metadata.version(name)
    except Exception:
        return "unknown"


class TeeLogger:
    def __init__(self, logfile: str | Path):
        self.logfile = Path(logfile)
        ensure_dir(self.logfile.parent)
        self.fp = open(self.logfile, "a", encoding="utf-8")

    def close(self):
        try:
            self.fp.close()
        except Exception:
            pass

    def log(self, msg: str):
        line = f"[{ts_utc()}] {msg}"
        print(line, flush=True)
        try:
            self.fp.write(line + "\n")
            self.fp.flush()
        except Exception:
            pass


def scenario_slug(pathway: str) -> str:
    return pathway.replace("-", "").replace("_", "")


def mode_slug(foresight_mode: str) -> str:
    m = foresight_mode.strip().lower()
    if m == "perf":
        return "PERF"
    if m == "myop":
        return "MYOP"
    raise ValueError(f"Unsupported foresight_mode: {foresight_mode}")


def model_slug(model: str) -> str:
    return model.strip().upper().replace("-", "_")


def derived_target_db_name(model: str, pathway: str, year: int, foresight_mode: str) -> str:
    return f"prospective_conseq_{model_slug(model)}_{scenario_slug(pathway)}_{int(year)}_{mode_slug(foresight_mode)}"


def canonical_biosphere_name(version: str = "3.10") -> str:
    # repo standard going forward: use 3.10 consistently
    return f"ecoinvent-{version}-biosphere"


def maybe_apply_uncertainty_shortcuts(cfg: dict) -> dict:
    out = dict(cfg)
    uncertainty = dict(out.get("uncertainty", {}))
    if "keep_all_uncertainty" in uncertainty:
        keep_all = bool(uncertainty["keep_all_uncertainty"])
        uncertainty.setdefault("keep_source_db_uncertainty", keep_all)
        uncertainty.setdefault("keep_imports_uncertainty", keep_all)
    out["uncertainty"] = uncertainty
    return out


def safe_path(x: Optional[str | Path]) -> Optional[Path]:
    if x in (None, "", "null"):
        return None
    return Path(x)


def _canon(s: Any) -> str:
    s = unicodedata.normalize("NFKC", str(s or "")).strip()
    return re.sub(r"\s+", " ", s)


def norm_unit(u: str, unit_map: dict[str, str]) -> str:
    key = _canon(u).lower()
    return unit_map.get(key, _canon(u))


def norm_region(loc: str, roi_label: str, roi_matches: set[str], na_matches: set[str]) -> str:
    s = _canon(loc)
    if not s:
        return s
    if s.upper().startswith("CA-"):
        return roi_label
    low = s.lower()
    if low in {x.lower() for x in roi_matches}:
        return roi_label
    if low in {x.lower() for x in na_matches}:
        return "NA"
    mapping = {
        "us": "USA", "usa": "USA", "united states": "USA",
        "glo": "GLO", "world": "GLO",
        "row": "RoW", "rest of world": "RoW",
        "rer": "RER",
    }
    return mapping.get(low, s)
