# Marginal supplier logic

This directory contains the Step 3 builder for displaced-market and marginal-supplier representations.

## Supported methods

The implementation supports six method types:

- `inherit_background`
- `custom_empirical_mix`
- `crr_screen`
- `weidema_heuristic`
- `proxy_provider`
- `prospective_overlay`

Not every method must be exercised in every case.

## Working example in this repository

The Central-case recycling example encodes only the methods exercised in the paper-facing central case subset selected for the repo:

- contemporary Canada electricity: `custom_empirical_mix`
- contemporary Canada aluminium billet / primary aluminium proxy: `custom_empirical_mix`
- prospective 2050 electricity: `inherit_background`
- prospective 2050 aluminium billet / primary aluminium proxy: `prospective_overlay`

Hydrogen is excluded from this first repo implementation even though the method layer supports it structurally.

## Build command example

```bash
python framework/marginal_supplier_logic/build_marginal_mix.py   --markets-csv framework/examples/step3_recycling_central_case_example/markets.csv   --rules-csv framework/examples/step3_recycling_central_case_example/method_rules.csv   --supplier-candidates-csv framework/examples/step3_recycling_central_case_example/supplier_candidates.csv   --provider-proxy-csv framework/examples/step3_recycling_central_case_example/provider_proxy_map.csv   --overlay-rules-csv framework/examples/step3_recycling_central_case_example/overlay_rules.csv   --out-register-csv _local/runs/step3_recycling_central_case_example/register.csv   --out-shares-csv _local/runs/step3_recycling_central_case_example/shares.csv   --out-overlay-csv _local/runs/step3_recycling_central_case_example/overlay_components.csv   --out-proxy-csv _local/runs/step3_recycling_central_case_example/provider_proxy_rows.csv   --out-register-json _local/runs/step3_recycling_central_case_example/register.json
```
