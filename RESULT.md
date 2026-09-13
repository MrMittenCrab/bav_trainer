Status: Step 9L.1 complete — lease-liability diagnostics + judgment-selector hardening

Implementation base:
- e81a048 Step 9K.1 complete
- b82f2fe Plan Step 9L.1

Review fixes / evidence:
- GOOGL provenance drift fixed: yes
- stale Answer-Key hash removed from persistent reference doc: yes
- identity: judgment selectors added: yes
- split duplicate-concept lease case verified: yes
- lease module orders 87–90: yes
- aggregate-vs-split gating verified: yes
- classification switch changes NOA/Net Debt but not raw lease ratio: yes
- no ROU / payment / discount-rate / amortization inference: yes
- canonical demos regenerated: yes
- forecasting / valuation still deferred: yes
- GOOGL workbook hash unchanged:
  81faf2882d0df07ecf5def45695431c1935b4f7a94c1e017367596a063063896
- TARGET.md unchanged by Cursor:
  88f69fb47d8464084d504b6e65be9742d5e4924ca78a2c3412156293b3fa2015

Product surfaces:
- active family orders 1..90
- base demo: 74 / 312
- normalization demo: 78 / 332
- shares only: 82 / 346
- shares + norm: 90 / 384
- services: 59 / 248
- retail: 78 / 331
- manufacturer: 74 / 311
- CLI: {ingest, build, check, list}
- Step 9I.1 presentation intact: yes
- deferred Model_*/Scenario_Summary remain hidden placeholders: yes

Files changed:
- Add: `core/model/lease_liability.py`
- Add: `core/tests/test_lease_liability.py`
- Modify: classification/judgment selectors, line_resolver, component_catalog, historical_expected
- Modify: reference_model / checker / workbook
- Modify: surface/exit-gate/integrity tests
- Modify: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `docs/GOOGL_HISTORICAL_REFERENCE.md`, `README.md`, `skills/bav-trainer/SKILL.md`, `RESULT.md`, `IMPLEMENTATION.md`

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 316 passed
- CLI -> `{ingest,build,check,list}` only
- Components resolved on canonical demo build: 332

Known deferred limitations:
- forecasting / valuation / scenarios remain deferred
- ROU-asset diagnostics, split lease aggregation, lease payments/discount rates deferred
- explicit capex / reinvestment bridge awaits source/sign contract (Priority B)
- next historical candidate: goodwill / acquired intangibles / acquisition-cash diagnostics (Priority A)
- synthetic fixtures are not real-company validation

Unresolved: none on the lease-liability diagnostics / judgment-selector hardening addressed by this checkpoint
