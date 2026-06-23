from __future__ import annotations

from typing import Dict, List

import pandas as pd

from ._common import safe_text


def build_market(
    market_row: pd.Series,
    rule_row: pd.Series,
    provider_proxy_rows: pd.DataFrame,
) -> Dict[str, object]:
    if provider_proxy_rows.empty:
        raise ValueError(f"No provider/proxy rows available for market_id={market_row['market_id']}")
    proxy_rows: List[Dict[str, object]] = []
    for _, row in provider_proxy_rows.iterrows():
        proxy_rows.append(
            {
                "market_id": market_row["market_id"],
                "proxy_id": safe_text(row.get("proxy_id")),
                "proxy_label": safe_text(row.get("proxy_label")),
                "proxy_type": safe_text(row.get("proxy_type") or "proxy_provider"),
                "provider_or_proxy_label": safe_text(row.get("provider_or_proxy_label") or market_row.get("provider_or_proxy_label")),
                "source_reference": safe_text(row.get("source_reference") or rule_row.get("source_reference") or market_row.get("source_reference")),
                "notes": safe_text(row.get("notes") or market_row.get("notes")),
            }
        )

    return {
        "summary": {
            "market_id": market_row["market_id"],
            "resolved_method": "proxy_provider",
            "resolution_basis": "explicit_proxy_provider_mapping",
            "proxy_count": len(proxy_rows),
        },
        "share_rows": [],
        "overlay_rows": [],
        "proxy_rows": proxy_rows,
    }
