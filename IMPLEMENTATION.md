# Step 9M.2.4.1.1.1 — Repair Coverage, Workbook Period Identity, and Acceptance Accounting

**Base:** `29fc582c212101063593daf7481fca254e7b56af`
**Status:** PROBLEMS — UNRESOLVED; repair of the same step.
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED pending every original acceptance criterion.
**Goal:** Complete pretax/ETR coverage, independently verify workbook periods, and replace unsupported completion claims with criterion-level evidence.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; write completion records and measured verification to `RESULT.md`.
- Changes limited to `core/tests/test_reference_integrity.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`; no production changes.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh.
- Verification artifacts belong only in temporary directories; preserve deterministic failure-path immutability coverage.
- Preserve classification metadata, source identity, explicit-concept and override precedence, ambiguity errors, required-value semantics, subtotal/detail boundaries, and non-balance-sheet completeness behavior.
- No invented facts or zeros, carry-forward, absent-after-zero inference, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Complete the parity coverage matrix

- Parameterize all 12 combinations: canonical `pretax_income`, alias `income_before_tax`, and normalized label fallback × both source-row orders × original and standardized export/reload input.
- For every combination, verify fixture-owned labels, concepts, period identities, amounts, and row ordering; check every historical Python pretax/ETR result and saved/reloaded Answer-Key source link and ETR expression.
- Keep expectations independent of production resolution and arithmetic helpers; retain 400 / 500 pretax, −60 / −80 tax, and 0.15 / 0.16 ETR expectations for the alias fixture.
- Retain zero-pretax `NA()` behavior, strict zero-guard/sign/numerator/denominator contracts, referenced-cell evaluation, and alias-removal, precedence, duplicate-ambiguity, missing-required-value, and tax-exclusion regressions.
- Give each matrix case a distinct test ID and record its measured outcome; partial coverage cannot establish matrix completion.

## Task 2 — Verify actual workbook period identity

- Replace `assert period == expect.period_ends[j]` with checks of actual saved/reloaded period headers in `Income Statement` and `Condensed Financials` against fixture-owned expected identities and header representations.
- Verify header count and order, and bind each pretax/tax source reference and ETR reference to its independently expected period; matching column numbers alone is insufficient.
- Establish a passing baseline, then alter or swap headers independently on each sheet while leaving formulas and values unchanged; require the same validator to reject each saved/reloaded copy with a period-specific assertion.
- Preserve separate corrupted-copy rejection for pretax links redirected to tax or another period and ETR formulas with missing minus sign, reversed division, or corrupted zero guard. Never regenerate a corrupted workbook before validation.
- Report this as formula inspection and referenced-cell evaluation, not Excel recalculation.

## Task 3 — Reconcile original acceptance and verify

- Withdraw the current unsupported COMPLETE claim. Inventory every original criterion and required evidence obligation from `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, and the current step; give each a separate RESULT entry with test node or artifact/revision, concrete measurements, and PASS/FAIL/UNVERIFIED status.
- Include causal before/after liability and equity evidence, sparse-position/zero/complete-row coverage, signed contra-equity, subtotal/override controls, missing totals/keys, contradictory and equal omissions, rounding boundaries, provenance preservation, deterministic reconciliation comparisons, and failure-path immutability. “Prior child” or aggregate suite success alone is insufficient.
- Use traceable historical evidence for unavailable pre-repair behavior; distinguish actual results from diagnostic probes. Missing evidence remains UNVERIFIED without inventing measurements or expanding production scope.
- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Probe unmodified Lululemon input in a temporary directory; record successful generation or the exact next exception without repairing it. Distinguish synthetic parity, real-company resolution, and unavailable full-company parity; workbook success is not an original parent acceptance requirement.
- Record fresh matrix/mutation outcomes, suite counts, verified revision, working-tree state, before/after source/artifact hashes, and final diff scope.

## Acceptance and next step

- All 12 matrix cases pass independent Python and emitted-formula expectations; workbook header checks reject header corruption as well as existing link/arithmetic defects.
- All four Lululemon periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies are explained with causal rows, detail counts, gaps, and tolerance envelopes.
- Independent asset, liability, and signed equity-detail gates reject unsupported sparse omissions before usable results; implied-equity reconciliation stays separate. Missing totals/keys, contradictory evidence, equal asset/liability omissions, and excessive gaps fail closed.
- Sparse absence stays distinct from reported zero through standardization, export/reload, and reformulation; provenance and selected/superseded/outside-axis observations remain preserved.
- NCIT remains 28555 / 15864 / reported 0 / `None`; Common stock remains 611 / 606 / 581 / 557; empty unclassified detail and G1/G2/G3 controls remain intact.
- Required suites pass; source facts and committed artifacts remain unchanged. Every original criterion has concrete evidence or an explicit unresolved status; missing evidence or execution restrictions cannot establish completion.
- On failure, next step: **Step 9M.2.4.1.1.1 — Repair Coverage, Workbook Period Identity, and Acceptance Accounting**.
- On acceptance, return to Plan for original-criteria parent closure assessment; preserve unresolved parents until their original criteria pass. Any genuinely new child uses **9M.2.4.1.1.1.3**. Step 9 remains incomplete.
