# RESULT.md — Step 9M.2.4.1.1.1.34 Historical geographic segment analytical series

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.34 — Historical geographic segment analytical series  
**Work:** `c70f8d503c0d49ecbb4ff0f755597f34`  
**Plan:** `748d6c34a29f4ce39633b855799d7e26`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs HEAD). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `7ac9f9b1254972d1073ef3988575d86642d758876305857156d7d3ea2f60de9d` (8154).  
No commit / push / sync / checkpoint / branch change. No workbook generation, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent or Step 9 acceptance.

Edits this child: `core/model/geographic_segment.py`, `core/tests/test_geographic_segment_analysis.py`, `RESULT.md`.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Optional geographic analytical series; independent five-period mix/growth/margin/bridge recomputation after in-memory admit `2022-01-30` and JSON reload; 105 observations / 56 selected model values; exact monetary diffs 0; share sums 1.0 within `GEOGRAPHIC_RATIO_TOLERANCE = 1e-12`; prior-presentation mutation; focused analytical/contract/geographic/serialization/CLI tests **144 passed**; checkpoint `38a1bc57f1b8caa5ef742041d7b660e9ed07779b` protected hashes |
| Retained (historical; not re-run) | Strict segment-period reload; parameterized `2025-12-31garbage` reject; role-aware geographic selection; JSON `note_facts` extraction; PDF SHA-256 identity; Lululemon/Fast Retailing benchmarks **171 passed**; `pytest core/tests` **1289 passed**; provenance `selected_geographic_segment_facts` (SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951`, 786300) |
| Not claimed | Workbook Check / spreadsheet recalculation; learner/Check segment schedules; parent or Step 9 completion |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Monetary tolerance: **`SEGMENT_BRIDGE_TOLERANCE = 0`**. Ratio tolerance: **`GEOGRAPHIC_RATIO_TOLERANCE = 1e-12`**. Reported operating margin basis: `income_from_operations / net_revenue` (not BAV NOPAT margin).

---

## Task 1 — Optional analytical series

`core/model/geographic_segment.py` consumes only `StandardizedFinancials.historical_segment` after `validate_historical_segment`. Series are keyed by `canonical_fiscal_periods` and identities `americas` / `china_mainland` / `rest_of_world`.

Computed per period: revenue share of consolidated revenue, adjacent-period revenue growth, reported operating margin, calculated segment revenue/IFOP totals, signed reconciling contributions in sorted identity order, reconstructed consolidated IFOP, and differences versus reported consolidated revenue/IFOP. Corporate-column ADD versus itemized SUBTRACT semantics and reported signs are preserved. Calculated totals are separate from any reported `segment_total`.

Missing/null payloads make the module absent (`MissingLineError`). Missing snapshots on the model axis yield `SOURCE_UNAVAILABLE` only for dependent outputs; gaps are not compressed. Opening growth is `None`. Later growth requires both immediately adjacent snapshots. Zero denominators use `#N/A`; zero numerators and negative profits are preserved. Invalid contracts are rejected without mutating inputs.

---

## Task 2 — Independent Lululemon five-period recomputation

Unchanged extracted filings reconciled in memory with `--admit-period 2022-01-30`, then `json.dumps` / `json.loads` → `standardized_from_payload`. Model values equal all **56** on-axis selections. Independent snapshot arithmetic matched the API for all five periods.

| Period | Family | Revenue Σ segs = cons | IFOP reconstructed | Mix A / CM / RoW | Growth A / CM / RoW |
|---|---|---|---|---|---|
| 2022-01-30 | itemized_reconciling | **6256617** | **2102008 − 41394 − 8782 − 718477 = 1333355** | 0.8470881308541022 / 0.06940827606995921 / 0.08350359307593865 | opening absent |
| 2023-01-29 | corporate_column | **8110518** | **2803809 − 1475401 = 1328408** | 0.8405694926020755 / 0.07108090999859688 / 0.08834959739932764 | 0.2863348897131383 / 0.3275495612085819 / 0.3715398602737104 |
| 2024-01-28 | corporate_column | **9619278** | **3476332 − 1343656 = 2132676** | 0.7933700429491694 / 0.10019047167573283 / 0.1064394853750978 | 0.11942772184454784 / 0.6717345790047927 / 0.428867884241537 |
| 2025-02-02 | corporate_column | **10588126** | **3840362 − 1334665 = 2505697** | 0.7487780179419852 / 0.1285720438158745 / 0.1226499382421403 | 0.03885255699064697 / 0.4125269776707894 / 0.26835607220050184 |
| 2026-02-01 | corporate_column | **11102600** | **3607682 − 1397067 = 2210615** | 0.7067753499180373 / 0.1580529785815935 / 0.1351716715003693 | −0.010230878403502655 / 0.2890261559040855 / 0.15564366530035814 |

Share sums measured **exactly 1.0** (within 1e-12). All five monetary revenue/IFOP differences measured **0.0**. 2022 itemized operations in stable identity order: `acquisition_related_expenses`, `amortization_of_intangible_assets`, `general_corporate_expenses`. 2026 corporate signed contribution `income_from_operations.corporate_unallocated = -1397067`.

Reported operating margins (IFOP / revenue), same five periods:

| Period | Americas | China Mainland | Rest of World |
|---|---:|---:|---:|
| 2022-01-30 | 0.3522734176794834 | 0.3852936367760402 | 0.12953201263278782 |
| 2023-01-29 | 0.3672544031833585 | 0.3414813105916188 | 0.14402681697720082 |
| 2024-01-28 | 0.3848689542375322 | 0.35 | 0.1971263958057216 |
| 2025-02-02 | 0.3803604520395411 | 0.37452812933167906 | 0.24252117418855057 |
| 2026-02-01 | 0.32632135107181764 | 0.39954604487465517 | 0.23048434889858918 |

Prior-presentation mutation (in-memory; extracted JSON not rewritten): selected Americas **`7928156`** survives standardization, JSON reload, and the analytical series (forward and reversed filing order); superseded **`7928256`** remains only in audit evidence; analytical series equals the unmutated selected series.

Synthetic regressions covered sparse snapshots (no gap compression), absent/null payloads, Fast Retailing omit-field compatibility, zero denominators / zero numerators / negative profits, reordered inputs, bridge contradictions, incompatible identities, and failure immutability.

---

## Task 3 — Verification

### Measured commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py -q` | 0 | **144 passed** in 1.56s |
| Independent in-memory reconcile + JSON reload + series vs snapshot arithmetic | 0 | 105 observations; 56 selected/model values; five-period independent match; `3607682 - 1397067 = 2210615` |
| Fast Retailing payload omit-field (`historical_segment` absent) | 0 | module absent |
| Protected artifacts vs checkpoint `38a1bc57f1b8caa5ef742041d7b660e9ed07779b` | 0 | **match** (table below) |

Default four-period committed `standardized.json` is unchanged and still omits `2022-01-30` from the model payload. Five-period series used a temporary in-memory admit only.

New files: `core/model/geographic_segment.py` SHA-256 `484d8841495e2cfdb865c402ad01162488b5d1145a7c481c23e5882bd3176cfb` (11091); `core/tests/test_geographic_segment_analysis.py` SHA-256 `f67c25f10b70b015d7570814151690413070752c688ae373f5b3d3dd7f947909` (19667).

### Protected-artifact hashes vs checkpoint `38a1bc57f1b8caa5ef742041d7b660e9ed07779b`

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

Segment workbook schedules and learner/Check integration; G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; all TARGET Step 9 exit gates. Segment assets/capex, significant-expense schedules and D&A remain outside this step. No parent or Step 9 completion claim.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (store KPIs, lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
