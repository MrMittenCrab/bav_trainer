Status: Step 9M.2A complete — real-company build unblockers (G1 + G2)

Implementation base:
- a707408 Step 9M.1.1 filing-JSON provenance + validation hardening
- Design: 37c0b84 Step 9M.2A real-company build unblockers

Step 9M.2A scope: G1 + G2 only

Final verification:
- focused tests: 95 passed
  (`test_classification.py` + `test_reference_integrity.py` + `test_fast_retailing_benchmark.py`)
- full core tests: 390 passed
- forecast/valuation activation: no
  (`test_normal_v1_build_does_not_call_run_scenario` PASS)
- Fast Retailing standardized source payload changed: no
- statement overlap conflicts: 3
- supplemental conflicts: 3

G1 one-unit BS tolerance: pass
- `BALANCE_SHEET_TOLERANCE = 1.0`
- residual `<= 1.0` accepted without plugs; `> 1.0` still fails
- Fast Retailing Stage 3: pass

G2 generic financial rows: guided judgment, no hard stop
- four side-aware judgment codes registered
- known G2 concepts classify as financial default + `ambiguous=True`
- vague label without concept still fails closed
- Fast Retailing Stage 4: fail
  - exception: `UnclassifiedBalanceSheetLineError`
  - message: `Cannot safely classify balance-sheet line 'Other assets'; provide classificationOverrides['Other assets']`
  - known G2 financial-instrument rows no longer block Stage 4

next blocker:
- stage `4_reference_model_builder`
- `UnclassifiedBalanceSheetLineError`
- `Cannot safely classify balance-sheet line 'Other assets'; provide classificationOverrides['Other assets']`
- workbook generation / Check not reached

G3–G7: remain open
TARGET.md: unchanged by Cursor

Next checkpoint:
- address post-9M.2A `Other assets` classifier gap / remaining G3–G7 queue
