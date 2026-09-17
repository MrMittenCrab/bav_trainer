# RESULT.md — Step 9M.2.4.1.1.1.56 Geographic Analysis: consolidated operating-margin contribution bridge

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.56 — Geographic Analysis — Consolidated operating-margin contribution bridge  
**Work:** `dccd3e31cefd448b893c791d843be663`  
**Plan:** `bed6fd33269d421e9b9e358d31c7dd9b`  
**Finding:** `geographic-consolidated-operating-margin-bridge`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted revenue-growth contribution work `e30ce840b284400daa0a26d87483948f` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `53a04f982d5300548d9124f49926c585985ebbf2249aa2ffd7b1911a7d1ca81a` (9755).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance.

Interrupted working-tree edits were present on the seven allowed code/test files and were inspected, preserved, finished, and reverified. `core/trainer/checker.py` required no edits (catalog-driven family IDs).

## Required plan change

No required plan change. IMPLEMENTATION.md already lists `core/tests/test_operating_kpi_workbook.py` among allowed files.

Working-tree HEAD is `bf2b34c337306fcce2eb0ce693145714c1feb351`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Task 1 — Compute the operating-margin bridge

`GeographicSegmentSeries` now carries identity-specific `operating_margin_contribution` (percentage points), aggregate `reconciling_operating_margin_contribution`, `consolidated_operating_margin`, signed `operating_margin_contribution_residual`, immediately adjacent changes of each, and signed `operating_margin_contribution_change_residual`. Segment contributions are `100 * segment_operating_profit / consolidated_revenue`. Aggregate reconciling contribution is `100 * sum(existing_signed_reconciling_amounts) / consolidated_revenue`. Consolidated margin is `100 * consolidated_operating_profit / consolidated_revenue`. Residual is `M − sum(C_s) − B` and is never forced to zero.

Opening changes remain `None`. Missing adjacent snapshots yield `SOURCE_UNAVAILABLE` without compressing gaps. Missing dependencies take precedence over zero-denominator handling. Zero required consolidated revenue is `UNDEFINED_RATIO`. Zero segment revenue does not suppress a valid contribution. Signed profits, reconcilers, losses, and residuals are preserved. Explicit ADD/SUBTRACT bridge operations are reused without combining corporate-column and itemized identities. Existing mix, growth, segment margins, revenue-growth contributions, signed bridges, validation, and comparability boundaries are unchanged.

---

## Task 2 — Integrate learner practice and Check

Geographic Segment Analysis now includes the operating-margin contribution bridge and the adjacent-change bridge. Reported geographic revenues, operating profits, and existing signed reconciling sources stay populated; formulas resolve mapped current/prior source and practice cells after relocation, including cross-sheet/nonadjacent placements and existing signed reconciling components. Labels identify percentage-point arithmetic decomposition of reported operating margin and its change and disclaim BAV NOPAT margin, mix, within-segment, normalization, and causal attribution.

Generated pair remains exactly two workbooks. Trainer practice cells are blank bright-yellow without formulas, answers, or Notes. Answer-Key counterparts are ordinary white/no-fill with nonempty arithmetic Notes. Aptos Narrow 11 non-bold black typography is unchanged. Missing adjacent dependencies produce non-practice unavailable displays; eligible undefined ratios remain practice. Accepted mix, growth, segment margins, revenue-growth contributions, signed bridges, and operating-KPI disclosure behavior are retained.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Supplied-filing reconciliation → standardization → export/reload → ordinary geographic workbook fixture remains five canonical periods with **56** selected geographic sources. New practice identities this increment: **54** (3 segment contributions + aggregate reconciling contribution + consolidated margin + residual on each of 5 snapshots, plus 3 segment contribution changes + reconciling change + consolidated-margin change + change residual on each of 4 adjacent pairs). Geographic practice total **148** (`74 + 20 + 54`). Independent FY2024/FY2026 arithmetic from accepted snapshots within `1e-12`, including `ΔE` equality:

| Quantity | Value |
|---|---|
| Canonical revenue/IFOP FY2024 | `9619278` / `2132676` |
| Americas IFOP FY2024 | `2937184` |
| Americas contribution FY2024 | `100 * 2937184 / 9619278` = `30.534349875323283` |
| China Mainland contribution FY2024 | `3.506666508650649` |
| Rest of World contribution FY2024 | `2.0982032123408847` |
| Aggregate reconciling contribution FY2024 | `100 * (-1343656) / 9619278` = `-13.968366440807719` |
| Consolidated reported operating margin FY2024 | `100 * 2132676 / 9619278` = `22.170853155507096` |
| Residual FY2024 `E` | `-1.7763568394002505e-15` (within `1e-12` of `0`) |
| Americas contribution change FY2024 | `-0.33593485864808414` |
| Change residual FY2024 `ΔE` | `-3.552713678800501e-15` (within `1e-12` of `0`) |
| Americas contribution FY2026 | `100 * 2560658 / 11102600` = `23.06358870895106` |
| Residual FY2026 `E` | `-7.105427357601002e-15` (within `1e-12` of `0`) |
| Change residual FY2026 `ΔE` | `-6.217248937900877e-15` (within `1e-12` of `0`) |
| Opening FY2022 contribution changes / `ΔE` | `None` |

Workbook Check on the admitted Lululemon geographic pair: **634** (`486 + 74 + 20 + 54`). Blank then formula-filled correct; authenticated source/formula tamper still rejects without disclosure. Store fixture **650** (`486 + 148 + 8 + 8`). Mixed selected 2/4 Check **652**. Selected-document compsales Check **644**. Fast Retailing **577**. Geo sources/practice **56/148**. Preserved **486**. Unavailable **101**. Segment-margin formulas **15**.

Relocated cross-sheet/nonadjacent geographic revenue, operating-profit, and signed reconciling sources produce contribution, reconciling-contribution, consolidated-margin, residual, adjacent-change, and change-residual formulas from mapped cells rather than adjacent columns.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Geographic operating-margin contribution APIs; learner margin-bridge and adjacent-change schedule; FY2024 Americas `30.534349875323283` / residual within `1e-12` of `0` and FY2026 Americas `23.06358870895106` within `1e-12`; Check **634**; geographic analysis+workbook **20 passed**; focused required suite **1499 passed**; complete `core/tests` **3234 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Zero current/prior consolidated `UNDEFINED_RATIO`; zero segment revenue still contributes; losses and signed reconcilers; family transition; relocated contribution/reconciling/residual/change formulas follow mapped identities; tamper still authenticated; store fixture **650**; mixed selected 2/4 Check **652**; selected-document compsales Check **644**; Fast Retailing **577**; geo **56/148**; preserved **486**; unavailable **101** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 segment-margin formulas; signed item-level bridges; revenue-growth contributions |
| Not claimed | Excel engine recalculation; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py -q --tb=short` | 0 | **20 passed** in **4.81s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1499 passed** in **42.23s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3234 passed**, **0 failed** in **272.20s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/geographic_segment.py` | `63448dcd06cd78553cb063c86ab3f429241bce2679049b8aabe381df795b8070` | 22912 |
| `core/engine/component_catalog.py` | `548e0258a2a9272780b35a63307e77e835d89de54fa14824852b0171ddb715f8` | 268042 |
| `core/engine/reference_model.py` | `01995d49ca1d1fa87d73e02fa30acf75eede4afc8a9ae2e37fa446163af27d3e` | 397338 |
| `core/model/historical_expected.py` | `0276ca8a236214c9ece6f35fb746f66f74885361947f33c343a6aae7a2f74064` | 67029 |
| `core/tests/test_geographic_segment_analysis.py` | `875bd610ca4f6983fbf7960df06847646cd929cb1196e1e5d422dd632058e405` | 34501 |
| `core/tests/test_geographic_segment_workbook.py` | `4d715d5b2b67326b17932b4374e6b87204561043b0fcaca11dc825809d3d321c` | 74046 |
| `core/tests/test_operating_kpi_workbook.py` | `5f43381bb03370fb36ffc3c1b9135c00af638c08d59e2945a8a337d1e09f9898` | 159431 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Eligible geographic snapshots now expose identity-specific percentage-point contributions to consolidated reported operating margin, aggregate reconciling contribution, adjacent changes, and signed residuals.

---

## Remaining scope

This child adds geographic contributions to consolidated reported operating margin and its adjacent change on the accepted Geographic Analysis Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.55` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic baseline **74** and prior increment’s **20** revenue-growth contribution identities reported separately from this increment’s **54** margin-bridge identities (**148** combined); Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales and revenue/SPSF relationship identities remain when eligible. Management-history adjacent-change and SPSF practice remain when eligible selections exist, reported separately from the previous **596**-cell store fixture, which is now **650** with this increment’s geographic margin-bridge identities. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, revenue/SPSF, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
