# BAV Excel Trainer — Hong Kong Edition

An extension of the BAVGems pipeline that turns manually supplied Hong Kong company filings into **interactive Excel training workbooks**. The full BAV accounting, DuPont, forecasting, residual-income, DCF, and scenario logic is preserved — but US/SEC EDGAR dependency is replaced with a **manual document-input adapter** behind a standardized data interface.

## Quick start

```bash
cd bav_trainer
pip install -r requirements-trainer.txt

# Build demo training workbook from illustrative HK data
python -m core build example/DEMO_HK_Standardized.json \
  -o example/DEMO_HK_Trainer.xlsx

# List practice components in dependency order
python -m core list

# After entering a formula in Excel and saving:
python -m core check --workbook example/DEMO_HK_Trainer.xlsx --component nopat_fy
python -m core hint  --workbook example/DEMO_HK_Trainer.xlsx --component nopat_fy
python -m core reveal --workbook example/DEMO_HK_Trainer.xlsx --component nopat_fy
```

## What it does

1. **Ingests** HK annual reports, interim reports, results materials, or Excel/Bloomberg/Wind exports via `HKManualDocumentAdapter`
2. **Reconciles** into standardized Income Statement / Balance Sheet / Cash Flow structure (`StandardizedFinancials`)
3. **Builds** a complete reference BAV model (`*_reference.xlsx`) — hidden from the learner
4. **Generates** a clean training workbook with source data, layout, labels, and formatting pre-done
5. **Strips** substantive formulas from practice cells so the user reconstructs the model part-by-part
6. **Provides** Check (output validation), Hint (progressive accounting guidance), and Reveal Answer (insert reference formula)

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
│  ReferenceModelBuilder — full BAV workbook (hidden)          │
│  IS/BS/CF → Condensed → DuPont → Model → Scenario Summary   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TrainingWorkbookGenerator                                   │
│  Practice cells + _RefFormulas + _TrainerMeta + Trainer tab  │
│  Check / Hint / Reveal via CLI + TrainerMacros.bas           │
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

JSON schema matches `example/DEMO_HK_Standardized.json`. Sign conventions: revenue positive, expenses negative.

Use Claude with `/bav-trainer` to assist PDF transcription while you gate classifications and forecasts.

## Excel macros

Import `core/templates/TrainerMacros.bas` via Developer → Visual Basic → Import File. Assign buttons on the Trainer tab to `CheckActive`, `HintActive`, `RevealActive`.

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
