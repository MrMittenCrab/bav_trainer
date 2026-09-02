# RESULT.md

**Status:** Step 2B complete

**Files changed:**
- `core/model/line_resolver.py` (new)
- `core/model/financial_math.py`
- `core/engine/reference_model.py`
- `core/tests/test_line_resolver.py` (new)
- `core/tests/test_reference_integrity.py`
- `RESULT.md`

**Summary:** Canonical `resolve_line()` now selects revenue / NI / pretax / tax / interest / equity for both Python `compute_anchor()` and the Excel reference model. Demo tax no longer resolves to `Profit before tax`. Optional interest lines and equity alias/fallback stay consistent; DuPont uses condensed Equity; dependency integrity checks were strengthened.

**Tests run:**
- `python -m pytest core/tests/test_line_resolver.py -v --tb=short` → 6 passed
- `python -m pytest core/tests/test_reference_integrity.py -v --tb=short` → 13 passed
- `python -m pytest core/tests/test_trainer.py -v --tb=short` → 15 passed
- `python -m pytest core/tests/ -q --tb=line` → 34 passed

**Unresolved:** Not recalculated in desktop Excel (openpyxl formula/presence checks only).
