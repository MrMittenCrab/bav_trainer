# RESULT.md — Step 9M.2.4.1.1.1.40 Operating KPIs: supported observation duplicate and conflict reconciliation

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.40 — Operating KPIs: supported observation duplicate and conflict reconciliation  
**Work:** `6f7f2400babe4b87987f3ec5314e45a9`  
**Plan:** `09d89b38143d4988b968fefd4f82f496`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `8b9f79d5eaa71bb655b7c60e6d70e9b1971421d2b88501ad710c035d0f0a562b` (10453).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, canonical history selection, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi_reconciliation.py` (new), `core/ingestion/management_kpi.py`, `core/ingestion/management_kpi_identity.py`, `core/tests/test_management_kpi_reconciliation.py` (new), `core/tests/test_management_kpi_identity.py`, `core/tests/test_management_kpi_admission.py`, `core/tests/test_filing_cli.py`, and `RESULT.md`.

No required plan change.

Ordinary admission now serializes occurrence-preserving pairwise reconciliation for the two supported families. Supplied mixed inputs remain zero comparable, 22 not-comparable, six unresolved, and 107 outside-scope. Measured supplied pair outcomes are 24 incompatible, 0 unresolved pairs, 0 agreeing duplicates, and 0 conflicting candidates. Canonical selection remains deferred.

---

## Task 1 — Source-grounded pair reconciliation

Within each supported metric identity, ordinary admission emits exactly one unordered pair per distinct occurrence pair. Self-pairs are not created. Singleton, unsupported-variant, and outside-scope observations serialize as explicit coverage records. All source occurrences are retained.

Each pair is evaluated independently from the two members only. A third incomplete or incompatible peer does not suppress an otherwise valid same-period pair and does not establish transitive equivalence.

Fully evidenced same-period pairs with two supplied numeric values classify as `agreeing_duplicate` when values agree exactly, or `conflicting_candidate` when they differ. No rounding tolerance, unit conversion, or missing-to-zero coercion is applied. Missing values, including missing versus reported zero, prevent duplicate/conflict classification.

Evidenced definition, calendar, and period incompatibility classifies as `incompatible`, separately from value conflict. Missing required evidence prevents agreement or conflict. Dimension-specific local and `peer_*` gaps are retained alongside proven incompatibility. Cross-year affirmative comparability remains `comparable` in assessments; those pairs are `incompatible` with `period_mismatch` and are not treated as duplicates.

Status remains `admitted_unreconciled`. Canonical selection remains deferred. Equal values, filing recency, extracted preferred values, and matching labels do not establish precedence or restatement.

---

## Task 2 — Ordinary-admission regressions

Independent mutations through ordinary admission, both families:

- same-period equal values: pair `agreeing_duplicate`; assessments remain comparable
- same-period differing values: pair `conflicting_candidate`; assessments remain comparable; no preferred/canonical winner
- missing value versus reported zero: pair `unresolved` with `missing_value` / `peer_missing_value`; not agreement or conflict
- different periods with equal values: pair `incompatible` with `period_mismatch`; assessments remain comparable without `period_mismatch`
- absent/`""`/`" "`/`" \t "` reporting basis on one peer: pair `unresolved` without mismatch; original blank strings retained
- definition text conflict with equal values: pair `incompatible` with `definition_mismatch`
- 52-week versus 53-week reporting bases: pair `incompatible` with `calendar_reporting_mismatch`; assessments `not_comparable`
- proven reporting-basis conflict plus missing week-adjustment: pair `incompatible`, retaining mismatch plus week-gap reasons
- three-peer affirmative pair plus incomplete peer: three pairs; the complete pair remains `agreeing_duplicate`; incomplete pairs `unresolved`; aggregate assessments unresolved via peer gaps
- three-peer affirmative pair plus definition-incompatible peer with a different value: complete pair remains `agreeing_duplicate`; other pairs `incompatible` with `definition_mismatch`; no transitive agreement
- three complete peers with values 10/10/11: one agreeing pair and two conflicting pairs; assessments remain comparable
- singleton self-exclusion; distinct same-document occurrences with identical values remain two records and one agreeing pair
- geographic/basis/population identities never share a pair
- renamed/reordered inputs preserve pair outcomes and semantic evidence; locators follow renamed files

Supplied four annual filings plus four management documents: no invented agreeing-duplicate or conflicting-candidate evidence.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent mixed-directory load of supplied extracted inputs:

- 4 statement filings (FY2022–FY2025) + 4 management documents
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- 107 market-table store observations
- 3 nonhistorical targets
- status `admitted_unreconciled`; canonical selection `deferred`
- assessments: **135** items covering every reported observation; **28** supported, **107** outside_scope, **0** unsupported_variant
- comparability: comparable **0**, not_comparable **22**, unresolved **6**, outside_scope **107**
- reconciliation: pair_count **24**; agreeing_duplicate **0**; conflicting_candidate **0**; incompatible **24**; unresolved pairs **0**; singleton **6**; unsupported_variant **0**; outside_scope **107**
- pair split: comparable-sales incompatible **18**, sales-per-square-foot incompatible **6**
- pair reasons: `definition_mismatch` 24, `calendar_reporting_mismatch` 24, `period_date` 24, `calendar_week_adjustment` 23, `peer_period_date` 24, `peer_calendar_week_adjustment` 23, `missing_comparison` 6, `peer_missing_comparison` 6
- union of reconciliation locators covers all 135 reported observations
- reversed/renamed directory semantic pair outcomes match mixed; locators follow the renamed files
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile` against temporary mixed and annual-only copies (admit `2022-01-30`): mixed writes `management_kpi_admission.json` with 135 assessment items, supported_count **28**, pair_count **24**, and comparability 0/22/6/107; annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`. Mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation pairs **24** all `incompatible`, agreeing/conflicting **0/0**, singletons **6**, outside-scope coverage **107**; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; CLI mixed admission includes reconciliation and annual-only omits the artifact; focused pytest **117 passed**; required suite including new reconciliation tests **796 passed**, **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Prior-child focused **87** / required **766**, and older 53/732 and 67/1735-pass results, remain historical and were not re-run as acceptance |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; canonical management-history selection; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_filing_cli.py -q --tb=short` | 0 | **117 passed** in **4.48s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py core/tests/test_management_kpi_identity.py -q` | 0 | **796 passed** in **167.49s** |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory annual copy; mixed from supplied extracted dir; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; std/conflicts/statement-provenance match; extracted JSON unchanged |
| Independent affirmative pair mutations through ordinary admission (both families) | 0 | same-period equal values agreeing; differing values conflicting; missing vs 0 unresolved; different periods incompatible with `period_mismatch` while assessments stay comparable; blank reporting basis unresolved without mismatch; three-peer incomplete/incompatible peers do not suppress the affirmative pair |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: 4 filings + 4 management-kpi documents; mixed writes `management_kpi_admission.json` (reported 135, assessments 135/supported 28, comparability 0/22/6/107, pair_count 24, agreeing/conflicting 0/0); annual-only omits that artifact; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release README.md present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi_reconciliation.py` | `74c2b73aacf73987512086f0fb3789aaee6c65f7e0f92504225b81daceb0cc5e` | 10736 |
| `core/ingestion/management_kpi.py` | `56f3047a500c47f763963affe4bcb349f1540844b3fc33e046a1d9e385833632` | 45430 |
| `core/ingestion/management_kpi_identity.py` | `b8b6af63a616847d81afadc9411bf3efc331076d9d0f8fd17aa7a9c87f28d07d` | 22873 |
| `core/tests/test_management_kpi_reconciliation.py` | `eeb391d90f70d6e3d422d159ab8f81065a94529cb63b35c1c2549bef2261cefc` | 31081 |
| `core/tests/test_management_kpi_identity.py` | `99a43994ca3f0471c2137b09646e8393890e1b250e7ee325fde8d63cc547d735` | 52606 |
| `core/tests/test_management_kpi_admission.py` | `0f04e96ef97037fff6b3f241a976be668b42224d5fcb49aee13a293987abfbb1` | 24205 |
| `core/tests/test_filing_cli.py` | `0b2df42c3b572022cb557d346e5f9b9d3b9814a03dc19cbc930cd3263d3b5fbd` | 12347 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Five snapshot-matched production/test identities retained from `edit_replay_counts`: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`. Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` (`d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`) / `cursor-20260915-034910-19408.log` (`57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`) retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining admission restrictions: later-audited precedence, physical-page mapping, assurance, and presentation role stay unresolved; admitted observations remain audit-only and excluded from `StandardizedFinancials`. Canonical value selection is still deferred.

---

## Remaining scope

Beyond this increment remain additional supported identities, current/comparative/restated/prior reconciliation, evidenced later-audited precedence, superseded observations and canonical selection; unavailable assurance/presentation evidence remains unresolved. Then extend validated `StandardizedFinancials` histories/round trips, Operating KPI analytics and supported revenue/geography/margin/inventory/working-capital/capex relationships, followed by ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and definition/calendar discontinuities; distinguish reported/statement-derived/analyst-derived measures; infer no causality. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` and `.39` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
