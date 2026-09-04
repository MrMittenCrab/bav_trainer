---
name: bav-trainer
description: Build matched BAV Excel Trainer / Answer Key workbooks for Hong Kong-listed non-financial companies from manually supplied filings or Excel/Bloomberg/Wind exports. v1 is a historical reformulation + DuPont model-construction foundation with workbook-wide Check; Answer Key Notes are the only hint/answer surface.
---

# BAV Excel Trainer — Hong Kong Edition

Build a **matched Trainer / Answer Key pair** where the learner reconstructs historical BAV reformulation and DuPont formulas while the system supplies source data, classifications, layout, and answer generation.

## Product loop

```text
end-state goal:
accounting novice -> junior accounting-based equity-research competence

current v1:
historical model-construction foundation for non-financial operating companies

provided in v1:
historical source values + classification/setup judgments

active practice in v1:
historical links + reformulation + ratios + DuPont (21 components)

deferred:
accounting-judgment exercises + research diagnostics + forecasting + valuation + research conclusion

normal v1 build:
does not execute forecast/scenario engine

Trainer = blank yellow practice cells, no answers, no hints.
Check = scans every practice cell; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = same practice cells with formula + one legacy Note hint.
```

## When to use

- User asks to **train on BAV historical modelling** for an HK-listed non-financial company
- User uploads **annual reports, interim reports, results announcements**, or **Excel/Bloomberg/Wind exports**
- User wants a **workbook with source data and classifications pre-filled** but reformulation/DuPont formulas left for practice

## Architecture

```
Manual HK documents / Excel exports
        ↓  HKManualDocumentAdapter (StandardizedFinancials)
        ↓  reconcile + reformulation integrity (blocking)
ReferenceModelBuilder → historical Answer Key
        ↓  TrainingWorkbookGenerator (sanitize Trainer)
*_Trainer.xlsx (blank yellow historical formulas; no answer metadata)
        ↓  python -m core check --workbook ...
Workbook-wide yellow / green / red validation (no answers disclosed)
```

Forecast/valuation sheet names exist only as **hidden deferred placeholders**. They are not active practice and are not listed by Check/`list`.

## Workflow

### 1. Ingest source documents

```bash
pip install -r requirements-trainer.txt
python -m core ingest example/DEMO_HK_Standardized.json -o /tmp/demo_std.json
```

### 2. Build Trainer + Answer Key

```bash
python -m core build example/DEMO_HK_Standardized.json \
  -o training/DEMO_HK_Trainer.xlsx
```

Outputs:
- `DEMO_HK_Trainer.xlsx` — source/classifications filled; 21 practice cells blank yellow
- `DEMO_HK_Answer_Key.xlsx` — working formulas + legacy Notes on the same cells

There is **no** user-facing `*_reference.xlsx` and no Trainer `.trainer.json`.

### 3. Practice loop

1. Complete yellow historical formula cells in dependency order (`python -m core list`).
2. Run one workbook-wide Check:

```bash
python -m core check --workbook training/DEMO_HK_Trainer.xlsx
```

3. Open the Answer Key for the formula and Note hint.

Active historical chain: effective tax → net interest → NOPAT → OWCA/OWCL/NOWC → OLTA/OLTL/NOLA → NOA → FA/FL/Net Debt → Equity → RNOA / After-tax CoD / Spread / FLEV / ROE.

## Design principles

| Automated | User practices |
|---|---|
| Document ingestion & reconciliation | Excel formula construction |
| Classifications & workbook setup | Reformulation / DuPont logic |
| Answer Key & semantic map | Cross-sheet dependency reasoning |
| Workbook-wide Check (colors only) | Auditing historical model results |

## References

- `core/data/interface.py` — standardized data contract
- `core/model/classification.py` — Stage-3 classification / reformulation
- `core/engine/component_catalog.py` — 21 historical practice definitions (semantic only)
- `core/engine/semantic_map.py` — runtime coordinates resolved at build time
- `TARGET.md` — product competency progression (future steps deferred)
