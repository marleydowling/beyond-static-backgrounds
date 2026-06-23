from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ._common import normalize_shares, to_bool, coalesce_numeric, safe_text


def build_market(
    market_row: pd.Series,
    rule_row: pd.Series,
    supplier_rows: pd.DataFrame,
) -> Dict[str, object]:
    df = supplier_rows.copy()
    if df.empty:
        raise ValueError(f"No supplier rows available for market_id={market_row['market_id']}")
    if "included_in_marginal_set" in df.columns:
        incl = df["included_in_marginal_set"].map(to_bool)
        included = df.loc[incl == True].copy()
    else:
        included = df.copy()

    explicit_share = pd.to_numeric(included.get("marginal_share"), errors="coerce") if "marginal_share" in included.columns else pd.Series(dtype=float)

    if not included.empty and explicit_share.notna().any() and float(explicit_share.fillna(0).sum()) > 0:
        included["resolved_share"] = normalize_shares(explicit_share)
        resolution_basis = "explicit_marginal_share"
    else:
        weights = coalesce_numeric(
            included,
            ["positive_delta_value", "net_annual_change", "delta_value", "start_value"],
            default=0.0,
        )
        positive = weights.clip(lower=0)
        if float(positive.sum()) > 0:
            included["resolved_share"] = normalize_shares(positive)
            resolution_basis = "positive_delta_normalization"
        else:
            fallback = coalesce_numeric(included, ["start_value"], default=0.0)
            included["resolved_share"] = normalize_shares(fallback)
            resolution_basis = "fallback_start_value_normalization"

    share_rows: List[Dict[str, object]] = []
    for _, row in included.iterrows():
        share_rows.append(
            {
                "market_id": market_row["market_id"],
                "representation_method": "custom_empirical_mix",
                "supplier_id": safe_text(row.get("supplier_id") or row.get("supplier_name")),
                "supplier_name": safe_text(row.get("supplier_name")),
                "technology_or_mechanism": safe_text(row.get("technology_or_mechanism")),
                "supplier_location": safe_text(row.get("supplier_location")),
                "resolved_share": float(row["resolved_share"]),
                "provider_or_proxy_label": safe_text(row.get("provider_or_proxy_label") or market_row.get("provider_or_proxy_label")),
                "source_reference": safe_text(row.get("source_reference") or rule_row.get("source_reference") or market_row.get("source_reference")),
                "notes": safe_text(row.get("notes") or market_row.get("notes")),
            }
        )

    return {
        "summary": {
            "market_id": market_row["market_id"],
            "resolved_method": "custom_empirical_mix",
            "resolution_basis": resolution_basis,
            "share_count": len(share_rows),
            "share_sum": float(sum(r["resolved_share"] for r in share_rows)),
        },
        "share_rows": share_rows,
        "overlay_rows": [],
        "proxy_rows": [],
    }
