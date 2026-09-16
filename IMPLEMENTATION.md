# Step 9M.2.4.1.1.1.36 — Operating KPIs: reject serialized non-string provenance labels

AUTOCYCLE_PLAN: {"baseline": "At 5eface243254ee261ef5ab9403dd0c70297b459d, geographic workbook integration is accepted with 560 practice counterparts. G7 store KPIs remain unresolved; supplied FY2022 and FY2023 reports disclose total company-operated stores of 574, 655 and 711, while no dedicated operating-KPI model contract exists.", "finding_key": "operating-kpi-store-history-missing-source-to-model-handoff", "inputs": [], "kind": "work", "objective": "Establish validated historical company-operated store inputs", "plan_id": "f88e276677ac468fb5d6ef063a35d003", "step_id": "9M.2.4.1.1.1.36", "success": "Supplied Lululemon store disclosures pass per-filing JSON validation, deterministic reconciliation and StandardizedFinancials JSON reload as optional, explicitly unit-qualified historical store counts, with independently verified provenance and unchanged protected artifacts.", "verification": "Independently exercise serialized non-string KPI labels through production loading, validation and reconciliation; verify rejection before coercion without mutation or partial output, unchanged non-KPI behavior, valid five-period standardized JSON reload in both filing orders, cited PDF provenance, invalid-unit/conflict/missing-data controls and all 50 protected hashes against both required checkpoints.", "work_id": "0a6a4585ec404220aa91d71fc7439eb6"}

## Scope and constraints

- Continue work `0a6a4585ec404220aa91d71fc7439eb6` under its existing step; retain original source-to-model acceptance.
- Permitted edits: `core/ingestion/filing_json.py`, narrowly necessary KPI validation integration under `core/ingestion/`, `core/data/historical_operating_kpis.py`, focused existing tests under `core/tests/`, and `RESULT.md`.
- Preserve source PDFs, extracted JSON, canonical reconciled artifacts, Fast Retailing data, releases and committed examples. All 50 protected artifacts must match `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189`; use temporary destinations for augmented filings and builds.
- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, publication, forecasting or valuation; execution remains subject to available permissions.
- Reuse completed transcription, fixtures and preparation helper; do not restart recovery or extend into KPI analytics, workbook practice or Check integration.

## Task 1 — Validate raw KPI labels before coercion

- At supplemental JSON parsing, reject non-string operating-KPI `source.label` values before `_parse_source` can stringify them. Apply the guard wherever KPI supplemental facts are parsed, using the existing KPI classifier and shared contract where appropriate.
- Retain object-level validation and rejection of omitted, null, empty and whitespace-only labels, including superseded observations. Errors must identify the KPI reported-label defect; populated notes cannot substitute.
- Preserve valid label text and supplied notes exactly. Keep existing non-KPI source parsing and validation behavior, with audit provenance separate from model inputs.

## Task 2 — Exercise serialized and object-level rejection

- Extend `test_filing_json.py`, `test_operating_kpi_facts.py`, `test_filing_reconciler.py` and, as necessary, `test_filing_cli.py` with serialized labels `123`, `1.5`, `0`, `true`, `false`, nonempty/empty objects and nonempty/empty arrays, with populated and absent notes.
- Assert production loading rejects malformed types before creating accepted provenance; validation/reconciliation entry paths must fail closed with no partial artifacts or input mutation. Record parser rejection distinctly from validation-report rejection.
- Independently exercise shared reconciliation validation using malformed in-memory KPI facts after a previously valid report, including superseded observations. Retain omitted/null/blank cases and the reproduction removing both label and note.
- Add positive controls for exact valid-label/note preservation, unchanged non-KPI coercion and optional-label behavior, and legacy absent/null KPI payloads.

## Task 3 — Verify retained handoff and record measured evidence

- Validate, reconcile, standardize and reload temporary source-grounded filings in both orders; require `574/655/711/767/811`, explicit stores/ones units, retained audit labels/notes and 56 geographic facts. Retain independently inspected PDF-table evidence without claiming a fresh transcription.
- Run `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest` on `core/tests/test_operating_kpi_facts.py`, `test_filing_json.py`, `test_filing_reconciler.py`, `test_filing_cli.py`, `test_historical_segment.py`, `test_geographic_segment_facts.py`, `test_geographic_segment_analysis.py`, `test_geographic_segment_workbook.py`, `test_lululemon_benchmark.py`, `test_fast_retailing_benchmark.py`, `test_normalization.py` and `test_historical_v1_exit_gate.py` under `core/tests/`, plus additionally affected modules.
- Record commands, measured outcomes, rejection boundaries, round trips and protected-hash comparisons in `RESULT.md`; correct the prior incomplete string-label acceptance claim and distinguish fresh checks, retained evidence and unavailable checks.

## Acceptance and retained commitments

- Non-string serialized KPI labels cannot become accepted strings. Valid source-grounded store histories pass production boundaries without company-specific selection; malformed contracts fail without mutation or partial output, and non-KPI behavior is unchanged.
- Retain value/date/identity/unit/duplicate/conflict controls, deterministic precedence, duplicate-source provenance and superseded observations. Missing data remains unavailable; legacy absent/null and sparse histories remain supported.
- Preserve filing hashes, physical pages, exact fiscal dates, current/comparative roles and company-operated population definitions. Counts remain independent of monetary scale; no licensed-location, outlet or geographic substitutions.
- Require model-axis membership and unique metric/population/period keys; retain temporary admission of `2022-01-30` without synthesizing `2021-01-31` balance-sheet data. Keep source evidence outside model-facing KPI payloads.
- Preserve geographic acceptance: 56 selected facts, 74 additions, 486 prior identities, 560 practice counterparts, 101 unavailable displays, 15 margin formulas, Americas revenue `7928156`, superseded `7928256` only in audit evidence, signed bridges and availability/semantic/source controls.
- Preserve exactly two user-facing workbooks, blank yellow/no-Notes Trainer practice, formula/Notes white-or-no-fill Answer Key without yellow, non-disclosing Check, minimal typography and visual parity; retain pale-yellow rejection, authenticated frozen compatibility and Fast Retailing 577-cell coverage.
- Preserve accepted 110 additions, G1/G2/G3/G5 aliases, reformulation/provenance/ambiguity gates, historical causal evidence, twelve pretax/ETR cases, sparse and zero-denominator behavior, partial interest closure and opening-only CoD `0.374`; invent no interest, zeros, lease repayments or deferred-tax interpretations.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences and liability/equity discrepancy explanations.
- Parent temporary-build acceptance remains success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds. This exception does not satisfy KPI acceptance.
- Preserve pending requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; parent acceptance and publication remain unfinished.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, five snapshot-matched edit identities, historical batch, recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, and hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1`, `9M.2.4` remain unresolved; retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED.
- Remaining scope: KPI analytics/workbook/Check and other source-supported KPIs; Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication and TARGET Step 9 exit gates. Retain the analytical focus gate; defer independent M&A Net Debt, Complete NOPAT/RNOA and forecasting. Claim no spreadsheet recalculation or broader Operating KPIs completion.
