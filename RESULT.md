Status: Step 9D.1 complete — historical ROE operating / financing attribution

Implementation base:
- 2ba3e65 Step 9C.2 complete

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 58
- formula practice cells: 244
- fresh Check: 0 / 0 / 244

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 62
- formula practice cells: 264
- fresh Check: 0 / 0 / 264

ROE operating / financing attribution:
- 7 ROE-attribution families / 22 practice cells on five-year demo: yes
- Financing Contribution = FLEV × Spread (comparable periods): yes
- level bridge RNOA + Financing Contribution = decomposed ROE when defined: yes
- Operating Effect = Direct Change in RNOA: yes
- Leverage Effect = ΔFLEV × midpoint Spread: yes
- Spread Effect = ΔSpread × midpoint FLEV: yes
- Financing Effect = Leverage + Spread effects: yes
- Operating + Financing effects reconcile to Direct ΔROE when defined: yes
- attribution starts at fiscal-period index 2 for change rows: yes
- undefined FLEV/Spread propagate to `#N/A` (0 × `#N/A` stays `#N/A`): yes
- live classification changes financing contribution / leverage / financing / driver expecteds: yes
- trusted ROE LEVEL / ROE CHANGE ATTRIBUTION CHECK tamper fails before recolor: yes
- exact/equivalent `#N/A` accepted; fabricated 0.0 rejected: yes
- existing direct ROE (decomposed) formula unchanged: yes
- Step 9C RNOA level/change families unchanged: yes
- Step 9B working-capital surface preserved: yes
- no automatic leverage-quality or financing-policy judgment: yes

Preservation:
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/roe_attribution.py`
- Add: `core/tests/test_roe_attribution.py`
- Modify: `core/engine/component_catalog.py` — ROE_ATTRIBUTION_COMPONENT_CATALOG + expand
- Modify: `core/model/historical_expected.py` — roe_attribution_expected_series
- Modify: `core/engine/reference_model.py` — ALT DuPont ROE attribution sections + registration
- Modify: `core/trainer/workbook.py` — family meta for list/index
- Modify: `core/tests/test_*.py` — demo surface 58/244 and 62/264
- Modify: `skills/bav-trainer/SKILL.md` — surface counts + ROE attribution note
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 232 passed
- base build/check/list -> 244 / 58 / 0-0-244 blank
- norm build/check/list -> 264 / 62 / 0-0-264 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- company-specific causal interpretation of operating vs financing ROE remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical ROE operating/financing attribution surface addressed by this checkpoint
