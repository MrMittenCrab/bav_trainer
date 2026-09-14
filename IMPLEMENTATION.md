# Step 9M.2 — Lululemon Benchmark Baseline and Gap Map

> **For agentic workers:** Implement this bounded step only. Use the existing production pipeline and tests; do not begin Step 10 forecasting or Step 11 valuation.

**Base:** `fe17dd9` (`Add Lululemon historical benchmark inputs`)

**Goal:** Make Lululemon the primary real-company benchmark for Step 9 historical convergence by proving the current generic filing-JSON → reconciliation → historical Trainer/Answer-Key pipeline on FY2022–FY2025 source filings, then record the highest-value general BAV gaps exposed by that benchmark.

**Architecture:** Treat `benchmark/lululemon/` as benchmark evidence, not issuer-specific product logic. The production engine must remain generic: no ticker checks, no hard-coded LULU labels, and no company-specific workbook formulas. Fast Retailing remains a regression benchmark while Lululemon becomes the development driver for the next Step 9 work.

## Global constraints

- `TARGET.md` is authoritative and read-only.
- Preserve one extracted JSON per source filing and all source/page provenance.
- Do not invent missing historical facts or silently reconcile disagreements.
- Any code fix required by LULU must be general and covered by a non-LULU or generic regression where practical.
- Do not implement forecasting, valuation, scenarios, M&A mechanics, or investment conclusions.
- Do not optimize specifically for LULU workbook coordinates or labels.
- Keep Fast Retailing and the synthetic suite passing.

### Task 1: Validate the four LULU filing inputs

**Inputs:**
- `benchmark/lululemon/source/LULU_FY2022_Annual_Report.pdf`
- `benchmark/lululemon/source/LULU_FY2023_Annual_Report.pdf`
- `benchmark/lululemon/source/LULU_FY2024_Annual_Report.pdf`
- `benchmark/lululemon/source/LULU_FY2025_Annual_Report.pdf`
- matching JSON files under `benchmark/lululemon/extracted/`

Run:

`PYTHONPATH=. python -m core validate-source benchmark/lululemon/extracted --source-root benchmark/lululemon/source`

Require all four filings to pass source binding. If validation fails, distinguish an extracted-input defect from a generic validator defect; never weaken validation merely to accept LULU.

### Task 2: Reconcile and build the untouched baseline

Run the generic production path:

`PYTHONPATH=. python -m core reconcile benchmark/lululemon/extracted --source-root benchmark/lululemon/source -o benchmark/lululemon/reconciled`

Then build:

`PYTHONPATH=. python -m core build benchmark/lululemon/reconciled/standardized.json -o release/lululemon/Lululemon`

Produce a matched `Lululemon_Trainer.xlsx` / `Lululemon_Answer_Key.xlsx` if the current engine can do so. Do not add analytical features merely to improve the baseline in this task. Record actual periods, overlap/supplemental conflicts, bound sources, component count, and any build failure.

### Task 3: Make LULU a permanent real-company regression

Create `core/tests/test_lululemon_benchmark.py` using source-supported anchors measured from the reconciled output. At minimum verify:

- all four filings validate and remain source-bound;
- reconciliation is deterministic across two runs;
- the reconciled period axis covers the intended FY2021–FY2025 historical range where supported by the filings;
- current production build either succeeds reproducibly or its exact general blocker is captured by a failing test before any fix;
- no LULU-specific production branch is introduced.

Run focused LULU tests, the Fast Retailing benchmark test, then `PYTHONPATH=. pytest core/tests -q`.

### Task 4: Record the Step 9M.2 gap map

Create `benchmark/lululemon/BASELINE.md` and `benchmark/lululemon/GAPS.md`; update `RESULT.md` with measured evidence only.

Classify each material LULU deficiency as one of:

1. extracted/source-data defect;
2. generic ingestion/reconciliation defect;
3. generic historical BAV analytical gap;
4. qualitative target-research item outside the workbook engine.

Prioritize generic historical gaps relevant to `TARGET.md`, especially inventory/working capital, capex/depreciation/asset intensity, leases, dilution/per-share history, segment economics, operating KPIs, and historical interpretation where source-supported.

## Acceptance and next step

- Four LULU source filings validate or any source-input defect is explicitly isolated.
- Generic reconciliation artifacts exist and are deterministic.
- A reproducible current-state LULU Trainer/Answer-Key baseline exists, or one precise general blocker is proven by test.
- LULU has a committed baseline/regression test and gap map.
- Fast Retailing and synthetic regressions remain valid.
- No forecasting/valuation work and no issuer-specific production logic.
- On PASS, propose **Step 9M.2.1** as the highest-value general historical gap exposed by LULU. Do **not** declare Step 9 complete merely because this baseline step passes.
