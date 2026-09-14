# Step 9M.2.4.1.1.1 — Complete Criterion-Level Evidence Accounting

**Base:** `7303db27810ba0e3c42ae59ee7c066424ab2cb60`
**Status:** PROBLEMS — UNRESOLVED; repair of the same step.
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED until every original acceptance criterion passes.
**Goal:** Supply omitted reconciliation and historical measurement evidence; explicitly retain unavailable evidence as UNVERIFIED.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record measured verification and completion accounting in `RESULT.md`.
- Edit only `RESULT.md` and, if necessary for evidence capture, `core/tests/test_lululemon_benchmark.py`; no production changes.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh.
- Run reconciliation, historical reproductions, tests, and workbook probes in isolated temporary locations under available permissions.
- Preserve classification metadata, source identity, concept/override precedence, ambiguity errors, required-value semantics, subtotal/detail boundaries, and non-balance-sheet completeness behavior.
- No invented facts or measurements, zeros, carry-forward, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Correct the acceptance ledger

- Withdraw the current COMPLETE claim and closing assertion that this step’s acceptance is met.
- Inventory each original criterion and required evidence obligation from `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, and `a62893f`; retain source revision and criterion wording without weakening scope.
- Give each obligation a separate PASS/FAIL/UNVERIFIED entry with exact test node or revision/artifact, command, measured outcome, and evidence location. Split bundled entries when their evidence or status differs.
- Explicitly include deterministic reconciliation, complete historical before/after measurements, synthetic before-failure/after-success evidence, provenance observations, unchanged non-balance-sheet omissions, and every inherited safeguard.
- Distinguish fresh measurements, traceable historical measurements, diagnostic probes, and unavailable evidence. Aggregate suite success, unchanged hashes, and “prior child” references cannot substitute for criterion-specific proof.
- Keep closure decisions separate from technical criteria; missing evidence remains UNVERIFIED with the precise missing measurement and blocker.

## Task 2 — Supply reconciliation and historical evidence

- Run the existing deterministic reconciliation path twice in separate temporary directories using identical unmodified filing inputs; record revision, exact commands, exit outcomes, and input hashes.
- For `standardized.json`, `provenance.json`, and `conflicts.json`, record both generated hashes, their byte comparison, and each comparison with committed output. Explain every difference; never refresh outputs or expectations to obtain PASS.
- Record `test_generic_reconcile_is_deterministic` and each subprocess-failure, comparison-failure, mutation-detection, and drift-detection outcome separately.
- Recover traceable pre-repair evidence from historical revisions and RESULT records; reproduce in temporary isolation where supported. For all four periods, report before/after asset-detail, liability-detail, equity-detail, and implied-equity gaps, actual detail counts, tolerance formulas/envelopes, resolved totals, and causal included/excluded row identities and amounts.
- Identify each historical code/input revision and distinguish the original liability defect, subsequent sparse-value exception, and equity-omission regression. Where an aggregate was unavailable or a gate did not exist, record that fact and UNVERIFIED; do not infer historical measurements from current results.
- Preserve NCIT 28555 / 15864 / reported 0 / `None` and Common stock 611 / 606 / 581 / 557; connect discrepancy explanations to source-grounded observations.

## Task 3 — Verify and finalize the accounting

- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Retain distinct outcomes for all 12 pretax/ETR matrix cases, actual workbook-header mutations, source-link/arithmetic mutations, zero-pretax behavior, and resolver safeguards; report formula inspection/reference evaluation, not Excel recalculation.
- Probe unmodified Lululemon input in a temporary directory; record generation success or the exact next exception. Keep synthetic parity, real-company resolution, and unavailable full-company parity distinct; workbook success is not an original parent acceptance requirement.
- Record verified revision, working-tree state, commands, counts, source/artifact hashes before/after, final diff scope, and every execution restriction.

## Acceptance and next step

- All four periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies are explained with complete historical evidence, causal rows, counts, and envelopes.
- Independent asset, liability, and signed equity-detail gates reject unsupported sparse omissions before usable results; implied-equity remains separate. Missing keys/totals, contradictory evidence, equal omissions, and excessive gaps fail closed.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; selected, superseded, and outside-axis observations remain preserved.
- Sparse-position, zero, complete-row, contra-equity, subtotal, override, non-balance-sheet completeness, empty unclassified-detail, and G1/G2/G3 controls remain satisfied.
- All 12 parity cases and workbook mutation controls pass; required suites, deterministic artifact comparisons, and failure-path immutability pass; source facts and committed artifacts remain unchanged.
- Every original obligation has concrete evidence or explicit UNVERIFIED/FAIL accounting. A complete ledger does not establish technical completion while required evidence remains missing.
- On unresolved evidence or failure, next step: **Step 9M.2.4.1.1.1 — Complete Criterion-Level Evidence Accounting**.
- Only after every original criterion passes, return to Plan for parent closure assessment. Any genuinely new child uses **9M.2.4.1.1.1.4**; Step 9 remains incomplete.
