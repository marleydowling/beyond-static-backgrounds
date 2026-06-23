from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def sign_label(x: float, tol: float = 1e-12) -> str:
    if pd.isna(x):
        return "missing"
    if x > tol:
        return "positive"
    if x < -tol:
        return "negative"
    return "zero"


def coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    bad_cols = []
    for col in cols:
        out[col] = pd.to_numeric(out[col], errors="coerce")
        if out[col].isna().any():
            bad_cols.append(col)
    if bad_cols:
        raise ValueError(
            "Non-numeric or placeholder values detected in decomposition columns: "
            + ", ".join(bad_cols)
            + ". Populate real numeric values first, or build the decomposition automatically from Step 4C results."
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute primary diagnostics and supplementary sign summaries.")
    parser.add_argument("--decomposition-csv", required=True)
    parser.add_argument("--out-primary-diagnostics-csv", required=True)
    parser.add_argument("--supplementary-results-csv")
    parser.add_argument("--out-supplementary-signs-csv")
    parser.add_argument("--out-supplementary-summary-csv")
    parser.add_argument("--c34-col", default="c34_score")
    parser.add_argument("--stage-d-col", default="stage_d_score")
    parser.add_argument("--net-col", default="net_score")
    parser.add_argument("--route-id-col", default="route_id")
    parser.add_argument("--route-name-col", default="route_name")
    parser.add_argument("--dominance-threshold", type=float, default=10.0)
    args = parser.parse_args()

    dec = pd.read_csv(args.decomposition_csv)
    dec = coerce_numeric(dec, [args.c34_col, args.stage_d_col, args.net_col])

    dec["dominance_ratio_abs_stageD_over_abs_c34"] = dec[args.stage_d_col].abs() / dec[args.c34_col].abs().replace({0: np.nan})
    dec["dominance_ge_threshold"] = dec["dominance_ratio_abs_stageD_over_abs_c34"] >= float(args.dominance_threshold)
    dec["c34_sign"] = dec[args.c34_col].map(sign_label)
    dec["stage_d_sign"] = dec[args.stage_d_col].map(sign_label)
    dec["net_sign"] = dec[args.net_col].map(sign_label)

    Path(args.out_primary_diagnostics_csv).parent.mkdir(parents=True, exist_ok=True)
    dec.to_csv(args.out_primary_diagnostics_csv, index=False)
    print(f"[ok] wrote primary diagnostics: {args.out_primary_diagnostics_csv}")

    if args.supplementary_results_csv:
        supp = pd.read_csv(args.supplementary_results_csv)
        supp["score"] = pd.to_numeric(supp["score"], errors="coerce")
        supp["sign"] = supp["score"].map(sign_label)

        if args.out_supplementary_signs_csv:
            Path(args.out_supplementary_signs_csv).parent.mkdir(parents=True, exist_ok=True)
            supp.to_csv(args.out_supplementary_signs_csv, index=False)
            print(f"[ok] wrote supplementary sign rows: {args.out_supplementary_signs_csv}")

        if args.out_supplementary_summary_csv:
            summary = (
                supp.groupby("route_id")["sign"]
                .value_counts()
                .unstack(fill_value=0)
                .reset_index()
            )
            Path(args.out_supplementary_summary_csv).parent.mkdir(parents=True, exist_ok=True)
            summary.to_csv(args.out_supplementary_summary_csv, index=False)
            print(f"[ok] wrote supplementary sign summary: {args.out_supplementary_summary_csv}")


if __name__ == "__main__":
    main()
