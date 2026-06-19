# Beyond Static Backgrounds

This repository accompanies the deterministic journal-paper workflow for a prospective consequential life cycle assessment (pCLCA) framework with explicit end-of-life modelling and application to a curtain wall.

## Repository purpose

The repository has two linked roles:

1. **General method framework**
   - receiving-system definition
   - displaced-market and marginal-supplier logic
   - substitution-rule implementation
   - deterministic post-processing for end-of-life comparisons

2. **Case-study application**
   - deterministic application to the aluminium subsystem of a Canadian stick-built mass timber curtain wall
   - case-specific scripts, configurations, results, and figure source data

## Paper-facing scope

This repository is aligned to the **deterministic journal-paper scope**. It includes:
- the general pCLCA method components required for the paper
- the curtain-wall aluminium case-study implementation
- machine-readable deterministic climate-change results
- machine-readable cross-indicator screening outputs
- case-study figure source data and processed inputs needed to interpret the application

This repository does **not** include:
- the broader three-scenario prospective comparison used elsewhere in the thesis workflow
- parameter-uncertainty propagation
- sensitivity or Monte Carlo analysis
- licensed background databases, including ecoinvent-derived and premise-generated background systems
- the journal-submitted Online Resources, which are provided separately with the paper

## Study focus

The paper evaluates explicit end-of-life substitution claims for the aluminium subsystem of a curtain wall. The declared building-scale unit is **1 m² of installed curtain wall**, and the representative aluminium content is **3.666 kg Al/m²**. The main route comparison in the paper is reported on a **1 kg Al** basis. The deterministic comparison covers two receiving systems:
- **Contemporary (2025)**
- **Prospective SSP2-M (2050)**

The retained end-of-life routes are:
- landfill
- direct reuse
- conventional recycling via remelting
- multi-step friction stir consolidation (MS-FSC)
- aluminium hydrolysis to hydrogen, with conditional aluminium hydroxide handling

## Repository structure

```text
framework/
  market_definition/
  marginal_supplier_logic/
  substitution_rules/
  postprocess/
  utils/

case_studies/
  curtain_wall_aluminium/
    configs/
    scripts/
    inputs_processed/
    results/
    figures/

env/
docs/
```

## Data and code availability

Case-study code, configuration files, processed foreground definitions, deterministic result exports, and supporting case-study materials are archived in a versioned DOI-bearing repository associated with this GitHub repository.

Repository URL: https://github.com/marleydowling/beyond-static-backgrounds

DOI: DOI_TO_BE_INSERTED_AFTER_RELEASE

Licensed background databases are **not redistributed** here.

## Reproducibility boundary

A reader with:
- this repository,
- the submitted supplementary files associated with the paper,
- and licensed access to the required background databases

should be able to inspect and reconstruct the custom deterministic workflow used in the journal paper.

## Citation

Please cite:
1. the associated journal paper
2. the DOI-minted repository release for the exact archived version used

See `CITATION.cff` for the software and repository citation record.
