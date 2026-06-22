# Repository Setup Guide

This guide documents the current methods-only repository setup.

## 1. Clone the repository

Clone the repository and work from the repository root.

## 2. Create the software environment

```bash
conda env create -f env/environment.yml
conda activate bss-repo-dev
```

## 3. Local-only working material

Keep probes, scratch files, exports, helper scripts, and run outputs under `_local/`. This directory is gitignored and is not part of the public repository.

Recommended local-only layout:

```text
_local/
  tests/
  runs/
  logs/
  scratch/
  setup/
```

## 4. Brightway workspace

Create a dedicated Brightway data root for repository development, for example:

- `C:\brightway_workspace\beyond_static_backgrounds\brightway_base`
- `C:\brightway_workspace\beyond_static_backgrounds\logs`

## 5. ecoinvent access

The baseline contemporary import uses Brightway's official ecoinvent release importer.

Provide valid ecoinvent access credentials either through:
- `EI_USERNAME`
- `EI_PASSWORD`

or through a working local `ecoinvent_interface` configuration.

Do **not** store credentials in tracked repository files.

## 6. premise and IAM access

Prospective background construction is implemented through `premise`.

If your local workflow requires an IAM access key, define it through the environment variable named in the YAML config, for example:
- `PREMISE_KEY`

Do **not** store keys in tracked repository files.

## 7. Working example config

The working example config is:

- `framework/backgrounds/configs/example_background_pipeline.yaml`

## 8. Current implementation status

### Implemented
- Step 1A: rebuild version-aligned biosphere
- Step 1B: import contemporary consequential baseline using Brightway's official importer
- Step 2: prospective background construction scaffolding using premise

### Scaffolded for next development
- Step 3: displaced-market registers and marginal-supplier logic
- Step 4: route wrappers and explicit Module D execution

## 9. Notes on testing

Public repository code should remain focused on methods scripts and documentation.
Functional run testing should be performed from `_local/tests/` and `_local/runs/` so that logs and outputs remain untracked.
