Status: Step 4 final correction pass complete

Files changed:
- Modify: `core/data/line_identity.py`
- Modify: `core/model/classification.py`
- Modify: `core/tests/test_line_identity.py`
- Modify: `core/tests/test_classification.py`
- Modify: `RESULT.md`

Tests run:
- `pytest core/tests/test_line_identity.py -k "case_variant_label or case_insensitive or differing_only_by_case" -v` -> 4 passed
- `pytest core/tests/test_classification.py -k "preferred_stock" -v` -> 1 passed
- `pytest core/tests/test_line_identity.py -v` -> 16 passed
- `pytest core/tests/test_classification.py -v` -> 13 passed
- `pytest core/tests/test_reference_integrity.py -q` -> 18 passed
- `pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `pytest core/tests/test_trainer.py -q` -> 15 passed
- `pytest core/tests/ -q` -> 68 passed
- `python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> exit 0; Trainer + Answer Key; 13 components; no `*_reference.xlsx`

Final identity checks:
- case-insensitive displayed-label identity: `Goodwill` == `GOODWILL` (and NBSP/whitespace) with same concept
- concept identifiers remain exact: `Goodwill` != `goodwill` as concepts
- case-only conceptless duplicate rejection: AmbiguousStatementIdentityError
- case-variant cross-document label merge: one row; display label stays `Goodwill`
- rowmap canonical identity + original worksheet display: keys use casefolded label; sheet still shows `Deferred income taxes` twice

Final classification checks:
- redeemable preferred stock no longer forced to Equity: PreferredStockSubjectToMandatoryRedemption + Long-term debt → Financial Liability
- previous debt-security / equity-method / cash-flow-hedge regressions: still pass
- deferred-tax asset/liability concept behavior: still pass

Preserved checks:
- Step 3 integrity: classification + reference_integrity pass
- paired Trainer / Answer Key: both exist; blank yellow Trainer practice cells; Answer Key Notes present; 13 components

Unresolved: none
