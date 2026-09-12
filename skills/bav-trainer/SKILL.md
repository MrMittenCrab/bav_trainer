---
name: bav-trainer
description: Build matched BAV Excel Trainer / Answer Key workbooks for Hong Kong-listed non-financial companies from manually supplied filings or Excel/Bloomberg/Wind exports. Step 7 historical schedules, Step 8A/8B1 classification, Step 8B2 earnings normalization, and Step 9A historical earnings-quality diagnostics with judgment-aware Formula Check.
---

# BAV Excel Trainer — Hong Kong Edition

Build a **matched Trainer / Answer Key pair** where the learner reconstructs multi-period historical BAV schedules, compares selected ambiguous classifications, practices explicit recurring/non-recurring earnings normalization, and computes mechanical cash-conversion / accrual diagnostics.

## Product loop

```text
end-state goal:
accounting novice -> junior accounting-based equity-research competence

Step 7 — historical model construction
- 25 historical formula families / 118 cells in the five-year illustrative demo
- workbook-wide Formula Check

Step 8A — guided classification reasoning
- supported supplied ambiguities become compare-and-defend exercises
- rationale/consequence are ungraded

Step 8B1 — live supported classification
- Accounting Judgment column F is the only learner treatment input
- blank F uses the supplied reference treatment
- generated Condensed Financials links are system-controlled and validated by Check
- Formula Check recomputes expected historical values for the selected supported treatment
- rationale/consequence remain ungraded

Step 8B2 — guided earnings normalization
- normalization candidates are explicitly supplied; they are not inferred from labels
- learner chooses Recurring vs Non-recurring
- reported statements and reported historical model remain unchanged
- Earnings Normalization bridges reported to normalized NOPAT / Net Income
- Step 8B2 supports operating pretax items using period effective tax rate as the supplied training convention
- Check conditions normalization formulas on the current treatment
- rationale/consequence are ungraded

Step 9A — historical earnings-quality diagnostics
- operating cash-flow link
- cash conversion ratio
- total accruals
- average total assets where supplied
- accrual ratio where supplied
- these are mechanical diagnostics and do not yet explain why conversion changed or grade an investment conclusion

ROU/deferred-tax alternatives, forecasting, and valuation remain deferred.

This is a transition from supplied judgment to guided judgment, not independent analyst competence.

still deferred:
- ROU / deferred-tax alternative modeling
- working-capital / driver interpretation of conversion changes
- forecasting
- valuation
- investment conclusion

normal build:
does not execute forecast/scenario engine

Trainer = blank yellow formula cells + blank yellow judgment-response cells; no answers/hints.
Check = scans formula practice cells against current Accounting Judgment and Normalization Judgment treatments; blank yellow, correct green, incorrect red; no answers disclosed.
Answer Key = formula + Note on formula cells; model treatment/rationale/consequence on judgment responses; hidden Check context for dynamic expecteds.
```

## When to use

- User asks to **train on BAV historical modelling** for an HK-listed non-financial company
- User uploads **annual reports, interim reports, results announcements**, or **Excel/Bloomberg/Wind exports**
- User wants a **workbook with source data and classifications pre-filled** but multi-period schedule formulas left for practice

## Architecture

```
Manual HK documents / Excel exports
        ↓  HKManualDocumentAdapter (StandardizedFinancials)
        ↓  reconcile + reformulation integrity (blocking)
ReferenceModelBuilder → multi-period historical Answer Key
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
  -a example/DEMO_HK_Assumptions.json \
  -o training/DEMO_HK_Trainer.xlsx
```

Outputs:
- `DEMO_HK_Trainer.xlsx` — source/classifications filled; yellow schedule cells blank
- `DEMO_HK_Answer_Key.xlsx` — working formulas + legacy Notes on the same cells
- With demo assumptions: 40 families / 188 cells (includes Earnings Normalization + Earnings Quality)
- Without `-a`: 36 families / 168 cells (includes Earnings Quality; no normalization sheets)

There is **no** user-facing `*_reference.xlsx` and no Trainer `.trainer.json`.

### 3. Practice loop

1. Complete each historical schedule left-to-right (`python -m core list --workbook ...` shows schedule families).
2. Run one workbook-wide Check:

```bash
python -m core check --workbook training/DEMO_HK_Trainer.xlsx
```

3. Open the Answer Key for the formula and Note hint.

Active historical schedules: Revenue/NI links → tax/interest/NOPAT → OWCA/OWCL/NOWC → OLTA/OLTL/NOLA → NOA → FA/FL/Net Debt → Equity → Sales Growth / NOPAT Margin → RNOA / After-tax CoD / Spread / FLEV / ROE → (optional) Earnings Normalization → Earnings Quality (CFO / cash conversion / accruals) → Working Capital Analysis (when OWCA/OWCL present).

## Design principles

| Automated | User practices |
|---|---|
| Document ingestion & reconciliation | Excel formula construction |
| Classifications & workbook setup | Reformulation / DuPont schedule logic |
| Answer Key & semantic map | Cross-sheet / cross-period dependency reasoning |
| Workbook-wide Check (colors only) | Auditing historical model results |

## References

- `core/data/interface.py` — standardized data contract
- `core/model/classification.py` — Stage-3 classification / reformulation
- `core/engine/component_catalog.py` — 25 conceptual families; period expansion at build time
- `core/engine/semantic_map.py` — runtime coordinates resolved at build time
- `TARGET.md` — product competency progression (future steps deferred)
