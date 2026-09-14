# Step 9M.2.4.1.1.1 — Repair Independent Pretax and ETR Parity Verification

**Base:** `8bd5f5071a3fa174165f08b246ce43dc82e94340`
**Status:** PROBLEMS — UNRESOLVED; repair of the same step.
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED pending original acceptance evidence.
**Goal:** Establish independent calculation expectations, validate emitted ETR arithmetic, demonstrate wrong-link rejection, and correct unsupported completion claims.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record completion and measured verification in `RESULT.md`.
- Changes limited to `core/tests/test_reference_integrity.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`; no production changes.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh.
- Verification artifacts belong only in temporary directories; preserve deterministic failure-path immutability coverage.
- Preserve source identity, explicit-concept and override precedence, ambiguity errors, required-value semantics, subtotal/detail boundaries, and non-balance-sheet completeness behavior.
- No invented company facts, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Replace circular expectations and verify emitted arithmetic

- Give parity assertions explicit fixture-owned labels, period identities, pretax values, tax values, and expected ETRs; never derive expectations through `resolve_line`, `ratio_or_na`, or other production helpers.
- Check every `compute_anchor` historical pretax and ETR result against those expectations, including 400 / 500 pretax, −60 / −80 tax, and 0.15 / 0.16 ETR.
- Build and reload actual Answer-Key workbooks with formulas retained; resolve emitted pretax and tax links to independently expected source labels, period columns, and values.
- Validate the complete emitted ETR expression: zero-denominator guard, `NA()` branch, negative-tax numerator, pretax denominator, and same-period references. Replace substring checks with a strict test-local formula contract and evaluation of its actual referenced cells.
- Compare evaluated emitted arithmetic with independent expectations and Python outputs; cover nonzero and zero pretax. Describe this as formula inspection/evaluation, not Excel recalculation.
- Exercise canonical concept, alias concept, normalized label fallback, and both source-row orders before and after standardized export/reload.

## Task 2 — Demonstrate corruption rejection

- Separate workbook construction from parity validation so negative controls validate saved, reloaded corrupted workbook copies without regenerating them.
- Establish a passing baseline, then redirect an emitted pretax link to the tax row and separately to another period; require the same validator to reject each with a specific assertion.
- Mutate emitted ETR formulas independently: remove the minus sign, reverse numerator/denominator, and corrupt the zero guard; demonstrate rejection despite retaining referenced row names and `NA()`.
- Restore or rebuild clean temporary copies between mutations; retain alias-removal, precedence, duplicate ambiguity, missing-required-value, and tax-exclusion regressions.

## Task 3 — Verify and correct RESULT

- Withdraw unsupported COMPLETE, independent-expectation, emitted-arithmetic, and wrong-link-detection claims; replace them only with measured evidence from the repaired checks.
- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Probe unmodified Lululemon input in a temporary directory; record successful generation or the exact next exception without repairing it. Workbook success is not an original parent acceptance requirement.
- Record independent inputs/results, inspected formulas/source cells, each mutation and rejection, fresh suite counts, verified revision, working-tree state, before/after source/artifact hashes, and final diff scope.
- Reconcile every original criterion from `aa6adc1`, `a370a02`, `2e88322`, and `88ce931` with concrete evidence or failed/unverified status; distinguish synthetic parity, real-company resolution, and unavailable full-company parity.

## Acceptance and next step

- Independent expectations establish Python pretax/ETR correctness; actual emitted source links and ETR arithmetic pass positive controls and reject the injected defects.
- All four Lululemon periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies are explained and repaired with causal rows, detail counts, gaps, and tolerance envelopes recorded.
- Independent asset, liability, and signed equity-detail gates reject unsupported sparse omissions; implied-equity reconciliation remains separate. Missing totals/keys, contradictory inputs, equal asset/liability omissions, and excessive gaps fail closed.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; provenance and selected observations remain preserved.
- NCIT remains 28555 / 15864 / reported 0 / `None`; Common stock remains 611 / 606 / 581 / 557; empty unclassified detail and G1/G2/G3 controls remain intact.
- Required suites pass and source facts and committed artifacts remain unchanged. Missing evidence or execution restrictions cannot establish completion.
- On failure, next step: **Step 9M.2.4.1.1.1 — Repair Independent Pretax and ETR Parity Verification**.
- On acceptance, return to Plan for original-criteria parent closure assessment; parents remain unresolved until those criteria pass. Any genuinely new child uses **9M.2.4.1.1.1.2**. Step 9 remains incomplete.
