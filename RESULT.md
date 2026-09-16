# RESULT.md — Step 9M.2.4.1.1.1.35 Geographic segment workbook schedules and learner/Check integration

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.35 — Geographic segment workbook schedules and learner/Check integration  
**Work:** `65d8d6e9a2f94bb398cace9a2f361b28`  
**Plan:** `038f5e1751ca425794276f95464d4249`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `44882db33a56a3e404f06ee110e5e3cd3b999251618109078ce7497792cedccd` (11694).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed (Check matched registered Excel formulas; Excel's calculation engine was not invoked).  
This child does **not** declare parent or Step 9 acceptance.

Edits this child: `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`.  
`core/trainer/workbook.py` and `core/tests/test_learner_ready_presentation.py` were not modified.

---

## Correction of premature yellow-coverage claims

The prior RESULT for this work claimed COMPLETE after classifying `FFFFCC` / tint `0.8`, while `_rgb_is_yellow` still used `chroma < 0x28`. That cutoff **rejects** pale yellow `FFFFDD` (chroma `0x22`) and `FFFFE0` (chroma `0x1F`), and also `FFFFFE` (chroma `1`). Independent Review required ZIP-byte mutation of those paler tints.

This child removes the chroma cutoff. Classification keeps RGB/ARGB compact-hex normalization, brightness (`red >= 0xC8`, `green >= 0xC0`), and yellow-family hue `[35, 75]`. Achromatic white/gray is `chroma == 0` only. Pale non-white yellow tints, including `FFFFDD` / `FFFFE0` / `FFFFFE` and yellow-theme tints `0.8` / `0.9` / `0.95` / `0.99`, are yellow without an isolated allowlist or another pale-yellow cutoff. Tint `1.0` resolves to `FFFFFF` and is not yellow. White, neutral gray, red, green, blue, and near-white non-yellow hues remain non-yellow at the predicate. The separate minimal-presentation white/no-fill contract is unchanged.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | `_rgb_is_yellow` True for `FFFFCC` / `FFFFDD` / `FFFFE0` / `FFFFFE` and ARGB equivalents, none of those six-hex forms in `YELLOW_RGBS`; `FFFFxx` sweep `00..FE` yellow and `FFFFFF` achromatic; tints `0.8→FFFFCC`, `0.9→FFFFE5`, `0.95→FFFFF2`, `0.99→FFFFFD` yellow after RGB rounding, tint `1.0→FFFFFF` not yellow; independent in-memory ZIP `xl/styles.xml` replace of frozen `00FFFF00` with `00FFFFCC` / `00FFFFDD` / `00FFFFE0` reopens and **rejects** `_verify_answer_key_no_yellow` at `Condensed Financials!B44`; historical-fill replacement of **622** `FFFF00` cells with each pale RGB rejects after in-memory serialize/reopen; saved/reopened RGB/ARGB/tint-0.8/0.9/0.95/0.99 resolved colors at practice B44, ordinary, and hidden cells; pale colors through pattern fg/bg, gradient, embedded/referenced dxf, and color scale; near-white non-yellow controls pass no-yellow; current-style Fast Retailing temporary pair **577/577** blank+filled Check, fingerprints unchanged, not regenerated; required pytest **578 passed** in **183.21s** (previous child **497 passed** in **155.33s**); checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH** (working-tree `git hash-object`) |
| Retained via passing required tests this child | Five-period in-memory admit `2022-01-30` + JSON reload + saved/reopened Lululemon temporary pair; **56** selected facts; `3607682 - 1397067 = 2210615`; geo **74** / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas/Notes; Geographic A2/A4 text; blank/filled/incorrect Check; whole-workbook Answer-Key no-yellow including presentation helper; restyled frozen-copy current-style 577-cell Check; frozen compatibility authentication; byte-identical copy accepted; fresh/altered/mixed/current-style pairs rejected with the flag; default frozen-yellow rejection; indexed/theme/bright-yellow coverage |
| Not claimed | Excel engine recalculation; parent or Step 9 completion; G6–G9; benchmark publication |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Ratio tolerance: **`GEOGRAPHIC_RATIO_TOLERANCE = 1e-12`**. Monetary tolerance: **`0`**. Temporary pairs only (`TemporaryDirectory`). xlsx ZIP timestamps make temporary SHA-256 run-specific. Independent in-memory verification used ZIP `xl/styles.xml` byte replacement plus `_workbook_xlsx_bytes` / `_load_workbook_xlsx_bytes` (no restyle of supplied release inputs).

---

## Task 1 — Repair pale-yellow classification

`_rgb_is_yellow` keeps RGB/ARGB compact-hex normalization. Bright and pale yellow-family fills classify by brightness and hue; zero chroma is achromatic. Known Excel yellows in `YELLOW_RGBS` remain yellow; pale tints are not gated on that list.

Workbook-context RGB/indexed/theme+tint, pattern fg+bg, gradient stops, conditional differential fills including referenced styles, and color-scale coverage on every sheet including hidden sheets are unchanged. Failures still report `sheet=` plus `cell=` or `range=`. Unresolved colors are not treated as white/no-fill.

Current-generation contract: Trainer formula/judgment responses start blank solid yellow (`FFFF00`) without Notes; Answer-Key counterparts keep formulas/responses and Notes with white/no-fill. Fill comparison is skipped only at validated practice/judgment coordinates.

Measured predicate (this child):

| RGB | `_rgb_is_yellow` |
|---|---|
| `FFFF00` / `FFFFCC` / `FFFFDD` / `FFFFE0` / `FFFFFE` / `FFFFFFCC` / `00FFFFDD` / `FFFFFFE0` | True |
| `FFFFFF` / `F2F2F2` / `808080` / `FF0000` / `00FF00` / `0000FF` / `CCCCFF` / `CCFFCC` / `FFCCCC` / `FFFEFE` / `FEFFFE` / `FEFEFF` / `FFFEFF` / `FEFFFF` | False |

Measured tints of `FFFF00`:

| Tint | Resolved | `_rgb_is_yellow` |
|---|---|---|
| `0.8` | `FFFFCC` | True |
| `0.9` | `FFFFE5` | True |
| `0.95` | `FFFFF2` | True |
| `0.99` | `FFFFFD` | True |
| `1.0` | `FFFFFF` | False |

---

## Task 2 — Persisted pale-yellow regressions and controls

Saved/reopened XLSX regressions cover explicit `FFFFCC` / `FFFFDD` / `FFFFE0`, ARGB equivalents, and yellow theme tints `0.8` / `0.9` / `0.95` / `0.99` at practice `Condensed Financials!B44`, ordinary `Income Statement!A6`, and hidden `_Hidden!A1`. After reload, resolved RGB matches the table above and `_verify_answer_key_no_yellow` rejects with `sheet=`/`cell=`. Pale yellow is also exercised through pattern foreground/background, gradient stops, embedded and referenced differential fills, and color scales. Indexed/theme/bright-yellow coverage is retained. Public current-pair contract rejection reaches the yellow audit; contract failures stop stage/CLI before Check.

Review-failure reproduction (independent of workbook mutation helpers; temporary XLSX ZIP `xl/styles.xml` bytes; supplied release bytes unchanged):

| Surface | Measured |
|---|---|
| Historical `FFFF00` cells (openpyxl replacement coverage) | **622** |
| ZIP `00FFFF00` → `00FFFFCC` B44 raw / resolved | `00FFFFCC` / `('FFFFCC', '000000')` |
| ZIP `00FFFF00` → `00FFFFDD` B44 raw / resolved | `00FFFFDD` / `('FFFFDD', '000000')` |
| ZIP `00FFFF00` → `00FFFFE0` B44 raw / resolved | `00FFFFE0` / `('FFFFE0', '000000')` |
| `_verify_answer_key_no_yellow` for each | **REJECT** `Answer Key yellow fill: sheet='Condensed Financials' cell=B44` |
| Source `release/fast_retailing/FastRetailing_Answer_Key.xlsx` after probes | unchanged |

White/no-fill, neutral-gray, red, green, blue, pale non-yellow, and near-white non-yellow (`FFFEFE` / `FEFFFE` / `FEFEFF` / `FFFEFF` / `FEFFFF`) controls pass the no-yellow predicate after save/reopen. Those controls do not relax the separate white/no-fill presentation contract.

Frozen compatibility remains bound to checkpoint SHA-256 identities of **both** historical workbooks. Trusted checkpoint: `3f6f5dde023847e3347a4c830d822614a28c81a9` (identical bytes also at `20d93331bd3c1b3cccd72a3bf5c805453789e189`).

| Member | SHA-256 | Bytes |
|---|---|---:|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |

API/CLI `--allow-frozen-yellow-answer-key` authenticates those bytes before any yellow exemption. Byte-identical temporary copies qualify. Fresh pairs, mutations, mixed historical/current pairs, and current-style pairs fail with `frozen compatibility pair is not authenticated`. Default verification of the frozen yellow Answer Key still fails with `Answer Key yellow fill`. Verification never restyles supplied inputs.

Independent current-style Fast Retailing saved/reopened temporary pair with `verify_release_pair=True`:

| Surface | Measured |
|---|---|
| Practice cells | **577** |
| Blank Check | correct=0 incorrect=0 blank=577 total=577 |
| Filled Check | correct=577 total=577 |
| Stage 5 | `persisted release pair (not regenerated)` |
| Input fingerprints | unchanged across audit |
| Temporary Trainer | SHA-256 `87c278796d67ceb7424705b77cfc629eef44f8f97c94d1ed42ae900598aca770` / 38981 bytes |
| Temporary Answer Key | SHA-256 `8e1b173b258496d0fdffa06a5cbe6d600a81be1902344415f5d88a95513e486b` / 139455 bytes |
| Frozen Trainer/Answer Key `SOURCE_UNAVAILABLE` | **0** / **0** |

---

## Task 3 — Geographic acceptance and verification commands

Required pytest this child (includes geographic workbook/analysis tests that assert five-period JSON-reloaded Lululemon **56** facts, geo **74**, preserved **486**, practice **560**, unavailable **101**, **15** margin Notes, `3607682 - 1397067 = 2210615`, Check states, and strengthened Answer-Key no-yellow, plus pale-yellow regressions):

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_analysis.py core/tests/test_historical_segment.py core/tests/test_trainer.py core/tests/test_reference_integrity.py core/tests/test_source_availability.py core/tests/test_learner_ready_presentation.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **578 passed** in **183.21s** |
| Independent in-memory ZIP FFFFCC/FFFFDD/FFFFE0 rejection and current-style Fast Retailing `verify_release_pair=True` | 0 | ZIP palettes reject at B44; 577 identities; blank 577/577; filled 577/577; fingerprints unchanged |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object`) |

Geographic A2: `Source-supported geographic revenue mix, adjacent-period growth, reported operating margins, and consolidated bridges. Reported operating margin is distinct from BAV NOPAT margin.`  
Geographic A4: `Calculated segment totals are distinct from any reported segment_total. Sparse unavailable amounts remain unavailable; opening growth is not practiced.`

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `scripts/audit_fast_retailing_benchmark.py` | `65b2f2a9e48577682a41f58c48a917c70d404a2260eab3b533af4019194dcf58` | 71493 |
| `core/tests/test_fast_retailing_benchmark.py` | `a79c9bde36eefd7fbf3051d4678a0bb1172abb71be9cebd032911b16a3e574e4` | 142737 |

Unedited product files (hashes measured now):

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/tests/test_learner_ready_presentation.py` | `27468c486cc50ba5f01e3029d1e935b8c7c7ad46d325e38938b2f45db79c037f` | 16032 |
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

Committed Fast Retailing Answer Key remains yellow as a frozen historical artifact and is accepted only through the hash-authenticated frozen exemption. Fresh and restyled pairs use current white Answer-Key fills. Pale `FFFFCC` / `FFFFDD` / `FFFFE0` on a temporary Answer Key is now rejected.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (store KPIs, lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
