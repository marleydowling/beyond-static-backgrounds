from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


import argparse

import pandas as pd

from framework.foreground_routes._bw_common import configure_brightway, make_dataset, safe_delete_database


def _text(x) -> str:
    return "" if pd.isna(x) else str(x)


def build_market_proxy_db(config_path: str, register_csv: str, shares_csv: str, overlay_csv: str, proxy_csv: str, target_db: str, overwrite: bool = False) -> None:
    bd, _cfg = configure_brightway(config_path)

    if overwrite:
        safe_delete_database(bd, target_db)
    elif target_db in bd.databases:
        raise RuntimeError(f"Target DB already exists: {target_db}. Use --overwrite to replace it.")

    r = pd.read_csv(register_csv)
    s = pd.read_csv(shares_csv)
    o = pd.read_csv(overlay_csv)
    p = pd.read_csv(proxy_csv)

    datasets = {}

    for _, row in s.iterrows():
        code = f"share::{row['market_id']}::{_text(row.get('supplier_id'))}"
        datasets[(target_db, code)] = make_dataset(
            target_db,
            code,
            name=f"step4a supplier share :: {row['market_id']} :: {_text(row.get('supplier_name'))}",
            reference_product=_text(row.get("provider_or_proxy_label")) or "supplier share",
            unit="unit",
            location=_text(row.get("supplier_location")) or "GLO",
            comment=f"Step 4A supplier-share placeholder for market {row['market_id']}.",
            extra={
                "market_id": _text(row.get("market_id")),
                "representation_method": _text(row.get("representation_method")),
                "supplier_id": _text(row.get("supplier_id")),
                "supplier_name": _text(row.get("supplier_name")),
                "resolved_share": float(row.get("resolved_share", 0.0)),
            },
        )

    for _, row in p.iterrows():
        code = f"proxy::{row['market_id']}::{_text(row.get('proxy_id'))}"
        datasets[(target_db, code)] = make_dataset(
            target_db,
            code,
            name=f"step4a proxy :: {row['market_id']} :: {_text(row.get('proxy_label'))}",
            reference_product=_text(row.get("proxy_label")) or "proxy",
            unit="unit",
            location="GLO",
            comment=f"Step 4A inherited/proxy placeholder for market {row['market_id']}.",
            extra={
                "market_id": _text(row.get("market_id")),
                "proxy_id": _text(row.get("proxy_id")),
                "proxy_label": _text(row.get("proxy_label")),
                "proxy_type": _text(row.get("proxy_type")),
            },
        )

    for _, row in o.iterrows():
        code = f"overlay::{row['market_id']}::{_text(row.get('overlay_id'))}"
        datasets[(target_db, code)] = make_dataset(
            target_db,
            code,
            name=f"step4a overlay component :: {row['market_id']} :: {_text(row.get('overlay_label'))}",
            reference_product=_text(row.get("overlay_provider_label")) or "overlay component",
            unit="unit",
            location="GLO",
            comment=f"Step 4A overlay component placeholder for market {row['market_id']}.",
            extra={
                "market_id": _text(row.get("market_id")),
                "overlay_id": _text(row.get("overlay_id")),
                "overlay_label": _text(row.get("overlay_label")),
                "overlay_provider_label": _text(row.get("overlay_provider_label")),
            },
        )

    for _, row in r.iterrows():
        market_id = _text(row["market_id"])
        code = f"market::{market_id}"
        ds = make_dataset(
            target_db,
            code,
            name=f"step4a market proxy :: {market_id}",
            reference_product=_text(row.get("displaced_product")) or _text(row.get("credited_output")) or "market proxy",
            unit="unit",
            location=_text(row.get("market_geography")) or "GLO",
            comment=f"Step 4A market proxy materialized from Step 3 register for {market_id}.",
            extra={
                "market_id": market_id,
                "resolved_method": _text(row.get("resolved_method")),
                "resolution_basis": _text(row.get("resolution_basis")),
                "representation_category": _text(row.get("representation_category")),
                "scenario": _text(row.get("scenario")),
                "receiving_system": _text(row.get("receiving_system")),
            },
        )

        share_rows = s.loc[s["market_id"] == market_id].copy() if not s.empty else pd.DataFrame()
        proxy_rows = p.loc[p["market_id"] == market_id].copy() if not p.empty else pd.DataFrame()

        if not share_rows.empty:
            for _, srow in share_rows.iterrows():
                child_code = f"share::{market_id}::{_text(srow.get('supplier_id'))}"
                ds["exchanges"].append(
                    {
                        "input": (target_db, child_code),
                        "amount": float(srow["resolved_share"]),
                        "type": "technosphere",
                        "name": f"supplier share input :: {market_id}",
                        "product": _text(srow.get("provider_or_proxy_label")) or "supplier share",
                        "unit": "unit",
                    }
                )
        elif not proxy_rows.empty:
            count = len(proxy_rows)
            for _, prow in proxy_rows.iterrows():
                child_code = f"proxy::{market_id}::{_text(prow.get('proxy_id'))}"
                ds["exchanges"].append(
                    {
                        "input": (target_db, child_code),
                        "amount": 1.0 / count,
                        "type": "technosphere",
                        "name": f"proxy input :: {market_id}",
                        "product": _text(prow.get("proxy_label")) or "proxy",
                        "unit": "unit",
                    }
                )
        datasets[(target_db, code)] = ds

    bd.Database(target_db).write(datasets)
    print(f"[ok] wrote Step 4A market proxy DB: {target_db}")
    print(f"[ok] activities written: {len(datasets)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a minimal Step 4A Brightway foreground DB from Step 3 outputs.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--register-csv", required=True)
    parser.add_argument("--shares-csv", required=True)
    parser.add_argument("--overlay-csv", required=True)
    parser.add_argument("--proxy-csv", required=True)
    parser.add_argument("--target-db", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    build_market_proxy_db(
        config_path=args.config,
        register_csv=args.register_csv,
        shares_csv=args.shares_csv,
        overlay_csv=args.overlay_csv,
        proxy_csv=args.proxy_csv,
        target_db=args.target_db,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
