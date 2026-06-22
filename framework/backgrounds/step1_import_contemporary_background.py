from __future__ import annotations

"""
Step 1B — import the contemporary consequential background database
using Brightway's official ecoinvent release importer.

Notes
-----
- Sets BRIGHTWAY2_DIR before importing bw2data / bw2io
- Uses bw2io.ecoinvent.import_ecoinvent_release(...)
- Does NOT call bw2setup()
- Imports LCI only (not LCIA methods) for this repo workflow
- Expects credentials either:
  1) from environment variables EI_USERNAME / EI_PASSWORD, or
  2) already configured externally through ecoinvent_interface
"""

import os
from pathlib import Path

from _common import TeeLogger, load_yaml, ts_utc


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument(
        "--release-version",
        default="3.10.1",
        help="Actual ecoinvent release version string for the official importer, e.g. 3.10.1",
    )
    parser.add_argument(
        "--system-model",
        default="consequential",
        help="ecoinvent system model, e.g. consequential, cutoff, apos",
    )
    parser.add_argument(
        "--biosphere-write-mode",
        choices=["replace", "patch"],
        default="patch",
    )
    parser.add_argument(
        "--use-mp",
        action="store_true",
        help="Use multiprocessing during import",
    )
    args = parser.parse_args()

    cfg = load_yaml(args.config)

    # IMPORTANT: set before importing bw2data / bw2io
    os.environ["BRIGHTWAY2_DIR"] = cfg["project"]["brightway2_dir"]

    import bw2data as bd
    import bw2io as bi

    bd.projects.set_current(cfg["project"]["name"])

    outputs = cfg["outputs"]
    biosphere_name = cfg["source"]["biosphere_name"]

    run_log_dir = Path(outputs["run_log_dir"])
    run_log_dir.mkdir(parents=True, exist_ok=True)
    logger = TeeLogger(
        run_log_dir / f"step1_import_contemporary_{ts_utc().replace(':', '').replace('.', '')}.log"
    )

    username = os.environ.get("EI_USERNAME")
    password = os.environ.get("EI_PASSWORD")

    logger.log(f"[info] project={bd.projects.current}")
    logger.log(f"[info] release_version={args.release_version}")
    logger.log(f"[info] system_model={args.system_model}")
    logger.log(f"[info] biosphere_name={biosphere_name}")
    logger.log(f"[info] lcia=False")
    logger.log(
        "[info] credentials_source="
        + ("environment variables EI_USERNAME/EI_PASSWORD" if username and password else "external ecoinvent_interface config")
    )

    bi.import_ecoinvent_release(
        version=args.release_version,
        system_model=args.system_model,
        username=username,
        password=password,
        lci=True,
        lcia=False,
        biosphere_name=biosphere_name,
        biosphere_write_mode=args.biosphere_write_mode,
        use_mp=args.use_mp,
    )

    logger.log(f"[done] import complete")
    logger.log(f"[done] current databases={list(bd.databases)}")
    logger.close()


if __name__ == "__main__":
    main()