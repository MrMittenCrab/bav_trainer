# Step 9M.2.4.1.1.1.22 — Historical stock-based compensation and operating cash diagnostics

AUTOCYCLE_PLAN: {"baseline": "At 84d0cd7e9b14d9968f13524b5a1494eb1dd47a84, Lululemon has 281 practice identities and reports cash-flow stock_based_compensation of 78075, 93560, 90011 and 62203; neither benchmark has SBC practice families. Fast Retailing has 501 identities and no corresponding explicit cash-flow SBC source.", "finding_key": "earnings-quality-omits-source-supported-stock-based-compensation-diagnostics", "kind": "work", "objective": "Expose reported stock-based compensation in historical cash-quality analysis", "plan_id": "13e37cf292d448c1b5389e79e61f44c8", "step_id": "9M.2.4.1.1.1.22", "success": "Add source-gated SBC/revenue, SBC/CFO and CFO-minus-reported-SBC formula families; preserve all 281/501 existing identities, add exactly 12 Lululemon exercises and none for Fast Retailing, regenerate both release pairs and retain unresolved acceptance and frozen requests.", "verification": "Read RESULT; independently calculate the three series from unchanged reconciled facts, compare baseline identities, inspect exported source links, formulas, Notes and non-disclosing Check evidence, verify missing-source gating, final release hashes and source immutability.", "work_id": "f3295bfc32d045ed81798dae1f18b030"}

**INPUT_STATUS:** PENDING
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; the controller assigns the new work identity.

## Scope

- Extend `core/model/earnings_quality.py`, `core/model/historical_expected.py`, `core/engine/reference_model.py` and directly affected earnings-quality, benchmark, Trainer and reference-integrity tests.
- Regenerate existing artifacts under `release/lululemon/` and `release/fast_retailing/`; permit existing benchmark tests to regenerate their measured `BASELINE.md` outputs.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance edits, note extraction, forecasting or valuation.

## Task 1 — Add the source-gated SBC diagnostic

- Resolve the unique explicit cash-flow concept `stock_based_compensation` through the shared resolver; retain its original source row, values and signs. Exclude settlement proceeds, withholding payments and repurchases.
- Add `sbc_to_revenue = SBC / revenue`, `sbc_to_operating_cash_flow = SBC / reported CFO` and `operating_cash_flow_less_sbc = reported CFO − SBC`.
- Keep the reported SBC source link populated; only the three derived families become practice cells. Integrate semantic identities, Python expectations, workbook formulas, row mapping and workbook-wide Check.
- Absent or ambiguous SBC omits only this extension. Require unambiguous CFO and explicit required-period values; preserve reported zeros, signed values and undefined-ratio semantics.
- Label the subtraction “Reported CFO less SBC add-back.” Answer-Key Notes must explain this mechanical diagnostic does not restate reported CFO, estimate cash compensation or dilution, establish free cash flow, or quantify tax effects.

## Task 2 — Verify and regenerate the benchmarks

- Independently calculate the three series from unchanged reconciled facts. Verify Lululemon CFO less SBC equals `888388 / 2202604 / 2182702 / 1540274`, and both ratios use their stated reported denominators.
- Test absent/ambiguous SBC and CFO, missing period values, reported zero and negative SBC/CFO, zero revenue/CFO, explicit-concept precedence, misleading settlement/repurchase labels, and failure immutability.
- Preserve all 281 Lululemon and 501 Fast Retailing baseline identities and expectations; add exactly 12 Lululemon exercises, reaching 293, while Fast Retailing remains 501.
- Run affected earnings-quality, source-availability, benchmark, Trainer and reference-integrity suites, then `python -m pytest core/tests -q`; record actual commands, subprocess exits and measured results.
- Run both existing release builders; compare repeated temporary builds semantically. Inspect exported source links and formulas against independent arithmetic.
- Verify blank/correct/incorrect non-disclosing Check behavior on disposable copies; matched visual structure; blank yellow Trainer practice cells without Notes; matching Answer-Key formulas with Notes; exactly two user-facing workbooks per issuer.
- Recompute every final release inventory SHA-256 and byte size; verify source, reconciled facts, provenance and supporting copies remain unchanged. State whether spreadsheet recalculation occurred.

## Task 3 — Record completion and carry pending obligations

- Record measured benchmark gains and verification in `RESULT.md`; retain prior capex acceptance, corrected original/resumed timing evidence and their distinction from fresh executions.
- Preserve recovery evidence at `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, snapshot-limited authorization, original edit ownership, historical batch identity and existing recovery work/attempt identity; publication recovery does not establish parent acceptance.
- Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING through the normal five stages until all requirements and unresolved acceptance are satisfied. No blanket DONE or prospective ID reservation.

## Original acceptance and pending work retained

- Preserve G5 aliases, all lease/deferred-tax/capex exercises, explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve 74 Lululemon unavailable displays and zero Fast Retailing displays, partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios and no unavailable-history 4% substitute.
- Preserve pretax resolution, distinct tax expense, Lululemon capex `638657 / 651865 / 689232 / 680802`, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all 12 pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
