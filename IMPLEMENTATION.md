# Step 9M.2.4.1.1.1.33 — Selected geographic facts into StandardizedFinancials

AUTOCYCLE_PLAN: {"baseline": "At b74ef31d612166a7dd4e6cfad5c8cf02b7ab1b8c, accepted reconciliation retains 105 observations and selects 56 geographic facts across five periods; standardize_reconciled emits shares and leases but no geographic segment payload.", "finding_key": "selected-geographic-facts-missing-standardized-handoff", "inputs": [], "kind": "work", "objective": "Integrate selected geographic facts into the model-facing historical contract", "plan_id": "5d42faec1fed44d9b8ddfe6cf86443b9", "step_id": "9M.2.4.1.1.1.33", "success": "Selected geographic facts populate an optional validated StandardizedFinancials payload, survive deterministic JSON round trips and reproduce five-period consolidated bridges while audit evidence remains separate and protected artifacts remain unchanged.", "verification": "Independently reject trailing-garbage segment dates through JSON reload; rerun focused contract, geographic, serialization and CLI tests; reconcile unchanged Lululemon filings into temporary output admitting 2022-01-30; compare all 56 selections, five bridges and prior-presentation mutation; check legacy compatibility and checkpoint-relative protected hashes.", "work_id": "68977f91981a43ecba811e61f0b865d6"}

## Scope

- Continue work `68977f91981a43ecba811e61f0b865d6` within its existing step; repair segment-date validation only.
- Permit changes to `core/data/standardized_io.py`, directly corresponding tests and `RESULT.md`; preserve existing non-segment date compatibility.
- Preserve extraction and accepted role-aware reconciliation. Source PDFs, extracted JSON, canonical reconciled artifacts, releases and Fast Retailing data remain byte-identical to checkpoint `f8bd8169aed35ca21e8299d2dd6eb488bbf42420`; verification output belongs in temporary directories.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, workbook generation, forecasting or valuation.

## Task 1 — Strict segment-date reload

- Validate the original segment `period` value as a canonical `YYYY-MM-DD` string representing a real calendar date before constructing `HistoricalSegmentPeriod`.
- Reject trailing garbage, timestamp suffixes, surrounding whitespace, noncanonical date forms, impossible dates and non-string values without truncation, stripping or coercion.
- Raise a field-specific validation error before returning financial data; retain existing duplicate-period, model-axis and bridge validation.

## Task 2 — Regression coverage

- Add parameterized reload regressions in `core/tests/test_historical_segment.py`, including exactly `2025-12-31garbage` against an otherwise valid fixture admitting `2025-12-31`.
- Exercise actual JSON encode/decode followed by `standardized_from_payload`; prove malformed dates raise and leave the supplied payload unchanged.
- Cover the other rejected forms, valid canonical dates and leap-day validity; retain deterministic valid round trips and missing/null segment compatibility.

## Task 3 — Verify and record

- Run `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py -q`.
- Temporarily reconcile unchanged Lululemon filings admitting `2022-01-30`; verify 105 observations, all 56 selected model values after reload and five revenue/operating-profit bridges at zero USD-thousands tolerance, including `3607682 - 1397067 = 2210615`.
- Verify Americas `7928156` survives prior-presentation mutation and reload, with superseded `7928256` only in audit evidence; retain reversed filing/observation-order determinism and outside-axis exclusion.
- Verify statement lines, shares, leases and audit payloads remain equivalent to checkpoint behavior; compare protected hashes. Retain existing benchmark/core-suite evidence as historical evidence, clearly distinct from fresh focused results.
- Update `RESULT.md` with the corrected acceptance status, interpreter, exact commands, measured results, regression evidence, protected-file comparisons and remaining scope. Missing execution evidence remains a blocker.

## Original acceptance and retained commitments

- The optional contract reproduces all 56 selected facts across five admitted periods after export/reload; missing evidence remains absent, invalid supplied data fails closed, and provenance remains separate.
- Populate only from selected geographic facts; preserve Q4-2023 definitions, China Mainland identity, parent currency/units, reported signs, corporate-column versus itemized bridge semantics and explicit operations.
- Preserve strict finite values, supported identities, unique keys, model-axis membership, complete reported bridges and consolidated IS agreement; no manufactured facts, zeros, totals, periods, channel/country/product substitution, corporate double counting or inferred week adjustments.
- Preserve missing/null compatibility and omit-when-absent exports; retain source paths, hashes, pages, observations, reasons and conflicts exclusively in audit artifacts.
- Preserve Lululemon five-period history, 486 identities/expectations, 101 unavailable displays and accepted 110 additions; Fast Retailing remains byte-identical at 577 identities and zero unavailable displays.
- Retain G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping and original-row provenance.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls and failure immutability.
- Preserve partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution and distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference or deferred-tax expense/recoverability claims.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / reported 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences, reformulation tolerances and liability/equity discrepancy explanations.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds. No workbook recalculation claim.
- Preserve pending benchmark-improvement and parent-acceptance obligations for requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; do not restart completed publication recovery.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, five snapshot-matched edit identities, historical batch, recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, and hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; distinguish original success, resumed wrapper failures and fresh evidence.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1` and `9M.2.4` remain unresolved; A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED remain distinct.
- Remaining scope: segment analytical schedules and learner/Check integration; G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; all TARGET Step 9 exit gates. Segment assets/capex, significant-expense schedules and D&A remain outside this step. No parent or Step 9 completion claim.
