# Repository Setup Guide

This guide documents the public, methods-only repository setup.

## 1. Clone the repository

Clone the repository and work from the repository root.

## 2. Create the software environment

```bash
conda env create -f env/environment.yml
conda activate bss-repo-dev
```

## 3. Local working files

Users should keep machine-specific configs, credentials, exact provider mappings, run outputs, and temporary test artefacts outside the tracked public methods scaffold. A common pattern is to use a gitignored local workspace such as `_local/`, but any equivalent untracked location is acceptable.

A typical local layout may include:

```text
_local/
  setup/
  tests/
  runs/
  logs/
  scratch/
```

## 4. Public template config versus local run config

The tracked config file:

- `framework/backgrounds/configs/example_background_pipeline.yaml`

is a public example template.

Create a local run config by copying that template to an untracked location and replacing the placeholder values with machine-specific paths and settings, including:

- Brightway data root
- local ecoinvent/ecospold source path
- local IAM output path, where needed
- Brightway project name
- IAM model, pathway, year, and foresight choice
- output and audit paths

## 5. Brightway workspace

Use a dedicated Brightway data root for repository development and local testing. The repository does not prescribe a single filesystem layout, but the local config should point to a writable Brightway workspace and any local output directories required by the workflow.

## 6. ecoinvent access

The contemporary baseline import uses Brightway's official ecoinvent release importer.

Provide valid ecoinvent access credentials through environment variables or a working local `ecoinvent_interface` setup. Do not place credentials in tracked repository files.

## 7. premise and IAM access

Prospective background construction is implemented through `premise`.

If a local workflow requires an IAM access key, define it through the environment variable named in the local YAML config. Do not store keys in tracked repository files.

## 8. Step 1 versus Step 2 source expectations

### Step 1
Step 1 uses Brightway's official ecoinvent release importer for the contemporary baseline.

### Step 2
Step 2 expects local ecospold inputs and local IAM outputs, or an equivalent authenticated `premise` setup. The YAML therefore acts as a variable map for local inputs rather than as a data container.

## 9. Current implementation status

### Implemented
- Step 1A: rebuild version-aligned biosphere
- Step 1B: import contemporary consequential baseline using Brightway's official importer
- Step 2: prospective background construction scaffolding using premise

### Scaffolded for next development
- Step 3: displaced-market registers and marginal-supplier logic
- Step 4: foreground route activities and explicit Module D execution

## 10. Local exact-link workflow

The public repository does not include exact licensed provider codes.

Users who want to reproduce exact local provider resolution should create an untracked provider-resolution file from the public template, populate it with machine-specific `(database, code)` mappings, and use that local mapping during exact-link testing or case-specific reruns.

This keeps the public repository publishable while still allowing local exact verification against licensed data.
