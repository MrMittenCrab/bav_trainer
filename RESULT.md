# RESULT.md — Step 9M.2.4.1.1.1.33 Selected geographic facts into StandardizedFinancials

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.33 — Selected geographic facts into StandardizedFinancials  
**Work:** `68977f91981a43ecba811e61f0b865d6`  
**Plan:** `5d42faec1fed44d9b8ddfe6cf86443b9`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `225abab84d6ab3db0f22c0abee4502bab63d7cce9de818d40bf68bdc8d3e5f4c` (7867).  
No commit / push / sync / checkpoint / branch change. No workbook generation, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent or Step 9 acceptance.

Edits this child: `core/data/standardized_io.py`, `core/tests/test_historical_segment.py`, `RESULT.md`.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Strict segment-period reload (no truncation/strip/coercion); parameterized JSON encode/decode regressions including exactly `2025-12-31garbage`; focused contract/geographic/serialization/CLI tests **136 passed**; independent garbage reject; temporary `python -m core reconcile` admitting `2022-01-30`; 105 observations / 56 selected model values after reload; five-period bridges at tolerance 0; prior-presentation mutation; checkpoint `f8bd8169aed35ca21e8299d2dd6eb488bbf42420` protected hashes |
| Retained (historical; not re-run) | Role-aware geographic selection; JSON `note_facts` extraction; PDF SHA-256 identity; Lululemon/Fast Retailing benchmarks **171 passed**; `pytest core/tests` **1289 passed**; provenance `selected_geographic_segment_facts` (SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951`, 786300) |
| Not claimed | Workbook Check / spreadsheet recalculation; learner/Check segment schedules; parent or Step 9 completion |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Tolerance: **`SEGMENT_BRIDGE_TOLERANCE = 0`**.

---

## Task 1 — Strict segment-date reload

`_parse_segment_period` validates the original `historical_segment.periods[].period` value as a canonical `YYYY-MM-DD` string and a real calendar date **before** constructing `HistoricalSegmentPeriod`. Non-segment `_parse_date` truncation (`[:10]`) is unchanged.

Rejected without truncation, stripping, or coercion: trailing garbage, timestamp suffixes, surrounding whitespace, noncanonical forms, impossible dates, non-leap 29 February, and non-string values. Field-specific `ValueError` is raised before `standardized_from_payload` returns financial data. Duplicate-period, model-axis, and bridge validation are unchanged.

---

## Task 2 — Regression coverage

`core/tests/test_historical_segment.py` parameterized JSON encode/decode → `standardized_from_payload`:

- Rejected, including exactly `2025-12-31garbage` against a valid fixture admitting `2025-12-31`; payload left unchanged.
- Also: timestamps, whitespace, `2025/12/31`, `20251231`, `2025-1-31`, `12-31-2025`, `2025-02-30`, `2025-13-01`, `2025-04-31`, `2025-02-29`, `1900-02-29`, empty string, `null`, int, bool, float, list, object.
- Valid canonical round trips: `2025-12-31`, leap days `2024-02-29` / `2000-02-29`, `2025-01-01`.
- Existing missing/null omit-when-absent compatibility retained.

---

## Task 3 — Verification

### Independent trailing-garbage JSON reload

Mutated an otherwise valid payload admitting `2025-12-31` to `2025-12-31garbage`, then `json.dumps` / `json.loads` → `standardized_from_payload`.

- Raised: `historical_segment period must be a canonical YYYY-MM-DD date: '2025-12-31garbage'`
- Supplied payload unchanged: **True**

### Independent five-period bridges (USD thousands, tolerance 0)

Temporary five-period admit `2022-01-30`. Model values equal all **56** on-axis selections after export/reload.

| Period | Family | Revenue Σ segs = cons | IFOP bridge | IS cross-check |
|---|---|---|---|---|
| 2022-01-30 | itemized_reconciling | **6256617** | **1333355** | match |
| 2023-01-29 | corporate_column | **8110518** | **1328408** | match |
| 2024-01-28 | corporate_column | **9619278** | **2132676** | match |
| 2025-02-02 | corporate_column | **10588126** | **2505697** | match |
| 2026-02-01 | corporate_column | **11102600** | **3607682 − 1397067 = 2210615** | match |

Prior-presentation mutation (in-memory; extracted JSON not rewritten): Americas **`7928156`** survives standardization and JSON reload (forward and reversed filing order); superseded **`7928256`** remains only in audit evidence.

Default four-period reconcile keeps `2022-01-30` out of the model payload and in provenance.

### Measured commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py -q` | 0 | **136 passed** in 1.43s |
| Independent JSON reload of `2025-12-31garbage` | 0 | field-specific `ValueError`; payload unchanged |
| `python -m core reconcile` extracted → **temporary** `/tmp/lulu-seg-9m2411133.2fazMH` `--admit-period 2022-01-30` | 0 | `overlap_conflicts=3`; `note_facts=105`; selected=56; model facts=56 |
| Temporary standardized.json minus `historical_segment` vs committed | 0 | **equal** (statement lines, shares, leases, periods) |
| Temporary conflicts.json vs committed | 0 | **equal** (SHA-256 `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0`) |
| Statement-only provenance vs committed | 0 | **equal** |
| Fast Retailing payload omit-field round trip (shares/lease preserved) | 0 | **no** `historical_segment` field |
| Protected artifacts vs checkpoint `f8bd8169aed35ca21e8299d2dd6eb488bbf42420` | 0 | **match** (table below) |

Temporary standardized.json SHA-256 `6c9aad59b04a5995742c68e08f1a704953796fc9fad97a036b08aeeab59051e5` (29584) — not a committed artifact. Temporary provenance SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951` (786300) matches the prior selection serialization.

### Protected-artifact hashes vs checkpoint `f8bd8169aed35ca21e8299d2dd6eb488bbf42420`

**Lululemon (five-period canonical; unchanged):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `4e06ce78957a291857d9db074113f071021d057234ff0f7376afafbce4b76904` | 34670 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` | 119554 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `cc584a7bca130e0d52472a7b186bca00954e6eb98d2194418eb3e1c973c1e09f` | 561320 |
| `release/lululemon/availability.json` | `12e3b90aa640b76839e91f388b494644d686dfd705910a0d5541b2e28fbcd8a0` | 15691 |
| `benchmark/lululemon/reconciled/standardized.json` | `a3568c29e883c8ba57af23da7b4286641a3c5f929af311e2e9593c5f63ea2287` | 25011 |
| `benchmark/lululemon/reconciled/provenance.json` | `6799371215e02c888b3a5f687637b38dba4840bd1548cb1860a253f7a699cb12` | 699438 |
| `benchmark/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `benchmark/lululemon/extracted/LULU_FY2022.json` | `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` | 60110 |
| `benchmark/lululemon/extracted/LULU_FY2023.json` | `fcaa9abb417c4f96eb5496c5fc3f1b683b13c17a498c400de869e81880788c05` | 73971 |
| `benchmark/lululemon/extracted/LULU_FY2024.json` | `0ddc2893afa892d2e1684a38fdc3a3275bb82ace5d4a237c785ad1246d327c4f` | 72244 |
| `benchmark/lululemon/extracted/LULU_FY2025.json` | `fc4ffe8e7ce7f919c815ff4eecdb171d7f75f528a925cbced5814044d8363a10` | 70176 |

**Source PDFs (unchanged):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `LULU_FY2022_Annual_Report.pdf` | `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 4913067 |
| `LULU_FY2023_Annual_Report.pdf` | `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 5848446 |
| `LULU_FY2024_Annual_Report.pdf` | `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` | 5953217 |
| `LULU_FY2025_Annual_Report.pdf` | `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 6590658 |

**Fast Retailing (byte-identical releases, 577 identities, 0 unavailable displays):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `8a3f4f0c0e8bebb84317ead5a2e1c29679e8b70cdf58c211fe50ccbab04f5a23` | 644387 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining scope

Segment analytical schedules and learner/Check integration; G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; all TARGET Step 9 exit gates. Segment assets/capex, significant-expense schedules and D&A remain outside this step. No parent or Step 9 completion claim.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (store KPIs, lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
