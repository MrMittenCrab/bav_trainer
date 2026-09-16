# RESULT.md — Step 9M.2.4.1.1.1.41 Operating KPIs: source-grounded presentation and assurance evidence

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.41 — Operating KPIs — Source-grounded presentation and assurance evidence  
**Work:** `c968a1160acf423097b38570ce2c6cb3`  
**Plan:** `62c958c557c348de8bcb72b738c48d57`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `08d6dc2c28495f1d19f51dd1b48b02e1cebede060beb23484a92d1976b5f23b8` (10886).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, canonical history selection, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi.py`, `core/ingestion/management_kpi_reconciliation.py`, `core/tests/test_management_kpi_admission.py`, `core/tests/test_management_kpi_reconciliation.py`, `core/tests/test_management_kpi_identity.py`, `core/tests/test_filing_cli.py`, and `RESULT.md`.

No required plan change.

Ordinary admission now validates optional occurrence-specific presentation and assurance evidence on the two supported families. Supplied mixed inputs remain unknown on both dimensions, zero comparable, 22 not-comparable, six unresolved, and 107 outside-scope. Measured supplied pair outcomes remain 24 incompatible, 0 unresolved pairs, 0 agreeing duplicates, and 0 conflicting candidates. Canonical selection remains deferred.

---

## Task 1 — Occurrence-level evidence contract

Supported `reported_kpis` entries may optionally supply nested `presentation` (`role`, `evidence`, `source`) and `assurance` (`status`, `evidence`, `source`) objects.

Admitted roles are `current`, `comparative`, `restated`, `prior`, and `unknown`. Admitted assurance values are `audited`, `unaudited`, and `unknown`. A non-unknown dimension requires nonblank documentary evidence and a printed source bound to that observation’s source document. Supplied evidence text, printed locator, and source are retained in serialized admission.

Dimensions validate independently. Absent, null, empty, or whitespace-only evidence leaves that dimension `unknown` with an explicit unresolved reason. Malformed types, invalid roles/statuses, contradictory top-level assertions, unbound `source_file`, asserted physical-page mapping, missing evidence/source on a non-unknown value, and non-unknown roles on unsupported observations fail closed through ordinary parse/admission.

`prior` is only an explicitly evidenced presentation role. Filing year, annual-report membership, filenames, equal values, and peer evidence do not infer presentation or assurance. Printed page references remain distinct from physical PDF pages; evidence sources always serialize `physical_page_mapping=unresolved`.

Legacy supplied documents are unchanged. Store-count and nonhistorical target observations stay unknown and cannot acquire accepted roles. Document-level admission serialization remains unknown and does not imply document-wide completeness.

---

## Task 2 — Pair-member evidence propagation

Each reconciliation occurrence serializes its own `presentation_evidence` and `assurance_evidence`. Repeated same-document occurrences and three-peer groups keep occurrence-local records. Peers do not inherit evidenced roles or assurance.

Presentation and assurance evidence do not change metric identity, pair membership, comparability, pair outcomes, or dimension-specific gaps. Equal values with differing evidenced roles remain duplicate/conflict classifications under existing rules; precedence and canonical selection stay deferred.

Observation unresolved lists drop only the dimension actually evidenced. Admission-level `assurance` and `presentation_role` remain unresolved while any observation, including store and target rows, is still unknown. Physical-page mapping and precedence remain unresolved.

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
- supplied presentation/assurance: all observations `unknown`; pair members serialize unknown evidence with `source=None`
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile` against temporary mixed and annual-only copies (admit `2022-01-30`): mixed writes `management_kpi_admission.json` with 135 assessment items, supported_count **28**, pair_count **24**, and comparability 0/22/6/107; annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`. Mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0.

Temporary fixtures exercised current/comparative/restated/prior, audited/unaudited, independently missing dimensions, absent/null/empty/whitespace evidence, invalid roles/types, contradictory assertions, mismatched source binding, repeated same-document occurrences, three-peer independence, renamed locators, and input immutability. Explicit `prior` is distinct from an older period or `comparative`; explicit `unaudited` is distinct from unknown assurance.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation pairs **24** all `incompatible`, agreeing/conflicting **0/0**, singletons **6**, outside-scope coverage **107**; supplied presentation/assurance remain unknown; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; CLI mixed admission includes occurrence evidence objects and annual-only omits the artifact; focused pytest **175 passed**; required suite **854 passed**, **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Prior-child focused **117** / required **796**, and older 87/766 and 53/732 results, remain historical and were not re-run as acceptance |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; canonical management-history selection; later-audited precedence; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_filing_cli.py -q --tb=short` | 0 | **175 passed** in **5.62s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py core/tests/test_management_kpi_identity.py -q` | 0 | **854 passed** in **168.19s** |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory annual copy; mixed from supplied extracted dir; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; supplied presentation/assurance unknown; std/conflicts/statement-provenance match; extracted JSON unchanged |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: 4 filings + 4 management-kpi documents; mixed writes `management_kpi_admission.json` (reported 135, assessments 135/supported 28, comparability 0/22/6/107, pair_count 24, agreeing/conflicting 0/0); annual-only omits that artifact; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi.py` | `57d6473c39518db2ab3b688f8dd5cd1960b3f49a210a9a3ea119a00b82bf73d9` | 54632 |
| `core/ingestion/management_kpi_reconciliation.py` | `cbf76d63034c7e9362faa1df44997c1abda6d373cda5a23f5ca3a63af9afa4f6` | 11880 |
| `core/tests/test_management_kpi_admission.py` | `b9870433017559b4b60c7431195df7ec76cbcb8c8178a89bf51221713dadc085` | 42060 |
| `core/tests/test_management_kpi_reconciliation.py` | `66a79e7a260bc847304de424efb85f30fafaf81146ecaff917660fe454e8b4e2` | 39640 |
| `core/tests/test_management_kpi_identity.py` | `5d7dc73b4dda23060e2b7c5b4eb599e2183e704dfd9890d603dd70383e55a532` | 53000 |
| `core/tests/test_filing_cli.py` | `3f8e5b1f3a1921880aa9d3bf1cf0a63f5ab5c4055f45131ee14dea22f2caeaa0` | 12830 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Five snapshot-matched production/test identities retained from `edit_replay_counts`: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`. Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` (`d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`) / `cursor-20260915-034910-19408.log` (`57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`) retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining admission restrictions: later-audited precedence and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance evidence, so those dimensions remain unknown there. Admitted observations remain audit-only and excluded from `StandardizedFinancials`. Canonical value selection is still deferred. Current/comparative/restated/prior relationship reconciliation is not performed in this child.

---

## Remaining scope

Beyond this increment remain additional supported identities, current/comparative/restated/prior relationship reconciliation, evidenced later-audited precedence, superseded observations and canonical selection; unavailable assurance/presentation evidence in supplied documents remains unresolved. Then extend validated `StandardizedFinancials` histories/round trips, Operating KPI analytics and supported revenue/geography/margin/inventory/working-capital/capex relationships, followed by ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and definition/calendar discontinuities; distinguish reported/statement-derived/analyst-derived measures; infer no causality. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39` and `.40` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
