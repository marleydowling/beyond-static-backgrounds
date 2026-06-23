from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from framework.foreground_routes._bw_common import configure_brightway


def main() -> None:
    parser = argparse.ArgumentParser(description="List LCIA methods in the active Brightway project and optionally write a CSV template.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--contains", default="")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--out-csv")
    parser.add_argument("--primary-method-index", type=int, default=0)
    args = parser.parse_args()

    bd, _cfg = configure_brightway(args.config)
    methods = list(bd.methods)
    query = args.contains.lower().strip()
    if query:
        methods = [m for m in methods if query in " | ".join(map(str, m)).lower()]

    if not methods:
        raise RuntimeError(
            f"No LCIA methods matched contains='{args.contains}'. Try omitting --contains or using a broader filter."
        )

    methods = methods[: args.limit]
    for i, method in enumerate(methods):
        print(f"[{i}] {method}")

    if args.out_csv:
        rows = []
        for i, method in enumerate(methods):
            rows.append(
                {
                    "method_id": f"method_{i}" if i != args.primary_method_index else "primary_indicator",
                    "is_primary": "Yes" if i == args.primary_method_index else "No",
                    "method_tuple_json": json.dumps(list(method)),
                    "notes": "Exported from local Brightway project",
                }
            )
        out = Path(args.out_csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["method_id", "is_primary", "method_tuple_json", "notes"])
            writer.writeheader()
            writer.writerows(rows)
        print(f"[ok] wrote methods CSV: {out}")


if __name__ == "__main__":
    main()
