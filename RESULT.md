Status: Step 8B1 complete — live classification with judgment-aware Check

Implementation base:
- 79d2357e Step 8A corrected

Historical formula surface:
- fiscal periods: 5
- formula families: 25
- formula practice cells: 118
- fresh Check: 0 / 0 / 118

Live judgment:
- supported templates: 4
- illustrative demo cases: 1
- case: Operating lease liabilities
- treatment drives Condensed Financials: yes
- blank treatment fallback: yes
- rationale/consequence graded: no
- ROU/deferred-tax alternatives: no

Dynamic Check:
- reference-state expected parity: 118/118
- alternative exact formula: pass
- alternative equivalent formula: pass
- repeated alternative Check: pass
- stale reference value under alternative: rejected
- two-case combined state: pass
- legacy no-context fallback: pass

Accounting invariants under demo alternative:
- reformulated equity reconciliation: pass
- RNOA/CoD/Spread/FLEV change: yes
- ROE decomposed total unchanged: yes
- Actual ROE unchanged: yes

Security/separation:
- Answer-Key hidden Check context: present
- Trainer Check context: absent
- Check context formula/expected/hint answers: none
- Trainer rationale/consequence leakage: none

Preservation:
- deferred tabs: four hidden placeholders
- forecast engine called by normal build: no
- CLI remains {ingest,build,check,list}

Files changed:
- Create: `core/data/standardized_io.py`
- Create: `core/trainer/check_context.py`
- Create: `core/model/historical_expected.py`
- Modify: `core/model/judgment.py` — `override_selector`
- Modify: `core/engine/reference_model.py` — live Condensed classification links + embed Check context
- Modify: `core/trainer/workbook.py` — sanitize `_CheckContext`; updated instruction
- Modify: `core/trainer/checker.py` — treatment-conditioned expected values
- Modify: `core/tests/test_reference_integrity.py` / `test_trainer.py`
- Modify: `README-HK-TRAINER.md` / `skills/bav-trainer/SKILL.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

Tests (fresh):
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 19 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 40 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 48 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 130 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> Components resolved: 118
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx` -> 25 schedule groups / 118 concrete formula cells
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only

Known deferred limitations:
- normalization / recurring-vs-non-recurring treatment is Step 8B2
- ROU/deferred-tax alternative modeling remains deferred
- irregular/stub/interim comparative modeling remains deferred

Unresolved: none
