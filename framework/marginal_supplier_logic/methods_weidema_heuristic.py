from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ._common import normalize_shares, coalesce_numeric, safe_text, to_bool


def build_market(
    market_row: pd.Series,
    rule_row: pd.Series,
    supplier_rows: pd.DataFrame,
) -> Dict[str, object]:
    df = supplier_rows.copy()
    if df.empty:
        raise ValueError(f"No supplier rows available for market_id={market_row['market_id']}")
    modernity_threshold = pd.to_numeric(pd.Series([rule_row.get("modernity_threshold")]), errors="coerce").fillna(0.0).iloc[0]

    if "included_in_marginal_set" in df.columns and df["included_in_marginal_set"].map(to_bool).notna().any():
        modern = df.loc[df["included_in_marginal_set"].map(to_bool) == True].copy()
        basis = "explicit_included_flag"
    else:
        annual_change = coalesce_numeric(df, ["annual_change_fraction", "net_annual_trend_fraction"], default=0.0)
        modern = df.loc[annual_change > modernity_threshold].copy()
        basis = "growth_threshold"

    if modern.empty:
        modern = df.nlargest(1, columns=["start_value"] if "start_value" in df.columns else df.columns[:1]).copy()
        basis = "largest_supplier_fallback"

    if "marginal_share" in modern.columns and pd.to_numeric(modern["marginal_share"], errors="coerce").fillna(0).sum() > 0:
        modern["resolved_share"] = normalize_shares(pd.to_numeric(modern["marginal_share"], errors="coerce").fillna(0.0))
    else:
        modern["resolved_share"] = normalize_shares(coalesce_numeric(modern, ["start_value", "end_value"], default=1.0))

    share_rows: List[Dict[str, object]] = []
    for _, row in modern.iterrows():
        share_rows.append(
            {
                "market_id": market_row["market_id"],
                "representation_method": "weidema_heuristic",
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
            "resolved_method": "weidema_heuristic",
            "resolution_basis": basis,
            "share_count": len(share_rows),
            "share_sum": float(sum(r["resolved_share"] for r in share_rows)),
        },
        "share_rows": share_rows,
        "overlay_rows": [],
        "proxy_rows": [],
    }
