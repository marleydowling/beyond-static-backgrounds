# Framework

This directory contains the reusable method components used by the deterministic journal-paper workflow.

## Intended contents

- `market_definition/`
  - displaced-product market definitions
  - receiving-system market-boundary logic
  - product-to-market mapping helpers

- `marginal_supplier_logic/`
  - marginal supplier mix construction
  - supplier-share tables
  - market-response logic used by explicit substitution claims

- `substitution_rules/`
  - like-for-like substitution rules
  - equivalence and conditioning logic
  - explicit Module D implementation rules

- `postprocess/`
  - deterministic summarizers
  - break-even calculations
  - cross-indicator screening helpers

- `utils/`
  - shared helper functions used across the repository

## Boundary

This folder should contain reusable framework logic only. Curtain-wall-specific scripts, inputs, and outputs should remain in `case_studies/curtain_wall_aluminium/`.
