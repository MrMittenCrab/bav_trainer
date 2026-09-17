# RESULT.md — Step 9M.2.4.1.1.1.53 Operating KPIs: management-history workbook integration (disclosure repair)

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.53 — Operating KPIs — Management-history workbook integration  
**Work:** `4902dbbb9a984ccab8e5bdf2dd7b4ed5`  
**Plan:** `66ed8fbf4a2a40f4a39411aaa3cce6f6`  
**Finding:** `operating-kpi-management-history-workbook-integration` — Review blocked prior COMPLETE because Sales per Square Foot Analysis!A5 taught subtraction and fractional-growth arithmetic on the visible Trainer. That prior COMPLETE is qualified: identity integration, Check, and independent arithmetic remain retained, but visible disclosure was not accepted until this repair.  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `34eb49e43ccc45598737d30d699ab3c92fc2a686725a54cbf79c3c8a5d6ba3d5` (10067).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/engine/reference_model.py`, `core/tests/test_operating_kpi_workbook.py`, and `RESULT.md`. Answer-Key Note content in `core/engine/component_catalog.py` already contained subtraction and fractional-growth guidance (`minus the immediately prior`; `(current - prior) / prior`); no catalog edit was required. The accepted `compute_management_kpi_series` API is consumed unchanged. Other supported revenue relationships remain unfinished.

No required plan change.

Working-tree HEAD is `46f5bc6f2f1e909fe571ed21de9d42b0b9e06d8a`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Task 1 — Remove visible calculation disclosure

Sales per Square Foot Analysis!A5 is now the shared non-disclosing `SALES_PER_SQUARE_FOOT_SCOPE_NOTE`:

> Adjacent change and growth are analyst-derived calculations, not causal evidence, and are distinct from comparable-sales percentage-point change.

Reviewed disclosing A5 (rejected by regression):

> Adjacent change is current minus prior reported sales per square foot. Growth is (current - prior) / prior. These are analyst-derived calculations, not causal evidence, and are distinct from comparable-sales percentage-point change.

Trainer and Answer Key share that repaired A5. Management-history column-A labels and A2–A4 retain source identities, units, period semantics, and unavailable explanations. Visible management-history cells no longer contain `current minus prior`, `(current - prior) / prior`, or equivalent growth instructions. Subtraction and fractional-growth guidance remain only in matching Answer-Key practice Notes. The schedule, reported sources, and eligible practice were not hidden.

Answer-Key Notes (catalog `short_hint`, nonempty):

- change: current reported sales per square foot minus the immediately prior reported value;
- growth: `(current - prior) / prior`.

No Trainer practice cell contains a formula, answer, or Note.

---

## Task 2 — Add generated-workbook disclosure regression

`test_reviewed_spsf_a5_disclosure_fails_before_repair` raises `AssertionError` against the reviewed A5 string and passes against the repaired scope note.

The selected-document fixture (test-augmentation selections, not supplied documentary facts) still uses comparable-sales `2/7` and SPSF `1410/1430` through reconciliation → standardization → export/reload → ordinary `build_training_workbook`. Generated pair is exactly two workbooks (`COMP_SELECTED_Trainer.xlsx`, `COMP_SELECTED_Answer_Key.xlsx`). Trainer A5 and all visible management-history explanatory cells were inspected immediately after generation and after openpyxl XLSX save/reload; both states use the approved A5 and reject the reviewed arithmetic fragments. Matching Answer-Key Notes retain both arithmetic explanations. Check components on Trainer are blank with no comments; Answer-Key counterparts keep nonempty Notes.

Independent arithmetic within `1e-12` is unchanged: comparable-sales adjacent change `5` percentage points; SPSF change `20`; growth `20/1410`. Source reuse, serialized mappings, physically relocated cross-sheet/nonadjacent SPSF/comparable-sales formulas, workbook-wide blank/correct/incorrect Check, authenticated moved-SPSF source tamper (`Trusted workbook cell was modified`), Aptos Narrow 11 non-bold black typography, blank bright-yellow Trainer practice, and Answer-Key ordinary white/no-fill with no yellow anywhere remain passing.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Repaired SPSF A5 visible text; Trainer/Answer-Key A5 inspected before and after XLSX save/reload on the selected-document `2/7` + `1410/1430` fixture; reviewed A5 fails `_assert_spsf_a5_non_disclosing` and repaired text passes; Answer-Key change/growth Notes still contain subtraction and `(current - prior) / prior`; Trainer practice cells blank with no Notes; focused workbook **43 passed**; focused required suite **1418 passed**; complete `core/tests` **3222 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Selected 2/7 + SPSF 1410/1430 independent arithmetic within `1e-12` (`5` pp, change `20`, growth `20/1410`); Check **569**; moved compsales+SPSF source formulas follow mapped identities; tamper still authenticated; store fixture without management selection remains **576**; mixed selected 2/4 Check **578**; Fast Retailing **577**; geo **56/74**; preserved **486**; unavailable **101** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Historical, qualified | Prior child claimed COMPLETE with focused **42** / complete **3221** while A5 still disclosed practice arithmetic; that COMPLETE does not cover this Review finding |
| Not claimed | Excel engine recalculation; other supported revenue relationships; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py::test_reviewed_spsf_a5_disclosure_fails_before_repair core/tests/test_operating_kpi_workbook.py::test_selected_document_compsales_workbook_uses_test_augmentation core/tests/test_operating_kpi_workbook.py::test_management_history_workbook_adjacent_change_and_spsf core/tests/test_operating_kpi_workbook.py::test_generated_workbooks_follow_moved_management_sources -q --tb=short` | 0 | **4 passed** in **4.31s** (reviewed A5 fails helper; repaired A5 and generated Trainer pass) |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py -q --tb=short` | 0 | **43 passed** in **21.92s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_reference_integrity.py::test_cli_assumptions_propagate -q --tb=short` | 0 | **1418 passed** in **40.26s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3222 passed**, **0 failed** in **279.62s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/reference_model.py` | `625894d1b2696b32ff81586f07a4177f43d53cd38f1870414d998805c7bdc953` | 357340 |
| `core/tests/test_operating_kpi_workbook.py` | `f27f6edd046bbcf8f6dd01e6525a4d83fccbe39fab662d7c55c16339ab7ab816` | 151672 |

Unedited, still required by the plan:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/component_catalog.py` | `df06d89ec3e6ae0c399ecf330a6c14cb4664ac6f6c00c5ab6f0bc722ce450b55` | 236913 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated management histories still expose identity-specific reported sources and eligible adjacent-period practice; visible Trainer text no longer discloses SPSF practice arithmetic.

---

## Remaining scope

This child repairs visible SPSF A5 disclosure on the accepted management-history Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.52` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales relationship identities remain when eligible. This increment adds identity-specific management adjacent-change and SPSF practice only when eligible selections exist, reported separately from the **576**-cell store fixture. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected management observations that pass those gates now produce the learner schedules; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
