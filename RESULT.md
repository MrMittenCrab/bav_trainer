Status: Step 9K.1 complete — PP&E / D&A asset-intensity diagnostics

Implementation base:
- 8b5df8b Step 9J.1 complete
- c5a05ea Plan Step 9K.1

Fixed-asset evidence:
- PP&E + D&A line resolution: yes
- FixedAssetSeries + availability gate (both required): yes
- eight families orders 79–86 on ALT DuPont: yes
- no new user-facing worksheet: yes
- average PP&E / turnover / intensity / change / D&A ratios: yes
- D&A/Average PP&E labeled context-only (not pure depreciation rate): yes
- capex not implemented or inferred: yes
- Check validates new families; trusted tamper fails closed: yes
- canonical demos regenerated: yes
- forecasting / valuation still deferred: yes
- GOOGL workbook hash unchanged:
  81faf2882d0df07ecf5def45695431c1935b4f7a94c1e017367596a063063896
- TARGET.md unchanged by Cursor:
  88f69fb47d8464084d504b6e65be9742d5e4924ca78a2c3412156293b3fa2015

Product surfaces:
- active family orders 1..86
- base demo: 70 / 294
- normalization demo: 74 / 314
- shares only: 78 / 328
- shares + norm: 86 / 366
- services: 59 / 248
- retail: 78 / 331
- manufacturer: 70 / 293
- CLI: {ingest, build, check, list}
- Step 9I.1 presentation intact: yes
- deferred Model_*/Scenario_Summary remain hidden placeholders: yes

Files changed:
- Add: `core/model/fixed_asset.py`
- Add: `core/tests/test_fixed_asset.py`
- Modify: `core/model/line_resolver.py`
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/workbook.py`
- Modify: exit-gate / surface / integrity tests
- Modify: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `docs/GOOGL_HISTORICAL_REFERENCE.md`
- Modify: `README.md`, `skills/bav-trainer/SKILL.md`, `RESULT.md`, `IMPLEMENTATION.md`

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 304 passed
- CLI -> `{ingest,build,check,list}` only
- Components resolved on canonical demo build: 314

Known deferred limitations:
- forecasting / valuation / scenarios remain deferred
- explicit capex / reinvestment bridge awaits source/sign contract (Priority B)
- next historical candidate: lease intensity / lease-liability diagnostics (Priority A)
- synthetic fixtures are not real-company validation

Unresolved: none on the PP&E / D&A asset-intensity diagnostics addressed by this checkpoint
