Status: Step 9E.1 complete — historical cash-conversion / accrual trend diagnostics

Implementation base:
- 787a1b9 Step 9D.1 complete

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 62
- formula practice cells: 259
- fresh Check: 0 / 0 / 259

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 66
- formula practice cells: 279
- fresh Check: 0 / 0 / 279

Cash-conversion trend diagnostics:
- 4 quality-change families / 15 practice cells on five-year demo with Total Assets: yes
- Change in CFO / Cash Conversion / Total Accruals (comparable): yes
- Change in Accrual Ratio (post-comparable, gated on Total Assets): yes
- no CFO -> no Earnings Quality sheet and no trend families: yes
- no Total Assets -> 3 trend families only; accrual-ratio change row literal N/A: yes
- undefined conversion/accrual-ratio inputs propagate to `#N/A`: yes
- numeric zero differences remain 0.0: yes
- signs preserved (no ABS on practice formulas): yes
- trusted EARNINGS QUALITY CHANGE CHECK tamper fails before recolor: yes
- exact/equivalent `#N/A` accepted; fabricated 0.0 rejected: yes
- composes with Accounting Judgment + Earnings Normalization Check: yes
- Step 9A quality level families unchanged: yes
- Step 9B/9C/9D surfaces preserved: yes
- no automatic earnings-quality good/bad labels: yes

Preservation:
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/earnings_quality_change.py`
- Add: `core/tests/test_earnings_quality_change.py`
- Modify: `core/engine/component_catalog.py` — QUALITY_CHANGE_COMPONENT_CATALOG + expand
- Modify: `core/model/historical_expected.py` — earnings_quality_change_expected_series
- Modify: `core/trainer/checker.py` — quality-change families in dynamic expected path
- Modify: `core/engine/reference_model.py` — Earnings Quality trend section + registration
- Modify: `core/trainer/workbook.py` — family meta for list/index
- Modify: `core/tests/test_*.py` — demo surface 62/259 and 66/279
- Modify: `skills/bav-trainer/SKILL.md` — surface counts + trend note
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 240 passed
- base build/check/list -> 259 / 62 / 0-0-259 blank
- norm build/check/list -> 279 / 66 / 0-0-279 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- company-specific causal interpretation of cash conversion / accruals remains deferred
- historical per-share expansion where share data is not supplied remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical cash-conversion trend surface addressed by this checkpoint
