# Step 9M.2.4.1.1.1 — Verify Generic Pretax-Income Resolution and Correct Acceptance Accounting

**Base:** `412922feb13823a1f1f98628cca917d30ed0e579`
**Status:** PROBLEMS — UNRESOLVED; repair planned.
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED pending original-criteria evidence.
**Goal:** Directly verify Python pretax calculations and emitted Excel source formulas; correct unsupported acceptance claims.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record completion and measured verification in `RESULT.md`.
- Changes limited to `core/tests/test_reference_integrity.py`, `core/tests/test_lululemon_benchmark.py`, `core/tests/test_line_resolver.py`, and `RESULT.md`; no production changes.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh.
- Verification artifacts belong only in temporary directories; retain deterministic failure-path immutability coverage.
- Preserve explicit-concept and override precedence, ambiguity errors, required-value semantics, source identity, subtotal/detail boundaries, and non-balance-sheet completeness behavior.
- No invented company facts, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Verify actual calculation and formula paths

- Add a complete synthetic fixture using `income_before_tax` and “Income before income tax expense,” with distinct tax-expense values; keep synthetic evidence separate from Lululemon evidence.
- Execute `compute_anchor`; assert every period’s historical pretax series and effective tax rate against independently specified input values and expected arithmetic.
- Generate the reference workbook through the actual builder; reload with formulas retained and inspect emitted Pretax Income source links, referenced source labels/values, distinct tax links, and effective-tax-rate formulas for every period.
- Resolve actual formula references to source values and compare their results with Python outputs; row-index arithmetic alone is insufficient. Do not describe formula inspection as Excel recalculation.
- Repeat after standardized export/reload; cover canonical identity, alias identity, normalized label fallback, and reordered source rows.
- Retain precedence, duplicate ambiguity, missing-required-value, and tax-exclusion regressions; demonstrate the new parity coverage detects removal of the alias or a wrong emitted source link.

## Task 2 — Correct parent acceptance accounting

- Reconcile `RESULT.md` against original criteria in plans `aa6adc1`, `a370a02`, `2e88322`, and `88ce931`; record each criterion with its evidence and supported, failed, or unverified status.
- Remove workbook-generation success as an invented original parent acceptance criterion. The original probe permits either successful generation or recording the exact next exception.
- Preserve the real Lululemon pretax concept, label, four-period values, provenance, and export/reload assertions.
- Probe unmodified Lululemon input in a temporary directory; record the actual outcome, including `interest_expense` if still raised, without adding synthetic financing facts or repairing that blocker.
- Distinguish synthetic calculation/formula evidence, real-company resolution evidence, and unavailable full-company parity evidence; correct the unsupported COMPLETE claim.
- Keep parents unresolved pending evidence for every original criterion; neither workbook success nor a subsequent exception alone establishes parent acceptance.

## Task 3 — Verify and record

- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Record direct calculation outputs, inspected formulas and source cells, regression outcomes/counts, workbook outcome, verified revision, working-tree state, before/after source/artifact hashes, and final diff scope.
- Record four-period asset-detail, liability-detail, signed equity-detail, and implied-equity gaps, causal liability/equity rows, detail counts, and unchanged tolerance envelopes; mark unavailable evidence explicitly.

## Acceptance and next step

- Actual Python calculations and emitted Excel formulas demonstrably consume the same pretax inputs; tax expense remains distinct and unsupported required inputs fail closed.
- Original parent criteria remain mandatory: all four Lululemon periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies are explained and repaired.
- Independent asset, liability, and signed equity-detail evidence gates reject unsupported sparse omissions; implied-equity reconciliation remains separate.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; provenance and selected observations remain preserved.
- NCIT remains 28555 / 15864 / reported 0 / `None`; Common stock remains 611 / 606 / 581 / 557; empty unclassified detail and G1/G2/G3 controls remain intact.
- Required suites pass, genuine inconsistencies fail closed, and source facts and committed artifacts remain unchanged.
- On failure or missing required evidence: **Step 9M.2.4.1.1.1 — Verify Generic Pretax-Income Resolution and Correct Acceptance Accounting** remains unresolved.
- On acceptance: return to Plan for evidence-based parent closure assessment; any genuinely new child uses the first unused ID **9M.2.4.1.1.1.1**. Step 9 remains incomplete.
