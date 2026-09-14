# Step 9N.3 — Source-Supported Lease-Repayment Diagnostics

**Base:** `3eb729b26e21cc6d8bb8c41864296f8b35f739e8`

**Goal:** Teach reported historical lease-repayment cash and revenue intensity through the matched Trainer, Answer Key, and Check.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`. Cursor must never modify either file.

**Writable files:**
- New: `core/model/lease_repayment.py`, `core/tests/test_lease_repayment.py`.
- Existing: `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/workbook.py`, `core/trainer/checker.py`.
- Verification and records: `core/tests/test_fast_retailing_benchmark.py`, `core/tests/test_historical_v1_exit_gate.py`, `docs/GOOGL_HISTORICAL_REFERENCE.md`, `RESULT.md`.

### Task 1: Implement source resolution and calculations

- Read `RESULT.md` before assessing the previous step; distinguish its recorded regression passes from independently verified results.
- Follow `core/model/capex.py` conventions for exact-concept CF resolution, period validation, signed cash conversion, and undefined ratios.
- Resolve only unique CF `repayments_of_lease_liabilities`; absent, ambiguous, label-only, or wrong-statement sources activate no module. Missing/null required period values fail closed without zero-filling.
- Compute `lease_repayments = -reported_repayments` and `lease_repayments_to_revenue = lease_repayments / revenue`; preserve source signs and values, never use `abs()`.
- Keep repayment activation independent of lease-liability balances, ROU balances, and lease-interest disclosures. Infer no repayments from balance changes.

### Task 2: Integrate the historical practice surface

- Add `LEASE_REPAYMENT_COMPONENT_CATALOG` with families `lease_repayments` and `lease_repayments_to_revenue`, orders 122–123, category/semantic prefix `lease_repayment`.
- Expand both families for every supplied historical period; integrate expected values, semantic mapping, workbook family metadata, and Check.
- Add a compact `LEASE REPAYMENT CONTEXT` block on ALT DuPont using existing optional-module layout conventions.
- Keep reported CF facts populated; practice formulas negate the source link and calculate revenue intensity.
- Answer-Key Notes explain signed repayment cash and intensity, distinguishing them from total lease cost, ROU amortization, and liability movement.
- Extend the historical catalog freeze to orders 1–123 with explicit new ID/order assertions; preserve all existing identities and deferred-category isolation.

### Task 3: Verify and record outcomes

- Test source gating, renamed/reordered exact-concept rows, missing/null periods, negative/positive/zero reported cash, zero revenue, and single-period support.
- Verify formula/source alignment, Trainer blank yellow cells without Notes, Answer-Key formulas with Notes, visual parity, and non-disclosing blank/correct/incorrect Check behavior.
- Assert Fast Retailing FY2021–FY2025 repayments of 148,248 / 136,889 / 140,646 / 146,403 / 140,483 JPY mn and ratios against supplied revenue.
- Assert 10 repayment specs and 491 total Fast Retailing specs; preserve 10 capex specs, existing liability/ROU specs, and three overlap plus three supplemental conflicts. DEMO remains unchanged.
- Run `python -m pytest core/tests/test_lease_repayment.py core/tests/test_historical_v1_exit_gate.py core/tests/test_fast_retailing_benchmark.py -q`.
- Run `python -m pytest core/tests -q`, `git diff --check`, and inspect `git diff --name-only`.
- Direct completion records, commands, measured outcomes, and limitations to `RESULT.md`; synchronize coverage, blockers, and exit-gate assessment in `docs/GOOGL_HISTORICAL_REFERENCE.md`.

### Acceptance criteria

- Source-supported repayment diagnostics work throughout reference-model → Trainer/Answer-Key → Check; unsupported inputs fail closed.
- Required tests pass; source fixtures, reconciliation evidence, and existing analytical results remain unchanged.
- Discount-rate analysis, complete lease roll-forward, and ROU acquisition-payment diagnostics remain separately deferred.
- Clear the repayment blocker only on measured evidence; reassess all Step 9 exit criteria without declaring completion from this module alone.
- No forecasting, valuation, or Step 10 implementation; only writable files change.
