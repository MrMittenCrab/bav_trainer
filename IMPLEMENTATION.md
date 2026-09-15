# Step 9M.2.4.1.1.1.24 — Source-supported share-repurchase cash-use diagnostics

AUTOCYCLE_PLAN: {"baseline": "At 1af61a71148f009f08d677e76b1c0da74c8bca39, Lululemon has 305 practice identities and explicit CF repurchase_of_common_stock values -444001, -558652, -1636879, -1178349 but no repurchase diagnostics; Fast Retailing has 501 identities and no corresponding explicit source.", "finding_key": "historical-cash-use-omits-material-reported-share-repurchases", "kind": "work", "objective": "Expose reported share repurchases in historical cash-use analysis", "plan_id": "1b25d74e21144f22980da7505b1d6f07", "step_id": "9M.2.4.1.1.1.24", "success": "Preserve all 305 Lululemon and 501 Fast Retailing identities and expectations; add twelve Lululemon repurchase exercises, reaching 317, with Fast Retailing unchanged; regenerate both release pairs and demonstrate cash-use shortfalls without inferring their funding source.", "verification": "Read RESULT; independently compute repurchase outflows, revenue ratios and residuals from unchanged reconciled facts; compare baseline semantic identities and expectations, exported formulas, Notes, source links, gating, non-disclosing Check evidence, release hashes and source immutability.", "work_id": "0820f1544ce749a39321df4419091e7b"}

INPUT_STATUS: PENDING
Parents 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; the controller assigns the new work identity.

## Scope

- Add `core/model/share_repurchase.py`; extend `core/model/line_resolver.py`, `core/model/historical_expected.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/checker.py` and directly affected model, benchmark, Trainer and catalog-integrity tests.
- Update necessary release-builder expectations, regenerate existing artifacts under both issuer release directories, and update measured benchmark `BASELINE.md` outputs and the relevant source-supported disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md`.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance edits, note extraction, forecasting or valuation.

## Task 1 — Add repurchase cash-use practice

- Resolve unique explicit CF `repurchase_of_common_stock` only; retain its original source row, signs and values. No label fallback, treasury-stock movement, share-count change, SBC expense, settlement proceeds or withholding-payment substitution.
- Add `share_repurchase_outflow = -reported repurchase cash`, `share_repurchase_to_revenue = outflow / revenue`, and `cash_after_ppe_capex_acquisitions_and_repurchases = CFO − ppe_capex − acquisition_cash_outflow − share_repurchase_outflow`.
- Gate outflow and revenue intensity independently of capex, acquisitions, share history and SBC. Gate the residual additionally on the existing unique CFO, PP&E-capex and acquisition sources; absent acquisition evidence must not become zero.
- Missing or ambiguous sources omit only dependent families; missing required-period values fail closed. Preserve reported zeros, signed reversals and undefined zero-denominator ratios.
- Integrate semantic identities, Python expectations, exported formulas, row mapping and workbook-wide Check; keep reported source links populated.
- Answer-Key Notes must distinguish reported repurchases from total shareholder distributions and dilution effects. Explain negative residuals as selected cash uses exceeding reported CFO, without claiming debt funding, comprehensive free cash flow or a complete cash reconciliation.

## Task 2 — Verify and regenerate

- Independently verify Lululemon outflows `444001 / 558652 / 1636879 / 1178349`, revenue ratios using reported revenue, and residuals `-116195 / 1085647 / -207544 / -256674`.
- Preserve every baseline identity and expectation; add exactly twelve Lululemon exercises to reach 317. Fast Retailing remains 501 with no repurchase exercises.
- Test absent, duplicate, wrong-statement and label-only sources; excluded SBC/treasury substitutes; missing values versus zero; signed reversals; zero revenue; independent gating; each absent/ambiguous residual dependency; original-row fidelity and failure immutability.
- Run affected model, benchmark, source-availability, Trainer and catalog-integrity suites, then `python -m pytest core/tests -q`; record actual commands, subprocess exits and results.
- Run both existing release builders; compare repeated temporary builds semantically and independently check exported arithmetic.
- Verify blank/correct/incorrect non-disclosing Check behavior on disposable copies, visual parity, blank yellow Trainer cells without Notes, matching Answer-Key formulas with Notes, and exactly two user-facing workbooks per issuer.
- Recompute final release inventory hashes and byte sizes; verify unchanged source facts, reconciliation, provenance and supporting copies. State whether spreadsheet recalculation occurred.

## Task 3 — Record results and carry pending obligations

- Record measured improvement and acceptance evidence in `RESULT.md`; retain unresolved parent acceptance and both frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages.
- Retain `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its exactly-five-file snapshot authorization, original edit ownership, historical batch identity and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`.
- Preserve hash-bound original/resumed log evidence, clean original status and replayed edits; distinguish successful original subprocess exits from resumed wrapper failures and fresh executions. Publication recovery does not establish capex or parent acceptance; claim NEW_EVIDENCE only for newly inspected hash-bound progress.
- INPUT_STATUS remains PENDING until all frozen requirements are satisfied. No blanket DONE, numbering repair or prospective ID reservation.

## Original acceptance and pending work retained

- Preserve G5 aliases, lease/deferred-tax/capex/SBC/acquisition exercises, explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve 74 Lululemon unavailable displays and zero Fast Retailing displays, partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios and no unavailable-history 4% substitute.
- Preserve pretax resolution, distinct tax expense, Lululemon capex `638657 / 651865 / 689232 / 680802`, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all twelve pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
