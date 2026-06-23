from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a primary-indicator decomposition table from Step 4C LCIA results.")
    parser.add_argument("--results-csv", required=True)
    parser.add_argument("--role-map-csv", required=True)
    parser.add_argument("--primary-method-id", default="primary_indicator")
    parser.add_argument("--out-decomposition-csv", required=True)
    args = parser.parse_args()

    results = pd.read_csv(args.results_csv)
    role_map = pd.read_csv(args.role_map_csv)

    required_results = {"route_id", "activity_code", "method_id", "score"}
    missing = required_results - set(results.columns)
    if missing:
        raise ValueError(f"Results CSV is missing required columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("Results CSV is empty.")

    results = results.loc[results["method_id"] == args.primary_method_id].copy()
    if results.empty:
        raise RuntimeError(f"No rows found in results CSV for method_id={args.primary_method_id}")

    results["score"] = pd.to_numeric(results["score"], errors="raise")
    score_map = {(str(r["route_id"]), str(r["activity_code"])): float(r["score"]) for _, r in results.iterrows()}

    out_rows = []
    for _, row in role_map.iterrows():
        route_id = str(row["route_id"])
        route_name = str(row.get("route_name", route_id))
        c34_code = str(row["c34_activity_code"])
        stage_d_code = str(row["stage_d_activity_code"])
        net_code = str(row["net_activity_code"])

        needed = [(route_id, c34_code), (route_id, stage_d_code), (route_id, net_code)]
        missing_keys = [k for k in needed if k not in score_map]
        if missing_keys:
            raise KeyError(f"Missing role-map keys in results CSV: {missing_keys}")

        c34 = score_map[(route_id, c34_code)]
        stage_d = score_map[(route_id, stage_d_code)]
        net = score_map[(route_id, net_code)]

        out_rows.append(
            {
                "route_id": route_id,
                "route_name": route_name,
                "c34_score": c34,
                "stage_d_score": stage_d,
                "net_score": net,
                "notes": "Built automatically from Step 4C results and a local role map.",
            }
        )

    out_df = pd.DataFrame(out_rows)
    out = Path(args.out_decomposition_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out, index=False)
    print(f"[ok] wrote decomposition CSV: {out}")


if __name__ == "__main__":
    main()
