# Step 9M.2.4.1.1.1.25 — Source-supported historical cash roll-forward practice

AUTOCYCLE_PLAN: {"baseline": "At 89802d327aa145451f8630567ccdd5a3dcc3202d, Lululemon has 317 practice identities and Fast Retailing 501; both supply operating, investing, financing, FX, opening cash, closing cash and reported cash-change facts, but no cash-roll-forward practice.", "finding_key": "reported-cash-flow-totals-lack-learner-cash-roll-forward", "kind": "work", "objective": "Connect reported cash flows to opening and closing cash", "plan_id": "4c1369f9295343f495a07ff5577f31c7", "step_id": "9M.2.4.1.1.1.25", "success": "Preserve all baseline identities and expectations; add four cash-roll-forward calculations per period, reaching 333 Lululemon and 521 Fast Retailing exercises; expose reported reconciliation differences without changing source facts.", "verification": "Read RESULT; independently recompute cash movements and reconciliation differences from unchanged standardized facts; compare baseline identities, exported formulas, Notes, Check behavior, repeated-build semantic maps, release hashes and source immutability.", "work_id": "70a2e6c171194e8697b32a1e29757e77"}

INPUT_STATUS: PENDING
Parents 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
Numbering remains administratively frozen; the controller stamps authoritative identities.

## Scope

- Add `core/model/cash_rollforward.py`; extend `core/model/line_resolver.py`, `core/model/historical_expected.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/checker.py` and directly affected tests.
- Update necessary expectations in both existing release builders; regenerate their existing release artifacts and measured benchmark `BASELINE.md` outputs; update the cash-reconciliation disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md`.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, source/provenance edits, note extraction, forecasting or valuation.

## Task 1 — Implement cash roll-forward practice

- Resolve unique explicit CF concepts for operating, investing and financing totals, FX effect, opening cash, closing cash and reported cash change; support both benchmarks’ stored concept spellings without changing stored rows.
- Accept FX aliases `effect_of_fx_on_cash` / `effect_of_exchange_rate_on_cash` and change aliases `change_in_cash` / `net_change_in_cash`; reject competing aliases, label-only inputs and wrong-statement substitutes.
- Add `cash_movement_from_flows = CFO + CFI + CFF + FX`, `cash_movement_difference = cash_movement_from_flows − reported_cash_change`, `cash_ending_from_flows = cash_beginning + cash_movement_from_flows`, and `cash_ending_difference = cash_ending_from_flows − reported_cash_ending`.
- Gate each calculation on its own unique dependencies; absent or ambiguous sources omit dependent families, while missing required-period values fail closed. Preserve reported zeros and signed flows.
- Keep original-row source links populated; integrate semantic identities, Python expectations, exported formulas and workbook-wide Check.
- Notes must explain signed flows, FX and calculated-minus-reported differences in statement units. Preserve nonzero differences; do not insert balancing plugs, assert an unsupported cause, substitute BS cash, or infer debt funding from selected cash-use shortfalls.

## Task 2 — Verify and regenerate

- Independently verify Lululemon movements `-105004 / 1089104 / -259635 / -177134`; both difference series are zero.
- Independently verify Fast Retailing movements `84204 / 180556 / -455013 / 290280 / -300321`, movement differences `0 / 0 / -2 / 1 / -1`, and ending differences `-1 / 0 / -1 / 0 / 0`, in canonical period order.
- Preserve all 317/501 baseline identities and expectations; add exactly 16/20 exercises to reach 333/521. Preserve 74/0 unavailable displays and existing availability semantics.
- Test aliases, competing sources, wrong statements, label-only inputs, each missing dependency, missing values versus zero, signed flows, nonzero discrepancies, original-row fidelity and failure immutability.
- Run affected model, resolver, benchmark, source-availability, Trainer and catalog-integrity suites, then `python -m pytest core/tests -q`; record actual commands and subprocess exits.
- Run both release builders and compare repeated temporary builds semantically; independently inspect exported arithmetic, source links and Notes.
- Verify blank/correct/incorrect non-disclosing Check behavior on disposable copies, visual parity, blank yellow Trainer cells without Notes, matching Answer-Key formulas with Notes, and exactly two user-facing workbooks per issuer.
- Record final hashes and sizes, unchanged source/reconciliation/provenance/supporting artifacts, and whether spreadsheet recalculation occurred.

## Task 3 — Record acceptance and carry obligations

- Record measured improvement and verification in `RESULT.md`; carry frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages.
- Retain recovery evidence `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its exact snapshot-matched checkpoint scope and five production/test edit identities; do not expand historical publication authorization.
- Preserve recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, historical batch identity, original clean status and replayed ownership evidence.
- Retain hash-bound original/resumed logs and distinguish original successful subprocess exits from resumed wrapper failures and fresh runs. Publication recovery does not establish capex or parent acceptance; use NEW_EVIDENCE only for newly inspected hash-bound progress.
- INPUT_STATUS remains PENDING until all frozen requests are satisfied; no blanket DONE, numbering repair or prospective ID reservation.

## Original unresolved acceptance retained

- Preserve G5 aliases, lease/deferred-tax/capex/SBC/acquisition/repurchase exercises, explicit-concept precedence, ambiguity rejection, original-row links, strict values and deterministic semantic mapping.
- Preserve partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios, no unavailable-history 4% substitute, pretax resolution and distinct tax expense.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all twelve pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; preserve current successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G6 period-axis assessment, G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates.
