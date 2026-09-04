# BAV Excel Trainer — Hong Kong Edition

Progressive training that takes an **accounting novice** toward junior accounting-based equity-research competence, with particular strength in Business Analysis and Valuation (BAV).

**Current Step 7 capability** is a **multi-period historical model-construction foundation** for non-financial operating companies. Accounting-judgment quizzes, research diagnostics, forecasting, valuation, and research conclusions remain deferred curriculum stages.

## Product loop (v1 / Step 7)

```text
end-state goal:
accounting novice -> junior accounting-based equity-research competence

current Step 7 capability:
- historical schedules across all supplied fiscal years
- cross-sheet Revenue / Net Income links
- reformulation across periods
- Sales Growth / NOPAT Margin
- multi-period DuPont from the second comparable year onward
- workbook-wide Check across every concrete period cell

learner view:
- 25 conceptual schedule families
- period-specific yellow cells inside each schedule
  (five-year demo → 118 concrete practice cells = 25*n − 7)

still deferred:
- classification/normalization judgment exercises
- earnings-quality diagnostics
- forecasting
- valuation
- investment conclusion

normal build:
does not execute forecast/scenario engine

Trainer = blank yellow practice cells, no answers, no hints.
Check = scans every practice cell; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = same practice cells with formula + one legacy Note hint.
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
# Components resolved: 118

# List the 25 conceptual historical schedule families
python -m core list

# After entering formulas in Excel and saving, validate the whole workbook:
python -m core check --workbook example/DEMO_HK_Trainer.xlsx
```

Open the matching Answer Key for the formula and hover the yellow cell's Note for the hint.

## What it does

1. **Ingests** HK annual reports, interim reports, results materials, or Excel/Bloomberg/Wind exports via `HKManualDocumentAdapter`
2. **Reconciles** into standardized Income Statement / Balance Sheet / Cash Flow structure (`StandardizedFinancials`)
3. **Builds** a complete multi-period historical BAV reformulation / DuPont model as the **Answer Key** (`*_Answer_Key.xlsx`)
4. **Derives** the matching **Trainer** — source data and classifications stay populated; yellow cells are blank historical schedule formulas only
5. **Checks** the entire Trainer in one pass: blank stays yellow, correct turns green, incorrect turns red — without disclosing answers

Banks, insurers, brokers, and other financial institutions are outside the initial competency scope.

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
│  ReferenceModelBuilder — multi-period historical BAV         │
│  IS/BS/CF → Condensed reformulation → ALT DuPont schedules   │
│  (forecast/valuation tabs are hidden deferred placeholders)  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TrainingWorkbookGenerator                                   │
│  Answer Key (formulas + Notes) + sanitized Trainer           │
│  Family-level Trainer index; cell-level Check                │
└─────────────────────────────────────────────────────────────┘
```

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

Optional historical configuration (e.g. `classificationOverrides`) can be passed with `-a/--assumptions`.

Use Claude with `/bav-trainer` to assist PDF transcription while you gate classifications.

## Relationship to BAV Pipeline

| BAV Pipeline (US) | BAV Trainer (HK) Step 7 |
|---|---|
| SEC EDGAR via edgartools | Manual document adapter |
| Persistent coverage vault | Per-session training workbook |
| Sentinel daily updates | Manual rebuild |
| Full forecast + valuation model | Multi-period historical foundation |

Both share the same analytical DNA for reformulated statements and DuPont; forecast and valuation layers return in later curriculum steps.

## Claude Code skill

Link the trainer skill alongside the pipeline skills:

```bash
ln -sfn /path/to/BAVGems/skills/bav-trainer .claude/skills/bav-trainer
```

Then: `/bav-trainer` to build a training workbook interactively.
