# Step 9M.2.3 — Narrow Paid-In-Capital Exemptions and Reject Contradictory Liability Concepts (G3)

**Base:** `b142604cd183d3f1c3c6c0abb6e67aa7137ce242`
**Status:** PROBLEMS
**Goal:** Reject common-stock payment movements and unsupported liability contradictions while preserving genuine paid-in-capital balances and supported liabilities.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_lululemon_benchmark.py` if needed, and `RESULT.md`.
- Preserve source facts, stored concepts, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, downstream reformulation repair, G4–G7 implementation, or forecasting/valuation work.

## Task 1 — Repair common-stock exclusion boundaries

- Narrow `_common_stock_concept_has_payment` exemptions to genuine paid-in-capital balance wording; the presence of `paidin` must not suppress payment detection.
- `Common stock` paired with `common_stock_paid_in_cash` must raise `UnclassifiedBalanceSheetLineError` before cash, liability, or equity fallbacks.
- Genuine payment wording must still reject common-stock rows when paid-in-capital wording also occurs.
- Extend concept-side liability evidence to accrued-expense, pension, retirement-benefit, and post-employment identities, using existing normalization conventions.
- Block both ordinary common-stock recognition routes for contradictory liability concepts. `Common stock` paired with `pension_obligation` or `accrued_expenses` must raise `UnclassifiedBalanceSheetLineError`.
- Preserve supported liability routes, their ambiguity and judgment metadata, common-stock movement scoping, and explicit override precedence.

## Task 2 — Add public-classifier regressions

- Add parameterized `classify_balance_sheet_line` tests for all three reported failures, asserting exact exception behavior.
- Cover normalized payment-concept variants, payments co-occurring with paid-in-capital wording, and contradictory retirement-benefit/post-employment concepts.
- Preserve non-ambiguous Equity with no judgment code for `Common stock` paired with `paid_in_capital` or `additional_paid_in_capital`, and existing paid-in-capital label controls.
- Retain `Accrued expenses` / `common_stock` as `Operating Working Capital Liability`; retain pension/retirement/post-employment liability labels paired with `common_stock` as ambiguous `Operating Long-Term Liability` with `pension_obligation_operating_vs_financing`.
- Retain decisive debt-concept classification, punctuation movement rejection, override precedence, ordinary common-stock, investment, redeemable/preferred, other equity-component, and G1/G2 controls.

## Task 3 — Verify and record

- Preserve Lululemon Common stock identity and values (611 / 606 / 581 / 557), the empty unclassified balance-sheet detail set, and existing gift-card/PPE assertions.
- Rerun the temporary-directory build probe and measure the expected `ReformulationIntegrityError` with `liability-detail gap`; record changed outcomes without repairing downstream gaps.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Update `RESULT.md` to supersede the previous G3 PASS claim with completion records, measured verification, build outcome, committed artifact hashes before/after, remaining blockers, and final diff scope.
- Record execution restrictions or failures explicitly; incomplete verification does not establish PASS.

## Acceptance and next step

- All three reported pairs raise through the public classifier; genuine paid-in-capital balances remain Equity.
- Supported liabilities retain exact categories and judgment behavior; existing classification controls pass.
- Required verification passes, and source facts and committed artifacts remain unchanged.
- On failure, retain **Step 9M.2.3 — Narrow Paid-In-Capital Exemptions and Reject Contradictory Liability Concepts (G3)**.
- On PASS, propose **Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity**, subject to the measured build outcome. G4 remains deferred; Step 9 remains incomplete.
