from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ._common import normalize_shares, safe_text, to_bool


def _resolve_identity_rows(
    market_row: pd.Series,
    rule_row: pd.Series,
    supplier_rows: pd.DataFrame,
    all_supplier_rows: pd.DataFrame,
) -> pd.DataFrame:
    if not supplier_rows.empty:
        src = supplier_rows.copy()
    else:
        src_market = rule_row.get("identity_source_market_id")
        if pd.isna(src_market):
            raise ValueError(f"Overlay market {market_row['market_id']} requires supplier rows or identity_source_market_id")
        src = all_supplier_rows.loc[all_supplier_rows["market_id"] == src_market].copy()
        if src.empty:
            raise ValueError(f"identity_source_market_id={src_market} has no supplier rows for overlay market {market_row['market_id']}")
    if "included_in_marginal_set" in src.columns:
        included = src.loc[src["included_in_marginal_set"].map(to_bool) == True].copy()
        if not included.empty:
            src = included
    if "marginal_share" in src.columns and pd.to_numeric(src["marginal_share"], errors="coerce").fillna(0).sum() > 0:
        src["resolved_share"] = normalize_shares(pd.to_numeric(src["marginal_share"], errors="coerce").fillna(0.0))
    else:
        raise ValueError(
            f"Overlay market {market_row['market_id']} requires explicit marginal_share values on the retained supplier identity structure"
        )
    return src


def build_market(
    market_row: pd.Series,
    rule_row: pd.Series,
    supplier_rows: pd.DataFrame,
    all_supplier_rows: pd.DataFrame,
    overlay_rows: pd.DataFrame,
) -> Dict[str, object]:
    overlay = overlay_rows.copy()
    if overlay.empty:
        raise ValueError(f"No overlay rows available for market_id={market_row['market_id']}")
    base = _resolve_identity_rows(market_row, rule_row, supplier_rows, all_supplier_rows)

    share_rows: List[Dict[str, object]] = []
    for _, row in base.iterrows():
        share_rows.append(
            {
                "market_id": market_row["market_id"],
                "representation_method": "prospective_overlay",
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

    overlay_out: List[Dict[str, object]] = []
    overlay_share_series = pd.to_numeric(overlay.get("overlay_share"), errors="coerce")
    has_overlay_weights = overlay_share_series.notna().any() and float(overlay_share_series.fillna(0).sum()) > 0
    if has_overlay_weights:
        overlay["overlay_share_resolved"] = normalize_shares(overlay_share_series.fillna(0.0))
        overlay_status = "resolved_weighted_overlay"
    else:
        overlay["overlay_share_resolved"] = pd.NA
        overlay_status = "unresolved_overlay_components_only"

    for _, row in overlay.iterrows():
        overlay_out.append(
            {
                "market_id": market_row["market_id"],
                "overlay_id": safe_text(row.get("overlay_id")),
                "overlay_label": safe_text(row.get("overlay_label")),
                "overlay_provider_label": safe_text(row.get("overlay_provider_label")),
                "overlay_share": None if pd.isna(row.get("overlay_share_resolved")) else float(row.get("overlay_share_resolved")),
                "overlay_rank": row.get("overlay_rank"),
                "source_reference": safe_text(row.get("source_reference") or rule_row.get("source_reference") or market_row.get("source_reference")),
                "notes": safe_text(row.get("notes") or market_row.get("notes")),
            }
        )

    return {
        "summary": {
            "market_id": market_row["market_id"],
            "resolved_method": "prospective_overlay",
            "resolution_basis": "retained_supplier_identity_plus_overlay_components",
            "identity_source_market_id": safe_text(rule_row.get("identity_source_market_id") or market_row["market_id"]),
            "share_count": len(share_rows),
            "share_sum": float(sum(r["resolved_share"] for r in share_rows)),
            "overlay_status": overlay_status,
            "overlay_component_count": len(overlay_out),
        },
        "share_rows": share_rows,
        "overlay_rows": overlay_out,
        "proxy_rows": [],
    }
