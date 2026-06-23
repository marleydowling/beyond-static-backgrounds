# Step 3 central-case recycling example

This example encodes the paper-facing central-case **recycling / MS-FSC billet-equivalent subset** selected for the repository:

- contemporary Canada electricity mix
- contemporary Canada primary aluminium / billet-equivalent proxy
- prospective 2050 inherited electricity representation
- prospective 2050 aluminium technology-evolution overlay

This example is intentionally **not** the full paper Step 3 implementation.

It excludes:
- hydrogen
- the reuse structured proxy
- aluminium-hydroxide proxy handling

## Why reuse is excluded here

In the paper and SI, reuse is **not** modelled as the same displaced market as conventional recycling or MS-FSC.
Reuse remains a façade-component/service replacement claim and its practical avoided-production representation is implemented through a structured proxy combining:
- avoided primary ingot, and
- avoided extrusion.

By contrast, conventional recycling and MS-FSC are represented against the billet / billet-equivalent feedstock market.
This example therefore focuses only on the recycling / MS-FSC billet case.

## Important note on the prospective aluminium overlay

The overlay is implemented in a two-layer way:

1. **retained supplier identity shares**
   The contemporary 2025 primary aluminium supplier identity structure is retained as the defensible
   `who supplies?` construct for the billet-equivalent recycling / MS-FSC case.

2. **overlay components**
   The 2050 production mechanism is represented through overlay families:
   - conventional aluminium
   - inert-anode / ELYSIS-type aluminium

The example overlay file intentionally leaves `overlay_share` blank because the uploaded materials
document the overlay families and rationale but do not impose a fixed plant-level 2050 split across
those families.

## Example build

```bash
python framework/marginal_supplier_logic/build_marginal_mix.py       --markets-csv framework/examples/step3_recycling_central_case_example/markets.csv       --rules-csv framework/examples/step3_recycling_central_case_example/method_rules.csv       --supplier-candidates-csv framework/examples/step3_recycling_central_case_example/supplier_candidates.csv       --provider-proxy-csv framework/examples/step3_recycling_central_case_example/provider_proxy_map.csv       --overlay-rules-csv framework/examples/step3_recycling_central_case_example/overlay_rules.csv       --out-register-csv _local/runs/step3_recycling_central_case_example/register.csv       --out-shares-csv _local/runs/step3_recycling_central_case_example/shares.csv       --out-overlay-csv _local/runs/step3_recycling_central_case_example/overlay_components.csv       --out-proxy-csv _local/runs/step3_recycling_central_case_example/provider_proxy_rows.csv       --out-register-json _local/runs/step3_recycling_central_case_example/register.json
```
