# Step 9M.2.4.1.1.1.32 — Lululemon geographic segment-fact extraction and supplemental reconciliation

AUTOCYCLE_PLAN: {"baseline": "At 4b38ea1aa2a27e4adc06e510cb78dbf346e828fa, the accepted assessment verifies five-period geographic revenue, segment operating profit and consolidated bridges; all four filing JSONs have empty note_facts and supplemental observations lack later-audited selection.", "finding_key": "lululemon-geographic-segment-facts-and-selection-missing", "inputs": [], "kind": "work", "objective": "Establish source-grounded geographic segment facts and deterministic supplemental reconciliation", "plan_id": "377527f6ed624e0288dcd56eb982456a", "step_id": "9M.2.4.1.1.1.32", "success": "Independently extracted geographic segment facts reconcile deterministically across five periods, retain all source observations and selection evidence, and reproduce consolidated revenue and operating-profit bridges without changing canonical reconciled artifacts or releases.", "verification": "Inspect extracted facts against cited PDF pages; rerun focused ingestion tests and temporary reconciliation; independently reproduce five-period totals, selection precedence and rejection cases; compare protected artifacts and non-note filing content with the checkpoint.", "work_id": "24a805ab41064b6aa5a8b6ad474edf88"}

## Scope

- Implement one upstream handoff: geographic segment revenue, operating profit and explicitly disclosed operating-profit reconciliation items.
- Permit changes only to `benchmark/lululemon/extracted/LULU_FY2023.json`, `LULU_FY2024.json`, `LULU_FY2025.json` within that directory; directly necessary supplemental contracts/parser/validator/reconciler/CLI serialization under `core/data/filing.py` and `core/ingestion/`; corresponding filing tests; and `RESULT.md`.
- Limit filing edits to `note_facts`. Preserve source PDFs, FY2022 JSON, all other filing content, canonical reconciled artifacts, releases and Fast Retailing bytes. Generate verification artifacts only in temporary directories.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, workbook generation, forecasting or valuation. The controller assigns authoritative IDs.

## Task 1 — Define and extract the bounded facts

- Establish an explicit namespaced `fact_type` convention identifying the Q4-2023 geographic definition, measure, segment or reconciliation item; document allowed identities, reported sign conventions and bridge operations in `RESULT.md`.
- Extract each filing independently: FY2023 Note 23 PDF p84/printed 78; FY2024 Note 23 PDF p79–80/printed 73–74; FY2025 Note 24 PDF p79–81/printed 73–75. Retain overlapping observations rather than extracting only eventual winners.
- Record Americas, China Mainland and Rest of World revenue and operating profit, disclosed consolidated control totals, and every explicitly disclosed item required for each operating-profit bridge. Preserve reported labels, values, dates, USD-thousands units, source hashes, pages and note references; use `status=reported`.
- Distinguish corporate totals from their components to prevent double counting. Preserve reported expense/gain signs; apply documented bridge operations separately. Omitted items remain absent rather than becoming inferred zeros.
- Exclude channel/country/product disaggregation, segment assets/capex, significant-expense schedules, D&A, store KPIs and lease detail. China Mainland is not PRC; do not manufacture 2021-01-31 facts or week-adjusted amounts.

## Task 2 — Add deterministic supplemental selection

- Add selection only for the explicit geographic namespace, preserving existing lease, share and unrelated supplemental behavior. Keep segment observations separate from IS/BS statement rows.
- Retain every original observation and disagreement in audit output; serialize selected identities, source filing/page, presentation basis and selection reasons separately. Distinguish original and restated presentations without conflating geographic and channel definitions.
- Select later audited comparable presentations deterministically: FY2023 for 2022-01-30, FY2024 for 2023-01-29, FY2025 for 2024-01-28, 2025-02-02 and 2026-02-01. Preserve superseded observations even when values agree.
- Fail closed on incompatible definitions/units, invalid values/provenance, unresolved equal-priority contradictions, duplicate conflicting identities or incomplete bridge groups. Never silently resolve ambiguity by input order.
- Validate each selected period: three segment revenues equal consolidated revenue; segment operating profits plus signed disclosed reconciliation items equal consolidated operating profit. Cross-check note controls against accepted consolidated IS facts and document numeric tolerance.
- Keep the optional model-facing segment payload, standardizer consumption, analytical schedules and learner exercises pending for subsequent work.

## Task 3 — Verify and record the handoff

- Test parser/export round trips, overlapping equal and revised observations, input-order independence, latest-source precedence, retained losers, missing segments/items, mixed definitions, invalid units/values, corporate double counting, bridge mismatch and failure immutability.
- Verify empty-note compatibility, unchanged lease/share handling and no segment promotion onto statement lines. Run focused filing tests and the required core regression suite; distinguish fresh results from the historical 1253-test evidence.
- Reconcile to temporary output and independently reproduce all five revenue and operating-profit bridges, including current segment profit `3607682 - 1397067 = 2210615`.
- Record commands, outcomes, source anchors, fact counts, selected-source matrix, rejected cases and before/after protected hashes in `RESULT.md`; verify non-note filing content is unchanged. Do not claim spreadsheet recalculation.
- Record the exact remaining standardizer/module dependency and broader G7 scope. Assessment acceptance stands; historical PENDING input wording is advisory and the authoritative undelivered-input snapshot is empty.

## Acceptance and retained commitments

- Every extracted value is source-supported; all five selected periods reconcile reproducibly; conflicts, restatements and original provenance survive serialization. Missing evidence is never marked verified.
- Preserve Lululemon five-period history, 486 identities/expectations, 101 unavailable displays and accepted 110 additions; Fast Retailing remains byte-identical at 577 identities and zero unavailable displays.
- Retain G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping and original-row provenance.
- Retain independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls and failure immutability.
- Preserve partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution and distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference or deferred-tax expense/recoverability claims.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / reported 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences, reformulation tolerances and liability/equity discrepancy explanations.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds.
- Preserve remaining benchmark-improvement and parent-acceptance obligations associated with requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; do not restart completed publication recovery.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its five snapshot-matched edit identities, historical batch and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`; retain hash-bound logs `cursor-20260915-033742-18263.log` and `cursor-20260915-034910-19408.log`, distinguishing original subprocess success, resumed wrapper failures and fresh evidence.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1` and `9M.2.4` remain unresolved; A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED remain distinct.
- Carry G6 missing 2021-01-31 BS, remaining G7 note facts and learner integration, G8 deferral, G9 standalone interest completeness and all TARGET Step 9 exit gates. No parent or Step 9 completion claim.
