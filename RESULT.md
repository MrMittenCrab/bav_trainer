# RESULT.md — Step 9M.2.4.1.1.1.35 Geographic segment workbook schedules and learner/Check integration

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.35 — Geographic segment workbook schedules and learner/Check integration  
**Work:** `65d8d6e9a2f94bb398cace9a2f361b28`  
**Plan:** `15fb173563b44460aaac1704b4f10c23`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `29027a4bf6f80ee02c458b72cf6fea9848c42a87c4fcc0e6fecd52508f2cd096` (10802).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed (Check matched registered Excel formulas; Excel's calculation engine was not invoked).  
This child does **not** declare parent or Step 9 acceptance.

Edits this child: `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.  
`core/trainer/workbook.py` was not modified.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Audit fill-role repair with `verify_release_pair=True`; saved/reopened current-style Fast Retailing temporary pair **577/577** blank+filled Check, **0** unavailable, `Condensed Financials!B44` Trainer yellow / Answer-Key white; restyled frozen-copy pair under current decorators; focused yellow/invalid-fill/unauthorized-fill/non-fill practice-coordinate failures; frozen yellow exception opt-in only; five-period in-memory admit `2022-01-30` + JSON reload + saved/reopened Lululemon temporary pair; visible-text scan **11** sheets / **3492** cells / **1231** text entries; **15** margin formulas/Notes; geo **74** / preserved **486** / practice **560**; Check blank **560/560** yellow, filled **560/560** green, incorrect **1** red with learner `=999` preserved; `3607682 - 1397067 = 2210615`; whole-workbook Answer-Key no-yellow including CF; focused pytest **429 passed** in **78.46s**; FR tests **144 passed** in **37.26s**; checkpoint `3f6f5dde023847e3347a4c830d822614a28c81a9` **50/50 MATCH** |
| Retained (historical; not re-run) | Analytical-series pytest **144 passed**; `pytest core/tests` **1289 passed**; provenance `selected_geographic_segment_facts` (SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951`, 786300) |
| Not claimed | Excel engine recalculation; parent or Step 9 completion; G6–G9; benchmark publication |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Ratio tolerance: **`GEOGRAPHIC_RATIO_TOLERANCE = 1e-12`**. Monetary tolerance: **`0`**. Reported operating margin basis: `income_from_operations / net_revenue` (not BAV NOPAT margin). Temporary pairs only (`TemporaryDirectory`). xlsx ZIP timestamps make temporary SHA-256 run-specific.

Corrected premature completion: the prior child left `verify_release_pair=False` and identical-fill Answer-Key yellow parity in `scripts/audit_fast_retailing_benchmark.py`. This child repaired those contracts without restyling supplied pairs inside verification.

---

## Task 1 — Repair audit fill rules without weakening verification

Current-generation contract (default): Trainer formula/judgment responses are blank yellow without Notes; Answer-Key counterparts keep formulas/responses and substantive Notes with white/no-fill. Fill comparison is skipped only at validated practice/judgment coordinates. All other formatting, source fidelity, semantic formulas, visibility, layout, non-practice contents and failure reporting remain. Whole-workbook Answer-Key no-yellow includes hidden sheets and conditional highlighting.

Frozen yellow Answer Keys are an explicit opt-in (`allow_frozen_yellow_answer_key=True` / `--allow-frozen-yellow-answer-key`). The exception applies only when Answer-Key practice cells are actually yellow; a current-style (white) pair using the flag fails with `frozen yellow Answer Key exception does not apply to current-style pairs`. Default verification of a frozen yellow Answer Key fails with `Answer Key yellow fill`. Verification never restyles supplied pairs.

---

## Task 2 — Restore full persisted-pair regression coverage

`test_release_audit_explicit_pair_verification` now uses `verify_release_pair=True` on a saved/reopened production-generated Fast Retailing pair. Independent measurement of that path:

| Surface | Measured |
|---|---|
| Practice cells | **577** |
| Unavailable displays | **0** / **0** |
| `Condensed Financials!B44` Trainer | blank, no Note, fill `FFFF00` |
| `Condensed Financials!B44` Answer Key | `='Income Statement'!B21`, Note present, fill `FFFFFF` |
| Accounting Judgment F5 Trainer | blank yellow |
| Accounting Judgment F5 Answer Key | `Financial Asset`, white/no-fill |
| Normalization Judgment | **absent** on Fast Retailing (both modules covered on saved/reopened demo fixture) |
| Contract | `practice_cells=577 source_fidelity=ok visibility=ok layout_parity=ok` |
| Blank Check | correct=0 incorrect=0 blank=577 total=577 |
| Filled Check | correct=577 total=577 |
| Stage 5 | `persisted release pair (not regenerated)` |
| Input fingerprints | unchanged across audit |
| Temporary Trainer | SHA-256 `11870145cdf74ff281cabd7ce47e3dc141b38c22884ad592cad71253132f7d8d` / 38978 bytes |
| Temporary Answer Key | SHA-256 `af983c2b6d46153d9ed208751c0d74e853f2d57f3e321e1cd0eba4b5a3ab1a2c` / 139452 bytes |

Temporary frozen-pair copies restyled with current production `TrainingWorkbookGenerator` decorators, including `Condensed Financials!B44`, pass the same current-style contract and 577-cell Check. Committed release copies remain frozen yellow and are verified only with the narrow frozen exception. Frozen source/visibility/layout/border/theme/hyperlink/corruption tests retained. Focused current-style failures: yellow Answer-Key practice cell, yellow Answer-Key non-practice cell, invalid Trainer practice fill, unauthorized ordinary-cell fill difference, non-fill corruption at `Condensed Financials!B44`. Stage/CLI failure still skips downstream Check after contract failure.

---

## Task 3 — Revalidate geographic acceptance and record evidence

Unchanged extracted filings reconciled in memory with `--admit-period 2022-01-30`, `json.dumps`/`json.loads` reload, then `build_training_workbook` in temporary storage. The matched pair was saved and reopened before inspection.

Visible Trainer inventory (every visible sheet, including Notes/comments and shared instructions):

| Coverage | Measured |
|---|---|
| Visible sheets | **11**: Trainer; Income Statement; Balance Sheet; Cash Flow Statement; Condensed Financials; ALT DuPont; Accounting Judgment; Earnings Quality; Working Capital Analysis; Per Share Analysis; Geographic Segment Analysis |
| Cells scanned | **3492** |
| Visible text entries | **1231** |
| Trainer visible comments/Notes | **0** |
| Geographic A2 | `Source-supported geographic revenue mix, adjacent-period growth, reported operating margins, and consolidated bridges. Reported operating margin is distinct from BAV NOPAT margin.` |
| Geographic A4 | `Calculated segment totals are distinct from any reported segment_total. Sparse unavailable amounts remain unavailable; opening growth is not practiced.` |

Exactly **15** margin identities. Every Trainer counterpart was blank yellow without a Note. Every Answer-Key counterpart was white/no-fill with the same-segment, same-period operating-profit/revenue formula and this Note:

`Reported operating margin = segment income from operations / segment net revenue. This is not BAV NOPAT margin. Zero revenue is undefined (#N/A). Negative profit is preserved.`

| Identity | Cell | Formula |
|---|---|---|
| `geographic_reported_operating_margin__americas__20220130` | `Geographic Segment Analysis!B37` | `=IF(B10=0,NA(),B29/B10)` |
| `geographic_reported_operating_margin__americas__20230129` | `Geographic Segment Analysis!C37` | `=IF(C10=0,NA(),C29/C10)` |
| `geographic_reported_operating_margin__americas__20240128` | `Geographic Segment Analysis!D37` | `=IF(D10=0,NA(),D29/D10)` |
| `geographic_reported_operating_margin__americas__20250202` | `Geographic Segment Analysis!E37` | `=IF(E10=0,NA(),E29/E10)` |
| `geographic_reported_operating_margin__americas__20260201` | `Geographic Segment Analysis!F37` | `=IF(F10=0,NA(),F29/F10)` |
| `geographic_reported_operating_margin__china_mainland__20220130` | `Geographic Segment Analysis!B38` | `=IF(B11=0,NA(),B30/B11)` |
| `geographic_reported_operating_margin__china_mainland__20230129` | `Geographic Segment Analysis!C38` | `=IF(C11=0,NA(),C30/C11)` |
| `geographic_reported_operating_margin__china_mainland__20240128` | `Geographic Segment Analysis!D38` | `=IF(D11=0,NA(),D30/D11)` |
| `geographic_reported_operating_margin__china_mainland__20250202` | `Geographic Segment Analysis!E38` | `=IF(E11=0,NA(),E30/E11)` |
| `geographic_reported_operating_margin__china_mainland__20260201` | `Geographic Segment Analysis!F38` | `=IF(F11=0,NA(),F30/F11)` |
| `geographic_reported_operating_margin__rest_of_world__20220130` | `Geographic Segment Analysis!B39` | `=IF(B12=0,NA(),B31/B12)` |
| `geographic_reported_operating_margin__rest_of_world__20230129` | `Geographic Segment Analysis!C39` | `=IF(C12=0,NA(),C31/C12)` |
| `geographic_reported_operating_margin__rest_of_world__20240128` | `Geographic Segment Analysis!D39` | `=IF(D12=0,NA(),D31/D12)` |
| `geographic_reported_operating_margin__rest_of_world__20250202` | `Geographic Segment Analysis!E39` | `=IF(E12=0,NA(),E31/E12)` |
| `geographic_reported_operating_margin__rest_of_world__20260201` | `Geographic Segment Analysis!F39` | `=IF(F12=0,NA(),F31/F12)` |

All **56** selected on-axis facts equal model values after reload. Independent snapshot arithmetic matched the analytical API for all five periods. All five revenue/IFOP differences **0.0**. FY2026: `3607682 - 1397067 = 2210615`.

| Metric | Value |
|---|---:|
| Existing identities/expectations preserved | **486** |
| Geographic additions | **74** |
| Total practice cells inspected | **560** |
| Unavailable displays | **101** |
| Blank Check | total=560 blank=560 correct=0 incorrect=0 |
| Filled Check | total=560 blank=0 correct=560 incorrect=0; sample fill `C8E6C9` |
| Incorrect Check | total=560 correct=559 incorrect=1 blank=0; learner `=999` retained, fill `FFC7CE`, no Note inserted |
| Answer-Key yellow cells (all sheets, including hidden) | **[]** |
| Conditional-formatting rules | **0** on every inspected sheet |
| Lululemon Accounting Judgment | five cases F5:H9; Answer-Key populated white/no-fill; Trainer blank yellow without Notes |
| Lululemon Normalization Judgment | **absent** (covered on demo pair) |
| Temporary Trainer | SHA-256 `f98d896518fe1ee490d305de66a2f6d2531cc433c9c8a1603084e6c9cb62b1c8` / 37455 bytes |
| Temporary Answer Key | SHA-256 `1b4b6f00b02d8cda1170203efacd9c71a6b923d1be65d2714ae0195bae23f6b4` / 135536 bytes |

Check summaries contained only aggregate counts (no answers, formulas, or hints). Matching Answer Key hashes were unchanged across filled/incorrect Check copies.

---

## Task 3 — Verification commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_analysis.py core/tests/test_historical_segment.py core/tests/test_trainer.py core/tests/test_reference_integrity.py core/tests/test_source_availability.py core/tests/test_learner_ready_presentation.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **429 passed** in **78.46s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_fast_retailing_benchmark.py -q` | 0 | **144 passed** in **37.26s** |
| Independent in-memory reconcile + JSON reload + series vs snapshot arithmetic + saved/reopened temporary pair disclosure/margin/Check/style/no-yellow audit | 0 | 56 selected/model values; five-period independent match; geo **74**; preserved **486**; 15/15 margin Notes; blank 560/560; filled 560/560; incorrect 1; Answer-Key yellow **[]** |
| Independent saved/reopened Fast Retailing current-style pair with `verify_release_pair=True` | 0 | 577 identities; 0 unavailable; blank 577/577; filled 577/577; fingerprints unchanged; B44 role fills |
| Protected artifacts vs checkpoint `3f6f5dde023847e3347a4c830d822614a28c81a9` | 0 | **50/50 MATCH** (git blob SHA-1); committed example Trainer/Answer Key match HEAD |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `scripts/audit_fast_retailing_benchmark.py` | `d6a4b8e72c1cfc5298f7b044e77de81e85ebe3f964e482804a71f4e8b58de1a6` | 63127 |
| `core/tests/test_fast_retailing_benchmark.py` | `6193c3566cbf171355bf3a6c8d7caa44402d223a4e32b03a60bce0ef338fa393` | 115828 |

Unedited product files (hashes measured now):

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/trainer/workbook.py` | `67ef87bf07b477dc2d8b7cdc2e04e60a07b2351e71205f06bdb950130e666cc4` | 16154 |
| `core/engine/component_catalog.py` | `629d0b140be8db6a3ff9a2d5bf05b61aab62fbed896c163788eb1b441f730329` | 186601 |
| `core/engine/reference_model.py` | `30d9465f7c14f9c91f47f6258bb87a70ab8d4a7c3d0820ee81eda70d8669b93d` | 310232 |
| `core/model/historical_expected.py` | `ff8f93a252e1e36580f433c1e3b1319f407d7c1d5ef1481deea3bfc879d53237` | 54281 |
| `core/trainer/checker.py` | `63a662264eea95fe4afcb970bd191ac45efaec166c78502da0cb938ca16e86ff` | 19034 |
| `core/trainer/check_context.py` | `c8fc77fa0a562a7926eb6965158dfd82e2416612cd83f5d5ad7bae53bee093f5` | 25740 |

### Protected-artifact hashes vs checkpoint `3f6f5dde023847e3347a4c830d822614a28c81a9`

All **50** git-tracked paths under `benchmark/lululemon/`, `benchmark/fast_retailing/`, `release/lululemon/`, and `release/fast_retailing/` matched the checkpoint blob SHA-1. Byte identity implies the previously tabulated SHA-256 values are unchanged.

Committed example workbooks match HEAD:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `example/DEMO_HK_Trainer.xlsx` | `dc93f5c1be5e3129f6f2767c313413e82296de53dfd5e5c56ed6d08c8b67b47c` | 26790 |
| `example/DEMO_HK_Answer_Key.xlsx` | `ae6df2406b7a40082d1ea8f73a73f6f6a05c12a7281a5077bda453f71dd98309` | 84370 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining scope

G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; all TARGET Step 9 exit gates. Segment assets/capex, significant-expense schedules and D&A remain outside this step. No parent or Step 9 completion claim.

Committed Fast Retailing Answer Key remains yellow as a frozen historical artifact and is accepted only through the explicit frozen-yellow exception. Fresh and restyled pairs use current white Answer-Key fills.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's admitted-five-period temporary pair **succeeded** (560 cells) and does not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (store KPIs, lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
