# BAV Excel Trainer — Hong Kong Edition

Progressive training that takes an **accounting novice** toward junior accounting-based equity-research competence, with particular strength in Business Analysis and Valuation (BAV).

**Current capability** is a **historical-v1 model-construction foundation** (release-gated by Step 9H.1) for non-financial operating companies: multi-period reformulation / DuPont, classification judgment, earnings normalization, cash-conversion / accrual diagnostics and trends, working-capital diagnostics, RNOA margin/turnover and change attribution, ROE operating/financing attribution, optional diluted per-share analysis, and an optional normalized diluted-EPS bridge — plus a synthetic cross-company robustness matrix. Forecasting, valuation, investment conclusions, and empirical real-company validation remain deferred.

## Product loop (historical v1)

```text
end-state goal:
accounting novice -> junior accounting-based equity-research competence

Historical v1 foundation: release-gated by Step 9H.1
Forecasting: deferred
Valuation: deferred
Investment conclusion: deferred
Real-company empirical validation: not established by the synthetic matrix

Active historical surface:
- historical reformulation + DuPont
- classification judgment (Accounting Judgment column F)
- earnings normalization (when candidates are supplied)
- cash-conversion / accrual diagnostics and trends
- working-capital diagnostics (when OWCA/OWCL present)
- RNOA margin/turnover and change attribution
- ROE operating/financing attribution
- optional diluted per-share analysis (when diluted WAS shares supplied)
- optional normalized diluted-EPS bridge (shares + normalization)
- synthetic cross-company robustness matrix (services / retail / manufacturer)

Regression surfaces:
- with DEMO_HK_Assumptions.json: 66 families / 279 practice cells
- without assumptions:           62 families / 259 practice cells
- share-enabled:                 70 / 293 base; 78 / 331 with normalization
- synthetic matrix:              services 59/248; retail 78/331; manufacturer 70/293

The illustrative demo has no historical share input, so Per Share Analysis is absent in both demo builds.

still deferred:
- ROU / deferred-tax alternative modeling
- company-specific causal / investment diagnosis
- forecasting
- valuation
- investment conclusion
- empirical real-company validation

normal build:
does not execute forecast/scenario engine

Trainer = blank yellow formula cells + blank yellow judgment-response cells; no answers/hints.
Check = scans formula practice cells against current Accounting Judgment and Normalization Judgment treatments; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = formula + Note on formula cells; model treatment/rationale/consequence on judgment responses; hidden Check context for dynamic expecteds.
```

Open the matching Answer Key for formula Notes and for judgment reference responses. Formula Check does not grade Accounting Judgment or Normalization Judgment rationale/consequence cells.

## Quick start

```bash
cd bav_trainer
pip install -r requirements-trainer.txt

# Build matched Trainer + Answer Key pair from illustrative HK data
# (with optional Step 8B2 normalization assumptions)
python -m core build example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx
# → example/DEMO_HK_Trainer.xlsx
# → example/DEMO_HK_Answer_Key.xlsx
# with DEMO_HK_Assumptions.json: 66 families / 279 practice cells
# without assumptions:           62 families / 259 practice cells
# (illustrative demo has no share history → no Per Share Analysis)

# List conceptual schedule families
python -m core list --workbook example/DEMO_HK_Trainer.xlsx

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
