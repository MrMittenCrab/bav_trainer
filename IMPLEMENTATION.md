# Step 9M.2.4.1.1.1.26 — Source-supported reported operating-margin bridge

AUTOCYCLE_PLAN: {"baseline": "At e1a707759ef9a006fd024713f13ae99fde8d296b, Lululemon has 333 practice identities and Fast Retailing 521; both supply revenue, gross_profit and operating_income/operating_profit, but neither has reported gross-margin or operating-margin bridge practice.", "finding_key": "reported-gross-and-operating-profit-lack-learner-margin-bridge", "kind": "work", "objective": "Explain reported operating-margin changes through gross margin and net operating expense burden", "plan_id": "20eb876192314d3eb8bc1f9c7f80d9f8", "step_id": "9M.2.4.1.1.1.26", "success": "Preserve all 333/521 baseline identities and expectations; add 21/27 source-supported margin exercises to reach 354/548, independently reconciling reported operating-margin changes without requiring interest facts.", "verification": "Read RESULT; independently calculate margins and adjacent-period bridges from unchanged standardized facts; compare baseline identities, exported formulas, source links, Notes, Check behavior, repeated-build semantic maps, release hashes and source immutability.", "work_id": "ed66f1fcc3b149d4b4edac8d03efee9e"}

INPUT_STATUS: PENDING
Parents 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; the controller stamps authoritative identities.

## Scope

- Add `core/model/reported_margin.py`; extend `core/model/line_resolver.py`, `core/model/historical_expected.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/checker.py` and directly affected tests.
- Update necessary expectations in existing release builders/auditors; regenerate both issuers’ existing release artifacts and benchmark `BASELINE.md` outputs.
- Update the relevant coverage disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md`; historical exit-PASS statements do not establish current parent acceptance.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance edits, note extraction, forecasting or valuation.

## Task 1 — Implement reported operating-margin practice

- Resolve unique explicit IS `gross_profit` and `operating_profit` / `operating_income`, using existing revenue resolution; preserve stored concepts and original-row links. Reject competing aliases, label-only profit inputs and wrong-statement substitutes.
- Add three calculations per period: `gross_margin = gross_profit / revenue`, `reported_operating_margin = operating_profit / revenue`, and `net_operating_expense_burden = (gross_profit − operating_profit) / revenue`.
- Add three calculations per adjacent-period pair: gross-margin change, net-operating-expense-burden change, and reconstructed operating-margin change = gross-margin change − burden change.
- Gate each family on its own dependencies; absent/ambiguous sources omit dependent families, missing required values fail closed, reported zeros remain valid, and zero revenue produces the existing undefined-ratio result with downstream propagation.
- Integrate semantic identities, Python expectations, exported formulas and workbook-wide Check in one coherent historical margin section.
- Notes explain percentage-point changes and that gross profit minus operating profit includes net intervening operating items; it is not necessarily SG&A. Positive burden change reduces operating margin. Do not infer price, mix, cost causes or normalized earnings; keep reported operating margin distinct from BAV NOPAT margin.

## Task 2 — Verify improvement and regenerate releases

- Preserve all 333/521 baseline identities and expectations; add exactly 21/27 exercises to reach 354/548, with no opening-period change exercises.
- Independently recompute every margin and bridge from standardized facts. Lululemon latest gross/operating margins approximately `56.6005% / 19.9108%`; Fast Retailing latest approximately `53.7814% / 16.5934%`.
- Verify reconstructed changes equal adjacent reported-operating-margin differences within existing numerical tolerance; store full-precision expectations, not rounded display anchors.
- Test aliases, ambiguity, wrong statements, label-only inputs, independent dependency omissions, missing values versus zero, undefined ratios, negative profits, original-row fidelity and failure immutability.
- Run affected model/resolver, both benchmark, source-availability, Trainer and catalog-integrity suites, then `python -m pytest core/tests -q`; record actual commands and subprocess exits.
- Run both release builders; compare repeated temporary builds semantically and inspect exported formulas, source links and Notes independently.
- Verify non-disclosing blank/correct/incorrect Check behavior on disposable copies, visual parity, blank yellow Trainer cells without Notes, matching Answer-Key formulas with Notes, and exactly two user-facing workbooks per issuer.
- Preserve 74/0 unavailable displays and availability semantics; record final hashes, sizes, unchanged source/reconciliation/provenance/supporting artifacts and whether spreadsheet recalculation occurred.

## Task 3 — Record acceptance and carry pending requests

- Record measured improvement and verification in `RESULT.md`; carry frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages.
- Retain `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its exact snapshot-matched checkpoint scope and five production/test edit identities; do not expand historical publication authorization.
- Preserve recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, historical batch identity, original clean status and replayed ownership evidence.
- Retain hash-bound original/resumed logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; distinguish original successful subprocess exits, resumed wrapper failures and fresh runs. Publication recovery does not establish capex or parent acceptance; NEW_EVIDENCE requires newly inspected hash-bound progress.
- INPUT_STATUS remains PENDING until all frozen requests are satisfied; no blanket DONE, numbering repair or prospective ID reservation.

## Original unresolved acceptance retained

- Preserve G5 aliases, lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward exercises, explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios, no unavailable-history 4% substitute, pretax resolution and distinct tax expense.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, all accepted cash-reconciliation differences, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all twelve pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
