Status: Step 3 complete

Files changed:
- Create: `core/model/classification.py`
- Modify: `core/model/financial_math.py`
- Modify: `core/model/line_resolver.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py`
- Modify: `core/data/validators.py`
- Modify: `example/DEMO_HK_Standardized.json`
- Create: `core/tests/test_classification.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`

Tests run:
- `pytest core/tests/test_classification.py -v` -> 9 passed
- `pytest core/tests/test_reference_integrity.py -v` -> 18 passed
- `pytest core/tests/test_line_resolver.py -v` -> 6 passed
- `pytest core/tests/test_trainer.py -v` -> 15 passed
- `pytest core/tests/ -q` -> 48 passed
- `python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> exit 0; wrote `/tmp/DEMO_HK_Trainer.xlsx` + `/tmp/DEMO_HK_Answer_Key.xlsx` (13 components)

Reconciliation:
- source statement checks: income_statement=True, balance_sheet=True, cash_flow=True
- demo reformulation gaps: asset/liability/equity gaps = (0,0,0,0,0) for all five fiscal years

Unresolved: none
