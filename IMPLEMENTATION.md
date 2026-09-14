# Step 9M.2.4.1.1.1 — Correct Completion Accounting and Isolated Verification

**Base:** `590c73a4eba8ee2901687f8f2d03e63aacc865bd`
**Status:** PROBLEMS — UNRESOLVED; repair of the same step.
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 remain UNRESOLVED until their original acceptance criteria pass.
**Goal:** Correct unsupported completion and numbering; replace artifact-mutating suite evidence with protected isolated verification.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; only `RESULT.md` may change in the authoritative workspace.
- No production or test changes. Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, release/demo workbooks, and baseline hashes.
- Disposable verification copies may generate or overwrite machine-generated artifacts within their isolated roots only; never copy generated artifacts back.
- Use only permitted writable temporary storage. Unavailable isolation or execution access remains a blocker; do not bypass permissions.
- Preserve classification metadata, source identity, concept/override precedence, ambiguity errors, required-value semantics, subtotal/detail boundaries, and non-balance-sheet completeness.
- No invented facts, zeros, carry-forward, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated repairs.

## Task 1 — Correct accounting and numbering

- Replace the operative COMPLETE status and acceptance-met claim in `RESULT.md` with PROBLEMS — UNRESOLVED; retain the current detailed step ID.
- Replace the proposed exhausted child `9M.2.4.1.1.1.5` with `9M.2.4.1.1.1.6` only as the first available ID for genuinely new bounded work; do not renumber historical work.
- Preserve the criterion ledger against `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, `a62893f`, and `0f1d2c3`, including original wording and source revision.
- Separate technical acceptance, evidence availability, and Plan-owned closure. A complete ledger cannot establish acceptance while required obligations remain unresolved.
- Retain prior suite counts as historical observations; withdraw their use as proof of isolated execution or artifact immutability. Record that reverting FR/demo mutations did not satisfy protection during execution.
- Reassess dependent PASS summaries, including A4/E8; assign FAIL or UNVERIFIED wherever supporting evidence does not establish the complete obligation.

## Task 2 — Establish artifact-protecting isolation

- Create independent disposable copies of the verified revision for each required suite, preserving required repository-relative inputs and baseline artifacts without writable hard links or symlinks into the authoritative workspace.
- Inspect suite subprocesses and output paths, including the Fast Retailing reconciliation refresh and demo/release generation; ensure imports, working directories, caches, temporary files, and generated outputs resolve within permitted isolated storage.
- Record the revision, copy method, resolved roots, input/baseline manifests, and protection mechanism before execution. A temporary pytest directory alone does not redirect repository-relative writes.
- Protect the authoritative workspace from test writes throughout execution; hash all tracked files except the authorized `RESULT.md` update before and after each suite, including failure paths. Do not use restoration as evidence of immutability.
- If protection cannot be established, record the exact restriction and leave verification UNVERIFIED.

## Task 3 — Rerun and record evidence

- In its isolated copy, run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- In separate isolated copies, run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Record exact commands, execution roots, code/input revisions, exit codes, measured counts, log locations, isolated artifact changes, authoritative before/after hashes, and final diff scope.
- Preserve traceable dual-reconciliation evidence for standardized/provenance/conflicts artifacts, both run hashes, immutable committed comparisons, and separate subprocess-failure, comparison-failure, mutation-detection, and drift-detection outcomes.
- Retain criterion-specific evidence for all 12 pretax/ETR cases, saved/reloaded header mutations, source-link/arithmetic mutations, zero-pretax behavior, and resolver safeguards; distinguish formula inspection/reference evaluation from Excel recalculation.
- Probe unmodified Lululemon input in isolation; record generation success or the exact next exception. Keep synthetic parity, real-company resolution, and unavailable full-company parity separate.

## Original acceptance retained

- All four periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies have complete causal and historical evidence, including resolved totals, detail counts, gaps, envelopes, and causal row identities/amounts.
- Independent asset, liability, and signed equity-detail gates reject unsupported sparse omissions before usable results; implied-equity remains separate. Missing keys/totals, contradictory evidence, equal omissions, and excessive gaps fail closed.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; selected, superseded, and outside-axis observations remain preserved.
- Synthetic before/after proof, sparse-position/zero/complete-row cases, latest-available label/concept selection, contra-equity, subtotal/override controls, non-balance-sheet omissions, empty unclassified detail, and G1/G2/G3 safeguards retain criterion-specific evidence.
- Preserve NCIT 28555 / 15864 / reported 0 / `None` and Common stock 611 / 606 / 581 / 557.
- All 12 parity cases, workbook mutation controls, required suites, deterministic comparisons, and failure-path immutability pass; authoritative source facts and committed artifacts remain unchanged throughout execution.
- Every original obligation has supported PASS or explicit FAIL/UNVERIFIED accounting. Historical gates that did not exist and aggregates unavailable after exceptions remain explicitly unavailable; workbook generation success is not an original parent acceptance requirement.
- On unresolved acceptance, next step: **Step 9M.2.4.1.1.1 — Correct Completion Accounting and Isolated Verification**. Only after original acceptance passes, return to Plan for closure assessment; genuinely new bounded work first uses **9M.2.4.1.1.1.6**. Step 9 remains incomplete.
