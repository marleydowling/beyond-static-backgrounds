# Market definition

This directory contains the Step 3 market-register loader and validator.

Step 3 separates:
- the **scenario-conditioned background** from Step 2, and
- the **explicit displaced-market and marginal-supplier representation** used for consequential substitution.

The public repo design is intentionally register-driven:
- machine-readable market table
- machine-readable method-rule table
- machine-readable supplier candidate table
- machine-readable proxy table
- machine-readable overlay table

This allows the same Python logic to support:
- inherited background mix
- custom empirical mix
- CRR screen
- Weidema-style heuristic
- proxy provider
- prospective overlay
