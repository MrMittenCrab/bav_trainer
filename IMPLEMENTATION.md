# Step 9M.9 — Capex Practice Validation Gate

**Base:** `671239c73379e8c3da103d2e1fe51269ce52d0b4`

**Goal:** Complete the pending capex practice validation in a writable environment.

### Task 1: Run the required validation

- Run `python -m pytest core/tests/test_capex.py core/tests/test_line_resolver.py core/tests/test_goodwill_intangibles.py core/tests/test_fast_retailing_benchmark.py -q`.
- Run `git diff --check`.
- Record test totals and any failures, errors, or skips; confirm workbook integration tests execute.

### Task 2: Resolve validation failures

**Files, only if implicated:** `core/model/capex.py`, `core/model/historical_expected.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/checker.py`, the four validation test files, and `docs/GOOGL_HISTORICAL_REFERENCE.md`.

- Fix concrete failures within the existing capex practice scope; preserve semantic keys and explicit source gating.
- Preserve signed capex, same-period revenue ratios, missing-value errors, and undefined ratios for zero revenue.
- Rerun the complete validation command and `git diff --check` after any fixes.

### Acceptance criteria

- All four test modules pass in a writable environment, including workbook integration coverage.
- Tests verify source gating, formula/expectation agreement, Trainer/Answer-Key parity, Notes, and non-disclosing Check.
- Fast Retailing FY2021–FY2025 capex anchors, revenue ratios, and practice counts pass.
- `git diff --check` passes.
- No new analytical modules, forecasting, valuation, or source/provenance changes.
