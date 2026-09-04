---
name: bav-trainer
description: Build matched BAV Excel Trainer / Answer Key workbooks for Hong Kong-listed non-financial companies from manually supplied filings or Excel/Bloomberg/Wind exports. Step 7 multi-period historical schedules plus Step 8A guided classification judgment; Answer Key Notes/rationale are the hint/answer surface.
---

# BAV Excel Trainer — Hong Kong Edition

Build a **matched Trainer / Answer Key pair** where the learner reconstructs multi-period historical BAV schedules and compares selected ambiguous classifications with defensible alternatives.

## Product loop

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
  -o training/DEMO_HK_Trainer.xlsx
```

Outputs:
- `DEMO_HK_Trainer.xlsx` — source/classifications filled; yellow schedule cells blank
- `DEMO_HK_Answer_Key.xlsx` — working formulas + legacy Notes on the same cells

There is **no** user-facing `*_reference.xlsx` and no Trainer `.trainer.json`.

### 3. Practice loop

1. Complete each historical schedule left-to-right (`python -m core list` shows 25 families).
2. Run one workbook-wide Check:

```bash
python -m core check --workbook training/DEMO_HK_Trainer.xlsx
```

3. Open the Answer Key for the formula and Note hint.

Active historical schedules: Revenue/NI links → tax/interest/NOPAT → OWCA/OWCL/NOWC → OLTA/OLTL/NOLA → NOA → FA/FL/Net Debt → Equity → Sales Growth / NOPAT Margin → RNOA / After-tax CoD / Spread / FLEV / ROE.

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
