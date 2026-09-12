Status: Step 9A.2 complete — undefined-ratio and Net-Income source hardening

Implementation base:
- 0ca16506 Step 9A.1

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

Undefined-ratio and Net Income hardening:
- missing CFO / Total Assets / Net Income are never fabricated as zero: yes
- explicit numeric zero remains a valid supplied historical fact: yes
- zero numerator with nonzero denominator remains a valid 0.0 ratio: yes
- zero Net Income -> cash conversion ratio #N/A (undefined denominator): yes
- zero Average Total Assets -> accrual ratio #N/A (undefined denominator): yes
- Excel Answer Key formulas use NA() for zero denominators: yes
- Formula Check accepts exact NA() formulas and cached #N/A; rejects fabricated 0.0: yes
- reported Net Income resolved + period-complete inside quality model; must match AnchorMetrics: yes
- first-period Average Total Assets / Accrual Ratio remain non-applicable (None / no FY1 component): yes

Preservation:
- Step 8A/8B1/8B2 trusted-workbook behavior preserved
- Step 9A formula families / sheet layout unchanged
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- working-capital interpretation / forecasting / valuation not begun: yes

Files changed:
- Modify: `core/model/earnings_quality.py` — UNDEFINED_RATIO; NI completeness; zero-denominator #N/A
- Modify: `core/engine/reference_model.py` — NA() denominator guards; pass #N/A expecteds
- Modify: `core/tests/test_earnings_quality.py` — undefined-ratio / NI / Check regressions; tighten ValueError
- Modify: `core/tests/test_normalization.py` — inject helper supports Excel error cached `#N/A`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v` -> 16 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 8 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py core/tests/test_normalization.py core/tests/test_trainer.py core/tests/test_classification.py core/tests/test_line_identity.py -q` -> 164 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 188 passed
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
