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
- With demo assumptions: 66 families / 279 cells (includes Earnings Normalization + Earnings Quality)
- Without `-a`: 62 families / 259 cells (includes Earnings Quality; no normalization sheets)

There is **no** user-facing `*_reference.xlsx` and no Trainer `.trainer.json`.

### 3. Practice loop

1. Complete each historical schedule left-to-right (`python -m core list --workbook ...` shows schedule families).
2. Run one workbook-wide Check:

```bash
python -m core check --workbook training/DEMO_HK_Trainer.xlsx
```

3. Open the Answer Key for the formula and Note hint.

Active historical schedules: Revenue/NI links → tax/interest/NOPAT → OWCA/OWCL/NOWC → OLTA/OLTL/NOLA → NOA → FA/FL/Net Debt → Equity → Sales Growth / NOPAT Margin → RNOA / After-tax CoD / Spread / FLEV / ROE → (optional) Earnings Normalization → Earnings Quality levels and cash-conversion/accrual trends → Working Capital Analysis (when OWCA/OWCL present) → RNOA margin/turnover drivers and change attribution → ROE financing contribution and operating/financing change attribution → (optional) Per Share Analysis when diluted weighted-average share history is supplied, including diluted-EPS earnings vs share-count attribution and (when normalization is also active) the normalized diluted-EPS bridge. These are arithmetic diagnostics, not automatic quality, leverage, dilution, or financing-policy judgments.

Step 9F.1 — historical diluted per-share foundation
- gated on explicitly supplied diluted weighted-average share history
- share counts remain populated trusted inputs
- Reported Diluted EPS and NOPAT per Diluted Share
- absolute changes in EPS and diluted weighted-average shares
- ordinary demo remains unchanged because it supplies no share history

Step 9F.2 — diluted EPS earnings / share-count attribution
- exact midpoint Earnings Effect + Share-Count Effect = Change in Diluted EPS
- rising share count is not forced to a negative “dilution” conclusion
- generated attribution check row is trusted (not practice)
- share-enabled surfaces: 70/293 base; with normalization before 9F.3 was 74/313

Step 9F.3 — normalized diluted EPS bridge
- gated on both explicit diluted weighted-average share history and active normalization cases
- Reported EPS remains reported
- Normalized EPS uses the current Normalization Judgment treatment
- Reported EPS + normalization adjustment/share reconciles to normalized EPS
- Reported EPS change + normalization effect reconciles to normalized EPS change
- No automatic claim is made that normalized EPS is economically superior or more predictive
- share+normalization surface: 78 families / 331 cells

Step 9G.1 — cross-company robustness
- historical engine regression-tested on three deterministic non-financial archetypes: asset-light services, inventory-heavy retail, and capital-intensive manufacturing
- these are synthetic robustness fixtures, not empirical company data or product examples
- surfaces: services 59/248; retail 78/331; manufacturer 70/293
- ordinary demo and share-enabled regressions preserved; no new families/sheets/CLI

Still deferred: company-specific causal diagnosis, basic-vs-diluted attribution, forecasting, valuation, investment conclusions, ROU/deferred-tax alternative modeling.

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
