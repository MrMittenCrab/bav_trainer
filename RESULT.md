Status: Step 4 complete

Files changed:
- Create: `core/data/line_identity.py`
- Create: `core/tests/test_line_identity.py`
- Modify: `core/ingestion/reconciler.py`
- Modify: `core/ingestion/excel_import.py`
- Modify: `core/trainer/workbook.py`
- Modify: `core/model/classification.py`
- Modify: `core/engine/reference_model.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`

Tests run:
- `pytest core/tests/test_line_identity.py -v` -> 10 passed
- `pytest core/tests/test_classification.py -v` -> 9 passed
- `pytest core/tests/test_reference_integrity.py -v` -> 18 passed
- `pytest core/tests/test_line_resolver.py -v` -> 6 passed
- `pytest core/tests/test_trainer.py -v` -> 15 passed
- `pytest core/tests/ -q` -> 58 passed
- `python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> exit 0; Trainer + Answer Key; 13 components

Identity checks:
- duplicate concept-qualified label preservation: Deferred income taxes asset/liability concepts remain two rows after merge; rowmap keys `Balance Sheet!concept=...|label=Deferred income taxes` both present; worksheet shows label twice
- ambiguous conceptless duplicate rejection: AmbiguousStatementIdentityError before build
- concept-specific override: `concept:DeferredIncomeTaxAssetsNet` / `LiabilitiesNet` apply independently; ambiguous `label:` selector rejected; bare unique `Goodwill` still works
- Excel Concept column: both `Line Item | dates` and `Concept | Line Item | dates` ingest correctly

Unresolved: none
