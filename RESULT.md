# RESULT.md — Step 9M.2.4.1.1.1.38 Operating KPIs: content-aware management-observation admission and mixed-directory repair

**Status:** BLOCKED (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.38 — Operating KPIs: content-aware management-observation admission and mixed-directory repair  
**Work:** `6bf50da023664e0daff65822d5cfc0f2`  
**Plan:** `0448f2dd8ce4488fad3e085a873dc58d`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006` (resume accepted checkpoint evidence; repair mixed-directory loading)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `1d6ee5e0ffd67ef7ce8094eb71bebd7f79065b8739fc435efe673049c2f3049a` (11890).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi.py`, `core/ingestion/filing_cli.py`, `core/ingestion/filing_json.py`, `core/ingestion/filing_validator.py`, `core/ingestion/filing_reconciler.py`, `core/ingestion/filing_standardizer.py`, `core/__main__.py`, `core/tests/test_management_kpi_admission.py`, `RESULT.md`.  
`core/data/filing.py` was permitted and left unchanged.

---

## Required plan change

`core/tests/test_lululemon_benchmark.py:133` still globs `LULU_FY*.json` and requires `int(stem.replace("LULU_FY",""))`. Mixed extracted files include `LULU_FY2022_management_kpis.json`, so the inventory assertion raises `ValueError: invalid literal for int() ... '2022_management_kpis'`. That file is outside this child's permitted edits. Plan should allow a narrowly necessary inventory update that still checks the four annual filings (explicit `LULU_FY2022.json`…`LULU_FY2025.json`, or an equivalent filter) and excludes management-KPI documents.

Functional mixed-directory admission is implemented and measured. This inventory glob is the only remaining required-suite failure.

---

## Task 1 — Dispatch and validate supplied observations

Directory loading classifies each `*.json` by validated structure, not filename. Management documents are identified by string `company` plus `report`, `kpi_definitions`, `reported_kpis`, `store_counts_by_market`, and `management_targets`. Schema version `1.0` is not used as the discriminator. Annual filings still use strict `load_extracted_filing`. Unknown, ambiguous, and malformed schemas fail with document-specific diagnostics.

Bound management documents reuse filing source-root containment and computed PDF hashes via company/ticker, fiscal year/end, and `source_file`. Printed Form 10-K/Annual Report page references remain unresolved physical-page mappings. Assurance and presentation role stay `unknown`. Targets are nonhistorical. Direct `load_extracted_filing` of a management document still raises `company object is required`.

---

## Task 2 — Admission audit output

Ordinary `validate-source` / `reconcile` process the mixed directory, retain the four statement filings, and write `management_kpi_admission.json` only when management documents are present. Canonical `standardized.json`, `provenance.json`, and `conflicts.json` do not gain extra top-level keys, so statement/geographic/store selectors and `StandardizedFinancials` stay unchanged. Observation identities keep definition, scope, period, unit, basis, comparison, and qualifiers; reported vs constant-dollar, stocks vs flows, bounds, and calendar-adjusted comparisons are not collapsed. Agreeing/conflicting store totals vs market tables and vs accepted temporary store facts are retained as diagnostics without canonical overwrite.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Mixed extracted directory loads 4 filings + 4 management documents; 135 reported observations (29/36/37/33) plus 9 definitions, market tables (totals 655/711/767/811), and 3 nonhistorical targets survive audit serialization; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; renamed/reversed inputs keep identities; unknown/ambiguous/malformed/dangling/orphan/conflict/hash-failure controls fail closed; mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; required pytest **703 passed**, **1 failed** (`test_four_filings_validate_and_remain_source_bound`); checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON SHA-256 values unchanged vs HEAD |
| Retained via passing required tests this child | Five-period admit `2022-01-30`; selected store provenance and labels from prior children; geo **74** / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; canonical management-history selection; parent or Step 9 completion; G6–G9 remainder; required Lululemon inventory glob |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations and augmented filings used `TemporaryDirectory` only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Task 3 — Measured verification

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_admission.py -q` | 0 | **17 passed** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 1 | **703 passed**, **1 failed** in **163.89s**; failure is `test_four_filings_validate_and_remain_source_bound` glob inventory |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_lululemon_benchmark.py -k 'not test_four_filings_validate_and_remain_source_bound' -q` | 0 | **35 passed**, 1 deselected in **7.26s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object`; example/release/benchmark `xlsx`/`json`/`pdf` plus release README.md) |
| Extracted JSON vs `HEAD` blob SHA-1 | 0 | eight files **UNCHANGED**, including four management-KPI documents |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi.py` | `c0d4d15254c2de7b2ff76b93a79678391b59db235727c4c11ca07667e7db96f2` | 44680 |
| `core/ingestion/filing_cli.py` | `038880d34385430b85cb1ec7db4d7d9702a2eb6b84e7a86a31438400def7c805` | 2983 |
| `core/ingestion/filing_json.py` | `46bc9271922965c3141a5161eceeb15c5485f5dd3ee2f5ca9b5ec55724d93562` | 12851 |
| `core/ingestion/filing_validator.py` | `9c2051171592cb7e230f8ee62c1b645fc014ce28b029747d839c186439e59a00` | 7491 |
| `core/ingestion/filing_reconciler.py` | `deb6d89750bc763868800a6923179d59d4a2d0bf18cd218f778d3b73e9fdc85d` | 16295 |
| `core/ingestion/filing_standardizer.py` | `6ee34744c454117ec01b377006924fb21c3cdf8d0461f40b505b8e2197b1bbcf` | 21864 |
| `core/__main__.py` | `a6864ea42c6b978bf2ccea2a4fcb10c76518502c8adc2d779672af50747a9e6a` | 16007 |
| `core/tests/test_management_kpi_admission.py` | `5ba7fff645d14d50e9e9e48f4eeef3eec9f7e79c7ec641dd25952b7881e49a83` | 21696 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining admission restrictions: canonical identity, comparability, precedence, physical-page mapping, assurance, and presentation role stay unresolved; admitted observations remain audit-only and excluded from `StandardizedFinancials`.

---

## Remaining scope

Canonical management-KPI identities/comparability and later-audited precedence; `StandardizedFinancials` histories; Operating KPI analytical integration beyond store counts; workbook/Check; Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

No plan rewrite. Required plan change is recorded above.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
