# Step 9M.2.4.1.1.1.35 — Geographic segment workbook schedules and learner/Check integration

AUTOCYCLE_PLAN: {"baseline": "At 3f6f5dde023847e3347a4c830d822614a28c81a9, geographic analysis is verified against 56 selected facts across five periods; 50 protected artifacts match, but segment workbook schedules and learner/Check integration remain absent.", "finding_key": "validated-geographic-series-missing-workbook-learner-check-integration", "inputs": [], "kind": "work", "objective": "Integrate historical geographic economics into the Trainer and Answer Key", "plan_id": "d70d43236d564997bc6ef217814ee918", "step_id": "9M.2.4.1.1.1.35", "success": "A temporary matched Trainer and Answer Key expose source-supported geographic schedules, semantic formula practice and non-disclosing Check using the validated analytical series; existing practice and protected artifacts remain intact.", "verification": "Inspect integration and independently compare a five-period JSON-reloaded Lululemon temporary workbook pair, component identities and Check results against selected facts and the analytical API; run focused integration and existing trainer/benchmark regressions; compare protected hashes to the checkpoint and inspect measured RESULT.md evidence.", "work_id": "65d8d6e9a2f94bb398cace9a2f361b28"}

## Scope

- One bounded historical module: geographic revenue mix, adjacent-period growth, reported operating margins and consolidated bridges.
- Modify `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/checker.py`; modify `core/trainer/check_context.py` and `core/trainer/workbook.py` only where integration requires it. Add `core/tests/test_geographic_segment_workbook.py`; record evidence in `RESULT.md`.
- Reuse `core/model/geographic_segment.py` and existing validated contracts, availability, semantic mapping and workbook conventions; preserve extraction, reconciliation, serialization and separate audit evidence.
- Source PDFs, extracted JSON, canonical reconciled artifacts, releases and all Fast Retailing data remain byte-identical to `3f6f5dde023847e3347a4c830d822614a28c81a9`. Generate test workbooks only in permitted temporary storage.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, publication, forecasting or valuation.

## Task 1 — Build the optional reference schedule

- Gate the schedule on validated `historical_segment`; absent/null payloads add no schedule or practice, and invalid supplied contracts fail closed without input mutation.
- Populate selected segment revenue/profit, consolidated amounts and reconciling facts with dates, units and stable Americas, China Mainland and Rest of World labels; keep audit paths, hashes, pages, observations and conflicts outside the model.
- Build linked Excel formulas for revenue mix, adjacent-period growth, reported operating margins, calculated segment totals, signed bridge contributions, reconstructed consolidated operating profit and differences against reported consolidated amounts.
- Preserve both presentation families and explicit ADD/SUBTRACT semantics without corporate double counting. Distinguish calculated totals from reported totals and reported operating margin from BAV NOPAT margin.
- Preserve canonical period alignment, opening-growth absence, sparse-period dependency unavailability, zero-denominator undefined ratios, reported zeros and negative profits; do not compress gaps or infer missing reconciling zeros.

## Task 2 — Connect learner practice and Check

- Register available calculations by stable family, segment/bridge identity and fiscal period; preserve existing component identities and expected values. Source literals and system-controlled links remain populated.
- Produce exactly one temporary Trainer and matching Answer Key with visual parity and existing TARGET styling. Active Trainer practice starts blank yellow without answers or Notes; corresponding Answer-Key cells contain formulas and concise non-empty Notes.
- Derive Check expectations from the validated analytical series; register every active segment practice cell and exclude unavailable displays and absent opening growth.
- Verify blank/correct/incorrect feedback is yellow/green/red and Check discloses no answers, formulas or hints. Preserve existing semantic relocation and source-edit controls.
- Notes explain mix, growth, reported margins and bridge arithmetic without unsupported causal claims.

## Task 3 — Verify and record

- Reconcile unchanged Lululemon filings in memory with `2022-01-30` admitted, export and reload actual JSON, then build the temporary pair through the existing generation path.
- Independently verify all five periods against selected facts: ratios within `1e-12`, monetary bridge differences exactly zero, including `3607682 - 1397067 = 2210615`; verify formula references and bridge operations rather than only cached values.
- Test both presentation families, sparse periods, absent/null payloads, undefined ratios, reordered inputs, invalid-contract failure immutability, semantic relocation and blank/correct/incorrect Check without disclosure. Verify populated source facts and Answer-Key-only Notes.
- Run `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_analysis.py core/tests/test_historical_segment.py core/tests/test_trainer.py core/tests/test_reference_integrity.py core/tests/test_source_availability.py core/tests/test_learner_ready_presentation.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py -q`.
- Record commands, interpreter, measured new component counts, preserved existing identities/expectations, independent calculations, Check outcomes and all 50 protected-file hash comparisons in `RESULT.md`. Separate fresh evidence from retained 144-test implementation evidence and restricted Review reruns; access failures are not passes. Claim spreadsheet recalculation only if actually performed.

## Retained acceptance and unfinished obligations

- Preserve Lululemon five-period history, existing 486 identities/expectations, 101 unavailable displays and accepted 110 additions; report geographic additions separately. Fast Retailing remains byte-identical at 577 identities and zero unavailable displays.
- Preserve Q4-2023 definitions, China Mainland identity, currency/units, strict dates/finite values, unique keys, model-axis membership, complete bridges and consolidated IS agreement; all 56 selected values survive reload. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence.
- No invented facts, inferred zeros, missing-period substitution, inferred week adjustments, channel/country/product substitution or unsupported causal explanations.
- Retain G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, deterministic mapping and original-row provenance.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls and failure immutability.
- Preserve partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution and distinct tax expense; no invented interest, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference or deferred-tax expense/recoverability claims.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / reported 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences, reformulation tolerances and liability/equity discrepancy explanations.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds. This exception does not establish geographic workbook integration acceptance.
- Preserve pending benchmark-improvement and parent-acceptance obligations for requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; do not restart completed publication recovery.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, five snapshot-matched edit identities, historical batch, recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, and hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; distinguish original success, resumed wrapper failures and fresh evidence.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1` and `9M.2.4` remain unresolved; A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED remain distinct.
- Remaining scope: G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; segment assets/capex, significant-expense schedules and D&A; benchmark publication and all TARGET Step 9 exit gates. This integration does not close parent or TARGET acceptance.
