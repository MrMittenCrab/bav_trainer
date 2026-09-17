# Step 9M.2.4.1.1.1.48 — Operating KPIs — Consolidated revenue and store-count growth relationship

AUTOCYCLE_PLAN: {"baseline": "At 169bfb3881931b717e0aa5f4a3d22982a815a986, Review accepted both-family management-history analytics, round trips, semantic gates and protected-artifact parity. RESULT records 2130 required-suite passes. Store-count analytics exist; revenue relationships remain unfinished. Supplied management inputs retain 135 observations and zero selections.", "finding_key": "operating-kpi-revenue-store-growth-relationship", "inputs": [], "kind": "work", "objective": "Compare consolidated revenue growth with store-count growth", "plan_id": "4238a5a8d65843e9b3eaf4c260601ce3", "step_id": "9M.2.4.1.1.1.48", "success": "A separate optional analytical API aligns consolidated revenue growth and company-operated period-end store-count growth, computes their explicitly descriptive percentage-point difference, and preserves availability, scope distinctions, existing analytics and deferred exclusion.", "verification": "Read-only Review independently recomputes revenue growth, store-count growth and their percentage-point difference through ordinary standardization and export/reload; checks missing and zero inputs, ambiguity rejection, scope labels, immutability, regression evidence and protected-artifact parity.", "work_id": "0b3dd54795ae40dea0c1511fe02479fb"}

## Scope and constraints

- Limit production changes to a new `core/model/operating_kpi_relationships.py`; permit corresponding relationship tests, necessary additions to existing KPI tests, and `RESULT.md`.
- Consume validated `StandardizedFinancials`; reuse canonical fiscal-axis, revenue resolver, store analytics and ratio conventions. Preserve existing APIs, admission, identities, revision selection and serialization.
- Preserve supplied JSON/PDFs, committed reconciliations, examples, releases, Fast Retailing data and checkpointed build-contract work. Use temporary fixtures/outputs; no re-extraction, company-specific pipeline, generic build redesign or AutoCycle changes.
- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, publication, forecasting or valuation; permissions remain binding.

## Task 1 — Add the bounded revenue/store relationship

- Add separate applicability and computation APIs requiring validated store-count observations. Absent/null/management-only histories have no relationship module; do not promote deferred management observations.
- Align reported consolidated revenue and period-end company-operated store counts to the canonical annual fiscal axis. Resolve revenue from income-statement lines with existing explicit-concept precedence and ambiguity rejection; retain currency and monetary-scale metadata.
- Calculate adjacent consolidated revenue growth `(current - prior) / prior`; reuse unchanged store-count growth. Calculate `100 * (revenue_growth - store_count_growth)` only when both growth values are numeric, labeling the result in percentage points.
- Label inputs as consolidated revenue and company-operated period-end store count, and calculations as analyst-derived. Explain that the difference compares distinct scopes and is not revenue attribution, same-store sales, store productivity, organic growth or causal evidence; derive no revenue-per-store ratio.
- Opening comparisons are `None`. Missing current/prior inputs suppress only dependent outputs with `SOURCE_UNAVAILABLE` and explicit reasons; zero denominators retain `UNDEFINED_RATIO` and propagate to the difference. Missing-input unavailability takes precedence when both conditions occur.
- Preserve reported zeros and declines; never compress gaps, substitute periods, annualize interim data or infer calendar adjustments. Reject malformed contracts, interim-only histories and noncanonical requested axes without mutation.

## Task 2 — Verify arithmetic and ordinary handoff

- Independently calculate positive, negative and zero growth, differing monetary scales, count units `stores`/`ones`, singleton and sparse histories, independently missing revenue/counts, zero denominators and mixed unavailable/undefined cases.
- Verify explicit revenue-concept precedence, ambiguous revenue rejection, malformed inputs, shuffled observations, axis rejection, deterministic results and input immutability. Assert scope labels and percentage-point units.
- Exercise filing reconciliation → standardization → relationship analytics and standardized export/reload → analytics using temporary source-grounded store fixtures and existing revenue statements. Compare numeric outputs within `1e-12`.
- Verify absent/null/management-only/mixed behavior; preserve both management-family analytics and store counts `574/655/711/767/811`, changes `None/81/56/56/44`. Supplied deferred documents alone must not activate management analytics or this relationship.

## Task 3 — Verify preservation and record measured results

- Use `/Users/lizhiguo/Documents/Developer/.venv/bin/python`; run focused relationship/KPI tests, then required regressions without deselections.
- Required files under `core/tests/`: `test_management_kpi_reconciliation.py`, `test_management_kpi_identity.py`, `test_management_kpi_admission.py`, `test_management_kpi_history.py`, `test_management_kpi_analysis.py`, `test_operating_kpi_analysis.py`, `test_operating_kpi_facts.py`, `test_operating_kpi_management_history.py`, `test_filing_json.py`, `test_filing_reconciler.py`, `test_filing_cli.py`, `test_historical_segment.py`, `test_geographic_segment_facts.py`, `test_geographic_segment_analysis.py`, `test_geographic_segment_workbook.py`, `test_lululemon_benchmark.py`, `test_fast_retailing_benchmark.py`, `test_normalization.py`, `test_historical_v1_exit_gate.py`; include new relationship tests.
- Verify temporary mixed-versus-annual-only standardized/statement-provenance/conflict parity: 135 observations (`29/36/37/33`), nine definitions, 107 market-table observations, three excluded targets, assessments `0/22/6/107`, 24 incompatible pairs, six singletons, zero revision links/selections and no supplied management history.
- Check 50 protected artifacts against `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189`, and eight extractions against `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`.
- Record commands, exit codes, measured counts, hashes, unavailable checks and remaining scope in `RESULT.md`; distinguish fresh evidence from retained results. Do not restart completed recovery or reserve prospective IDs.

## Acceptance and retained commitments

- The separate API produces independently verified revenue/store growth comparisons through ordinary handoff and reload; missing/undefined results propagate correctly, scope distinctions remain explicit, and existing analytics and protected artifacts remain unchanged.
- Preserve unique evidenced compatible uncontradicted documentary direction, occurrence-specifically audited nonmissing reviser, complete-group membership, ambiguous incoming-candidate blocking and superseded audit evidence. Infer no chronology, transitive precedence or missing assurance.
- Preserve count-unit round trips and missing/gap/zero-denominator behavior; admit `2022-01-30` without inventing `2021-01-31`.
- Preserve geographic 56 facts/74 additions, 486 prior identities/560 practice counterparts, 101 unavailable displays, 15 margin formulas, selected Americas `7928156`, audit-only `7928256`, signed bridges and semantic/source/availability controls.
- Preserve two-workbook mechanics, blank yellow/no-Notes Trainer practice, formula/Notes white-or-no-fill Answer Key, non-disclosing Check, typography/visual parity, pale-yellow rejection, authenticated frozen compatibility and Fast Retailing 577-cell coverage.
- Preserve 110 accepted additions, G1/G2/G3/G5 aliases, reformulation/provenance/ambiguity and causal-evidence gates, twelve pretax/ETR cases, sparse histories, partial interest closure and opening-only CoD `0.374`; invent no interest, zeros, lease repayments or deferred-tax interpretations.
- Preserve capex `638657/651865/689232/680802`, repurchase residuals `-116195/1085647/-207544/-256674`, NCIT `28555/15864/0/None`, Common stock `611/606/581/557`, and cash/inventory and liability/equity discrepancy explanations.
- Canonical generation succeeds; retained parent temporary-build acceptance is success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. That exception does not satisfy this increment.
- Retain `20260916-075534-000000006` extraction/source binding, accepted analytics and completed recovery evidence. Additional identities, larger-group selection, general evidenced later-audited precedence, physical-page mapping and unavailable supplied evidence remain unfinished.
- Remaining Operating KPI scope includes other supported revenue relationships, geography/margin/inventory/working-capital/capex relationships and ordinary BAV/Trainer/Answer-Key/Check integration; preserve semantic discontinuities and distinguish reported, statement-derived and analyst-derived measures without causal inference.
- Requests `20260914-193338-000000004` and `20260915-042248-000000005` retain normal five-stage commitments. Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1`, `9M.2.4`, publication and Step 9 remain unresolved.
- Retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED; Normalization Judgment/Earnings Normalization, G6 opening BS, G7 lease maturity/notes, G8 deferral, G9 standalone interest completeness, segment assets/capex/significant expenses/D&A, benchmark publication and TARGET exit gates remain pending.
- Preserve the analytical focus gate; independent M&A Net Debt, Complete NOPAT/RNOA and forecasting remain deferred.
