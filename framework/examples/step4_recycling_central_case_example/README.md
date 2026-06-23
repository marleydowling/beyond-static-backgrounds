# Step 4 recycling / MS-FSC central-case example

This example provides a minimal Step 4 wrapper layer for:
- conventional recycling (2025 and 2050)
- MS-FSC (2025 and 2050)

The purpose is to test that:
1. Step 3 outputs can be materialized into a Brightway foreground market-proxy database, and
2. foreground route activitys can then point explicitly to those market proxies through Module D-style proxy exchanges.

This is a minimal test harness, not the full paper-exact foreground implementation.

## What is included

- conventional recycling wrapper examples
- MS-FSC wrapper examples
- explicit credit amounts for the billet-equivalent claim
- qualitative equivalence / conditioning / exclusion metadata

## What is not yet included

- exact provider-linked route burden clones
- reuse structured proxy route
- hydrogen route
- aluminium-hydroxide co-product route
- full utility-localized and background-linked burden builds

## Interpretation

- Conventional recycling is treated here as a mature wrapper route with a default 1.0 credit amount to the billet-equivalent market.
- MS-FSC is treated here with a realized billet-equivalent output of 0.7616 per kg prepared scrap, based on 0.80 shred yield and 0.952 retained yield.
