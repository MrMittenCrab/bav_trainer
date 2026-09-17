# RESULT.md — Step 9M.2.4.1.1.1.50 Operating KPIs: store-count learner schedule and Check

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.50 — Operating KPIs — Store-count learner schedule and Check integration  
**Work:** `a486cad27960408bb13d183bbf863bba`  
**Plan:** `736aac05666748f581744a4dfabde09c`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `6e6631f7c139c41c2e454a373c55cd99a1e9491ed8e0fd44d80e9589c9d14165` (10633).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/trainer/workbook.py`, `core/trainer/checker.py`, `core/tests/test_operating_kpi_workbook.py`, `core/data/standardized_io.py`, `README.md`, and `RESULT.md`. `core/engine/build_contract.py`, `core/model/historical_expected.py`, `core/trainer/check_context.py`, and `core/__main__.py` required no edits. Existing store analytics, management, and revenue-relationship APIs were not redesigned.

No required plan change.

Working-tree HEAD is `db6ac40ecc8aaa088890f61dfecbd83d1140cdfb`. `.git/autocycle/latest-implementation` was not rewritten.

Validated company-operated store-count histories produce an optional `Store Count Analysis` schedule through the ordinary builder. Reported period-end counts and units stay populated as period-specific semantic source identities. Adjacent net count change and count growth are semantic practice families whose formulas resolve from registered current/prior source cells, not from adjacent-column arithmetic. Absent, null, and management-only histories add no store schedule, store identities, or Check expectations. Deferred supplied management documents still cannot supply store-count inputs.

---

## Task 1 — Resolve store formulas through semantic sources

`STORE_COUNT_SOURCE_FAMILY` and `expand_store_count_source_specs` register period-specific source identities (`store_count_source__YYYYMMDD`, semantic key `operating_kpi.store_count.source.{period}`) with population `company-operated` and count-unit context. These identities are populated, non-practice, and excluded from Check totals.

`expand_store_count_specs` now sets `depends_on` to the current and immediately preceding canonical-period source identities. `_build_store_count` writes and registers every validated count source first, then resolves net-change and growth formulas through `resolve_store_count_net_change_formula` / `resolve_store_count_growth_formula` using `semantic_map.get(...)` cells. Column-index adjacency (`col_idx - 1`) is no longer the dependency-resolution mechanism.

Source gating is unchanged: absent/null/management-only histories add no schedule, store identities, or expectations. Singleton histories keep populated source identities without opening practice. Signed changes, reported zeros, count units independent of monetary scale, canonical gaps, unavailable dependencies, and zero-denominator `IF(prior=0,NA(),…)` behavior are retained.

---

## Task 2 — Prove dependency mapping and retained learner behavior

`core/tests/test_operating_kpi_workbook.py` now asserts exact source identities and dependency edges, source/practice separation, deterministic export/reload mapping, and unchanged non-KPI identities/expectations. `test_formula_resolution_follows_mapped_source_identities` perturbs source row and period-column placement, including nonadjacent columns (`E20` vs `B8`), and checks current-minus-prior direction independently of default layout.

Ordinary `build_training_workbook` still emits exactly two matching workbooks. Source counts stay populated on both and are not yellow. Trainer practice cells start blank bright yellow without Notes. Answer-Key counterparts contain linked formulas and nonempty Notes with ordinary white/no-fill and no yellow. Visible structure and typography remain shared. Formula instructions stay only in the Answer Key.

Independently verified on the five-period admitted axis:

- counts `574/655/711/767/811`
- net changes `None/81/56/56/44`
- growth within `1e-12`
- source identities **5**; exact active store practice identities **8** (4 net change + 4 growth)
- source identities do **not** inflate practice or Check totals
- formulas follow mapped source cells after ordinary save/reload
- sparse/singleton histories, missing inputs, zero denominators, declines, `ones`/`stores` round trip, monetary-scale invariance
- absent/null/management-only parity, invalid-contract fail-closed, source tampering
- committed Lululemon **486** and Fast Retailing **577** unchanged
- augmented Lululemon preserves geo **56** facts / **74** additions and prior **486**; total practice **568** = 486 + 74 + 8
- unavailable displays remain **101**
- management and revenue-relationship APIs unchanged

---

## Task 3 — Repair regression blockers and record verification

Root `README.md` heading `## Manual build` was restored to `## Quick start`. Supported `python -m core build` / `list` / `check` usage and the two-workbook practice flow remain; current scope statements were preserved.

DEMO CLI `metadata` rejection was traced to strict canonical validation treating `StandardizedFinancials.metadata` as an unsupported field and requiring a top-level `jurisdiction` that the protected DEMO fixture stores only under `metadata.jurisdiction`. `standardized_from_payload(..., strict=True)` now admits that supported metadata object, copies it, and fills jurisdiction from `metadata.jurisdiction` when the top-level field is absent. Unknown/malformed fields remain rejected. The protected DEMO fixture was not edited. `test_cli_assumptions_propagate` and `test_cli_build_reports_both_paths` now pass.

Prior RESULT claims that formulas “resolve through populated count-row identities” while still using `col_idx - 1` coordinate arithmetic are withdrawn. This increment’s evidence is identity lookup after source registration, plus an independent nonadjacent-layout resolver test.

---

## Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Period-specific store-count source identities; practice `depends_on` current/prior source IDs; formula resolution from mapped cells rather than adjacent-column arithmetic; layout-perturbation resolver test; source/practice/Check separation; singleton sources without practice; ordinary-path handoff → reload → Trainer/Answer Key → Check with temporary store-prep fixtures; README `## Quick start`; DEMO strict metadata/jurisdiction admission; focused workbook/Check/build-contract/CLI/README **199 passed**; complete `core/tests` **3184 passed / 0 failed / 3184 collected**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Augmented five-period admit `2022-01-30` keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, store practice additions **8**, store sources **5**, geo **56/74**, preserved **486**, total practice **568**, unavailable **101**, Americas `7928156`; Fast Retailing **577**; pale-yellow/frozen tests remain in the complete suite; mixed deferred documents 135/9/107/0 selections; management/revenue-relationship APIs unchanged |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Historical, not this child | Prior comparable-sales child focused **1207** / required **2158**; revenue/store-relationship child focused **1193** / required **2144**; both-family-analytics child focused **1179** / required **2130**; selected-history-handoff child focused **1160** / required **2111** |
| Not claimed | Excel engine recalculation; management or revenue-relationship workbook/Check surfaces; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py -q --tb=short` | 0 | **11 passed** in **4.90s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_reference_integrity.py::test_cli_assumptions_propagate -q --tb=short` | 0 | **199 passed** in **17.22s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3184 passed**, **0 failed**, **3184 collected** in **258.71s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m core build example/DEMO_HK_Standardized.json -o /tmp/bav_demo_cli_check.xlsx` | 0 | Trainer/Answer Key written; **312** components resolved; no store schedule |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/component_catalog.py` | `2b8ae30120593039e84dabd1737e28402e62aca3bc55fa8717dddc8ef8f7da8f` | 196976 |
| `core/engine/reference_model.py` | `e21f6d50fb539c14637d2aeff69dc8fcf72454cb25c998f049fc54ff47927963` | 301107 |
| `core/trainer/workbook.py` | `620d85eb758e1586b888fb46bef17590e2a99d74bac6d78456d2d1277089c5c5` | 16573 |
| `core/trainer/checker.py` | `fe1d594328bcb23618905533777c62808debf52ce4e64a0bb4c007b7f274114e` | 19801 |
| `core/tests/test_operating_kpi_workbook.py` | `843297919b2fdef8d2e6b562217965557013f17a25cb779f86f8c8c2ad802b21` | 43089 |
| `core/data/standardized_io.py` | `a092e0aac2c979bc6b04161e3aa7590354f0e78ee27caafe36ed232bea3ecaf5` | 23576 |
| `README.md` | `1870364e272d23389521b508c1dda3cfa8088ee6b92aff90caf2a2c3fa2745a1` | 4975 |

Unedited permitted files this child: `core/engine/build_contract.py` SHA-256 `f9be68daac881e0efa4ab37b96dfdb55a48a0b4d1b0d9e367271fc5423797cc1` (9508); `core/model/historical_expected.py` SHA-256 `7a870f579cd57c68df2c60260e683875c2b2d88ef018d8d3ff3a2dae154f8df8` (55793); `core/trainer/check_context.py` SHA-256 `73b4d18ede31136225e19f61d7016921d841a30f222090764c1c2e4a976dc767` (26518); `core/__main__.py` SHA-256 `a6864ea42c6b978bf2ccea2a4fcb10c76518502c8adc2d779672af50747a9e6a` (16007).

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated store-count histories now expose a learner schedule with semantic source mapping; management and revenue-relationship workbook integration remain unfinished.

---

## Remaining scope

This child integrates company-operated period-end store counts into the historical Trainer/Answer-Key/Check path with semantic source identities. Management-KPI learner schedules, revenue-relationship workbook integration, other supported revenue relationships, and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41`, `.42`, `.43`, `.44`, `.45`, `.46`, `.47`, `.48` and `.49` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. This increment adds **8** store-count practice identities and **5** non-practice source identities on source-bound store fixtures only. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store and revenue/comparable-sales relationship APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected store-count observations that pass those gates now produce the learner schedule; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
