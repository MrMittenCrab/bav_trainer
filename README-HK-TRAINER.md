# BAV Excel Trainer — Hong Kong Edition

Progressive training that takes an **accounting novice** toward junior accounting-based equity-research competence, with particular strength in Business Analysis and Valuation (BAV).

**Current capability** is a **multi-period historical model-construction foundation** plus **Step 8A guided classification judgment** for non-financial operating companies. Normalization, earnings-quality diagnostics, forecasting, valuation, and research conclusions remain deferred.

## Product loop (Step 7 + Step 8A)

```text
end-state goal:
accounting novice -> junior accounting-based equity-research competence

Step 7 historical model construction:
- 25 historical schedule families across supplied fiscal years
- 118 formula practice cells in the five-year demo
- workbook-wide formula Check

Step 8A guided judgment:
- company-specific classification cases only when the authoritative classifier flags a supported ambiguity
- supplied reference treatment + explicit defensible alternative(s)
- learner treatment choice + short rationale + consequence explanation
- Answer Key shows model reasoning
- judgment responses are not automatically graded yet
- learner choices do not yet drive the main reformulated model

This is a transition from supplied judgment to guided judgment, not independent analyst competence.

still deferred:
- live alternative classification driving the main model
- normalization / recurring vs non-recurring adjustments
- earnings-quality diagnostics
- forecasting
- valuation
- investment conclusion

normal build:
does not execute forecast/scenario engine

Trainer = blank yellow formula cells + blank yellow judgment-response cells; no answers/hints.
Check = scans formula practice cells only; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = formula + Note on formula cells; model treatment/rationale/consequence on judgment responses.
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
