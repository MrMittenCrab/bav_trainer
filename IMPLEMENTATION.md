# Step 9M.2.4.1.1.1.32 — Lululemon geographic segment-fact extraction and supplemental reconciliation

AUTOCYCLE_PLAN: {"baseline": "At 4b38ea1aa2a27e4adc06e510cb78dbf346e828fa, the accepted assessment verifies five-period geographic revenue, segment operating profit and consolidated bridges; all four filing JSONs have empty note_facts and supplemental observations lack later-audited selection.", "finding_key": "lululemon-geographic-segment-facts-and-selection-missing", "inputs": [], "kind": "work", "objective": "Establish source-grounded geographic segment facts and deterministic supplemental reconciliation", "plan_id": "54dbb892521c44bc90dffd4ecded2eb0", "step_id": "9M.2.4.1.1.1.32", "success": "Independently extracted geographic segment facts reconcile deterministically across five periods, retain all source observations and selection evidence, and reproduce consolidated revenue and operating-profit bridges without changing canonical reconciled artifacts or releases.", "verification": "Inspect retained source anchors; rerun focused ingestion tests and temporary reconciliation; independently reproduce the prior-presentation mutation, role precedence, rejection cases and all five bridges; compare protected artifacts and non-note filing content with b17e8460fd5baa272ceaa4d86886fe50c9515279.", "work_id": "24a805ab41064b6aa5a8b6ad474edf88"}

## Scope

- Repair the existing work `24a805ab41064b6aa5a8b6ad474edf88`; acceptance remains unresolved.
- Permit changes to `core/ingestion/geographic_segment.py`, directly necessary supplemental contracts/parser/validator/reconciler/serialization under `core/data/filing.py` and `core/ingestion/`, corresponding filing tests, and `RESULT.md`.
- Retain completed extraction. Existing permission for FY2023–FY2025 Lululemon extracted JSON remains limited to source-supported `note_facts` corrections; use in-memory fixtures for mutations.
- Preserve source PDFs, FY2022 JSON, non-note filing content, canonical reconciled artifacts, releases and Fast Retailing bytes. Generate verification artifacts only in temporary directories.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, workbook generation, forecasting or valuation.

## Task 1 — Repair presentation eligibility and precedence

- Define and enforce eligibility at the complete period/source presentation level before ranking; prevent mixed-role facts from assembling a falsely comparable snapshot. Reject ambiguous mixtures and incomplete eligible bridge groups.
- Eligible roles are `current_period`, `comparative` and `restated_comparative`; retain `prior_presentation` observations in audit provenance but exclude them from comparable selection. Fail closed when a period has no eligible complete presentation.
- Apply explicit role precedence consistent with the filing contract: restated comparative above current/comparative, current and comparative at equal rank, then later filing year within that rank. Preserve ambiguity rejection for unresolved equal-priority candidates.
- Preserve whole-presentation selection, namespace/definition compatibility, units, strict values, provenance validation, duplicate rejection, bridge completeness and failure immutability.
- Serialize the actual selected role and truthful selection reason, including exclusion of newer prior presentations and restated precedence; retain all superseded observations and disagreements even when values agree. Keep geographic selection separate from statement rows and unrelated supplemental behavior.

## Task 2 — Add regression coverage

- Reproduce the blocking mutation: mark FY2025 observations for `2025-02-02` as `prior_presentation`, add 100 to Americas revenue and subtract 100 from another segment. Consolidated controls must still pass; selection must retain FY2024 Americas revenue `7928156`, preserve the superseded `7928256`, and explain role eligibility accurately.
- Cover equal-valued prior observations, current/comparative year precedence, restated precedence, prior-only periods, mixed roles, incomplete eligible presentations and equal-priority contradictions; reverse filing and observation order.
- Verify parser/export and audit serialization preserve roles, winners, losers and disagreements; rejected cases must leave inputs and output artifacts unchanged.
- Retain coverage for missing segments/items, incompatible definitions/units, invalid values/provenance, corporate double counting, revenue/operating-profit and IS-control mismatches, empty notes, unchanged lease/share handling and no segment promotion onto statement lines.

## Task 3 — Verify and record

- Run focused geographic, filing JSON, reconciler and CLI tests; Lululemon/Fast Retailing benchmark tests; and the required `core/tests` suite. Record the interpreter, commands and measured outcomes; unavailable pytest is a verification blocker, not a passing result.
- Reconcile unchanged filings to temporary output with `2022-01-30` admitted. Retain 105 observations and 56 selections; preserve source years FY2023 for `2022-01-30`, FY2024 for `2023-01-29`, and FY2025 for `2024-01-28`, `2025-02-02` and `2026-02-01`.
- Independently reproduce all five revenue and operating-profit bridges and accepted IS cross-checks at zero USD-thousands tolerance, including `3607682 - 1397067 = 2210615`.
- Verify retained source support: FY2023 Note 23 PDF p84/printed 78; FY2024 Note 23 PDF p79–80/printed 73–74; FY2025 Note 24 PDF p79–81/printed 73–75. Preserve labels, signs, dates, units, hashes and pages; no repeat extraction absent a concrete defect.
- Update `RESULT.md` with repair completion evidence, role policy, selection matrix/reasons, mutation and rejection results, fact counts, and checkpoint-relative protected hashes/non-note comparisons. Distinguish historical 88/171/1267 test results from fresh evidence; do not claim spreadsheet recalculation.

## Original acceptance and retained commitments

- Every extracted value remains source-supported; all five selected periods reconcile reproducibly; conflicts, restatements and original provenance survive serialization. Missing evidence is never marked verified.
- Preserve the Q4-2023 geographic namespace, reported expense/gain signs and separate bridge operations; distinguish corporate totals from components. Omitted items stay absent. China Mainland is not PRC; no manufactured `2021-01-31` facts or week adjustments.
- Exclude channel/country/product disaggregation, segment assets/capex, significant-expense schedules, D&A, store KPIs and lease detail from this step.
- Preserve Lululemon five-period history, 486 identities/expectations, 101 unavailable displays and accepted 110 additions; Fast Retailing remains byte-identical at 577 identities and zero unavailable displays.
- Retain G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping and original-row provenance.
- Retain independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls and failure immutability.
- Preserve partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution and distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference or deferred-tax expense/recoverability claims.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / reported 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences, reformulation tolerances and liability/equity discrepancy explanations.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds.
- Preserve remaining benchmark-improvement and parent-acceptance obligations for requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; do not restart completed publication recovery.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its five snapshot-matched edit identities, historical batch and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`; retain hash-bound logs `cursor-20260915-033742-18263.log` and `cursor-20260915-034910-19408.log`, distinguishing original subprocess success, resumed wrapper failures and fresh evidence.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1` and `9M.2.4` remain unresolved; A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED remain distinct.
- Record remaining selected-facts → `StandardizedFinancials` dependency, optional segment payload, analytical schedules and learner/Check integration; carry G6 missing `2021-01-31` BS, remaining G7 store KPIs/lease maturity and note facts, G8 deferral, G9 standalone interest completeness and all TARGET Step 9 exit gates. No parent or Step 9 completion claim.
