Status: Step 9F.2 complete — historical diluted EPS earnings / share-count attribution

Implementation base:
- 7e9afb1 Step 9F.1 complete
- a89b24f Prepare Step 9F.2

Historical formula surface (no normalization assumptions, no share history):
- fiscal periods: 5
- formula families: 62
- formula practice cells: 259
- fresh Check: 0 / 0 / 259
- Per Share Analysis sheet: absent

Step 9A illustrative demo (with DEMO_HK_Assumptions.json, no share history):
- fiscal periods: 5
- formula families: 66
- formula practice cells: 279
- fresh Check: 0 / 0 / 279
- Per Share Analysis sheet: absent

Share-enabled five-year fixture (in-memory demo + diluted WAS 1000+25*i):
- without normalization: 70 families / 293 cells; fresh Check 0 / 0 / 293
- with normalization: 74 families / 313 cells; fresh Check 0 / 0 / 313
- Per Share Analysis present; 8 per-share(+attribution) families / 34 practice cells
  - Step 9F.1: 4 families / 18 cells
  - Step 9F.2 attribution: 4 families / 16 cells

Diluted EPS attribution:
- exact midpoint identity: Earnings Effect + Share-Count Effect = ΔEPS: yes
- Earnings Effect = ΔNI × midpoint inverse diluted shares: yes
- Share-Count Effect = Δinverse shares × midpoint NI: yes
- signs preserved (rising shares + positive NI → negative share effect; losses can reverse): yes
- zero NI remains numeric (not `#N/A`): yes
- generated DILUTED EPS CHANGE ATTRIBUTION CHECK trusted; tamper fails before recolor: yes
- practice formulas contain no ABS(): yes
- Step 9F.1 rows/formulas unchanged: yes
- no normalized EPS / basic-vs-diluted / causal share-change labels: yes
- dynamic Check derives attribution from live PerShareSeries + treatment-conditioned NI: yes
- live Accounting Judgment coexistence: yes

Preservation:
- CLI remains {ingest,build,check,list}
- DEMO_HK_Standardized.json unchanged (share-data-free)
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/per_share_attribution.py`
- Add: `core/tests/test_per_share_attribution.py`
- Modify: `core/engine/component_catalog.py` — attribution catalog + expand
- Modify: `core/model/historical_expected.py` — attribution expected routing
- Modify: `core/engine/reference_model.py` — attribution section on Per Share Analysis
- Modify: `core/trainer/checker.py` — attribution families in per-share Check path
- Modify: `core/trainer/workbook.py` — family meta
- Modify: `core/tests/test_per_share.py` — share-enabled surface counts
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 259 passed
- base build/check/list -> 259 / 62 / 0-0-259 blank; no Per Share Analysis
- norm build/check/list -> 279 / 66 / 0-0-279 blank; no Per Share Analysis
- share-enabled fixture -> 293 / 70 and 313 / 74
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- normalized EPS remains deferred
- basic-vs-diluted / period-end share-count analysis remains deferred
- company-specific dilution / share-change causal interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical diluted-EPS attribution surface addressed by this checkpoint
