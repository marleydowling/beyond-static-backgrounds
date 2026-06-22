# Marginal supplier logic

This directory will hold Step 3 code for marginal-supplier construction.

Planned supported methods:
- inherited background mix
- CRR-style screening
- Weidema-style heuristic screening
- proxy-provider representation

The generic design is:
1. read structured input tables
2. validate the method requested for each market
3. compute or inherit the marginal representation
4. export an auditable marginal-mix register
