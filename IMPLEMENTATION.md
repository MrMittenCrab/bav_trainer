# Step 9M.2.4.1.1.1.21 — Historical operating cash after PP&E capex

AUTOCYCLE_PLAN: {"baseline": "At 19b6a690e54b8eb9cef8d40ed9dbe52df052abf4, Lululemon has 273 practice identities and Fast Retailing 491. Both supply CFO and PP&E payments, but capex diagnostics expose only spending and revenue intensity. Capex historical test durations in RESULT are misattributed.", "finding_key": "capex-diagnostics-omit-source-supported-operating-cash-after-ppe-spending", "kind": "work", "objective": "Connect reported operating cash flow to historical PP&E reinvestment", "plan_id": "eea265ddd4284f6ca636ec6ab4d52f26", "step_id": "9M.2.4.1.1.1.21", "success": "Add two source-gated historical formula families for CFO minus PP&E capex and its revenue margin, preserving all existing identities; regenerate both release pairs and independently verify 8 added Lululemon exercises and 10 added Fast Retailing exercises. Correct capex timing attribution and retain unresolved parent acceptance and frozen requests.", "verification": "Read RESULT; independently calculate both new series from unchanged source facts, inspect source links, formulas, semantic maps and Check evidence, compare baseline identities, verify final release hashes and source immutability, and match corrected historical timings to hash-bound original and resumed logs.", "work_id": "aa533817002047788f078c692f14d061"}

**INPUT_STATUS:** PENDING
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; controller assigns the new work identity.

## Scope

- Extend `core/model/capex.py`, `core/model/historical_expected.py`, `core/engine/reference_model.py` and their capex, benchmark, Trainer and reference-integrity tests.
- Regenerate existing artifacts under `release/lululemon/` and `release/fast_retailing/` using existing build scripts; record completion in `RESULT.md`.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance edits, new note extraction, forecasting or valuation.

## Task 1 — Add the historical cash/reinvestment connection

- Add `cash_after_ppe_capex = reported CFO − ppe_capex` and `cash_after_ppe_capex_to_revenue = cash_after_ppe_capex / revenue` to the existing capex schedule.
- Resolve CFO through the shared resolver; reuse the accepted signed PP&E payment contract. Populate source links; make only derived calculations practice cells.
- Gate the extension on unambiguous CFO and capex sources without disabling existing capex exercises when CFO is absent. Preserve strict required-period validation, reported zeros, signed values and undefined-ratio semantics.
- Label the schedule “Operating cash after PP&E capex”; explain in Answer-Key Notes that it excludes other investing flows and is not comprehensive free cash flow or a maintenance/growth-capex estimate.
- Integrate semantic identities, Python expected values, workbook formulas, row mapping and workbook-wide Check.

## Task 2 — Verify and regenerate both benchmarks

- Add independent arithmetic tests and synthetic cases for absent/ambiguous CFO, missing period values, zero revenue, negative CFO, reported zero and payment reversals; verify failure immutability.
- Independently verify Lululemon cash after PP&E capex: `327806 / 1644299 / 1583481 / 921675`; Fast Retailing: `372468 / 379546 / 401452 / 577793 / 445083`. Verify each margin against supplied revenue.
- Run affected capex, earnings-quality, source-availability, Trainer, reference-integrity and both benchmark suites, then `python -m pytest core/tests -q`; record actual commands and subprocess exits.
- Run both release builders; compare repeated temporary builds semantically. Preserve all 273/491 baseline identities and add exactly 8/10 exercises, reaching 281/501.
- Inspect exported source links and formulas against independently calculated values. Verify blank/correct/incorrect non-disclosing Check behavior on disposable copies.
- Verify matched visual structure, blank yellow Trainer cells without Notes, Answer-Key formulas with Notes, and exactly two user-facing workbooks per issuer.
- Recompute every final release inventory SHA-256 and byte size after verification; confirm source, reconciled facts, provenance and supporting copies remain unchanged. State whether spreadsheet recalculation occurred.

## Task 3 — Correct evidence and retain acceptance obligations

- Inspect `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` and hash-bound original/resumed Cursor logs; preserve snapshot-limited authorization, original edit ownership, historical batch identity and existing recovery work/attempt identity.
- Correct original capex pytest durations to 76/543/132/1099 passed in `6.34/14.51/30.51/95.38s`; distinguish subprocess elapsed times `6.63/14.81/30.77/95.66s`. Attribute resumed durations separately and retain wrapper exit 1.
- Keep historical test evidence separate from fresh executions. Publication recovery does not establish parent acceptance; do not reopen ownership or manufacture NEW_EVIDENCE.
- Record measured benchmark gains, corrected evidence and remaining acceptance in `RESULT.md`; no blanket DONE or prospective ID reservation.

## Original acceptance and pending work retained

- Preserve G5 aliases, all prior lease/deferred-tax exercises, explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve 74 Lululemon unavailable displays and zero Fast Retailing displays, partial-period interest dependency closure, opening-only CoD `0.374`, undefined-ratio semantics and no unavailable-history 4% substitute.
- Preserve pretax resolution, distinct tax expense, capex `638657 / 651865 / 689232 / 680802`, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all 12 pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
- Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING through the normal five stages until their full requirements and unresolved acceptance are satisfied.
