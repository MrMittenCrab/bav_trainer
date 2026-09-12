Status: Step 9F.1 complete — historical diluted per-share foundation

Implementation base:
- 8959cad Step 9E.1 complete
- 8b88d53 Plan Step 9F.1

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
- without normalization: 66 families / 277 cells; fresh Check 0 / 0 / 277
- with normalization: 70 families / 297 cells; fresh Check 0 / 0 / 297
- Per Share Analysis present; 4 per-share families / 18 practice cells

Historical share contract:
- `HistoricalShareData` + `StandardizedFinancials.historical_shares`: yes
- standardized payload round-trip preserves share history: yes
- structured JSON/YAML ingest of `historical_shares`: yes
- multi-document merge newest-wins; scale_basis mismatch fails: yes
- absent / empty shares omit module: yes
- incomplete / None / zero / negative / unsupported scale fail closed: yes
- share counts remain populated trusted inputs (never practice): yes
- no use of `assumptions["marketData"]["dilutedShares"]`: yes

Per-share diagnostics:
- Reported Diluted EPS = NI / diluted WAS: yes
- NOPAT per Diluted Share = NOPAT / diluted WAS: yes
- absolute Change in Diluted EPS / Change in Diluted WAS: yes
- first-period change rows literal N/A and not practice: yes
- `#N/A` NOPAT → `#N/A` NOPAT/share; fabricated 0.0 rejected: yes
- dynamic Check recomputes via current treatment-conditioned anchor: yes
- live Accounting Judgment coexistence (EPS/share row unchanged): yes
- share-row / source-link tamper fails before recolor: yes
- no normalized EPS / basic-vs-diluted attribution: yes

Preservation:
- CLI remains {ingest,build,check,list}
- DEMO_HK_Standardized.json unchanged (share-data-free)
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/per_share.py`
- Add: `core/tests/test_per_share.py`
- Modify: `core/data/interface.py` — HistoricalShareData
- Modify: `core/data/standardized_io.py` — serialize/deserialize historical_shares
- Modify: `core/ingestion/manual_hk.py` — JSON/YAML share ingest
- Modify: `core/ingestion/reconciler.py` — merge historical shares
- Modify: `core/engine/component_catalog.py` — PER_SHARE_COMPONENT_CATALOG + expand
- Modify: `core/model/historical_expected.py` — per_share expected routing
- Modify: `core/engine/reference_model.py` — gated Per Share Analysis sheet
- Modify: `core/trainer/check_context.py` — trusted Per Share validation
- Modify: `core/trainer/checker.py` — dynamic compute_per_share_series
- Modify: `core/trainer/workbook.py` — family meta
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 252 passed
- base build/check/list -> 259 / 62 / 0-0-259 blank; no Per Share Analysis
- norm build/check/list -> 279 / 66 / 0-0-279 blank; no Per Share Analysis
- share-enabled fixture -> 277 / 66 and 297 / 70
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- normalized EPS remains deferred
- basic-vs-diluted / period-end share-count analysis remains deferred
- company-specific dilution / per-share causal interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical diluted per-share surface addressed by this checkpoint
