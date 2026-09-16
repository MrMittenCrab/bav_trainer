# RESULT.md — Step 9M.2.4.1.1.1.37 Operating KPIs: historical company-operated store analysis

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.37 — Operating KPIs: historical company-operated store analysis  
**Work:** `7608d8dab10c49959e9d24407e3cc040`  
**Plan:** `88639dae567748c4971027f20b81df83`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `301c09f3696e88d8dfa9f3ab307f12c75e00a5cccc35eda71d783f1179e7b59b` (8419).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, or Step 9 acceptance.

Edits this child: `core/model/operating_kpi.py`, `core/tests/test_operating_kpi_analysis.py`, narrowly necessary helpers in `core/tests/test_operating_kpi_facts.py`, `RESULT.md`.

---

## Task 1 — Optional analytical series

`operating_kpi_applicable` is true only when `StandardizedFinancials.historical_operating_kpis` is supplied. `compute_operating_kpi_series` validates that contract, uses `canonical_fiscal_periods`, and returns metric/population `store_count` / `company_operated`, per-period count units, period-end counts, net count change `current - previous`, and growth `(current - previous) / previous`.

Absent/null payloads raise `MissingLineError: operating KPI sources not available`. Malformed supplied payloads raise validation errors. Opening change/growth is `None`. Later comparisons require both immediately adjacent model-period observations; missing observations yield `Source unavailable` without compressing gaps. Zero denominators yield `#N/A`. Actual zero counts and negative net changes remain numeric. Accepted `stores` / `ones` are count units independent of monetary scale. The series labels net count changes only; it does not derive closures, same-store sales, revenue-per-store, geographic allocation, or operating causality.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Temporary source-grounded augment → validate / reconcile / standardize / JSON reload in both filing orders produced identical series: counts `574/655/711/767/811` `stores`, net changes `None/81/56/56/44`, growth `None`, `81/574`, `56/655`, `56/711`, `44/767` within `1e-12`; geo **56** and Americas `7928156` retained; model KPI JSON has no source labels/notes; in-memory controls for absent/null, shuffled observations, both count units, monetary-scale independence, single-period, sparse gaps, zero denominator, zero current count, declining counts, malformed values/identities/units/duplicates/off-axis periods, canonical-axis rejection, and success/failure immutability; required pytest **687 passed** in **164.76s**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH** |
| Retained via passing required tests this child | Five-period admit `2022-01-30`; selected store provenance and labels from prior children; geo **74** / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; other Operating KPIs; parent or Step 9 completion; G6–G9 remainder |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Augmented filings and reconciliations used `TemporaryDirectory` only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Task 2 — Measured arithmetic and source-to-analysis continuity

Independent temporary reconstruction of serialized source-grounded filings, both orders, after validate / reconcile / standardize / standardized JSON reload. Analytical outputs after reload equalled pre-reload outputs and the reversed-order series. Expected values were recomputed from period-end counts (`current - previous` and `(current - previous) / previous`), not from company-specific module constants.

| Period | Count | Unit | Net change | Growth |
|---|---:|---|---:|---:|
| 2022-01-30 | 574 | stores | None | None |
| 2023-01-29 | 655 | stores | 81 | 81/574 = 0.14111498257839722 |
| 2024-01-28 | 711 | stores | 56 | 56/655 = 0.08549618320610687 |
| 2025-02-02 | 767 | stores | 56 | 56/711 = 0.07876230661040788 |
| 2026-02-01 | 811 | stores | 44 | 44/767 = 0.05736636245110821 |

Measured availability / control outcomes:

| Case | Result | Inputs |
|---|---|---|
| Absent / null payload | `operating_kpi_applicable` false; `MissingLineError` | unchanged |
| Fast Retailing standardized.json | no `historical_operating_kpis`; same unavailable behavior | committed JSON unread as KPI source |
| Shuffled / reversed observations | same series; observation list order preserved after success | observations unchanged except explicit reorder assertion |
| `stores` vs `ones`; thousands vs millions units text | identical counts/changes/growth; unit identity preserved | monetary scale ignored |
| Single period 811 | count 811; change/growth `None` | unchanged |
| Sparse 655, gap, 767 | gap and later change/growth `Source unavailable`; 767-vs-655 growth not substituted | unchanged |
| Prior count 0, current 10 | change 10; growth `#N/A` | unchanged |
| Current count 0 after 10 | count 0; change -10; growth -1.0 | unchanged |
| Decline 711 → 655 | change -56; growth -56/711 | unchanged |
| Malformed value/identity/unit, duplicate key, off-axis period | `ValueError`; mutated payload unchanged | success path also leaves inputs unchanged |
| Non-canonical `periods` argument | `operating KPI series must use the canonical fiscal axis` | original payload unchanged |

Geographic selected facts remain **56**; Americas revenue `7928156`. Model-facing KPI JSON contains neither `source_label` nor `source_note`; five selected KPI provenance rows remain in the separate audit payload.

---

## Task 3 — Regressions and protected hashes

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **687 passed** in **164.76s** |
| Independent temporary augment → JSON reload → analysis (forward and reversed) | 0 | Counts `574/655/711/767/811` `stores`; changes `None/81/56/56/44`; growth matches independent arithmetic within `1e-12`; orders equal; geo **56**; Americas `7928156` |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object`) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/operating_kpi.py` | `0740f4f8e04c03d033d2ac702951cde6d3c824af21a8e6f7fb3bbe5d435e698e` | 4714 |
| `core/tests/test_operating_kpi_analysis.py` | `86219dff011a83d6e98dab1434e15e2dac4cf65fe02f5f11189befa01eed8485` | 16913 |
| `core/tests/test_operating_kpi_facts.py` | `21e9ede38cb93d4d13dd963b6cbead7ab39f43e3861964cf6f34bd3cc4b66a2f` | 39052 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining scope

KPI workbook/Check and other source-supported KPIs; Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
