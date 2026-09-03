# BAV Excel Trainer — Hong Kong Edition

An extension of the BAVGems pipeline that turns manually supplied Hong Kong company filings into **interactive Excel training workbooks**. The full BAV accounting, DuPont, forecasting, residual-income, DCF, and scenario logic is preserved — but US/SEC EDGAR dependency is replaced with a **manual document-input adapter** behind a standardized data interface.

## Product loop

```text
Trainer = blank yellow practice cells, no answers, no hints.
Check = scans every practice cell; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = same practice cells with formula/input + one legacy Note hint.
```

## Quick start

```bash
cd bav_trainer
pip install -r requirements-trainer.txt

# Build matched Trainer + Answer Key pair from illustrative HK data
python -m core build example/DEMO_HK_Standardized.json \
  -o example/DEMO_HK_Trainer.xlsx
# → example/DEMO_HK_Trainer.xlsx
# → example/DEMO_HK_Answer_Key.xlsx

# List practice components in dependency order
python -m core list

# After entering formulas in Excel and saving, validate the whole workbook:
python -m core check --workbook example/DEMO_HK_Trainer.xlsx
```

Open the matching Answer Key for the formula/input and hover the yellow cell's Note for the hint.

## What it does

1. **Ingests** HK annual reports, interim reports, results materials, or Excel/Bloomberg/Wind exports via `HKManualDocumentAdapter`
2. **Reconciles** into standardized Income Statement / Balance Sheet / Cash Flow structure (`StandardizedFinancials`)
3. **Builds** a complete BAV model and writes it as the **Answer Key** (`*_Answer_Key.xlsx`) — yellow practice cells with working formulas and concise Excel Notes
4. **Derives** the matching **Trainer** workbook (`*_Trainer.xlsx`) — same layout, blank yellow practice cells, no answers, Notes, or answer-bearing metadata
5. **Checks** the entire Trainer in one pass: blank stays yellow, correct turns green, incorrect turns red — without disclosing answers

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Ingestion adapters (pluggable)                              │
│  ├── HKManualDocumentAdapter  (v1 — manual documents)       │
│  ├── ExcelExportAdapter       (Bloomberg / Wind / Excel)    │
│  └── [future] HKEXAdapter, SECAdapter, SGXAdapter           │
└──────────────────────────┬──────────────────────────────────┘
                           │ StandardizedFinancials
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  ReferenceModelBuilder — full BAV workbook                   │
│  IS/BS/CF → Condensed → DuPont → Model → Scenario Summary   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TrainingWorkbookGenerator                                   │
│  Answer Key (formulas + Notes) + sanitized Trainer           │
│  Workbook-wide Check via CLI (colors only; no answer dump)   │
└─────────────────────────────────────────────────────────────┘
```

The BAV engine layer (`skills/bav-pipeline/references/lib/`, stage rubrics) is unchanged. Only the ingestion front-end differs from the US SEC pipeline.

## Preparing real HK company data

v1 does **not** scrape HKEX automatically. Supply documents manually:

| Input | How to use |
|---|---|
| Annual report PDF | Transcribe IS/BS/CF into JSON or Excel; cite page numbers |
| Interim report PDF | Same; mark `is_interim: true` on periods |
| Results announcement | Supplement quarterly/interim figures |
| Excel export | Tabs: Income Statement, Balance Sheet, Cash Flow |
| Bloomberg / Wind | Export to Excel; pass file to `ingest` |

JSON schema matches `example/DEMO_HK_Standardized.json`. Sign conventions: revenue positive, expenses negative. When exporting via `python -m core ingest ... -o ...`, each statement row includes `concept` (empty string when absent) so concept-aware identity survives reload.

Use Claude with `/bav-trainer` to assist PDF transcription while you gate classifications and forecasts.

## Relationship to BAV Pipeline

| BAV Pipeline (US) | BAV Trainer (HK) |
|---|---|
| SEC EDGAR via edgartools | Manual document adapter |
| Persistent coverage vault | Per-session training workbook |
| Sentinel daily updates | Manual rebuild |
| Analyst edits register to assumptions.json | User practices formulas in Excel |
| Full 13-tab professional model | Same model structure, training mode |

Both share the same analytical DNA: reformulated statements, DuPont, calibrated residual income.

## Claude Code skill

Link the trainer skill alongside the pipeline skills:

```bash
ln -sfn /path/to/BAVGems/skills/bav-trainer .claude/skills/bav-trainer
```

Then: `/bav-trainer` to build a training workbook interactively.
