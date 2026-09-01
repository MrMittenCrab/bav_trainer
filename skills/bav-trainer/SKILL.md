---
name: bav-trainer
description: Build BAV Excel training workbooks for Hong Kong-listed companies from manually supplied annual reports, interim reports, results materials, or Excel/Bloomberg/Wind exports. Generates a complete hidden reference model and a practice workbook with Check, Hint, and Reveal Answer support.
---

# BAV Excel Trainer — Hong Kong Edition

Build a **practice workbook** where the analyst reconstructs a full BAV model (classification, DuPont, forecasting, residual-income valuation, DCF cross-check, scenario weighting) in natural dependency order — while the system handles data extraction, reconciliation, layout, formatting, and answer generation.

## When to use

- User asks to **train on BAV modeling** for an HK-listed company
- User uploads **annual reports, interim reports, results announcements**, or **Excel/Bloomberg/Wind exports**
- User wants a **workbook with source data pre-filled** but formulas left for practice

## Architecture

```
Manual HK documents / Excel exports
        ↓  HKManualDocumentAdapter (StandardizedFinancials)
Reference model builder (hidden _reference.xlsx)
        ↓  TrainingWorkbookGenerator
Practice workbook + Check / Hint / Reveal
```

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

### 2. Build reference + training workbooks

```bash
python -m core build example/DEMO_HK_Standardized.json \
  -o training/DEMO_HK_Trainer.xlsx
```

Outputs:
- `DEMO_HK_Trainer_reference.xlsx` — complete professional model (hidden from learner)
- `DEMO_HK_Trainer.xlsx` — practice workbook with layout, labels, source data, formatting done; substantive formulas stripped from practice cells
- `DEMO_HK_Trainer.trainer.json` — component metadata sidecar

### 3. Practice loop

Components are ordered by dependency (see `python -m core list`):

1. NOPAT reformulation
2. NOWC / NOA / Net Debt aggregates
3. DuPont decomposition
4. Forecast vectors
5. Abnormal earnings / terminal value / IVPS
6. Scenario weighting

For each component the user:
1. Reads the short hint in the adjacent cell
2. Enters a formula in the highlighted practice cell
3. Runs **Check** — validates by output value, not exact formula text
4. Runs **Hint** — progressively exposes accounting relationships and related cells
5. Runs **Reveal Answer** — inserts the reference formula for inspection

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
| Reference model & answer generation | Forecasting & scenario judgment |
| Check / Hint / Reveal infrastructure | Valuation mechanics & calibration |

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
- `core/engine/component_catalog.py` — static trainer exercise definitions (semantic only)
- `core/engine/semantic_map.py` — runtime coordinates resolved at build time
- `skills/bav-pipeline/references/stage3_analyst.md` — condensed/DuPont rubric
- `skills/bav-pipeline/references/stage4_modeler.md` — residual income model rubric
- `skills/bav-pipeline/references/xlsx_patterns.md` — formatting conventions
