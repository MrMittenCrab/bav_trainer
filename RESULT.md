# RESULT.md — Step 9M.2.4.1.1.1.35 Geographic segment workbook schedules and learner/Check integration

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.35 — Geographic segment workbook schedules and learner/Check integration  
**Work:** `65d8d6e9a2f94bb398cace9a2f361b28`  
**Plan:** `d70d43236d564997bc6ef217814ee918`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `48d7d40e7984538e972c8c6b6d2421b5bc8eb33354f1919964568e208cb231ce` (9352).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed (Check matched registered Excel formulas; Excel's calculation engine was not invoked).  
This child does **not** declare parent or Step 9 acceptance.

Edits this child: `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/checker.py`, `core/trainer/check_context.py`, `core/trainer/workbook.py`, `core/tests/test_geographic_segment_workbook.py`, `RESULT.md`.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Optional Geographic Segment Analysis sheet; five-period in-memory admit `2022-01-30` + JSON reload + temporary Trainer/Answer Key; **74** geographic practice cells; existing **486** identities preserved; Check blank **560/560** then filled **560/560**; independent mix/growth/margin/bridge match; `3607682 - 1397067 = 2210615`; focused pytest **376 passed** in 61.34s; checkpoint `3f6f5dde023847e3347a4c830d822614a28c81a9` **50/50 MATCH** |
| Retained (historical; not re-run) | Analytical-series pytest **144 passed**; `pytest core/tests` **1289 passed**; provenance `selected_geographic_segment_facts` (SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951`, 786300) |
| Not claimed | Excel engine recalculation; parent or Step 9 completion; G6–G9; benchmark publication |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Ratio tolerance: **`GEOGRAPHIC_RATIO_TOLERANCE = 1e-12`**. Monetary tolerance: **`0`**. Reported operating margin basis: `income_from_operations / net_revenue` (not BAV NOPAT margin). Temporary pair only (pytest `tmp_path` / process `TemporaryDirectory`).

---

## Task 1 — Optional reference schedule

Gated on validated `historical_segment`. Absent/null payloads add no sheet and no geographic specs (`ReferenceModelBuilder` committed Lululemon **486 / geo 0**; Fast Retailing **577 / geo 0**). Invalid contracts raise without mutating inputs.

Populated source rows: Americas / China Mainland / Rest of World net revenue and income from operations, reported consolidated amounts, reported `segment_total` only when present, reconciling amounts, dates, and units. Audit paths/hashes/pages/observations/conflicts stay outside the model.

Linked formulas: mix, adjacent-period growth, reported operating margins, calculated segment totals, signed ADD/SUBTRACT contributions, reconstructed consolidated operating profit, and differences vs reported consolidated amounts. Calculated totals are distinct from reported totals. Opening growth is `N/A` (not practiced). Sparse missing snapshots display `Source unavailable` without gap compression or inferred zeros.

---

## Task 2 — Learner practice and Check

Families 152–160 registered by family + segment/bridge identity + fiscal period. Source literals remain populated. Temporary Trainer practice starts blank yellow without Notes; matching Answer-Key cells contain formulas and non-empty Notes (mix/growth/reported-margin/bridge arithmetic; no causal claims). Check uses the validated series; unavailable displays and opening growth are excluded from the practice surface. Trusted-sheet source-edit controls cover `Geographic Segment Analysis`.

Measured five-period admitted Lululemon temporary pair:

| Metric | Value |
|---|---:|
| Existing identities/expectations preserved | **486** |
| Geographic additions | **74** |
| Total practice cells | **560** |
| Blank Check | total=560 blank=560 correct=0 incorrect=0 |
| Filled Check | total=560 blank=0 correct=560 incorrect=0 |
| Temporary Trainer bytes | 37455 |
| Temporary Answer Key bytes | 135763 |

---

## Task 3 — Verification

Unchanged extracted filings reconciled in memory with `--admit-period 2022-01-30`, `json.dumps`/`json.loads` reload, then `build_training_workbook` in temporary storage. Model values equal all **56** on-axis selections. Independent snapshot arithmetic matched the API for all five periods. Share sums **1.0**. All five revenue/IFOP differences **0.0**. FY2026: `3607682 - 1397067 = 2210615` with corporate ADD formula (not itemized SUBTRACT). FY2022 itemized signed formulas use `=-`.

### Measured commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_analysis.py core/tests/test_historical_segment.py core/tests/test_trainer.py core/tests/test_reference_integrity.py core/tests/test_source_availability.py core/tests/test_learner_ready_presentation.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py -q` | 0 | **376 passed** in 61.34s |
| Independent in-memory reconcile + JSON reload + series vs snapshot arithmetic + temporary pair Check | 0 | 56 selected/model values; five-period independent match; geo **74**; preserved **486**; blank 560/560; filled 560/560 |
| Protected artifacts vs checkpoint `3f6f5dde023847e3347a4c830d822614a28c81a9` | 0 | **50/50 MATCH** |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/engine/component_catalog.py` | `629d0b140be8db6a3ff9a2d5bf05b61aab62fbed896c163788eb1b441f730329` | 186601 |
| `core/engine/reference_model.py` | `51f9d0ee54c45154b371f1238bd99d49d0c32d944c63e300ceaf80adc679d372` | 310320 |
| `core/model/historical_expected.py` | `ff8f93a252e1e36580f433c1e3b1319f407d7c1d5ef1481deea3bfc879d53237` | 54281 |
| `core/trainer/checker.py` | `63a662264eea95fe4afcb970bd191ac45efaec166c78502da0cb938ca16e86ff` | 19034 |
| `core/trainer/check_context.py` | `c8fc77fa0a562a7926eb6965158dfd82e2416612cd83f5d5ad7bae53bee093f5` | 25740 |
| `core/trainer/workbook.py` | `c44f86e9e55f8660d9be268cb4e6f0a0527f56fcc26be8f744c331d457eff0ea` | 16165 |
| `core/tests/test_geographic_segment_workbook.py` | `e88a5a7a1fcf643863d9be074c9f24d04b6703e35c88e22ccd14d1cc9ca52d04` | 25752 |

### Protected-artifact hashes vs checkpoint `3f6f5dde023847e3347a4c830d822614a28c81a9`

All **50** git-tracked paths under `benchmark/lululemon/`, `benchmark/fast_retailing/`, `release/lululemon/`, and `release/fast_retailing/` matched the checkpoint blob SHA-256.

**Lululemon releases / reconciled / extracted / PDFs:**

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
| `benchmark/lululemon/source/LULU_FY2022_Annual_Report.pdf` | `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 4913067 |
| `benchmark/lululemon/source/LULU_FY2023_Annual_Report.pdf` | `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 5848446 |
| `benchmark/lululemon/source/LULU_FY2024_Annual_Report.pdf` | `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` | 5953217 |
| `benchmark/lululemon/source/LULU_FY2025_Annual_Report.pdf` | `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 6590658 |

**Fast Retailing (byte-identical, 577 identities, 0 unavailable displays):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `8a3f4f0c0e8bebb84317ead5a2e1c29679e8b70cdf58c211fe50ccbab04f5a23` | 644387 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |
| `benchmark/fast_retailing/reconciled/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining scope

G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; all TARGET Step 9 exit gates. Segment assets/capex, significant-expense schedules and D&A remain outside this step. No parent or Step 9 completion claim.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's admitted-five-period temporary pair **succeeded** (560 cells) and does not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (store KPIs, lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
