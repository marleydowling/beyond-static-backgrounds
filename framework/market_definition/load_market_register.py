from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


def _trim_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_object_dtype(out[col]):
            out[col] = out[col].map(lambda x: x.strip() if isinstance(x, str) else x)
            out[col] = out[col].replace({"": pd.NA})
    return out


def load_csv_table(path: str | Path, required_columns: Optional[Iterable[str]] = None) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path)
    df = _trim_string_columns(df)
    if required_columns:
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns in {path.name}: {missing}")
    return df


def load_step3_bundle(
    market_csv: str | Path,
    rules_csv: str | Path,
    supplier_candidates_csv: str | Path | None = None,
    provider_proxy_csv: str | Path | None = None,
    overlay_rules_csv: str | Path | None = None,
) -> Dict[str, pd.DataFrame]:
    tables: Dict[str, pd.DataFrame] = {
        "markets": load_csv_table(market_csv),
        "rules": load_csv_table(rules_csv),
    }
    if supplier_candidates_csv:
        tables["suppliers"] = load_csv_table(supplier_candidates_csv)
    else:
        tables["suppliers"] = pd.DataFrame()

    if provider_proxy_csv:
        tables["provider_proxy"] = load_csv_table(provider_proxy_csv)
    else:
        tables["provider_proxy"] = pd.DataFrame()

    if overlay_rules_csv:
        tables["overlay_rules"] = load_csv_table(overlay_rules_csv)
    else:
        tables["overlay_rules"] = pd.DataFrame()

    return tables
