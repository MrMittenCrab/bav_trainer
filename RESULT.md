# RESULT.md — Step 9M.2.4.1.1.1.38 Operating KPIs: complete mixed-directory admission acceptance

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.38 — Operating KPIs: complete mixed-directory admission acceptance  
**Work:** `6bf50da023664e0daff65822d5cfc0f2`  
**Plan:** `e0bf283a24254e5aadfed86447d41b4a`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `b892f5f19aab62b457a7ad020898112fcf0777470d423c0775a4ce7f2051b572` (9770).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, or Step 9 acceptance.

Edits this child: `core/tests/test_lululemon_benchmark.py` (annual inventory glob only) and `RESULT.md`.  
Ingestion behavior was not modified. `core/data/filing.py` was not modified.

No required plan change.

---

## Task 1 — Annual-filing inventory repair

`test_four_filings_validate_and_remain_source_bound` now discovers only the filename shape `LULU_FY` + four digits + `.json` via `EXTRACTED.glob("LULU_FY[0-9][0-9][0-9][0-9].json")`. Mixed-directory files `LULU_FY*_management_kpis.json` are excluded from this inventory only.

Discovered set: `LULU_FY2022.json`, `LULU_FY2023.json`, `LULU_FY2024.json`, `LULU_FY2025.json` → fiscal years `{2022, 2023, 2024, 2025}`.

The original PDF existence, byte-size, SHA-256, schema, fiscal-year, source-file, statement-presence, validation-success, computed-source-hash, and `warnings == ()` assertions were reached and passed. The test was not skipped, xfailed, caught, or weakened.

Ordinary mixed-directory ingestion remains separate and is covered by `core/tests/test_management_kpi_admission.py`.

---

## Task 2 — Admission and required regressions

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent mixed-directory load of supplied extracted inputs:

- 4 statement filings (FY2022–FY2025) + 4 management documents
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- market-table store totals `655/711/767/811`
- 3 nonhistorical targets
- status `admitted_unreconciled`; canonical selection `deferred`
- printed page mapping `unresolved`; assurance and presentation role `unknown`
- reversed/renamed directory identities match mixed identities
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed `historical_operating_kpis is None`; annual-only admission artifact absent
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile` against temporary mixed and annual-only copies (admit `2022-01-30`): mixed writes `management_kpi_admission.json`; annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`. Mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0.

Renamed/reordered inputs, fail-closed unknown/ambiguous/malformed schemas, dangling definitions, source hash failures, mismatched/orphan bindings, duplicates/conflicts, and input immutability remain covered by passing admission tests this child.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Inventory glob discovers exactly FY2022–FY2025 annual filings; inventory/source-binding test passes; mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, market totals `655/711/767/811`, 3 nonhistorical targets; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; CLI mixed admission artifact separate; required pytest **704 passed**, **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; canonical management-history selection; parent or Step 9 completion; G6–G9 remainder |

---

## Task 3 — Measured verification

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_lululemon_benchmark.py::test_four_filings_validate_and_remain_source_bound core/tests/test_management_kpi_admission.py -q` | 0 | **18 passed** in **1.40s** (1 inventory + 17 admission) |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **704 passed** in **162.16s** |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory annual/reversed copies; mixed from supplied extracted dir) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; std/conflicts/statement-provenance match; reversed identities match; extracted JSON unchanged |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: 4 filings + 4 management-kpi documents; mixed writes `management_kpi_admission.json` (`reported_observation_count=135`, `document_count=4`, 9 definitions, targets 3); annual-only omits that artifact; standardized/conflicts match; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release README.md present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited file this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/tests/test_lululemon_benchmark.py` | `4adfaf985e02209b52726114718e1f1eb7b2504a5bebaf32966dc19241a328a0` | 83953 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Five snapshot-matched production/test identities retained from `edit_replay_counts`: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`. Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` (`d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`) / `cursor-20260915-034910-19408.log` (`57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`) retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining admission restrictions: canonical identity, comparability, precedence, physical-page mapping, assurance, and presentation role stay unresolved; admitted observations remain audit-only and excluded from `StandardizedFinancials`.

---

## Remaining scope

Canonical management-KPI identities/comparability and later-audited precedence; `StandardizedFinancials` histories; Operating KPI analytical integration beyond store counts; workbook/Check; Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed `.37` is not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
