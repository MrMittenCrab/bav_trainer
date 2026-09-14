# Step 9M.2.4.1.1.1 — Repair Generic Pretax-Income Resolution

**Base:** `8c0098c8091f65814f77ed1b9d3fd082a1721671`
**Status:** PLANNED
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — UNRESOLVED pending original-criteria closure assessment.
**Previous repair:** Sparse equity reconciliation PASS; broader parent closure is not established.
**Goal:** Resolve supplied pretax-income identity without changing historical facts or weakening integrity gates.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; record completion and measured verification in `RESULT.md`.
- Production scope: `core/model/line_resolver.py`, limited to generic pretax-income resolution and directly implicated tax-expense exclusion.
- Test scope: `core/tests/test_line_resolver.py`, `core/tests/test_reference_integrity.py`, and `core/tests/test_lululemon_benchmark.py`.
- Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, committed artifacts, and baseline hashes; no generated refresh.
- Preserve explicit-concept precedence, ambiguity errors, source identity, classification overrides, subtotal/detail boundaries, required-value semantics, and non-balance-sheet completeness behavior.
- Verification artifacts belong only in temporary directories; retain deterministic failure-path immutability coverage.
- No invented values, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated blocker repair.

## Task 1 — Assess parent criteria and trace the blocker

- Compare original acceptance in plans `aa6adc1`, `a370a02`, `2e88322`, and `88ce931` against `RESULT.md` and the supplied PASS review; record each criterion as supported, failed, or unverified.
- Distinguish the satisfied sparse-equity repair from unresolved parent closure; workbook probes originally allowed recording the next exception and must not be rewritten as unconditional workbook-success criteria.
- Reproduce `MissingLineError: Required concept 'pretax_income' not found in statement lines`.
- Trace supplied `income_before_tax` / “Income before income tax expense” through standardized data, selected filing provenance, resolver priority, and the reference-model source row.

## Task 2 — Repair resolution and add focused regressions

- Add the narrow generic explicit-concept alias `income_before_tax` for `pretax_income`, retaining canonical `pretax_income`; support the exact normalized supplied label when explicit identity is unavailable.
- Ensure that label cannot resolve as `tax_expense`; preserve existing legitimate tax-expense resolution.
- Demonstrate pre-repair failure and post-repair success; cover canonical and alias identities, normalized label fallback, explicit-concept precedence, duplicate ambiguity, missing required lines, and nearby nonmatching labels.
- Verify Python calculations and Excel source links resolve the same supplied row, with unchanged values and concept through export/reload.
- Replace the obsolete expected pretax exception with direct resolution/source-link assertions; probe workbook generation and record any next exception without expanding production scope.

## Task 3 — Verify and record

- Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. pytest core/tests -q`.
- Retain four-period asset-detail, liability-detail, equity-detail, and implied-equity integrity assertions, empty unclassified detail, and G1/G2/G3 controls.
- Record exact gaps, detail counts, unchanged tolerance envelopes, causal liability/equity rows, test outcomes/counts, workbook outcome, verified revision, working-tree state, before/after source/artifact hashes, and final diff scope in `RESULT.md`.

## Acceptance and next step

- Supplied pretax income resolves generically and consistently in Python and Excel; tax expense remains distinct, and ambiguity and missing required evidence still fail closed.
- Original parent acceptance remains mandatory: all four Lululemon periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies are explained and repaired.
- Independent asset, liability, and signed equity-detail evidence gates reject unsupported sparse omissions; implied-equity reconciliation remains separate.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; provenance and selected observations remain preserved.
- NCIT remains 28555 / 15864 / reported 0 / `None`; Common stock remains 611 / 606 / 581 / 557; gift-card/PPE controls pass.
- Required suites pass, genuine inconsistencies fail closed, and source facts and committed artifacts remain unchanged.
- Keep parents UNRESOLVED until every original criterion is supported; unavailable evidence or access remains a blocker.
- On failure: **Step 9M.2.4.1.1.1 — Repair Generic Pretax-Income Resolution**. On PASS: return to Plan for evidence-based parent closure and selection of an unused detailed ID for any remaining blocker; Step 9 remains incomplete.
