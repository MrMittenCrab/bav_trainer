# Step 9M.9 — Source-Gated Capex-to-Revenue Practice

**Base:** `59cf3907ac964f83a4c5a03c9feea517afa1bad2`

**Goal:** Add historical PP&E capex and capex-to-revenue practice with matching Answer Key formulas, Notes, and workbook-wide Check.

### Task 1: Extend capex calculations and expected values

**Files:** `core/model/capex.py`, `core/model/historical_expected.py`

- Preserve `compute_capex_series` source/sign behavior; add current-period `ppe_capex_to_revenue` using resolved historical revenue and `ratio_or_na`.
- Missing/`None` required period values raise `MissingHistoricalValueError`; explicit zero capex remains valid; zero revenue yields `UNDEFINED_RATIO`.
- Add expected-value families for `ppe_capex` and `ppe_capex_to_revenue`, following existing optional-module dispatch conventions.

### Task 2: Integrate workbook practice and Check

**Files:** `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/checker.py`

- Add capex component catalog/spec expansion with semantic keys `capex.ppe_capex` and `capex.ppe_capex_to_revenue`; wire builder registration, counts, and Check reconstruction.
- Gate the section on the existing unique, explicit `payments_for_ppe` cash-flow source contract; unavailable sources produce no capex rows or practice specs.
- Add an `ALT DuPont` section following the intangible-payments layout: populated reported-payment source links, `PP&E Capex (−reported)`, and `PP&E Capex / Revenue`.
- Register two practice cells per historical period. Use formulas that negate reported payments and divide capex by same-period revenue, with `IF(revenue=0,NA(),...)`.
- Provide concise Answer Key Notes explaining sign conversion, revenue intensity, and zero-denominator behavior; Trainer cells remain blank yellow without Notes.
- Include both families in workbook-wide, non-disclosing Check through existing semantic mapping.

### Task 3: Verify practice and update coverage

**Files:** `core/tests/test_capex.py`, `core/tests/test_fast_retailing_benchmark.py`, `docs/GOOGL_HISTORICAL_REFERENCE.md`

- Extend capex tests for ratios, positive/negative/mixed/zero payments, zero revenue, and missing/`None` inputs.
- Verify workbook gating for absent, label-only, duplicate, and wrong-statement sources; renamed/reordered valid sources retain correct links.
- Verify semantic families, matched workbook structure, Answer Key formulas/Notes, populated source links, and Trainer practice formatting.
- Exercise Check for blank, correct, incorrect, and undefined-ratio answers without answer disclosure.
- Verify Fast Retailing FY2021–FY2025 capex anchors and independently calculated revenue ratios; add ten capex practice cells and update affected benchmark counts.
- Mark capex-to-revenue practice complete in the reference audit; leave other capex diagnostics deferred.

### Validation

- Run `python -m pytest core/tests/test_capex.py core/tests/test_line_resolver.py core/tests/test_goodwill_intangibles.py core/tests/test_fast_retailing_benchmark.py -q`.
- Run `git diff --check`.

### Acceptance criteria

- Supported sources activate two checked capex practice families across all historical periods.
- Formulas, model expectations, Notes, and Check agree on signed capex and undefined ratios.
- Unsupported sources remain inactive; missing historical values are never substituted.
- No depreciation ratios, reinvestment bridge, forecasting, valuation, or source/provenance changes.
