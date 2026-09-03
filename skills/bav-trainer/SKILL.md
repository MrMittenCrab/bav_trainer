---
name: bav-trainer
description: Build matched BAV Excel Trainer / Answer Key workbooks for Hong Kong-listed companies from manually supplied annual reports, interim reports, results materials, or Excel/Bloomberg/Wind exports. Uses shared Stage-2/3 accounting integrity and workbook-wide Check with Answer Key Notes as the only hint/answer surface.
---

# BAV Excel Trainer — Hong Kong Edition

Build a **matched Trainer / Answer Key pair** where the analyst reconstructs a BAV model (classification, DuPont, forecasting, residual-income valuation) in natural dependency order — while the system handles data extraction, reconciliation, layout, formatting, and answer generation.

## Product loop

```text
Trainer = blank yellow practice cells, no answers, no hints.
Check = scans every practice cell; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = same practice cells with formula/input + one legacy Note hint.
```

## When to use

- User asks to **train on BAV modeling** for an HK-listed company
- User uploads **annual reports, interim reports, results announcements**, or **Excel/Bloomberg/Wind exports**
- User wants a **workbook with source data pre-filled** but formulas left for practice

## Architecture

```
Manual HK documents / Excel exports
        ↓  HKManualDocumentAdapter (StandardizedFinancials)
        ↓  reconcile + reformulation integrity (blocking)
ReferenceModelBuilder → *_Answer_Key.xlsx
        ↓  TrainingWorkbookGenerator (sanitize Trainer)
*_Trainer.xlsx (blank yellow; no answer metadata)
        ↓  python -m core check --workbook ...
Workbook-wide yellow / green / red validation (no answers disclosed)
```

HK ingestion and trainer generation stay in `core/`. Domain rubrics for statement checksums, balance-sheet classification, and DuPont definitions come from BAVGEM Stage 2 / 3 / 4 references — selectively integrated as pure Python in `core/model/`, not by running the full BAVGEM coverage pipeline.

Real-company standardized rows use **concept-aware line identity** when `LineItem.concept` is present: same displayed labels with different concepts stay distinct through merge, classification, and source row maps. Duplicate label-only rows without concepts are rejected rather than silently merged; disambiguate them with concepts (or Excel `Concept | Line Item | dates` columns). Classification overrides accept `concept:<id>` / `label:<text>` selectors (bare unique labels remain backwards compatible). Standardized JSON export preserves `concept` on every statement row.

The ingestion layer implements `DataSourceAdapter`. v1 accepts manual documents only; future HKEX/SEC/SGX adapters plug in without changing the BAV engine or trainer.

## Workflow

### 1. Ingest source documents

Accept any of:
- **Structured JSON** — transcribed IS/BS/CF (see `example/DEMO_HK_Standardized.json`)
- **Excel workbook** — tabs named Income Statement / Balance Sheet / Cash Flow
- **Document manifest** — list PDFs for assisted extraction (PDF parsing not automated in v1)

```bash
pip install -r requirements-trainer.txt
python -m core ingest example/DEMO_HK_Standardized.json -o /tmp/demo_std.json
```

For real HK companies: read annual/interim PDFs, transcribe line items into JSON (or Excel), citing page numbers in provenance. Use the Assembler rubric from `skills/bav-pipeline/references/stage2_assembler.md` for sign conventions and checksum rules — but replace SEC sourcing with document citations.

### 2. Build Trainer + Answer Key

```bash
python -m core build example/DEMO_HK_Standardized.json \
  -o training/DEMO_HK_Trainer.xlsx
```

Outputs (matched pair from one semantic model):
- `DEMO_HK_Trainer.xlsx` — practice workbook: source/layout filled; practice cells blank `#FFFF00` with **no** Notes, no adjacent hint cells, and no answer-bearing hidden sheets or sidecars
- `DEMO_HK_Answer_Key.xlsx` — complete model with formulas; yellow practice/input cells carry legacy Excel Notes (`BAV Trainer`); semantic map lives here

There is **no** user-facing `*_reference.xlsx` and no Trainer `.trainer.json`. Build refuses inputs with failed evaluatable source checksums or failed balance-sheet reformulation integrity.

### 3. Practice loop

1. Complete any number of blank yellow practice cells in the Trainer.
2. Run **one** workbook-wide Check when ready:

```bash
python -m core check --workbook training/DEMO_HK_Trainer.xlsx
```

Check recolors every practice cell from current contents: blank → yellow, correct → green, incorrect → red. It does not change cell values and does not disclose formulas, expected values, or hints.

3. When you want the answer or a hint, open the matching Answer Key: inspect the yellow cell's formula/input and hover its Note.

Practice components (dependency order via `python -m core list`):

1. NOPAT reformulation
2. NOWC / NOA / Net Debt aggregates
3. DuPont decomposition
4. Forecast vectors
5. Abnormal earnings / terminal value / IVPS
6. Scenario weighting

## Design principles

| Automated | User practices |
|---|---|
| Document ingestion & reconciliation | Balance-sheet classification judgment |
| Workbook structure & formatting | Excel formula construction |
| Answer Key & semantic map | Forecasting & scenario judgment |
| Workbook-wide Check (colors only) | Valuation mechanics & calibration |

## Selective BAVGEM integration

| Reuse as domain contract | Do not run merely to build a trainer |
|---|---|
| `stage2_assembler.md` — checksums / signs | SEC/edgartools sourcing, coverage vault |
| `stage3_analyst.md` — 8-category BS / DuPont | Quarterly sections, Core Earnings Bridge, EQ screens |
| `stage4_modeler.md` — later valuation layer | Price Rationalization, ICC, sensitivity, DCF feature chain |

## Extending ingestion (future adapters)

Implement `DataSourceAdapter` in `core/ingestion/`:

```python
class HKEXAdapter(DataSourceAdapter):
    jurisdiction = "HK"
    def ingest(self, manifest): ...
    def reconcile(self, data): ...
```

Register in CLI; BAV engine and trainer layers unchanged.

## References

- `core/data/interface.py` — standardized data contract
- `core/model/classification.py` — Stage-3 classification / reformulation
- `core/engine/component_catalog.py` — static trainer exercise definitions (semantic only)
- `core/engine/semantic_map.py` — runtime coordinates resolved at build time
- `skills/bav-pipeline/references/stage2_assembler.md` — source integrity rubric
- `skills/bav-pipeline/references/stage3_analyst.md` — condensed/DuPont rubric
- `skills/bav-pipeline/references/stage4_modeler.md` — residual income model rubric
- `skills/bav-pipeline/references/xlsx_patterns.md` — formatting conventions
