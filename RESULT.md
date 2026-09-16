# RESULT.md — Step 9M.2.4.1.1.1.39 Operating KPIs: supported management identities and comparability

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.39 — Operating KPIs: supported management identities and comparability  
**Work:** `e24b509039454e0ba70a28da60489c41`  
**Plan:** `5c0ada0a9b6845fbb044af1c6e7ae1bc`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `bc65a989c3a90b4c5d379ebbfe3bd1f08c024efff6e01ce42d36558b03080d86` (10883).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, canonical history selection, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi_identity.py` (new), `core/ingestion/management_kpi.py`, `core/tests/test_management_kpi_identity.py` (new), `core/tests/test_management_kpi_admission.py`, `core/tests/test_filing_cli.py`, and `RESULT.md`.

No required plan change.

---

## Task 1 — Supported identities and comparability

Explicit mappings cover comparable-sales growth and sales per square foot, including geographic and reported/constant-dollar variants plus FY2022 store-only and store+DTC populations. Contradictory unit/basis/comparison/geography/channel/scope mappings become `unsupported_variant` with reason codes. Unknown family-like metric IDs are retained as `unknown_variant`. Every other reported metric is `outside_scope`.

Metric identity is delimiter-safe JSON (`family`, entity ticker/company, geography, population, unit, basis, comparison) and is independent of mapping declaration order. Fiscal period and source locators remain outside the metric identity. Definitions resolve only inside their source document; matching IDs or labels do not establish equivalence. Comparability is conservative: identical bound definition text plus identical calendar/qualifier/period-kind evidence is required; otherwise `not_comparable` or `unresolved`. 52/53-week qualifiers, reporting-basis calendar strings, and definition text (including shifted comparison weeks, acquisition eligibility, and SPSF exclusions) are preserved as evidence and are not inferred from free text.

---

## Task 2 — Ordinary admission serialization

`admit_management_documents` now emits a deterministic `assessments` section on the existing management admission payload. Ordinary CLI `reconcile` writes it automatically inside `management_kpi_admission.json`. Annual-only directories still omit that artifact. Canonical selection remains `deferred`. Market-table rows and three nonhistorical targets keep their prior audit representation and are not assessed. Agreeing duplicates and conflicting values remain separate occurrences; comparable identities do not select winners.

Admission-level remaining unresolved metadata: `precedence`, `physical_page_mapping`, `assurance`, `presentation_role`. Identity/comparability now live in assessments and cannot enter `StandardizedFinancials`.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent mixed-directory load of supplied extracted inputs:

- 4 statement filings (FY2022–FY2025) + 4 management documents
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- 107 market-table store observations; store totals `655/711/767/811`
- 3 nonhistorical targets
- status `admitted_unreconciled`; canonical selection `deferred`
- assessments: **135** items covering every reported observation; **28** supported, **107** outside_scope, **0** unsupported_variant
- comparability: comparable **6**, not_comparable **22**, unresolved **0**, outside_scope **107**
- supported split: comparable-sales not_comparable **18**, comparable-sales comparable **6** (FY2022 store/DTC singletons and FY2023-only constant-dollar global/Americas series), sales-per-square-foot not_comparable **4**
- unresolved reasons: `outside_supported_families` 107, `period_date` 28, `calendar_week_adjustment` 27, `definition_mismatch` 22
- reversed/renamed directory semantic identities and comparability match mixed; locators follow the renamed files
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile` against temporary mixed and annual-only copies (admit `2022-01-30`): mixed writes `management_kpi_admission.json` with 135 assessment items and supported_count **28**; annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`. Mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0. CLI assessment payload matched the in-process mixed admission payload.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets; assessments 135/28/107/0; comparability 6/22/0/107; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; CLI mixed admission includes assessments and annual-only omits the artifact; focused pytest **36 passed**; required suite including new identity tests **715 passed**, **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; canonical management-history selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_filing_cli.py -q --tb=short` | 0 | **36 passed** in **3.24s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py core/tests/test_management_kpi_identity.py -q` | 0 | **715 passed** in **160.61s** |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory annual/reversed copies; mixed from supplied extracted dir) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; assessments 135 (28 supported / 107 outside / 0 variant); comparability 6/22/0/107; std/conflicts/statement-provenance match; reversed identities match; extracted JSON unchanged |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: 4 filings + 4 management-kpi documents; mixed writes `management_kpi_admission.json` (reported 135, assessments 135/supported 28); annual-only omits that artifact; CLI assessments match in-process payload; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release README.md present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi.py` | `e4e91a30c312c25252d4edb5f02995e68769d37983a8503665bffe94fd723a2c` | 44817 |
| `core/ingestion/management_kpi_identity.py` | `a113c57f3486a405ac256314a4a8e86765164bac2493bbb1a01fe5ca224d5ccf` | 17946 |
| `core/tests/test_management_kpi_identity.py` | `c33cd6a1e70018fd3f653ed47eb46a78e6cf91649d1de4ec73641aa4bcb74af9` | 25110 |
| `core/tests/test_management_kpi_admission.py` | `2f422f6e6e33c4231cb3a748a543b583bb6b644edf01a8334339f4b424c98db1` | 22199 |
| `core/tests/test_filing_cli.py` | `4ccdfef1dac52acf9f3eda986632a16d8aeb12148a5a76d74166659c1ee1811e` | 9704 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Five snapshot-matched production/test identities retained from `edit_replay_counts`: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`. Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` (`d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`) / `cursor-20260915-034910-19408.log` (`57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`) retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining admission restrictions: later-audited precedence, physical-page mapping, assurance, and presentation role stay unresolved; admitted observations remain audit-only and excluded from `StandardizedFinancials`. Canonical value selection is still deferred.

---

## Remaining scope

Extend supported identities beyond these two families; implement current/comparative/restated/prior reconciliation, evidenced later-audited precedence, agreeing duplicates, superseded observations and conflicts. Then extend validated `StandardizedFinancials` histories/round trips, Operating KPI analytics and supported revenue/geography/margin/inventory/working-capital/capex relationships, followed by ordinary BAV/Trainer/Answer-Key/Check integration. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission and `.37` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
