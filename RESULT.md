Status: Step 4 correction pass complete

Files changed:
- Modify: `core/model/classification.py`
- Modify: `core/ingestion/reconciler.py`
- Modify: `core/tests/test_classification.py`
- Modify: `core/tests/test_line_identity.py`
- Modify: `RESULT.md`

Tests run:
- `pytest core/tests/test_line_identity.py -v` -> 13 passed
- `pytest core/tests/test_classification.py -v` -> 12 passed
- `pytest core/tests/test_reference_integrity.py -q` -> 18 passed
- `pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `pytest core/tests/test_trainer.py -q` -> 15 passed
- `pytest core/tests/ -q` -> 64 passed
- `python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> exit 0; Trainer + Answer Key; 13 components

Correction checks:
- conservative concept classification: DebtSecuritiesAvailableForSale → Financial Asset (label); EquityMethodInvestments → OLTA; CashFlowHedgeReserve → Equity; deferred-tax asset/liability concepts still correct
- duplicate identity inside existing source: AmbiguousStatementIdentityError before dict merge
- duplicate identity inside incoming source: AmbiguousStatementIdentityError before dict merge
- cross-document same-identity restatement: still merges with conflict logging
- case-insensitive bare-label override: `goodwill` matches `Goodwill`
- case-insensitive label: override: `label:GOODWILL` matches
- ambiguous duplicate-label override rejection: `label:Deferred income taxes` still fails

Preserved checks:
- Step 3 accounting integrity: classification + reference_integrity suites pass
- paired Trainer / Answer Key build: exit 0
- 13 semantic components: reported by CLI

Unresolved: none
