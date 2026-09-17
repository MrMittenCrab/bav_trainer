# Step 9M.2.4.1.1.1.50 — Operating KPIs — Store-count learner schedule and Check integration

AUTOCYCLE_PLAN: {"baseline": "At aa6278a6b15f6fadb359f706d0bd62ef3faf4697, Review accepted revenue/comparable-sales comparisons with 23 fresh tests and inspected 2158-pass regression evidence. Store-count analytics already provide counts 574/655/711/767/811 and changes None/81/56/56/44; their ordinary reference-model, Trainer, Answer-Key and Check integration remains unfinished. Supplied management documents retain 135 deferred observations and zero selections.", "finding_key": "operating-kpi-store-count-workbook-integration", "inputs": [], "kind": "work", "objective": "Integrate accepted store-count analytics into the historical learning workbooks", "plan_id": "56656f9f222f41fc86fedbefca81fd98", "step_id": "9M.2.4.1.1.1.50", "success": "Validated store-count histories produce an optional historical workbook schedule with populated reported counts, semantic net-change and growth practice, matching Answer-Key formulas and Notes, and non-disclosing Check coverage; absent histories preserve existing builds.", "verification": "Read-only Review independently checks store arithmetic, semantic identities, source gating, reload, generated workbook formulas and learner surfaces, Check outcomes and tamper handling, regression evidence and protected-artifact hashes.", "work_id": "a486cad27960408bb13d183bbf863bba"}

## Scope and constraints

- Implement only the company-operated period-end store-count learner schedule: reported counts, adjacent net count change and growth. Revenue relationships and management-KPI learner schedules remain subsequent work.
- Permit necessary edits to `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/engine/build_contract.py`, `core/model/historical_expected.py`, `core/trainer/workbook.py`, `core/trainer/checker.py`, `core/trainer/check_context.py`, focused tests and `RESULT.md`; preserve accepted analytical APIs and data contracts.
- Reuse validated `StandardizedFinancials`, canonical annual axes, existing store analytics, semantic mapping and optional geographic-schedule integration conventions. Restrict build-contract edits to registering this optional schedule; no generic redesign.
- Preserve supplied JSON/PDFs, committed reconciliations, examples, releases, Fast Retailing data and accepted build-contract behavior. Generate fixtures and workbooks only in temporary locations; no re-extraction, company-specific pipeline or AutoCycle changes.
- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, publication, forecasting or valuation; permissions remain binding.

## Task 1 — Integrate the optional reference schedule

- Activate only for validated store-count observations; absent/null and management-only histories add no store schedule, practice identities or Check expectations. Deferred management documents cannot supply store-count inputs.
- Populate reported period-end counts and units; add semantic practice families for adjacent net count change and count growth, resolving formulas through semantic source identities rather than fixed coordinates.
- Preserve count units independently of monetary scale, signed changes, reported zeros and canonical gaps. Opening change/growth are not practiced; missing dependencies remain unavailable and non-practice; zero denominators retain the existing undefined-ratio convention.
- Reuse accepted arithmetic without substituting periods or compressing gaps. Label changes as net count changes, not gross openings/closures; infer no productivity, same-store sales, geographic allocation or causality.
- Preserve source context and population labels. Reject malformed contracts and unsupported axes without mutation.

## Task 2 — Complete Trainer, Answer Key and Check behavior

- Produce exactly two matching user-facing workbooks through the ordinary builder path. Keep source counts populated; Trainer practice cells start blank bright yellow without Notes; Answer-Key counterparts contain linked formulas and concise nonempty Notes, with no yellow anywhere.
- Maintain visible structure and typography parity, Aptos Narrow 11 non-bold black text, ordinary white/no-fill cells, and existing functional Check feedback. Keep formula instructions and answer hints exclusively in the Answer Key.
- Register every active store practice identity with independent expected-value lookup and workbook-wide Check; retain blank/correct/incorrect feedback without revealing answers, formulas or hints.
- Extend existing authenticated Check-context handling only as required for this schedule. Detect relevant source/context tampering while allowing intended learner edits; preserve frozen compatibility and pale-yellow rejection.

## Task 3 — Verify ordinary handoff and preservation

- Add `core/tests/test_operating_kpi_workbook.py`; exercise reconciliation → standardization → export/reload → reference model → Trainer/Answer Key → Check with existing source-bound store fixtures. Identify temporary fixture additions separately from supplied source facts.
- Independently verify counts `574/655/711/767/811`, net changes `None/81/56/56/44`, growth within `1e-12`, exact active identity coverage, formulas, Notes, styling and Check outcomes; cover sparse/singleton histories, missing inputs, zero denominators, declines, count-unit round trips and monetary-scale invariance.
- Verify absent/null/management-only parity, deterministic mapping, immutability, source tampering, and unchanged management/revenue-relationship APIs. Retain mixed-versus-annual-only standardized/statement-provenance/conflict parity and supplied-source counts: 135 observations (`29/36/37/33`), nine definitions, 107 market-table observations, three excluded targets, assessments `0/22/6/107`, 24 incompatible pairs, six singletons and zero revision links/selections.
- Use `/Users/lizhiguo/Documents/Developer/.venv/bin/python`; run focused workbook/Check/build-contract tests and the complete `core/tests` suite without deselections. Record actual commands, exit codes, counts and unavailable checks; distinguish injected cached-value verification from actual spreadsheet recalculation.
- Verify 50 protected artifacts against `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189`, and eight extractions against `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`.
- Record completion evidence, measured incremental practice counts, preservation hashes and remaining scope in `RESULT.md`; do not reserve prospective IDs.

## Acceptance and retained commitments

- The optional store schedule works through ordinary handoff and reload, with independently verified arithmetic, semantic practice, matched workbook mechanics and complete non-disclosing Check coverage. Existing non-KPI identities and expectations remain unchanged; count new KPI additions separately.
- Canonical generation succeeds. Retain parent temporary-build acceptance of success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; that exception does not satisfy this increment’s workbook acceptance.
- Preserve geographic 56 facts/74 additions, 486 prior identities/560 practice counterparts, 101 unavailable displays, 15 margin formulas, selected Americas `7928156`, audit-only `7928256`, signed bridges and semantic/source/availability controls; preserve Fast Retailing 577-cell coverage.
- Preserve 110 accepted additions, G1/G2/G3/G5 aliases, reformulation/provenance/ambiguity and causal-evidence gates, twelve pretax/ETR cases, sparse histories, partial interest closure and opening-only CoD `0.374`; invent no interest, zeros, lease repayments or deferred-tax interpretations.
- Preserve capex `638657/651865/689232/680802`, repurchase residuals `-116195/1085647/-207544/-256674`, NCIT `28555/15864/0/None`, Common stock `611/606/581/557`, and cash/inventory and liability/equity discrepancy explanations.
- Preserve unique evidenced compatible uncontradicted documentary direction, occurrence-specifically audited nonmissing reviser, complete-group membership, ambiguous incoming-candidate blocking and superseded audit evidence. Infer no chronology, transitive precedence or missing assurance; admit `2022-01-30` without inventing `2021-01-31`.
- Retain `20260916-075534-000000006` extraction/source binding and completed recovery evidence without restarting recovery. Additional identities, larger-group selection, general evidenced later-audited precedence, physical-page mapping and unavailable supplied evidence remain unfinished.
- Remaining Operating KPI scope includes management and revenue-relationship workbook integration, other supported revenue relationships, and geography/margin/inventory/working-capital/capex relationships; preserve semantic discontinuities and reported/statement-derived/analyst-derived distinctions without causal inference.
- Requests `20260914-193338-000000004` and `20260915-042248-000000005` retain normal five-stage commitments. Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1`, `9M.2.4`, publication and Step 9 remain unresolved.
- Retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED; Normalization Judgment/Earnings Normalization, G6 opening BS, G7 lease maturity/notes, G8 deferral, G9 standalone interest completeness, segment assets/capex/significant expenses/D&A, benchmark publication and TARGET exit gates remain pending.
- Preserve TARGET’s analytical focus gate; independent M&A Net Debt, Complete NOPAT/RNOA and forecasting remain deferred.
