# Beyond Static Backgrounds

This repository supports the deterministic journal-paper workflow for a prospective consequential life cycle assessment (pCLCA) framework with explicit end-of-life modelling and application to building systems.

## Repository purpose

The repository has two linked roles:

1. **General method framework**

   * baseline background preparation
   * scenario-consistent background construction
   * displaced-market and marginal-supplier logic
   * substitution-rule implementation
   * deterministic post-processing for end-of-life comparisons

2. **Case-study application**

   * deterministic application to the aluminium subsystem of a Canadian curtain wall
   * case-specific scripts, configurations, results, and figure source data

## Current repository scope

The current repository development is focused first on the **methods layer**, especially the background-construction workflow required for deterministic pCLCA. The initial scripted workflow is organized to align with the method steps in the journal paper:

* **Step 1** — establish baseline conventions and import baseline databases
* **Step 2** — construct, version, freeze, audit, and inspect scenario-consistent prospective backgrounds

The case-study layer will be added after the methods layer is stabilized and cleaned for public release.

## Included in the public repository

The intended public repository includes:

* reusable method scripts in `framework/`
* configuration files required to reproduce the deterministic workflow
* case-study application files that are suitable for public release
* environment specification for the software stack
* repository documentation and archive notes

## Excluded from the public repository

The public repository does **not** include:

* licensed background databases, including ecoinvent-derived and premise-generated Brightway databases
* private IAM source files that cannot be redistributed
* local testing utilities and scratch files
* temporary build helpers used only to scaffold or reorganize the repository
* unpublished case-study scripts or outputs that are still under active restructuring
* uncertainty propagation and sensitivity workflows outside the deterministic journal-paper scope

## Repository structure

```text
framework/
  backgrounds/
  market_definition/
  marginal_supplier_logic/
  substitution_rules/
  postprocess/
  utils/

case_studies/
  curtain_wall_aluminium/

env/
docs/
```

## Methods-layer design principles

This repository is designed to be transparent about what is original to this work and what depends on established external tools.

The repository **does provide**:

* orchestration scripts around Brightway and premise
* configuration-driven workflow control
* audit, versioning, and freeze logic
* explicit setup for deterministic background construction
* downstream consequential logic specific to this methodological framework

The repository **does not claim authorship of**:

* premise’s internal IAM–LCI transformation engine
* Brightway’s core infrastructure
* ecoinvent data
* IAM source data

Those external tools and datasets are treated as dependencies and are documented accordingly.

## Software environment

The tested repository-development environment uses:

* Python 3.11
* bw2data 4.5.3
* bw2calc 2.2.2
* bw2io 0.9.11
* premise 2.3.2
* numpy < 2.0
* scipy < 1.14
* peewee < 4

See `env/environment.yml` for the pinned environment specification.

## Local development versus public repository content

Local-only development material should be kept outside the tracked repository content. In this project, local probes, scratch files, exports, and setup utilities are intended to live under `_local/`, which is ignored by git.

The public repository should remain focused on method scripts, documented configuration, and release-appropriate case-study material.

## Data and code availability

Case-study code, configuration files, processed foreground definitions, deterministic result exports, and release-appropriate supporting materials are intended to be archived in a versioned DOI-bearing repository associated with this GitHub repository.

Repository URL: https://github.com/marleydowling/beyond-static-backgrounds

DOI: DOI_TO_BE_INSERTED_AFTER_RELEASE

Licensed background databases are **not redistributed** here.

## Reproducibility boundary

A reader with:

* this repository,
* the documented software environment,
* licensed access to the required external background datasets,
* and the required IAM inputs where applicable

should be able to reconstruct the deterministic workflow used in the journal paper.

## Citation

Please cite:

1. the associated journal paper
2. the DOI-minted repository release for the exact archived version used

See `CITATION.cff` for the software and repository citation record.
