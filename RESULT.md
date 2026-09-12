Status: Step 9A.4 complete — historical DuPont undefined-ratio hardening

Implementation base:
- fea4b384 Step 9.3

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 30
- formula practice cells: 141
- fresh Check: 0 / 0 / 141

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 34
- formula practice cells: 161
- fresh Check: 0 / 0 / 161

DuPont undefined-ratio semantics:
- Sales Growth zero prior Revenue -> #N/A: yes
- NOPAT Margin zero Revenue -> #N/A: yes
- RNOA zero average NOA -> #N/A: yes
- After-tax CoD zero average Net Debt -> #N/A: yes
- FLEV / Actual ROE zero average Equity -> #N/A: yes
- Spread / decomposed ROE undefined propagation: yes
- explicit zero numerator with nonzero denominator -> numeric 0.0 preserved: yes
- Excel Answer Key DuPont formulas use NA() for zero denominators: yes
- Formula Check exact/equivalent #N/A accepted; fabricated 0.0 rejected: yes
- Step 9A earnings-quality #N/A behavior preserved: yes
- Step 9A.3 source-completeness behavior preserved: yes
- stale optional-interest hint removed: yes

Preservation:
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- working-capital interpretation / forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/ratio_values.py`
- Modify: `core/model/earnings_quality.py` — shared ratio_or_na
- Modify: `core/model/financial_math.py` — DuPont #N/A + propagation
- Modify: `core/engine/reference_model.py` — DuPont NA() guards
- Modify: `core/engine/component_catalog.py` — interest hint + denominator Notes
- Modify: `core/tests/test_reference_integrity.py` — DuPont #N/A regressions
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 197 passed
- base build/check/list -> 141 / 30 / 0-0-141 blank
- norm build/check/list -> 161 / 34 / 0-0-161 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- effective-tax-rate zero-denominator convention and any downstream NOPAT implications remain unchanged in this checkpoint
- dormant deferred-forecast defaults/fallbacks remain (e.g. revenue `or 1000.0` path)
- working-capital / driver interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical DuPont surface addressed by this checkpoint
