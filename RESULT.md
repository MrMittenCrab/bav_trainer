Status: Step 5 correction pass complete

Files changed:
- Create: `core/trainer/xlsx_fill_patch.py` — OOXML ZIP fill writer preserving formula `<f>` / cached `<v>`
- Modify: `core/trainer/checker.py` — collect fills then `apply_fill_updates`; no openpyxl save for recolor
- Modify: `core/tests/test_trainer.py` — repeated equivalent-formula cached-result regression + OOXML inject helper
- Modify: `core/tests/test_reference_integrity.py` — self-contained assumptions from temp Answer Key sidecar
- Delete (untrack): `example/DEMO_HK_Answer_Key.component_map.json`
- Delete (untrack): `example/DEMO_HK_Answer_Key.assumptions.json`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx` (unchecked blank yellow Trainer)
- Modify: `RESULT.md`
- Keep: existing narrow `.gitignore` rules for generated demo/build metadata

Tests run:
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 14 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v` -> 18 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 26 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 81 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> exit 0; 13 components
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 13 practice cells: 0 correct, 0 incorrect, 13 blank.`
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only

Generated-metadata hygiene:
- committed Answer-Key sidecars removed: `example/DEMO_HK_Answer_Key.component_map.json` and `.assumptions.json` deleted from git index; only `*_Trainer.xlsx` + `*_Answer_Key.xlsx` remain as demo workbooks
- demo rebuild ignored sidecars cleanly: after `python -m core build ... -o example/DEMO_HK_Trainer.xlsx`, local sidecars/`rowmap.json` may exist on disk but `git status --short` does not list them as untracked

Check cache preservation:
- equivalent non-reference formula + valid cached result first Check: `correct=1` (formula `=4150.866...` ≠ Answer Key formula; cached path used)
- cached value after first Check: `4150.866462793068` preserved (not wiped to `None`)
- second Check without Excel recalculation: still `correct=1`
- learner formula unchanged: `True`; fill `C8E6C9`

Preserved Step 5 contract:
- Trainer leakage audit: no `_ComponentMap` / `_Ref*` / Trainer sidecars; practice cells blank yellow / no Notes
- Answer Key formula + Note contract: working formulas + legacy Notes; embedded `_ComponentMap` retained
- workbook-wide yellow/green/red Check: blank `FFFF00` / correct `C8E6C9` / incorrect `FFC7CE`
- Hint/Reveal absent: no CLI/API/macros

Unresolved: none
