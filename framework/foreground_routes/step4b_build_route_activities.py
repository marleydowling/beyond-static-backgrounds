from __future__ import annotations

import argparse

import pandas as pd

from framework.foreground_routes._bw_common import configure_brightway, make_dataset, safe_delete_database


def _text(x) -> str:
    return "" if pd.isna(x) else str(x)


def build_route_activity_db(config_path: str, route_activities_csv: str, market_db: str, target_db: str, overwrite: bool = False, credit_as_negative_technosphere: bool = True) -> None:
    bd, _cfg = configure_brightway(config_path)

    if overwrite:
        safe_delete_database(bd, target_db)
    elif target_db in bd.databases:
        raise RuntimeError(f"Target DB already exists: {target_db}. Use --overwrite to replace it.")

    routes = pd.read_csv(route_activities_csv)
    datasets = {}

    for _, row in routes.iterrows():
        route_id = _text(row["route_id"])
        burden_code = f"burden::{route_id}"
        route_code = f"route::{route_id}"
        credit_market_id = _text(row.get("credit_market_id"))
        credit_amount = float(row.get("credit_amount", 0.0))
        burden_amount = float(row.get("burden_amount", 1.0))

        datasets[(target_db, burden_code)] = make_dataset(
            target_db,
            burden_code,
            name=f"step4b burden proxy :: {route_id}",
            reference_product=_text(row.get("burden_proxy_name")) or "burden proxy",
            unit="unit",
            location=_text(row.get("receiving_system")) or "GLO",
            comment=f"Step 4B burden-side placeholder for {route_id}. Replace with linked route-side burdens when exact provider mappings are available.",
            extra={
                "route_id": route_id,
                "route_family": _text(row.get("route_family")),
                "burden_proxy_name": _text(row.get("burden_proxy_name")),
            },
        )

        ds = make_dataset(
            target_db,
            route_code,
            name=f"step4b foreground route activity :: {route_id}",
            reference_product=_text(row.get("route_name")) or route_id,
            unit="unit",
            location=_text(row.get("receiving_system")) or "GLO",
            comment=f"Step 4B foreground route activity for {route_id}. Positive burden proxy plus explicit Module D proxy exchange.",
            extra={
                "route_id": route_id,
                "route_name": _text(row.get("route_name")),
                "route_family": _text(row.get("route_family")),
                "scenario": _text(row.get("scenario")),
                "credit_market_id": credit_market_id,
                "substitution_ratio": float(row.get("substitution_ratio", 0.0)),
                "qualifying_yield": float(row.get("qualifying_yield", 0.0)),
                "credit_amount": credit_amount,
                "equivalence_gate": _text(row.get("equivalence_gate")),
                "conditioning_before_credit": _text(row.get("conditioning_before_credit")),
                "exclusion_rule": _text(row.get("exclusion_rule")),
            },
        )

        ds["exchanges"].append(
            {
                "input": (target_db, burden_code),
                "amount": burden_amount,
                "type": "technosphere",
                "name": f"burden proxy input :: {route_id}",
                "product": _text(row.get("burden_proxy_name")) or "burden proxy",
                "unit": "unit",
            }
        )

        if credit_market_id:
            market_code = f"market::{credit_market_id}"
            ds["exchanges"].append(
                {
                    "input": (market_db, market_code),
                    "amount": -credit_amount if credit_as_negative_technosphere else credit_amount,
                    "type": "technosphere",
                    "name": f"explicit Module D proxy :: {route_id}",
                    "product": "market proxy",
                    "unit": "unit",
                }
            )

        datasets[(target_db, route_code)] = ds

    bd.Database(target_db).write(datasets)
    print(f"[ok] wrote Step 4B foreground route activity DB: {target_db}")
    print(f"[ok] activities written: {len(datasets)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build minimal Step 4B foreground route activities from Step 3/4A objects.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--route-activities-csv", required=True)
    parser.add_argument("--market-db", required=True)
    parser.add_argument("--target-db", required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--credit-as-negative-technosphere", action="store_true")
    args = parser.parse_args()

    build_route_activity_db(
        config_path=args.config,
        route_activities_csv=args.route_activities_csv,
        market_db=args.market_db,
        target_db=args.target_db,
        overwrite=args.overwrite,
        credit_as_negative_technosphere=args.credit_as_negative_technosphere,
    )


if __name__ == "__main__":
    main()
