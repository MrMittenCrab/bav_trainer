Status: Step 8B2 complete — guided recurring/non-recurring earnings normalization

Implementation base:
- 39c0db46 SStep 8.1 Corrected

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
- reference treatment: Non-recurring
- alternative: Recurring
- FY2023 pretax adjustment under reference: +200
- FY2023 after-tax adjustment: pretax × (1 − FY2023 ETR)
- Check context schema: 2
- Trainer `_CheckContext`: absent
- Answer Key `_CheckContext`: hidden present

Normalization integrity:
- candidates only from explicit assumptions: yes
- no label heuristic for candidates: yes
- blank F falls back to literal reference treatment: yes
- generated Earnings Normalization treatment link references D: no
- D/E prompt edits rejected before grading: yes
- overwritten treatment link rejected before grading: yes
- invalid treatment / structural failure partial recoloring: none
- classification + normalization compose in one Check: yes
- schema v1 Check context still loadable: yes

Dynamic Check preservation:
- Non-recurring exact formula: pass
- Non-recurring equivalent formula: pass
- Recurring exact formula: pass
- Recurring equivalent formula: pass
- stale Non-recurring under Recurring: rejected
- combined lease alternative + Recurring normalization: pass

Security/separation:
- Answer-Key hidden Check context: present (schema v2)
- Trainer Check context: absent
- rationale/consequence leakage into Trainer: none observed

Preservation:
- deferred tabs: four hidden placeholders
- forecast engine called by normal build: no
- CLI remains {ingest,build,check,list}
- reported IS/Condensed/118 historical cells unchanged by normalization treatment: yes

Files changed:
- Create: `core/model/normalization.py`
- Create: `example/DEMO_HK_Assumptions.json`
- Create: `core/tests/test_normalization.py`
- Modify: `example/DEMO_HK_Standardized.json` — FY2023 admin/restructuring split
- Modify: `core/engine/component_catalog.py` — `NORMALIZATION_COMPONENT_CATALOG` + expand
- Modify: `core/engine/reference_model.py` — judgment + Earnings Normalization sheets
- Modify: `core/model/historical_expected.py` — normalization expecteds
- Modify: `core/trainer/check_context.py` — schema v2 bindings + structure gate
- Modify: `core/trainer/checker.py` — treatment-conditioned normalization expecteds
- Modify: `core/trainer/workbook.py` — sanitization + family grouping + instruction
- Modify: `README-HK-TRAINER.md` / `skills/bav-trainer/SKILL.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

Tests (fresh):
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 19 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 41 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -v` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 53 passed
- `PYTHONPATH=. pytest core/tests/test_normalization.py -v` -> 13 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 149 passed
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
