# Step 9M.2.4.1.1.1.47 — Operating KPIs — Comparable management-history analytics

AUTOCYCLE_PLAN: {"baseline": "At e825ad48b9568171c10fe283c24bcb464560856a, Review accepted both-family selected-history handoff, round trips, stale-reference rejection and deferred exclusion. RESULT records 2111 required-suite passes. core/model/operating_kpi.py computes store-count analytics only; supplied inputs retain 135 reported observations and no selected management histories.", "finding_key": "management-kpi-history-analytics", "inputs": [], "kind": "work", "objective": "Compute comparable management-KPI historical analytics", "plan_id": "2a8e031ffc2e4246a58457438403b610", "step_id": "9M.2.4.1.1.1.47", "success": "Validated histories for both supported management families produce deterministic identity-specific reported series and adjacent-period changes, with explicit availability and comparability gates, preserved semantics and unchanged store analytics. Deferred supplied observations produce no management analytics.", "verification": "Read-only Review independently recomputes both-family analytics through ordinary handoff and export/reload, exercises gaps, semantic discontinuities, zero denominators and malformed inputs, and checks input immutability, supplied-data exclusion, recorded regression results and protected-artifact parity.", "work_id": "94231be671374d77a0b746a50168f1cf"}

## Scope and constraints

- Limit production changes to `core/model/operating_kpi.py` and an optional dedicated `core/model/management_kpi.py`; permit corresponding operating/management-KPI tests and `RESULT.md`.
- Consume validated `StandardizedFinancials` only. Preserve admission, identity, revision-selection, standardized serialization and reload contracts; do not broaden selection eligibility or supported identities.
- Preserve supplied JSON/PDFs, committed reconciliations, examples, releases, Fast Retailing data and checkpointed build-contract work. Use temporary fixtures/outputs; no re-extraction, company-specific pipeline, generic build redesign or AutoCycle changes.
- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, publication, forecasting or valuation; permissions remain binding.

## Task 1 — Compute both-family historical series

- Add a management-specific applicability function and computation API without changing the existing store-only applicability or series API. Validate supplied contracts before computing; absent/null/store-only inputs have no management module.
- Return deterministic series keyed by the existing full management identity, aligned to the canonical fiscal axis. Preserve each observation’s reported value, unit, definition, period kind, calendar fields and qualifiers; keep source/audit evidence outside model-facing outputs.
- For comparable-sales growth, retain signed reported percentages and compute adjacent-period percentage-point change as current minus prior; do not compute growth of a growth rate.
- For sales per square foot, retain reported `USD_per_square_foot`, compute adjacent absolute change and fractional growth `(current - prior) / prior`; use existing undefined-ratio behavior for a zero prior value. Apply no financial-statement monetary scaling.
- Permit comparisons only between immediately adjacent canonical periods with the same full identity and exactly matching definition text, period kind, calendar week adjustment, reporting basis and qualifier mappings. Do not normalize away differences or infer equivalence.
- Retain reported values across discontinuities but suppress dependent comparisons with `SOURCE_UNAVAILABLE` and explicit reasons distinguishing missing observations from semantic changes. Opening comparisons are `None`; never compress gaps, carry values forward or substitute periods.
- Distinguish reported measures from analyst-derived changes. Reject malformed inputs and noncanonical requested axes without mutation; do not infer revenue contributions, geographic allocation or causality.

## Task 2 — Verify arithmetic, gating and ordinary handoff

- Add independent arithmetic fixtures for both families, including negative/zero comparable growth, declining/zero sales per square foot, zero denominators, singleton and sparse histories, multiple supported identities sharing dates, and shuffled observations.
- Verify that each definition/calendar/qualifier discontinuity independently blocks comparisons while preserving reported values; equal qualifier mappings with different insertion order remain equivalent.
- Exercise bound-document admission → reconciliation → standardization → analytics and export/reload → analytics for both families. Check exact semantic preservation, deterministic results, input immutability and rejection of malformed histories.
- Verify absent/null/store-only/management-only/mixed behavior, deferred exclusion and unchanged store counts, changes and growth within `1e-12`. Supplied documents must still yield no management analytics.

## Task 3 — Verify preservation and record results

- Use `/Users/lizhiguo/Documents/Developer/.venv/bin/python`; run focused analytics tests, then required regressions without deselections.
- Required files under `core/tests/`: `test_management_kpi_reconciliation.py`, `test_management_kpi_identity.py`, `test_management_kpi_admission.py`, `test_management_kpi_history.py`, `test_operating_kpi_analysis.py`, `test_operating_kpi_facts.py`, `test_operating_kpi_management_history.py`, `test_filing_json.py`, `test_filing_reconciler.py`, `test_filing_cli.py`, `test_historical_segment.py`, `test_geographic_segment_facts.py`, `test_geographic_segment_analysis.py`, `test_geographic_segment_workbook.py`, `test_lululemon_benchmark.py`, `test_fast_retailing_benchmark.py`, `test_normalization.py`, `test_historical_v1_exit_gate.py`; include any new analytics test file.
- Verify temporary mixed-versus-annual-only standardized/statement-provenance/conflict parity: 135 observations (`29/36/37/33`), nine definitions, 107 market-table observations, three excluded targets, assessments `0/22/6/107`, 24 incompatible pairs, six singletons, zero revision links/selections and no supplied management history.
- Check 50 protected artifacts against `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189`, and eight extractions against `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`.
- Record commands, exit codes, measured counts, hashes, unavailable checks and remaining scope in `RESULT.md`; distinguish fresh evidence from retained results. Do not restart completed recovery or reserve prospective IDs.

## Acceptance and retained commitments

- Both management families expose correctly calculated, semantically gated historical analytics through the new API; unavailable comparisons remain unavailable and deferred observations never become analytical inputs.
- Preserve unique evidenced compatible uncontradicted documentary direction, occurrence-specifically audited nonmissing reviser, complete-group membership, ambiguous incoming-candidate blocking and superseded audit evidence. Infer no chronology, transitive precedence or missing assurance.
- Preserve store counts `574/655/711/767/811`, changes `None/81/56/56/44`, count-unit round trips and missing/gap/zero-denominator behavior; admit `2022-01-30` without inventing `2021-01-31`.
- Preserve geographic 56 facts/74 additions, 486 prior identities/560 practice counterparts, 101 unavailable displays, 15 margin formulas, selected Americas `7928156`, audit-only `7928256`, signed bridges and semantic/source/availability controls.
- Preserve two-workbook mechanics, blank yellow/no-Notes Trainer practice, formula/Notes white-or-no-fill Answer Key, non-disclosing Check, typography/visual parity, pale-yellow rejection, authenticated frozen compatibility and Fast Retailing 577-cell coverage.
- Preserve 110 accepted additions, G1/G2/G3/G5 aliases, reformulation/provenance/ambiguity and causal-evidence gates, twelve pretax/ETR cases, sparse histories, partial interest closure and opening-only CoD `0.374`; invent no interest, zeros, lease repayments or deferred-tax interpretations.
- Preserve capex `638657/651865/689232/680802`, repurchase residuals `-116195/1085647/-207544/-256674`, NCIT `28555/15864/0/None`, Common stock `611/606/581/557`, and cash/inventory and liability/equity discrepancy explanations.
- Canonical generation succeeds; retained parent temporary-build acceptance is success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. That exception does not satisfy this increment.
- Retain `20260916-075534-000000006` extraction/source binding, accepted analytics and completed recovery evidence. Additional identities, larger-group selection, general evidenced later-audited precedence, physical-page mapping and unavailable supplied evidence remain unfinished.
- Remaining Operating KPI scope: supported revenue/geography/margin/inventory/working-capital/capex relationships and ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.
- Requests `20260914-193338-000000004` and `20260915-042248-000000005` retain normal five-stage commitments. Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1`, `9M.2.4`, publication and Step 9 remain unresolved.
- Retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED; Normalization Judgment/Earnings Normalization, G6 opening BS, G7 lease maturity/notes, G8 deferral, G9 standalone interest completeness, segment assets/capex/significant expenses/D&A, benchmark publication and TARGET exit gates remain pending.
- Preserve the analytical focus gate; independent M&A Net Debt, Complete NOPAT/RNOA and forecasting remain deferred.
