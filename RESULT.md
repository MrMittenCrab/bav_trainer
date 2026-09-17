# RESULT.md — Step 9M.2.4.1.1.1.45 Operating KPIs: validated management-history contract and round trips

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.45 — Operating KPIs — Validated management-history contract and round trips  
**Work:** `9bbf038004e9489a96c15f73aa82e375`  
**Plan:** `f28d736dd3294318ae1416b422132a5f`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `16ab60fc0d80a3d54574eaba48e063b151d54fc5d9289ad834ffa350143f5fbf` (10406).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, selected-history handoff, or Step 9 acceptance.

Edits this child: `core/data/interface.py`, `core/data/historical_operating_kpis.py`, `core/data/standardized_io.py`, `core/model/operating_kpi.py`, `core/tests/test_operating_kpi_facts.py`, `core/tests/test_operating_kpi_analysis.py`, `core/tests/test_operating_kpi_management_history.py`, and `RESULT.md`.

No required plan change.

Prior revision-selection work remains accepted. Recorded 370 focused / 1049 required passes belong to the previous child (`b15c586a94d94f5b8bc4f011456ed5db`) and are historical measurements, not this child's fresh results. `.git/autocycle/latest-implementation` currently references `HEAD: 5d21788a0f14dcb920e2a438897033cdff6f0adc` and log `cursor-20260917-110328-14258.log` and was not rewritten. That pointer is a controller artifact, not this increment's acceptance.

`HistoricalOperatingKpiData` now carries a distinct `management_observations` collection beside the existing store-observation list. Supported comparable-sales-growth and sales-per-square-foot identities validate family, semantic identity fields, canonical period, finite numeric value, explicit unit, definition text, period kind, comparison basis, and calendar/qualifier distinctions. Export/reload/export is semantically equal and canonically ordered. Invalid histories fail closed. Legacy store-only JSON omits `management_observations`. Management-only histories do not activate store-count analytics. Mixed histories preserve store growth within `1e-12`. Automatic admission remains `admitted_unreconciled` and is not promoted into model-facing management histories.

---

## Task 1 — Extend the optional standardized contract

`HistoricalManagementKpiObservation` is the typed management collection. Store observations keep their prior shape. Serialization emits `observations` always and `management_observations` only when that collection is non-empty.

Validation uses existing `SUPPORTED_METRIC_MAPPINGS` identity combinations without broadening admission. Rejected: inconsistent identity fields, missing required semantics, duplicate identity-period entries (including when definition text differs), invalid/non-canonical dates, periods outside the model axis, booleans, nonfinite values, unsupported units/families/variants, and audit fields (`source_file`, `assurance`, and similar). Comparable-sales values may be signed or zero on the `percent` scale. Sales-per-square-foot values must be nonnegative on `USD_per_square_foot`. No implicit unit conversion or statement scaling. Unavailable periods are omitted; definition/calendar discontinuities remain distinct observations.

At least one observation is required across the two collections. Source paths, pages, extraction references, assurance, revision evidence, and superseded occurrences stay in existing audit artifacts.

---

## Task 2 — Prove export/reload and failure behavior

Temporary both-family fixtures cover accepted geographic, population, and reported/constant-dollar variants, negative growth, zero, sparse periods, and definition/calendar discontinuities. Object validation and serialized-input validation run independently. Reordered collections and identity-field key order reload to the same canonical payload. Distinct supported variants may share a period. Duplicate identity-period rows fail even when definition text differs. Legacy absent/null and store-only payloads remain compatible. Mixed store/management round trips preserve store counts and growth. Management-only payloads keep `operating_kpi_applicable` false. Failing inputs are left unchanged. Supplied mixed admission still does not write model-facing management histories.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent mixed-directory load of supplied extracted inputs:

- 4 statement filings (FY2022–FY2025) + 4 management documents
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- 107 market-table store observations
- 3 nonhistorical targets
- status `admitted_unreconciled`; model-facing canonical selection `deferred`
- assessments: **135** items covering every reported observation; **28** supported, **107** outside_scope, **0** unsupported_variant
- comparability: comparable **0**, not_comparable **22**, unresolved **6**, outside_scope **107**
- reconciliation: pair_count **24**; agreeing_duplicate **0**; conflicting_candidate **0**; incompatible **24**; unresolved pairs **0**; singleton **6**; unsupported_variant **0**; outside_scope **107**
- supplied presentation/assurance/revision: `revision_links` **[]**; counts recognized/unresolved/incompatible **0/0/0**
- group selections: **28** identity-period groups, all `deferred`; selected **0**; superseded **0**
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed and annual-only `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile --admit-period 2022-01-30` against temporary mixed and annual-only copies: mixed validate-source prints `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0. Mixed writes `management_kpi_admission.json` with reported 135, supported 28, comparability 0/22/6/107, pair_count 24, revision_links 0, selected/superseded 0/0, 28 deferred groups. Annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Object and serialized management-history validation; both-family round trips; mixed/management-only applicability; mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; mixed `historical_operating_kpis is None`; CLI mixed admission includes group_selections and annual-only omits the artifact; focused contract/analysis pytest **126 passed**; required listed files **1051 collected**, all passed inside **1077 passed** / **0 failed** (listed files plus new contract file); checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Prior child focused **370** / required **1049**; older 352/1031, 309/988, 232/911, 175/854 and 117/796 remain historical |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; selected-history handoff; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

`.git/autocycle/latest-implementation` SHA-256 `b972414759ae52689b1e103070b89abd7d53359b26fa7476cb3995c1304918cd` (183) currently points at `5d21788a0f14dcb920e2a438897033cdff6f0adc` / `cursor-20260917-110328-14258.log` and was **not** manually rewritten. Working-tree HEAD is `5bc34ad95eee7e737db658c46fa80484d6d44b15`. Any remaining controller refresh belongs to the existing controller mechanism; prospective IDs are not certified here.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_management_history.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py -q --tb=short` | 0 | **126 passed** in **2.52s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **1077 passed** in **178.99s**, **0 failed**. Listed required files collect **1051**; the extra **26** are this child's new contract file. |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory copies; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; std/conflicts/statement-provenance match; mixed and annual-only `historical_operating_kpis is None`; extracted JSON unchanged |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`; mixed writes `management_kpi_admission.json` (reported 135, assessments 135/supported 28, comparability 0/22/6/107, pair_count 24, revision_links 0, selected/superseded 0/0, 28 deferred groups); annual-only omits that artifact; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/data/interface.py` | `41e0ede1833e9243fa79a1739f99636285ecd39ed60efef63fceb294d0d78536` | 5259 |
| `core/data/historical_operating_kpis.py` | `48093ab4ccff85c7e49cf9996012b95ca493c929a50ddf3bd0765bd04e488508` | 12766 |
| `core/data/standardized_io.py` | `f50d202e2e84d5d4e95238d68d901dc279a569135d798adf5cb3648b1fa9bebe` | 22636 |
| `core/model/operating_kpi.py` | `3adbf519260fc5c4e2c33e7ce2e409550665ca28d35ce4f3f637e86353cba09f` | 4793 |
| `core/tests/test_operating_kpi_facts.py` | `c12cdf2150675dd0f14e1fb272daff6fc96637952cf93666297ddbcca46af9b0` | 39451 |
| `core/tests/test_operating_kpi_analysis.py` | `fc8468cb70cd2ebf1c9adaae867e2550ec4f26896e9df3a25f4c468de03edb0c` | 20754 |
| `core/tests/test_operating_kpi_management_history.py` | `792efa7f13b2f86c8301b026caab174c44678d1e6d46d1e9e9f5df2295d131e0` | 21677 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Admitted observations remain audit-only and excluded from `StandardizedFinancials` unless an explicit validated management-history payload is supplied. Automatic selected-history handoff remains unfinished.

---

## Remaining scope

This child delivers the validated standardized management-history contract and round trips. Selected-history handoff, Operating KPI analytics, and supported revenue/geography/margin/inventory/working-capital/capex relationships remain unfinished product scope, then ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and definition/calendar discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41`, `.42`, `.43` and `.44` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
