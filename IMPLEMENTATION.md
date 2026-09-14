# Step 9M.2.3 — Restrict Paid-In-Capital Exemptions to Balance Wording (G3)

**Base:** `4f2dcc1bfe5b41a836f15507a186adc93e8c861d`
**Status:** PROBLEMS
**Goal:** Reject common-stock payment concepts even when paid-in-capital wording co-occurs, while preserving genuine equity balances.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, and `RESULT.md`.
- Preserve source facts, stored concepts, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, downstream reformulation repair, G4–G7 implementation, or forecasting/valuation work.

## Task 1 — Repair payment detection

- Update `_common_stock_concept_has_payment` so `paidincapital` exempts only the balance phrase itself; it must not suppress separate payment wording elsewhere in the normalized concept.
- `Common stock` / `common_stock_paid_in_cash_from_paid_in_capital` must raise `UnclassifiedBalanceSheetLineError` before cash, liability, or equity fallbacks.
- Preserve existing normalization, common-stock movement scoping, supported liability routing, contradictory-liability rejection, and explicit override precedence.

## Task 2 — Add public-classifier regressions

- Add the exact reported pair to `test_common_stock_payment_movements_raise_unclassified`; demonstrate failure before the repair and success afterward.
- Parameterize co-occurring paid-in-cash and paid-in-capital wording across snake_case, CamelCase, punctuation variants, reversed phrase order, and additional-paid-in-capital wording.
- Retain `paid_in_capital` and `additional_paid_in_capital` balance controls: Equity, `ambiguous is False`, and `judgment_code is None`.
- Retain existing cash-paid/paid-for co-occurrence, ordinary common-stock, liability, investment, redeemable/preferred, override, and G1/G2 controls.

## Task 3 — Verify and record

- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Rerun the existing temporary-directory Lululemon build probe; record the measured `ReformulationIntegrityError` with `liability-detail gap` without repairing it.
- Confirm Common stock identity and values (611 / 606 / 581 / 557), the empty unclassified balance-sheet detail set, and existing gift-card/PPE assertions.
- Update `RESULT.md` to supersede the previous G3 PASS claim with the exact regression outcome, completed repair, measured test results, build outcome, committed artifact hashes before/after, remaining blockers, and final diff scope.
- Record execution restrictions or failures explicitly; incomplete verification does not establish PASS.

## Acceptance and next step

- The reported pair and normalized co-occurrence regressions raise through `classify_balance_sheet_line`; genuine paid-in-capital balances retain exact Equity metadata.
- Required tests pass; existing classification behavior, source facts, and committed artifacts remain preserved.
- On failure, retain **Step 9M.2.3 — Restrict Paid-In-Capital Exemptions to Balance Wording (G3)**.
- On PASS, propose **Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity**, subject to the measured build outcome. G4 remains deferred; Step 9 remains incomplete.
