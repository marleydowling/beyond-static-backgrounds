from __future__ import annotations

from typing import Dict, List

import pandas as pd


ALLOWED_METHODS = {
    "inherit_background",
    "custom_empirical_mix",
    "crr_screen",
    "weidema_heuristic",
    "proxy_provider",
    "prospective_overlay",
}

REQUIRED_MARKET_COLUMNS = [
    "market_id",
    "market_role",
    "route_or_use",
    "receiving_system",
    "booking_year",
    "scenario",
    "credited_output",
    "displaced_product",
    "market_geography",
    "representation_method",
    "representation_category",
]

REQUIRED_RULE_COLUMNS = [
    "market_id",
    "method",
]

REQUIRED_SUPPLIER_COLUMNS = [
    "market_id",
    "supplier_name",
]

REQUIRED_PROVIDER_PROXY_COLUMNS = [
    "market_id",
    "proxy_id",
    "proxy_label",
]

REQUIRED_OVERLAY_COLUMNS = [
    "market_id",
    "overlay_id",
    "overlay_label",
    "overlay_provider_label",
]


def _require_columns(df: pd.DataFrame, required: List[str], name: str) -> List[str]:
    return [f"{name}: missing column '{c}'" for c in required if c not in df.columns]


def validate_step3_bundle(tables: Dict[str, pd.DataFrame]) -> List[str]:
    errors: List[str] = []

    markets = tables["markets"]
    rules = tables["rules"]
    suppliers = tables.get("suppliers", pd.DataFrame())
    provider_proxy = tables.get("provider_proxy", pd.DataFrame())
    overlay_rules = tables.get("overlay_rules", pd.DataFrame())

    errors += _require_columns(markets, REQUIRED_MARKET_COLUMNS, "markets")
    errors += _require_columns(rules, REQUIRED_RULE_COLUMNS, "rules")

    if not suppliers.empty:
        errors += _require_columns(suppliers, REQUIRED_SUPPLIER_COLUMNS, "suppliers")
    if not provider_proxy.empty:
        errors += _require_columns(provider_proxy, REQUIRED_PROVIDER_PROXY_COLUMNS, "provider_proxy")
    if not overlay_rules.empty:
        errors += _require_columns(overlay_rules, REQUIRED_OVERLAY_COLUMNS, "overlay_rules")

    if errors:
        return errors

    if markets["market_id"].duplicated().any():
        dupes = sorted(markets.loc[markets["market_id"].duplicated(), "market_id"].astype(str).unique())
        errors.append(f"markets: duplicate market_id values: {dupes}")

    rule_market_ids = set(rules["market_id"].astype(str))
    market_ids = set(markets["market_id"].astype(str))
    missing_rules = sorted(market_ids - rule_market_ids)
    if missing_rules:
        errors.append(f"rules: missing rule rows for market_id values: {missing_rules}")

    for _, row in rules.iterrows():
        method = str(row["method"])
        if method not in ALLOWED_METHODS:
            errors.append(f"rules: unsupported method '{method}' for market_id={row['market_id']}")

    merged = markets[["market_id", "representation_method"]].merge(
        rules[["market_id", "method"]], on="market_id", how="left"
    )
    mismatched = merged.loc[merged["representation_method"] != merged["method"]]
    for _, row in mismatched.iterrows():
        errors.append(
            f"rules: representation_method '{row['representation_method']}' does not match method '{row['method']}' for market_id={row['market_id']}"
        )

    methods_need_suppliers = {"custom_empirical_mix", "crr_screen", "weidema_heuristic", "prospective_overlay"}
    for market_id, method in merged[["market_id", "method"]].itertuples(index=False):
        if method in methods_need_suppliers:
            if suppliers.empty or market_id not in set(suppliers["market_id"].astype(str)):
                if method == "prospective_overlay":
                    rule = rules.loc[rules["market_id"] == market_id].iloc[0]
                    src = rule.get("identity_source_market_id")
                    if pd.isna(src):
                        errors.append(f"suppliers: no supplier rows for overlay market {market_id} and no identity_source_market_id given")
                    else:
                        if suppliers.empty or str(src) not in set(suppliers["market_id"].astype(str)):
                            errors.append(f"suppliers: identity_source_market_id '{src}' for overlay market {market_id} has no supplier rows")
                else:
                    errors.append(f"suppliers: no supplier rows provided for market_id={market_id} ({method})")

        if method == "proxy_provider":
            if provider_proxy.empty or market_id not in set(provider_proxy["market_id"].astype(str)):
                errors.append(f"provider_proxy: no provider rows provided for market_id={market_id} ({method})")

        if method == "prospective_overlay":
            if overlay_rules.empty or market_id not in set(overlay_rules["market_id"].astype(str)):
                errors.append(f"overlay_rules: no overlay rows provided for market_id={market_id} ({method})")

    return errors
