from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from framework.foreground_routes._bw_common import configure_brightway


def load_methods(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = ["method_id", "is_primary", "method_tuple_json"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in methods CSV: {missing}")
    if df.empty:
        raise ValueError(
            "The methods CSV is empty. Export at least one local LCIA method first, "
            "or rerun list_lcia_methods without an over-restrictive filter."
        )
    out = df.copy()
    out["is_primary"] = (
        out["is_primary"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin({"true", "yes", "1", "y"})
    )
    return out


def load_demands(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = ["route_id", "activity_code", "demand_amount"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in demand CSV: {missing}")
    if df.empty:
        raise ValueError("The demands CSV is empty.")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Run configurable LCIA methods against a local route database.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--demands-csv", required=True)
    parser.add_argument("--methods-csv", required=True)
    parser.add_argument("--out-results-csv", required=True)
    parser.add_argument("--out-primary-summary-csv")
    args = parser.parse_args()

    bd, _cfg = configure_brightway(args.config)
    import bw2calc as bc

    if args.db not in bd.databases:
        raise RuntimeError(f"Database not found: {args.db}")

    db = bd.Database(args.db)
    activities = {act["code"]: act for act in db}

    demands = load_demands(args.demands_csv)
    methods = load_methods(args.methods_csv)

    print(f"[info] routes to evaluate: {len(demands)}")
    print(f"[info] LCIA methods to run: {len(methods)}")

    rows = []
    for _, drow in demands.iterrows():
        code = str(drow["activity_code"])
        if code not in activities:
            raise KeyError(f"Activity code not found in {args.db}: {code}")
        act = activities[code]
        demand_amount = float(drow["demand_amount"])

        for _, mrow in methods.iterrows():
            method_tuple = tuple(json.loads(mrow["method_tuple_json"]))
            lca = bc.LCA({act: demand_amount}, method=method_tuple)
            lca.lci()
            lca.lcia()
            rows.append(
                {
                    "route_id": str(drow["route_id"]),
                    "activity_code": code,
                    "demand_amount": demand_amount,
                    "method_id": str(mrow["method_id"]),
                    "is_primary": bool(mrow["is_primary"]),
                    "method_tuple_json": json.dumps(list(method_tuple)),
                    "score": float(lca.score),
                }
            )

    if not rows:
        raise RuntimeError(
            "No LCIA rows were produced. Check the methods CSV, demand CSV, and selected database."
        )

    out_df = pd.DataFrame(rows)
    Path(args.out_results_csv).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.out_results_csv, index=False)
    print(f"[ok] wrote LCIA results: {args.out_results_csv}")

    if args.out_primary_summary_csv:
        primary = out_df.loc[out_df["is_primary"] == True].copy()
        if primary.empty:
            raise RuntimeError("No primary methods were flagged in the methods CSV.")
        primary.to_csv(args.out_primary_summary_csv, index=False)
        print(f"[ok] wrote primary summary seed: {args.out_primary_summary_csv}")


if __name__ == "__main__":
    main()
