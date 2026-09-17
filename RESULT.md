# RESULT.md — Step 9M.2.4.1.1.1.46 Operating KPIs: evidenced selected-history handoff

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.46 — Operating KPIs — Evidenced selected-history handoff  
**Work:** `b52537e7ed244ce4974748923d629154`  
**Plan:** `1034d0ad2cb84867bfdab75bb46a1b16`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `0b40e7cc63a53b0d810eb7baf6a6eab2be6c18d6d4239ad6d33ca171733b9b48` (10233).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi_history.py`, `core/ingestion/filing_standardizer.py`, `core/ingestion/management_kpi.py`, `core/tests/test_management_kpi_history.py`, `core/tests/test_management_kpi_reconciliation.py`, and `RESULT.md`.

No required plan change.

`.git/autocycle/latest-implementation` currently references `HEAD: fdd80f12e48a35c6d63cabed6b47b5a10346d0e6` and log `cursor-20260917-113310-20649.log` and was not rewritten. That pointer is a historical controller artifact, not this increment's acceptance. Working-tree HEAD is `08e73681bdd2de4df1af309903f01fe1e32a7192`.

The ordinary `standardize_reconciled` path now transfers only unique evidenced selected occurrences from complete two-occurrence groups into `historical_operating_kpis.management_observations`, combining them with existing store-selected observations. Selections are re-derived from bound documents through the accepted admission/identity/revision-selection pipeline; cached status strings are not trusted. Deferred observations remain audit-only. Admission status stays `admitted_unreconciled`. Supplied mixed data still has zero selections and no model-facing management history.

---

## Task 1 — Connect validated selections to standardized histories

`selected_management_kpi_histories` re-runs `assess_reported_observations`, `reconcile_revision_links`, and `reconcile_group_selections` from the reconciled admission's bound documents and observations. Cached `group_selections` must match that derivation or standardization raises `ValueError` without mutating inputs. Eligible complete two-occurrence groups contribute only the unique selected occurrence. Full supported identity, selected definition text, period kind, calendar week adjustment/reporting basis, and qualifiers come from validated assessment/source records. Combined store plus management payloads are validated against the existing model axis; off-axis selected dates, malformed values, missing semantics, and duplicate identity-period entries fail closed. Source paths/pages, extraction, assurance, revision, and superseded observations remain in the admission artifact. Diagnostic `management_kpi_history_handoff` reports eligible selected counts versus deferred groups; `deferred_canonical_selection` still records that general admission is not complete.

`_historical_operating_kpis` returns `None` when both store selections and management histories are absent.

---

## Task 2 — Prove handoff and exclusion through the ordinary path

Synthetic bound-document fixtures cover both families through admission → reconciliation → `standardize_reconciled` → export/reload/export, including CLI reconcile on temporary files. Selected values and exact semantics survive; input permutation of reported rows is deterministic; sparse histories and definition/calendar changes across periods do not merge or gap-fill; supported variants may share a period. Missing/unknown/unaudited assurance, absent or contradictory revision evidence, ambiguous incoming candidates, singletons, larger groups, incompatible definitions/calendars, and missing reviser values remain deferred and absent from model-facing histories. Tampered/stale cached selections and missing occurrence references raise and leave inputs unchanged. Signed/zero comparable growth on `percent` and nonnegative sales-per-square-foot on `USD_per_square_foot` are preserved; negative SPSF is rejected; no conversion/scaling. Legacy absent/null/store-only round trips, management-only histories without store analytics, mixed histories with store growth within `1e-12`, and malformed management-text rejection on object/default/false/true reload remain covered.

---

## Task 3 — Measured verification

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
- mixed and annual-only `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile --admit-period 2022-01-30` against temporary mixed and annual-only copies: mixed validate-source prints `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0. Mixed writes `management_kpi_admission.json` with reported 135, definitions 9, targets 3, market 107, supported 28, comparability 0/22/6/107, pair_count 24, revision_links 0, selected/superseded 0/0, 28 deferred groups. Annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Ordinary-path both-family selected-history handoff; stale/inconsistent cached selections rejected with input immutability; deferred groups excluded; mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets, 107 market-table; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; mixed `historical_operating_kpis is None`; CLI mixed admission includes group_selections and annual-only omits the artifact; focused handoff/KPI pytest **1160 passed**; required listed files **2111 collected**, all passed / **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication; malformed management-text rejection on object/default/`strict=False`/`strict=True` reload |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Prior fail-closed-reload child focused **1125** / required **2076**; premature-completion child focused **126** / required **1077**; revision-selection child focused **370** / required **1049**; older 352/1031, 309/988, 232/911, 175/854 and 117/796 remain historical |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

`.git/autocycle/latest-implementation` currently points at `fdd80f12e48a35c6d63cabed6b47b5a10346d0e6` / `cursor-20260917-113310-20649.log` and was **not** rewritten. Working-tree HEAD is `08e73681bdd2de4df1af309903f01fe1e32a7192`. Any remaining controller refresh belongs to the existing controller mechanism; prospective IDs are not certified here.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_history.py core/tests/test_operating_kpi_management_history.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py -q --tb=short` | 0 | **1160 passed** in **4.36s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_history.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **2111 passed** in **184.11s**, **0 failed**. Listed required files collect **2111**. |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory copies; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical / 107 market-table; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; std/conflicts/statement-provenance match; mixed and annual-only `historical_operating_kpis is None`; extracted JSON unchanged |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`; mixed writes `management_kpi_admission.json` (reported 135, definitions 9, targets 3, market 107, assessments 135/supported 28, comparability 0/22/6/107, pair_count 24, revision_links 0, selected/superseded 0/0, 28 deferred groups); annual-only omits that artifact; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi_history.py` | `78132856c66bdcefa6fb913f28c794ea69313b1ba2857274f166e9b9cce31a26` | 6425 |
| `core/ingestion/filing_standardizer.py` | `4209f4f3d7ae6bc34d2828f9d204a86342893e370158862a38d177b2d33ec97a` | 22165 |
| `core/ingestion/management_kpi.py` | `f8d367b5aaa27075a56b6c6779dbeca6f50d4f2e3c33bcf38214ce3aede3e37a` | 65009 |
| `core/tests/test_management_kpi_history.py` | `9fdce04fbd3a0fe2858847238468fff964707a8b215b23a53954b349d1a23436` | 25415 |
| `core/tests/test_management_kpi_reconciliation.py` | `2c60aeb4922bfea6cd1f35b20ef03248667038d5f114b24dce9483cad6288031` | 128247 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Evidenced complete two-occurrence selections now reach `StandardizedFinancials` through the ordinary path; additional identities remain unfinished.

---

## Remaining scope

This child hands off evidenced selected management KPIs into validated standardized histories. Operating KPI analytics and supported revenue/geography/margin/inventory/working-capital/capex relationships remain unfinished product scope, then ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and definition/calendar discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41`, `.42`, `.43`, `.44` and `.45` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected occurrences that pass those gates now transfer into model-facing histories; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
