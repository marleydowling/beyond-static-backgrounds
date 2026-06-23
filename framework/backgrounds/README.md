# Background pipeline

This directory contains the methods scripts for Step 1 and Step 2.

## Config convention

The tracked config:

- `configs/example_background_pipeline.yaml`

is an example template. Users should copy it into a local, untracked file and replace the placeholder values with their own machine-specific settings.

Recommended local config path:

- `_local/setup/background_pipeline.local.yaml`

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

Step 2 uses:
- a local ecospold dataset path
- a local IAM output path or compatible authenticated premise setup
- a config-defined IAM model / pathway / year / foresight selection

The current paper-facing example corresponds to:
- model: `image`
- pathway: `SSP2-M`
- year: `2050`
- foresight: `perf`

These are example defaults, not required values for all users.

## Sector-update note

The current paper-facing implementation is intended primarily for the energy-system transformation logic demonstrated in the methods workflow, especially electricity and fuel / energy-carrier changes. Broader sector updating depends on premise support and script behavior and should not be assumed automatically.
