# Step 9M.2.4.1.1 — Repair Sparse Equity-Detail Evidence Reconciliation

**Base:** `17114fc2b600b461a6c68fe6b30ad1ab01dbc11e`
**Status:** PROBLEMS — UNRESOLVED; repair planned
**Parents:** Step 9M.2.4.1 and Step 9M.2.4 — UNRESOLVED
**Goal:** Reject unsupported sparse equity omissions while preserving every original parent acceptance criterion.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record completion and measured verification in `RESULT.md`.
- Production scope: `core/model/classification.py`, limited to sparse-detail evidence reconciliation and integrity safeguards.
- Test scope: `core/tests/test_classification.py`, `core/tests/test_reference_integrity.py`, and `core/tests/test_lululemon_benchmark.py`.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh is authorized.
- Preserve classification metadata, source identity, explicit override precedence, subtotal/detail boundaries, shared required-value semantics, and non-balance-sheet completeness behavior.
- Verification artifacts belong only in temporary directories; preserve deterministic failure-path immutability coverage.
- No invented zeros, carry-forward, absent-after-zero inference, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, or suppressed integrity errors.
- No G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Reproduce and repair the equity evidence gate

- Reproduce removal of 100 of equity detail through explicit `None` while independent totals remain unchanged; demonstrate that existing asset-detail, liability-detail, and implied-equity gaps incorrectly remain zero.
- Reconcile classified equity detail independently against supplied reported equity for every period requiring sparse-detail eligibility; retain the existing implied-equity identity check separately.
- Use signed equity contributions, exclude subtotals, and apply the existing rounding formula to the actual equity-detail count without changing existing asset, liability, or implied-equity tolerance rules.
- Require supplied independent asset, liability, and equity totals and successful separate detail reconciliations before returning usable sparse reformulation results.
- Missing keys, unavailable totals or reconciliation evidence, unsupported absence, and contradictory detail must fail closed. Eligible absence remains non-contributing only in the affected aggregate; never rewrite source nulls.

## Task 2 — Add focused regression coverage

- Add a regression that fails on the reviewed revision and rejects the 100 equity omission after repair despite zero existing identity gaps.
- Cover sparse equity with leading, interior, and trailing absence; reported zero; complete rows; missing keys; unavailable totals; and equity-detail gaps at and beyond the unchanged rounding envelope.
- Cover incomplete equity detail when a sparse asset or liability activates the gate, signed contra-equity contributions, subtotal exclusion, and explicit override controls.
- Preserve genuine omission, contradictory input, equal asset/liability omission, and rounding-boundary rejection controls.
- Retain supported sparse liability success, nullable export/reload, source-value immutability, four-period Lululemon integrity, empty unclassified detail, and G1/G2/G3 assertions.

## Task 3 — Verify and record fresh evidence

- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Probe the Lululemon build in a temporary directory; record workbook generation or the exact next exception without repairing unrelated blockers.
- Record the reproduction and repair outcome, all four periods’ exact asset-detail, liability-detail, equity-detail, and implied-equity gaps, causal rows, detail counts, tolerance formulas, and envelopes.
- Confirm NCIT remains 28555 / 15864 / reported 0 / `None`, Common stock remains 611 / 606 / 581 / 557, and gift-card/PPE controls pass.
- Correct the unsupported completion claim in `RESULT.md`; record verified revision, working-tree state, fresh test outcomes/counts, source/artifact hashes before and after, and final diff scope.

## Acceptance and next step

- Unsupported sparse equity omissions fail closed before usable reformulation results; balanced assets and liabilities alone cannot authorize missing equity detail.
- All four Lululemon periods pass `check_reformulation_integrity` within unchanged tolerance rules; original liability and corresponding equity discrepancies are explained and repaired.
- Required tests pass, genuine inconsistencies still fail closed, and source facts and committed artifacts remain unchanged.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; provenance and selected observations remain preserved, and no missing historical fact is invented.
- Keep Step 9M.2.4.1.1 and both parents UNRESOLVED until their original acceptance criteria pass; missing evidence, execution restrictions, or further required production scope remain blockers.
- On failure, next step: **Step 9M.2.4.1.1 — Repair Sparse Equity-Detail Evidence Reconciliation**. On acceptance, return to Plan for parent closure assessment and selection of an unused detailed ID; Step 9 remains incomplete.
