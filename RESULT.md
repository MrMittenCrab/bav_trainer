# RESULT.md — Step 9M.2.4.1.1.1.39 Operating KPIs: supported management identities and comparability

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.39 — Operating KPIs: supported management identities and comparability  
**Work:** `e24b509039454e0ba70a28da60489c41`  
**Plan:** `00d33c0a49354a359733e15dbe61d96c`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `6fd1a7d1a9974eec891c9c118bea6d2ab93eb074775473be2de279070a3cedca` (11383).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, canonical history selection, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi_identity.py`, `core/tests/test_management_kpi_identity.py`, `core/tests/test_management_kpi_admission.py`, `core/tests/test_filing_cli.py`, and `RESULT.md`. `core/ingestion/management_kpi.py` was inspected and left unchanged.

No required plan change.

Obsolete prior-child claims of six comparable / zero unresolved supplied assessments are **withdrawn**. Measured supplied-input counts are zero comparable, 22 not-comparable, six unresolved, and 107 outside-scope.

---

## Task 1 — Calendar-evidence gating

Source-grounded `calendar_reporting_basis` is required for each supported observation and evaluated peer. Absence is a required-gap reason (`calendar_reporting_basis`). Evidenced incompatible reporting bases are a conflict reason (`calendar_reporting_mismatch`). Unknown-versus-known or empty-versus-known evidence alone is not a mismatch.

Missing reporting basis on either peer or both peers prevents comparability, retains the explicit missing reason, keeps distinct-peer locators, and does not emit `calendar_reporting_mismatch`. Affirmative definition, population, unit, basis, comparison, period, and week-adjustment requirements remain. Matching labels/IDs, equal missing values, or aligned reporting strings alone cannot establish equivalence.

Metric identity, source-bound definitions, fiscal periods, qualifiers, 52/53-week adjustments, shifted comparison weeks, acquisition eligibility, sales-per-square-foot exclusions, self-exclusion, distinct-source-occurrence requirements, unresolved singletons, deterministic ordering, and explicit outside-scope classifications are unchanged. Canonical winners are not selected.

---

## Task 2 — Reporting-basis regressions

Ordinary admission serialization of affirmative distinct-occurrence fixtures for both supported families, with complete required evidence including matching `calendar_reporting_basis`, remains comparable with no unresolved required reasons and with distinct peers.

Independent mutations through ordinary admission:

- remove reporting basis from either peer, both peers, absent key, and accepted empty `""`: both assessments lose comparability (`unresolved`); missing reasons survive serialization; absence alone creates no `calendar_reporting_mismatch`
- incompatible 52-week versus 53-week reporting-basis strings with period, definition, and week-adjustment held fixed: `not_comparable` with `calendar_reporting_mismatch` and no week-adjustment conflict
- the same proven reporting-basis conflict alongside missing week-adjustment evidence: `not_comparable`, with both `calendar_reporting_mismatch` and `calendar_week_adjustment` retained
- reversed reporting-basis strings preserve the not-comparable decision

Period/definition/week-adjustment, singleton, self-exclusion, duplicate/conflict, supplied six-false-positive, renamed/reordered, and CLI serialization regressions are retained.

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
- supported split: comparable-sales not_comparable **18**, comparable-sales unresolved **6**, sales-per-square-foot not_comparable **4**
- unresolved reasons: `outside_supported_families` 107, `period_date` 28, `calendar_week_adjustment` 27, `definition_mismatch` 22, `calendar_reporting_mismatch` 22, `no_distinct_peer` 6, `missing_comparison` 4
- no comparable assessment has unresolved required dimensions, missing/incompatible calendar reporting basis, or no distinct peer
- reversed/renamed directory semantic identities and comparability match mixed; locators follow the renamed files
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

Independent affirmative-pair mutations (both families) through ordinary admission: complete fixtures comparable with shared reporting basis and distinct peers; missing/empty reporting basis on either or both peers unresolved without mismatch; incompatible 52/53-week reporting bases not-comparable with week adjustment still `included`.

CLI `validate-source` / `reconcile` against temporary mixed and annual-only copies (admit `2022-01-30`): mixed writes `management_kpi_admission.json` with 135 assessment items and supported_count **28**; annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`. Mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0. CLI assessment payload matched the in-process mixed admission payload.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets; assessments 135/28/107/0; comparability **0/22/6/107**; `calendar_reporting_mismatch` 22 on supplied not-comparable peers; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; CLI mixed admission includes assessments and annual-only omits the artifact; focused pytest **53 passed**; required suite including identity tests **732 passed**, **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Checkpoint results of 67 focused passes and 1735 passes / three baseline failures remain historical and were not re-run |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; canonical management-history selection; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_filing_cli.py -q --tb=short` | 0 | **53 passed** in **3.99s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py core/tests/test_management_kpi_identity.py -q` | 0 | **732 passed** in **165.80s** |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory annual/reversed copies; mixed from supplied extracted dir) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; std/conflicts/statement-provenance match; renamed identities match; extracted JSON unchanged |
| Independent affirmative reporting-basis mutations through ordinary admission (both families) | 0 | complete fixtures comparable; missing/empty either-or-both unresolved without mismatch; incompatible 52/53-week reporting bases not-comparable with week adjustment fixed |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: 4 filings + 4 management-kpi documents; mixed writes `management_kpi_admission.json` (reported 135, assessments 135/supported 28, comparability 0/22/6/107); annual-only omits that artifact; CLI assessments match in-process payload; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release README.md present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi_identity.py` | `95cd72592647fb1d1526ba3f75bac6373ab3943d697a2e77c24b93071993ae29` | 20640 |
| `core/tests/test_management_kpi_identity.py` | `022e855e3c8ba94fcd67e2b315c830ba7391689f165f29e366a66270fff0a316` | 45809 |
| `core/tests/test_management_kpi_admission.py` | `83d253c634cbc9e99d6ace3ba66ffe4bb25e95049ebba25f7cc324e7c68f1127` | 22992 |
| `core/tests/test_filing_cli.py` | `092c952ead9da7423f5ba9cf9f8943794b7396aff422c860bd4b685a574140b3` | 11476 |

Unchanged this child (inspected only): `core/ingestion/management_kpi.py` SHA-256 `e4e91a30c312c25252d4edb5f02995e68769d37983a8503665bffe94fd723a2c` (44817).

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Five snapshot-matched production/test identities retained from `edit_replay_counts`: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`. Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` (`d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`) / `cursor-20260915-034910-19408.log` (`57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`) retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining admission restrictions: later-audited precedence, physical-page mapping, assurance, and presentation role stay unresolved; admitted observations remain audit-only and excluded from `StandardizedFinancials`. Canonical value selection is still deferred.

---

## Remaining scope

Extend supported identities beyond these two families; implement current/comparative/restated/prior reconciliation, evidenced later-audited precedence, agreeing duplicates, superseded observations and conflicts. Unknown assurance and extracted preferred values cannot determine precedence. Then extend validated `StandardizedFinancials` histories/round trips, Operating KPI analytics and supported revenue/geography/margin/inventory/working-capital/capex relationships, followed by ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and definition/calendar discontinuities; distinguish reported/statement-derived/analyst-derived measures; infer no causality. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission and `.37` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
