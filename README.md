# Beyond Static Backgrounds

This repository is a **methods-only** implementation scaffold for deterministic prospective consequential life cycle assessment (pCLCA) with explicit end-of-life substitution modelling.

It is intended to provide reusable workflow templates and methodological scaffolding for:

1. **Step 1 — baseline conventions and contemporary reference background**
2. **Step 2 — scenario-consistent prospective background construction**
3. **Step 3 — displaced-market definition and marginal-supplier representation**
4. **Step 4 — foreground route modelling and explicit Module D execution**

The repository is **not** intended to be a journal supplementary-information archive or a paper-specific case-study package. Those records belong in submitted online resources and DOI-linked archive materials.

## Repository scope

This repository currently focuses on reusable method components for:

- baseline background preparation
- scenario-consistent prospective background construction
- displaced-market definition
- marginal-supplier mix construction
- explicit substitution-rule implementation
- deterministic post-processing and audit logging

This repository does **not** include:

- the case-study implementation
- submitted supplementary-information resources
- licensed background databases
- imported ecoinvent databases
- premise-generated Brightway databases
- private IAM files or credentials
- local probes, scratch files, exports, and setup helpers
- uncertainty propagation and sensitivity workflows outside the deterministic methods scope

## Structure

```text
framework/
  backgrounds/
  market_definition/
  marginal_supplier_logic/
  foreground_routes/
  substitution_rules/
  postprocess/
  schemas/
  examples/

env/
docs/
```

## Methods logic

### Step 1 — baseline background preparation

Step 1 establishes the baseline background context used as the contemporary reference background system. In the current implementation, this includes:

- rebuilding a version-aligned biosphere database
- importing the contemporary consequential background through Brightway's official ecoinvent release importer

### Step 2 — scenario-consistent prospective background construction

Step 2 constructs deterministic prospective backgrounds using premise. In the current implementation, this includes:

- configuration-driven scenario specification
- prospective background construction for the selected IAM / pathway / year / foresight mode
- versioning and manifest generation
- freeze and audit routines
- optional relinking and inspection utilities for downstream methodological work

### Step 3 — displaced-product markets and marginal supplier mixes

Step 3 is designed as a **register-driven layer** rather than a hard-coded case-study script set.

Planned implementation:
- machine-readable displaced-market register
- machine-readable supplier-candidate table
- trend-input tables
- marginal-mix rule tables
- support for:
  - inherited background mixes
  - CRR-style screening
  - Weidema-style heuristic screening
  - proxy-provider representations

### Step 4 — foreground routes and explicit Module D

Step 4 is designed as a **route-wrapper and substitution-execution layer**.

Planned implementation:
- route register
- route parameter table
- route process map
- equivalence rules
- explicit Module D application
- embedded-credit stripping / neutralization
- auditable claim logs

## External dependencies

This repository builds on external tools and datasets but does not claim authorship of them.

Dependencies include:
- Brightway
- premise
- ecoinvent
- IAM source data

The repository provides orchestration, configuration, validation, and audit logic around those dependencies.

## ecoinvent and IAM setup

### ecoinvent
The baseline contemporary import uses Brightway's official ecoinvent release importer.
Users must provide valid ecoinvent access credentials through either:
- `EI_USERNAME` and `EI_PASSWORD` environment variables, or
- a working local `ecoinvent_interface` configuration

The licensed ecoinvent database itself is **not redistributed** in this repository.

### premise and IAM access
Prospective background construction is implemented through `premise`.
If your local workflow requires an IAM access key, define it through the variable named in the YAML config, for example:
- `PREMISE_KEY`

Do not store credentials or keys in tracked repository files.

## Environment

See `env/environment.yml` for the tested repository-development environment.

## Local-only testing and runs

Local-only probes, scratch files, exports, and run outputs should live under `_local/`, which is gitignored.

Recommended subfolders:
- `_local/tests/`
- `_local/runs/`
- `_local/logs/`
- `_local/scratch/`
- `_local/setup/`

## Reproducibility boundary

A reader with:
- this repository
- the documented software environment
- licensed access to the required external background datasets
- and the required IAM inputs where applicable

should be able to reconstruct the deterministic methods workflow documented here.

## Citation

Please cite:
1. the associated journal paper, where relevant
2. the DOI-minted repository release for the exact archived version used

See `CITATION.cff` for the repository citation record.
