from __future__ import annotations

from typing import Dict

import pandas as pd

from ._common import safe_text


def build_market(
    market_row: pd.Series,
    rule_row: pd.Series,
) -> Dict[str, object]:
    return {
        "summary": {
            "market_id": market_row["market_id"],
            "resolved_method": "inherit_background",
            "resolution_basis": "scenario_conditioned_background",
            "background_source_db": safe_text(rule_row.get("background_source_db")),
            "provider_or_proxy_label": safe_text(rule_row.get("provider_or_proxy_label") or market_row.get("provider_or_proxy_label")),
        },
        "share_rows": [],
        "overlay_rows": [],
        "proxy_rows": [
            {
                "market_id": market_row["market_id"],
                "proxy_id": safe_text(rule_row.get("provider_or_proxy_label") or market_row.get("provider_or_proxy_label")),
                "proxy_label": safe_text(rule_row.get("provider_or_proxy_label") or market_row.get("provider_or_proxy_label")),
                "proxy_type": "background_inherited",
                "background_source_db": safe_text(rule_row.get("background_source_db")),
                "source_reference": safe_text(rule_row.get("source_reference") or market_row.get("source_reference")),
                "notes": safe_text(rule_row.get("notes") or market_row.get("notes")),
            }
        ],
    }
