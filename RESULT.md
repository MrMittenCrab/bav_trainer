# RESULT.md — Step 9M.2.4.1.1.1.53 Operating KPIs: management-history workbook integration

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.53 — Operating KPIs — Management-history workbook integration  
**Work:** `4902dbbb9a984ccab8e5bdf2dd7b4ed5`  
**Plan:** `ab5278e2ba514a50b2d9cc580aebaccb`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `7a2247e454d6a7c9d371e15d4f6340878a9f839aa6106cc42f0f7f1c9903dfbb` (10032).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/engine/build_contract.py`, `core/model/historical_expected.py`, `core/trainer/workbook.py`, `core/trainer/checker.py`, `core/trainer/check_context.py`, `core/tests/test_operating_kpi_workbook.py`, and `RESULT.md`. The accepted `compute_management_kpi_series` API is consumed unchanged. Other supported revenue relationships remain unfinished.

No required plan change.

Working-tree HEAD is `9f6b2a2c0c00442ce2a94928e983d98222dad6dc`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Task 1 — Register identity-specific histories and analytical dependencies

`_prepare_operating_kpi` now consumes `compute_management_kpi_series` on the canonical annual axis independently of store-count and revenue-relationship eligibility. Absent/null/store-only payloads and unselected documentary observations do not activate management schedules.

Full management identities stay isolated with deterministic API order. Reported sources are registered separately from practice. Existing `operating_kpi_comparable_sales_source` identities are reused when the accepted revenue/comparable-sales relationship already registered the same identity/period; revenue-growth practice is not duplicated.

New components:

- practice `operating_kpi_comparable_sales_adjacent_change` (percentage points = current − prior reported percent; not growth of growth);
- populated `operating_kpi_sales_per_square_foot_source` (`USD_per_square_foot`, no statement monetary scaling);
- practice `operating_kpi_sales_per_square_foot_change` and `operating_kpi_sales_per_square_foot_growth` (`(current-prior)/prior`).

Opening `None`, canonical gaps, explicit `SOURCE_UNAVAILABLE` reasons, and non-practice unavailable outputs are preserved. Zero-prior `UNDEFINED_RATIO` remains practiced with `NA()`. Semantic discontinuities keep current reported values and suppress dependent practice without bridging.

---

## Task 2 — Generate and verify matched learner surfaces

Store fixture without management selection still has counts `574/655/711/767/811`, changes `None/81/56/56/44`, five count sources, eight store practice identities, five revenue sources and eight revenue/store practice identities. Check total remains **576**. Unavailable displays remain **101**. Fast Retailing remains **577**. Geographic remains **56** facts / **74** additions. Preserved non-store/non-relationship identities remain **486**.

Temporary selected-document augmentations (not supplied documentary facts):

| Fixture | Independent arithmetic | Check delta |
|---|---|---|
| Selected compsales `2/7` + SPSF `1410/1430` | adjacent change `5` pp; SPSF change `20`; growth `20/1410` | +1 compsales change, +2 SPSF practice, sources reused (compsales still **2**) |
| Mixed selected `2/4` | adjacent changes unavailable across the 2024 gap | difference practice stays **2**; Check **578** |

Independent cell arithmetic is within `1e-12`. Unchanged supplied management documents still yield 135 observations and zero selections.

Selected both-family Check total is **569** (`486+74+4` revenue-growth `+2` differences `+1` adjacent-change `+2` SPSF). Mixed selected Check total remains **578** (`576+2`). Trainer practice cells are blank bright yellow without Notes. Answer-Key counterparts contain linked formulas, nonempty Notes, ordinary white/no-fill, and no yellow anywhere. Labels distinguish reported, statement-derived, and analyst-derived measures. Reported `2` displays as 2%; adjacent change is percentage points; SPSF retains `USD_per_square_foot`.

A generated pair with physically moved comparable-sales and SPSF sources onto Income Statement was saved, reloaded, and inspected from sidecar JSON and worksheet cells. Adjacent-change and SPSF formulas follow mapped identities, including cross-sheet qualification. Adjacent-column coordinates are absent. Check blank equals total; tampering a moved SPSF source raises authenticated `Trusted workbook cell was modified`. Spreadsheet engine recalculation was not performed.

Absent/null/store-only histories omit management schedules. SPSF-only activates Sales per Square Foot Analysis without the comparable-sales relationship. Regional/constant-dollar comparable-sales identities populate sources without revenue-difference practice. Singleton histories populate current sources without opening change/growth practice. Sparse KPI gaps stamp `SOURCE_UNAVAILABLE` and do not practice dependent cells. Zero prior SPSF keeps `UNDEFINED_RATIO` / `NA()`. Declines and qualifier-order equivalence are preserved. Invalid `period_kind` and negative SPSF fail closed at historical construction without mutation. Multiple isolated identities produce separate source and change components.

---

## Task 3 — Run regressions and record measured evidence

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Management-KPI workbook identities, semantic adjacent-change and SPSF source links, generated-workbook moved compsales+SPSF placement through ordinary `build_training_workbook` + save/reload, sidecar/embedded mapping inspection, independent arithmetic within `1e-12` for selected `2/7` (`5` pp) and `1410/1430` (change `20`, growth `20/1410`), Check blank/correct/incorrect + moved-SPSF tamper, focused workbook **42 passed**, focused required suite **1417 passed**, complete `core/tests` **3221 passed / 0 failed / 3221 collected**, checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**, eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Augmented five-period admit `2022-01-30` without management selection keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, store practice **8**, store sources **5**, relationship practice **8**, revenue sources **5**, geo **56/74**, preserved **486**, total practice **576**, unavailable **101**, Americas `7928156`; Fast Retailing **577**; mixed deferred documents 135/9/107/0 selections; mixed selected 2/4 keeps **2** compsales sources and **2** difference practice with **0** adjacent-change practice (Check **578**); selected 2/7 + SPSF 1410/1430 Check **569** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Historical, not this child | Prior revenue/comparable-sales workbook child focused **39** / complete **3218** |
| Not claimed | Excel engine recalculation; other supported revenue relationships; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py -q --tb=short` | 0 | **42 passed** in **22.02s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_reference_integrity.py::test_cli_assumptions_propagate -q --tb=short` | 0 | **1417 passed** in **39.41s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3221 passed**, **0 failed**, **3221 collected** in **274.56s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/component_catalog.py` | `df06d89ec3e6ae0c399ecf330a6c14cb4664ac6f6c00c5ab6f0bc722ce450b55` | 236913 |
| `core/engine/reference_model.py` | `8080f1519add616c9fd5f3b2f59b8df2ae41b190b8ff4bf81535b659da753bc8` | 357413 |
| `core/engine/build_contract.py` | `3c063c53d638f5e97a05db41b0fe319f513793be5c471c4122f91370e765114e` | 9941 |
| `core/model/historical_expected.py` | `727f4f2de4f76978483b624f0387fb866f69155030abd16575a8c7309113b136` | 62822 |
| `core/trainer/workbook.py` | `6c7cdfeee4a43066631e9116720a88c2ab51ed43ff78d3adcb8986b9e5a0254b` | 16939 |
| `core/trainer/checker.py` | `9a0e424230b5d4d6c2e9752589c5bd2aa7cc328f9b7045ae48450be036a72c7e` | 22291 |
| `core/trainer/check_context.py` | `65438c1b24c846b57577671d4605b7175bba82e7ad106f5f16a552c239afd032` | 28315 |
| `core/tests/test_operating_kpi_workbook.py` | `5b31979c783421df0b034ec3830a562995f12af9be60829f42d33fe83acc0b34` | 143645 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated management histories now expose identity-specific reported sources and eligible adjacent-period practice with semantic source mapping, including generated-workbook formulas that follow moved comparable-sales and SPSF source cells.

---

## Remaining scope

This child integrates accepted comparable-sales adjacent-change and sales-per-square-foot histories into the historical Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.52` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales relationship identities remain when eligible. This increment adds identity-specific management adjacent-change and SPSF practice only when eligible selections exist, reported separately from the **576**-cell store fixture. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected management observations that pass those gates now produce the learner schedules; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
