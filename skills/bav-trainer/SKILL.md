---
name: bav-trainer
description: Build matched BAV Excel Trainer / Answer Key workbooks for Hong Kong-listed non-financial companies from manually supplied filings or Excel/Bloomberg/Wind exports. Historical-v1 model-construction foundation (release-gated by Step 9H.1): reformulation/DuPont, classification and normalization judgment, earnings-quality and working-capital diagnostics, profitability/ROE attribution, optional per-share and normalized-EPS bridge, plus a synthetic cross-company robustness matrix. Forecasting and valuation remain deferred.
---

# BAV Excel Trainer — Hong Kong Edition

Build a **matched Trainer / Answer Key pair** where the learner reconstructs multi-period historical BAV schedules, practices classification and earnings-normalization judgment, and computes mechanical research diagnostics through the historical-v1 surface.

## Product loop

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
- classification judgment
- earnings normalization
- cash-conversion / accrual diagnostics and trends
- working-capital diagnostics
- RNOA margin/turnover and change attribution
- ROE operating/financing attribution
- optional diluted per-share analysis
- optional normalized diluted-EPS bridge
- synthetic cross-company robustness matrix

Regression surfaces:
- ordinary demo: 62/259 base, 66/279 with normalization
- share-enabled: 70/293 base, 78/331 with normalization
- cross-company synthetic matrix: services 59/248, retail 78/331, manufacturer 70/293

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

Step 9H.1 — historical v1 exit gate
- active family namespace frozen at orders 1..78
- normal builds never execute dormant forecast/valuation engines
- Trainer/Answer-Key practice contract and non-disclosing Check release-gated
- canonical demo workbooks regenerated from current builder (66/279)
- historical-v1 model-construction foundation complete/release-gated; forecasting and valuation remain deferred

Still deferred: company-specific causal diagnosis, basic-vs-diluted attribution, forecasting, valuation, investment conclusions, ROU/deferred-tax alternative modeling, empirical real-company validation.

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
- `core/engine/component_catalog.py` — conceptual families; period expansion at build time
- `core/engine/semantic_map.py` — runtime coordinates resolved at build time
- `TARGET.md` — product competency progression (future steps deferred)
