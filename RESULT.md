Status: Step 5 complete

Files changed:
- Modify: `core/model/classification.py` — remove unsafe `commonstock` Equity shortcut
- Modify: `core/trainer/workbook.py` — sanitize Trainer; drop `_Ref*` / `_TrainerMeta`; no Trainer sidecars; simplify index
- Modify: `core/trainer/checker.py` — workbook-wide non-disclosing `check_workbook` + `CheckSummary`
- Modify: `core/trainer/__init__.py` — export Check only; drop Hint/Reveal
- Modify: `core/__main__.py` — workbook-wide `check`; remove `hint`/`reveal`; preserve `concept` on ingest JSON export
- Delete: `core/trainer/hints.py`
- Delete: `core/templates/TrainerMacros.bas`
- Modify: `core/tests/test_classification.py` — redeemable common-stock regression
- Modify: `core/tests/test_trainer.py` — Trainer sanitization + Check contract regressions
- Modify: `core/tests/test_line_identity.py` — concept JSON round-trip regression
- Modify: `core/tests/test_reference_integrity.py` — load map from Answer Key; assumptions path update
- Modify: `README-HK-TRAINER.md`, `skills/bav-trainer/SKILL.md` — final product loop
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx` (+ Answer Key sidecars)
- Delete: stale `example/*_reference*`, `example/*.trainer.json`, `example/rowmap.json`
- Modify: `RESULT.md`

Tests run:
- `PYTHONPATH=. pytest core/tests/test_classification.py -k "common_stock or preferred_stock or debt_security or equity_method or cash_flow_hedge" -v` -> 5 passed
- `PYTHONPATH=. pytest core/tests/test_classification.py -v` -> 14 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -v` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -q` -> 18 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 25 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 80 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> exit 0; Trainer + Answer Key; 13 components
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 13 practice cells: 0 correct, 0 incorrect, 13 blank.`
- `PYTHONPATH=. python -m core --help` -> subcommands `{ingest,build,check,list}` only (no hint/reveal)

Trainer / Answer Key contract:
- Trainer practice cells: all 13 blank, `#FFFF00`, no comments immediately after build
- Trainer answer-bearing hidden sheets/sidecars: none (`_ComponentMap` / `_RefFormulas` / `_RefValues` / `_TrainerMeta` absent; no `.trainer.json` / Trainer `.component_map.json`)
- Answer Key formulas + Notes: all 13 practice cells retain working `=` formulas, `#FFFF00`, non-empty legacy Notes; `_ComponentMap` + `.component_map.json` retained on Answer Key only

Workbook-wide Check:
- fresh blank workbook: 13 blank; all remain yellow after Check
- mixed correct/incorrect/blank color test: exact formula → `C8E6C9`; wrong `=1+1` → `FFC7CE`; remaining blank → `FFFF00`
- recheck refresh behavior: wrong→red, corrected formula→green, cleared→yellow
- content preservation: Check does not alter practice-cell values or add Notes
- answer/hint disclosure scan: CLI Check output contains no Answer Key formulas, expected values, or hint strings

Removed surfaces:
- Hint API/CLI: deleted (`core.trainer.hints`, `python -m core hint`)
- Reveal API/CLI: deleted (`reveal_answer`, `python -m core reveal`)
- Trainer macros: `core/templates/TrainerMacros.bas` deleted

Identity round trip:
- concept preservation: `ingest -o` writes `"concept"` on every statement row (`""` when absent); Excel Concept|Line Item source → JSON → `HKManualDocumentAdapter` reload keeps both deferred-tax concepts separately identifiable

Examples:
- Trainer: `example/DEMO_HK_Trainer.xlsx` (fresh unchecked blank yellow practice cells)
- Answer Key: `example/DEMO_HK_Answer_Key.xlsx` (+ `.component_map.json`, `.assumptions.json`)
- stale reference artifacts: removed (`*_reference.xlsx`, `*.trainer.json`, committed `rowmap.json`)

Unresolved: none
