# RESULT.md — Step 9M.2.4.1.1.1.52 Operating KPIs: revenue/comparable-sales workbook integration

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.52 — Operating KPIs — Revenue/comparable-sales workbook integration  
**Work:** `d8220596d27949c68111e0684164c787`  
**Plan:** `12f7cc5918724518a3e6f4cecb6fd516`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `a397bcbb85084ee0f556e6faa6cd93926dd15811d1f1eb8bf878f6134af346c4` (10239).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/engine/build_contract.py`, `core/model/historical_expected.py`, `core/trainer/workbook.py`, `core/trainer/checker.py`, `core/trainer/check_context.py`, `core/tests/test_operating_kpi_workbook.py`, and `RESULT.md`. The accepted `compute_operating_kpi_revenue_comparable_sales_relationship` API is consumed unchanged. General management-KPI workbook integration remains unfinished.

No required plan change.

Working-tree HEAD is `61f028b823efae2a1d06784d968951915bef340b`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Task 1 — Register the optional comparison and semantic dependencies

`_prepare_operating_kpi` now consumes `compute_operating_kpi_revenue_comparable_sales_relationship` on the canonical annual axis independently of store-count availability. Deferred, non-global, non-reported, and sales-per-square-foot histories do not activate it.

Shared consolidated-revenue source identities (`operating_kpi_revenue_source`) and statement-derived revenue-growth practice (`operating_kpi_revenue_growth`) are registered once. Mixed store+comparable-sales histories reuse the store-sheet identities; comparable-sales-only histories register the same shared identities on Comparable Sales Analysis. Sources never count as practice.

New identity-specific components, never merged or averaged:

- populated `operating_kpi_comparable_sales_source` (reported percent; 2 means 2%);
- practice `operating_kpi_revenue_comparable_sales_difference` (analyst-derived `100*revenue_growth-current_reported_comparable_sales_percent`).

Opening `None` and missing-input `SOURCE_UNAVAILABLE` stay non-practice. Zero-denominator `UNDEFINED_RATIO` remains practiced with `NA()`. Missing-input unavailability takes precedence in the difference. A missing prior KPI observation does not suppress an otherwise available current comparison. Cross-sheet semantic A1 qualification is used when a mapped dependency lives on another tab.

---

## Task 2 — Generate and verify matched learner surfaces

Store fixture without comparable-sales selection still has counts `574/655/711/767/811`, changes `None/81/56/56/44`, five count sources, eight store practice identities, five revenue sources and eight revenue/store practice identities. Check total remains **576**. Comparable-sales additions are reported separately. Unavailable displays remain **101**. Fast Retailing remains **577**. Geographic remains **56** facts / **74** additions. Preserved non-store/non-relationship identities remain **486**.

Temporary selected-document augmentations (not supplied documentary facts):

| Fixture | Compsales values | Independent revenue growth | Difference `100*growth-current%` |
|---|---|---:|---:|
| Selected 2/7 (compsales-only) | 2023=2, 2024=7 | 0.2963104502001641 / 0.1860251096169196 | 27.63104502001641 / 11.60251096169197 |
| Mixed selected 2/4 | 2023=2, 2025=4; 2024 unavailable | 0.2963104502001641 / 0.1007194095024595 | 27.63104502001641 / 6.071940950245954 |

Independent cell arithmetic is within `1e-12`. Adjacent percentage-point change and growth-of-growth are not substituted. Unchanged supplied management documents still yield 135 observations and zero selections.

Comparable-sales-only Check total is **566** (`486+74+4` revenue-growth `+2` differences). Mixed selected Check total is **578** (`576+2`); revenue-growth practice stays **4** (not duplicated). Trainer practice cells are blank bright yellow without Notes. Answer-Key counterparts contain linked formulas, nonempty Notes, ordinary white/no-fill, and no yellow anywhere. Visible A5 carries the accepted comparable-sales scope note (not a formula). Labels distinguish reported, statement-derived, and analyst-derived measures and retain definition, period kind, calendar adjustment, reporting basis, and qualifiers.

Default mixed layout keeps revenue sources on Store Count Analysis. A generated pair with physically moved revenue sources (`C28`/`F36`/`I28`/`L36`/`O28`) and comparable-sales sources relocated onto Income Statement (`D44`/`G52`/`J44`/`M52`/`P44`) was saved, reloaded, and inspected from sidecar JSON, embedded `_ComponentMap`, and worksheet cells. Difference formulas follow mapped revenue-growth and current reported comparable-sales cells, including cross-sheet qualification. Adjacent-column and stale default coordinates are absent. Check blank `578/578/0/0`; filled-correct `578/578/0/0`; one injected wrong difference cached value yields incorrect `1` without disclosing `=999` or the answer formula. Tampering a moved comparable-sales source raises authenticated `Trusted workbook cell was modified`. Spreadsheet engine recalculation was not performed.

Absent/null/store-only/ineligible/deferred/spsf histories omit the comparable-sales schedule. Singleton histories populate current sources without opening difference practice. Sparse KPI gaps stamp difference `SOURCE_UNAVAILABLE` and do not practice it; a missing prior KPI does not suppress a current comparison. Zero prior revenue keeps `UNDEFINED_RATIO` / `NA()`. Declines and fraction-like `0.08` percent scaling are preserved. Null last-period revenue fails closed at historical construction (`MissingHistoricalValueError`) without mutation. Ambiguous duplicate `revenue` concepts raise `AmbiguousLineError` without mutation. Multiple isolated identities produce separate source and difference components.

---

## Task 3 — Run regressions and record measured evidence

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Comparable-sales workbook identities, semantic revenue-growth and current reported comparable-sales links, generated-workbook moved revenue+compsales placement through ordinary `build_training_workbook` + save/reload, sidecar/embedded mapping inspection, independent relationship arithmetic within `1e-12` for selected `2/7` and mixed `2/4`, Check blank/correct/incorrect + moved-compsales tamper, focused workbook **39 passed**, focused required suite **1258 passed**, complete `core/tests` **3218 passed / 0 failed / 3218 collected**, checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**, eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Augmented five-period admit `2022-01-30` without compsales selection keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, store practice **8**, store sources **5**, relationship practice **8**, revenue sources **5**, geo **56/74**, preserved **486**, total practice **576**, unavailable **101**, Americas `7928156`; Fast Retailing **577**; mixed deferred documents 135/9/107/0 selections; mixed selected 2/4 adds **2** compsales sources and **2** difference practice (Check **578**); selected 2/7 compsales-only Check **566** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Historical, not this child | Prior revenue/store workbook child focused **222** / complete **3207** |
| Not claimed | Excel engine recalculation; general management-KPI workbook/Check surfaces; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py -q --tb=short` | 0 | **39 passed** in **19.85s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_reference_integrity.py::test_cli_assumptions_propagate -q --tb=short` | 0 | **1258 passed** in **33.63s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3218 passed**, **0 failed**, **3218 collected** in **271.80s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/component_catalog.py` | `28401e750e595bdf02a884587cfd44f168561835be8278374c6ce906e46396e9` | 219446 |
| `core/engine/reference_model.py` | `055e0bc38d51bea9edb50a0e2c909d107a1a906183e80418466f068bf3f4e4ad` | 332777 |
| `core/engine/build_contract.py` | `32e3661ee87263a8da78cf14f0720eca544b8e5d962d91ddad725bb398f116e1` | 9816 |
| `core/model/historical_expected.py` | `f245fdf3ee94e2e7b4ac57b14a68ae4ba7afd1e901d141d938c85e73db6c5fdd` | 60559 |
| `core/trainer/workbook.py` | `d755cde453bfe2e71e4406a8dbfcc491480b05df9038269bcc44c4d038c6eb39` | 16811 |
| `core/trainer/checker.py` | `a4db3a4fe4ca69f52c61ca79917898803f14d1a9866a8ba0f4342ee83cabb87d` | 21665 |
| `core/trainer/check_context.py` | `824d7e583b46d2ca55cec0c22e5c578805f11ef1f35deb8edeb2ef019e04784c` | 27404 |
| `core/tests/test_operating_kpi_workbook.py` | `32d6edda0d25a0c331750e13f8e918f3a42890e3e8f191368475782af70bfef5` | 120173 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated comparable-sales histories now expose a revenue/comparable-sales comparison with semantic source mapping, including generated-workbook formulas that follow moved revenue and comparable-sales source cells; general management-KPI workbook integration remains unfinished.

---

## Remaining scope

This child integrates the accepted consolidated-revenue/reported-comparable-sales relationship into the historical Trainer/Answer-Key/Check path. Management-KPI learner schedules, other supported revenue relationships, and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.51` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. This increment adds identity-specific comparable-sales sources and difference practice only when eligible selections exist, reported separately from the **576**-cell store fixture. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store and revenue/comparable-sales relationship APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected comparable-sales observations that pass those gates now produce the learner schedule and the revenue/comparable-sales comparison; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
