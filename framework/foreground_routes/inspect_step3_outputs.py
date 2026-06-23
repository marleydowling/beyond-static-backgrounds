from __future__ import annotations

import argparse

import pandas as pd


METHOD_HELP = {
    "inherit_background": {
        "purpose": "Use the Step 2 scenario-conditioned background representation directly.",
        "required_inputs": ["markets.csv", "method_rules.csv", "provider_proxy_map.csv (optional but useful)"],
        "what_it_outputs": "A market register row and a proxy/background note rather than computed supplier shares.",
    },
    "custom_empirical_mix": {
        "purpose": "Normalize explicit shares or positive change data into a supplier mix.",
        "required_inputs": ["markets.csv", "method_rules.csv", "supplier_candidates.csv"],
        "what_it_outputs": "Supplier share rows that sum to 1 for the market.",
    },
    "crr_screen": {
        "purpose": "Apply a capital-replacement corrected growth screen before normalizing shares.",
        "required_inputs": ["markets.csv", "method_rules.csv", "supplier_candidates.csv"],
        "what_it_outputs": "Supplier share rows after positive-net-trend or least-decline screening.",
    },
    "weidema_heuristic": {
        "purpose": "Apply a rule-based modernity / competitiveness screen when fully empirical data are limited.",
        "required_inputs": ["markets.csv", "method_rules.csv", "supplier_candidates.csv"],
        "what_it_outputs": "Supplier share rows for the retained heuristic set.",
    },
    "proxy_provider": {
        "purpose": "Represent the displaced product through an explicit proxy provider rather than a computed mix.",
        "required_inputs": ["markets.csv", "method_rules.csv", "provider_proxy_map.csv"],
        "what_it_outputs": "Proxy rows defining the chosen provider boundary condition.",
    },
    "prospective_overlay": {
        "purpose": "Retain a supplier identity structure while attaching future technology overlay families.",
        "required_inputs": ["markets.csv", "method_rules.csv", "supplier_candidates.csv", "overlay_rules.csv"],
        "what_it_outputs": "Supplier share rows plus overlay component rows.",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect Step 3 outputs and explain supported methods.")
    parser.add_argument("--register-csv", required=True)
    parser.add_argument("--shares-csv", required=True)
    parser.add_argument("--overlay-csv", required=True)
    parser.add_argument("--proxy-csv", required=True)
    parser.add_argument("--show-method-help", action="store_true")
    args = parser.parse_args()

    r = pd.read_csv(args.register_csv)
    s = pd.read_csv(args.shares_csv)
    o = pd.read_csv(args.overlay_csv)
    p = pd.read_csv(args.proxy_csv)

    print("[register]")
    cols = [c for c in ["market_id", "resolved_method", "share_count", "overlay_component_count", "background_source_db"] if c in r.columns]
    print(r[cols].to_string(index=False))

    print("\n[share sums]")
    if not s.empty and "market_id" in s.columns and "resolved_share" in s.columns:
        print(s.groupby("market_id")["resolved_share"].sum().to_string())
    else:
        print("(no share rows)")

    print("\n[overlay rows]")
    if not o.empty:
        cols = [c for c in ["market_id", "overlay_id", "overlay_label", "overlay_share"] if c in o.columns]
        print(o[cols].to_string(index=False))
    else:
        print("(no overlay rows)")

    print("\n[proxy rows]")
    if not p.empty:
        cols = [c for c in ["market_id", "proxy_id", "proxy_label", "proxy_type"] if c in p.columns]
        print(p[cols].to_string(index=False))
    else:
        print("(no proxy rows)")

    if args.show_method_help:
        print("\n[method help]")
        for method, payload in METHOD_HELP.items():
            print(f"\n- {method}")
            print(f"  purpose: {payload['purpose']}")
            print(f"  required_inputs: {', '.join(payload['required_inputs'])}")
            print(f"  outputs: {payload['what_it_outputs']}")


if __name__ == "__main__":
    main()
