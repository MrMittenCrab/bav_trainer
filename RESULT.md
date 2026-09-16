# RESULT.md — Step 9M.2.4.1.1.1.36 Operating KPIs: source-grounded company-operated store history

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.36 — Operating KPIs: source-grounded company-operated store history  
**Work:** `0a6a4585ec404220aa91d71fc7439eb6`  
**Plan:** `fba56f17e8c540b78693d83b01516397`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `5a85d7a0a80a478af6170e6df29711d9ac6517ab5347c4952e510a92a263be89` (9185).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/data/filing.py`, `core/data/interface.py`, `core/data/standardized_io.py`, `core/data/historical_operating_kpis.py`, `core/ingestion/filing_json.py`, `core/ingestion/filing_validator.py`, `core/ingestion/filing_reconciler.py`, `core/ingestion/filing_standardizer.py`, `core/ingestion/operating_kpi.py`, `core/tests/fixtures/operating_kpis/lululemon_company_operated_stores.json`, `core/tests/test_operating_kpi_facts.py`, `core/tests/test_filing_json.py`, `core/tests/test_lululemon_benchmark.py`, `scripts/prepare_lululemon_operating_kpi_filings.py`, `RESULT.md`.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Rendered-page store totals `574` / `655` / `711` / `767` / `811`; temporary augmented-filing JSON export/reload; production validate/reconcile/standardize + standardized JSON reload; selected unit `stores`; order-independent selection; agreeing repeats; valid precedence with superseded `700` retained; unresolved equal-priority fail-closed; monetary-scale independence (`thousands` does not rescale counts; `ones` retained); sparse/null/legacy-absent payloads; invalid unit/value/date/identity fail without mutation; CLI rejection leaves inputs/outputs unchanged; geographic selected **56** and Americas `7928156` unchanged on the augmented path; required pytest **546 passed** in **159.00s**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH** |
| Retained via passing required tests this child | Five-period admit `2022-01-30`; geo **74** / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; selected Americas `7928156`; superseded `7928256` only in audit evidence; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Not claimed | Excel engine recalculation; workbook/Check/KPI analytics; parent or Step 9 completion; G6–G9 remainder |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Augmented filings and reconciliations used `TemporaryDirectory` only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Task 1 — Reported store facts

Independent transcription from cited physical PDF pages. FY2024/FY2025 text extraction is encoded; totals below are from rendered pages, not guessed glyph conversion. Licensed locations and outlets are disclosed separately and were not substituted for company-operated totals.

| Filing | PDF page | Table / label | Period | Role | Count | Unit |
|---|---:|---|---|---|---:|---|
| FY2022 | 7 | Total company-operated stores | 2023-01-29 | current_period | 655 | stores |
| FY2022 | 7 | Total company-operated stores | 2022-01-30 | comparative | 574 | stores |
| FY2023 | 11 (continuation; header also on p11) | Total company-operated stores | 2024-01-28 | current_period | 711 | stores |
| FY2023 | 11 | Total company-operated stores | 2023-01-29 | comparative | 655 | stores |
| FY2024 | 11 (rendered) | Total company-operated stores | 2025-02-02 | current_period | 767 | stores |
| FY2024 | 11 (rendered) | Total company-operated stores | 2024-01-28 | comparative | 711 | stores |
| FY2025 | 11 (rendered) | Total company-operated stores | 2026-02-01 | current_period | 811 | stores |
| FY2025 | 11 (rendered) | Total company-operated stores | 2025-02-02 | comparative | 767 | stores |

Excluded from capture: licensed locations (FY2022 26; FY2023 39/26), outlets (47 / 52 / 58), country/segment rows, sales per square foot.

Temporary copies only: `scripts/prepare_lululemon_operating_kpi_filings.py` appends fixture note facts without changing statements, share facts, geographic notes, or `source_sha256`. After export/reload:

| Filing | KPI observations | Geographic notes | Share facts |
|---|---:|---:|---:|
| FY2022 | 2 | 0 | 6 |
| FY2023 | 2 | 39 | 6 |
| FY2024 | 2 | 33 | 6 |
| FY2025 | 2 | 33 | 6 |

Identity `kpi.operating.store_count.company_operated`. Rejected: booleans, non-finite, negative/fractional counts, missing provenance, unsupported units, unknown identities, duplicate identities, invalid dates.

---

## Task 2 — Reconcile and round-trip

Optional `StandardizedFinancials.historical_operating_kpis` retains metric, population, period, value, and unit. Source paths, pages, and selection reasons stay in provenance. Legacy absent/null omits the field. Sparse histories do not infer zero. `2022-01-30` enters the model only through the accepted admit path; `2021-01-31` is not synthesized.

Measured selected store history after production reconcile + standardized JSON reload (forward and reversed filing order identical):

| Period | Selected count | Unit | Filing year | Basis | Reason | Page |
|---|---:|---|---:|---|---|---:|
| 2022-01-30 | 574 | stores | 2022 | comparative | sole_source_observation | 7 |
| 2023-01-29 | 655 | stores | 2023 | comparative | later_audited_presentation | 11 |
| 2024-01-28 | 711 | stores | 2024 | comparative | later_audited_presentation | 11 |
| 2025-02-02 | 767 | stores | 2025 | comparative | later_audited_presentation | 11 |
| 2026-02-01 | 811 | stores | 2025 | current_period | sole_source_observation | 11 |

Model axis with `--admit-period 2022-01-30`: `2022-01-30, 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01`. Without admit, `2022-01-30` remains selected in provenance and stays out of the model payload. Equal-priority value disagreement fails closed before write. Agreeing same-year repeats select deterministically (`agreeing_observations`) and retain both observations. Later-audited `711` supersedes earlier `700`; the loser remains in `note_facts` and supplemental conflicts. Store counts are not mixed into geographic identities.

Unchanged on the augmented five-period path: selected geographic facts **56**; Americas revenue `7928156`; model geographic identities **56**.

---

## Task 3 — Verification commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **546 passed** in **159.00s** |
| Independent temporary augment → JSON reload → validate/reconcile/standardize/reload | 0 | Selected `574/655/711/767/811` `stores`; geo **56**; Americas `7928156`; reversed order identical |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object`) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/data/historical_operating_kpis.py` | `e63766429f1525c3f158becd4e0e32327a214847b04f68c0ba226770b0429fb4` | 5558 |
| `core/data/interface.py` | `fed5135d80839902016ef9939557f38cdf21135199a85caa314ec9fbd0466fd8` | 4656 |
| `core/data/filing.py` | `6f0e4fa3bf04f5b8229e2ce072b3cd616d69f60b4a75a8b26e0e31be4af05a43` | 1907 |
| `core/data/standardized_io.py` | `8c2943f7b9578731cf64aa9b923b3b0d8951ad11d349b676924de36363e52d41` | 13819 |
| `core/ingestion/operating_kpi.py` | `12fb0e935a1121096b6d05b5fe9d446ea79af9147815920ca9849de971a429a1` | 5236 |
| `core/ingestion/filing_json.py` | `77e5a5268b33e061446766c2d66b8aabd2908f623c6f58c475491bb75be32827` | 12215 |
| `core/ingestion/filing_validator.py` | `1ead5bb19e584012c137e579a89323be4110b3552b099e6e548595ba31e67545` | 7254 |
| `core/ingestion/filing_reconciler.py` | `96f2fb2aaddc4c806695195e0b504d4abf97cfdfb142f792ac3947e8b13ef666` | 15704 |
| `core/ingestion/filing_standardizer.py` | `1dafaef68ecd411184a1e533f7c9bcb166438aa3e6e52c751d87e53cf44aa8d8` | 21467 |
| `core/tests/fixtures/operating_kpis/lululemon_company_operated_stores.json` | `7a7fca2965ea89bfc897a444676ecd0879bc120cd1ae24cb74270cae19c6ff3d` | 3125 |
| `core/tests/test_operating_kpi_facts.py` | `20b92e43626b5d292412a659c116310eadde055c6ea5655409efcb08b2ee943b` | 24351 |
| `core/tests/test_filing_json.py` | `c4bd7ac7f555bbc6ac2cdc0ea29e29810d0f0624d44e4ef791c953b0ed65a774` | 17170 |
| `core/tests/test_lululemon_benchmark.py` | `b8ee9fc5643125bbf37a471640e75a50294a699e0e44a5387808b684da1d569b` | 83934 |
| `scripts/prepare_lululemon_operating_kpi_filings.py` | `bb8346f3c5faad4858510d90fb5071bba52c9d4d39a0dc4d7fef35e162885b9c` | 3790 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining scope

KPI analytics/workbook/Check; other source-supported KPIs; Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
