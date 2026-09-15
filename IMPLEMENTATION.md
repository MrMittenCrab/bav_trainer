# Step 9M.2.4.1.1.1.28 — Inventory balance movement versus reported operating cash-flow adjustment

AUTOCYCLE_PLAN: {"baseline": "At 2edaed06c70184dad3636ee01a8a38783872e3bf, Lululemon/Fast Retailing preserve 370/569 practice identities; both supply explicit BS inventories and CF change_in_inventories, but no comparison schedule. Latest negative BS movements are -258672/-36498 versus reported CF adjustments -188710/-29855.", "finding_key": "inventory-balance-movements-not-compared-with-reported-cash-flow-adjustments", "kind": "work", "objective": "Explain differences between inventory balance movements and reported operating cash-flow adjustments", "plan_id": "8d8b0081de894f0b9168958942fb4e97", "step_id": "9M.2.4.1.1.1.28", "success": "Preserve all 370/569 baseline identities and expectations; add exactly 6/8 comparison exercises reaching 376/577, exposing latest unexplained differences of 69962/6643 without altering reported facts or attributing unsupported causes.", "verification": "Read RESULT; independently calculate all adjacent-period negative inventory movements and reported-minus-implied differences from unchanged standardized facts; verify baseline preservation, exported source links/formulas/Notes, Check behavior, repeated-build semantic maps, release hashes and source immutability.", "work_id": "04fefb0cc5274857b2b79a0ad9096974"}

INPUT_STATUS: PENDING
Parents 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; the controller assigns authoritative identities.

## Scope

- Extend `core/model/inventory_analysis.py`, `core/model/line_resolver.py`, `core/model/historical_expected.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/checker.py` and directly affected tests.
- Update necessary release-builder/auditor expectations, both issuers’ generated release artifacts, benchmark `BASELINE.md` outputs and the relevant coverage disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md`.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance edits, note extraction, forecasting or valuation.

## Task 1 — Add inventory balance-to-cash-flow comparison

- Resolve unique explicit CF `change_in_inventories`, preserving original-row links and signed reported values; reject duplicates, label-only matches and wrong-statement substitutes.
- Extend the existing inventory section with populated reported CF adjustment links and two exercises per adjacent-period pair: balance-implied adjustment `B_t = -(inventory_t - inventory_(t−1))`; unexplained difference `D_t = reported_CF_adjustment_t - B_t`.
- Gate `B_t` on unique BS inventory alone; gate `D_t` additionally on the unique CF adjustment. Neither requires revenue, CFO or interest. Missing/ambiguous sources omit only dependent families; missing required values fail closed; reported zeros remain valid.
- Do not create opening-period comparison exercises or infer an opening inventory balance. Keep available opening-period CF facts populated.
- Integrate semantic identities, Python expectations, exported formulas and workbook-wide Check; reuse the existing inventory-change result where appropriate.
- Answer-Key Notes distinguish the negative balance movement from the reported operating CF reconciliation adjustment. Explain that a nonzero difference needs further evidence; it does not establish an error, cash paid for inventory, FX, acquisitions, write-downs or another specific cause. Do not insert a balancing plug.

## Task 2 — Verify improvement and regenerate releases

- Preserve every baseline identity and expectation; add exactly 6 Lululemon and 8 Fast Retailing exercises, reaching 376/577.
- Independently calculate all expectations from standardized facts: Lululemon differences `-57181 / -37606 / 69962`; Fast Retailing `40164 / 10234 / 1666 / 6643`. Verify `B_t + D_t = reported_CF_adjustment_t` within `1e-8` reporting units.
- Test ambiguity, statement boundaries, independent dependency omissions, missing versus zero values, increasing/decreasing/flat inventory, signed CF adjustments, opening-period exclusion, original-row fidelity and failure immutability.
- Run affected inventory/resolver/catalog/availability/Trainer and both benchmark suites, then `python -m pytest core/tests -q`; record actual commands and subprocess exits.
- Run both release builders and the Fast Retailing release audit; compare repeated temporary builds semantically and independently inspect exported formulas, source links and Notes.
- Verify disposable blank/correct/incorrect Check behavior without answer disclosure, visual parity, 376/577 blank yellow Trainer cells without Notes, matching Answer-Key formulas with Notes and exactly two user-facing workbooks per issuer.
- Preserve 74/0 unavailable displays and availability semantics; record release hashes, sizes, unchanged source/reconciliation/provenance/supporting artifacts and whether spreadsheet recalculation occurred.

## Task 3 — Record acceptance and carry pending requests

- Record measured completion and verification in `RESULT.md`; carry requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages. INPUT_STATUS remains PENDING until both are satisfied; no blanket DONE or prospective ID reservation.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its exact snapshot-matched checkpoint scope, five production/test edit identities and reviewed clean-status/replayed-ownership evidence; do not expand historical publication authorization.
- Preserve recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` and historical batch identity.
- Retain hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; distinguish original successful subprocess exits, resumed wrapper failures and fresh runs. Publication recovery does not establish capex or parent acceptance; NEW_EVIDENCE requires newly inspected hash-bound progress against the original objective.

## Original unresolved acceptance retained

- Preserve G5 aliases; lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward/margin/inventory exercises; explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios, no unavailable-history 4% substitute, pretax resolution and distinct tax expense.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, accepted cash-reconciliation differences, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all twelve pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
