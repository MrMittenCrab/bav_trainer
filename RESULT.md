Status: Step 9B.1 complete — historical working-capital diagnostics foundation

Implementation base:
- 67f273a Step 9.5 (Step 9A.5 complete)

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 36
- formula practice cells: 168
- fresh Check: 0 / 0 / 168

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 40
- formula practice cells: 188
- fresh Check: 0 / 0 / 188

Working-capital diagnostics:
- applicability gate (any nonzero OWCA or OWCL): yes
- all-zero OWCA/OWCL omits Working Capital Analysis sheet: yes
- six families / 27 practice cells on five-year applicable demo: yes
- OWCA / Revenue, OWCL / Revenue, NOWC / Revenue: yes
- Change in Revenue, Change in NOWC: yes
- Incremental NOWC / Change in Revenue: yes
- zero Revenue / zero ΔRevenue -> `#N/A` / Excel `NA()`: yes
- first-period change/incremental cells are non-applicable `N/A` text: yes
- signed ΔNOWC / ΔRevenue retained (no absolute-value conversion): yes
- live classification-conditioned Check (short-term investment FA↔OWCA): yes
- trusted Condensed source-link tamper rejected before recolor: yes
- exact/equivalent `#N/A` accepted; fabricated `0.0` rejected: yes
- no automatic good/bad quality labels or seasonality inference: yes
- Step 9A earnings-quality / source-completeness / `#N/A` conventions preserved: yes

Preservation:
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/working_capital.py`
- Add: `core/tests/test_working_capital.py`
- Modify: `core/engine/component_catalog.py` — WORKING_CAPITAL_COMPONENT_CATALOG + expand
- Modify: `core/model/historical_expected.py` — working_capital_expected_series
- Modify: `core/engine/reference_model.py` — applicability, sheet, registration
- Modify: `core/trainer/check_context.py` — trusted Working Capital Analysis sheet
- Modify: `core/trainer/workbook.py` — family meta for list/index
- Modify: `core/tests/test_*.py` — demo surface 36/168 and 40/188
- Modify: `skills/bav-trainer/SKILL.md` — surface counts + schedule list
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 210 passed
- base build/check/list -> 168 / 36 / 0-0-168 blank
- norm build/check/list -> 188 / 40 / 0-0-188 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- working-capital interpretation beyond mechanical diagnostics remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical working-capital diagnostic surface addressed by this checkpoint
