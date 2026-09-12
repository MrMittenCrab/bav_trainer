Status: Step 9A complete — historical earnings-quality diagnostics (cash conversion and accruals)

Implementation base:
- 5254d627 Step 8.3

Historical formula surface (no normalization assumptions; demo CFO + total assets present):
- fiscal periods: 5
- formula families: 30
- formula practice cells: 141
- fresh Check: 0 / 0 / 141
- quality expansion: +5 families / +23 cells

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 34
- formula practice cells: 161
- fresh Check: 0 / 0 / 161

Earnings-quality diagnostics (mechanical only):
- canonical `operating_cash_flow` via explicit concept or narrow final-CFO aliases: yes
- curly-apostrophe line resolution: yes
- missing CFO disables Earnings Quality module (no invented CFO): yes
- ambiguous CFO fails clearly: yes
- cash conversion + total accruals when CFO available: yes
- average total assets + accrual ratio gated independently on total assets: yes
- zero average assets → accrual ratio None (no division by zero): yes
- no quality score / threshold / automatic good-bad label: yes
- trusted-state protection for populated Earnings Quality rows: yes
- learner practice quality cells remain blank yellow / Check-gradable: yes

Preservation:
- Step 8A/8B1/8B2 trusted-workbook behavior preserved
- CFO-unavailable fixtures keep prior 25 / 118 (or 29 / 138 with assumptions) surface
- expand_historical_specs remains 118; COMPONENT_CATALOG remains 25
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- working-capital interpretation / forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/earnings_quality.py`
- Add: `core/tests/test_earnings_quality.py`
- Modify: `core/model/line_resolver.py` — curly apostrophes; OCF aliases
- Modify: `core/engine/component_catalog.py` — QUALITY_COMPONENT_CATALOG + expand_quality_specs
- Modify: `core/engine/reference_model.py` — Earnings Quality sheet + quality gating
- Modify: `core/model/historical_expected.py` — quality expected series
- Modify: `core/trainer/checker.py` — recompute quality expecteds
- Modify: `core/trainer/check_context.py` — trusted validation for Earnings Quality
- Modify: `core/trainer/workbook.py` — family grouping + instruction wording
- Modify: `core/tests/test_line_resolver.py`
- Modify: `core/tests/test_trainer.py`
- Modify: `core/tests/test_normalization.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `example/DEMO_HK_Trainer.xlsx` / `example/DEMO_HK_Answer_Key.xlsx` (regenerated)
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh):
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 8 passed
- `PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v` -> 11 passed
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 19 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 41 passed
- `PYTHONPATH=. pytest core/tests/test_normalization.py -v` -> 34 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 53 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 183 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_BASE_Trainer.xlsx` -> Components resolved: 141
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_BASE_Trainer.xlsx` -> `Checked 141 practice cells: 0 correct, 0 incorrect, 141 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_BASE_Trainer.xlsx` -> 30 schedule groups
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -a example/DEMO_HK_Assumptions.json -o /tmp/DEMO_NORM_Trainer.xlsx` -> Components resolved: 161
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_NORM_Trainer.xlsx` -> `Checked 161 practice cells: 0 correct, 0 incorrect, 161 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_NORM_Trainer.xlsx` -> 34 schedule groups
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only

Known deferred limitations:
- working-capital / driver interpretation of conversion changes remains deferred
- special-tax / below-the-line / non-operating normalization remain deferred
- ROU/deferred-tax alternative modeling remains deferred
- forecasting / valuation / investment conclusion remain deferred
- irregular/stub/interim comparative modeling remains deferred

Unresolved: none
