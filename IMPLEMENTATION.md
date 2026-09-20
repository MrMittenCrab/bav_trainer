# Step 3.2.8 — Require affirmative agreement for repeated management disclosures

AUTOCYCLE_PLAN: {"finding_key": "Complete real-source Lululemon KPI production acceptance", "kind": "work", "minor": 8, "objective": "Require affirmative agreement for repeated management disclosures", "plan_id": "64e2a5cb1c96448a94587974e055eed1", "step_id": "3.2.8", "work_id": "6743e8167c864555b33c54efb3c41328"}

## Completion

The ordinary source-bound Lululemon build delivers verified historical Revenue per Store for supported periods and resolves Comparable Sales/SPSF admission from supplied evidence, activating supported analysis and documenting precise source gaps otherwise, with matching BAV formulas/Notes, Trainer practices, Check and required Excel verification.

## Bounded work

- Repair `_ordinary_agreement_reasons` in `core/ingestion/management_kpi_reconciliation.py` so repeated ordinary disclosures require affirmative agreement across every occurrence on value, relevant identity, definition, population, units, currency basis and calendar semantics.
- Missing population, unit, basis, `calendar_week_adjustment` or `calendar_reporting_basis` on any member must defer the complete group with dimension-specific reasons. Absence on every member is not agreement. Apply existing evidence normalization and relevance rules; do not infer evidence from another occurrence or treat empty values as not applicable.
- Keep the repair local to ordinary repeated-disclosure admission. Preserve conflict-only helper semantics where other callers intentionally distinguish missing evidence from contradiction.
- Select a deterministic representative only after complete-group agreement succeeds. Preserve every occurrence and provenance; do not select a convenient subset or silently prefer a later filing.
- Preserve supported singleton admission, actual assurance labels, audited documentary-revision gates and rejection of unresolved incoming or intra-group revisions through the ordinary route.
- Keep canonical selection, occurrence admission and historical comparison eligibility independent. Preserve definition, population, currency, fiscal-calendar, metric-exclusion, comparison-window and pair-specific requirements.
- Recompute selection from bound evidence through admission and model handoff. Deferred repeats must not reach `StandardizedFinancials`; retain stale/tampered-selection rejection and unique identity-period transfer through export/reload.

## Verification

- Add missing-evidence regressions for both management-KPI families: remove each relevant dimension independently from either repeat member and from all members; cover absent, null and blank evidence, reversed occurrence order, and a larger group with one incomplete member.
- Reproduce the reviewed defect using the real selected 2024 SPSF repeat group. Each individual removal of population, unit, basis, calendar adjustment or calendar reporting evidence must defer selection with the corresponding reason; the intact group must remain selected.
- Retain positive agreeing-repeat and singleton cases, deterministic representative selection, conflicting-group rejection, assurance preservation, revision-route safeguards and tampered-handoff coverage. Verify missing-evidence deferral survives admission and standardized export/reload.
- Run affected reconciliation, identity, admission, enrichment and model-handoff regressions, then `python -m bav build Lululemon`. Compare all 28 decisions against the accepted 27 selected / one deferred baseline. Preserve supported coverage; investigate any change against bound evidence rather than forcing counts.
- Preserve 24 admitted Comparable Sales facts, three SPSF levels and five Revenue per Store observations where their evidence remains sufficient. Keep Build Status, CLI, formulas and Notes consistent with actual coverage and precise unavailable reasons.
- Verify the regenerated BAV, explicit Trainer derivation and workbook-wide Check: populated source facts and BAV formulas/Notes, no BAV yellow cells or exercise framing, blank-yellow Trainer practices without comments or answer leakage, unchanged primary artifacts, and blank/correct/incorrect Check behavior. Run affected workbook/build regressions and Lululemon/Fast Retailing benchmarks.
- Carry forward accepted Excel evidence from `.git/autocycle/excel-verification-ti974vnt/` and `.git/autocycle/excel-verification-kzg9a_ex/`, including retained snapshots and independent references. Confirm corresponding formulas, literal inputs and dependencies remain unchanged; packaging-only differences do not require replay.
- Obtain native Excel recalculation and independent saved-cache verification only for changed formulas, inputs or dependencies. Preserve formula/input checks, ownership, access and recovery guards.
- Verify all 50 protected artifacts and eight source extracts against existing authenticated baselines without replacing them.
- Append measured repair results, regression commands, group/pair outcomes, model coverage, workbook/Trainer/Check results, retained or new Excel evidence, output paths/hashes and remaining requirements to `RESULT.md`. Leave historical records intact; distinguish this repair from parent Completion and the Session Endpoint.

## Preserved evidence and boundaries

- Preserve FY2022 physical page 37 / printed page 33 presentation bindings across all four identities, separate management-use and definition locators, and store-only versus stores-plus-DTC populations.
- Preserve all 39 pair assessments, five supported historical SPSF comparisons, seven SPSF occurrence calendars, three traced priors and presentation roles. Retain FY2022 calendar evidence from FY2023 physical page 33 and both FY2024 exclusion bindings to physical page 40 / printed page 34 with cross-filing provenance.
- Keep fiscal-year length, metric exclusion and observed comparison windows separate. Preserve FY2022 definition disagreement and FY2024 exclusion/calendar failures on their correct pairs; unsupported historical comparisons and the undated FY2021 SPSF observation remain documented gaps.
- Preserve Revenue per Store denominator distinctions, period alignment, scaling, missing/zero-input behavior and total-company-revenue scope limitation.
- Modify permitted working copies and regenerate outputs through the ordinary pipeline. Preserve protected PDFs, extracts, benchmarks, original observations, conflicts, superseded occurrences and deferred groups; synthetic fixtures are regression evidence only.
- Preserve accepted accounting, ingestion, geographic, store-count, normalization and provenance behavior; `SEGMENT_BRIDGE_TOLERANCE = 0.0`; inactive provisional normalization judgments; primary metadata, derivative-output contracts, Trainer sanitization, non-disclosing Check, atomic publication, protected-path checks and invalid-source rejection.
- Missing evidence, unavailable access and unresolved human decisions remain explicit. Do not invent evidence or reopen accepted work solely because documented unsupported comparisons remain.
- Disclosure-led historical driver testing and strategy interpretation remain subsequent Session work. Earlier normalization, broader source-workflow and normalized-per-share commitments retain their deferred evidence and unresolved decisions.
- No forecasting, valuation, scenarios, forward assumptions, investment conclusions or unrelated infrastructure/cosmetic expansion.
- Cursor must not modify `TARGET.md`, `SESSION.md` or `IMPLEMENTATION.md`.
