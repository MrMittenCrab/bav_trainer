Status: Step 9M.2D complete — reporting-unit rounding envelope for reformulation integrity

Implementation base:
- 290361d Step 9M.2C deterministic tax/provision/equity concepts

Step 9M.2D status: complete

Final verification:
- focused tests: 139 passed
  (`test_classification.py` + `test_reference_integrity.py` + `test_fast_retailing_benchmark.py`)
- full core tests: 434 passed
- forecast/valuation isolation: pass
  (`test_normal_v1_build_does_not_call_run_scenario` + historical exit-gate family orders)
- family orders: 1..90 unchanged
- Fast Retailing standardized/provenance/conflicts source artifacts unchanged: yes
- statement overlap conflicts: 3
- supplemental conflicts: 3

Rounding envelope:
- formula: max(base_tolerance, 0.5 * (detail_count + 1))
- FR asset detail count: 16 → envelope 8.5
- FR liability detail count: 13 → envelope 7.0
- FR equity-bridge contributors: 29 → envelope 15.0
- committed FR gaps unchanged and accepted; material omissions still fail closed
- Stage-3 G1 Assets=L+E tolerance 1.0 unchanged

Fast Retailing Stages 1–7: all pass
- Stage 4: expected_specs=294 lease_specs=0 fixed_asset_specs=35
- Stage 6 blank Check: correct=0 incorrect=0 blank=294 total=294
- Stage 7 filled Check: correct=294 total=294
- first newly exposed Stage failure: none

G1/G1B/G2/G2B/G2C closed; G3–G7 remain open
TARGET.md: unchanged by Cursor

Next checkpoint:
- select from remaining substantive gaps G3–G7 (split-lease module, lease-interest
  treatment, NCI attribution, share-basis/per-share, restatement conflicts);
  no Stage-1–7 exception remains as the first blocker
