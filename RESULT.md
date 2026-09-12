Status: Step 9I.1 complete — learner-ready historical presentation

Implementation base:
- 80985ef Step 9H.1 complete
- 917a0f5 Plan Step 9I.1

Presentation contract:
- fresh visible workbook fonts: Aptos Narrow 11 everywhere
- fresh visible workbook fills: white/yellow only
- fresh visible workbook borders: none
- Check green/red feedback preserved: yes
- canonical example pair regenerated: yes

Documentation:
- root README replaced with practical trainer guide: yes
- legacy/pipeline origin material absent from root README: yes
- README-HK-TRAINER lineage/plugin sections removed: yes

Surfaces preserved:
- base demo: 62 / 259 / 0-0-259 blank
- normalization demo: 66 / 279 / 0-0-279 blank
- canonical committed demo pair: 66 / 279 / 0-0-279 blank
- shares only: 70 / 293
- shares + norm: 78 / 331
- services matrix: 59 / 248
- retail matrix: 78 / 331
- manufacturer matrix: 70 / 293
- active family namespace 1..78 unchanged: yes

Preservation:
- CLI remains {ingest,build,check,list}
- formulas / expected values / Check semantics unchanged: yes
- DEMO_HK_Standardized.json / DEMO_HK_Assumptions.json unchanged: yes
- TARGET.md unchanged:
  c826071609046ba4205aed7fba564bbcc96b6afabec5bfe00b6cf38976d64b08
- forecasting / valuation still deferred: yes

Files changed:
- Add: `core/tests/test_learner_ready_presentation.py`
- Modify: `core/trainer/workbook.py` — minimal white/yellow style
- Modify: `core/tests/test_trainer.py` — style assertions
- Replace: `README.md`
- Modify: `README-HK-TRAINER.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 292 passed
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain
- forecasting / valuation / investment conclusions remain deferred
- synthetic fixtures are not real-company validation

Unresolved: none on the learner-ready presentation polish addressed by this checkpoint
