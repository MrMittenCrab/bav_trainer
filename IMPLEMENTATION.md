# Step 9M.2.4.1.1.1.17 — Restore Source-Supported Capex Coverage and Regenerate Release

**Base:** `04aa1c4a6864883062e4ccbe901d61d2e774a76c`
**Status:** PROBLEMS — UNRESOLVED.
**INPUT_STATUS:** PENDING
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 remain UNRESOLVED until their original acceptance passes and Plan assesses closure.
**Scope:** Lululemon G4 capex resolution, generic regression coverage, measured benchmark improvement, and Fast Retailing release regeneration.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Numbering is administratively frozen; do not repair historical numbering unless it prevents execution.
- Authorize bounded production/test changes and generated release refreshes below, subject to actual filesystem permissions; unavailable write access remains BLOCKED.
- Preserve source facts, provenance, conflicts, period identity, accounting tolerances, and existing release contracts. No invented interest values, issuer-specific production rules, forecasting, valuation, commits, or pushes.
- Run artifact-writing tests/builds in independent disposable copies; publish only validated authorized outputs.

## Task 1 — Establish the benchmark baseline

- Compare current Fast Retailing and Lululemon build stages and source-supported module availability; record commands, revisions, input hashes, and measurements in `RESULT.md`.
- Prioritize Lululemon G4: reported `capital_expenditures` fails the `payments_for_ppe` contract, hiding supplied capex diagnostics. Confirm filing provenance and cash-flow meaning before accepting equivalence.
- Record the separate Lululemon `interest_expense` build blocker; do not reinterpret `Other income (expense), net` as interest or supply missing values.
- Measure all four Lululemon periods’ capex availability and diagnostic outputs; record Fast Retailing module/practice counts and blank/filled Check baseline.

## Task 2 — Implement bounded generic capex support

- Update `core/model/line_resolver.py` and, only as needed, `core/model/capex.py` and the capex source-link construction in `core/engine/reference_model.py`.
- Resolve source-supported cash-flow `capital_expenditures` through the shared capex contract without changing stored concepts, values, signs, or provenance.
- Preserve canonical-concept precedence, duplicate/ambiguity handling, statement boundaries, missing-period failures, reported-zero semantics, and rejection of unsupported label-only inputs.
- Extend `core/tests/test_line_resolver.py`, `core/tests/test_capex.py`, and `core/tests/test_lululemon_benchmark.py` with generic alias, ambiguity, missing-value, sign, round-trip, and Python/Excel source-identity coverage.

## Task 3 — Measure, regenerate, and verify

- Repeat identical before/after probes on identical benchmark inputs; require Lululemon capex availability to change from unavailable to available with independently checked four-period diagnostics.
- Verify Excel formulas and Python expectations on a complete synthetic fixture using the same alias; report actual Lululemon workbook availability separately.
- Run the focused resolver/capex/Lululemon tests, retained parent regression suites, Fast Retailing benchmark tests, and `pytest core/tests -q` in isolated copies.
- Run `python scripts/build_fast_retailing_release.py`; regenerate its matched workbook pair, sidecars, supporting JSON, rowmap, and generated README under `release/fast_retailing/`.
- Verify source fidelity, semantic determinism across two builds, visual parity, blank yellow Trainer practice cells without hints, Answer-Key formulas/Notes, non-disclosing blank/filled Check, and failure-path artifact immutability before publishing validated release outputs.
- Record measured deltas, suite outcomes, artifact hashes, remaining blockers, and completion evidence in `RESULT.md`; update only relevant G4/current-stage entries in `benchmark/lululemon/GAPS.md`.

## Original parent acceptance retained

- Supplied pretax income resolves generically and consistently in Python and Excel; tax expense remains distinct; explicit-concept precedence, ambiguity errors, and missing-required-value failures remain intact.
- All four Lululemon periods pass `check_reformulation_integrity` under unchanged tolerances; original liability and corresponding equity discrepancies are explained and repaired.
- Independent asset, liability, and signed equity-detail gates reject unsupported sparse omissions before usable results; implied-equity reconciliation remains separate. Missing keys/totals, contradictory evidence, equal omissions, and excessive gaps fail closed.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; source identity, selected/superseded/outside-axis observations, and non-balance-sheet completeness remain preserved without invented facts.
- NCIT remains 28555 / 15864 / reported 0 / `None`; Common stock remains 611 / 606 / 581 / 557. G1/G2/G3, empty unclassified-detail, subtotal/override, contra-equity, and sparse-position controls retain criterion-specific proof.
- Historical causal totals, counts, gaps, envelopes, synthetic before/after evidence, all 12 pretax/ETR cases, and workbook mutation controls retain supported outcomes or explicit missing-evidence accounting.
- Required suites, deterministic artifact comparisons, and failure-path immutability pass with authoritative artifacts protected throughout execution. Complete accounting alone does not satisfy missing required technical proof.
- Original temporary-directory workbook acceptance permits success or the exact next exception: `MissingLineError: Required concept 'interest_expense' not found in statement lines`.
- Preserve A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure, and E11 NonReq UNVERIFIED/unavailable without inventing evidence.

## Child acceptance and continuation

- A production change produces measured four-period capex coverage gains; generic safeguards pass; regenerated Fast Retailing release passes its existing contract without regression.
- Documentation-only changes, passing test counts alone, or release regeneration without measured benchmark gains do not satisfy this step.
- Carry forward Lululemon interest-source/build completion, remaining source-supported benchmark gaps, and original parent closure; keep `INPUT_STATUS: PENDING` until every frozen request is satisfied. Review may report DONE only when the goal and all frozen requests are satisfied.
- **Next step:** Complete **Step 9M.2.4.1.1.1.17 — Restore Source-Supported Capex Coverage and Regenerate Release**; then return to Plan for original parent acceptance assessment and remaining Step 9 prioritization.
