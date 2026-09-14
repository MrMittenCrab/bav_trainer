# Step 9M.2.4.1.1.1 — Complete Criterion-Level Evidence Accounting

**Base:** `c4a09ed6338c2ab87df40d68b258b0d346b2994e`
**Status:** PROBLEMS — UNRESOLVED; repair of the same step.
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED until every original acceptance criterion passes.
**Goal:** Complete missing evidence, replace unsupported PASS entries, and withdraw unsupported completion.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record evidence and completion accounting in `RESULT.md`.
- Edit only `RESULT.md` and, where necessary for missing evidence coverage, `core/tests/test_filing_reconciler.py`, `core/tests/test_classification.py`, and `core/tests/test_lululemon_benchmark.py`; no production changes.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh.
- Execute historical reproductions, tests, reconciliation, and workbook probes only in permitted temporary isolation. Access restrictions remain blockers.
- Preserve classification metadata, source identity, concept/override precedence, ambiguity errors, required-value semantics, subtotal/detail boundaries, and non-balance-sheet completeness.
- No invented facts, zeros, carry-forward, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated repairs.

## Task 1 — Repair the acceptance ledger

- Withdraw `RESULT.md`’s COMPLETE status and assertion that this step’s acceptance is met; retain this step and its parents as UNRESOLVED.
- Inventory original criteria and evidence obligations from `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, `a62893f`, and `0f1d2c3`, preserving source revision and wording.
- Split each obligation into criterion-specific PASS/FAIL/UNVERIFIED entries with exact test node and parameters or artifact location, code/input revision, command, measured outcome, and evidence location.
- Reassess A2/E4 historical explanations, B3/E6 provenance, C5 synthetic before/after proof, and the unitemized non-balance-sheet safeguards; downgrade unsupported claims and dependent summaries to UNVERIFIED.
- Keep technical acceptance, evidence availability, and Plan-owned closure separate. Suite totals, unchanged hashes, current negative/positive tests, and “prior child” references alone cannot prove these missing obligations.

## Task 2 — Complete missing evidence

- Recover historical records or reproduce isolated historical code/input pairs for the original liability defect, sparse-value exception, and equity-omission regression; identify exact revisions and artifact hashes.
- For all four periods, account separately for asset-detail, liability-detail, equity-detail, and implied-equity gaps, resolved totals, actual detail counts, tolerance formulas/envelopes, and causal included/excluded row identities and amounts.
- Distinguish historical measurements from current-code diagnostic probes. Gates that did not exist and aggregates unavailable because execution raised remain explicitly UNVERIFIED; do not infer missing historical results.
- Demonstrate each required synthetic regression on identified pre-repair and repaired revisions using the same fixture and acceptance assertion: sparse standardization, eligible sparse aggregation, and rejection of the 100 equity omission despite zero identity gaps. Record expected versus observed behavior and exit outcomes; unrelated setup failures are not before-failure proof.
- Inspect `test_standardize_retains_sparse_balance_sheet_facts` and relevant committed provenance; record concrete selected, superseded, and outside-axis observations with row/period, amount, source identity, selection disposition, and artifact location.
- Separately verify leading/interior/trailing absence, reported zero, complete rows, latest-available label/concept selection, and export/reload identity. Record incomplete non-balance-sheet fixtures, omitted rows, omission reasons, and exact assertions proving unchanged behavior; add focused coverage only where absent.
- Preserve NCIT 28555 / 15864 / reported 0 / `None` and Common stock 611 / 606 / 581 / 557. Give every unavailable measurement its precise blocker.

## Task 3 — Verify and record

- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q` in isolation that protects committed artifacts.
- Retain traceable dual-reconciliation evidence for all three generated artifacts, both run hashes, committed comparisons, and separate subprocess-failure, comparison-failure, mutation-detection, and drift-detection outcomes.
- Record distinct outcomes for all 12 pretax/ETR cases, saved/reloaded workbook-header mutations, source-link/arithmetic mutations, zero-pretax behavior, and resolver safeguards; describe formula inspection/reference evaluation, not Excel recalculation.
- Probe unmodified Lululemon input in temporary isolation; record generation success or the exact next exception. Keep synthetic parity, real-company resolution, and unavailable full-company parity separate; workbook success is not an original parent acceptance requirement.
- Record verified revision, working-tree state, commands, counts, before/after source/artifact hashes, final diff scope, and execution restrictions.

## Acceptance and next step

- All four periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies have complete causal and historical evidence.
- Independent asset, liability, and signed equity-detail gates reject unsupported sparse omissions before usable results; implied-equity remains separate. Missing keys/totals, contradictory evidence, equal omissions, and excessive gaps fail closed.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; selected, superseded, and outside-axis observations remain preserved.
- Synthetic before/after proof, sparse-position/zero/complete-row cases, contra-equity, subtotal/override controls, non-balance-sheet omissions, empty unclassified detail, and G1/G2/G3 safeguards have criterion-specific evidence.
- All 12 parity cases, workbook mutation controls, required suites, deterministic comparisons, and failure-path immutability pass; source facts and committed artifacts remain unchanged.
- Every original obligation has supported PASS or explicit FAIL/UNVERIFIED accounting. A complete ledger does not establish completion while required evidence or acceptance remains unresolved.
- On any unresolved requirement, next step: **Step 9M.2.4.1.1.1 — Complete Criterion-Level Evidence Accounting**. Only after original acceptance passes, return to Plan for parent closure assessment; any genuinely new child starts at **9M.2.4.1.1.1.5**. Step 9 remains incomplete.
