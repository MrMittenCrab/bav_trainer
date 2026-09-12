Status: Step 8B2.1 complete — normalization integrity hardening

Implementation base:
- 3c02649c Step 8.2

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 25
- formula practice cells: 118
- fresh Check: 0 / 0 / 118
- Normalization Judgment sheet: absent
- Earnings Normalization sheet: absent

Step 8B2 illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 29
- formula practice cells: 138
- fresh Check: 0 / 0 / 138
- normalization cases: 1 (Restructuring expense)

Integrity hardening (Step 8B2.1):
- generated non-practice Earnings Normalization formulas structurally protected: yes
- learner practice formulas remain equivalent-formula eligible: yes
- duplicate normalization candidates rejected: yes
- normalization computation uses stable line_identity: yes
- label selector not silently converted to ambiguous concept: yes
- whitespace-only judgment treatment rejected (classification + normalization): yes
- typographic apostrophe label selector regression: pass
- invalid/tampered structural failure partial recoloring: none

Preservation:
- Step 8B1 classification behavior: preserved
- Step 8B2 economics / operating_pretax_effective_tax: preserved
- deferred tabs: four hidden placeholders
- forecast engine called by normal build: no
- CLI remains {ingest,build,check,list}
- committed demo XLSX not regenerated (validation/model-resolution only)
- TARGET.md unchanged: yes
- Step 9 functionality introduced: no

Files changed:
- Modify: `core/model/normalization.py` — duplicate reject; identity resolve; label-stable selector; apostrophe fix
- Modify: `core/trainer/check_context.py` — generated-formula gate; whitespace-closed treatment helper
- Modify: `core/trainer/checker.py` — pass practice_cells into structure validation
- Modify: `core/tests/test_normalization.py` — Step 8B2.1 regressions
- Modify: `RESULT.md`

Tests (fresh):
- `PYTHONPATH=. pytest core/tests/test_classification.py -q` -> 19 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -q` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -q` -> 41 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -q` -> 53 passed
- `PYTHONPATH=. pytest core/tests/test_normalization.py -q` -> 27 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 163 passed
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
