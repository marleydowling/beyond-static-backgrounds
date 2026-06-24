# Beyond Static Backgrounds

This repository is a **methods-only** implementation scaffold for deterministic prospective consequential life cycle assessment (pCLCA) with explicit end-of-life substitution modelling.

It is intended to provide reusable workflow templates and methodological scaffolding for:

1. **Step 1 — baseline conventions and contemporary reference background**
2. **Step 2 — scenario-consistent prospective background construction**
3. **Step 3 — displaced-market definition and marginal-supplier representation**
4. **Step 4 — foreground route materialization and explicit substitution-governance scaffolding**
5. **Post-processing — deterministic indicators, sign screens, break-even scaling, and dominance diagnostics**

## Scope and boundary

This is a **public methods scaffold**, not a redistribution of licensed background data and not a full paper-exact case-study archive.

The repository currently provides:

- public, reusable method code
- public schemas and example tables
- public Step 3 market-register logic
- public Step 4A/4B structural Brightway scaffolding
- deterministic post-processing logic for paper-facing indicators and diagnostics

The repository does **not** redistribute:

- ecoinvent databases
- premise-generated databases
- exact licensed provider mappings
- exact case-study exchange-edit logs derived from licensed databases
- private IAM credentials or local machine paths

## Public-safe Step 4 policy

The public Step 4 layer uses **generic role identifiers** and **placeholder/provider-role objects** rather than publishing exact licensed provider codes.

Examples:
- `AL_RECYCLING_BURDEN_PROXY_CA`
- `FSC_CONSOLIDATION_BURDEN_PROXY_CA`
- `MM_AL_BILLET_CA_2025`

If a user wants a full local rerun against licensed databases, they should create a local, untracked provider-resolution table that maps these public-safe role identifiers to exact internal `(database, code)` providers on their machine.

## What Step 4 currently proves

The current Step 4 scaffold proves that:

- Step 3 market logic can be materialized into valid Brightway foreground objects
- foreground route activities can be constructed around those market proxies
- the resulting graph can be written and can solve an LCI structurally

The current Step 4 scaffold does **not yet** prove that:

- exact licensed burden providers have been resolved
- nonzero biosphere exchanges are present for all route activities
- full LCIA-ready case-study activities have been reproduced exactly

## Post-processing layer

The deterministic indicator and interpretation layer remains separate from Step 4 construction.

That layer includes:
- climate-change / GWP summaries
- midpoint screening
- sign-consistency and reversal checks
- break-even credit scaling
- dominance-ratio diagnostics

Step 4C assumes that a user's local Brightway project already has a functioning LCIA method setup. Step 4D can be used independently when numeric route-level results are already available.

These are important paper-facing outputs, but they are **not substitutes** for exact provider-linked Step 4 foreground construction.

## Public intent of Step 4

The public repository does not claim a full foreground rebuild for every possible case study.

Instead, it provides:
- a generic Step 3 market-definition layer
- a generic Step 4 foreground construction pattern
- public-safe examples showing how market activities, foreground route activities, LCIA runs, and diagnostics fit together

Exact case-study foreground recreation remains local-only and depends on the user's own licensed background access, local provider mappings, and route-specific implementation choices.

## Archive boundary

This repository is a methods scaffold and **not a complete case-study rerun archive**. The article-specific supplementary resources remain the journal-facing case-study record, while this repository provides reusable workflow templates, public-safe examples, and methodological scaffolding.

## Archived software release

This repository has an archived software release with DOI: 10.5281/zenodo.20834341.
