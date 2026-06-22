# Background pipeline

This directory contains the methods scripts for Step 1 and Step 2.

## Step 1 — baseline background preparation

Active scripts:
- `step1_rebuild_biosphere.py`
- `step1_import_contemporary_background.py`

Current baseline logic:
- rebuild a version-aligned biosphere database
- import the contemporary consequential baseline using Brightway's official ecoinvent release importer

## Step 2 — prospective background construction

Active scripts:
- `step2_build_premise_backgrounds.py`
- `step2_version_manifest.py`
- `step2_freeze_and_audit.py`
- `step2_relink_energy_and_fuels.py`

This layer is intended to remain generic:
- users should be able to substitute a different IAM
- users should be able to substitute a different ecoinvent release
- users should be able to toggle prospective background uncertainty retention where supported
