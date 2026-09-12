Status: Step 8A repair complete — guided classification judgment conforms to approved architecture

Implementation base:
- 5904379e Step 8A guided classification judgment
- Plan: 494e1f6 Plan Step 8A repair against latest implementation

Historical model preservation:
- fiscal periods: 5
- conceptual formula families: 25
- concrete formula practice cells: 118
- fresh formula Check: 0 / 0 / 118

Guided judgment (repaired):
- supported judgment templates: 4
- illustrative demo judgment cases: 1
- case: Operating lease liabilities
- reference treatment: Operating Long-Term Liability
- alternative: Financial Liability
- Trainer F:G:H: 3 blank / yellow / no Note
- Answer Key F:G:H: 3 populated / yellow
- Trainer direct-constructor sanitization regression: pass
- judgment rationale/consequence leakage: none
- deferred-tax Step 8A cases: 0
- ROU Step 8A cases: 0
- Accounting Judgment excluded from formula Check/list family count: yes (25 families)
- judgment responses auto-graded: no
- learner judgment drives main model: no

Preservation:
- source values populated: yes
- main classifications populated: yes
- reformulation guardrails pass: yes
- forecast engine called by normal build: no
- deferred tabs: four hidden placeholders
- CLI: {ingest,build,check,list}

Files changed:
- Modify: `core/model/classification.py` — `judgment_code` only; remove guided pedagogical fields
- Replace: `core/model/judgment.py` — four-template registry; canonical `periods` axis
- Modify: `core/engine/reference_model.py` — builder wiring; A2/A3/header copy; wrap-text responses
- Modify: `core/trainer/workbook.py` — structural row sanitization; two-arg constructor; instruction fix
- Modify: `core/tests/test_classification.py` / `test_reference_integrity.py` / `test_trainer.py`
- Modify: `README-HK-TRAINER.md` / `skills/bav-trainer/SKILL.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

Tests (fresh):
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 19 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 33 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 40 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 115 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> Components resolved: 118
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx` -> 25 schedule groups / 118 concrete formula cells
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only
- demo rebuild: Components resolved: 118; Accounting Judgment sheet with 1 lease case; final audit OK

Known deferred limitation:
- irregular/stub/interim period comparability still requires later robustness work
- Step 8B live classification / normalization not started

Unresolved: none
