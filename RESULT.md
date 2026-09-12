Status: Step 9C.2 complete — historical RNOA Margin / Turnover change attribution

Implementation base:
- 536d5e6 Step 9C.1 complete

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 51
- formula practice cells: 222
- fresh Check: 0 / 0 / 222

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 55
- formula practice cells: 242
- fresh Check: 0 / 0 / 242

RNOA change attribution:
- 6 profitability-change families / 18 practice cells on five-year demo: yes
- attribution starts at fiscal-period index 2 (post-comparable): yes
- Margin Effect = ΔMargin × midpoint Turnover: yes
- Turnover Effect = ΔTurnover × midpoint Margin: yes
- Margin Effect + Turnover Effect reconciles to Direct ΔRNOA when defined: yes
- undefined Margin/Turnover inputs propagate to `#N/A` (no fabricated zero effects): yes
- zero driver change with defined inputs remains numeric 0.0: yes
- signs preserved (no ABS on practice formulas): yes
- live classification changes turnover-change / turnover-effect / driver-change expecteds: yes
- trusted RNOA CHANGE DRIVER CHECK tamper fails before recolor: yes
- exact/equivalent formulas pass; fabricated 0.0 rejected when expected `#N/A`: yes
- Step 9C.1 level decomposition families unchanged: yes
- Step 9B working-capital surface preserved: yes
- no automatic causal diagnosis or profitability quality score: yes

Preservation:
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/profitability_change.py`
- Add: `core/tests/test_profitability_change.py`
- Modify: `core/engine/component_catalog.py` — PROFITABILITY_CHANGE_COMPONENT_CATALOG + expand
- Modify: `core/model/historical_expected.py` — profitability_change_expected_series
- Modify: `core/engine/reference_model.py` — ALT DuPont change section + registration
- Modify: `core/trainer/workbook.py` — family meta for list/index
- Modify: `core/tests/test_*.py` — demo surface 51/222 and 55/242
- Modify: `skills/bav-trainer/SKILL.md` — surface counts + change-attribution note
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 226 passed
- base build/check/list -> 222 / 51 / 0-0-222 blank
- norm build/check/list -> 242 / 55 / 0-0-242 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- company-specific causal interpretation of margin vs intensity remains deferred
- ROE operating-versus-financing attribution remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical RNOA change-attribution surface addressed by this checkpoint
