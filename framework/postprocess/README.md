# Postprocess

This directory contains the public post-processing layer.

## Current layers

### Step 4C — LCIA runner
`step4c_run_lcia.py`

This script runs a configurable set of LCIA methods against a locally available, LCIA-ready route database.

### Step 4C helper — list or export available methods
`list_lcia_methods.py`

This helper lists LCIA methods in the active local Brightway project and can write a local methods CSV for `step4c_run_lcia.py`.

### Step 4D helper — build primary decomposition from LCIA results
`step4d_build_decomposition.py`

This helper converts Step 4C primary-indicator results into a decomposition table using a local role map.

### Step 4D — diagnostics and interpretation
`step4d_route_diagnostics.py`

This script converts route-level decomposition and supplementary indicator results into:
- primary indicator summaries
- dominance-ratio diagnostics
- sign-screen summaries for supplementary indicators

## Boundary

Step 4C and 4D are post-construction layers.
They do not replace exact local Step 4 provider resolution.

To obtain meaningful LCIA results, the user must run Step 4C against a locally linked, biosphere-bearing database rather than the public structural placeholder database alone.


### Background recycling exact smoke test

A simple local exact-function test can be run against a mature background recycling process rather than a custom copied foreground chain.

This is useful to verify that:
- Step 4C can run LCIA against a biosphere-bearing local route database
- Step 4D can build decomposition tables and dominance diagnostics from numeric outputs
- the public post-processing layer behaves correctly before case-specific exact foreground recreation is attempted
