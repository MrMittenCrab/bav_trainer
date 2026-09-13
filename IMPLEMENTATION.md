# Step 9M.8 — Capex Source and Sign Contract

**Base:** `5a01a8bd5964a9dfab7b929696767cf0e20ef68f`

**Goal:** Establish tested source resolution and sign conversion for the planned `payments_for_ppe` capex module.

### Task 1: Implement the source and sign contract — COMPLETE

**Files:** `core/model/line_resolver.py`, `core/model/capex.py` (new)

- Registered `payments_for_ppe` as explicit-concept-only (empty alias set); no label or pattern fallback.
- Resolves only from `StandardizedFinancials.cash_flow`. Missing/duplicate → unavailable; `compute_capex_series` raises `MissingLineError`.
- Periods via `required_period_value`; missing/`None` → `MissingHistoricalValueError`; explicit zero valid.
- Series: `payments_reported` preserved; `ppe_capex = -payments_reported` (no `abs()`, no inferred sign).

### Task 2: Test resolution and sign behavior — COMPLETE

**Files:** `core/tests/test_capex.py` (new), `core/tests/test_line_resolver.py`

- Covered unique concept, renamed labels, reordered rows, absent/label-only/duplicates/wrong-statement, sign cases, missing/`None` periods, request ordering, unchanged inputs.
- Fast Retailing FY2021–FY2025 `ppe_capex` anchors: `56500, 51271, 61764, 73728, 135535`.

### Task 3: Document the bounded contract — COMPLETE

**Files:** `docs/GOOGL_HISTORICAL_REFERENCE.md`, `IMPLEMENTATION.md`

- Documented source gating, missing-period behavior, and signed-cash-flow conversion.
- Capex **source contract** complete; workbook capex practice / ratios remain pending.
- Revenue and optional PP&E dependencies reserved for subsequent analytical ratios.

### Verification

```text
$ python -m pytest core/tests/test_capex.py core/tests/test_line_resolver.py \
    core/tests/test_goodwill_intangibles.py core/tests/test_fast_retailing_benchmark.py -q
54 passed in 6.02s

$ git diff --check
(no whitespace errors)
```

**Blockers:** none.

### Acceptance criteria

- Capex resolution fails closed for missing or ambiguous sources and never substitutes missing historical values. ✅
- Sign tests and Fast Retailing anchors pass without changing source facts or provenance. ✅
- Workbook generation, semantic practice registration, Check coverage, and benchmark practice counts remain unchanged. ✅
- This step adds no ratios, reinvestment bridge, workbook practice, forecasting, or valuation. ✅
