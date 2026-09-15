# RESULT.md — Step 9M.2.4.1.1.1.29 Lululemon comparative-period coverage assessment

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.29 — Lululemon comparative-period coverage assessment  
**Work:** `84e4473456c849d592caecc54f5622d1`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `e564087b3e08b1043e28c759c7bbd687a53ddec75c980e4ea228c0440ca92b65` (6783).  
No commit / push / sync / checkpoint / branch change. No production, source, reconciliation, provenance, or release edits. No note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed (Check used formula-text identity).  
G6 disposition updated in `benchmark/lululemon/GAPS.md` only. Assessment does **not** deliver axis expansion or parent acceptance.

---

## Task 1 — Comparative-period eligibility

`reconcile_filings` sets `periods = sorted({filing.filing.period_end})` only. Comparative observations remain in `reconciled.values` and provenance `outside_model_axis`; `_group_by_row` drops them from model-facing `StandardizedFinancials`. `canonical_fiscal_periods` then reads that already-truncated axis.

Validated 4/4 filings, 0 warnings. Reconciled documentary periods:

| Period | Role vs filings | IS rows | BS rows | CF rows | Diluted WAS (ones → statement thousands) | Missing required dependency |
|---|---|---:|---:|---:|---|---|
| 2022-01-30 | FY2022+FY2023 comparative (not a filing `period_end`) | 20 | 32 | 36 | 130295000 → 130295 (FY2022 p50 and FY2023 p56 agree) | Individual CF `change_in_accounts_receivable` (FY2024/FY2025 only; 2023–2026). Not a missing statement. |
| 2021-01-31 | FY2022 comparative only | 19 | **0** | 34 | 130871000 → 130871 (FY2022 p50) | **Entire BS** (32 FY2022 BS lines have 2023-01-29 and 2022-01-30 only). CF beginning cash `1093505` is not a BS. |
| 2023-01-29 … 2026-02-01 | Four filing year-ends (canonical) | — | — | — | 128017 / 127060 / 123935 / 119068 | None for the accepted four-period map |

FY2022 PDF (source SHA-256 `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e`):

- p49 Consolidated Balance Sheets: columns January 29, 2023 and January 30, 2022 only. No January 31, 2021 BS.
- p50 IS: Net revenue `8,110,518 / 6,256,617 / 4,401,879`; diluted WAS `128,017 / 130,295 / 130,871`.
- p53 CF: purchase of PPE `(638,657) / (394,502) / (229,226)`; three years including January 31, 2021.

FY2023 PDF p56 IS restates 2022-01-30 revenue `6,256,617` (agrees with FY2022). Selected 2022-01-30 IS/CF values have two agreeing observations; later filing year wins. 2022-01-30 BS is FY2022 p49 only.

2022-01-30 is eligible as a fifth model period independently of the missing 2021-01-31 BS. 2021-01-31 is not eligible as a sixth model-facing period. A six-period probe via the same override plus `date(2021,1,31)` yields IS/CF complete and **32/32 BS values None**; those Nones were not treated as zero.

No standalone `interest_expense` on either comparative IS (2022-01-30 other income `514`; 2021-01-31 other income `-636`).

---

## Task 2 — Disposable five-period build

Assessment-only axis override (production code untouched):

```text
extended = dataclasses.replace(
    reconciled,
    periods=tuple(sorted({*reconciled.periods, date(2022, 1, 30)})),
)
fin5 = standardize_reconciled(extended)          # production
builder = ReferenceModelBuilder(fin5)            # production
build_training_workbook(fin5, disposable_path)   # production
```

Axis: `2022-01-30, 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01` (year-contiguous; `canonical_fiscal_periods` accepted). Disposable artifacts only under `/tmp/lulu_g6_assessment/five_period_build/` (not canonical).

| Surface | Four-period accepted | Five-period assessment |
|---|---|---|
| Standardized IS / BS / CF rows | 16 / 32 / 34 | 16 / 32 / **33** |
| `expected_specs` / semantic map | **376** | **486** (+110, removed 0) |
| Existing expected values | 376 identities | **0 changed** (376 formula-only column shifts) |
| Check blank / filled | (0,0,376,376) / (376,0,0,376) | **(486,0,0,486) / (486,0,0,486)** |
| Incorrect injection | non-disclosing | **(0,1,485,486)**; injected `123456789` unchanged; no comment |
| Trainer practice | 376 blank yellow, 0 Notes | **486** blank yellow, 0 Notes |
| Answer Key | 376 formulas + Notes | **486** formulas + Notes |
| `Source unavailable` displays | 74 / 74 | **101 / 101** |
| Hist-avg after-tax CoD | `Source unavailable` / `absent_line` | still **Source unavailable**; no 4% substitute |

Added exercises by period: **48** at 2022-01-30 (new opening, `period_scope=all`), **60** at 2023-01-29 (old opening becomes comparable), **2** at 2024-01-28 (`post_comparable` shift: `profitability_change.noa_turnover_change`, `quality_change.accrual_ratio_change`).

Fail-closed omission: CF `change_in_accounts_receivable` / `Accounts receivable, net` has selected values only on 2023-01-29…2026-02-01 (FY2024/FY2025). Production omitted the incomplete IS/CF row; it was **not** filled with zero. No practice family required that line; the builder succeeded.

Independent arithmetic from selected facts (USD thousands):

| Item | Independent result | Matches disposable series |
|---|---|---|
| Revenue 2022-01-30 | 6256617 (PDF p50/p56) | yes |
| Diluted WAS 2022-01-30 | 130295000/1000 = 130295 | yes |
| PPE capex | 394502 / 638657 / 651865 / 689232 / 680802 | yes; four accepted values preserved |
| Inventory `B_t` 2023 | `-(1447367-966481) = -480886` | yes (new comparable) |
| Inventory `D_t` 2023 | `-573438 - (-480886) = -92552` | yes |
| Existing `B_t`/`D_t` 2024–2026 | `-57181 / -37606 / 69962` differences with `B+D=CF` | unchanged |
| Common stock | 616 / 611 / 606 / 581 / 557 | yes |
| NCIT | 38074 / 28555 / 15864 / 0 / None | yes |
| Repurchase residuals 2023–2026 | `-116195 / 1085647 / -207544 / -256674` | preserved; 2022 cash-after-capex/acq/repurchase `182004` is new opening |

Build exception: none.

---

## Task 3 — Acceptance disposition

**G6 remains OPEN.** 2022-01-30 is source-eligible for a future fifth-period axis. 2021-01-31 is not, until a complete BS is supplied. This child does not expand the canonical axis.

Implementation boundary for a later planned step (not reserved here):

1. Replace filing-`period_end`-only `reconcile_filings.periods` with an explicit policy that may add a comparative date only when selected IS+BS+CF coverage exists.
2. Keep fail-closed omission of incomplete IS/CF rows (`change_in_accounts_receivable`); do not invent zeros or promote 2021-01-31 on CF beginning-cash.
3. Expect map 376→486 with **no** existing expected-value mutation; regenerate Trainer/Answer Key/Check; unavailable displays rise 74→101.

Canonical inputs and both releases remain hash-identical to the 9M.2.4.1.1.1.28 inventory. Accepted **376 / 577** identities and expectations retained.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| Inventory + reconcile + PDF page extract + eligibility (inline Python) | 0 | 2022-01-30 IS/BS/CF complete; 2021-01-31 BS absent; AR CF incomplete on a 5-period axis |
| Disposable five-period `standardize_reconciled` + `ReferenceModelBuilder` + `build_training_workbook` + Check | 0 | 486 specs; blank/filled/incorrect as above; canonical hashes unchanged |
| Post-assessment SHA-256 of TARGET, releases, reconciled, recovery evidence, retained logs | 0 | hashes below; Fast Retailing map still 577 |

### Canonical inventory (SHA-256 / bytes; unchanged)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `e92429b9ba77d0abd156e28eedcb1f8b4a9fe8ebf4484be4380e44fe4dd7bb1c` | 33232 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `e951e23d6031d57f2133a2aa50e1a2bf2c8ffcac481a56122361adb61d54261d` | 104190 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `fec1cc9ca587730593ea92fbd1f04483d06064cf74ff9ba3fedd59fcf24e3e84` | 434346 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `benchmark/lululemon/reconciled/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `8a3f4f0c0e8bebb84317ead5a2e1c29679e8b70cdf58c211fe50ccbab04f5a23` | 644387 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Snapshot-limited authorization remains the five production/test files listed there. Original edit ownership, historical batch, and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` are retained. Publication recovery is not restarted and does not establish parent acceptance.

Hash-bound logs (retained, not re-executed as this child's proof):

- original `cursor-20260915-033742-18263.log` SHA-256 `d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`
- resumed `cursor-20260915-034910-19408.log` SHA-256 `57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`

Distinguish original successful subprocess exits from resumed wrapper failures; this child's evidence is the fresh assessment above.

Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING through the normal five stages, with remaining benchmark-improvement and parent-acceptance obligations.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward/reported-margin/inventory-intensity/BS-vs-CF comparison exercises; explicit-concept precedence; ambiguity rejection; original-row links; 74 Lululemon / 0 Fast Retailing unavailable displays on **canonical** releases; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Partial-period interest dependency closure, opening-only CoD `0.374` on supported fixtures, undefined ratios, no unavailable-history 4% substitute, pretax resolution and distinct tax expense. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; current successful gated generation and 74/0 unavailable displays.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates. No blanket DONE. No prospective ID reservation.

No plan rewrite. Required next plan work is a **new** implementation step if axis expansion is authorized; this assessment must not be treated as delivery.
