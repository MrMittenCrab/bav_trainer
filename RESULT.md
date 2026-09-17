# RESULT.md — Step 9M.2.4.1.1.1.58 Geographic Analysis: operating-profit amount-change bridge

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.58 — Geographic Analysis — Operating-profit amount-change bridge  
**Work:** `06c5cb92775a41e1a9b7515d0268b9e4`  
**Plan:** `48754410c77148c185ba39c27336ab87`  
**Finding:** `geographic-operating-profit-amount-change-bridge`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted mix/within work `3bc0356f73fb4e289eec1c23db6e6ff4` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `e04ff2bb0fed603363f46d20925f5c2371bfd5dd5e857eeea87087279c1063bd` (10207).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance.

No interrupted working-tree edits were present. `core/trainer/checker.py` required no edits (catalog-driven family IDs).

## Required plan change

No required plan change.

Working-tree HEAD is `b3ed0e5e7ec1875616a0a07de44e3a24f1167d2c`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Task 1 — Compute the adjacent operating-profit amount bridge

`GeographicSegmentSeries` now carries identity-specific `operating_profit_amount_change`, aggregate `reconciling_operating_profit_amount_change`, `consolidated_operating_profit_amount_change`, and signed `operating_profit_amount_change_residual`. Segment and consolidated changes are current minus immediately prior reported operating profit. Aggregate reconciling change is current minus prior sum of accepted signed reconciling contributions, preserving ADD/SUBTRACT signs and comparing aggregates only across presentation families. Residual is consolidated profit change minus summed segment profit changes minus aggregate reconciling amount change.

These are monetary differences with no revenue denominator. Opening changes/residual remain `None`. Missing adjacent snapshots are `SOURCE_UNAVAILABLE` without compressing gaps. Zero current or prior revenue does not suppress available profit changes. Zeros, losses, negative changes, and signed residuals are preserved. Residual equals the constructed bridge identity and the negation of the adjacent change in accepted `consolidated_operating_profit_difference` (reported-minus-reconstructed) at measured maximum error `0.0`.

---

## Task 2 — Integrate learner practice and Check

Geographic Segment Analysis now includes segment operating-profit amount-change rows, aggregate reconciling amount change, consolidated amount change, and the signed residual, in statement currency and monetary scale. Formulas resolve mapped current/prior operating-profit sources and mapped signed reconciling practice cells after relocation, including cross-sheet/nonadjacent source placements. Aggregate reconciling formulas sum accepted signed monetary contributions; they do not reverse-engineer rounded margins. Answer-Key Notes explain absolute profit-change attribution, signed reconcilers, and residuals, and distinguish monetary changes from the accepted percentage-point margin bridge and midpoint mix/within decomposition. Notes claim no normalization, organic growth, causality, or BAV NOPAT.

Generated pair remains exactly two workbooks. Trainer practice cells are blank bright-yellow without formulas, answers, or Notes. Answer-Key counterparts are ordinary white/no-fill with nonempty arithmetic Notes. Aptos Narrow 11 non-bold black typography is unchanged. Missing adjacent dependencies produce non-practice unavailable displays. Absent/null histories activate nothing. Accepted mix, growth, segment margins, revenue-growth contributions, operating-margin contribution bridges, mix/within decomposition, signed bridges, and operating-KPI disclosure behavior are retained.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Supplied-filing reconciliation → standardization → export/reload → ordinary geographic workbook fixture remains five canonical periods with **56** selected geographic sources. New practice identities this increment: **24** (3 segment amount changes + aggregate reconciling change + consolidated change + residual on each of 4 adjacent pairs). Geographic practice total **200** (`74 + 20 + 54 + 28 + 24`). Ordinary components **686** (`486 + 200`). Independent FY2024/FY2026 arithmetic from accepted snapshots, including residual = `ΔP − ΣΔsegment − Δreconciling` and residual = `−Δifop_diff`, at maximum absolute error **0.0**:

| Quantity | Value |
|---|---|
| Americas operating-profit amount change FY2024 | `433444.0` |
| China Mainland amount change FY2024 | `140451.0` |
| Rest of World amount change FY2024 | `98628.0` |
| Aggregate reconciling amount change FY2024 | `131745.0` |
| Consolidated operating-profit amount change FY2024 | `804268.0` |
| Amount-change residual FY2024 | `0.0` (`804268 − (433444 + 140451 + 98628) − 131745`) |
| Americas operating-profit amount change FY2026 | `-454899.0` |
| China Mainland amount change FY2026 | `191264.0` |
| Rest of World amount change FY2026 | `30955.0` |
| Aggregate reconciling amount change FY2026 | `-62402.0` |
| Consolidated operating-profit amount change FY2026 | `-295082.0` |
| Amount-change residual FY2026 | `0.0` (`-295082 − (-454899 + 191264 + 30955) − (-62402)`) |
| Maximum bridge / `−Δifop_diff` identity error | `0.0` |
| Opening FY2022 amount changes / residual | `None` |

Workbook Check on the admitted Lululemon geographic pair: **686** (`486 + 74 + 20 + 54 + 28 + 24`). Blank then formula-filled correct; authenticated source/formula tamper still rejects without disclosure. Store fixture **702** (`486 + 200 + 8 + 8`). Mixed selected 2/4 Check **704**. Selected-document compsales Check **696**. Fast Retailing **577**. Geo sources/practice **56/200**. Preserved **486**. Unavailable **101**. Segment-margin formulas **15**.

Relocated cross-sheet/nonadjacent geographic operating-profit sources produce amount-change formulas from mapped current/prior ifop cells, and reconciling amount-change formulas from mapped signed monetary contributions, rather than adjacent columns or rounded margins.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Geographic amount-change APIs; learner segment/reconciling/consolidated amount-change and residual schedule; FY2024 Americas amount change `433444.0` / residual `0.0` and FY2026 Americas amount change `-454899.0` / residual `0.0`; identity error **0.0**; Check **686**; geographic analysis+workbook **21 passed**; focused required suite **1500 passed**; complete `core/tests` **3235 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Zero current/prior revenue does not suppress available profit amount changes; unaffected mix/within remain `UNDEFINED_RATIO` where required; losses, zeros, negative changes, and signed reconcilers; family transition uses aggregate signed sums; relocated amount-change formulas follow mapped ifop sources and signed contributions; tamper still authenticated; store fixture **702**; mixed selected 2/4 Check **704**; selected-document compsales Check **696**; Fast Retailing **577**; geo **56/200**; preserved **486**; unavailable **101** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 segment-margin formulas; signed item-level bridges; revenue-growth contributions; operating-margin contribution bridge; mix/within midpoint decomposition |
| Not claimed | Excel engine recalculation; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py -q --tb=short` | 0 | **21 passed** in **5.21s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1500 passed** in **43.40s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3235 passed**, **0 failed** in **272.52s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/geographic_segment.py` | `f24284d5919fb29661daa1d474b0e2e579e5c967165bd7ac01573fc6182c8a67` | 32292 |
| `core/engine/component_catalog.py` | `39ec31ad0d413c748f56e4c1d33799d31427200f15be3eaa16428c447ac44acd` | 287980 |
| `core/engine/reference_model.py` | `be1f434c85085c065ceb06c86f491cce4fd98dcc04a4e870c2dd1f9af32842c1` | 413366 |
| `core/model/historical_expected.py` | `429ec3f8b63ba60c0fc0f3a0df1f0feba0faeb4ecac0d913c0701f9ace1326ee` | 68447 |
| `core/tests/test_geographic_segment_analysis.py` | `ef6c94c734af6eebe8386208bc6dc1e4fa6d63e2f9641ee1eb54ff234e5f5426` | 52612 |
| `core/tests/test_geographic_segment_workbook.py` | `3ae8e8565d31fe7ac466de2ca3a1c03547adb7f3579e72e8b5b56729fb822449` | 104404 |
| `core/tests/test_operating_kpi_workbook.py` | `a97ea7738c68bf6c11bcc152038cbc2cd950f8bffb59209b1aef83eef162d15b` | 159571 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Eligible geographic snapshots now expose identity-specific adjacent operating-profit amount changes, aggregate reconciling amount change, consolidated amount change, and a signed residual.

---

## Remaining scope

This child adds a geographic operating-profit amount-change bridge on the accepted Geographic Analysis Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.57` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic baseline **74**, prior increment’s **20** revenue-growth contribution identities, prior increment’s **54** margin-bridge identities, and prior increment’s **28** mix/within identities reported separately from this increment’s **24** amount-change identities (**200** combined); Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales and revenue/SPSF relationship identities remain when eligible. Management-history adjacent-change and SPSF practice remain when eligible selections exist, reported separately from the previous **678**-cell store fixture, which is now **702** with this increment’s geographic amount-change identities. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, revenue/SPSF, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
