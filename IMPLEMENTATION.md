# Step 3.2 — Complete real-source Lululemon KPI production acceptance
AUTOCYCLE_PLAN: {"finding_key": "Complete real-source Lululemon KPI production acceptance", "kind": "work", "objective": "Complete real-source Lululemon KPI production acceptance", "plan_id": "ad722ab097464605aea2eb97d0d0f911", "step_id": "3.2", "work_id": "6743e8167c864555b33c54efb3c41328"}

## Completion

The ordinary source-bound Lululemon build delivers verified historical Revenue per Store for supported periods and resolves Comparable Sales/SPSF admission from supplied evidence, activating supported analysis and documenting precise source gaps otherwise, with matching BAV formulas/Notes, Trainer practices, Check and required Excel verification.

## Implementation

- Inspect supplied Lululemon filings, management documents and admission evidence for Comparable Sales and SPSF. Trace each candidate through extraction, validation, reconciliation and model admission; distinguish missing evidence from an implementation defect.
- Admit supported observations through the existing source-bound pipeline, preserving page-level provenance, fiscal periods, units, population, geography, reported/constant-currency basis, definitions and comparability. Repair only demonstrated extraction or admission defects; do not bypass documentary requirements or promote unreconciled observations automatically.
- Where supplied materials cannot support admission, record the documents/pages searched, exact unmet requirements and additional evidence required. Keep explicit unavailable states for affected identities and periods; continue supported Revenue per Store work.
- Implement generic historical Revenue per Store calculations using admitted revenue and company-operated store history. Specify fiscal-period alignment, monetary scaling and denominator basis. Label period-end or average-store denominators explicitly; require the necessary admitted observations and never silently substitute between them.
- Explain that total-company revenue divided by company-operated stores includes revenue outside those stores and is not store-only productivity, SPSF or comparable sales. Preserve unavailable and undefined results for missing, incompatible or zero-denominator inputs.
- Integrate Revenue per Store through reference calculations, semantic families/components, formula dependencies, workbook schedules, useful analytical Notes, Trainer derivation, historical expected values and workbook-wide Check. Reuse established KPI mechanisms.
- Replace the hardcoded inactive Revenue per Store entry in `core/build_status.py` with evidence-based availability. Build Status, CLI and emitted schedules must agree; Comparable Sales Analysis, Sales per Square Foot Analysis and Revenue per Store Analysis must be Active wherever supplied evidence supports them, with partial coverage and limitations visible.
- Keep source extraction separate from analytical judgment. Use permitted working copies and generated outputs; do not overwrite protected source extracts or benchmark artifacts.

## Verification

- Run `python -m bav build Lululemon` through the ordinary supplied-source pipeline. Verify the professional BAV builds independently, reloads successfully and exposes the supported KPI schedules and accurate availability.
- Independently reconcile admitted KPI facts to source evidence and compare new calculations with reference results, including fiscal alignment, monetary scaling and denominator scope.
- Verify standardized export/reload, embedded and sidecar semantic maps, populated source facts, correct BAV formulas and non-empty Notes, with no yellow cells or exercise framing.
- Explicitly derive the matching Trainer. Confirm the BAV and primary sidecars remain unchanged, new active practices are blank yellow without comments or answer leakage, and source facts remain populated.
- Exercise workbook-wide Check on blank, correctly completed and deliberately incorrect KPI practices without disclosing answers.
- Perform actual Excel recalculation for the new analytical formulas and affected dependencies; inspect recalculated values and errors against reference results. Record unavailable access as an unresolved verification blocker, not a pass.
- Add focused regressions for admission outcomes, supported Revenue per Store periods, missing/incompatible inputs and production integration. Run affected KPI, ingestion, workbook, semantic-map, Check and build regressions, plus Lululemon and Fast Retailing checks.
- Verify the 50 protected artifacts and eight source extracts against existing authenticated baselines; do not replace baselines with current outputs.
- Record measured results, commands, generated paths, source-admission decisions, Build Status and outstanding evidence/access gaps in `RESULT.md`.

## Boundaries and retained commitments

- Preserve accepted accounting, ingestion, geographic, store-count, KPI, normalization, provenance and workbook behavior, including fail-closed admission, `SEGMENT_BRIDGE_TOLERANCE = 0.0` and inactive provisional normalization judgments.
- Preserve independent BAV generation, supported paired-output contracts, primary metadata, Trainer sanitization, non-disclosing Check, atomic publication, protected-path checks and invalid-source rejection.
- Synthetic fixtures may verify generic behavior but cannot establish real-company production acceptance.
- Disclosure-led historical driver testing and evidence-backed strategy interpretation remain subsequent Session work; distinguish disclosures, source facts, accounting identities, observed relationships and inference.
- Earlier normalization, broader source-workflow, normalized-per-share and real-company acceptance commitments remain deferred with their ledger evidence and unresolved decisions preserved.
- No forecasting, valuation, scenarios, forward assumptions, investment conclusions or unrelated infrastructure and cosmetic expansion.
- Cursor must not modify `TARGET.md`, `SESSION.md` or `IMPLEMENTATION.md`.
