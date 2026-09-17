# RESULT.md — Step 9M.2.4.1.1.1.50 Operating KPIs: store-count learner schedule and Check

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.50 — Operating KPIs — Store-count learner schedule and Check integration  
**Work:** `a486cad27960408bb13d183bbf863bba`  
**Plan:** `56656f9f222f41fc86fedbefca81fd98`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `42bcc1b0f846c25ddd333f870e62b7d02f1f5a1661e233f32db2fbd9390aec4c` (9652).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/engine/component_catalog.py`, `core/engine/build_contract.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/checker.py`, `core/trainer/check_context.py`, `core/tests/test_operating_kpi_workbook.py`, and `RESULT.md`. Existing store analytics, management, and revenue-relationship APIs were not redesigned.

No required plan change.

`.git/autocycle/latest-implementation` currently references `HEAD: 747b1eed1298a1f400bc504094564f3d605211d3` and log `cursor-20260917-123301-34838.log` and was not rewritten. That pointer is a historical controller artifact, not this increment's acceptance. Working-tree HEAD is `d45416ccbbd588f1df76fa3ae29ba93ed244d043`.

Validated company-operated store-count histories now produce an optional `Store Count Analysis` schedule through the ordinary builder. Reported period-end counts and units stay populated. Adjacent net count change and count growth are semantic practice families. Absent, null, and management-only histories add no store schedule, practice identities, or Check expectations. Deferred supplied management documents still cannot supply store-count inputs.

---

## Task 1 — Integrate the optional reference schedule

`STORE_COUNT_COMPONENT_CATALOG` and `expand_store_count_specs` sit in `core/engine/component_catalog.py`. The optional module is registered in `BUILD_MODULES` as `_integrated("operating_kpi", (OPERATING_KPI,))`. `_prepare_operating_kpi` activates only when `operating_kpi_applicable` is true.

Reported counts and count units are written as source cells. Practice identities exist only for adjacent net count change and count growth when both immediately adjacent observations exist. Opening change/growth display `N/A` and are not practiced. Missing adjacent snapshots display `Source unavailable` and are not practiced. Zero prior count keeps the existing `IF(prior=0,NA(),…)` undefined-ratio convention. Formulas resolve through the populated count-row identities (`=C{count}-B{count}` and the matching growth ratio), not hardcoded catalog coordinates.

Changes are labeled net count changes. Population is labeled `company-operated`. Count units remain independent of monetary scale. Malformed contracts and noncanonical axes raise without mutation.

---

## Task 2 — Complete Trainer, Answer Key and Check behavior

Ordinary `build_training_workbook` emits exactly two matching workbooks. Source counts stay populated on both. Trainer practice cells start blank bright yellow without Notes. Answer-Key counterparts contain linked formulas and nonempty Notes with ordinary white/no-fill and no yellow. Visible structure and typography remain shared. Formula instructions stay only in the Answer Key.

Every active store practice identity has independent `operating_kpi_expected_value_for_component` lookup and workbook-wide Check. Blank/correct/incorrect feedback does not print answers, formulas, or hints. Check-context trusted-sheet validation covers `Store Count Analysis` whenever the sheet is present, including singleton histories with no practice cells. Source-count edits raise `Trusted workbook cell was modified: Store Count Analysis`. Intended learner edits remain allowed.

---

## Task 3 — Verify ordinary handoff and preservation

`core/tests/test_operating_kpi_workbook.py` exercises reconciliation → standardization → export/reload → reference model → Trainer/Answer Key → Check with existing source-bound store fixtures (`_validated_augmented` temporary copies). Fixture-added store facts are identified separately from supplied source facts.

Independently verified on the five-period admitted axis:

- counts `574/655/711/767/811`
- net changes `None/81/56/56/44`
- growth within `1e-12`
- exact active store identities **8** (4 net change + 4 growth)
- formulas, Notes, styling, blank/correct/incorrect Check
- sparse/singleton histories, missing inputs, zero denominators, declines, `ones`/`stores` round trip, monetary-scale invariance
- absent/null/management-only parity, invalid-contract fail-closed, source tampering
- committed Lululemon **486** and Fast Retailing **577** unchanged
- augmented Lululemon preserves geo **56** facts / **74** additions and prior **486**; total practice **568** = 486 + 74 + 8
- unavailable displays remain **101**
- management and revenue-relationship APIs unchanged

Mixed vs annual-only supplied-source counts remain: 135 observations (`29/36/37/33`), nine definitions, 107 market-table observations, three excluded targets, assessments `0/22/6/107` comparability with supported/outside `28/107`, 24 incompatible pairs, six singletons, zero revision links/selections.

---

## Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent mixed-directory load of supplied extracted inputs (admit `2022-01-30`):

- 4 statement filings (FY2022–FY2025) + 4 management documents vs annual-only 4+0
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- 107 market-table store observations
- 3 nonhistorical targets
- status `admitted_unreconciled`; model-facing canonical selection `deferred`
- assessments: **135** items; **28** supported, **107** outside_scope, **0** unsupported_variant
- comparability: comparable **0**, not_comparable **22**, unresolved **6**, outside_scope **107**
- reconciliation: pair_count **24**; agreeing_duplicate **0**; conflicting_candidate **0**; incompatible **24**; unresolved pairs **0**; singleton **6**; unsupported_variant **0**; outside_scope **107**
- supplied presentation/assurance/revision: `revision_links` **[]**; counts recognized/unresolved/incompatible **0/0/0**
- group selections: **28** identity-period groups, all `deferred`; selected **0**; superseded **0**
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed and annual-only `historical_operating_kpis is None`; store schedule specs `()`; management analytics absent (`MissingLineError: management KPI sources not available`); revenue/store relationship absent; comparable-sales relationship absent
- extracted JSON bytes immutable after the exercise

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Optional `Store Count Analysis` workbook schedule gated on validated store-count observations; populated reported counts/units; semantic net-change and growth practice; Answer-Key formulas/Notes; non-disclosing Check; singleton schedule without practice; sparse/zero/decline/unit/scale coverage; source tamper detection; ordinary-path handoff → reload → Trainer/Answer Key → Check with temporary store-prep fixtures; deferred supplied exclusion; mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets, 107 market-table; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; mixed `historical_operating_kpis is None` and no store schedule; focused workbook/Check/build-contract **195 passed**; complete `core/tests` **3180 passed / 3 failed / 3183 collected**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Augmented five-period admit `2022-01-30` keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, store additions **8**, geo **56/74**, preserved **486**, total practice **568**, unavailable **101**, Americas `7928156`; Fast Retailing **577**; pale-yellow/frozen tests remain in the complete suite; management/revenue-relationship APIs unchanged |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Historical, not this child | Prior comparable-sales child focused **1207** / required **2158**; revenue/store-relationship child focused **1193** / required **2144**; both-family-analytics child focused **1179** / required **2130**; selected-history-handoff child focused **1160** / required **2111** |
| Not claimed | Excel engine recalculation; management or revenue-relationship workbook/Check surfaces; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

Three complete-suite failures are outside this increment's permitted files and store-count acceptance. They fail before the store schedule runs:

- `test_root_readme_is_practical_trainer_guide` — root `README.md` lacks `## Quick start`
- `test_cli_assumptions_propagate` and `test_cli_build_reports_both_paths` — `python -m core build` on `example/DEMO_HK_Standardized.json` exits 1 with `standardized: unsupported field(s): metadata`

Ordinary `build_training_workbook` / `ReferenceModelBuilder` on the same DEMO ingest still succeeds and emits no store schedule. README and CLI JSON admission were not edited.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py -q --tb=short` | 0 | **10 passed** in **4.81s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py -q --tb=short` | 0 | **195 passed** in **17.22s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 1 | **3180 passed**, **3 failed**, **3183 collected** in **259.71s**. Failures are README `## Quick start` and DEMO CLI `metadata` admission, not store-count workbook/Check. |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory copies; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical / 107 market-table; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; std/conflicts/statement-provenance match; mixed and annual-only `historical_operating_kpis is None`; store specs `()`; management analytics, store relationship, and comparable-sales relationship absent; extracted JSON unchanged |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m core build example/DEMO_HK_Standardized.json -o /tmp/bav_demo_cli_check.xlsx` | 1 | `error: build failed: standardized: unsupported field(s): metadata` (pre-builder; no store schedule involved) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/component_catalog.py` | `a7f2a43bd32d4efc7f09775f0b9be8c4e90f00087af419e7f7a5ca2193952fa6` | 190972 |
| `core/engine/build_contract.py` | `f9be68daac881e0efa4ab37b96dfdb55a48a0b4d1b0d9e367271fc5423797cc1` | 9508 |
| `core/engine/reference_model.py` | `6e1c0ba2ab0487285b7149f375498435a64f4b1c44bfb7b36efb43d8c2b5b0cc` | 299223 |
| `core/model/historical_expected.py` | `7a870f579cd57c68df2c60260e683875c2b2d88ef018d8d3ff3a2dae154f8df8` | 55793 |
| `core/trainer/checker.py` | `d51b206c20671bde75431a3bb0fa1226f6f3a831edc29cac09006e0d44b4cce0` | 19688 |
| `core/trainer/check_context.py` | `73b4d18ede31136225e19f61d7016921d841a30f222090764c1c2e4a976dc767` | 26518 |
| `core/tests/test_operating_kpi_workbook.py` | `49f800f321edc5248859a9a815d0d9871787c41332169742f97233fa99829952` | 35627 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated store-count histories now expose a learner schedule; management and revenue-relationship workbook integration remain unfinished.

---

## Remaining scope

This child integrates company-operated period-end store counts into the historical Trainer/Answer-Key/Check path. Management-KPI learner schedules, revenue-relationship workbook integration, other supported revenue relationships, and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41`, `.42`, `.43`, `.44`, `.45`, `.46`, `.47`, `.48` and `.49` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. This increment adds **8** store-count practice identities on source-bound store fixtures only. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store and revenue/comparable-sales relationship APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected store-count observations that pass those gates now produce the learner schedule; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
