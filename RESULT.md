Status: Step 6 correction complete

Implementation base:
- 6e06db1 chat 6 corrected

Historical-only boundary:
- normal build calls run_scenario: no
- forecast assumptions required: no
- deferred tabs: four hidden placeholders (`Model_Bear`, `Model_Base`, `Model_Bull`, `Scenario_Summary`)
- public forecast CLI: none

Active practice:
- component count: 21
- Trainer blank/yellow/no Note: 21/21
- Answer Key formula/yellow/Note: 21/21
- Check fresh result: 0 correct / 0 incorrect / 21 blank

Preservation:
- historical source values populated: yes
- classifications/setup judgments populated: yes
- Trainer answer leakage: none
- repeated cached Check behavior: preserved

Files changed:
- Modify: `core/engine/reference_model.py` — `include_deferred_forecast=False` default; no `run_scenario` / default forecast synthesis on normal path; hidden deferred placeholders
- Modify: `core/engine/component_catalog.py` — public catalog = 21 historical; six forecast/valuation specs moved to `DEFERRED_COMPONENT_SPECS`
- Modify: `core/__main__.py` — assumptions help text for historical configuration only
- Modify: `core/tests/test_reference_integrity.py` — quarantine regressions; classification-override CLI test; deferred-path isolation for forecast chain tests
- Modify: `core/tests/test_trainer.py` — 21-component catalog; placeholder audit; Check totals 21/1/1/19; remove live forecast-input expectations
- Modify: `README-HK-TRAINER.md`, `skills/bav-trainer/SKILL.md` — historical foundation framing aligned with TARGET competency progression
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

Tests:
- `PYTHONPATH=. pytest core/tests/test_classification.py -q` -> 14 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -q` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -q` -> (included in full suite)
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -q` -> (included in full suite)
- `PYTHONPATH=. pytest core/tests/ -q` -> 90 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> Components resolved: 21
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 21 practice cells: 0 correct, 0 incorrect, 21 blank.`
- `PYTHONPATH=. python -m core list` -> 21 historical components only
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only
- demo rebuild Check: `Checked 21 practice cells: 0 correct, 0 incorrect, 21 blank.`
- generated Answer-Key sidecars / `rowmap.json` remain gitignored

Unresolved: none
