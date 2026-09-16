# Step 9M.2.4.1.1.1.36 — Operating KPIs: reported-label provenance validation

AUTOCYCLE_PLAN: {"baseline": "At 5eface243254ee261ef5ab9403dd0c70297b459d, geographic workbook integration is accepted with 560 practice counterparts. G7 store KPIs remain unresolved; supplied FY2022 and FY2023 reports disclose total company-operated stores of 574, 655 and 711, while no dedicated operating-KPI model contract exists.", "finding_key": "operating-kpi-store-history-missing-source-to-model-handoff", "inputs": [], "kind": "work", "objective": "Establish validated historical company-operated store inputs", "plan_id": "fc6cf3a69853493a8a54b0550e0a98d8", "step_id": "9M.2.4.1.1.1.36", "success": "Supplied Lululemon store disclosures pass per-filing JSON validation, deterministic reconciliation and StandardizedFinancials JSON reload as optional, explicitly unit-qualified historical store counts, with independently verified provenance and unchanged protected artifacts.", "verification": "Independently inspect serialized KPI provenance mutations through production filing validation and reconciliation, verify rejection without mutation, reconstruct selected store observations and standardized JSON reload in both filing orders, retain cited PDF-table evidence, exercise invalid-unit/conflict/missing-data controls, inspect regression evidence and compare all protected hashes with both required checkpoints.", "work_id": "0a6a4585ec404220aa91d71fc7439eb6"}

## Scope and constraints

- Repair the existing work `0a6a4585ec404220aa91d71fc7439eb6`; preserve its original source-to-model acceptance criteria.
- Permitted edits: `core/data/historical_operating_kpis.py`, narrowly necessary KPI validation integration under `core/ingestion/`, focused existing tests under `core/tests/`, and `RESULT.md`.
- Preserve source PDFs, extracted JSON, canonical reconciled artifacts, Fast Retailing data, releases and committed examples. All 50 protected artifacts must match `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189`; augmented filings and builds use temporary destinations.
- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, publication, forecasting or valuation; execution remains subject to available permissions.
- Reuse completed source transcription, fixtures and preparation helper. Do not restart completed recovery or extend into KPI analytics, workbook practice or Check integration.

## Task 1 — Enforce reported-label provenance

- Require every operating-KPI supplemental fact to have a string `source.label` containing non-whitespace text in `validate_operating_kpi_fact`; identify the missing reported label in validation errors.
- A populated `source.note` must not substitute for the reported label. Preserve supplied note context and label text through serialization and audit selection; do not synthesize provenance from metric identity.
- Apply the shared contract through production filing validation and reconciliation, including superseded observations. Keep the requirement scoped to KPI facts; preserve non-KPI behavior and the separation of model inputs from audit provenance.

## Task 2 — Prove rejection at production boundaries

- Extend `core/tests/test_operating_kpi_facts.py` and relevant filing JSON/reconciliation tests with omitted, empty and whitespace-only labels, each with populated and absent note context. Include the exact review reproduction removing both fields from an otherwise valid serialized store observation.
- Reload serialized mutations and assert production filing validation reports failure; reconciliation must reject invalid filings. Exercise reconciliation's shared fact validation independently with a previously valid report and a subsequently invalid KPI fact.
- Verify unchanged inputs and no partial output on rejection. Add positive controls for valid labels, preserved supplied notes, legacy absent/null KPI payloads and unrelated supplemental facts.

## Task 3 — Verify retained handoff and record evidence

- Reuse source-grounded temporary augmented filings to validate, reconcile, standardize and reload standardized JSON in forward and reversed filing orders. Require selected counts `574/655/711/767/811`, explicit stores/ones units, retained reported labels and note context in audit artifacts, and unchanged 56 geographic facts.
- Run `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest` with `core/tests/test_operating_kpi_facts.py`, `test_filing_json.py`, `test_filing_reconciler.py`, `test_filing_cli.py`, `test_historical_segment.py`, `test_geographic_segment_facts.py`, `test_geographic_segment_analysis.py`, `test_geographic_segment_workbook.py`, `test_lululemon_benchmark.py`, `test_fast_retailing_benchmark.py`, `test_normalization.py` and `test_historical_v1_exit_gate.py` under `core/tests/`; include additionally affected modules.
- Record measured rejection cases, positive round trips, commands/results and protected-hash comparisons in `RESULT.md`. Correct the prior unsupported missing-provenance acceptance claim; distinguish fresh verification from retained PDF evidence and report unavailable checks.

## Acceptance and retained commitments

- Production processing accepts verified store histories without company-specific selection. Missing or blank reported labels fail through filing validation and reconciliation, including when note context is present; invalid contracts fail without mutation.
- Retain all original value/date/identity/unit/duplicate/conflict controls, deterministic precedence, duplicate-source provenance and superseded observations. Missing data remains unavailable; legacy absent/null and sparse histories remain supported.
- Preserve filing hashes, physical pages, exact fiscal dates, current/comparative roles and company-operated population definitions. Counts remain independent of monetary scale; no licensed-location, outlet or geographic substitutions.
- Require model-axis membership and unique metric/population/period keys; retain the accepted temporary admission of `2022-01-30` without synthesizing `2021-01-31` balance-sheet data. Keep source evidence outside model-facing KPI payloads.
- Preserve geographic acceptance: 56 selected facts, 74 additions, 486 prior identities, 560 practice counterparts, 101 unavailable displays, 15 margin formulas, selected Americas revenue `7928156`, superseded `7928256` only in audit evidence, signed bridges and availability/semantic/source controls.
- Preserve exactly two user-facing workbooks, blank yellow/no-Notes Trainer practice, formula/Notes white-or-no-fill Answer Key with no yellow, non-disclosing Check, minimal typography and visual parity; retain pale-yellow rejection, authenticated frozen compatibility and Fast Retailing 577-cell coverage.
- Preserve accepted 110 additions, G1/G2/G3/G5 aliases, reformulation/provenance/ambiguity gates, historical causal evidence, twelve pretax/ETR cases, sparse and zero-denominator behavior, partial interest closure and opening-only CoD `0.374`; invent no interest, zeros, lease repayments or deferred-tax interpretations.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences and liability/equity discrepancy explanations.
- Parent temporary-build acceptance remains success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds. This exception does not satisfy KPI acceptance.
- Preserve pending requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; parent acceptance and publication remain unfinished.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, five snapshot-matched edit identities, historical batch, recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, and hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1`, `9M.2.4` remain unresolved; retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED.
- Remaining scope: KPI analytics/workbook/Check and other source-supported KPIs; Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication and TARGET Step 9 exit gates. Retain the analytical focus gate; defer independent M&A Net Debt, Complete NOPAT/RNOA and forecasting. Claim no spreadsheet recalculation or broader Operating KPIs completion.
