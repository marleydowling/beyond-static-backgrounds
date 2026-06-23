# Foreground routes

This directory contains the Step 4 foreground scaffolding.

## Current status

The implementation here is intentionally a minimal, public-safe structural scaffold.

### Step 4A — market proxy materialization
`step4a_build_market_proxy_db.py`

This writes a minimal Brightway database of:
- market proxy activities
- supplier share child activities
- inherited/proxy child activities
- overlay component child activities

### Step 4B — foreground route activity construction
`step4b_build_route_activities.py`

This writes minimal foreground route activities that:
- include a burden-side proxy exchange, and
- include an explicit Module D proxy exchange to the relevant Step 4A market activity

## Important boundary

These scripts are written in a repo-safe way and intentionally avoid publishing exact licensed ecoinvent or premise provider codes.

For a full local rerun against licensed backgrounds, use a local, ignored provider-resolution table outside the public repository.

## What is still needed for a paper-exact implementation

A paper-exact local build would still need:
- exact local provider mappings for burden-side proxies
- exact local provider mappings for any direct displaced-market provider links
- route-specific exchange-edit logs where activities clone and modify licensed processes
- full route-entry tables for reuse and hydrolysis if those are added later

## Recommended user workflow

1. Build or load the Step 2 background(s) locally
2. Compile Step 3 market logic from the public schemas/examples
3. Materialize Step 4A market proxies
4. Materialize Step 4B foreground route activities
5. For internal exact reruns, resolve public-safe role IDs to local exact providers using an ignored local mapping file
6. Run LCI/LCIA and post-processing diagnostics locally
