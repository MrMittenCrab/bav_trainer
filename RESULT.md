Status: Step 9F.3 complete — historical normalized diluted EPS bridge

Implementation base:
- 1e0d412 Step 9F.2 complete
- 3cf9244 Plan Step 9F.3

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

Share-enabled five-year fixture:
- shares, no normalization: 70 families / 293 cells; Step 9F.3 absent
- shares + normalization: 78 families / 331 cells; fresh Check 0 / 0 / 331
  - four Step 9F.3 families / 18 practice cells

Normalized diluted EPS bridge:
- Normalization Adjustment per Diluted Share = after-tax adj / diluted WAS: yes
- Normalized Diluted EPS = normalized NI / diluted WAS: yes
- level bridge: Reported EPS + adj/share = Normalized EPS: yes
- change bridge: ΔReported EPS + normalization effect = ΔNormalized EPS: yes
- gated on both shares and active normalization cases: yes
- live Normalization Judgment recomputes normalized EPS; reported EPS unchanged: yes
- `#N/A` after-tax adj propagates to adj/share and normalized EPS: yes
- zero adj with undefined tax remains numeric 0; normalized EPS = reported EPS: yes
- trusted normalization links + level/change checks; tamper fails before recolor: yes
- Step 9F.1–9F.2 rows/formulas unchanged: yes
- no basic-vs-diluted / growth rates / valuation: yes

Preservation:
- CLI remains {ingest,build,check,list}
- DEMO_HK_Standardized.json unchanged (share-data-free)
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/normalized_per_share.py`
- Add: `core/tests/test_normalized_per_share.py`
- Modify: `core/engine/component_catalog.py` — NORMALIZED_PER_SHARE catalog + expand
- Modify: `core/model/historical_expected.py` — normalized-per-share expected routing
- Modify: `core/engine/reference_model.py` — gated bridge section on Per Share Analysis
- Modify: `core/trainer/checker.py` — include normalized families in per-share Check path
- Modify: `core/trainer/workbook.py` — family meta
- Modify: `core/tests/test_per_share.py` / `test_per_share_attribution.py` — share+norm counts
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 266 passed
- base build/check/list -> 259 / 62 / 0-0-259 blank; no Per Share Analysis
- norm build/check/list -> 279 / 66 / 0-0-279 blank; no Per Share Analysis
- share-only -> 293 / 70; share+norm -> 331 / 78
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- basic-vs-diluted / period-end share-count analysis remains deferred
- company-specific dilution / normalization causal interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical normalized diluted-EPS bridge addressed by this checkpoint
