# Step 9M.2.4.1.1 — Evidence-Grounded Sparse-Detail Reformulation Repair

**Base:** `c50912cf7fd04abbc9d99754982ba84abb2b5eb1`
**Status:** PLANNED
**Parents:** Step 9M.2.4.1 and Step 9M.2.4 — UNRESOLVED
**Goal:** Repair sparse-detail aggregation while preserving null source facts and every original parent acceptance criterion.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record completion and measured verification in `RESULT.md`.
- Production scope: `core/model/classification.py`, limited to evidence-gated sparse-detail aggregation and its integrity safeguards.
- Test scope: `core/tests/test_classification.py`, `core/tests/test_reference_integrity.py`, `core/tests/test_lululemon_benchmark.py`, and `core/tests/test_filing_reconciler.py`.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh is authorized for this child.
- Preserve classification metadata, source identity, explicit override precedence, subtotal/detail boundaries, and failure-path immutability guards.
- Verification artifacts belong only in temporary directories.
- No invented zeros, carry-forward, absent-after-zero inference, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, or suppressed integrity errors.
- Keep shared required-value semantics unchanged; no G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Establish the sparse-detail evidence gate

- Reproduce HEAD’s `MissingHistoricalValueError` for `non_current_income_taxes_payable` at 2026-02-01; trace classification, aggregation, reported totals, and committed source provenance.
- Confirm the retained series remains 28555 / 15864 / reported 0 / `None`; preserve labels, concepts, selected observations, conflicts, and export/reload identity.
- Define a generic eligibility gate for explicit nullable balance-sheet detail: require supplied independent asset, liability, and equity totals for the affected period and successful separate detail reconciliations under existing tolerance rules.
- Treat aggregate reconciliation as evidence for non-contribution only; never represent it as proof of a reported zero. Missing keys, unavailable required totals, unsupported absence, and contradictory evidence must fail closed.

## Task 2 — Repair aggregation and regress safeguards

- Permit eligible sparse detail to be non-contributing only in the affected period’s aggregate; preserve `LineItem.values` nulls and reported zeros distinctly.
- Enforce the evidence gate before returning usable reformulation results; preserve strict required-value checks for totals and other required historical inputs.
- Add synthetic before-failure/after-success coverage for leading, interior, and trailing explicit absence, reported zero, complete rows, and nullable export/reload.
- Cover missing keys, null or absent totals, genuine detail omissions, contradictory inputs, equal asset/liability omissions, and gaps beyond unchanged rounding envelopes; retain neighboring classification and override controls.
- Replace the expected sparse-value exception with direct four-period Lululemon integrity assertions; retain empty unclassified detail, G1/G2/G3 controls, and deterministic failure-path artifact immutability coverage.
- Preserve sparse-standardization provenance tests and unchanged non-balance-sheet completeness behavior.

## Task 3 — Verify and record current evidence

- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Probe the Lululemon build in a temporary directory; record workbook generation or the exact next exception without repairing an unrelated blocker.
- Record all four periods’ exact asset-detail, liability-detail, and equity gaps, causal rows, detail counts, unchanged tolerance formulas, and resulting envelopes. Distinguish actual results from unavailable pre-repair aggregates and diagnostic probes.
- Confirm Common stock remains 611 / 606 / 581 / 557 and gift-card/PPE assertions pass.
- Record verified revision and working-tree state, fresh regression outcomes and test counts, source/artifact hashes before and after, and final diff scope in `RESULT.md`; older verification does not establish acceptance.

## Acceptance and next step

- All four Lululemon periods pass `check_reformulation_integrity` within unchanged tolerance rules; the original liability and corresponding equity discrepancies are explained and repaired.
- Required tests pass, genuine inconsistencies still fail closed, and source facts and committed artifacts remain unchanged.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; no missing historical fact is invented.
- Keep **Step 9M.2.4.1 and Step 9M.2.4 — UNRESOLVED** until every original acceptance criterion passes; missing evidence, execution restrictions, or further required production scope remain blockers.
- On failure, next step: **Step 9M.2.4.1.1 — Evidence-Grounded Sparse-Detail Reformulation Repair**. On acceptance, return to Plan for parent closure assessment and selection of an unused detailed ID; Step 9 remains incomplete.
