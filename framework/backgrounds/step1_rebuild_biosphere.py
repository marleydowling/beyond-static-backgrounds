from __future__ import annotations

"""
Step 1 — rebuild a version-aligned biosphere database from ecoinvent MasterData.

This version fixes two issues:
1. It sets BRIGHTWAY2_DIR before importing bw2data
2. It uses Ecospold2BiosphereImporter with explicit named arguments
"""

import os
from pathlib import Path

from _common import load_yaml


def find_elementary_exchanges_xml(root: Path) -> Path:
    candidates = list(root.rglob("ElementaryExchanges.xml"))
    if not candidates:
        raise FileNotFoundError(
            f"Could not find ElementaryExchanges.xml under {root}. "
            "Use the extracted ecoinvent release root containing datasets/ and MasterData/."
        )
    candidates.sort(key=lambda p: ("masterdata" not in str(p).lower(), len(str(p))))
    return candidates[0]


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--ecoinvent-release-root", required=True)
    parser.add_argument("--write-mode", choices=["replace", "patch"], default="replace")
    args = parser.parse_args()

    cfg = load_yaml(args.config)

    # IMPORTANT: set this before importing bw2data/bw2io
    os.environ["BRIGHTWAY2_DIR"] = cfg["project"]["brightway2_dir"]

    import bw2data as bd
    from bw2io.importers.ecospold2_biosphere import Ecospold2BiosphereImporter

    bd.projects.set_current(cfg["project"]["name"])

    target_db = cfg["source"].get("biosphere_name", "ecoinvent-3.10-biosphere")
    release_root = Path(args.ecoinvent_release_root)
    elementary_xml = find_elementary_exchanges_xml(release_root)

    if args.write_mode == "replace" and target_db in bd.databases:
        del bd.databases[target_db]

    importer = Ecospold2BiosphereImporter(
        name=target_db,
        version=str(cfg["source"].get("source_version", "3.10")),
        filepath=elementary_xml,
    )
    importer.apply_strategies()
    importer.write_database(overwrite=True)

    print(f"[done] biosphere database ready: {target_db}")


if __name__ == "__main__":
    main()