# RESULT.md — Step 9M.2.4.1.1.1.30 Lululemon supported comparative-period admission

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.30 — Lululemon supported comparative-period admission  
**Work:** `1df615c8e50b4b20932cb59593e7dd84`  
**Plan:** `772fcbfc00aa47b88aed4ee9c07503dc`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `ea28bb7d7dc4332248c93ec896c2b35d2502dc53c9bd11ed5ba98c3316ed1099` (7963).  
No commit / push / sync / checkpoint / branch change. No note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed (Check used formula-text identity).  
G6 updated in `benchmark/lululemon/GAPS.md`. This child does **not** declare parent or Step 9 acceptance.

---

## Task 1 — Explicit comparative admission

Generic `admit_periods` on `reconcile_filings` and repeatable CLI `--admit-period YYYY-MM-DD`. Default remains filing year-ends. No issuer-specific branches in `core/`.

Admission requires selected documentary IS+BS+CF coverage. Unsupported dates and missing-statement requests raise `ValueError` before artifacts are written. Downstream completeness, contradiction, and accounting gates are unchanged.

| Request | Result |
|---|---|
| none (default Lululemon) | periods `2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01` |
| `2022-01-30` | admitted; canonical axis five dates |
| `2021-01-31` | rejected: `missing selected balance_sheet coverage`; no outputs written |
| `2022-01-30` and `2021-01-31` | rejected on 2021-01-31; no partial admit |

Provenance (admission runs only) records `admitted_comparative_periods=["2022-01-30"]` and `excluded_comparative_periods=["2021-01-31"]`. 2021-01-31 observations remain `outside_model_axis`. CF beginning cash is not treated as BS coverage.

Incomplete CF `change_in_accounts_receivable` is omitted on the five-period axis (standardized CF 34→33), available periods `2023-01-29…2026-02-01`, **not** zero-filled. Sparse BS retained (NCIT `38074 / 28555 / 15864 / reported 0 / None`). Conflicts hash unchanged (`overlap_conflicts=3`).

Independent selected 2022-01-30 facts (USD thousands): revenue `6256617`; diluted WAS `130295`; PPE capex `394502`; inventory `966481`; common stock `616`; NCIT `38074`.

---

## Task 2 — Canonical regeneration

Baseline captured from the four-period release map: **376** semantic identities/expectations. After production admit + regenerate:

| Surface | Four-period baseline | Five-period canonical |
|---|---|---|
| Axis | 2023-01-29 … 2026-02-01 | **2022-01-30, 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01** |
| Standardized IS / BS / CF rows | 16 / 32 / 34 | 16 / 32 / **33** |
| `expected_specs` / semantic map | **376** | **486** (+110, removed **0**, changed existing expected values **0**) |
| Check blank / filled / inject | (376,0,0,376) / (376,0,0,376) | **(486,0,0,486) / (486,0,0,486) / (0,1,485,486)** |
| Trainer practice | 376 blank yellow, 0 Notes | **486** blank yellow, 0 Notes |
| Answer Key | 376 formulas + Notes | **486** formulas + nonempty Notes |
| `Source unavailable` displays | 74 / 74 | **101 / 101** |
| Hist-avg after-tax CoD | Source unavailable | still **Source unavailable**; no 4% substitute |

Added identities by period: **48** at 2022-01-30, **60** at 2023-01-29, **2** at 2024-01-28. Coordinate shifts only for the retained 376; expected values identical.

Four-period values preserved: capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; inventory CF diffs `-57181 / -37606 / 69962`; common stock `611 / 606 / 581 / 557`; NCIT `28555 / 15864 / 0 / None`. New opening: inventory `D_t` 2023 `-92552`; cash-after-capex/acq/repurchase 2022 `182004`.

Visible sheets match. Trainer source Net revenue `6256617 / 8110518 / 9619278 / 10588126 / 11102600`. Fast Retailing **577** identities; unavailable displays **0 / 0**.

---

## Task 3 — Regression evidence

`pytest core/tests` **1253 passed** (exit 0). Includes generic default/admission/rejection/omission/round-trip tests, Lululemon/Fast Retailing benchmarks, historical model, workbook, and Check. Four-period Lululemon value assertions retained as subsets of the five-period series. Default Lululemon CLI still emits four filing year-ends and does not rewrite committed five-period artifacts. Failure-immutability guards still pass.

Independent CLI `python -m core reconcile … --admit-period 2022-01-30` reproduced committed `standardized.json` / `provenance.json` / `conflicts.json` byte-for-byte.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| `pytest core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py` | 0 | 35 passed |
| Disposable admit probe (validate → reconcile → standardize → build) | 0 | 486 specs; +110 / 0 removed / 0 changed |
| `python scripts/build_lululemon_release.py` | 0 | five-period canonical reconciled + release |
| Independent CLI admit to `/tmp/lulu_admit_cli` | 0 | byte-identical to committed reconciled |
| Independent CLI default (no admit) | 0 | four filing year-ends; committed unchanged |
| Independent CLI `--admit-period 2021-01-31` | 1 | missing BS; wrote no artifacts |
| Canonical Check blank / filled / inject | 0 | (486,0,0,486) / (486,0,0,486) / (0,1,485,486); non-disclosing |
| `pytest core/tests` | 0 | **1253 passed** |

### Before → after hashes (SHA-256 / bytes)

**Lululemon four-period baseline (before):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `e92429b9ba77d0abd156e28eedcb1f8b4a9fe8ebf4484be4380e44fe4dd7bb1c` | 33232 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `e951e23d6031d57f2133a2aa50e1a2bf2c8ffcac481a56122361adb61d54261d` | 104190 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `fec1cc9ca587730593ea92fbd1f04483d06064cf74ff9ba3fedd59fcf24e3e84` | 434346 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `benchmark/lululemon/reconciled/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `benchmark/lululemon/reconciled/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `benchmark/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

**Lululemon five-period canonical (after):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `2e23f3b6d6fdba9b5f101d983a29f0854c9406474c92305ee06ca452e45afa6e` | 34670 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` | 119554 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `cc584a7bca130e0d52472a7b186bca00954e6eb98d2194418eb3e1c973c1e09f` | 561320 |
| `release/lululemon/availability.json` | `12e3b90aa640b76839e91f388b494644d686dfd705910a0d5541b2e28fbcd8a0` | 15691 |
| `benchmark/lululemon/reconciled/standardized.json` | `a3568c29e883c8ba57af23da7b4286641a3c5f929af311e2e9593c5f63ea2287` | 25011 |
| `benchmark/lululemon/reconciled/provenance.json` | `6799371215e02c888b3a5f687637b38dba4840bd1548cb1860a253f7a699cb12` | 699438 |
| `benchmark/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

Supporting copies match reconciled standardized/provenance/conflicts.

**Fast Retailing (unchanged):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `8a3f4f0c0e8bebb84317ead5a2e1c29679e8b70cdf58c211fe50ccbab04f5a23` | 644387 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Snapshot-limited authorization remains the five production/test files listed there. Original edit ownership, historical batch, and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` are retained. Publication recovery is not restarted and does not establish parent acceptance.

Hash-bound logs (retained, not re-executed as this child's proof):

- original `cursor-20260915-033742-18263.log` SHA-256 `d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`
- resumed `cursor-20260915-034910-19408.log` SHA-256 `57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`

Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING through the normal five stages.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward/reported-margin/inventory-intensity/BS-vs-CF comparison exercises; explicit-concept precedence; ambiguity rejection; original-row links; **101** Lululemon / **0** Fast Retailing unavailable displays on canonical releases; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Partial-period interest dependency closure, opening-only CoD `0.374` on supported fixtures, undefined ratios, no unavailable-history 4% substitute, pretax resolution and distinct tax expense. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; current successful gated generation.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates. G6 remains OPEN for the 2021-01-31 BS dependency. No blanket DONE. No prospective ID reservation.

No plan rewrite. Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
