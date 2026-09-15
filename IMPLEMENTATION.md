# Step 9M.2.4.1.1.1.23 — Source-supported acquisition cash and historical cash-use diagnostics

AUTOCYCLE_PLAN: {"baseline": "At d6483a191c7fbb9d784cbee789a4e59983505966, Lululemon has 293 practice identities and explicit acquisition_net_of_cash_acquired values 0, 0, -154146, 0; acquisition-cash exercises are absent. Fast Retailing has 501 identities and no corresponding acquisition source.", "finding_key": "historical-cash-use-omits-source-supported-acquisition-payments", "kind": "work", "objective": "Expose reported acquisition cash in historical cash-use analysis", "plan_id": "42445c696a6e4a359b46daf35bbf5bc4", "step_id": "9M.2.4.1.1.1.23", "success": "Preserve all 293/501 baseline identities and expectations; add twelve Lululemon acquisition-cash exercises, reaching 305, with Fast Retailing unchanged at 501; regenerate both release pairs and retain unresolved acceptance and frozen requests.", "verification": "Read RESULT; independently calculate acquisition outflows, revenue ratios and CFO less PP&E capex and acquisitions from unchanged reconciled facts; compare baseline identities, inspect exported formulas, source links, Notes, gating and non-disclosing Check evidence; verify release hashes and source immutability.", "work_id": "1ab2dedee174455eab63872e9a7fb818"}

INPUT_STATUS: PENDING
Parents 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; the controller assigns the new work identity.

## Scope

- Add `core/model/acquisition_cash.py`; extend `core/model/line_resolver.py`, `core/model/historical_expected.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py` and directly affected model, benchmark, Trainer and reference-integrity tests.
- Update benchmark release-builder expectations; regenerate existing artifacts under both issuer release directories and measured benchmark `BASELINE.md` outputs. Update only the acquisition-source disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md`.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance edits, note extraction, forecasting or valuation.

## Task 1 — Add acquisition-cash practice

- Resolve the unique explicit CF concept `acquisition_net_of_cash_acquired`; retain its source row, reported signs and values. No label fallback or substitution from goodwill changes, intangible purchases, securities or ROU payments.
- Add `acquisition_cash_outflow = -reported acquisition cash`, `acquisition_cash_to_revenue = acquisition_cash_outflow / revenue`, and `cash_after_ppe_capex_and_acquisitions = reported CFO − ppe_capex − acquisition_cash_outflow`.
- Gate the first two families independently of goodwill/intangible balances and capex. The third additionally requires existing unambiguous CFO and PP&E-capex sources; reuse their established sign and resolution contracts.
- Missing or ambiguous sources omit only dependent families. Missing required-period values fail closed through the strict-value contract; preserve reported zeros, signed inflows and undefined zero-denominator ratios.
- Keep reported source links populated; integrate derived formulas, semantic identities, Python expectations, row mapping and workbook-wide Check.
- Answer-Key Notes must explain net-of-acquired-cash reporting and that the residual is a mechanical cash-use diagnostic, not comprehensive free cash flow, acquisition profitability, purchase-price allocation or a goodwill roll-forward.

## Task 2 — Verify and regenerate

- Independently verify Lululemon acquisition outflows `0 / 0 / 154146 / 0`, revenue ratios using reported revenue, and cash after PP&E capex and acquisitions `327806 / 1644299 / 1429335 / 921675`.
- Preserve all 293 Lululemon and 501 Fast Retailing baseline identities and expectations; add exactly twelve Lululemon exercises, reaching 305, and none for Fast Retailing.
- Test absent/ambiguous/wrong-statement/label-only acquisition sources, missing values versus reported zero, signed inflows, zero revenue, absent/ambiguous CFO and capex, independent gating without goodwill, source-row fidelity and failure immutability.
- Run affected model, benchmark, availability, Trainer and catalog-integrity suites, then `python -m pytest core/tests -q`; record actual commands, subprocess exits and results.
- Run both existing release builders; compare repeated temporary builds semantically and inspect exported formulas against independent arithmetic.
- Verify blank/correct/incorrect non-disclosing Check behavior on disposable copies, visual parity, blank yellow Trainer practice cells without Notes, matching Answer-Key formulas with Notes, and exactly two user-facing workbooks per issuer.
- Recompute final release inventory SHA-256 values and byte sizes; verify unchanged source, reconciled facts, provenance and supporting copies. State whether spreadsheet recalculation occurred.

## Task 3 — Record results and pending obligations

- Record measured gains and verification in `RESULT.md`; update the acquisition deferral to distinguish Lululemon’s explicit source from Fast Retailing’s absent source. Preserve unsupported impairment/allocation deferrals.
- Retain reviewed capex recovery evidence at `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, exactly-five-file snapshot authorization, original edit ownership, historical batch identity and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`.
- Preserve hash-bound original/resumed log evidence and successful original subprocess exits separately from resumed wrapper failures and fresh executions. Publication recovery does not establish parent acceptance; claim NEW_EVIDENCE only for newly inspected hash-bound progress evidence.
- Carry frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; INPUT_STATUS remains PENDING until all requirements and unresolved acceptance are satisfied. No blanket DONE or prospective ID reservation.

## Original acceptance and pending work retained

- Preserve G5 aliases, lease/deferred-tax/capex/SBC exercises, explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve 74 Lululemon unavailable displays and zero Fast Retailing displays, partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios and no unavailable-history 4% substitute.
- Preserve pretax resolution, distinct tax expense, Lululemon capex `638657 / 651865 / 689232 / 680802`, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all twelve pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
