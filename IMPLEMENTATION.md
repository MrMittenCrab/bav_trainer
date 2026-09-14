# Step 9M.2.3 — Repair Punctuation Movements, Liability Preservation, and Paid-In-Capital Balances (G3)

**Base:** `901a4b2df4a16d2469344e5d38b3e264a834a808`
**Status:** PROBLEMS
**Goal:** Close common-stock payment escapes while preserving supported liabilities and paid-in-capital balances.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_lululemon_benchmark.py` if needed, and `RESULT.md`.
- Preserve source facts, stored concepts, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, downstream reformulation repair, G4–G7 implementation, or forecasting/valuation work.

## Task 1 — Repair movement detection

- Normalize punctuation consistently for common-stock topic detection and payment phrases in labels and concepts, following existing project conventions without changing stored identities.
- Reject payment variants such as `Cash-paid-for common-stock`, `Cash paid—for common stock`, and `Paid-for common stock`, including label-only rows and rows with exact `common_stock` concepts.
- Raise `UnclassifiedBalanceSheetLineError` before concept or label fallbacks can classify movements as cash assets, liabilities, or equity.
- Replace the unrestricted concept `paid` match with payment-sensitive detection that preserves `paid_in_capital` and `additional_paid_in_capital` balances. Genuine payment wording must still reject rows containing paid-in-capital wording.
- Keep movement guards scoped to common-stock identity and preserve explicit override precedence.

## Task 2 — Preserve liabilities and add public-classifier regressions

- Prevent both ordinary common-stock recognition routes from overriding supported accrued-expense, pension, retirement-benefit, and post-employment liability evidence.
- `Accrued expenses` / `common_stock` must retain `Operating Working Capital Liability`; `Pension obligations` / `common_stock` must retain ambiguous `Operating Long-Term Liability` with `pension_obligation_operating_vs_financing`.
- Preserve existing supported liability categories and judgment metadata; unsupported contradictory concepts paired with whole-label `Common stock` must fail closed.
- Add parameterized `classify_balance_sheet_line` regressions for punctuation in both payment phrases and common-stock topics, covering exact, empty, unrelated, and fallback-triggering concepts.
- Assert exceptions for movement rows and exact categories, ambiguity, and judgment codes for liability controls.
- Assert non-ambiguous Equity for `Common stock` paired with `paid_in_capital` or `additional_paid_in_capital`, and paid-in-capital labels paired with their concepts or `common_stock`.
- Retain ordinary common-stock, genuine-payment, override, investment, redeemable/preferred, other equity-component, and G1/G2 controls.

## Task 3 — Verify and record

- Retain Lululemon Common stock identity and values (611 / 606 / 581 / 557), empty unclassified balance-sheet detail set, and existing gift-card/PPE assertions.
- Rerun the temporary-directory build probe; measure the expected `ReformulationIntegrityError` with `liability-detail gap`. Record changed outcomes without repairing downstream gaps.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Update `RESULT.md` to supersede the previous G3 PASS claim with completion records, measured verification, build outcome, artifact hashes before/after, remaining blockers, and final diff scope. Record restrictions or failures explicitly.

## Acceptance and next step

- Punctuation-normalized common-stock payments fail closed through the public classifier unless explicitly overridden.
- Supported accrued-expense and pension liabilities preserve classification and judgment behavior; paid-in-capital balances remain Equity.
- Existing classification controls pass; source facts and committed artifacts remain unchanged.
- Required verification passes; incomplete verification does not establish PASS.
- On failure, retain **Step 9M.2.3 — Repair Punctuation Movements, Liability Preservation, and Paid-In-Capital Balances (G3)**.
- On PASS, propose **Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity**, subject to the measured build outcome. G4 remains deferred; Step 9 remains incomplete.
