# Step 9M.2.3 — Repair Common-Stock Liability and Movement Exclusions (G3)

**Base:** `b06b501860a6c148ab6e5319aa8293f0936d6ba5`
**Status:** PROBLEMS
**Goal:** Prevent contradictory liabilities and payment movements from classifying as ordinary common-stock Equity through either recognition route.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`.
- Preserve source facts, stored concepts, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, downstream reformulation repair, G4–G7 implementation, or forecasting/valuation work.

## Task 1 — Repair both recognition routes

- Apply contradictory liability exclusions to exact normalized `common_stock` concepts and whole-label `Common stock` recognition, inspecting both label and concept.
- Preserve supported liability classification: `Long-term debt` paired with `common_stock` must return `Financial Liability`; supported payable and other-liability balances must retain their existing categories and judgment behavior.
- Reject common-stock payment movements, including `Cash paid for common stock` and corresponding payment concepts. Detect case, whitespace, and punctuation variants using established normalization conventions.
- Ensure excluded movements raise `UnclassifiedBalanceSheetLineError` before concept or label fallbacks can classify them as cash assets, liabilities, or equity.
- Keep movement guards scoped to common-stock identity. Preserve explicit override precedence, valid common-stock balances, existing equity components, investment behavior, and G1/G2 rules.

## Task 2 — Add public-classifier regressions

- Exercise `classify_balance_sheet_line` with contradictory liability labels paired with `common_stock`, and whole-label `Common stock` paired with contradictory liability concepts.
- Assert exact supported liability categories and judgment metadata; unsupported contradictions must raise `UnclassifiedBalanceSheetLineError`.
- Cover `Cash paid for common stock` / `common_stock`, `Common stock` / `cash_paid_for_common_stock`, and label-only payment movements, including punctuation and normalization variants.
- Include movement cases containing cash, liability, or equity-component fallback wording; assert exceptions rather than merely checking the decision reason.
- Retain positive balance, redeemable/preferred stock, investment, paid-in-capital, explicit-override, and G1/G2 controls. Valid ordinary balances remain non-ambiguous Equity without judgment cases.

## Task 3 — Verify and record the repair

- Retain Lululemon Common stock identity and values (611 / 606 / 581 / 557), empty unclassified balance-sheet detail set, and existing gift-card/PPE assertions.
- Rerun the temporary-directory build probe and verify the measured `ReformulationIntegrityError` with `liability-detail gap`; report any changed outcome without repairing downstream gaps.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Update `RESULT.md` to supersede the previous G3 PASS claim with repair results, measured command outcomes, build outcome, artifact hashes before/after, remaining blockers, and final diff scope. Record execution restrictions or failures explicitly.

## Acceptance and next step

- Both recognition routes exclude contradictory liabilities; supported liability behavior survives.
- Common-stock movements fail closed through the public classifier unless explicitly overridden.
- Valid common-stock balances and existing classification controls pass; source facts and committed artifacts remain unchanged.
- Required verification passes; incomplete verification does not establish PASS.
- On failure, retain **Step 9M.2.3 — Repair Common-Stock Liability and Movement Exclusions (G3)**.
- On PASS, propose **Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity**, subject to the measured build outcome. G4 remains deferred; Step 9 remains incomplete.
