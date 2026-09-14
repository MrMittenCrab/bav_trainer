# Step 9M.2.1 — Repair Plural Gift-Card Movement Detection and Liability Fallback Escapes (G1)

**Base:** `44e7651968651e38715e08ef8692d7acffb46eb3`
**Status:** PROBLEMS
**Goal:** Make plural gift-card movement rows raise instead of escaping through liability classification.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, and `RESULT.md`.
- Preserve source inputs, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards; generate test artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, G2–G7 implementation, or forecasting/valuation work.

## Task 1 — Repair plural gift-card detection

- Extend customer-prepayment topic matching to cover `gift card liabilities`, `gift-card liabilities`, `gift cards liabilities`, and `gift-cards liabilities`, retaining singular forms.
- Keep label topic recognition consistent between balance classification and movement protection, using bounded wording.
- Ensure movement protection raises `UnclassifiedBalanceSheetLineError` before concept classification or current, noncurrent, other-liability, and long-term label fallbacks.
- Preserve explicit override precedence, noncurrent-before-current handling, contradictory-asset exclusions, and unrelated classification behavior.

## Task 2 — Add public-classifier regressions

- Add the exact failing label `Recognition of gift card liabilities within other current liabilities` with an empty concept; assert `UnclassifiedBalanceSheetLineError`.
- Parameterize singular/plural card and liability wording, spaced/hyphenated forms, and current, noncurrent, other-liability, and long-term fallback contexts.
- Cover recognition, derecognition, change, increase, decrease, amortization, additions, and reductions across representative plural cases.
- Include empty and unrelated concepts, movement labels paired with supported balance concepts, and movement concepts paired with balance labels.
- Assert hard raises through `classify_balance_sheet_line`; absence of the customer-prepayment reason is insufficient.
- Add positive current/noncurrent plural balance controls and an explicit override control for the reported failing row. Retain existing asset, unrelated-classification, judgment, and reformulation checks.
- Demonstrate that the new defect regressions fail against the base revision before applying the repair, then pass afterward.

## Task 3 — Verify and record completion

- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Preserve Lululemon gift-card classification across all four periods, exactly `Property and equipment, net` and `Common stock` as unclassified rows, and the temporary build probe’s exact PPE blocker.
- Verify deterministic reconciliation, committed hashes, failure-path immutability, and no-issuer-branch guards.
- Update `RESULT.md` to supersede the previous G1 PASS with the plural repair outcome, base-failure/post-fix evidence, newly measured verification, before/after artifact hashes, remaining G2/G3 blockers, and final diff scope. Record failures or restrictions explicitly.

## Acceptance and next step

- Plural gift-card movements, including the reported label, raise without liability fallback escapes unless explicitly overridden.
- Valid balances and existing classification/reformulation behavior remain correct; required checks pass and committed artifacts remain unchanged.
- On failure, retain **Step 9M.2.1 — Repair Plural Gift-Card Movement Detection and Liability Fallback Escapes (G1)**.
- On PASS, propose **Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)**; Step 9 remains incomplete.
