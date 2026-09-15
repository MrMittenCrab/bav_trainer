# Step 9M.2.4.1.1.1.19 — Repair Partial-Period Interest Availability

AUTOCYCLE_PLAN: {"baseline": "At 94db2b04e5915d7326de71e2b62bc772032d155e, four-period Lululemon capex resolves, but compute_anchor and ReferenceModelBuilder raise MissingLineError for absent standalone interest; Fast Retailing retains its 491-cell release contract.", "finding_key": "interest-source-absence-blocks-supported-historical-analysis", "kind": "work", "objective": "Gate interest-dependent historical analysis by source availability", "plan_id": "c611e81b6a3b4b32b0e8909e7df8ecf1", "step_id": "9M.2.4.1.1.1.19", "success": "Lululemon generates a matched historical workbook pair containing supported analysis while unavailable interest-dependent outputs remain explicitly unavailable and excluded from practice and Check; Python and Excel agree, Fast Retailing retains its contract, and regenerated releases demonstrate measured improvement without invented facts.", "verification": "Read RESULT.md; reproduce partial-period display and aggregate regressions; compare Python results, workbook formulas, availability sidecars and semantic maps; verify regenerated release hashes, active-cell counts, unchanged source facts, preserved benchmark contracts and unresolved parent criteria.", "work_id": "94dff45c03374b6484c0c4e51a1ef1d4"}

**Base:** `a5336a7d3c6f88709d0e11f3ed5bac8e579a6b1a`
**Identity:** Preserve work `94dff45c03374b6484c0c4e51a1ef1d4` and attempt `cf87bd67e9f24c0cbcf6655675a1a530`; numbering remains frozen.
**INPUT_STATUS:** PENDING
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; respect permissions. No commits or pushes.
- Preserve source PDFs, extracted/reconciled facts, provenance, accepted capex edits and hash-bound recovery records. The historical candidate batch is not current approval.
- No issuer-specific rules, invented interest, inferred zero, cash-interest substitution, mixed-income equivalence, forecasting or valuation.
- Limit changes to the availability repair, directly affected production/tests, release generators if necessary, generated issuer releases, benchmark `GAPS.md` and `RESULT.md`.

## Task 1 — Repair displays and shared aggregate availability

- In `core/engine/reference_model.py`, gate each condensed interest source link by concept/period availability: missing values display `Source unavailable` in both workbooks; reported zero retains its source formula. Preserve absent source rows and original source blanks.
- Align `core/model/source_availability.py` and `core/model/financial_math.py` through shared aggregate eligibility rules. Opening-period interest absence must not block a numeric average supported by comparable periods.
- Preserve unavailable status when any required comparable CoD period lacks interest; distinguish source absence from undefined ratios. Preserve existing supported-history undefined-ratio fallback semantics without substituting 4% for unavailable history.
- Ensure aggregate metadata, missing-dependency reasons, Python values and workbook output agree, including no numeric comparable CoD and single-period history. Retain all supported independent outputs and strict errors for ambiguity, malformed evidence and unrelated required facts.

## Task 2 — Add regressions and verify contracts

- Extend `core/tests/test_source_availability.py` with each interest concept missing independently or together in opening, interior and latest periods; cover omitted keys, explicit `None`, reported zero and fully absent lines.
- Assert condensed cells directly after export/reload in both workbooks; missing interest must never retain a formula linking an empty source cell. Verify supported formulas and downstream dependency closure.
- Reproduce opening-only omission with independently calculated historical average CoD `0.374`; test mixed numeric/undefined comparable ratios, missing comparable interest, no numeric comparable ratios and single-period history against metadata and Python.
- Verify unavailable outputs remain excluded from semantic maps, expected answers, hints and Check; preserve blank yellow practice cells, Answer-Key formulas/Notes, visible parity and non-disclosing blank/correct/incorrect Check behavior.
- Run focused availability tests, affected model/trainer/reference-integrity and both benchmark suites, then `core/tests`; record actual commands and subprocess exits. Separate formula inspection from spreadsheet recalculation and disclose unavailable calculation coverage.

## Task 3 — Regenerate releases and measure acceptance

- Use `scripts/build_lululemon_release.py` and `scripts/build_fast_retailing_release.py`; stage and verify generation before replacing release artifacts.
- Retain exactly one matched Trainer/Answer-Key pair per issuer, synchronized semantic maps and availability sidecars; verify repeat-build semantic determinism and record artifact hashes.
- Preserve Lululemon’s 248 active cells and Fast Retailing’s 491-cell contract; compare source/supporting hashes, unavailable-cell counts, available numerical outputs and Check outcomes against the checkpoint.
- In `RESULT.md`, correct the superseded child PASS assessment, record measured defect repairs and capex acceptance separately from recovered ownership/publication, and update relevant benchmark gaps. Carry both frozen requests and unresolved parent criteria forward; historical test logs are not fresh verification.

## Acceptance and retained parent criteria

- Partial-period interest displays never infer zero; Python, workbook output and availability metadata agree while supported periods remain usable. Lululemon’s unchanged facts produce the matched pair; standalone source-interest completeness remains unresolved.
- Preserve supplied pretax resolution, distinct tax expense, explicit-concept precedence, ambiguity errors and strict missing-required-value failures outside optional gated analysis.
- All four Lululemon periods retain unchanged reformulation tolerances, liability/equity discrepancy explanations, independent asset/liability/signed-equity detail gates, sparse omission handling and contradiction rejection.
- Preserve source identities, comparative provenance and absence versus zero: NCIT remains 28555 / 15864 / reported 0 / `None`; Common stock remains 611 / 606 / 581 / 557.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all 12 pretax/ETR cases, mutation controls, deterministic comparisons and failure immutability requirements.
- Preserve the original parent temporary-build criterion: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; this work requires successful gated generation.
- Carry forward A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending closure, E11 NonReq UNVERIFIED, G5 lease/deferred-tax coverage, G6 period-axis assessment, G7 note facts, G8 deferral and remaining TARGET Step 9 gates.
- Keep INPUT_STATUS PENDING until all frozen requests are satisfied; child acceptance neither closes parents nor permits blanket DONE.
