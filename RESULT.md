Status: Step 7 correction complete — period-axis integrity and metadata hygiene

Implementation base:
- 598948d3 Step 7 multi-period historical model

Period-axis audit:
- descending input canonicalized oldest -> newest: yes
- supported descending Excel input canonicalized: yes
- duplicate fiscal periods rejected: yes
- gapped annual histories rejected: yes
- comparative formulas use true previous fiscal year: yes

Trainer metadata audit:
- stale Trainer component-map sidecar removed: yes
- stale Trainer trainer.json removed: yes
- stale Trainer assumptions sidecar removed: yes
- Answer Key semantic metadata preserved: yes
- Trainer list resolves current 25 families: yes
- Trainer answer leakage: none

Demo preservation:
- fiscal periods: 5
- conceptual families: 25
- concrete practice cells: 118
- Trainer index rows: 25
- fresh Check: 0 correct / 0 incorrect / 118 blank

Files changed:
- Create: `core/model/period_axis.py` — `canonical_fiscal_periods()` / `PeriodAxisError`
- Modify: `core/engine/reference_model.py` — consume canonical period axis before anchor/expansion/build
- Modify: `core/engine/component_catalog.py` — `expand_historical_specs()` rejects non-increasing/duplicate dates
- Modify: `core/trainer/workbook.py` — `remove_trainer_sidecars()` on every Trainer generation
- Modify: `core/tests/test_reference_integrity.py` — descending / Excel / duplicate / contiguous regressions
- Modify: `core/tests/test_trainer.py` — expansion contract + stale-sidecar cleanup
- Modify: `IMPLEMENTATION.md`, `RESULT.md`

Tests:
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "period or chronological or descending or duplicate or contiguous" -v` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -k "period or sidecar or list" -v` -> 8 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 30 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 36 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 103 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> Components resolved: 118
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.`
- `PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx` -> 25 schedule groups / 118 concrete cells

Unresolved: none
