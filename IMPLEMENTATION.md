# Step 9N.1 — Repair Lease-Payment Exit-Gate Evidence

**Base:** `f4172600c5348c9b5baf442ac00ffced1f47fcc8`

**Goal:** Correct lease-payment dispositions and reassess historical curriculum closure.

**Writable files:** `RESULT.md`, `docs/GOOGL_HISTORICAL_REFERENCE.md`.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`. Cursor must never modify either file.

### Task 1: Establish supplied facts and actual coverage

- Read the previous assessment in `RESULT.md`.
- Trace `repayments_of_lease_liabilities` and `payments_for_rou_assets` through `benchmark/fast_retailing/reconciled/standardized.json`, relevant provenance entries, and referenced extracted filing rows.
- Record FY2021–FY2025 values, units, sign conventions, and source references. Measure repayment materiality against supplied revenue and lease-liability balances; assess ROU acquisition payments separately.
- Verify coverage in `core/model/lease_liability.py`, `core/model/lease_rou.py`, their component catalogs, and corresponding tests: liability balances, intensity, change/growth, ROU balance context, and treatment-conditioned lease interest. Identify payment and amortization diagnostics as absent.

### Task 2: Correct dispositions and affected exit criteria

- Replace unsupported repayment-duplication and amortization claims throughout both writable files, including the gap matrix, queue, and completion statements.
- Separate source-supported repayment diagnostics from discount-rate analysis and a complete lease roll-forward. Missing rates do not prevent analysis of reported repayments; balance changes do not measure amortization or repayments.
- Classify repayment analysis as an unresolved source-supported gap unless a concrete, measured curriculum reason supports deferral. Do not use missing contracts or ROU acquisition-payment materiality to dismiss repayments.
- Reassess exit criteria 1, 2, and 6 with explicit pass/fail/unverified dispositions and evidence. Preserve unaffected evidence and the recorded criterion 5 regression blocker.
- Synchronize the queue and exactly one next implementation across both documents. Retain catalog-freeze repair as the next implementation unless the corrected assessment establishes a higher-priority blocker; keep every unresolved blocker visible.

### Task 3: Verify and record the repair

- Run `python -m pytest core/tests/test_lease_liability.py core/tests/test_lease_rou.py -q`.
- Run `git diff --check` and inspect the changed-file list.
- Record corrected source measurements, coverage findings, commands, measured outcomes, and limitations in `RESULT.md`.
- Label previous full-suite and benchmark results as prior measurements; do not imply they were rerun.

### Acceptance criteria

- Both documents distinguish implemented balance diagnostics from absent repayment/amortization analysis.
- Lease-payment dispositions cite supplied facts, measured materiality, and actual module coverage.
- Exit criteria 1, 2, and 6 no longer rely on unsupported curriculum-closure claims.
- Step 9 remains incomplete while material gaps or regression blockers remain; no Step 10 advancement.
- Exactly one next implementation is recorded consistently.
- Only the two writable documents change; no code, tests, fixtures, or baselines are modified.
