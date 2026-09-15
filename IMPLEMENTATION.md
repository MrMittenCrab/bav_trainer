# Step 9M.2.4.1.1.1.19 — Generic Source-Availability Gating for Interest-Dependent Analysis

AUTOCYCLE_PLAN: {"baseline": "At 94db2b04e5915d7326de71e2b62bc772032d155e, four-period Lululemon capex resolves, but compute_anchor and ReferenceModelBuilder raise MissingLineError for absent standalone interest; Fast Retailing retains its 491-cell release contract.", "finding_key": "interest-source-absence-blocks-supported-historical-analysis", "kind": "work", "objective": "Gate interest-dependent historical analysis by source availability", "plan_id": "90dd105fe66843c8a5636b8390e7c0af", "step_id": "9M.2.4.1.1.1.19", "success": "Lululemon generates a matched historical workbook pair containing supported analysis while unavailable interest-dependent outputs remain explicitly unavailable and excluded from practice and Check; Python and Excel agree, Fast Retailing retains its contract, and regenerated releases demonstrate measured improvement without invented facts.", "verification": "Read RESULT.md; inspect availability rules and dependency coverage, reproduce focused and benchmark checks, compare Python expected values with workbook formulas and semantic maps, and verify regenerated release hashes, active-cell counts, missing-fact preservation and unresolved parent criteria.", "work_id": "94dff45c03374b6484c0c4e51a1ef1d4"}

**Base:** `94db2b04e5915d7326de71e2b62bc772032d155e`
**INPUT_STATUS:** PENDING
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 remain UNRESOLVED.
**Identity:** Controller assigns this new work’s identity; preserve completed assessment and recovery identities.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; respect filesystem permissions. No commits or pushes.
- Preserve source PDFs, extracted/reconciled facts, provenance, accepted capex edits and historical recovery records; numbering remains frozen.
- No issuer-specific rules, invented interest, inferred zero, cash-interest substitution, mixed-income equivalence, forecasting or valuation.
- Authorize bounded production/test changes and generated release updates for this availability contract; replace the previous documentary-only file restriction for this step.

## Task 1 — Implement the shared availability contract

- Add generic concept/period availability assessment alongside `core/model/financial_math.py`, using existing resolver precedence and source-value validation.
- Distinguish absent lines and missing period values from reported zero, ambiguity, invalid values and mathematically undefined ratios; ambiguity and malformed evidence still raise.
- Apply availability to interest, after-tax interest, NOPAT and every transitive dependent output, including historical cost-of-debt aggregates; never substitute the existing 4% fallback for unavailable history.
- Retain independent supported outputs. A dependent cell is available only when all its required periods and facts exist; expose missing concepts/periods and reasons.
- Preserve strict required-input resolution for explicit requests for unavailable calculations and all unrelated required facts.

## Task 2 — Integrate Python, Excel and training surfaces

- Update `core/engine/reference_model.py`, affected historical model consumers, semantic mapping and `core/trainer/` integration only where required by the dependency contract.
- Build supported historical schedules without evaluating unavailable branches; display consistent source-unavailable status in both workbooks without creating synthetic source rows.
- Exclude unavailable outputs from active practice, expected answers, hints and Check counts; retain supported formulas, Answer-Key Notes, blank yellow Trainer cells and non-disclosing Check.
- Preserve independent balance-sheet integrity gates, visible workbook parity and existing undefined-ratio semantics.

## Task 3 — Verify and measure

- Add focused tests for each interest concept missing independently, both absent, partial-period absence, reported zero, alias/explicit precedence, ambiguity and malformed inputs; use synthetic issuers and unchanged Lululemon facts.
- Independently verify available numerical outputs and unavailable dependency closure across Python, Excel formulas, export/reload, semantic maps and Check; test adjacent-period dependencies and failure-path immutability.
- Run affected model/trainer suites, reference-integrity and both benchmark suites, then the full suite; record commands, actual subprocess exits and limitations.
- Measure baseline versus result: workbook build outcomes, available/unavailable outputs by period, active practice counts and Check outcomes; distinguish workbook access gains from unchanged source completeness.

## Task 4 — Regenerate releases and record acceptance

- Regenerate Fast Retailing through `scripts/build_fast_retailing_release.py`; add a bounded equivalent Lululemon release entry point using existing validated filing and workbook APIs.
- Stage generation and verification before replacing release artifacts; retain exactly one Trainer/Answer-Key pair per issuer with required supporting sidecars and availability documentation.
- Verify repeat-build semantic determinism, artifact hashes, blank/correct/incorrect Check behavior and Fast Retailing’s 491-cell contract.
- Record completion evidence in `RESULT.md` and relevant benchmark `GAPS.md`; preserve unresolved criteria and remaining requested work.

## Acceptance and retained parent criteria

- Lululemon produces a usable matched pair from unchanged facts; all unavailable interest dependencies are visibly identified and excluded from grading. Source-interest completeness remains unresolved.
- Both engines retain supplied pretax resolution, distinct tax expense, explicit-concept precedence, ambiguity errors and strict missing-required-value failures outside optional gated analysis.
- All four Lululemon periods pass unchanged reformulation tolerances; retain liability/equity discrepancy explanations and independent asset, liability and signed-equity detail gates, including sparse omission and contradiction rejection.
- Preserve absence versus zero, source identities and comparative provenance; NCIT remains 28555 / 15864 / reported 0 / `None`, and Common stock 611 / 606 / 581 / 557.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all 12 pretax/ETR cases, mutation controls, deterministic comparisons and failure immutability requirements.
- Preserve the original parent temporary-build criterion: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; this new step requires successful gated generation.
- Carry forward A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending closure, E11 NonReq UNVERIFIED, G5 lease/deferred-tax coverage, G6 period-axis assessment, G7 note facts, G8 deferral and remaining TARGET Step 9 gates.
- Keep INPUT_STATUS PENDING until all frozen requests are satisfied; child success does not close parents or justify blanket DONE.
