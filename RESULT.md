Status: Step 8A complete — guided classification judgment with consequences

Implementation base:
- 9ddc60ab Step 7 correction

Historical model preservation:
- fiscal periods: 5
- conceptual formula families: 25
- concrete formula practice cells: 118
- fresh formula Check: 0 / 0 / 118

Guided judgment:
- demo judgment cases: 1
- case: Operating lease liabilities
- supplied treatment: Operating Long-Term Liability
- alternative: Financial Liability
- Trainer response cells blank/yellow/no Note: 3/3
- Answer Key response cells populated/yellow: 3/3
- judgment answer leakage: none
- judgment responses auto-graded: no
- learner judgment drives main model: no

Preservation:
- source values populated: yes
- main classifications populated: yes
- reformulation guardrails pass: yes
- forecast engine called by normal build: no
- deferred tabs: four hidden placeholders
- repeated cached formula Check: preserved

Files changed:
- Modify: `core/model/classification.py` — guided options / topic / consequence metadata; ROU remains ambiguous without fake options
- Create: `core/model/judgment.py` — `JudgmentCase` + `classification_judgment_cases()`
- Modify: `core/engine/reference_model.py` — `Accounting Judgment` sheet + dropdown validation
- Modify: `core/trainer/workbook.py` — decorate/blank judgment response cells F/G/H
- Modify: `example/DEMO_HK_Standardized.json` — split lease liability without changing totals
- Modify: `core/tests/test_classification.py` / `test_reference_integrity.py` / `test_trainer.py`
- Modify: `README-HK-TRAINER.md` / `skills/bav-trainer/SKILL.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

Tests:
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 32 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 37 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 109 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> Components resolved: 118
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx` -> 25 schedule groups / 118 concrete formula cells
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only
- demo rebuild: Components resolved: 118; Accounting Judgment sheet with 1 lease case; final audit OK

Known deferred limitation:
- irregular/stub/interim period comparability still requires later robustness work

Unresolved: none
