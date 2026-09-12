Status: Step 9C.1 complete — historical RNOA margin / turnover driver decomposition

Implementation base:
- 70f2af5 Step 9B.2 complete

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 45
- formula practice cells: 204
- fresh Check: 0 / 0 / 204

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 49
- formula practice cells: 224
- fresh Check: 0 / 0 / 224

RNOA margin / turnover drivers:
- 4 profitability-driver families / 16 practice cells on five-year demo: yes
- Average NOA = (prior + current NOA) / 2: yes
- NOA Turnover = Revenue / Average NOA: yes
- NOA Intensity = Average NOA / Revenue: yes
- RNOA from Margin × Turnover reconciles to direct RNOA when defined: yes
- undefined decomposition yields Excel/Python `#N/A` and check text `N/A` (not false CHECK): yes
- zero Average NOA -> turnover `#N/A`: yes
- zero Revenue -> intensity `#N/A`; turnover may remain numeric 0.0: yes
- existing direct RNOA / NOPAT Margin formulas unchanged: yes
- live classification changes Average NOA / turnover / intensity / driver RNOA: yes
- trusted RNOA DRIVER CHECK tamper fails before recolor: yes
- exact/equivalent `#N/A` accepted; fabricated `0.0` rejected: yes
- Step 9B working-capital surface preserved: yes
- no automatic causal diagnosis or profitability quality score: yes

Preservation:
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/profitability_drivers.py`
- Add: `core/tests/test_profitability_drivers.py`
- Modify: `core/engine/component_catalog.py` — PROFITABILITY_DRIVER_COMPONENT_CATALOG + expand
- Modify: `core/model/historical_expected.py` — profitability_driver_expected_series
- Modify: `core/engine/reference_model.py` — ALT DuPont driver section + registration
- Modify: `core/trainer/workbook.py` — family meta for list/index
- Modify: `core/tests/test_*.py` — demo surface 45/204 and 49/224
- Modify: `skills/bav-trainer/SKILL.md` — surface counts + RNOA driver note
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 219 passed
- base build/check/list -> 204 / 45 / 0-0-204 blank
- norm build/check/list -> 224 / 49 / 0-0-224 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- company-specific causal interpretation of margin vs intensity remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical RNOA margin/turnover driver surface addressed by this checkpoint
