Status: Step 9A.1 complete — earnings-quality source completeness hardening

Implementation base:
- 3e4be697 Step 9

Historical formula surface (no normalization assumptions; demo CFO + total assets present):
- fiscal periods: 5
- formula families: 30
- formula practice cells: 141
- fresh Check: 0 / 0 / 141

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 34
- formula practice cells: 161
- fresh Check: 0 / 0 / 161

Earnings-quality source completeness:
- absent CFO line -> quality module omitted: yes
- incomplete resolved CFO line -> build rejected; no zero fabrication: yes
- absent Total Assets line -> asset-scaled extension omitted: yes
- incomplete resolved Total Assets line -> rejected; no zero fabrication: yes
- explicit numeric zero remains valid supplied data: yes
- zero Net Income -> cash conversion ratio 0.0 (Step 9A convention): yes
- zero average assets → accrual ratio 0.0 (explicit Step 9A denominator convention): yes
- no quality score / threshold / automatic good-bad label: yes

Preservation:
- Step 8A/8B1/8B2 trusted-workbook behavior preserved
- Step 9A formula families / sheet layout unchanged
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- working-capital interpretation / forecasting / valuation not begun: yes

Files changed:
- Modify: `core/model/earnings_quality.py` — `_required_period_value`; fail-closed CFO/Total Assets periods
- Modify: `core/tests/test_earnings_quality.py` — incompleteness vs availability matrix
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v` -> 14 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 8 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py core/tests/test_normalization.py core/tests/test_trainer.py core/tests/test_classification.py core/tests/test_line_identity.py -q` -> 164 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 186 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_BASE_Trainer.xlsx` -> Components resolved: 141
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_BASE_Trainer.xlsx` -> `Checked 141 practice cells: 0 correct, 0 incorrect, 141 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_BASE_Trainer.xlsx` -> 30 schedule groups
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -a example/DEMO_HK_Assumptions.json -o /tmp/DEMO_NORM_Trainer.xlsx` -> Components resolved: 161
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_NORM_Trainer.xlsx` -> `Checked 161 practice cells: 0 correct, 0 incorrect, 161 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_NORM_Trainer.xlsx` -> 34 schedule groups
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only

Known deferred limitations:
- working-capital / driver interpretation of conversion changes remains deferred
- quality scoring / automatic good-bad labels remain deferred
- ROU/deferred-tax alternative modeling remains deferred
- forecasting / valuation / investment conclusion remain deferred

Unresolved: none
