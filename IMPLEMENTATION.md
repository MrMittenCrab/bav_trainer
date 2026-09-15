# Step 9M.2.4.1.1.1.33 — Selected geographic facts into StandardizedFinancials

AUTOCYCLE_PLAN: {"baseline": "At b74ef31d612166a7dd4e6cfad5c8cf02b7ab1b8c, accepted reconciliation retains 105 observations and selects 56 geographic facts across five periods; standardize_reconciled emits shares and leases but no geographic segment payload.", "finding_key": "selected-geographic-facts-missing-standardized-handoff", "inputs": [], "kind": "work", "objective": "Integrate selected geographic facts into the model-facing historical contract", "plan_id": "719aadd63cb049668af20b2c4a63e52b", "step_id": "9M.2.4.1.1.1.33", "success": "Selected geographic facts populate an optional validated StandardizedFinancials payload, survive deterministic JSON round trips and reproduce five-period consolidated bridges while audit evidence remains separate and protected artifacts remain unchanged.", "verification": "Rerun focused contract, geographic, serialization and CLI tests; reconcile unchanged Lululemon filings into temporary output admitting 2022-01-30; independently compare model values with all 56 selections, reproduce five bridges and prior-presentation mutation, check legacy payload compatibility and checkpoint-relative protected hashes.", "work_id": "68977f91981a43ecba811e61f0b865d6"}

## Scope

- Implement only the selected-facts → optional historical segment contract and serialization dependency.
- Permit changes to `core/data/interface.py`, `core/data/standardized_io.py`, necessary exports/validation under `core/data/`, `core/ingestion/filing_standardizer.py`, directly corresponding tests and `RESULT.md`.
- Preserve extraction and accepted role-aware reconciliation. Source PDFs, extracted JSON, canonical reconciled artifacts, releases and Fast Retailing data remain byte-identical to the checkpoint; verification output belongs in temporary directories.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, workbook generation, forecasting or valuation.

## Task 1 — Define and validate the optional contract

- Add `HistoricalSegmentData` and an optional `StandardizedFinancials` field, following existing historical-data conventions; absence defaults to `None`.
- Represent geographic namespace, segment identities, period-specific revenue/operating profit, consolidated controls and reported reconciling items. Preserve corporate-column versus itemized bridge semantics, reported signs and explicit bridge operations.
- Retain all selected model-relevant facts without manufacturing omitted items, segment totals, periods or zero values. Use the parent financial currency/unit scale.
- Validate supported identities, strict finite numeric values, unique period/identity keys, model-axis membership, complete reported bridge groups and consolidated IS agreement. Distinguish absent data from malformed supplied data; reject contradictions before emitting output.
- Keep source files, hashes, pages, observations, selection reasons and conflicts exclusively in existing audit artifacts.

## Task 2 — Wire selection and round trips

- Populate the contract only from `selected_geographic_facts`; do not reselect raw notes or promote segment values onto statement lines.
- Restrict model data to admitted model periods. Preserve complete available period snapshots without filling missing periods; retain outside-axis observations in provenance.
- Extend standardized JSON export/reload deterministically, preserving identities, dates, values and bridge semantics. Validate supplied segment payloads on reload.
- Accept legacy payloads without the field and explicit null; omit the new field when absent so existing no-segment exports remain unchanged.
- Preserve Q4-2023 geographic definitions and China Mainland identity; prohibit channel/country/product substitution, corporate double counting and inferred week adjustments.

## Task 3 — Verify and record

- Add focused tests for selected-value transfer, five-period round trips, absent/null data, incomplete and contradictory bridges, invalid values/identities/dates, duplicate keys, outside-axis facts and failure immutability.
- Carry the prior-presentation mutation through standardization and reload: select Americas `7928156`, retain superseded `7928256` only in audit evidence, and preserve results under reversed filing/observation order.
- Temporarily reconcile unchanged Lululemon filings with `2022-01-30` admitted; retain 105 observations and 56 selections. Independently reproduce all five revenue/operating-profit bridges at zero USD-thousands tolerance, including `3607682 - 1397067 = 2210615`.
- Verify statement lines, shares, leases and existing audit payloads remain equivalent to checkpoint behavior; only the temporary standardized segment payload is added.
- Run focused contract/serialization/geographic/filing CLI tests, Lululemon/Fast Retailing benchmark tests and `core/tests`. Record interpreter, exact commands, measured outcomes, protected-file comparisons and remaining scope in `RESULT.md`; missing execution evidence is a blocker.

## Acceptance and retained commitments

- The optional contract reproduces all 56 selected facts across five admitted periods after export/reload; missing evidence remains absent, invalid supplied data fails closed, and provenance remains separate.
- Preserve Lululemon five-period history, 486 identities/expectations, 101 unavailable displays and accepted 110 additions; Fast Retailing remains byte-identical at 577 identities and zero unavailable displays.
- Retain G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping and original-row provenance.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls and failure immutability.
- Preserve partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution and distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference or deferred-tax expense/recoverability claims.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / reported 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences, reformulation tolerances and liability/equity discrepancy explanations.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds. This step does not claim workbook recalculation.
- Preserve pending benchmark-improvement and parent-acceptance obligations for requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; do not restart completed publication recovery.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, five snapshot-matched edit identities, historical batch, recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, and hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; distinguish original success, resumed wrapper failures and fresh evidence.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1` and `9M.2.4` remain unresolved; A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED remain distinct.
- Remaining scope: segment analytical schedules and learner/Check integration; G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; all TARGET Step 9 exit gates. Segment assets/capex, significant-expense schedules and D&A remain outside this step. No parent or Step 9 completion claim.
