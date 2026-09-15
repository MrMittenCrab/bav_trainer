# Step 9M.2.4.1.1.1.27 — Source-supported inventory growth and intensity bridge

AUTOCYCLE_PLAN: {"baseline": "At 575f23acc43d0a25ebad807ca54c55e3988a4346, Lululemon/Fast Retailing have 354/548 practice identities and explicit inventory and revenue across four/five periods, but no inventory-specific change attribution.", "finding_key": "reported-inventory-lacks-revenue-and-intensity-change-attribution", "kind": "work", "objective": "Explain inventory changes through revenue growth and inventory intensity", "plan_id": "ceb771f0976147d4bfa7bac573ae46af", "step_id": "9M.2.4.1.1.1.27", "success": "Preserve all 354/548 baseline identities and expectations; add 16/21 inventory exercises reaching 370/569, with independently reconciled revenue-scale and inventory-intensity effects.", "verification": "Read RESULT; independently calculate inventory intensities and adjacent-period bridges from unchanged standardized facts; inspect baseline preservation, exported formulas, source links, Notes, Check results, repeated-build semantic maps, release hashes and source immutability.", "work_id": "b57b3f6199f54daa98b20563fb784b55"}

INPUT_STATUS: PENDING
Parents 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; the controller assigns authoritative identities.

## Scope

- Add `core/model/inventory_analysis.py`; extend `core/model/line_resolver.py`, `core/model/historical_expected.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/checker.py` and directly affected tests.
- Update necessary release-builder/auditor expectations, both issuers’ generated release artifacts and benchmark `BASELINE.md` outputs; update the relevant coverage disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md`.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance changes, note extraction, forecasting or valuation.

## Task 1 — Implement inventory attribution

- Resolve unique explicit BS `inventories`, retaining original-row links and stored values; use existing revenue resolution. Reject duplicate inventory concepts, label-only inventory and wrong-statement substitutes.
- Add inventory intensity `I_t = inventory_t / revenue_t` for each period.
- Add four exercises per adjacent-period pair: inventory change; revenue-scale effect `I_(t−1) × (revenue_t − revenue_(t−1))`; intensity effect `revenue_t × (I_t − I_(t−1))`; reconstructed inventory change as the sum of both effects.
- Gate inventory change on inventory alone; intensity and attribution additionally require revenue. Absent/ambiguous sources omit dependent families; missing required values fail closed; reported zeros remain valid.
- Zero revenue yields the existing undefined-ratio result with dependency propagation; direct inventory change remains available. Do not create opening-period change exercises.
- Integrate semantic identities, Python expectations, exported formulas and workbook-wide Check in one coherent inventory section.
- Answer-Key Notes explain ending inventory relative to annual revenue, prior-intensity/current-revenue attribution convention and signed effects. This is an arithmetic decomposition, not proof of cash movement, deterioration, seasonality, markdowns or management causes; it is not inventory days or turnover.

## Task 2 — Measure improvement and regenerate releases

- Preserve all 354/548 baseline identities and expectations; add exactly 16/21 exercises to reach 370/569.
- Independently recompute every expectation from standardized facts, retaining full precision; reconstructed changes must reconcile within `1e-8` reporting units on both benchmarks.
- Latest Lululemon: intensity `0.15318510979410227`; inventory change `258672`; revenue-scale/intensity effects approximately `70070.30142954475 / 188601.69857045508`.
- Latest Fast Retailing: intensity `0.15025794440234327`; inventory change `36498`; effects approximately `45354.74985791775 / -8856.749857917737`.
- Test source ambiguity, statement boundaries, independent dependency omissions, missing versus zero values, zero revenue in either adjacent period, flat/decreasing revenue, signed movements, original-row fidelity and failure immutability.
- Run affected model/resolver, both benchmark, availability, Trainer and catalog-integrity suites, then `python -m pytest core/tests -q`; record actual commands and subprocess exits.
- Run both release builders and the Fast Retailing release audit; compare repeated temporary builds semantically and independently inspect exported formulas, source links and Notes.
- Verify disposable blank/correct/incorrect Check behavior without answer disclosure, visual parity, 370/569 blank yellow Trainer cells without Notes, matching Answer-Key formulas with Notes and exactly two user-facing workbooks per issuer.
- Preserve 74/0 unavailable displays and availability semantics; record release hashes, sizes, unchanged source/reconciliation/provenance/supporting artifacts and whether spreadsheet recalculation occurred.

## Task 3 — Record acceptance and carry pending requests

- Record measured implementation and verification in `RESULT.md`; carry frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its exact snapshot-matched checkpoint scope, five production/test edit identities and original clean-status/replayed-ownership evidence; do not expand historical publication authorization.
- Preserve recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` and historical batch identity; do not substitute the current batch.
- Retain hash-bound original/resumed logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; distinguish original successful subprocess exits, resumed wrapper failures and fresh runs. Publication recovery does not establish capex or parent acceptance; NEW_EVIDENCE requires newly inspected hash-bound progress against the original objective.
- INPUT_STATUS remains PENDING until both frozen requests are satisfied; no blanket DONE, numbering repair or prospective ID reservation.

## Original unresolved acceptance retained

- Preserve G5 aliases; lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward/margin exercises; explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios, no unavailable-history 4% substitute, pretax resolution and distinct tax expense.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, accepted cash-reconciliation differences, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all twelve pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
