Status: Step 9H.1 complete — historical v1 exit gate

Implementation base:
- 76ec6f2 Step 9G.1 complete
- d5d4562 Plan Step 9H.1

Active family namespace: orders 1..78 unique; deferred forecast/valuation specs disjoint: yes
Normal build forecast isolation (`run_scenario` / `weighted_ivps` fail-fast stubs): yes
Trainer/Answer-Key practice contract verified across all canonical demo cells (66/279): yes
Check formula-preservation / non-disclosure verified: yes
Canonical demo workbooks regenerated from source: yes
TARGET.md SHA-256 unchanged:
  c826071609046ba4205aed7fba564bbcc96b6afabec5bfe00b6cf38976d64b08

Surfaces preserved:
- base demo: 62 / 259 / 0-0-259 blank
- normalization demo: 66 / 279 / 0-0-279 blank
- canonical committed demo pair: 66 / 279 / 0-0-279 blank
- shares only: 70 / 293
- shares + norm: 78 / 331
- services matrix: 59 / 248
- retail matrix: 78 / 331
- manufacturer matrix: 70 / 293

Release-gate notes:
- historical-v1 model-construction foundation complete/release-gated: yes
- cross-company matrix remains synthetic, not empirical company validation: yes
- forecasting / valuation remain deferred: yes
- no new semantic family / sheet / CLI / forecast / valuation: yes
- production model code unchanged: yes

Preservation:
- CLI remains {ingest,build,check,list}
- DEMO_HK_Standardized.json / DEMO_HK_Assumptions.json unchanged: yes
- TARGET.md unchanged: yes

Files changed:
- Add: `core/tests/test_historical_v1_exit_gate.py`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 288 passed
- exit-gate module -> 7 passed
- focused release suite (exit + cross-company + trainer + integrity + norm + per-share) -> 186 passed
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- basic-vs-diluted / period-end share-count analysis remains deferred
- company-specific causal interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred
- synthetic fixtures are not real-company validation

Unresolved: none on the historical-v1 exit gate addressed by this checkpoint
