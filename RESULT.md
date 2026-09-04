Status: Step 6 complete

Implementation checkpoint used:
- 1db2b333 chat 5 corrected
- 953e6c1 chat 6 formulas (catalog / anchor / registration)

Product decision implemented:
- source data / classifications / assumptions remain supplied
- formula-construction cells are the practice surface

Practice surface:
- total components: 27
- historical reformulation + DuPont: 21
- existing forecast/valuation: 6
- newly added component IDs:
  - effective_tax_rate_fy
  - net_interest_fy
  - net_interest_after_tax_fy
  - owca_agg
  - owcl_agg
  - olta_agg
  - oltl_agg
  - nola_agg
  - financial_assets_agg
  - financial_liabilities_agg
  - equity_reformulated_fy
  - after_tax_cod
  - flev
  - actual_roe

Files changed (this handoff completion):
- Modify: `core/tests/test_reference_integrity.py` — tax/interest anchor, historical formula integrity, full DuPont registration
- Modify: `core/tests/test_trainer.py` — 27-component catalog order, populated-input guardrail, expanded-chain Check states
- Modify: `README-HK-TRAINER.md`, `skills/bav-trainer/SKILL.md` — formula-construction framing
- Regenerate: `example/DEMO_HK_Trainer.xlsx`, `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

Tests run:
- `PYTHONPATH=. pytest core/tests/test_classification.py -q` -> 14 passed
- `PYTHONPATH=. pytest core/tests/test_line_identity.py -q` -> 17 passed
- `PYTHONPATH=. pytest core/tests/test_reference_integrity.py -q` -> 21 passed
- `PYTHONPATH=. pytest core/tests/test_line_resolver.py -q` -> 6 passed
- `PYTHONPATH=. pytest core/tests/test_trainer.py -v` -> 29 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 87 passed
- `PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx` -> exit 0; Components resolved: 27
- `PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx` -> `Checked 27 practice cells: 0 correct, 0 incorrect, 27 blank.`
- `PYTHONPATH=. python -m core --help` -> `{ingest,build,check,list}` only

Artifact audit:
- Trainer 27 blank/yellow/no Notes; no `_ComponentMap` / `_Ref*` / Trainer answer sidecars
- Answer Key 27 formula/yellow/Notes; embedded `_ComponentMap` retained for Check
- supplied source/classification/assumption cells preserved (guardrail regression)
- Check fresh count 0/0/27
- no Trainer answer leakage
- generated Answer-Key JSON sidecars / `rowmap.json` remain gitignored

Unresolved: none
