from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from framework.market_definition.load_market_register import load_step3_bundle
from framework.market_definition.validate_market_register import validate_step3_bundle
from framework.marginal_supplier_logic.methods_custom_empirical_mix import build_market as build_custom_empirical_mix
from framework.marginal_supplier_logic.methods_crr import build_market as build_crr_screen
from framework.marginal_supplier_logic.methods_weidema_heuristic import build_market as build_weidema_heuristic
from framework.marginal_supplier_logic.methods_inherit_from_background import build_market as build_inherit_background
from framework.marginal_supplier_logic.methods_proxy_provider import build_market as build_proxy_provider
from framework.marginal_supplier_logic.methods_prospective_overlay import build_market as build_prospective_overlay


def build_step3_register(tables: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict[str, object]]]:
    errors = validate_step3_bundle(tables)
    if errors:
        raise ValueError("\\n".join(errors))

    markets = tables["markets"]
    rules = tables["rules"]
    suppliers = tables.get("suppliers", pd.DataFrame())
    provider_proxy = tables.get("provider_proxy", pd.DataFrame())
    overlay_rules = tables.get("overlay_rules", pd.DataFrame())

    register_rows: List[Dict[str, object]] = []
    share_rows: List[Dict[str, object]] = []
    overlay_rows_out: List[Dict[str, object]] = []
    proxy_rows_out: List[Dict[str, object]] = []

    for _, market_row in markets.iterrows():
        market_id = market_row["market_id"]
        rule_row = rules.loc[rules["market_id"] == market_id].iloc[0]
        method = str(rule_row["method"])

        supplier_rows = suppliers.loc[suppliers["market_id"] == market_id].copy() if not suppliers.empty else pd.DataFrame()
        provider_rows = provider_proxy.loc[provider_proxy["market_id"] == market_id].copy() if not provider_proxy.empty else pd.DataFrame()
        overlay_rows = overlay_rules.loc[overlay_rules["market_id"] == market_id].copy() if not overlay_rules.empty else pd.DataFrame()

        if method == "custom_empirical_mix":
            result = build_custom_empirical_mix(market_row, rule_row, supplier_rows)
        elif method == "crr_screen":
            result = build_crr_screen(market_row, rule_row, supplier_rows)
        elif method == "weidema_heuristic":
            result = build_weidema_heuristic(market_row, rule_row, supplier_rows)
        elif method == "inherit_background":
            result = build_inherit_background(market_row, rule_row)
        elif method == "proxy_provider":
            result = build_proxy_provider(market_row, rule_row, provider_rows)
        elif method == "prospective_overlay":
            result = build_prospective_overlay(market_row, rule_row, supplier_rows, suppliers, overlay_rows)
        else:
            raise ValueError(f"Unsupported method: {method}")

        register_rows.append(
            {
                **market_row.to_dict(),
                "resolved_method": result["summary"].get("resolved_method"),
                "resolution_basis": result["summary"].get("resolution_basis"),
                "share_count": result["summary"].get("share_count", 0),
                "share_sum": result["summary"].get("share_sum"),
                "overlay_component_count": result["summary"].get("overlay_component_count", 0),
                "overlay_status": result["summary"].get("overlay_status"),
                "background_source_db": result["summary"].get("background_source_db"),
            }
        )
        share_rows.extend(result["share_rows"])
        overlay_rows_out.extend(result["overlay_rows"])
        proxy_rows_out.extend(result["proxy_rows"])

    return {
        "register_rows": register_rows,
        "share_rows": share_rows,
        "overlay_rows": overlay_rows_out,
        "proxy_rows": proxy_rows_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Step 3 displaced-market and marginal-supplier register.")
    parser.add_argument("--markets-csv", required=True)
    parser.add_argument("--rules-csv", required=True)
    parser.add_argument("--supplier-candidates-csv")
    parser.add_argument("--provider-proxy-csv")
    parser.add_argument("--overlay-rules-csv")
    parser.add_argument("--out-register-csv", required=True)
    parser.add_argument("--out-shares-csv", required=True)
    parser.add_argument("--out-overlay-csv")
    parser.add_argument("--out-proxy-csv")
    parser.add_argument("--out-register-json")
    args = parser.parse_args()

    tables = load_step3_bundle(
        market_csv=args.markets_csv,
        rules_csv=args.rules_csv,
        supplier_candidates_csv=args.supplier_candidates_csv,
        provider_proxy_csv=args.provider_proxy_csv,
        overlay_rules_csv=args.overlay_rules_csv,
    )
    outputs = build_step3_register(tables)

    register_df = pd.DataFrame(outputs["register_rows"])
    shares_df = pd.DataFrame(outputs["share_rows"])
    overlay_df = pd.DataFrame(outputs["overlay_rows"])
    proxy_df = pd.DataFrame(outputs["proxy_rows"])

    Path(args.out_register_csv).parent.mkdir(parents=True, exist_ok=True)
    register_df.to_csv(args.out_register_csv, index=False)
    shares_df.to_csv(args.out_shares_csv, index=False)

    if args.out_overlay_csv:
        Path(args.out_overlay_csv).parent.mkdir(parents=True, exist_ok=True)
        overlay_df.to_csv(args.out_overlay_csv, index=False)
    if args.out_proxy_csv:
        Path(args.out_proxy_csv).parent.mkdir(parents=True, exist_ok=True)
        proxy_df.to_csv(args.out_proxy_csv, index=False)
    if args.out_register_json:
        Path(args.out_register_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out_register_json, "w", encoding="utf-8") as f:
            json.dump(outputs, f, indent=2)

    print(f"[ok] wrote register: {args.out_register_csv}")
    print(f"[ok] wrote shares:   {args.out_shares_csv}")
    if args.out_overlay_csv:
        print(f"[ok] wrote overlay:  {args.out_overlay_csv}")
    if args.out_proxy_csv:
        print(f"[ok] wrote proxies:  {args.out_proxy_csv}")
    if args.out_register_json:
        print(f"[ok] wrote json:     {args.out_register_json}")


if __name__ == "__main__":
    main()
