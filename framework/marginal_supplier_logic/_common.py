from __future__ import annotations

from typing import Iterable, List

import pandas as pd


TRUE_VALUES = {"true", "yes", "y", "1", True, 1}
FALSE_VALUES = {"false", "no", "n", "0", False, 0}


def to_bool(value) -> bool | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        v = value.strip().lower()
        if v in TRUE_VALUES:
            return True
        if v in FALSE_VALUES:
            return False
        return None
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    return None


def normalize_shares(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    total = float(s.sum())
    if total <= 0:
        return s * 0.0
    return s / total


def coalesce_numeric(df: pd.DataFrame, columns: List[str], default: float = 0.0) -> pd.Series:
    out = pd.Series([pd.NA] * len(df), index=df.index, dtype="float64")
    for col in columns:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            out = out.fillna(s)
    return out.fillna(default)


def safe_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value)
