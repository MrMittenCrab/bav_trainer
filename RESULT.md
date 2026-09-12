Status: Step 8B2.2 complete — trusted workbook state hardening

Implementation base:
- 77df6213 Step 8.2 Hardened

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 25
- formula practice cells: 118
- fresh Check: 0 / 0 / 118

Step 8B2 illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 29
- formula practice cells: 138
- fresh Check: 0 / 0 / 138

Trusted-state hardening (Step 8B2.2):
- exact padded treatment rejected (no strip-and-accept): yes
- blank / empty F still falls back to reference treatment: yes
- historical source statements structurally protected: yes
- fixed supplied classifications structurally protected: yes
- non-practice model cells protected (Condensed / ALT DuPont / Earnings Normalization): yes
- learner practice formulas still editable / equivalent-formula eligible: yes
- judgment F:G:H learner surface preserved: yes
- integrity failure before any fill update / no partial recoloring: yes

Preservation:
- Step 8A/8B1/8B2/8B2.1 behavior otherwise preserved
- CLI remains {ingest,build,check,list}
- committed demo XLSX not regenerated
- TARGET.md unchanged: yes
- Step 9 functionality introduced: no

Files changed:
- Modify: `core/trainer/check_context.py` — exact treatment match; trusted sheet content gate
- Modify: `core/tests/test_normalization.py` — padded/source/classification/G:H regressions
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh):
- `PYTHONPATH=. pytest core/tests/test_classification.py -q` -> 19 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -q` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -q` -> 41 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -q` -> 53 passed
- `PYTHONPATH=. pytest core/tests/test_normalization.py -q` -> 34 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 170 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_BASE_Trainer.xlsx` -> Components resolved: 118
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_BASE_Trainer.xlsx` -> `Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_BASE_Trainer.xlsx` -> 25 schedule groups
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -a example/DEMO_HK_Assumptions.json -o /tmp/DEMO_NORM_Trainer.xlsx` -> Components resolved: 138
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_NORM_Trainer.xlsx` -> `Checked 138 practice cells: 0 correct, 0 incorrect, 138 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_NORM_Trainer.xlsx` -> 29 schedule groups
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only

Known deferred limitations:
- special-tax / below-the-line / non-operating normalization remain deferred
- ROU/deferred-tax alternative modeling remains deferred
- earnings-quality diagnostics / accrual-cash conversion remain Step 9+
- irregular/stub/interim comparative modeling remains deferred

Unresolved: none
