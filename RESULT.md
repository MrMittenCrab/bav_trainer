# RESULT.md — Step 9M.2.4.1.1.1.54 Operating KPIs: revenue/SPSF growth relationship

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.54 — Operating KPIs — Revenue/SPSF growth relationship  
**Work:** `4d6514b288f442909212b1cc54f571c2`  
**Plan:** `0c1653dfcd814a81ab201fd916277e3c`  
**Finding:** `operating-kpi-revenue-spsf-growth-relationship`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted management-history work `4902dbbb9a984ccab8e5bdf2dd7b4ed5` remains complete and is not reopened. Visible SPSF A5 disclosure repair remains intact.  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `dfea8eadddb56787169d25ffe83e39f598a106f7a321a6ae159a9b9ec473aabb` (9694).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/model/operating_kpi_relationships.py`, `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/tests/test_operating_kpi_relationships.py`, `core/tests/test_operating_kpi_workbook.py`, `core/model/historical_expected.py`, `core/trainer/checker.py`, and `RESULT.md`. Interrupted working-tree work on those paths was inspected and finished; no cosmetic-only edits.

## Required plan change

IMPLEMENTATION.md limited edits to the five listed code/test files plus `RESULT.md`. Ordinary Check expected-value registration for the new difference family also requires `core/model/historical_expected.py` and `core/trainer/checker.py` (same path as the accepted comparable-sales relationship). Those two files were already present as interrupted work and were preserved. Plan should add them to the allowed-file list; the plan text was not rewritten.

No other required plan change.

Working-tree HEAD is `777bdf02126c569a95f126f91962020e0a0d3790`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Task 1 — Add the source-gated relationship

`operating_kpi_revenue_sales_per_square_foot_relationship_applicable` and `compute_operating_kpi_revenue_sales_per_square_foot_relationship` follow existing relationship conventions. Eligible identities are validated global-empty-geography, reported, company-operated-store `sales_per_square_foot` observations with unit `USD_per_square_foot`. Series stay keyed by full identity and are never merged.

The API reuses `compute_management_kpi_series` fractional SPSF growth and `_resolved_revenue_maps` statement revenue growth. Descriptive difference is `100 * (revenue_growth - spsf_growth)` in percentage points. Reported `USD_per_square_foot` is retained without statement monetary scaling. Opening growth/difference remain `None`. Adjacent canonical revenue and existing SPSF semantic gates are unchanged. Missing-input `SOURCE_UNAVAILABLE` takes precedence over `UNDEFINED_RATIO`. Zero prior remains `UNDEFINED_RATIO` and stays practiced. Malformed contracts, ambiguous revenue, and invalid axes reject without mutation.

Absent/null/store-only/comparable-sales-only and ineligible geography/basis/population SPSF histories do not activate this relationship.

---

## Task 2 — Integrate one learner comparison

Sales per Square Foot Analysis now includes eligible revenue-growth comparison practice. Shared consolidated-revenue sources/growth are reused when already registered; SPSF-only histories supply those revenue identities on the SPSF sheet. Comparison practice is added only for identity/period pairs with a numeric or `UNDEFINED_RATIO` difference. Semantic dependencies are `operating_kpi_revenue_growth` then `operating_kpi_sales_per_square_foot_growth` for the same period.

Visible A4 includes `SALES_PER_SQUARE_FOOT_REVENUE_SCOPE_NOTE`: consolidated revenue and the disclosed SPSF population have different scopes; the comparison does not establish revenue attribution, selling-area growth, or causal effects. A5 remains the accepted non-disclosing `SALES_PER_SQUARE_FOOT_SCOPE_NOTE`. Arithmetic lives only in Answer-Key Notes (`100 × (statement-derived consolidated revenue growth − disclosed sales-per-square-foot growth)`). Trainer practice cells stay blank bright-yellow without formulas/answers/Notes. Answer-Key counterparts are ordinary white/no-fill with nonempty Notes. Aptos Narrow 11 non-bold black typography is unchanged.

Generated pair remains exactly two workbooks. Missing or semantically unavailable dependencies produce non-practice unavailable displays.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Selected-document fixture (test-augmentation selections, not supplied documentary facts) uses comparable-sales `2/7` and SPSF `1410/1430` through reconciliation → standardization → export/reload → ordinary `build_training_workbook`. Generated pair is exactly two workbooks (`COMP_SELECTED_Trainer.xlsx`, `COMP_SELECTED_Answer_Key.xlsx`).

Independent arithmetic within `1e-12`:

| Quantity | Value |
|---|---|
| SPSF sources | `1410` then `1430` |
| SPSF adjacent change | `20` |
| SPSF growth | `20/1410` = `0.014184397163120567` |
| Canonical revenue FY2023/FY2024 | `8110518` / `9619278` |
| Revenue growth FY2024 | `(9619278 - 8110518) / 8110518` = `0.18602510961691965` |
| Growth difference FY2024 | `100 * (revenue_growth - 20/1410)` = `17.184071245379908` |
| Tiny SPSF-only fixture `1000/1100` vs `1410/1430` | `100 * (0.1 - 20/1410)` = `8.581560283687944` |
| Opening SPSF difference | `SOURCE_UNAVAILABLE` on selected FY2023 (no prior SPSF) |

Workbook Check on the selected fixture: **570** (`486 + 74 + 4 + 2 + 1 + 3`). Blank then formula-filled correct; authenticated source/formula tamper still rejects without disclosure. Store fixture without management selection remains **576**. Mixed selected 2/4 Check **578**. Fast Retailing **577**. Geo **56/74**. Preserved **486**. Unavailable **101**.

SPSF-only workbook supplies shared revenue on Sales per Square Foot Analysis and does not create Store Count or Comparable Sales sheets. Mixed identities stay isolated. Relocated cross-sheet/nonadjacent SPSF and revenue-growth formulas follow mapped identities rather than adjacent columns.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Revenue/SPSF relationship APIs; SPSF-only shared revenue schedule; selected-document `2/7` + `1410/1430` difference `100 * (rev_growth - 20/1410)` within `1e-12`; Check **570**; focused workbook **44 passed**; focused relationships **35 passed** (combined **79**); focused required suite **1426 passed**; complete `core/tests` **3230 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | SPSF-only tiny difference `8.581560283687944`; moved SPSF source formulas follow mapped identities including difference `=100*(revenue_growth - spsf_growth)`; tamper still authenticated; store fixture **576**; mixed selected 2/4 Check **578**; Fast Retailing **577**; geo **56/74**; preserved **486**; unavailable **101** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Not claimed | Excel engine recalculation; other supported revenue relationships; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_workbook.py -q --tb=short` | 0 | **79 passed** in **23.25s** (relationships **35**, workbook **44**) |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_reference_integrity.py::test_cli_assumptions_propagate -q --tb=short` | 0 | **1426 passed** in **40.04s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3230 passed**, **0 failed** in **278.57s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/operating_kpi_relationships.py` | `f7ea761acac9b6e09195a1c56d1cab0365888ef0ff1f12c8f1d2d1ededcaae34` | 31718 |
| `core/engine/component_catalog.py` | `267de5f3d69ee2c78deaa46250a524bfd769039aca69ab68fcdbf9d3c1572f68` | 242069 |
| `core/engine/reference_model.py` | `c428855365c1b2fa7289acb1dc752bc2ae6dfb335c9801566aabc2d04fb25337` | 367533 |
| `core/tests/test_operating_kpi_relationships.py` | `c89b9e102879018cec32fe947c91525f43ea97cfacff304a43d70738b9bad442` | 85778 |
| `core/tests/test_operating_kpi_workbook.py` | `10f31128c31ab0588c7e347b555f82aa1ff94cc8311aae3cf5ecbb14aa99d920` | 159126 |
| `core/model/historical_expected.py` | `3cac8f42fcc156664db381fab0a1b9bf7c35784c9fa4ecff3002b3ac435c2006` | 64844 |
| `core/trainer/checker.py` | `aec15dfb7ce6ee356a5e6b718ffdeda9fd63dcabe11740b87ab6a7797a27938d` | 22993 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Eligible validated SPSF histories now expose identity-specific revenue/SPSF growth-difference practice when adjacent revenue and SPSF growth exist.

---

## Remaining scope

This child adds the revenue versus SPSF growth comparison on the accepted Operating KPI Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.53` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales relationship identities remain when eligible. Management-history adjacent-change and SPSF practice remain when eligible selections exist, reported separately from the **576**-cell store fixture. This increment adds identity-specific revenue/SPSF growth-difference practice only when eligible. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected management observations that pass those gates now produce the learner schedules including eligible revenue/SPSF comparison; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
