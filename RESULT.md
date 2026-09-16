# RESULT.md — Step 9M.2.4.1.1.1.35 Geographic segment workbook schedules and learner/Check integration

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.35 — Geographic segment workbook schedules and learner/Check integration  
**Work:** `65d8d6e9a2f94bb398cace9a2f361b28`  
**Plan:** `3f95227cf3d84dba905fbef9ab1d00fb`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `592023f1a521905a5023ef772d9b8b469884d75f2e3cbbfa4b0adbdcf2676ac4` (11369).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed (Check matched registered Excel formulas; Excel's calculation engine was not invoked).  
This child does **not** declare parent or Step 9 acceptance.

Edits this child: `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `core/tests/test_learner_ready_presentation.py`, `RESULT.md`.  
`core/trainer/workbook.py` was not modified.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Resolved fill detection (RGB / indexed / theme+tint / pattern fg+bg / gradient stops / conditional dxf / referenced dxfId / color-scale) on all sheets including hidden; saved/reopened yellow-encoding rejections with sheet/cell or rule-range diagnostics; white/no-fill and non-yellow controls; frozen compatibility bound to checkpoint SHA-256 pair identities; byte-identical copy accepted; fresh, altered, mixed, and current-style pairs rejected with the flag; default frozen-yellow rejection retained; current-style Fast Retailing temporary pair **577/577** blank+filled Check, **0** unavailable, fingerprints unchanged; focused pytest **462 passed** in **112.05s**; checkpoint `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH** |
| Retained via passing required tests this child | Five-period in-memory admit `2022-01-30` + JSON reload + saved/reopened Lululemon temporary pair; **56** selected facts; `3607682 - 1397067 = 2210615`; geo **74** / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas/Notes; Geographic A2/A4 text; blank/filled/incorrect Check; whole-workbook Answer-Key no-yellow including presentation helper; restyled frozen-copy current-style 577-cell Check |
| Not claimed | Excel engine recalculation; parent or Step 9 completion; G6–G9; benchmark publication |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Ratio tolerance: **`GEOGRAPHIC_RATIO_TOLERANCE = 1e-12`**. Monetary tolerance: **`0`**. Temporary pairs only (`TemporaryDirectory`). xlsx ZIP timestamps make temporary SHA-256 run-specific.

---

## Task 1 — Close yellow-highlight detection gaps

Fill inspection now resolves RGB, indexed palette, and theme/tint through workbook context. Pattern fills inspect both foreground and background regardless of pattern type. Gradient fills inspect every stop. Non-solid fills and unresolved encodings are not treated as white/no-fill.

Conditional rules inspect embedded differential fills, referenced `dxfId` styles, and color-scale colors on every sheet including hidden sheets. Yellow highlighting fails with `sheet=` plus `cell=` or `range=` diagnostics. Non-yellow blue/red/white controls remain accepted.

Current-generation contract: Trainer formula/judgment responses start blank solid yellow (`FFFF00`) without Notes; Answer-Key counterparts keep formulas/responses and Notes with white/no-fill. Fill comparison is skipped only at validated practice/judgment coordinates.

---

## Task 2 — Authenticate historical compatibility

Frozen compatibility is bound to checkpoint-derived SHA-256 identities of **both** historical workbooks as one matched pair. The allowlist is a source constant, not derived from candidate files, filenames, caller assertions, or yellow-cell appearance.

Trusted checkpoint: `3f6f5dde023847e3347a4c830d822614a28c81a9` (identical bytes also at `20d93331bd3c1b3cccd72a3bf5c805453789e189`).

| Member | SHA-256 | Bytes |
|---|---|---:|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |

API/CLI `--allow-frozen-yellow-answer-key` authenticates those bytes before any yellow exemption. Byte-identical temporary copies qualify. Fresh pairs, fresh yellow pairs, mutations of either member, mixed historical/current pairs, and current-style pairs fail with `frozen compatibility pair is not authenticated`. Default verification of the frozen yellow Answer Key still fails with `Answer Key yellow fill`. Verification never restyles supplied inputs.

Source, visibility, layout, border, theme, hyperlink, and non-fill corruption coverage is retained via `_verify_release_pair_contents` (historical yellow skip without rebinding identity). Public contract failures still skip Check through stage/CLI: altered frozen+flag fails authentication; current-style mutated pairs surface source-fidelity errors without the flag.

Independent current-style Fast Retailing saved/reopened temporary pair with `verify_release_pair=True`:

| Surface | Measured |
|---|---|
| Practice cells | **577** |
| Blank Check | correct=0 incorrect=0 blank=577 total=577 |
| Filled Check | correct=577 total=577 |
| Stage 5 | `persisted release pair (not regenerated)` |
| Input fingerprints | unchanged across audit |
| Temporary Trainer | SHA-256 `5fc3f4bf72f8ff3ffaeddb661b68ee890ca211fc71a0e1133f6be1e06a42d382` / 38981 bytes |
| Temporary Answer Key | SHA-256 `638c5a47a4d0b25d7274d0168c84e001d6f2af6e65272b6a9b2365f240322213` / 139455 bytes |

---

## Task 3 — Geographic acceptance and verification commands

Required pytest this child (includes geographic workbook/analysis tests that assert five-period JSON-reloaded Lululemon **56** facts, geo **74**, preserved **486**, practice **560**, unavailable **101**, **15** margin Notes, `3607682 - 1397067 = 2210615`, Check states, and strengthened Answer-Key no-yellow):

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_analysis.py core/tests/test_historical_segment.py core/tests/test_trainer.py core/tests/test_reference_integrity.py core/tests/test_source_availability.py core/tests/test_learner_ready_presentation.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **462 passed** in **112.05s** |
| Independent saved/reopened Fast Retailing current-style pair with `verify_release_pair=True` | 0 | 577 identities; blank 577/577; filled 577/577; fingerprints unchanged |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (git blob SHA-1) |

Geographic A2: `Source-supported geographic revenue mix, adjacent-period growth, reported operating margins, and consolidated bridges. Reported operating margin is distinct from BAV NOPAT margin.`  
Geographic A4: `Calculated segment totals are distinct from any reported segment_total. Sparse unavailable amounts remain unavailable; opening growth is not practiced.`

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `scripts/audit_fast_retailing_benchmark.py` | `f2af3598eeccff0e773b00d560d469cabf2e9b464a284dd9cd101f8074588060` | 70321 |
| `core/tests/test_fast_retailing_benchmark.py` | `ad8d41ac69799a534458b14f2101c8b8c3f237c38ab4d120e2b7857bca7fba70` | 129676 |
| `core/tests/test_learner_ready_presentation.py` | `d8aaca9596c12d3972a94b3e3919cd8bdaf1297764a8e41841bd24046a040ee0` | 16409 |

Unedited product files (hashes measured now):

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/trainer/workbook.py` | `67ef87bf07b477dc2d8b7cdc2e04e60a07b2351e71205f06bdb950130e666cc4` | 16154 |
| `core/engine/component_catalog.py` | `629d0b140be8db6a3ff9a2d5bf05b61aab62fbed896c163788eb1b441f730329` | 186601 |
| `core/engine/reference_model.py` | `30d9465f7c14f9c91f47f6258bb87a70ab8d4a7c3d0820ee81eda70d8669b93d` | 310232 |
| `core/model/historical_expected.py` | `ff8f93a252e1e36580f433c1e3b1319f407d7c1d5ef1481deea3bfc879d53237` | 54281 |
| `core/trainer/checker.py` | `63a662264eea95fe4afcb970bd191ac45efaec166c78502da0cb938ca16e86ff` | 19034 |
| `core/trainer/check_context.py` | `c8fc77fa0a562a7926eb6965158dfd82e2416612cd83f5d5ad7bae53bee093f5` | 25740 |

Committed example workbooks match HEAD:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `example/DEMO_HK_Trainer.xlsx` | `dc93f5c1be5e3129f6f2767c313413e82296de53dfd5e5c56ed6d08c8b67b47c` | 26790 |
| `example/DEMO_HK_Answer_Key.xlsx` | `ae6df2406b7a40082d1ea8f73a73f6f6a05c12a7281a5077bda453f71dd98309` | 84370 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining scope

G6 missing `2021-01-31` BS; G7 store KPIs, lease maturity and remaining note facts; G8 deferral; G9 standalone interest completeness; all TARGET Step 9 exit gates. Segment assets/capex, significant-expense schedules and D&A remain outside this step. No parent or Step 9 completion claim.

Committed Fast Retailing Answer Key remains yellow as a frozen historical artifact and is accepted only through the hash-authenticated frozen exemption. Fresh and restyled pairs use current white Answer-Key fills.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (store KPIs, lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
