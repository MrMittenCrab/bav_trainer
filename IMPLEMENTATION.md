# Step 9M.2.4.1.1.1.34 — Historical geographic segment analytical series

AUTOCYCLE_PLAN: {"baseline": "At 38a1bc57f1b8caa5ef742041d7b660e9ed07779b, the accepted optional historical_segment contract preserves 56 selections from 105 observations and five consolidated bridges through deterministic JSON reloads; core/model has no geographic segment analytical series.", "finding_key": "validated-geographic-handoff-missing-analytical-series", "inputs": [], "kind": "work", "objective": "Compute source-supported historical geographic segment economics", "plan_id": "748d6c34a29f4ce39633b855799d7e26", "step_id": "9M.2.4.1.1.1.34", "success": "A validated optional analytical series computes geographic revenue mix, growth, reported operating margins and consolidated bridges from the accepted handoff, with deterministic period alignment, explicit unavailable and undefined results, and unchanged protected artifacts.", "verification": "Inspect the analytical API and independently recompute its five-period outputs from unchanged Lululemon filings after in-memory reconciliation and JSON reload; run focused analytical, contract, geographic and serialization regressions without modifying tracked files; compare protected hashes against the checkpoint and inspect RESULT.md for measured evidence and unresolved parent obligations.", "work_id": "c70f8d503c0d49ecbb4ff0f755597f34"}

## Scope

- Add `core/model/geographic_segment.py`, `core/tests/test_geographic_segment_analysis.py`, and measured evidence in `RESULT.md`; reuse existing contract validation, fiscal-axis and ratio helpers.
- Consume only `StandardizedFinancials.historical_segment`; preserve extraction, reconciliation, serialization and separate audit evidence.
- Source PDFs, extracted JSON, canonical reconciled artifacts, releases and all Fast Retailing data remain byte-identical to `38a1bc57f1b8caa5ef742041d7b660e9ed07779b`.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, workbook generation, forecasting or valuation.

## Task 1 — Compute the optional analytical series

- Provide a typed, deterministic series keyed by canonical fiscal periods and existing Americas, China Mainland and Rest of World identities; validate supplied data before calculation without mutating inputs.
- Compute each segment’s revenue share of consolidated revenue, adjacent-period revenue growth and reported operating margin (`income_from_operations / net_revenue`); distinguish reported operating margin from BAV NOPAT margin.
- Expose calculated segment revenue and operating-profit totals, signed reconciling contributions, reconstructed consolidated operating profit, and differences against reported consolidated revenue/operating profit.
- Apply the validated explicit bridge operations in stable identity order; preserve corporate-column versus itemized semantics, reported signs and separately identified calculated totals.

## Task 2 — Availability and independent regressions

- Missing/null segment data makes the module absent. Missing snapshots on an otherwise valid model axis yield `SOURCE_UNAVAILABLE` only for dependent outputs; never compress gaps or substitute another period.
- Opening growth is absent; later growth requires both immediately adjacent model-period snapshots. Zero denominators use `UNDEFINED_RATIO`; preserve reported zero numerators and negative profits. Reject invalid supplied contracts.
- Independently calculate expected mix, growth, margins and bridges from the unchanged Lululemon extracted filings reconciled in memory with `2022-01-30` admitted, then exported and reloaded through actual JSON.
- Cover both presentation families, all five periods, ratio identities within declared numerical tolerance, exact monetary bridge differences of zero, sparse snapshots, absent/null payloads, zero denominators, reordered inputs and failure immutability.
- Prove prior-presentation mutation retains selected Americas revenue `7928156`, keeps superseded `7928256` exclusively in audit evidence and leaves analytical results unchanged; reject bridge contradictions and incompatible geographic identities.

## Task 3 — Verify and record

- Run `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py -q`.
- Confirm all 56 selected model values survive reload and all five bridges reproduce, including `3607682 - 1397067 = 2210615`; verify legacy payload compatibility and checkpoint-relative protected hashes.
- Record exact commands, interpreter, measured results, independent calculations, tolerances and protected comparisons in `RESULT.md`. Separate fresh evidence from retained results; permission failures remain unexecuted verification, not passes.

## Acceptance and retained obligations

- All analytical outputs derive from admitted selected facts; no invented facts, inferred zeros, missing-period substitution, inferred week adjustments, channel/country/product substitution, corporate double counting or unsupported causal explanations.
- Preserve Q4-2023 definitions, China Mainland identity, currency/units, strict dates/finite values, unique keys, model-axis membership, complete bridges and consolidated IS agreement; keep paths, hashes, pages, observations, selection reasons and conflicts exclusively in audit artifacts.
- Preserve Lululemon five-period history, 486 identities/expectations, 101 unavailable displays and accepted 110 additions; Fast Retailing remains byte-identical at 577 identities and zero unavailable displays.
- Retain G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, deterministic mapping and original-row provenance.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls and failure immutability.
- Preserve partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution and distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference or deferred-tax expense/recoverability claims.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / reported 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences, reformulation tolerances and liability/equity discrepancy explanations.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; accepted canonical generation succeeds. No workbook recalculation claim.
- Preserve pending benchmark-improvement and parent-acceptance obligations for requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; do not restart completed publication recovery.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, five snapshot-matched edit identities, historical batch, recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, and hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; distinguish original success, resumed wrapper failures and fresh evidence.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1` and `9M.2.4` remain unresolved; A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED remain distinct.
- Remaining scope: segment workbook schedules and learner/Check integration; G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; segment assets/capex, significant-expense schedules and D&A; all TARGET Step 9 exit gates. This analytical dependency does not close parent or TARGET acceptance.
