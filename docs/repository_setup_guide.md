# Repository setup guide

## 1. Create the scaffold
Run the repository structure script from the parent directory.

## 2. Fill the root files
Update:
- `README.md`
- `CITATION.cff`
- `LICENSE`
- `env/environment.yml`

## 3. Populate the case-study folders

### Put these into `case_studies/curtain_wall_aluminium/scripts/`
- Resource 2 builder script
- Resource 3 builder script
- deterministic post-processing scripts used in the paper

### Put these into `case_studies/curtain_wall_aluminium/results/`
- deterministic exported tables
- cross-indicator screening tables

### Put these into `case_studies/curtain_wall_aluminium/figures/`
- figure source tables used to generate manuscript figures

### Put these into `case_studies/curtain_wall_aluminium/si/`
- `resource1_si/` — final SI PDF and source text
- `resource2_deterministic_results/` — final paper-facing CSVs
- `resource3_cross_indicator_screening/` — final paper-facing CSVs

## 4. Mirror final paper-facing files
Copy the final released versions into:
- `online_resources/resource1_si/`
- `online_resources/resource2_deterministic_results/`
- `online_resources/resource3_cross_indicator_screening/`

## 5. Initialize git
From the repository root:
- `git init`
- `git add .`
- `git commit -m "Initial deterministic paper repository"`

## 6. Create GitHub repo and push
- create the empty GitHub repository
- add the remote
- push `main`

## 7. Archive the first release
- connect the GitHub repo to Zenodo
- create a GitHub release (for example `v1.0.0`)
- use the minted DOI in the manuscript and SI
