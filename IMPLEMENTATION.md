# Step 9M.2.1 — Repair Customer-Prepayment Movement Exclusions and Liability Fallbacks (G1)

**Base:** `da4b3e1b7b6ffc4c987ad5a0ec21ea893f595703`
**Status:** PROBLEMS
**Goal:** Prevent movement rows from being classified as customer-prepayment balances or escaping exclusions through liability fallbacks.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`.
- Preserve source inputs, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards; generate test artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, G2–G7 implementation, or forecasting/valuation work.

## Task 1 — Repair movement exclusions

- Make concept and label movement exclusions consistent, including `Recognition of deferred revenue` with an empty concept or a supported balance concept.
- Ensure excluded customer-prepayment movements cannot regain liability classification through current, noncurrent, other-liability, or long-term label fallbacks.
- Cover recognition, derecognition, change, increase, decrease, amortization, additions, and reductions using bounded matching.
- Require unsupported movement rows to raise `UnclassifiedBalanceSheetLineError`; preserve explicit override precedence.
- Preserve valid balance classification, noncurrent-before-current handling, contradictory-asset exclusions, and existing deferred-tax, lease, financial-instrument, and equity treatment.

## Task 2 — Add regressions through the public classifier

- Add parameterized cases for label-only movement wording, movement labels paired with balance concepts, and movement concepts paired with balance labels.
- Cover gift-card, deferred-revenue, unearned-revenue, and contract-liability movements, including noncurrent and long-term labels that reach broad liability fallbacks.
- Assert `UnclassifiedBalanceSheetLineError` for unsupported movements; checking only that the customer-prepayment reason is absent is insufficient.
- Retain positive current/noncurrent balance controls, safe asset treatment, override precedence, no-guided-judgment coverage, and the two-period NOWC/NOLA/Net Debt/equity reformulation checks.
- Confirm the new regressions expose the base revision’s defects before applying the repair.

## Task 3 — Verify benchmarks and record completion

- Retain Lululemon gift-card classification across all four periods, exactly `Property and equipment, net` and `Common stock` as unclassified rows, and the temporary build probe’s exact PPE blocker.
- Retain deterministic reconciliation, committed-hash, failure-path immutability, and no-issuer-branch assertions.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Update `RESULT.md` to supersede the premature G1 PASS with the repair outcome, regression evidence, newly measured check results, before/after reconciliation hashes, remaining G2/G3 blockers, and final diff scope. Report restrictions or failures explicitly.

## Acceptance and next step

- Recognition and other excluded movements fail closed across customer-prepayment classification and liability fallbacks unless explicitly overridden.
- Valid balance classifications and reformulation results remain correct; required checks pass and committed artifacts remain unchanged.
- On failure, retain **Step 9M.2.1 — Repair Customer-Prepayment Movement Exclusions and Liability Fallbacks (G1)**.
- On PASS, propose **Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)**; Step 9 remains incomplete.
