---
name: bav-trainer
description: Build matched BAV Excel Trainer / Answer Key workbooks for Hong Kong-listed companies from manually supplied annual reports, interim reports, results materials, or Excel/Bloomberg/Wind exports. Uses shared Stage-2/3 accounting integrity and optional Check / Hint / Reveal support.
---

# BAV Excel Trainer — Hong Kong Edition

Build a **matched Trainer / Answer Key pair** where the analyst reconstructs a BAV model (classification, DuPont, forecasting, residual-income valuation) in natural dependency order — while the system handles data extraction, reconciliation, layout, formatting, and answer generation.

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
        ↓  TrainingWorkbookGenerator
*_Trainer.xlsx (blank yellow practice cells) + optional Check / Hint / Reveal
```

HK ingestion and trainer generation stay in `core/`. Domain rubrics for statement checksums, balance-sheet classification, and DuPont definitions come from BAVGEM Stage 2 / 3 / 4 references — selectively integrated as pure Python in `core/model/`, not by running the full BAVGEM coverage pipeline.

Real-company standardized rows use **concept-aware line identity** when `LineItem.concept` is present: same displayed labels with different concepts stay distinct through merge, classification, and source row maps. Duplicate label-only rows without concepts are rejected rather than silently merged; disambiguate them with concepts (or Excel `Concept | Line Item | dates` columns). Classification overrides accept `concept:<id>` / `label:<text>` selectors (bare unique labels remain backwards compatible).

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
- `DEMO_HK_Trainer.xlsx` — practice workbook: source/layout filled; practice cells blank `#FFFF00` with **no** Notes and no adjacent hint cells as the normal UX
- `DEMO_HK_Answer_Key.xlsx` — complete model with formulas; yellow practice/input cells carry legacy Excel Notes (`BAV Trainer`)
- `DEMO_HK_Trainer.trainer.json` — component metadata sidecar

There is **no** user-facing `*_reference.xlsx`. Build refuses inputs with failed evaluatable source checksums or failed balance-sheet reformulation integrity.

### 3. Practice loop

**Primary feedback:** compare the Trainer against the static Answer Key.

**Optional CLI / macros** (dependency-ordered components via `python -m core list`):

1. NOPAT reformulation
2. NOWC / NOA / Net Debt aggregates
3. DuPont decomposition
4. Forecast vectors
5. Abnormal earnings / terminal value / IVPS
6. Scenario weighting

```bash
python -m core check --workbook training/DEMO_HK_Trainer.xlsx --component nopat_fy
python -m core hint  --workbook training/DEMO_HK_Trainer.xlsx --component nopat_fy
python -m core reveal --workbook training/DEMO_HK_Trainer.xlsx --component nopat_fy
```

Import `core/templates/TrainerMacros.bas` into Excel for button macros (Reveal works in-VBA; Check/Hint delegate to CLI or show local value).

## Design principles

| Automated | User practices |
|---|---|
| Document ingestion & reconciliation | Balance-sheet classification judgment |
| Workbook structure & formatting | Excel formula construction |
| Answer Key & semantic map | Forecasting & scenario judgment |
| Optional Check / Hint / Reveal | Valuation mechanics & calibration |

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
