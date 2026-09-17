# RESULT.md — Step 9M.2.4.1.1.1.51 Operating KPIs: revenue/store-growth workbook integration

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.51 — Operating KPIs — Revenue/store-growth workbook integration  
**Work:** `fdb87e7c4ea54d4c9b77dbb5e589fe6c`  
**Plan:** `e07fd62751d447d79236fbad9dd855c2`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `bfd0b180a2555b910f739c90025da82405071c45a1da9a7d652e2473e9ce193d` (9442).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/workbook.py`, `core/trainer/checker.py`, `core/tests/test_operating_kpi_workbook.py`, and `RESULT.md`. The accepted `compute_operating_kpi_revenue_store_relationship` API is consumed unchanged. Management and comparable-sales workbook integration remain unfinished.

No required plan change.

Working-tree HEAD is `97b7d21a4def659d98a3bfd1720e35792cfe349b`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Task 1 — Register the optional relationship and semantic dependencies

`_prepare_operating_kpi` now consumes `compute_operating_kpi_revenue_store_relationship` on the canonical annual axis whenever store-count histories apply. Non-practice consolidated-revenue source identities are registered before formula resolution. Store-count growth practice is reused, not duplicated. Revenue sources and store-count sources are excluded from Check totals.

New identities on Store Count Analysis:

- populated `operating_kpi_revenue_source` (consolidated revenue);
- practice `operating_kpi_revenue_growth` (statement-derived `(current-prior)/prior`);
- practice `operating_kpi_revenue_store_growth_difference` (analyst-derived `100*(revenue_growth-store_count_growth)` percentage points).

Opening `None` and missing-input `SOURCE_UNAVAILABLE` stay non-practice. Zero-denominator `UNDEFINED_RATIO` remains practiced with `NA()`. Missing-input unavailability takes precedence in the difference. Cross-sheet semantic A1 qualification is used when a mapped dependency lives on another tab.

---

## Task 2 — Generate and verify the matched learner surfaces

Source-grounded Lululemon admit `2022-01-30` still has counts `574/655/711/767/811`, changes `None/81/56/56/44`, five count sources and eight store practice identities. Relationship additions are separate: five populated revenue sources and eight relationship practice identities. Check total is **576** (`568+8`). Unavailable displays remain **101**. Fast Retailing remains **577**. Geographic remains **56** facts / **74** additions. Preserved non-store/non-relationship identities remain **486**.

Independent cell arithmetic within `1e-12`:

| Period | Revenue growth `(current-prior)/prior` | Store growth | Difference `100*(rev-store)` |
|---|---:|---:|---:|
| 2023-01-29 | 0.2963104502001641 | 0.1411149825783972 | 15.51954676217668 |
| 2024-01-28 | 0.1860251096169196 | 0.08549618320610687 | 10.05289264108128 |
| 2025-02-02 | 0.1007194095024595 | 0.07876230661040788 | 2.195710289205166 |
| 2026-02-01 | 0.04858971266492295 | 0.05736636245110821 | -0.877664978618526 |

Opening period is `N/A` / not practiced. Trainer relationship practice cells are blank bright yellow without Notes. Answer-Key counterparts contain linked formulas, nonempty Notes, ordinary white/no-fill, and no yellow anywhere. Visible A5 carries the accepted scope note (not a formula). Labels distinguish consolidated revenue from company-operated period-end counts and mark statement-derived vs analyst-derived measures. Trainer visible text does not disclose `(current-prior)/prior` or `100*(...)`.

Default layout maps revenue sources to `B20`–`F20`. A generated pair with physically moved revenue and count sources (`C28`/`F36`/`I28`/`L36`/`O28` and prior count placement `B32`/`E40`/`H32`/`K40`/`N32`) was saved, reloaded, and inspected from sidecar JSON, embedded `_ComponentMap`, and worksheet cells. Growth formulas follow mapped current/prior revenue cells; difference formulas follow mapped revenue-growth and store-growth cells. Adjacent-column and stale default coordinates are absent. Check blank `576/576/0/0`; filled-correct `576/576/0/0`; one injected wrong difference cached value yields incorrect `1` without disclosing `=999` or the answer formula. Tampering a moved revenue source raises authenticated `Trusted workbook cell was modified: Store Count Analysis`. Spreadsheet engine recalculation was not performed.

Absent/null/management-only histories still omit the schedule. Singleton histories populate sources without growth/difference practice. Sparse count gaps stamp difference `SOURCE_UNAVAILABLE` and do not practice it. Zero prior revenue keeps `UNDEFINED_RATIO` / `NA()`. Declines are preserved. Null last-period revenue fails closed at historical construction (`MissingHistoricalValueError`) without mutation. Ambiguous duplicate `revenue` concepts raise `AmbiguousLineError` without mutation.

---

## Task 3 — Run regressions and record measured evidence

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Revenue/store workbook identities, semantic current/prior and same-period store-growth links, generated-workbook moved revenue+count placement through ordinary `build_training_workbook` + save/reload, sidecar/embedded mapping inspection, independent relationship arithmetic within `1e-12`, Check blank/correct/incorrect + moved-revenue tamper, focused **222 passed**, complete `core/tests` **3207 passed / 0 failed / 3207 collected**, checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**, eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Augmented five-period admit `2022-01-30` keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, store practice **8**, store sources **5**, relationship practice **8**, revenue sources **5**, geo **56/74**, preserved **486**, total practice **576**, unavailable **101**, Americas `7928156`; Fast Retailing **577**; mixed deferred documents 135/9/107/0 selections; management/comparable-sales workbook surfaces still absent |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Historical, not this child | Prior store-count workbook child focused **217** / complete **3202**; revenue/store-relationship API child focused **1193** / required **2144** |
| Not claimed | Excel engine recalculation; management or comparable-sales workbook/Check surfaces; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py -q --tb=short` | 0 | **28 passed** in **11.52s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_reference_integrity.py::test_cli_assumptions_propagate -q --tb=short` | 0 | **222 passed** in **24.51s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3207 passed**, **0 failed**, **3207 collected** in **258.04s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/component_catalog.py` | `f9ffaca9cca0efab74873cd7d67965f535e1980856f1f8ce45bc7199b1f8822f` | 208024 |
| `core/engine/reference_model.py` | `fd7338b50236e88d53acc7fbf81c405bae15d7f8c45ac77ff9302cfe914baff5` | 309894 |
| `core/model/historical_expected.py` | `155b7ffad470cf814e9a23d83496092cbc40b4e70a1399f1ac508720349f32de` | 57858 |
| `core/trainer/workbook.py` | `d79f0b4126195deb6e1685b51caa00711ba4e9697debe543ddb2e3acb086faf0` | 16693 |
| `core/trainer/checker.py` | `9c0f7511e856e950a3e271159227d3a1cd170c83a887decee439d048f412a495` | 20672 |
| `core/tests/test_operating_kpi_workbook.py` | `8020cd733e07183fc94cab6ff78e07b9c8506231f1a11aeca6c56a647c7ae0b3` | 87906 |

Unedited permitted files this child: `core/engine/build_contract.py` SHA-256 `f9be68daac881e0efa4ab37b96dfdb55a48a0b4d1b0d9e367271fc5423797cc1` (9508); `core/trainer/check_context.py` SHA-256 `73b4d18ede31136225e19f61d7016921d841a30f222090764c1c2e4a976dc767` (26518); `core/tests/test_build_cli.py` SHA-256 `5429dfc12eeb7dcc60c241c2039f4d82115bf8a1740b7bb6e24fe4e1297a54e0` (10030).

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated store-count histories now expose a revenue/store-growth comparison with semantic source mapping, including generated-workbook formulas that follow moved revenue and count source cells; management and comparable-sales workbook integration remain unfinished.

---

## Remaining scope

This child integrates the accepted consolidated-revenue/company-operated-store-growth relationship into the historical Trainer/Answer-Key/Check path. Management-KPI learner schedules, comparable-sales workbook integration, other supported revenue relationships, and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.50` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. Prior increment added **8** store-count practice identities and **5** non-practice count sources. This increment adds **8** relationship practice identities and **5** non-practice revenue sources on source-bound store fixtures only, reported separately from the previous **568**-cell augmented fixture (now **576** Check cells). G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store and revenue/comparable-sales relationship APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected store-count observations that pass those gates now produce the learner schedule and the revenue/store-growth comparison; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
