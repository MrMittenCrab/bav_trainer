Status: Step 8B1.1 complete — live-judgment integrity hardening

Implementation base:
- 74d9867b Step 8B1

Historical formula surface:
- fiscal periods: 5
- formula families: 25
- formula practice cells: 118
- fresh Check: 0 / 0 / 118

Live-judgment integrity:
- F is the only live judgment input: yes
- blank F falls back to literal trusted reference treatment: yes
- generated Condensed link references D: no
- D/E prompt edits rejected before grading: yes
- overwritten Condensed live link rejected before grading: yes
- valid blank and alternative treatments pass structural validation: yes
- invalid treatment / structural failure partial recoloring: none
- workbook handles closed on Check exceptions: yes

Dynamic Check preservation:
- alternative exact formula: pass
- alternative equivalent formula: pass
- stale reference under alternative: rejected
- repeated Check cache survival: pass
- legacy no-context fallback: pass
- vacuous `or True` regressions: removed

Security/separation:
- Answer-Key hidden Check context: present
- Trainer Check context: absent
- illustrative demo cases: 1 (Operating lease liabilities)

Preservation:
- deferred tabs: four hidden placeholders
- forecast engine called by normal build: no
- CLI remains {ingest,build,check,list}

Files changed:
- Modify: `core/trainer/check_context.py` — `live_classification_formula`, `validate_live_judgment_structure`
- Modify: `core/engine/reference_model.py` — literal-fallback live links; clarified A3 instruction
- Modify: `core/trainer/checker.py` — structure gate before grading; try/finally workbook close; fills only after success
- Modify: `core/trainer/workbook.py` — Trainer instruction wording
- Modify: `core/tests/test_reference_integrity.py` / `test_trainer.py`
- Modify: `README-HK-TRAINER.md` / `skills/bav-trainer/SKILL.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

Tests (fresh):
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 19 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 41 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 53 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 136 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> Components resolved: 118
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx` -> 25 schedule groups
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only

Known deferred limitations:
- normalization / recurring-vs-non-recurring treatment is Step 8B2
- ROU/deferred-tax alternative modeling remains deferred
- irregular/stub/interim comparative modeling remains deferred

Unresolved: none
