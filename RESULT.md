Status: Step 9M.2C complete — deterministic tax/provision/equity concept classification

Implementation base:
- 894c525 Step 9M.2B residual other-balance guided classification

Step 9M.2C status: complete

Final verification:
- focused tests: 130 passed
  (`test_classification.py` + `test_reference_integrity.py` + `test_fast_retailing_benchmark.py`)
- full core tests: 425 passed
- forecast/valuation isolation: pass
  (`test_normal_v1_build_does_not_call_run_scenario` + historical exit-gate family orders)
- family orders: 1..90 unchanged
- all Fast Retailing BS detail rows classifiable: yes
- new Step 9M.2C judgment cases: 0
- Fast Retailing standardized/provenance/conflicts source artifacts unchanged: yes
- statement overlap conflicts: 3
- supplemental conflicts: 3

Deterministic concepts (ambiguous=False, no new judgment templates):
- current_tax_liabilities → Operating Working Capital Liability
- provisions_current → Operating Working Capital Liability
- provisions_noncurrent → Operating Long-Term Liability
- capital_stock / capital_surplus / other_components_of_equity /
  noncontrolling_interests → Equity

Fast Retailing Stage 3: pass
Fast Retailing Stage 4: fail
- exception: ReformulationIntegrityError
- message: Balance-sheet reformulation does not reconcile — multi-year classified
  detail vs reported totals gaps (e.g. FY2021 asset-detail gap=-4,
  liability-detail gap=-6, equity gap=2; similar across FY2022–FY2025)
- workbook generation / Check: not reached

G1/G2/G2B/G2C closed; G3–G7 remain open
TARGET.md: unchanged by Cursor

Next checkpoint:
- address Stage 4 ReformulationIntegrityError (classified detail vs totals)
  and/or substantive G3–G7 work; do not reopen G2C concept mappings unless
  evidence shows they are wrong
