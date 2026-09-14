# Step 9M.2.4.1 — Preserve Sparse Liability Facts in Standardization

**Base:** `cdf0c9f5d0222f52728f0d6ba9cf86d61d3df63c`
**Parent:** Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity — UNRESOLVED
**Goal:** Restore omitted sparse balance-sheet facts without inventing missing values; satisfy the parent’s original integrity acceptance.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record completion and measured verification in `RESULT.md`.
- Production scope: `core/ingestion/filing_standardizer.py`, including its provenance generation.
- Test scope: `core/tests/test_filing_reconciler.py` and `core/tests/test_lululemon_benchmark.py`.
- Authorized generated changes: `benchmark/lululemon/reconciled/standardized.json`, `provenance.json`, and their benchmark hash expectations, only from verified deterministic regeneration.
- Preserve source PDFs, extracted JSON, reported labels/concepts/values, selection precedence, observations, conflicts, and unrelated committed artifacts.
- Preserve failure-path immutability guards; tests and workbook probes write only to temporary directories.
- No invented zeros, carry-forward values, absent-after-zero inference, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, or suppressed integrity errors.
- No G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Retain sparse balance-sheet facts

- Retain balance-sheet rows with selected observations on only part of the model axis; preserve supplied amounts and use explicit `None` for unreported periods through the existing nullable contract.
- Select label/concept deterministically from the latest available model-period observation; preserve source identity and keep non-balance-sheet completeness behavior unchanged.
- Update provenance to distinguish retained sparse rows and missing periods from omitted rows; retain all selected, superseded, and outside-axis observations without fabricating source evidence.
- Restore `non_current_income_taxes_payable`: 28555 at 2023-01-29, 15864 at 2024-01-28, reported 0 at 2025-02-02, and `None` at 2026-02-01.

## Task 2 — Regress and regenerate

- Add a synthetic sparse balance-sheet regression that fails before repair; cover leading, interior, and trailing absence, explicit zero versus absence, complete rows, and unchanged non-balance-sheet omissions.
- Verify standardized export/reload preserves amounts, nulls, labels, and concepts; verify provenance remains source-grounded.
- Run reconciliation twice in separate temporary directories; compare all three generated artifacts and explain every difference from committed output before refreshing authorized files and hash expectations. `conflicts.json` must remain unchanged.
- Replace the obsolete expected liability-gap blocker assertion with direct four-period integrity assertions. Preserve empty unclassified-detail, G1/G2/G3, neighboring classification, subtotal/detail, and explicit override controls.
- Retain deterministic failure-path immutability coverage and rejection of genuine omissions, contradictory inputs, equal asset/liability omissions, and gaps beyond existing rounding envelopes.

## Task 3 — Verify and record fresh evidence

- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Probe the Lululemon build in a temporary directory; record successful workbook generation or the exact next exception without repairing an unrelated blocker.
- Record exact before/after asset-detail, liability-detail, and equity gaps for all four periods, causal rows, detail counts, unchanged tolerance formulas and resulting envelopes.
- Confirm Common stock remains 611 / 606 / 581 / 557 and gift-card/PPE assertions pass.
- Record regression outcomes, fresh test counts, deterministic comparisons, before/after artifact hashes, source immutability, and final diff scope in `RESULT.md`. Previous green tests cannot establish acceptance.

## Acceptance and next step

- Parent original acceptance remains mandatory: all four periods pass `check_reformulation_integrity` within unchanged tolerance rules; liability and corresponding equity discrepancies are explained and repaired.
- Required tests pass and genuine inconsistencies still fail closed; source facts and committed artifacts remain unchanged except the explicitly authorized generated refresh and matching hash expectations.
- Sparse absence remains distinguishable from reported zero throughout standardization and export/reload; no missing fact is invented to obtain PASS.
- Retain **Step 9M.2.4 — UNRESOLVED** until every original acceptance criterion passes. Missing evidence, execution restrictions, or further required production scope remain blockers.
- On failure, next step: **Step 9M.2.4.1 — Preserve Sparse Liability Facts in Standardization**. On acceptance, return to Plan for parent closure and selection of an unused detailed ID for subsequent work; Step 9 remains incomplete.
