# Step 9N.2 — Repair Historical Active-Catalog Freeze

**Base:** `8ddee77790761659ec61fef4c3be884cfe42115a`

**Goal:** Restore the historical catalog regression gate with all currently active optional catalogs covered.

**Writable files:** `core/tests/test_historical_v1_exit_gate.py`, `RESULT.md`, `docs/GOOGL_HISTORICAL_REFERENCE.md`.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`. Cursor must never modify either file.

### Task 1: Repair the catalog contract

- Read `RESULT.md` before assessing the previous step.
- Use `core/engine/component_catalog.py` as the read-only source of existing family identities and orders.
- Extend `ACTIVE_CATALOGS` with `GOODWILL_INTANGIBLES_COMPONENT_CATALOG`, `DEFERRED_TAX_COMPONENT_CATALOG`, and `CAPEX_COMPONENT_CATALOG`; retain lease ROU and existing catalogs.
- Freeze the complete active historical namespace: orders 1–121, including goodwill/intangibles 98–111, lease ROU 112–115, deferred tax 116–119, and capex 120–121.
- Assert explicit expected family-ID/order mappings for these additions, preserving uniqueness checks and deferred-ID/category isolation.
- Clarify the test’s description to cover the current Step 9 historical namespace. Preserve existing family IDs, orders, and workbook assertions.

### Task 2: Run required verification

- Run `python -m pytest core/tests/test_historical_v1_exit_gate.py -q`.
- Run `python -m pytest core/tests -q`.
- Run `python -m pytest core/tests/test_fast_retailing_benchmark.py -q`.
- Verify Fast Retailing retains 481 practice specs, 10 capex specs, three overlap conflicts, and three supplemental conflicts.
- Run `git diff --check` and inspect `git diff --name-only`.

### Task 3: Record outcomes and synchronize blockers

- Direct completion records, commands, measured outcomes, and limitations to `RESULT.md`; distinguish new results from prior measurements.
- Update the exit-gate assessment and queue in `docs/GOOGL_HISTORICAL_REFERENCE.md` to match measured regression results.
- Clear the catalog-freeze blocker only if required tests pass.
- Keep material lease-repayment diagnostics unresolved and Step 9 incomplete; preserve separate deferrals for discount-rate analysis, complete lease roll-forward, and ROU acquisition payments.
- If verification passes, record exactly one next implementation consistently in both documents: source-supported lease-repayment diagnostics. Otherwise, retain the concrete regression repair as next.

### Acceptance criteria

- Every current active historical catalog is covered by a fixed namespace assertion; duplicate IDs/orders and deferred forecast/valuation leakage still fail.
- Required regression and Fast Retailing benchmark tests pass without changing production code, fixtures, baselines, or benchmark expectations.
- Fast Retailing counts and conflict evidence remain unchanged.
- Only writable files change; no new analytical modules or Step 10 advancement.
- Both documents preserve the unresolved repayment gap and agree on the next implementation.
