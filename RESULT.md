Status: Step 9G.1 complete — cross-company historical robustness matrix

Implementation base:
- f1cc147 Step 9F.3 complete
- 0c56192 Plan Step 9G.1

Matrix cases: 3/3 build + fresh Check + fully-filled Check pass
- asset-light services: 59 families / 248 cells
- inventory retail: 78 / 331
- capital-intensive manufacturer: 70 / 293

Ordinary demo preserved:
- no assumptions / no share history: 62 / 259
- normalization assumptions / no share history: 66 / 279

Share-enabled regressions preserved:
- shares only: 70 / 293
- shares + normalization: 78 / 331

Cross-company robustness evidence:
- three synthetic FY2021–FY2025 non-financial archetypes: yes
- source/reformulation integrity without validator relaxation: yes
- standardized payload → manual HK adapter round-trip: yes
- services omits Total-Assets-dependent quality families only: yes
- retail declining-revenue WC signed arithmetic: yes
- retail STI live judgment updates expecteds / rejects stale cache: yes
- retail Normalization Judgment updates normalized EPS; reported EPS unchanged: yes
- manufacturer lease judgment updates financing diagnostics; reported EPS unchanged: yes
- manufacturer falling share count has correct share-count effect sign: yes
- trusted source-cell tamper fails before recolor on all three: yes
- deferred Model_*/Scenario_Summary remain hidden placeholders: yes
- no new semantic family / sheet / CLI / forecast / valuation: yes
- fixtures are synthetic robustness cases, not empirical company data: yes

Preservation:
- CLI remains {ingest,build,check,list}
- DEMO_HK_Standardized.json unchanged (share-data-free)
- TARGET.md unchanged: yes
- forecasting / valuation not begun: yes
- production engine unchanged (robustness tests only): yes

Files changed:
- Add: `core/tests/cross_company_fixtures.py`
- Add: `core/tests/test_cross_company_robustness.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 281 passed
- cross-company matrix -> 15 passed
- base build/check/list -> 259 / 62 / 0-0-259 blank
- norm build/check/list -> 279 / 66 / 0-0-279 blank
- share-only -> 293 / 70; share+norm -> 331 / 78
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- basic-vs-diluted / period-end share-count analysis remains deferred
- company-specific dilution / normalization causal interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred
- synthetic fixtures are not real-company validation

Unresolved: none on the active cross-company historical robustness matrix addressed by this checkpoint
