# Step 9M.8 — Capex Source and Sign Contract

**Base:** `5a01a8bd5964a9dfab7b929696767cf0e20ef68f`

**Goal:** Establish tested source resolution and sign conversion for the planned `payments_for_ppe` capex module.

### Task 1: Implement the source and sign contract

**Files:** `core/model/line_resolver.py`, `core/model/capex.py` (new)

- Register `payments_for_ppe` as explicit-concept-only, following existing resolver normalization; no label or pattern fallback.
- Resolve only from `StandardizedFinancials.cash_flow`. Follow existing optional-module source, applicability, and series conventions.
- Missing or duplicate sources make the module unavailable; direct computation without a usable source raises `MissingLineError`.
- Read each requested period through `required_period_value`; missing values raise `MissingHistoricalValueError`, while explicit zero remains valid.
- Expose `payments_reported` and `ppe_capex` series. Preserve source values and calculate `ppe_capex = -payments_reported`.
- Define input as signed cash flow: negative payments become positive expenditure; positive reported values remain negative analytical capex. Never use absolute values or infer sign from the series.
- Do not infer capex from investing totals, PP&E movements, D&A, intangible purchases, or lease payments.

### Task 2: Test resolution and sign behavior

**Files:** `core/tests/test_capex.py` (new), `core/tests/test_line_resolver.py`

- Cover unique concept resolution, renamed labels, reordered rows, absent concepts, label-only matches, duplicates, and concepts supplied in the wrong statement.
- Cover negative, positive, mixed-sign, and explicit-zero values; missing and `None` period values; requested-period ordering; and unchanged input data.
- Load the existing Fast Retailing standardized fixture and verify FY2021–FY2025 capex equals `56500`, `51271`, `61764`, `73728`, `135535`.
- Run `python -m pytest core/tests/test_capex.py core/tests/test_line_resolver.py core/tests/test_goodwill_intangibles.py core/tests/test_fast_retailing_benchmark.py`.

### Task 3: Document the bounded contract

**Files:** `docs/GOOGL_HISTORICAL_REFERENCE.md`, `IMPLEMENTATION.md`

- Record source gating, missing-period behavior, and the signed-cash-flow conversion contract.
- Mark the capex source contract complete only after verification; retain workbook capex practice as pending.
- Keep Revenue and optional PP&E dependencies reserved for subsequent analytical ratios and context.
- Record actual test results and blockers; run `git diff --check`.

### Acceptance criteria

- Capex resolution fails closed for missing or ambiguous sources and never substitutes missing historical values.
- Sign tests and Fast Retailing anchors pass without changing source facts or provenance.
- Workbook generation, semantic practice registration, Check coverage, and benchmark practice counts remain unchanged.
- This step adds no ratios, reinvestment bridge, workbook practice, forecasting, or valuation.
