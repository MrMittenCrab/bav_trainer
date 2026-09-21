# RESULT.md — Step 4.1.2 Repair centralized Drivers figure spacing

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 4.1.2 — Repair centralized Drivers figure spacing  
**Work:** `e4c434039eb248f3985ef7254930e7be`  
**Plan:** `28482007e0c2496a92d601ac0007296b`  
**Finding:** Publish Lululemon Drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `e42f104e22b753ba957bb2e6c9988d446c49a90c3b3ab987cf8d05973e5566af` (28705).  
SESSION SHA-256 `610809fd496777d99ddbae5931a3d18b4097323c0e92418b7127a4fb3b9c9311` (4170).  
IMPLEMENTATION SHA-256 `10814ec87edafff9af90105873c9261d9f49e280cf6d9dfb0acb993ba9ade697` (6016).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Centralized figure spacing now uses a renderer-measured run of the supported U+0020 from Aptos Regular and DengXian Regular. Session acceptance, forecasting and earlier deferred obligations remain subsequent work.

## Repair

`core/research/style.py` no longer substitutes U+2002. Aptos Regular and DengXian Regular both contain U+0020 and neither contains U+2002; the previous en-space path produced missing-glyph boxes via last-resort. One U+0020 does advance under Agg, but the rasterized gap at figure sizes is below a visible word break (5–8 px at 11 pt / 150 dpi).

`apply_research_style` now measures Agg ink gaps for `Revenue growth`, `store-count growth` and `2 Feb 2025` at 11 pt and 9 pt, then repeats U+0020 until every probe gap is ≥ 0.65 em. This host selected **four** U+0020 (21 / 20 / 23 px at 11 pt; 17 / 16 / 18 px at 9 pt). Last-resort substitution is disabled. `spaced()` still runs on every figure text artist before the shared `savefig`.

Resolved fonts (not vendored): Aptos Regular `/Applications/Microsoft Excel.app/Contents/Resources/DFonts/Aptos.ttf`; DengXian Regular `/Applications/Microsoft Excel.app/Contents/Resources/DFonts/Deng.ttf`. `STYLE.md` SHA unchanged. No font copying or warning suppression.

| N × U+0020 | 11 pt `Revenue growth` | 11 pt `store-count growth` | 9 pt `store-count growth` | Result |
|---|---|---|---|---|
| 1 | 6 px (< 14.9) | 5 px | 4 px | invisible |
| 2 | 11 px | 10 px | 8 px | still tight |
| 3 | 16 px | 15 px | 12 px (< 12.2) | fails 9 pt tight pair |
| 4 | 21 px | 20 px | 16 px | selected |

Calendar wording is unchanged: displayed FY2025 ends 2 February 2025 and is the issuer’s fiscal 2024 53-week year; displayed FY2024 ends 28 January 2024.

## Per-figure visual inspection (4×–6× readable crops)

Inspected regenerated `build/lululemon/figures/drivers/{growth,geography,margin}.png` at 1125×720 and enlarged title, legend, y-label, tick and source-note bands.

| Figure | Titles / legends / notes | Ticks | Defects |
|---|---|---|---|
| growth | Word-separated; no tofu | `2 Feb 2025`, `28 Jan 2024` readable at 6× | None. No clip, overlap, or missing-glyph boxes |
| geography | `China Mainland`, `Rest of World`, source note spaced | Same fiscal dates | None |
| margin | `Reported operating margin`, `Operating margin`, source note spaced | FY2022–FY2026 including `2 Feb 2025` | None |

Figures are reusable without manual cleanup. Chart data, labels, source notes, relative Markdown links and grayscale presentation are unchanged.

## Verification

| Check | Measured result |
|---|---|
| Focused rendering regression `test_figure_word_spacing_uses_required_fonts_and_visible_gaps` | **1 passed** — Aptos/DengXian files; U+2002 absent from both cmaps; no `missing from font` / Glyph warnings on shared `finish_figure` save; native one-space gap below threshold; spaced title/note ink gaps above 0.65 em |
| Calendar regression `test_drivers_calendar_limitation_reconciles_53_week_year` | **1 passed** — FY2025 / 2 February 2025 / fiscal 2024; FY2024 is 28 January 2024 |
| `test_research_drivers` | **7 passed** |
| `test_current_build` + `test_build_cli` + `test_build_contract` + `test_revenue_driver` + `test_protected_artifacts_and_eight_extracts_unchanged` | **87 passed**; **50/50** protected and **8/8** extracts |
| Two builds, unchanged inputs | Markdown, placeholders and all three PNGs byte-identical. Workbook zip 227421 vs 227420; analytical cells formula **0**, literal **0** |
| vs pre-rebuild BAV `bcacf70d…` (228421) | Formula **0**, literal **0** |
| vs `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | Formula **0**. Literal/structure diffs confined to Overview (2 changed + 2 only-left + 48 only-right = 52 previously recorded). Native recalc not required |
| vs checkpoint `51468d6872d6cc6bfebbe780664003171bcb105c` `release/lululemon/Lululemon_Answer_Key.xlsx` | Historical product gap, not this repair: ckpt has Trainer / no later KPI-driver sheets; shared cells formula **61**, literal **802**; only-ckpt 679 (Trainer 668); only-cur 8690. This step added none versus last published BAV |
| Fast Retailing BAV | Unchanged SHA-256 `4b308474…` (135552) |
| `python -m bav build Lululemon` (twice) | Research + figures published; Forecast/Valuation/Overview remain 0 bytes; Drivers SHA unchanged `9923e74f…` |
| Learner-ready + export-reload + management-KPI + Trainer + reference + Fast Retailing suites | Carried forward from Step 4.1.1 (unchanged analytical surfaces; workbook formulas/literals identical to last published BAV) |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected PDFs, extracts and authenticated baselines were not replaced. Workbook presentation was not changed; native Excel carry-forward remains applicable.

## Session conditions (measured, not acceptance)

1. STYLE.md sole standard — yes; SHA unchanged.  
2. README architecture / module order / STYLE authority — yes; unchanged.  
3–4. Four research files; Forecast/Valuation/Overview 0 bytes — yes.  
5. Drivers structure and prose — yes; calendar Limit still names FY2025 / 2 February 2025.  
6. Three Matplotlib figures, centralized style, reusable without cleanup — yes after this spacing repair; 4×/6× inspection found normal word separation and no tofu.  
7. Five-minute understanding — yes, as read.  
8. Workbook still traces calculations; numbers from same inputs — yes; analytical cells identical to pre-rebuild.  
9. No analytical control weakened — formula/literal 0 vs last published BAV.  
10. Focused rendering + calendar + build/protected checks passed; native evidence carried forward.  
11. No buyer/M&A/Forecast/Valuation/Overview analysis in Drivers — yes.

## Artifact hashes

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/lululemon/Lululemon_BAV.xlsx` | `2507ef35930fd4be42a69ac6bef059d97e58fa1ad4a28ee4b866086c4d237bc0` | 227420 |
| `build/lululemon/research/Lululemon_Drivers.md` | `9923e74f58b034997dacac98b3def8dfaadc9b35a3cdee7e1ce2789db94cafe0` | 3853 |
| `build/lululemon/research/Lululemon_Forecast.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/research/Lululemon_Valuation.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/research/Lululemon_Overview.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/figures/drivers/growth.png` | `82bd14146ad776041fa868a0491cbf172f9321d3bbb34143591557a10db2c372` | 63775 |
| `build/lululemon/figures/drivers/geography.png` | `a57ebcb7474b9ae14ec4263f3c9c003ab2d74c843f165adf5482c14bd4d81c6a` | 51721 |
| `build/lululemon/figures/drivers/margin.png` | `4c2ad01b7564e684dddf6d119bbcd60e9b481b7b33e1052e1bdc2c26c33e63e6` | 61408 |
| `build/fast_retailing/FastRetailing_BAV.xlsx` | `4b308474353a3303548f9daaa41ee9124fd7d56bddd189e25611e5e6d32b1eb8` | 135552 |
| `STYLE.md` | `4360b24bb849370a0fa48f21aa7cc83b8bf6b35c2ad9bac7e10de2829a107fc6` | 1645 |
| `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` | 260706 |

## Native Excel carry-forward

Formulas, literal inputs and transitive dependencies on analytical surfaces match the last published BAV by cell identity. The older saved snapshot still differs only on already-accepted Overview narrative (52 literals). Native recalculation and new screenshots were not required.

Retained: `.git/autocycle/excel-verification-fb95_r2m/`, `excel-verification-7vjhjujd/`, `excel-verification-kd2d78ng/`, `excel-verification-ti974vnt/`, `excel-verification-kzg9a_ex/`, `revenue-driver-render-3-3-1/`, `overview-synthesis-3-4/`.

## Remaining toward Completion

This bounded work repairs centralized figure word spacing and regenerates the three Drivers PNGs. Publication and this repair are not Session acceptance. Review still judges professional figure presentation against all eleven conditions. Forecasting, valuation, Overview content, and earlier deferred normalization / source-workflow / normalized-per-share obligations remain open.

---

# RESULT.md — Step 4.1.1 Reconcile Drivers calendar limitation

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 4.1.1 — Reconcile Drivers calendar limitation  
**Work:** `e4c434039eb248f3985ef7254930e7be`  
**Plan:** `95525118e4a74878a28d7bf14daaf9ed`  
**Finding:** Publish Lululemon Drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `e42f104e22b753ba957bb2e6c9988d446c49a90c3b3ab987cf8d05973e5566af` (28705).  
SESSION SHA-256 `610809fd496777d99ddbae5931a3d18b4097323c0e92418b7127a4fb3b9c9311` (4170).  
IMPLEMENTATION SHA-256 `540aa40c92a93d86e65ac5fbad28a03261add628f0c141c982f99064b191c27a` (5832).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. The ordinary Lululemon build now resolves the Drivers calendar limitation from source calendar metadata and the same period mapping used by the table and figures. Session acceptance, forecasting and earlier deferred obligations remain subsequent work.

## Correction

`core/research/drivers.py` no longer hardcodes “FY2024 is a 53-week year.” It identifies the unique admitted extra-week period (`calendar_week_adjustment == excluded`) on the canonical axis, then writes the displayed label from `_label_for` / `financials.periods`.

| Identity | Source | Output |
|---|---|---|
| 53-week period-end | Protected extract `LULU_FY2024_management_kpis.json` `report.fiscal_year_end`; PDF inspection `2024 in fifty_three_week_years` | **2 February 2025** |
| Issuer naming | Extract `report.fiscal_year == 2024`; original reporting basis “FY2024 contains 53 weeks.” | **fiscal 2024** |
| Displayed label | Same mapping as the table and figures (`FY{end_date.year}`) | **FY2025** |
| Displayed FY2024 | Period ended **28 January 2024** | 52-week / `included`; does not receive the 53-week claim |

Issuer naming is distinguished from the output label using existing `calendar_reporting_basis` (“Sunday closest to January 31 of the following year”). The analytical period axis is unchanged.

Extra-week wording checked against source locators and retained once: FY2024 extract / FY2024 10-K comparable-sales definition excludes the 53rd week; FY2025 extract realigns the prior-year window (“shifted by one week”). Regenerated Limits sentence:

> FY2025, the year ended 2 February 2025, is a 53-week year; the issuer names it fiscal 2024. Some later comparable-sales presentations exclude or realign that extra week and cannot be joined to the earlier observations.

Numerical table, figure labels/captions, units, rounding, geographic contribution sums and the other three Limits are unchanged.

## Verification

| Check | Measured result |
|---|---|
| Focused calendar regression `test_drivers_calendar_limitation_reconciles_53_week_year` | **1 passed** — source 53-week period, issuer fiscal 2024, displayed FY2025, 2 February 2025 reconciled; “FY2024 is a 53-week” absent |
| Regenerated Drivers vs source metadata | Calendar sentence uses FY2025 / 2 February 2025 / fiscal 2024. Table: FY2024 \| 28 January 2024; FY2025 \| 2 February 2025. Headings exact. Five conclusions. |
| `test_research_drivers` | **6 passed** |
| `test_current_build` + `test_build_cli` + `test_build_contract` + `test_revenue_driver` + protected artifacts/extracts | **87 passed**; **50/50** protected and **8/8** extracts |
| Learner-ready + export-reload + management-KPI history | **1081 passed** |
| Trainer + reference integrity + Fast Retailing | **418 passed** |
| Two builds, unchanged inputs | Markdown, placeholders and all three PNGs byte-identical. Workbook zip 228423 vs 228421; analytical cells formula **0**, literal **0** |
| vs pre-rebuild BAV `7fa3c9fd…` | Formula **0**, literal **0** |
| vs `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | Formula **0**. Literal **52**, all Overview (already recorded; not new). Native recalc not required |
| Fast Retailing BAV | Unchanged SHA-256 `4b308474…` (135552) |
| STYLE / fonts / centralized figures | STYLE SHA unchanged. Aptos / DengXian still resolved. Figure code untouched; two-build PNG hashes identical |
| `python -m bav build Lululemon` (twice) | Research + figures published; Forecast/Valuation/Overview remain 0 bytes |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected PDFs, extracts and authenticated baselines were not replaced. Native Excel carry-forward remains applicable; workbook presentation was not changed.

## Session conditions (measured, not acceptance)

1. STYLE.md sole standard — yes; unchanged.  
2. README architecture / module order / STYLE authority — yes; unchanged.  
3–4. Four research files; Forecast/Valuation/Overview 0 bytes — yes.  
5. Drivers structure and prose — yes; calendar Limit now names FY2025 / 2 February 2025.  
6. Three Matplotlib figures, centralized style — yes; two-build identical.  
7. Five-minute understanding — yes, as read; 53-week year is the displayed FY2025 period.  
8. Workbook still traces calculations; numbers from same inputs — yes; analytical cells identical to pre-rebuild.  
9. No analytical control weakened — formula/literal 0 vs last published BAV.  
10. Focused checks passed; native evidence carried forward.  
11. No buyer/M&A/Forecast/Valuation/Overview analysis in Drivers — yes.

## Artifact hashes

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/lululemon/Lululemon_BAV.xlsx` | `bcacf70d41492771545d37a426276a59e88f7eef21c47ead9aa9d46ba3596e79` | 228421 |
| `build/lululemon/research/Lululemon_Drivers.md` | `9923e74f58b034997dacac98b3def8dfaadc9b35a3cdee7e1ce2789db94cafe0` | 3853 |
| `build/lululemon/research/Lululemon_Forecast.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/research/Lululemon_Valuation.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/research/Lululemon_Overview.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/figures/drivers/growth.png` | `5488ca7bfecf0899e6330c621b56aff01e299e7697acf34305ddb29e9128abde` | 71293 |
| `build/lululemon/figures/drivers/geography.png` | `4fc599c74c618bf4eed27f2b9d28efc3eb1965d92612fe538d1340858dfe3e3b` | 56412 |
| `build/lululemon/figures/drivers/margin.png` | `146839561c0da23beb21fc3ab5abd9ea9a36f8c3b00e1a51adbb103554799dc7` | 65213 |
| `build/fast_retailing/FastRetailing_BAV.xlsx` | `4b308474353a3303548f9daaa41ee9124fd7d56bddd189e25611e5e6d32b1eb8` | 135552 |
| `STYLE.md` | `4360b24bb849370a0fa48f21aa7cc83b8bf6b35c2ad9bac7e10de2829a107fc6` | 1645 |
| `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` | 260706 |

## Native Excel carry-forward

Formulas, literal inputs and transitive dependencies on analytical surfaces match the last published BAV by cell identity. The older saved snapshot still differs only on already-accepted Overview narrative (52 literals). Native recalculation and new screenshots were not required.

Retained: `.git/autocycle/excel-verification-fb95_r2m/`, `excel-verification-7vjhjujd/`, `excel-verification-kd2d78ng/`, `excel-verification-ti974vnt/`, `excel-verification-kzg9a_ex/`, `revenue-driver-render-3-3-1/`, `overview-synthesis-3-4/`.

## Remaining toward Completion

This bounded work corrects the Drivers calendar limitation and regenerates the module. Publication and this repair are not Session acceptance. Forecasting, valuation, Overview content, and earlier deferred normalization / source-workflow / normalized-per-share obligations remain open.

---

# RESULT.md — Step 4.1 Publish Lululemon Drivers

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 4.1 — Publish Lululemon Drivers  
**Work:** `e4c434039eb248f3985ef7254930e7be`  
**Plan:** `d8a7307b658f4b27b9c88481416820b2`  
**Finding:** Publish Lululemon Drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `e42f104e22b753ba957bb2e6c9988d446c49a90c3b3ab987cf8d05973e5566af` (28705).  
SESSION SHA-256 `610809fd496777d99ddbae5931a3d18b4097323c0e92418b7127a4fb3b9c9311` (4170).  
IMPLEMENTATION SHA-256 `95b342954453504aacab4afd6b51372cad742e539747cc30c483326a121c19e8` (9269).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Ordinary `python -m bav build Lululemon` now publishes the workbook / research / figures architecture at `build/lululemon/`. Forecast, Valuation and Overview remain zero-byte. Session acceptance, forecasting and earlier deferred obligations remain subsequent work.

## Publication

Company output moved from `build/output/<Name>/` to `build/<slug>/`. Ordinary Lululemon writes `build/lululemon/Lululemon_BAV.xlsx`, `research/Lululemon_Drivers.md`, empty reserved modules, and `figures/drivers/{growth,geography,margin}.png`. Fast Retailing writes `build/fast_retailing/FastRetailing_BAV.xlsx` and does not publish research. Supporting artifacts, formula links, derivative Trainer paths and atomic replacement are unchanged except for that directory.

Root `STYLE.md` is the sole presentation and language specification. One Matplotlib implementation in `core/research/style.py` applies it. Figures do not set independent typography, spacing or palettes. Accent is optional and off by default; accent-enabled generation produced identical PNGs because no series used the highlight role.

Resolved fonts (not vendored): Aptos Regular `/Applications/Microsoft Excel.app/Contents/Resources/DFonts/Aptos.ttf`; DengXian Regular `/Applications/Microsoft Excel.app/Contents/Resources/DFonts/Deng.ttf`. Aptos ASCII space does not advance under the Agg renderer; figures use the same face's en space (U+2002). That is not a family substitution. Required faces were present; none were reported unavailable.

Drivers headings are exactly `# Lululemon — Drivers` then Context, Growth, Geography, Margin, Conclusions, Limits. Five conclusions. Four Limits, each once. No Forecast, Valuation, Overview, buyer or M&A analysis. Relative figure links: `../figures/drivers/{growth,geography,margin}.png`.

## Claim / source mappings

All research numbers come from the same compute path as the workbook (`prepare_company_input` → existing BAV series). Independent anchors reconcile.

| Claim | Source series | Independent check |
|---|---|---|
| Revenue $6,256.6 / 8,110.5 / 9,619.3 / 10,588.1 / 11,102.6 million | IS `revenue` (USD thousands / 1000) | `REVENUE_ANCHORS` 6256617 … 11102600 |
| Operating profit $1,333.4 … $2,210.6 million | IS `operating_income` / 1000 | 1333355 … 2210615 |
| Operating margin 21.3 / 16.4 / 22.2 / 23.7 / 19.9% | `compute_reported_margin_series` | 2210615/11102600 = 19.91% → 19.9% |
| Stores 574 / 655 / 711 / 767 / 811 | `compute_operating_kpi_series` | `INDEPENDENT_STORE_TOTALS` |
| Revenue growth 29.63 / 18.60 / 10.07 / 4.86% | store-revenue relationship | (8110518−6256617)/6256617 = 29.63% |
| Store growth 14.11 / 8.55 / 7.88 / 5.74% | same | (811−767)/767 = 5.74% |
| FY2026 store > revenue (−0.878 pp) | same | 5.74 − 4.86 = 0.88 pp |
| Compsales 25% FY2023 stores+DTC; 13/4/2% later stores+e-comm; 16% store-only | driver analysis + management KPI series | reported global identities; not one series |
| Geo pp FY2026 Americas −0.766, China 3.716, RoW 1.909 | `revenue_growth_contribution` | sum = 4.859 vs 4.86% growth; residuals ~0 |
| Geo sums all four growth years | same | \|Σ contrib − 100×growth\| < 1e-9 |

Plotted values are the same floats. Display rounding: millions 1 decimal, growth 2 decimals, contributions 3 decimals.

## Verification

| Check | Measured result |
|---|---|
| Required paths, 0-byte placeholders, exact headings, 3 PNGs, relative links | Pass |
| Fonts actually resolved to Aptos / DengXian Regular files | Pass; ASCII space workaround recorded |
| Centralized style; accent-disabled default | Pass; accent-on hashes identical to accent-off |
| Internal BAV terminology scan of Drivers | None of admitted / fail-closed / SOURCE_UNAVAILABLE / hypothesis / verdict / audit-only |
| Five-minute read | Revenue slowed 29.63→4.86%; stores 574→811; FY2026 store>revenue; Americas −0.766 pp; OM 16.4→23.7→19.9%; compsales not one series |
| Two builds, unchanged inputs | Markdown, placeholders and all three PNGs byte-identical. Workbook zip bytes 227423 vs 227421; analytical cells vs prior `build/output/Lululemon` BAV: formula 0, literal 0 |
| `test_research_drivers` + `test_current_build` + `test_build_cli` + `test_build_contract` | **73 passed** |
| `test_revenue_driver` + generic-engine + research retest | **25 passed** |
| Trainer, learner-ready, protected artifacts, Fast Retailing, reference integrity | **426 passed** including **50/50** protected and **8/8** extracts |
| Lululemon + geographic/KPI workbook + revenue-driver suites (prior batch) | **581 passed** after removing issuer literals from production research modules |
| Ordinary `python -m bav build Lululemon` | Active including Revenue Driver Analysis; research+figures published |
| Ordinary `python -m bav build FastRetailing` | No research directory; driver families unavailable |
| Trainer derivation from final BAV | BAV bytes unchanged. 37 source facts; 824 blank yellow; Check **0 / 0 / 824 / 824** |
| Formula/literal vs `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | Formula changed **0**. Non-Overview literal changed **0**. Overview already differed from that older snapshot (Step 3.4). Native recalc not required |
| vs last accepted BAV `5bb6537b…` | Formula **0**, literal **0**, only xlsx container metadata |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected PDFs, extracts and authenticated baselines were not replaced.

## Session conditions (measured, not acceptance)

1. STYLE.md sole standard — yes.  
2. README architecture / module order / STYLE authority, no style-rule copy — yes.  
3–4. Four research files; Forecast/Valuation/Overview 0 bytes — yes.  
5. Drivers structure and prose — yes.  
6. Three Matplotlib figures, centralized style — yes.  
7. Five-minute understanding — yes, as read.  
8. Workbook still traces calculations; numbers from same inputs — yes.  
9. No analytical control weakened — workbook cells identical to last accepted BAV.  
10. Focused checks passed; native evidence carried forward.  
11. No buyer/M&A/Forecast/Valuation/Overview analysis in Drivers — yes.

## Artifact hashes

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/lululemon/Lululemon_BAV.xlsx` | `7fa3c9fdc52e5c78fbc9c646dca9df4454533cabbf6852d7265dd0d684a358bd` | 227421 |
| `build/lululemon/research/Lululemon_Drivers.md` | `bfd1b0cb8a26f0feac1a37dfd75439298342f19bc8dfc42dc2573548cec19d4f` | 3787 |
| `build/lululemon/research/Lululemon_Forecast.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/research/Lululemon_Valuation.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/research/Lululemon_Overview.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `build/lululemon/figures/drivers/growth.png` | `76d4e28f7dbf7aea4ea2f8e67fc6aa0de1617e8b873bc60c5bbf5348ec12c16b` | 65406 |
| `build/lululemon/figures/drivers/geography.png` | `5ad8e6d2eab2a503b6917fa0350083775a7c0a4ba8fd59217b576a98adeb6432` | 53598 |
| `build/lululemon/figures/drivers/margin.png` | `4a9a206f21e46720c192df1a06406f0c86264216ebbf5f34c3258b579d1da9c4` | 62091 |
| `build/lululemon/Lululemon_BAV_Trainer.xlsx` (derived) | `866b24521bb4f9b3a88b8f4ab4894942beed9cc837fc9f414d223c7d4ed69fb3` | 66616 |
| `build/fast_retailing/FastRetailing_BAV.xlsx` | `4b308474353a3303548f9daaa41ee9124fd7d56bddd189e25611e5e6d32b1eb8` | 135552 |
| `STYLE.md` | `4360b24bb849370a0fa48f21aa7cc83b8bf6b35c2ad9bac7e10de2829a107fc6` | 1645 |
| `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` | 260706 |

After blank Check the Trainer file was 66998 / `89ed00b1749410053bc3ae685a20586a6b7f5df90c3b1dab0afe484771e05def`. BAV bytes were not rewritten.

## Native Excel carry-forward

Formulas, literal inputs and transitive dependencies on analytical surfaces match the last accepted BAV by cell identity. The older saved snapshot still differs only on already-accepted Overview narrative. Native recalculation and new screenshots were not required.

Retained: `.git/autocycle/excel-verification-fb95_r2m/`, `excel-verification-7vjhjujd/`, `excel-verification-kd2d78ng/`, `excel-verification-ti974vnt/`, `excel-verification-kzg9a_ex/`, `revenue-driver-render-3-3-1/`, `overview-synthesis-3-4/`.

## Remaining toward Completion

This bounded work publishes Drivers, STYLE, empty reserved modules and three figures. Publication is not Session acceptance. Forecasting, valuation, Overview content, and earlier deferred normalization / source-workflow / normalized-per-share obligations remain open.

---

# RESULT.md — Step 3.4 Connect historical revenue findings to disclosed strategy

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.4 — Connect historical revenue findings to disclosed strategy  
**Work:** `a0711a837cc54312a8ab84b424f945bb`  
**Plan:** `f50d0be82bde4cefbe1f97c59d6327a1`  
**Finding:** Connect historical revenue findings to disclosed strategy  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `bf053b273c2926814a5c3b14e71adb23c66dc6c8985fdbbeb30922bfe03f5b6e` (6635).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Ordinary Lululemon BAV Overview is now a source-backed historical reading that connects the four accepted driver findings to management-disclosed strategy, with locators, counterexamples and explicit limits. Session Endpoint, forecasting and earlier deferred obligations remain subsequent work.

## Synthesis published on Overview

Ordinary `python -m bav build Lululemon` remains Active for Revenue Driver Analysis and the supporting KPI / geographic schedules. Fast Retailing still has no strategy payload; Overview uses the generic professional fallback and the driver sheet stays absent.

Generic module `core/model/revenue_strategy_synthesis.py` consumes admitted `compute_revenue_driver_analysis` results and source-bound disclosures. Issuer statements stay in company inputs. Protected `benchmark/lululemon/reconciled/standardized.json` still has no `historical_strategy`. Disclosure fixture unchanged SHA-256 `8da4536a21d6874ddedfaea06cb4e3b948f11b23a33d8f55b1f24c850157d845`.

| Theme | Management statement / locator | Historical finding / schedule | Analyst inference / qualification |
|---|---|---|---|
| Store expansion | FY2022 10-K p.32 strategy; FY2024 10-K p.3 strategy; FY2024 p.3 objective as locator only | Supported descriptively; 4 aligned periods; 2026-02-01 store 5.74% exceeded revenue 4.86% (−0.878 pp); period-end RPS declined. See Revenue Driver / Store Count / Revenue per Store. | Coincident descriptor, not new-store contribution, organic growth or causal evidence. Objective is a plan, not an achieved outcome. |
| Comparable sales | FY2022 10-K p.31 and p.32 operating use; FY2024 10-K p.33 operating use | Supported descriptively; 4 identity-period observations. See Revenue Driver and Comparable Sales Analysis. | Descriptive only. Reported vs constant-currency remain separate. Historical comparable-sales comparison remains ineligible. |
| Store productivity | FY2022 10-K p.3 operating use; FY2024 10-K p.34 operating use | Insufficiently evidenced; sample 0; adjacent SPSF unavailable. RPS rose in 3 periods and declined in 1 as identity only. | Disclosure remains a statement, not a demonstrated outcome. Total-company revenue / stores is not independent productivity evidence. |
| Geographic expansion | FY2022 10-K p.24 Power of Three ×2; FY2024 10-K p.3 China Mainland | Mixed; 4 periods / 3 identities. 2026-02-01 revenue 4.86%; Americas −0.766 pp; China Mainland 3.716 pp; Rest of World 1.909 pp. See Revenue Driver and Geographic Segment Analysis. | Arithmetic decomposition of reported revenue, not organic, constant-currency or causal growth. |

Combined reading: store expansion and comparable sales are descriptively consistent; geographic mix is mixed; productivity cannot be treated as a demonstrated driver; latest-period store and geographic counterexamples prevent lockstep or uniformly positive readings. History does not establish causal drivers, comprehensive strategy execution, or untested initiatives.

Productivity gap links to the complete deferred 2023-01-29 SPSF disagreement on Revenue Driver Analysis without copying member locators or definition texts onto Overview. Untested initiatives remain untested. Supporting-schedule hyperlinks retained.

Preserved: four hypotheses/verdicts/sample sizes/counterexamples; 24 CompSales facts; 3 SPSF levels; 5 RPS periods; 39 pair assessments; five supported historical SPSF comparisons; admission/comparison independence; FY2022 store-only vs later stores-plus-DTC; 2023-01-29 disagreement audit-only; FY2024 exclusion/calendar failures; `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

## Verification

| Check | Measured result |
|---|---|
| `python -m pytest core/tests/test_revenue_driver.py` | **18 passed** (prior 15 retained; added synthesis, deferred-SPSF link-without-promotion, professional fallback, Overview assertions) |
| `test_current_build` + `test_build_cli` + `test_build_contract` + `test_protected_artifacts_and_eight_extracts_unchanged` | **69 passed** including **50/50** protected artifacts and **8/8** extracts |
| Lululemon + Fast Retailing + Trainer + learner-ready | **394 passed** |
| operating KPI workbook + geographic workbook + management KPI history + revenue driver | **120 passed** |
| Ordinary `python -m bav build Lululemon` | Active for driver / CompSales / SPSF / RPS / geographic. Overview has synthesis; 0 yellow; no exercise framing. |
| Trainer derivation from final BAV | BAV bytes unchanged. 37 source facts populated; 824 blank yellow practices; pristine Check **0 / 0 / 824 / 824**. |
| Formula/literal compare vs `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | Overview narrative **52** cells changed (intended). Formula changed **0**. Non-Overview literal changed **0**. Native recalculation not required. |
| Native Overview screenshots | Granted overlapping views at 100% zoom inspected; no clipping/truncation demonstrated. AutoRecover banner present, not dismissed. |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected PDFs, extracts and authenticated baselines were not replaced.

## Artifact hashes

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/output/Lululemon/Lululemon_BAV.xlsx` | `5bb6537b6cf32556b4382c51b18a1a2ca013ec85e804b91803e1fece7bc4b2a3` | 228422 |
| `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` | `2dd85f089755242951b7cd7f046080e1ac7c6c5bcee69fd89e43b53701d8ce52` | 66642 |
| `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` | 260706 |
| granted working copy (in-place update of same source-path copy) | `5bb6537b6cf32556b4382c51b18a1a2ca013ec85e804b91803e1fece7bc4b2a3` | 228422 |
| `core/tests/fixtures/strategy/lululemon_management_disclosures.json` | `8da4536a21d6874ddedfaea06cb4e3b948f11b23a33d8f55b1f24c850157d845` | 4255 |

## Native Excel carry-forward

Formulas, literal inputs and transitive dependencies on unchanged analytical surfaces match the immutable saved snapshot by identity. Accepted 37-reference / 103-cell VERIFIED evidence is carried forward without recalculation.

Retained: `.git/autocycle/revenue-driver-render-3-3-1/`, `excel-verification-fb95_r2m/`, `excel-verification-7vjhjujd/`, `excel-verification-kd2d78ng/`, `excel-verification-ti974vnt/`, `excel-verification-kzg9a_ex/`.

New visual evidence: `.git/autocycle/overview-synthesis-3-4/` (`inspection.json`, `capture-granted-log.txt`, `capture-granted-hashes.sha256`, 8 PNGs under `captures-granted/`). First ungranted-folder captures under `captures/` show Chrome plus a folder-access dialog and are not readability evidence; that dialog was not clicked.

## Remaining toward Completion

This bounded work publishes the Overview synthesis connecting verified findings to disclosed strategy. It does not close the Session Endpoint, forecasting, valuation, or earlier deferred normalization / source-workflow / normalized-per-share obligations.

---

# RESULT.md — Step 3.3.1 Finish revenue-driver presentation and verification

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.3.1 — Finish revenue-driver presentation and verification  
**Work:** `8a8f7457f9524a6997e0ec2fbbe5ac23`  
**Plan:** `8aa00f2d3d2749d5a2f4ab39f2f3eec0`  
**Finding:** Test disclosure-led historical revenue drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `222af3e06a7083bce757747728e63de4bda63789db3acbdfacf5fad744a3d98a` (8325).  
No commit / push / sync / checkpoint / branch change. No BAV regeneration. No layout edit.

## Required plan change

No required plan change. Native `screencapture -x` inspection of all four Revenue Driver Analysis hypotheses on the authorized working copy found no demonstrated clipping, truncation, overlap, or unreadable scaling. Broader strategy synthesis and Session Endpoint closure remain subsequent work.

## Native screenshot inspection (this attempt)

Carried forward Screen Recording recovery: `.git/autocycle/implement-render-fix-20260920/SCREEN-RECORDING.md` and `screen-test.png` SHA-256 `12e93d5d0f4674a14a5670a591a329ce45d4956762db38245227ccf6ec431091`.

Started from accepted BAV SHA-256 `f0f46a03f4c2091f8d9a1d3002b37bcda2bd46c6851389d9ebc4171cbf4f1a0c` (224649). Operated only on the already-authorized native Excel working copy `.git/autocycle/excel-workbooks/5dc9d0038b5f6b7cfbc50b3c/autocycle-verification-5dc9d0038b5f6b7cfbc50b3c.xlsx` SHA-256 `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae`. Immutable saved snapshot `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` was not overwritten (same hash). Prior `attempt-20260920-1818-diagnostics.json` SHA-256 `8d43da333a8a03fd0e5430b15ea4ded5581e5faf5ddd6a12b4d83be7b68c2554` retained.

Capture method: activate Microsoft Excel, `goto` a range on `Revenue Driver Analysis`, 100% zoom, window bounds `{0,39,1710,1112}`, overlapping `scroll row`/`scroll column`, then direct `/usr/sbin/screencapture -x`. PDF/CopyPicture/print-area paths were not repeated. AutoRecover banner "Open recovered workbooks?" was present; it was not dismissed. `set active sheet` failed `-10006` while that banner was up; `goto` switched the visible sheet without clicking the banner. Source and granted-copy hashes were unchanged after close-without-save.

New evidence (does not overwrite 1818 files): `.git/autocycle/revenue-driver-render-3-3-1/attempt-20260920-1938/` including `inspection.json`, `rda-capture-log.txt`, `capture-hashes.sha256`, and 44 PNGs under `captures/`.

| Required cell | Inspected screenshot | SHA-256 | Visual finding |
|---|---|---|---|
| A5 | `rda-01-header-a5.png` | `b68a141ad97f822bb4fdaf71b4b90edd226316d97b64581369a1947fb34b129d` | Merged wrapped scope note fully readable: management statements vs outcomes; descriptive differences not causal; revenue/stores identity; reported vs constant-currency / fiscal labels kept distinct. |
| B12 | `rda-01-header-a5.png` | same | Store disclosure + `LULU_FY2022_Annual_Report.pdf`; Form 10-K p. 32; Item 7; period-end 2023-01-29. B13/B14 locators also visible. |
| B15 | `rda-01-header-a5.png` | same | Finding complete: 4 aligned periods; supported descriptively; 2026-02-01 store-count growth 5.74% exceeded revenue 4.86% (−0.878 pp); Revenue per Store declined as identity, not productivity proof. |
| B18 | `rda-01-header-a5.png` / `rda-03-store-b18.png` | `450d1af5b374b07b8c4343dba20e624620f272d37dc47059d93417e55f3a8b22` | Limitations fully wrapped: distinct scopes; not new-store contribution/organic/productivity/causal; period-end vs average-store denominators not substituted. |
| F25 | `rda-03-store-b18.png` | `450d1af5…` | Period-specific store counterexample in the Feb 1, 2026 column fully wrapped, including the identity caveat. Aligned observations: store growth 14.1/8.5/7.9/5.7%; revenue 29.6/18.6/10.1/4.9%; differences 15.52/10.05/2.20/−0.88. |
| B36 | `rda-07-compsales.png` | `728276189f9293e3e01699b08d57a066f1f69d074d671d35997e9da609b0e7e9` | Comparable-sales limitations complete: not causal; reported vs constant-currency separate; identities unmerged (`company_operated_stores` / `…_direct_to_consumer` / `…_ecommerce`); historical compsales comparison ineligible. Verdict supported descriptively; sample 4 period-ends. |
| B56 | `rda-09-productivity.png` | `7e1bf4abd935ddd72eb4f64ac5b54df1a07b4ccdcc7303bcd45e9cd57fd05676` | Productivity limitations complete; adjacent SPSF unavailable at 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01 with named mismatch reasons; gaps not bridged. Verdict insufficiently evidenced; sample 0. |
| A57:A58 | `rda-09-productivity.png` | same | Heading DEFERRED DISAGREEMENT. Full 2023-01-29 SPSF disagreement: FY2022 during-the-year definition (10-K p. 3; physical 3→7) vs FY2023 average-ending definition (10-K p. 4; physical 4→10); reasons `definition_mismatch`, `ordinary_disagreement`; complete group audit-only, not admitted, not bridged. |
| F83 | `rda-13-geographic.png` / `rda-14-geographic-obs.png` | `8e33b839de68b78a0e0084c392687dc4b4710238440f2ec6441f8cd70c8513a8` / `a23e3799db1e5a9eb23e51efd274f57cf511c398e47cbf49bfa6f4f166fc0e1e` | 2026-02-01 geographic counterexample complete: revenue 4.86%; Americas −0.766 pp; China Mainland 3.716 pp; Rest of World 1.909 pp; mix mixed, not causal. Hypothesis, Power of Three ×2 / China Mainland locators, mixed verdict, arithmetic-decomposition limitations readable. |
| A90:B90 | `rda-14-geographic-obs.png` | `a23e3799…` | NOTES: Scope and evidence limits + full scope paragraph; Identities versus inference also readable. Revenue per Store identity 10,900 / 12,382 / 13,539 / 13,805 / 13,690 visible. |

First 16 numbered captures (`01-header-a5.png` …) showed Overview because sheet `goto` had not yet run; retained, not overwritten. Some later `screencapture -x` frames were occluded by Cursor, Chrome, or Mission Control (`rda-front-05-f25.png` is Mission Control). Overlapping RDA views above were used for inspection. Formatting properties were not treated as readability.

**Presentation defects demonstrated:** none. No wrapping/row-height/column-width/pagination edit. Ordinary `python -m bav build Lululemon` was not re-run.

## Native Excel carry-forward

Final BAV bytes unchanged (`f0f46a03…`). Granted copy and saved snapshot remain `1d332daa…`. Formulas, literal inputs and transitive dependencies are unchanged by identity; the accepted 37-reference / 103-cell VERIFIED evidence is carried forward without recalculation.

Retained: `.git/autocycle/excel-verification-fb95_r2m/`, `excel-verification-7vjhjujd/`, `excel-verification-kd2d78ng/`, `excel-verification-ti974vnt/`, `excel-verification-kzg9a_ex/`.

## Artifact hashes (unchanged)

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/output/Lululemon/Lululemon_BAV.xlsx` | `f0f46a03f4c2091f8d9a1d3002b37bcda2bd46c6851389d9ebc4171cbf4f1a0c` | 224649 |
| `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` | 260706 |
| granted working copy | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` | 260706 |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected artifacts and source extracts were not replaced. No Trainer derivation (BAV unchanged). No model/workbook/Trainer/build regressions re-run (no implementation change).

## Remaining toward Completion

Four hypotheses, deferred SPSF disagreement, and both period-specific counterexamples were visually inspected at readable scale on native Excel screenshots. This bounded work does not close broader strategy synthesis, Session Endpoint, or earlier deferred obligations.

---

# RESULT.md — Step 3.3.1 Finish revenue-driver presentation and verification

**Status:** BLOCKED (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.3.1 — Finish revenue-driver presentation and verification  
**Work:** `8a8f7457f9524a6997e0ec2fbbe5ac23`  
**Plan:** `1514e4f5040245289fcedaab76234184`  
**Finding:** Test disclosure-led historical revenue drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `7b5b63e1192cb5d98e44d1bf8b688bf8d585db78dab5daacab38885ad944c85e` (6640).  
No commit / push / sync / checkpoint / branch change. No BAV regeneration.

## Required plan change

Rendered readability remains blocked on human authorization. Bounded alternatives were attempted; a timeout is not the only evidence. `screencapture` returned a concrete Screen Recording denial (`could not create image from display` / `from rect`). Excel CopyPicture, copy, and print-area assignment fail with automation errors. Whole-sheet PDF still times out on an ungranted destination; a granted-folder PDF returned `exported` in 8.3s but wrote no file. Do not treat wrapping, character counts, or export-command success as readability. Broader strategy synthesis and Session Endpoint closure remain subsequent work.

## Rendering attempts (this attempt)

Started from reviewed final workbook SHA-256 `f0f46a03f4c2091f8d9a1d3002b37bcda2bd46c6851389d9ebc4171cbf4f1a0c` (224649). Inspected `.git/autocycle/revenue-driver-render-3-3-1/export.applescript` (prior 120s whole-sheet PDF). Operated on the already-granted native Excel verification copy of that workbook (`1d332daa…`); source BAV bytes were never overwritten. Idle hung Excel (0 workbooks / 0 windows leftover from the prior PDF timeout) was quit and relaunched so open/select would work. Granted copy and source hashes were unchanged after close-without-save.

| Method | Limit | Measured result |
|---|---|---|
| Prior whole-sheet PDF to `revenue-driver-render-3-3-1/` | 120s | Timed out; no PDF (preserved diagnostic) |
| Healthy-Excel whole-sheet PDF after hiding other sheets, ungranted PDF path | 60s AppleScript / 70s runner | `AppleEvent timed out` (-1712); no PDF |
| Whole-sheet PDF beside granted xlsx | 70s | Script returned `exported` in 8.3s; **no PDF file written** (searched granted dir, render dir, Documents, Desktop, Downloads, Excel container) |
| Set worksheet / page-setup print area | 45s | `Can't set print area` (-10006) |
| CopyPicture plain / screen / bitmap / picture | 45–60s | Parameter error (-50) after successful select |
| `copy` / `copy object selection` then temp-workbook PDF | 45s | `-1708` (`misccopy` / selection does not understand copy object) |
| System Events window resize / bounds | 15s | `Can't get window 1 of process Microsoft Excel` (-1719) |
| Quartz `screencapture -l` | n/a | Quartz/AppKit unavailable in invoking Python |
| `screencapture -x` display and `-R` Excel bounds `{20,40,1600,1000}` after activate/select/100% zoom | immediate | **Concrete denial:** `could not create image from display` / `could not create image from rect` |

Successful authorized Excel automation (not readability evidence): open granted copy; activate `Revenue Driver Analysis`; select `A1:F18`, `A21:F26`, `A27:F37`, `A48:F61`, `A67:F84`, `A85:F91`, `A57:F58` at 100% zoom; move window to `{20,40,1620,1040}`; close without saving.

No readable screenshot or rendered page was retained. Required cells were therefore not inspected at readable scale. No presentation defect was demonstrated; no wrapping/row-height/column-width edit and no `python -m bav build Lululemon` regeneration were performed.

Diagnostics: `.git/autocycle/revenue-driver-render-3-3-1/attempt-20260920-1818-diagnostics.json` (SHA-256 `8d43da333a8a03fd0e5430b15ea4ded5581e5faf5ddd6a12b4d83be7b68c2554`). Prior `export.applescript` retained.

Human decision required (do not bypass): grant Screen Recording to the invoking terminal/agent, and/or grant/repair native Excel PDF export so a PDF is actually written to a permitted path. Do not dismiss Excel dialogs as a retry.

## Native Excel carry-forward

Final BAV bytes unchanged (`f0f46a03…`). Granted verification copy and `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` remain `1d332daa…`. Formulas, literal inputs and transitive dependencies are unchanged by identity; the accepted 37-reference / 103-cell VERIFIED evidence is carried forward without recalculation.

Retained: `.git/autocycle/excel-verification-fb95_r2m/`, `excel-verification-7vjhjujd/`, `excel-verification-kd2d78ng/`, `excel-verification-ti974vnt/`, `excel-verification-kzg9a_ex/`.

## Artifact hashes (unchanged)

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/output/Lululemon/Lululemon_BAV.xlsx` | `f0f46a03f4c2091f8d9a1d3002b37bcda2bd46c6851389d9ebc4171cbf4f1a0c` | 224649 |
| `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` | 260706 |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected artifacts and source extracts were not replaced. No Trainer derivation (BAV unchanged).

## Remaining toward Completion

Required rendered inspection of all four hypotheses (A5, B12, B15, B18, B36, B56, A57:A58, F25, F83, A90:B90) is still missing. Deferred SPSF disclosure and native Excel caches remain as previously verified. This attempt does not close broader strategy interpretation, Session Endpoint, or earlier deferred obligations.

---

# RESULT.md — Step 3.3.1 Finish revenue-driver presentation and verification

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.3.1 — Finish revenue-driver presentation and verification  
**Work:** `8a8f7457f9524a6997e0ec2fbbe5ac23`  
**Plan:** `ae0a334d973046dba34439501d718da6`  
**Finding:** Test disclosure-led historical revenue drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `2421f7753841af1d1cde8f1e5b548e06d8e3223dd5205ce55d9d8619e2a602ed` (6773).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Ordinary Lululemon BAV now publishes the deferred 2023-01-29 SPSF disagreement from admission/provenance evidence without admitting the group. Native Excel PDF/page screenshots of Revenue Driver Analysis timed out; that visual-clipping check remains an explicit rendering-access gap already allowed by the plan. Broader strategy synthesis, forecasting and Session Endpoint closure remain subsequent work.

## Deferred 2023-01-29 SPSF disagreement

Ordinary `python -m bav build Lululemon` remains Active for Revenue Driver Analysis. Fast Retailing still has no strategy payload; the sheet is absent and Build Status reports Source unavailable / not admitted.

The disagreement is carried through the existing StandardizedFinancials KPI handoff as `historical_operating_kpis.deferred_disagreements`, not as `management_observations`. Reported values stay documentary. Admission and comparison eligibility remain independent.

Handoff rule (generic): a deferred group is published only when it has `ordinary_disagreement` plus at least one evidenced conflict reason (`definition_mismatch`, qualifier/population/unit/basis/calendar mismatches). Missing-revision, missing-presentation, unknown-assurance, value-only ordinary disagreement, absent admission, and other-family conflicts do not produce a sales-per-square-foot disagreement assertion.

Measured Lululemon deferred group (not admitted):

| Field | Evidence |
|---|---|
| Period-end | 2023-01-29 |
| Family | `sales_per_square_foot` |
| Reasons | `definition_mismatch`, `ordinary_disagreement` |
| Current locator | `LULU_FY2022_management_kpis.json:reported_kpis[17]:sales_per_square_foot:2023-01-29` |
| Current source | Form 10-K p. 3; physical `3→7` |
| Current definition | Total net revenue from all company-operated stores divided by average store square footage **during the year** … |
| Prior locator | `LULU_FY2023_management_kpis.json:reported_kpis[36]:sales_per_square_foot:2023-01-29` |
| Prior source | Form 10-K p. 4; physical `4→10` |
| Prior definition | Total net revenue from all company-operated stores divided by average **ending** square footage of stores for each period during the year … |
| Reported values | 1580 and 1580 (unadmitted) |
| Consequence | Complete group remains audit-only; not bridged into the productivity test; does not create an admitted observation |

Admitted SPSF levels remain **3** (2024-01-28 / 2025-02-02 / 2026-02-01). Period-end 2023-01-29 is absent from `management_observations`. Missing admitted observations and unavailable adjacent SPSF growth remain stated separately and do not substitute for the disagreement row.

Preserved KPI coverage: **24** Comparable Sales facts, **3** SPSF levels, **5** Revenue per Store periods, **39** pair assessments and five supported historical SPSF comparisons. Store-count sources remain 5.

## Workbook presentation (inspected after regeneration)

Professional BAV sheet `Revenue Driver Analysis` after `python -m bav build Lululemon`. Period columns widened 16→28. Deferred disagreement is a full-width wrapped row, not joined into the ordinary limitations blob.

| Cell (relocated equivalents) | Role | Characters | wrap_text | row height |
|---|---|---|---|---|
| A5 | scope note | 615 | True | 68 |
| B12 | first store disclosure | 225 | True | 38 |
| B15 | store finding + 2026-02-01 counterexample | 635 | True | 98 |
| B18 | store limitations | 640 | True | 98 |
| B36 | compsales limitations | 655 | True | 98 |
| B56 | productivity limitations (admitted-evidence only) | 887 | True | 128 |
| A57 | DEFERRED DISAGREEMENT heading | 21 | False | default |
| A58 | deferred SPSF disagreement (full-width merge A–F) | 1215 | True | 113 |
| F25 | store period-specific interpretation 2026-02-01 | 485 | True | 308 |
| F83 (was F81) | geographic period-specific interpretation 2026-02-01 | 218 | True | 143 |
| A90 / B90 (was A5/B88 pair at foot) | scope note | 25 / 615 | True | 143 / 83 |

Four hypotheses, long disclosures, findings, limitations, counterexamples, headings and source locators are present. Yellow cells: **0**. Exercise-framing hits: **0**. Linked observation formulas: **37**. Notes present.

Period-specific counterexamples preserved:

- Store expansion, period-end **2026-02-01**: store-count growth **5.74%** exceeded revenue growth **4.86%** (descriptive difference **−0.878 pp**). Period-end Revenue per Store declined. Not new-store contribution or productivity proof.
- Geographic growth, period-end **2026-02-01**: consolidated revenue grew **4.86%** while **Americas −0.766 pp** contributed negatively and China Mainland **3.716 pp** / Rest of World **1.909 pp** contributed positively. Mix is mixed, not causal.

Native Excel PDF export of this sheet timed out after 120s on a dedicated copy (`.git/autocycle/revenue-driver-render-3-3-1/`). No screenshot or rendered page was obtained. Character counts and wrap/height properties therefore do not close visual clipping. That remains an explicit rendering-access gap. The original BAV bytes were unchanged by the timed-out export (`f0f46a03…`).

## Trainer / Check

Optional `derive_trainer_workbook`: primary BAV bytes unchanged. **37** driver practice cells blank-yellow, no comments; **37** KPI source facts populated. Semantic components **861**; Check surface **824**.

Workbook-wide Check on copies of the ordinary derived Trainer (BAV bytes unchanged throughout):

| Case | total | blank | correct | incorrect |
|---|---|---|---|---|
| Blank | 824 | 824 | 0 | 0 |
| All formulas filled | 824 | 0 | 824 | 0 |
| Incorrect each driver family (`=999`) | 824 | 0 | 823 | 1 |

Families covered with an incorrect case: Revenue per Store, store growth, revenue growth, store difference, comparable sales, comparable-sales difference, geographic contribution. Summaries are non-disclosing (`=999` and formulas absent from `repr`).

## Native Excel

Formulas relocated with the extra deferred-disagreement rows (geographic C76/C78/C80 → C78/C80/C82; Revenue per Store B84:F84 → B86:F86). Store and compsales formula addresses were unchanged. Independent references were rebound to the final workbook hash and recalculated.

```
python3 ~/.autocycle/excel_verification.py build/output/Lululemon/Lululemon_BAV.xlsx -- python scripts/verify_cached_workbook.py '{workbook}' --original build/output/Lululemon/Lululemon_BAV.xlsx --references docs/native-excel-revenue-driver-references.json
```

| Item | Value |
|---|---|
| Status | VERIFIED |
| Independent references | 37 |
| Checked cells (incl. transitive deps) | 103 |
| Formulas preserved | true |
| Evidence | `.git/autocycle/excel-verification-fb95_r2m/` |
| Snapshot | `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` |
| Copy SHA-256 | `1d332daa8740fc53df6eaf90ecff5c7446f19502ad9510a7ab5ff56954aa1cae` |
| References SHA-256 | `440732349af1a8c11e2c51de5a96e71125b4e55584e97be1a198fe0474727aea` |

Retained prior evidence dirs: `.git/autocycle/excel-verification-7vjhjujd/`, `.git/autocycle/excel-verification-kd2d78ng/`, `.git/autocycle/excel-verification-ti974vnt/`, `.git/autocycle/excel-verification-kzg9a_ex/`.

## Verification commands

| Command | Result |
|---|---|
| `python -m pytest core/tests/test_revenue_driver.py` | **15 passed** |
| `python -m pytest core/tests/test_management_kpi_history.py` (with revenue-driver) | included in **63 passed** then later **132 passed** with build/protected |
| `python -m pytest` operating_kpi_management_history, management_kpi_admission, current_build, operating_kpi_workbook, lululemon_benchmark, fast_retailing_benchmark, build_cli, build_contract, revenue_per_store | **1574 passed** |
| `python -m pytest` protected artifacts + operating_kpi_relationships/facts + geographic_segment_analysis + trainer | **199 passed** including **50/50** protected artifacts and **8/8** extracts |
| `python -m pytest` current_build, revenue_driver, management_kpi_history, protected artifacts, build_cli, build_contract (after layout) | **132 passed** |
| `python -m bav build Lululemon` | exit 0; Revenue Driver Analysis Active |
| `python -m bav build FastRetailing` | exit 0; no Revenue Driver sheet; status unavailable |
| Trainer Check | blank 824; filled 824 correct; 7 driver-family incorrect cases each 1 incorrect |
| Native Excel helper | **VERIFIED** (37 refs, 103 cells) |
| Native Excel PDF export of Revenue Driver Analysis | **timed out 120s**; no rendered pages |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected PDFs, extracts and authenticated baselines were not replaced.

## Artifact hashes

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/output/Lululemon/Lululemon_BAV.xlsx` | `f0f46a03f4c2091f8d9a1d3002b37bcda2bd46c6851389d9ebc4171cbf4f1a0c` | 224649 |
| `build/output/Lululemon/Lululemon_BAV.component_map.json` | `0db382729238162bc6e1240c42b6792fc63fbb5b526fd95c3fda5e45d19619f3` | 1202071 |
| `build/output/Lululemon/supporting/standardized.json` | `88021a6274fedf54899b12ee5727ce8985ad50dcb8f0b85e051a746d1dd8d803` | 70646 |
| `core/tests/fixtures/strategy/lululemon_management_disclosures.json` | `8da4536a21d6874ddedfaea06cb4e3b948f11b23a33d8f55b1f24c850157d845` | 4255 |
| `docs/native-excel-revenue-driver-references.json` | `440732349af1a8c11e2c51de5a96e71125b4e55584e97be1a198fe0474727aea` | 19150 |
| `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (derived) | `747cf7ba4e822b0202bbb0a4d5c68ebffbb2a58ec37d619096098c5dd5d7721d` | 63829 |
| `build/output/FastRetailing/FastRetailing_BAV.xlsx` | `228f3933478b2e2241bd0e0726f6c3eb979ce6dc22cf93d88ee92c4e87e6854b` | 135092 |

## Remaining toward Completion

Deferred SPSF disagreement is now evidence-derived in the model and published workbook, with generic non-Lululemon/absent/incompatible regressions. Native Excel cached values for the 37 relocated driver formulas were independently recalculated. Visual readability of wrapped cells was not established by a rendered page or screenshot because Excel PDF export timed out; that remains an explicit rendering-access gap. This attempt does not close broader strategy interpretation, Session Endpoint, historical comparable-sales comparison windows, or earlier normalization / normalized-per-share obligations.

---

# RESULT.md — Step 3.3.1 Finish revenue-driver presentation and verification

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.3.1 — Finish revenue-driver presentation and verification  
**Work:** `8a8f7457f9524a6997e0ec2fbbe5ac23`  
**Plan:** `6573768c570445d7a990964b4c543a70`  
**Finding:** Test disclosure-led historical revenue drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `abe85697fa119bd53cf9f0485d5c626babe9cdf2978567fd446da3c28a9eac05` (6606).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Ordinary Lululemon BAV now publishes period-specific counterexample interpretations beside observations and verdicts, wraps long disclosure/finding/limitation text with explicit row heights, and derives FY2022-style population and 2023-01-29 SPSF limitations from admitted identities, periods and comparison evidence. Broader strategy synthesis, forecasting and Session Endpoint closure remain subsequent work.

## Presentation and evidence-derived limitations

Ordinary `python -m bav build Lululemon` remains Active for Revenue Driver Analysis. Fast Retailing still has no strategy payload; the sheet is absent.

Rendered Revenue Driver Analysis (inspected after regeneration):

| Cell | Characters | wrap_text | row height |
|---|---|---|---|
| B12 (first disclosure) | 225 | True | 68 |
| B15 (store finding, includes 2026-02-01 counterexample) | 635 | True | 143 |
| B18 (store limitations) | 640 | True | 143 |
| A5 / B88 (scope note) | 615 | True | 83 / 143 |
| B36 (compsales limitations) | 655 | True | 158 |
| B56 (productivity limitations) | 887 | True | 203 |
| F25 / F81 (period interpretations) | 485 / 218 | True | 323 / 158 |

Merged narrative cells use wrapping and explicit heights. Formula addresses on this sheet are unchanged versus the prior Excel-verified copy (37 linked observation formulas). Component map SHA-256 is unchanged.

Period-specific counterexamples are in findings, observation notes, and a "Period-specific interpretation" row beside the relevant period columns:

- Store expansion, period-end **2026-02-01**: store-count growth **5.74%** exceeded revenue growth **4.86%** (descriptive difference **−0.878 pp**). Period-end Revenue per Store declined. Not new-store contribution or productivity proof.
- Geographic growth, period-end **2026-02-01**: consolidated revenue grew **4.86%** while **Americas −0.766 pp** contributed negatively and China Mainland **3.716 pp** / Rest of World **1.909 pp** contributed positively. Mix is mixed, not causal.

Generic analysis no longer asserts unconditional "FY2022 store-only" or "deferred 2023-01-29 SPSF definition disagreement". Those facts appear only from supplied evidence:

- Comparable-sales populations remain distinct: `company_operated_stores` at 2023-01-29; `company_operated_stores_and_direct_to_consumer` at 2023-01-29; `company_operated_stores_and_ecommerce` at 2024-01-28, 2025-02-02, 2026-02-01. Historical compsales-to-compsales comparison remains ineligible on admitted calendar/comparison-window evidence.
- No admitted SPSF observation for period-end **2022-01-30, 2023-01-29** (not bridged). Adjacent SPSF growth unavailable at 2023-01-29 (missing observation), 2024-01-28 (missing prior), 2025-02-02 and 2026-02-01 (definition / calendar week-adjustment / qualifier mismatch). Audit-only deferred 2023-01-29 SPSF disagreement is not promoted into the test.
- Synthetic single-population / missing-SPSF cases do not emit Lululemon period labels or disagreement assertions.

Preserved KPI coverage (standardized SHA-256 unchanged): **24** Comparable Sales facts, **3** SPSF levels, **5** Revenue per Store periods, **39** pair assessments and five supported historical SPSF comparisons remain as previously admitted. Admission and comparison eligibility stay independent.

## Trainer / Check

Optional `derive_trainer_workbook`: primary BAV bytes unchanged. **37** driver practice cells blank-yellow, no comments; **37** KPI source facts populated.

Workbook-wide Check on the ordinary derived Trainer:

| Case | total | blank | correct | incorrect |
|---|---|---|---|---|
| Blank | 824 | 824 | 0 | 0 |
| All formulas filled | 824 | 0 | 824 | 0 |
| Incorrect each driver family (`=999`) | 824 | 0 | 823 | 1 |

Families covered with an incorrect case: store growth, revenue growth, store difference, comparable sales, comparable-sales difference, Revenue per Store, geographic contribution. Summaries are non-disclosing (`=999` and formulas absent from `repr`). Primary BAV bytes unchanged throughout derivation and Check.

## Native Excel

Driver formula cells, formula text and KPI-sheet dependencies match the prior saved copy. Independent references were re-bound to the new workbook hash and recalculated.

```
python3 ~/.autocycle/excel_verification.py build/output/Lululemon/Lululemon_BAV.xlsx -- python3 scripts/verify_cached_workbook.py '{workbook}' --original build/output/Lululemon/Lululemon_BAV.xlsx --references docs/native-excel-revenue-driver-references.json
```

| Item | Value |
|---|---|
| Status | VERIFIED |
| Independent references | 37 |
| Checked cells (incl. transitive deps) | 103 |
| Formulas preserved | true |
| Evidence | `.git/autocycle/excel-verification-7vjhjujd/` |
| Snapshot | `.git/autocycle/excel-verification-7vjhjujd/saved-copy.xlsx` |
| Copy SHA-256 | `988c37a02b9ddf507976f1614635bf4093663eb2cba5595f1ad48cdc8a91ee9f` |
| References SHA-256 | `3bcbaaa2187c5fac469a19c9a282a13dd8a7db8b4153aa4c5bda74fba0354c8e` |

Retained prior evidence dirs (formula/input/dependency identity confirmed against `kd2d78ng` saved copy): `.git/autocycle/excel-verification-kd2d78ng/`, `.git/autocycle/excel-verification-ti974vnt/`, `.git/autocycle/excel-verification-kzg9a_ex/`.

## Verification commands

| Command | Result |
|---|---|
| `python -m pytest core/tests/test_revenue_driver.py` | **13 passed** |
| `python -m pytest` current_build, RPS, build_contract, build_cli, `test_protected_artifacts_and_eight_extracts_unchanged` | **88 passed** including **50/50** protected artifacts and **8/8** extracts |
| `python -m pytest` operating_kpi_workbook, lululemon_benchmark, fast_retailing_benchmark, operating_kpi_relationships/facts, geographic analysis | **513 passed** |
| `python -m bav build Lululemon` | exit 0; Revenue Driver Analysis Active |
| `python -m bav build FastRetailing` | exit 0; no Revenue Driver sheet; status unavailable |
| Trainer Check | blank 824; filled 824 correct; 7 driver-family incorrect cases each 1 incorrect |
| Native Excel helper | **VERIFIED** |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected PDFs, extracts and authenticated baselines were not replaced.

## Artifact hashes

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/output/Lululemon/Lululemon_BAV.xlsx` | `783b31fa7598ce169fcb038f8d0056eeca87d6260b9fe86be857ed0e8b5f34f3` | 224032 |
| `build/output/Lululemon/Lululemon_BAV.component_map.json` | `847ab414c3b1c5a1e4141a6bffee8cb1f071ac6d9d67df5a90a51b41fd74fe62` | 1202071 |
| `build/output/Lululemon/supporting/standardized.json` | `e283d2ebf9bc63a7678a58bd7f25c8a0577776886b327086718a4872ce94cf8a` | 68218 |
| `core/tests/fixtures/strategy/lululemon_management_disclosures.json` | `8da4536a21d6874ddedfaea06cb4e3b948f11b23a33d8f55b1f24c850157d845` | 4255 |
| `docs/native-excel-revenue-driver-references.json` | `3bcbaaa2187c5fac469a19c9a282a13dd8a7db8b4153aa4c5bda74fba0354c8e` | 19150 |
| `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (derived) | `d6186895357fd6e51e4a5e2223e436db5eb50953350f88bbc8579152498e8ad8` | 63446 |
| `build/output/FastRetailing/FastRetailing_BAV.xlsx` | `414c715a9613e13d4d3d3d26908b968219f9583a1ed28d8d8a99579812580083` | 135090 |

## Remaining toward Completion

Readable publication, evidence-derived limitations, counterexample interpretations and Trainer Check coverage for this bounded repair are measured. This attempt does not close broader strategy interpretation, Session Endpoint, deferred SPSF adjacency as an admission/audit fact, historical comparable-sales comparison windows, or earlier normalization / normalized-per-share obligations.

---



**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.3 — Test disclosure-led historical revenue drivers  
**Work:** `8a8f7457f9524a6997e0ec2fbbe5ac23`  
**Plan:** `c725d560c2fb486191e16749804fd7ce`  
**Finding:** Test disclosure-led historical revenue drivers  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `0928f4128b1fb67324e0f2094a30ee7522c9d865049a5661b63b71c992ee3c0b` (6828).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Ordinary Lululemon BAV now presents four source-linked revenue-driver hypothesis tests on admitted history. Broader strategy synthesis, forecasting and Session Endpoint closure remain subsequent work. Deferred SPSF comparison, historical comparable-sales comparison ineligibility, and earlier normalization/per-share obligations are unchanged.

## Ordinary publication

`python -m bav build Lululemon` emits **Revenue Driver Analysis** as Active. Fast Retailing has no strategy payload; the sheet is absent and Build Status reports **Source unavailable / not admitted**.

Disclosures live in `core/tests/fixtures/strategy/lululemon_management_disclosures.json` (10 source-bound statements) and attach only in ordinary `prepare_company_input`. Protected `benchmark/lululemon/reconciled/standardized.json` has no `historical_strategy`; `LEASE_DT_LULULEMON_SPECS = 486` is unchanged.

## Tested hypotheses (admitted Lululemon history)

Independent anchors: `REVENUE_ANCHORS` and `INDEPENDENT_STORE_TOTALS`; admitted global reported comparable-sales percentages and geographic net revenue from `supporting/standardized.json`. Sample n and period-ends are actual filing dates, not fiscal-year labels.

| Theme | Locators | Periods tested | Verdict | Measured result |
|---|---|---|---|---|
| Store expansion | FY2022 10-K p.32 strategy; FY2024 10-K p.3 strategy + objective | 4: 2023-01-29 … 2026-02-01 | **supported descriptively** | Store counts 574→655→711→767→811 and revenue 6,256,617→8,110,518→9,619,278→10,588,126→11,102,600 both rose in every adjacent window. FY2026 store growth 5.74% exceeded revenue growth 4.86% (descriptive difference −0.88 pp); period-end Revenue per Store declined 13,804.60→13,690.01. Objective text is not treated as an achieved outcome. |
| Comparable sales | FY2022 10-K p.31–32 operating use; FY2024 10-K p.33 operating use | 4 identity-periods across the same four dates | **supported descriptively** | Global reported compsales +25% (stores+DTC, 2023-01-29), +13% / +4% / +2% (stores+ecommerce, 2024-01-28 … 2026-02-01) were positive while statement-derived revenue grew. FY2022 store-only vs later stores+DTC/ecommerce identities are not merged. Historical compsales-to-compsales comparison remains ineligible. Differences are descriptive, not organic/new-store attribution. |
| Productivity | FY2022 10-K p.3 and FY2024 10-K p.34 SPSF operating use | 0 | **insufficiently evidenced** | Failed requirement: immediately adjacent semantically compatible reported SPSF observations. Additional evidence: equivalent definition, population, calendar and comparison-window. Three SPSF levels remain admitted (1,609 / 1,574 / 1,426) without adjacent growth. RPS is labeled an identity, not store-only productivity. |
| Geographic growth | FY2022 10-K p.24 Power of Three ×2; FY2024 10-K p.3 China Mainland | 4; 3 identities | **mixed** | Reported-currency contributions. Americas 2026-02-01 contribution −0.766 pp while China Mainland and Rest of World were positive and consolidated revenue still grew. Not organic, constant-currency, or causal. |

Revenue-growth-minus-store-growth and revenue-growth-minus-compsales are descriptive percentage-point differences only. Total-company revenue / company-operated stores cannot independently demonstrate productivity or expansion’s causal contribution.

## Workbook presentation

Professional BAV sheet `Revenue Driver Analysis`: management statements with source file / page / section / period-end, analyst hypotheses, mechanisms, findings, verdicts, sample sizes, limitations, failed requirements, identity notes, linked observation formulas (37), and Notes. No yellow cells; no Trainer/exercise/practice framing.

Mapped driver cells: store growth 4, revenue growth 4, store difference 4, compsales 4, compsales difference 4, geographic contribution 12, Revenue per Store identity 5. **Total 37.**

Preserved KPI coverage: **24** Comparable Sales source facts, **3** SPSF levels, **5** Revenue per Store period-end cells (**17** RPS mapped cells). Store-count sources remain 5.

## Trainer / Check

Optional `derive_trainer_workbook`: primary BAV bytes unchanged. 37 driver practice cells blank-yellow, no comments. Workbook-wide Check: **blank 824 / correct 0 / incorrect 0 / total 824** (non-disclosing).

## Native Excel

New/changed driver formulas were recalculated with the installed helper. Status **VERIFIED**.

```
python3 ~/.autocycle/excel_verification.py build/output/Lululemon/Lululemon_BAV.xlsx -- python3 scripts/verify_cached_workbook.py '{workbook}' --original build/output/Lululemon/Lululemon_BAV.xlsx --references docs/native-excel-revenue-driver-references.json
```

| Item | Value |
|---|---|
| Status | VERIFIED |
| Independent references | 37 |
| Checked cells (incl. transitive deps) | 103 |
| Formulas preserved | true |
| Evidence | `.git/autocycle/excel-verification-kd2d78ng/` |
| Snapshot | `.git/autocycle/excel-verification-kd2d78ng/saved-copy.xlsx` |
| Copy SHA-256 | `5cd5bf14328ff378b4f07bb0d1f26fb866c3a754d343c6167cb952c2ce5b8c74` |
| References SHA-256 | `cb64ba83ae9b4057fbbb00fb1328935f0e0d3e4878c8c1b56c0292a96a6cd241` |

Carried forward unchanged RPS/store-count cached-value evidence: `.git/autocycle/excel-verification-ti974vnt/` and `.git/autocycle/excel-verification-kzg9a_ex/` (corresponding formulas, literal inputs and transitive dependencies on those schedules were not rewritten).

## Verification commands

| Command | Result |
|---|---|
| `python -m pytest core/tests/test_revenue_driver.py` | **11 passed** |
| `python -m pytest` current_build, RPS, build_contract, build_cli, catalog wording, `test_protected_artifacts_and_eight_extracts_unchanged` | **87 passed** including **50/50** protected artifacts and **8/8** extracts |
| `python -m pytest` operating_kpi_workbook, lululemon_benchmark, fast_retailing_benchmark, operating_kpi_relationships/facts, geographic committed identities | **498 passed** |
| `python -m bav build Lululemon` | exit 0; Revenue Driver Analysis Active |
| `python -m bav build FastRetailing` | exit 0; no Revenue Driver sheet; status unavailable |
| Trainer Check | 824 blank, 0 correct, 0 incorrect |
| Native Excel helper | **VERIFIED** |

`SEGMENT_BRIDGE_TOLERANCE = 0.0`. Protected PDFs, extracts and authenticated baselines were not replaced.

## Artifact hashes

| Path | SHA-256 | Bytes |
|---|---|---|
| `build/output/Lululemon/Lululemon_BAV.xlsx` | `7470a1aaba549ace96895b04ae53b130353785783a8c3c739259118ac3bd5162` | 223349 |
| `build/output/Lululemon/Lululemon_BAV.component_map.json` | `847ab414c3b1c5a1e4141a6bffee8cb1f071ac6d9d67df5a90a51b41fd74fe62` | 1202071 |
| `build/output/Lululemon/supporting/standardized.json` | `e283d2ebf9bc63a7678a58bd7f25c8a0577776886b327086718a4872ce94cf8a` | 68218 |
| `core/tests/fixtures/strategy/lululemon_management_disclosures.json` | `8da4536a21d6874ddedfaea06cb4e3b948f11b23a33d8f55b1f24c850157d845` | 4255 |
| `docs/native-excel-revenue-driver-references.json` | `cb64ba83ae9b4057fbbb00fb1328935f0e0d3e4878c8c1b56c0292a96a6cd241` | 19150 |
| `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (derived) | `0b91cc3c398410a17fb80422b18c12074de0ceb84469af31e6dbc504d6efc7c8` | 63139 |
| `build/output/FastRetailing/FastRetailing_BAV.xlsx` | `0503bbf580fa4c55ca71ace4adcdd2a909eb540ba82a665e5e7482fba94cff1c` | 135090 |

## Remaining toward Completion

Ordinary BAV now shows source-linked tests, measured findings, identities and evidence limits. This attempt does not close broader strategy interpretation, Session Endpoint, deferred SPSF adjacency, historical comparable-sales comparison windows, or earlier normalization / normalized-per-share obligations.

---

# RESULT.md — Step 3.2.8 Require affirmative agreement for repeated management disclosures

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.8 — Require affirmative agreement for repeated management disclosures  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `64e2a5cb1c96448a94587974e055eed1`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `1f53c3feace4df41e17365315869bd5edd6b8530c4ecc8c08210f3ffe309509c` (7524).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Ordinary repeats now require affirmative present evidence on every member; empty/null/blank population, unit, basis, `calendar_week_adjustment` or `calendar_reporting_basis` defers the complete group. Conflict-only `evidenced_conflicts` is unchanged. Production Lululemon coverage is unchanged versus the accepted 27 selected / 1 deferred baseline. This bounded repair does not close the major Completion or the Session Endpoint.

## Ordinary agreement repair

`_ordinary_agreement_reasons` now checks each repeat member independently with `text_present` before using conflict-only `evidenced_conflicts`. Representative selection still runs only after complete-group agreement.

| Rule | Behavior |
|---|---|
| Affirmative evidence | Every member must present population, unit, basis, `calendar_week_adjustment` and `calendar_reporting_basis`; absence / null / blank is not agreement and is not inferred from a peer |
| Missing on any member | Complete group deferred with the dimension-specific reason plus `ordinary_disagreement` |
| Conflicts | Unchanged: `evidenced_conflicts` still reports mismatch only when both sides are present and disagree |
| Singletons | Ordinary admission unchanged; missing calendar/population/unit/basis does not by itself block a singleton |
| Revision route | Unchanged; unresolved revision cannot bypass through the ordinary route |
| Handoff | Deferred repeats do not reach `StandardizedFinancials`; stale/tampered-selection rejection retained |

## Missing-evidence regressions

Both families: remove each of the five dimensions independently from either member, from all members, and from one member of a three-occurrence group. Cover absent, null, blank (`""`, `" "`, `" \t "`), and reversed occurrence order. Intact agreeing groups remain selected. `evidenced_conflicts` still does not treat equal-missing as `*_mismatch`.

Real selected 2024 SPSF repeat group (value 1609, two occurrences): each individual removal of population, unit, basis, calendar adjustment or calendar reporting evidence defers selection with the corresponding reason; the intact group remains selected.

Pipeline admission: missing `reporting_basis` or week-adjustment qualifiers on either or both members defers the group. Missing-evidence deferral survives standardized export/reload: the deferred family-period is absent from management histories while a co-period ordinary singleton of the other family still transfers.

## All 28 group decisions (ordinary pipeline)

`python -m bav build Lululemon` recomputed selections from bound evidence. Status `admitted_unreconciled`. Payload `canonical_selection` remains `deferred` because 1/28 groups is deferred.

| Measurement | Result |
|---|---|
| Documents / reported observations | 4 / **138** |
| Group decisions | **28** (CompSales **24**, SPSF **4**) |
| Canonical | selected **27**, deferred **1** — matches accepted baseline |
| StandardizedFinancials management histories | **27** (24 CompSales + 3 SPSF); store-count observations remain 5 |
| Pair assessments | **39** (36 historical, 3 same-period); **7 supported**, **32 unsupported** |
| SPSF pairs | **21** (14 unsupported, **7 supported**) |
| SPSF historical pairs supported | **5** |
| Failure attribution | pair-scoped **79**, without pair **8** (occurrence-only **7** + canonical-selection **1**) |
| Assurance on selected groups | `unknown` (not upgraded) |
| Handoff diagnostic | `27 evidenced selected occurrence(s) …; 1 deferred group(s) remain audit-only` |
| Admission SHA-256 | `c5b28f92bae9776a592131ad0463d8fff695265a3f2fbebcfd3d3acd123b38b9` (2269596) — unchanged vs 3.2.7 |
| Standardized SHA-256 | `b698177d768ee88fb91dd9f08462c388721222d6ad04ae9f597e52753b0930ef` (63714) — unchanged vs 3.2.7 |
| Page resolution SHA-256 | `d2f55444eb4dd7105149c7da3640b12592762307c7deb13a5727cdb6e8c6e188` (126057) — unchanged vs 3.2.6/3.2.7 |

The remaining deferred group is SPSF **2023-01-29** (`definition_mismatch`, `ordinary_disagreement`). FY2022 store-only versus later stores-plus-e-commerce identities remain distinct. Comparison eligibility stays independent of selection: all 24 CompSales groups are comparison-ineligible; SPSF 2024 and 2026 eligible and selected; SPSF 2025 selected but ineligible.

Intact 2024 SPSF repeat evidence (both members): population `company_operated_stores`, unit `USD_per_square_foot`, basis `reported`, week `included`, reporting basis the bound fiscal-calendar sentence.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (210329) |
| Trainer generated by ordinary build | **No** |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Comparable Sales Analysis (24)**, **Sales per Square Foot Analysis (3)**, **Revenue per Store Analysis** |
| CLI / Build Status Unavailable | none of the three KPI analyses |

## BAV / Trainer / Check

Component-map SHA-256 `c8371376a1b525e52361ff91d367ca0a9a2223e1489721f6580320fec73e6d77` (1154015) — **unchanged vs 3.2.7**.  
Assumptions SHA-256 `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69) — unchanged.  
BAV SHA-256 `21f2af1a815c4afa236bca93b91668081528a0a7822d7ed46a0e5c2cf8f8fe3c` (210329). Size +3 bytes vs 3.2.7; formulas/Notes/component map/standardized inputs unchanged (packaging-only xlsx difference).

- Sheets include `Overview`, `Build Status`, `Comparable Sales Analysis`, `Sales per Square Foot Analysis`, `Revenue per Store Analysis`; no Trainer sheet.
- Exercise-framing hits: **0**. Yellow fill: **0**.
- Semantic components **824**; sidecar **824**; embedded `_ComponentMap` **824**.
- Non-source identities **787/787** formulas match the map and have non-empty Notes.
- KPI source facts **37/37** populated (Store Count 10, CompSales 24, SPSF 3).
- Standardized export/reload: payload equality **True**.
- CompSales Excel formulas unchanged: `C143`, `D178`, `E178`, `F178`. SPSF Excel formulas: **0**.

`derive_trainer_workbook` on the published BAV (BAV bytes unchanged):

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (57575 at derive) |
| Active practice cells | **787** blank, **787** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **37** still populated |
| Check blank | 787 / 0 / 0 / 787 |
| Check correctly completed | 787 / 787 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 787 / 786 / 1 / 0 |
| BAV after derivation and Check | unchanged |

## Excel recalculation

Formulas, literal inputs and dependencies are unchanged (identical component map, CompSales formula text, SPSF still has no formulas, identical `standardized.json`). Packaging-only BAV zip difference does not require replay.

Carried forward:

- `.git/autocycle/excel-verification-kzg9a_ex/result.json` — `status: VERIFIED`, RPS/store-count surface, `formulas_preserved: true`
- `.git/autocycle/excel-verification-ti974vnt/result.json` — `status: VERIFIED`, 4/4 CompSales independent references, 17 checked cells, `formulas_preserved: true`, references SHA-256 `ae8f7de1676ee6c770768ff668444ec399ee16b656f4d96bcbcbfd34a64d6fda`

## Revenue per Store (preserved)

| Period | Period-end RPS | Average-store RPS |
|---|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 |

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

| Suite | Result |
|---|---|
| Focused ordinary-selection / missing-evidence / handoff | **61 passed** (singletons, agreeing repeats, deterministic current, conflicting groups, unsupported occurrences, revision-route bypass, missing-dimension deferral, real 2024 SPSF repeat, ordinary singleton history, missing-evidence export/reload, tampered-handoff) |
| identity + admission + reconciliation + history + analysis + enrichment + management-history | **1527 passed** |
| current build + filing CLI + RPS + source availability + operating KPI facts/relationships/workbook + Lululemon + Fast Retailing + protected artifacts | **561 passed** including `test_protected_artifacts_and_eight_extracts_unchanged` — **50/50** artifacts and **8/8** extracts |

Protected PDFs, `benchmark/lululemon/extracted/` and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis is Active for **24** admitted source facts and **4** revenue-versus-compsales difference formulas. Historical compsales-to-compsales comparison remains ineligible (calendar / comparison-window). Selection did not waive those pair rules.
- Sales per Square Foot Analysis is Active for **3** admitted levels (2024, 2025, 2026). FY2023 SPSF is not in the model because the 2023-01-29 group disagrees on definition (`selection_limitation`). Adjacent SPSF change/growth remain unavailable.
- FY2021 SPSF `$1,443` on FY2023 page 10 has no corpus fiscal-year-end, so it remains metadata only.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

This bounded repair completed affirmative-agreement for ordinary repeated disclosures. It does not close the major Completion: historical compsales comparison and FY2023 SPSF remain unsupported for documented pair/definition reasons.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.


---

# Historical record — Step 3.2.7 Select supported management disclosures through production admission

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.7 — Select supported management disclosures through production admission  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `3bb735beb0854fba840957b87e60cd64`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `27723596f11acfa4e9adea7fcdc3e3c24f62cbed13b47c0b0f3a18c4c3dd4e78` (7943).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Ordinary supported singletons and agreeing repeats now become canonical without a documentary revision. One SPSF group remains deferred for a real definition disagreement. Comparable Sales historical comparison stays ineligible on calendar/window rules independently of selection. This bounded repair does not close the major Completion or the Session Endpoint.

## Canonical selection repair

Ordinary selection and documentary-revision selection are now separate generic routes. Missing revision evidence is not a failure for a disclosure that makes no revision claim. Reported KPIs without a `revises` target no longer carry occurrence-level `revision` as unresolved.

| Rule | Behavior |
|---|---|
| Ordinary singleton | Selected when value, identity, dated period, definition, documented presentation and provenance satisfy occurrence admission |
| Agreeing repeats | Require agreement on value, definition text, population, units, currency basis and calendar semantics; deterministic representative prefers the unique `current` role, else locator order; every occurrence and provenance is retained |
| Conflicting / ambiguous ordinary group | Deferred (`ordinary_disagreement`); no subset selection and no silent later-filing preference |
| Incoming or intra-group revision assertion | Revision route only; unresolved revision cannot bypass through the ordinary route |
| Audited reviser gates | Unchanged: direction, target identity, complete membership, competing assertions, unaudited/unknown assurance, superseded occurrences |
| Assurance | Actual labels retained; annual-report placement / management use / repetition do not upgrade `unknown` |
| Independence | Selection does not waive definition equivalence, population, currency, fiscal calendar, metric exclusion, comparison-window or pair-specific requirements |

## All 28 group decisions (ordinary pipeline)

`prepare_company_input` / `python -m bav build Lululemon` recomputed selections from bound evidence. Status `admitted_unreconciled`. Payload `canonical_selection` remains `deferred` because 1/28 groups is deferred; that is a selection limitation, not source absence.

| Measurement | Result |
|---|---|
| Documents / reported observations | 4 / **138** (135 original + 3 traced prior-period SPSF) |
| Group decisions | **28** (CompSales **24**, SPSF **4**) |
| Canonical | selected **27**, deferred **1** |
| StandardizedFinancials management histories | **27** (24 CompSales + 3 SPSF); store-count observations remain 5 |
| Pair assessments | **39** (36 historical, 3 same-period); **7 supported**, **32 unsupported** |
| SPSF pairs | **21** (14 unsupported, **7 supported**) |
| SPSF historical pairs supported | **5** (52-week included, average-ending levels) |
| Failure attribution | pair-scoped **79**, occurrence-only **7**, canonical-selection **1** |
| Assurance on selected groups | `unknown` (not upgraded) |
| Handoff diagnostic | `27 evidenced selected occurrence(s) …; 1 deferred group(s) remain audit-only` |

All 24 CompSales groups are ordinary singletons and were selected. Comparison eligibility remains **ineligible** on every CompSales group (calendar / comparison-window pair failures). FY2022 store-only versus later stores-plus-e-commerce identities remain distinct.

### Three comparison-eligible SPSF groups

| Period | Occurrences | Comparison | Canonical | Model |
|---|---:|---|---|---|
| 2023-01-29 | 2 | eligible | **deferred** | not handed off |
| 2024-01-28 | 2 | eligible | selected (agreeing repeats) | 1609 |
| 2026-02-01 | 1 | eligible | selected (ordinary singleton) | 1426 |

**2023-01-29 remaining rejection:** `definition_mismatch`, `ordinary_disagreement`. FY2022 `sales_per_square_foot_fy2022` (average *during* the year) and FY2023 `sales_per_square_foot_fy2023` (average *ending* square footage) both report **1580** for the same identity-period. The complete group was evaluated; a convenient subset was not selected. Comparison eligibility stays independent of that deferral.

SPSF 2025-02-02 is selected (1574) but comparison-**ineligible** (53-week exclusion / calendar). Adjacent SPSF change, growth and revenue-difference cells are `Source unavailable` / `N/A` opening — unsupported comparisons are not presented as available.

FY2022 presentation, population, pair, calendar and exclusion preservations from Step 3.2.6 remain: physical 37 / printed 33 (`33→37`) for all four CompSales identities; store-only versus stores-plus-DTC; 39 pairs and five supported historical SPSF comparisons; seven SPSF occurrence calendars; FY2022 calendar evidence from FY2023 physical page 33; both FY2024 exclusion bindings to physical 40 / printed 34. FY2022 SPSF historical comparison stays `definition_mismatch` on the correct pairs; FY2024 current / FY2025 prior stays `calendar_mismatch` on those pairs.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (210326) |
| Trainer generated by ordinary build | **No** |
| Admission | `supporting/management_kpi_admission.json` (2269596; SHA-256 `c5b28f92bae9776a592131ad0463d8fff695265a3f2fbebcfd3d3acd123b38b9`) |
| Page resolution | `supporting/management_kpi_page_resolution.json` (126057; SHA-256 `d2f55444eb4dd7105149c7da3640b12592762307c7deb13a5727cdb6e8c6e188`) — unchanged vs 3.2.6 |
| Standardized | `supporting/standardized.json` (63714; SHA-256 `b698177d768ee88fb91dd9f08462c388721222d6ad04ae9f597e52753b0930ef`) |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Comparable Sales Analysis (24)**, **Sales per Square Foot Analysis (3)**, **Revenue per Store Analysis (17)** |
| CLI / Build Status Unavailable | none of the three KPI analyses |

Build Status still states that Active may cover only admitted periods. Canonical deferral of SPSF 2023-01-29 is `selection_limitation` (definition disagreement), not genuine source absence of the 1580 disclosure.

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Comparable Sales Analysis`, `Sales per Square Foot Analysis`, `Revenue per Store Analysis`; no Trainer sheet. Deferred forecast tabs remain placeholders.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner. Exercise-framing hits: **0**.
- Semantic components **824**; sidecar **824**; embedded `_ComponentMap` **824**.
- Non-source identities **787/787** formulas match the map and have non-empty Notes.
- KPI source facts **37/37** populated (Store Count 10, CompSales 24, SPSF 3).
- Yellow fill: **0**.
- Standardized export/reload: payload equality **True**.
- CompSales Excel formulas: **4** revenue-versus-compsales differences on the global reported identity (`C143`, `D178`, `E178`, `F178`). Adjacent compsales change is not implied.
- SPSF Excel formulas: **0**. Levels 1609 / 1574 / 1426 are populated source facts; adjacent change/growth/difference remain unavailable.

BAV SHA-256: `39914cba2d93f6d5ec1ffce6a584468a7a0452f91d58bc312a753085c7759476` (210326).  
Component-map SHA-256: `c8371376a1b525e52361ff91d367ca0a9a2223e1489721f6580320fec73e6d77` (1154015).  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69) — unchanged.

Independent CompSales difference anchors (USD thousands revenue; selected global reported percents 25, 13, 4, 2):

| Cell | Arithmetic | Value |
|---|---|---:|
| C143 | 100×(8110518−6256617)/6256617 − 25 | 4.631045020016408 |
| D178 | 100×(9619278−8110518)/8110518 − 13 | 5.602510961691966 |
| E178 | 100×(10588126−9619278)/9619278 − 4 | 6.0719409502459545 |
| F178 | 100×(11102600−10588126)/10588126 − 2 | 2.8589712664922953 |

FY2022 global reported comparable sales remain stores-plus-DTC (25); later global reported observations are stores-plus-e-commerce (13/4/2). Those identities are not equated.

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV (BAV bytes unchanged):

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (57574 at derive; 57925 after blank Check recolor) |
| Trainer SHA-256 after blank Check | `634993a7f2c80508788f0d32c8683f9c220b9e806169fcfb4448a64304e0468f` |
| BAV SHA-256 after derivation and Check | unchanged |
| Active practice cells | **787** blank, **787** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **37** still populated |
| Check blank | 787 / 0 / 0 / 787 |
| Check correctly completed | 787 / 787 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 787 / 786 / 1 / 0 |

Check summaries were `CheckSummary(total=…, correct=…, incorrect=…, blank=…)` and did not disclose formulas.

## Excel recalculation

Unchanged RPS / store-count surface is carried forward from `.git/autocycle/excel-verification-kzg9a_ex/result.json` (`status: VERIFIED`, 50 independent references, `formulas_preserved: true`).

Newly activated CompSales formulas were recalculated in native Excel:

```bash
python3 ~/.autocycle/excel_verification.py build/output/Lululemon/Lululemon_BAV.xlsx -- python3 scripts/verify_cached_workbook.py '{workbook}' --original build/output/Lululemon/Lululemon_BAV.xlsx --references docs/native-excel-compsales-references.json
```

| Measurement | Result |
|---|---|
| Evidence | `.git/autocycle/excel-verification-ti974vnt/result.json` |
| Status | **VERIFIED** |
| Independent references | **4/4** matched (abs 1e-8) |
| Checked cells | **17** (4 CompSales formulas + Store Count growth dependencies) |
| `formulas_preserved` | true |
| References SHA-256 | `ae8f7de1676ee6c770768ff668444ec399ee16b656f4d96bcbcbfd34a64d6fda` |
| Saved copy SHA-256 | `ea0bd1bb0aa3e25ece56451f2d895fe99e6f30ae037c493f2562beb4e95d2266` |
| SPSF formulas | none; no additional Excel formula verification required |

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged.

| Period | Period-end RPS | Average-store RPS |
|---|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 |

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

| Suite | Result |
|---|---|
| Focused ordinary-selection / handoff | **17 passed** (singletons, agreeing repeats, deterministic current, conflicting groups, unsupported occurrences, revision-route bypass, ordinary singleton standardized history) |
| identity + admission + reconciliation + history + analysis + enrichment | **463 passed** (audited revision, ambiguous-target, competing-direction, complete-group and tampered-handoff coverage retained) |
| current build + filing CLI + RPS + source availability + operating KPI facts/relationships/workbook + Lululemon + Fast Retailing + protected artifacts | **561 passed** including `test_protected_artifacts_and_eight_extracts_unchanged` — **50/50** artifacts and **8/8** extracts |

Protected PDFs, `benchmark/lululemon/extracted/` and authenticated baselines were not replaced. Working-copy enrichment wrote only permitted `supporting/extracted/` copies during the ordinary build.

## Remaining gaps toward Completion

- Comparable Sales Analysis is Active for **24** admitted source facts and **4** revenue-versus-compsales difference formulas. Historical compsales-to-compsales comparison remains ineligible (calendar / comparison-window). Selection did not waive those pair rules.
- Sales per Square Foot Analysis is Active for **3** admitted levels (2024, 2025, 2026). FY2023 SPSF is not in the model because the 2023-01-29 group disagrees on definition (`selection_limitation`). Adjacent SPSF change/growth remain unavailable.
- FY2021 SPSF `$1,443` on FY2023 page 10 has no corpus fiscal-year-end, so it remains metadata only.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

This bounded repair completed ordinary canonical selection, model handoff and activation of supported CompSales/SPSF analysis through the ordinary Lululemon build. It does not close the major Completion: historical compsales comparison and FY2023 SPSF remain unsupported for documented pair/definition reasons.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.


---

# Historical record — Step 3.2.6 Repair FY2022 provenance and population metadata through admission


**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.6 — Repair FY2022 provenance and population metadata through admission  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `3ef0b7a54ef14ce9972456cbbdeea8bc`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `60577fdf82d9bde92581dd49d674584fcf3549be9df2aba00ef4aac3d14053d5` (7584).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. FY2022 `presentation_evidence.source` now agrees with the current-period table passage (physical 37 / printed 33) without overwriting management-use or definition locators. Reported comparable-store-sales `definition_features.channel_population` is store-only; total comparable remains stores-plus-DTC. Canonical selection still requires a later-audited two-occurrence revision group with a documentary revision link (`selection_limitation`). That remaining gate is a selection-policy / unavailable-assurance decision for Review. This bounded repair does not close the major Completion.

## FY2022 provenance and population-metadata repair

Prior Step 3.2.6 bound presentation *passages* to the page-37 table but left `presentation_evidence.source` on the value observation locator (`Form 10-K p. 27` / `27→31`) and classified store-only definitions as stores-plus-DTC because the exclusion clause mentions direct-to-consumer. Constant-dollar identities also received empty `definition_features` because definition lookup used `metric_id` only.

Ordinary enrichment now writes presentation `page_reference` from the presentation passage binding and admission re-validates that locator against the PDF (`33→37`). Management-use stays on physical 35 / printed 31 (reported) or physical 36 / printed 32 (constant-dollar). Definition stays on the identity-specific passage (store-only table footnote physical 37 / printed 33; total comparable MD&A physical 35 / printed 31). Observation value source remains `Form 10-K p. 27` / `27→31`. Unrelated strategy language and neighboring DTC disclosures still cannot satisfy store-only presentation, management-use or store-only population features.

| Identity | Presentation source | Management use | Definition | `definition_features.channel_population` | Scope / basis |
|---|---|---|---|---|---|
| `comparable_store_sales_growth` | physical 37 / printed 33 / `33→37` | physical 35 / printed 31 | physical 37 / printed 33 (table footnote) | `company_operated_stores` | `{channel: company_operated_stores}` / reported |
| `comparable_store_sales_growth_constant_dollar` | same table `33→37` | physical 36 / printed 32 | physical 37 / printed 33 | `company_operated_stores` | same channel / constant-dollar |
| `total_comparable_sales_growth` | same table `33→37` | physical 35 / printed 31 | physical 35 / printed 31 | `company_operated_stores_and_direct_to_consumer` | `{geography: global}` / reported |
| `total_comparable_sales_growth_constant_dollar` | same table `33→37` | physical 36 / printed 32 | physical 35 / printed 31 | `company_operated_stores_and_direct_to_consumer` | same geography / constant-dollar |

Store-only versus store-plus-DTC, reported versus constant-currency, and FY2022 versus later stores+e-commerce definitions remain distinct. FY2022 definitions are not equated with FY2023 e-commerce. Assurance and revision stay unresolved (`unknown` / `selection_limitation`). Annual-report placement was not treated as audited KPI assurance. The four false FY2022 presentation-absence findings remain removed (**0** presentation / `genuine_source_absence` failures).

This supersedes the prior Step 3.2.6 metadata-consistency claim that presentation was already bound to physical 37 / printed 33: passage bindings were correct, but `presentation_evidence.source` and store-only `definition_features` were not until this repair.

## Admission after ordinary build

`prepare_company_input` / `python -m bav build Lululemon` enriched permitted working copies only (`supporting/extracted/`). Protected PDFs, `benchmark/lululemon/extracted/` and authenticated baselines were not written.

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` |
| Documents / reported observations | 4 / **138** (135 original + 3 traced prior-period SPSF) |
| Focus CompSales + SPSF assessments | **31** (24 CompSales, 7 SPSF) |
| Period kind on focus items | **date** (all 31) |
| Definition equivalence (focus) | CompSales **18 equivalent**, **6 different**; SPSF **7 different** |
| FY2022 CompSales presentation | **4/4** `role=current`; source `Form 10-K p. 33` / `33→37`; `presentation_role` absent from unresolved; **0** presentation failures |
| FY2022 store-only features | **2/2** `company_operated_stores` (reported + constant-dollar); total comparable **2/2** stores-plus-DTC; identity `population` matches features |
| Pair assessments | **39** (36 historical, 3 same-period); **7 supported**, **32 unsupported** |
| SPSF pairs | **21** (14 unsupported, **7 supported**) |
| SPSF historical pairs supported | **5** (52-week included, average-ending levels) |
| FY2022-current / FY2023-current SPSF | `unsupported` for `definition_mismatch` (and recorded `period_mismatch`); **`calendar_mismatch` absent** |
| Failure attribution | pair-scoped **79**, occurrence-only **69**, canonical-selection **28** |
| SPSF level / historical comparison | **7/7 level admitted**; historical comparison **4 eligible** / **3 ineligible** |
| Group selection | selected **0**, deferred **28** |
| Group level / comparison / canonical | level **28 admitted**; comparison **3 eligible** (SPSF 2023-01-29, 2024-01-28, 2026-02-01) / **25 ineligible**; canonical **28 deferred** |
| Reconciliation | 37 incompatible; 6 singletons; 2 unresolved; revision links recognized **0** |
| StandardizedFinancials management histories | **0** (store-count observations remain 5) |
| Cause class on all 28 groups | **selection_limitation** |

All seven SPSF occurrence calendars, three traced priors and both FY2024 SPSF exclusion bindings (FY2024 physical 40 / printed 34; traced occurrence `cross_filing=true`) are unchanged. Comparison windows remain unbound on SPSF and are not copied onto priors. FY2022 calendar evidence remains FY2023 physical page 33 (`Fiscal 2023, 2022, and 2021 were each 52-week years.`).

Remaining FY2022 CompSales failures are occurrence-scoped **assurance** and **revision** (`selection_limitation`; pages 31, 33, 35–37) plus group-scoped **canonical_selection** (later-audited two-occurrence revision group with a documentary revision link). Those are selection-policy / unavailable-assurance gaps, not implementation defects or genuine source absence of the table or store-only definition. Canonical deferral alone does not establish source absence.

Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable (no sheets; Build Status / CLI `Source unavailable / not admitted`). Supported SPSF historical pairs do not enter `StandardizedFinancials` without canonical selection.

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged. Independent Python series matches prior anchors. Component-map SHA unchanged.

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Scope note still states total-company consolidated revenue includes revenue outside company-operated stores.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192536) |
| Trainer generated by ordinary build | **No** |
| Admission | `supporting/management_kpi_admission.json` (2300533; SHA-256 `9bf64b582b6f31baeb12db46bdb378fecb0c0509f478bba1e89ef91cc34c2538`) |
| Page resolution | `supporting/management_kpi_page_resolution.json` (126057; SHA-256 `d2f55444eb4dd7105149c7da3640b12592762307c7deb13a5727cdb6e8c6e188`) |
| Standardized | `supporting/standardized.json` (30504; SHA-256 `a1eea9608b0dc60eb5be0a70b47668dc3db6a4e4e4be56cf2bfc431d6447447f`) — unchanged vs Step 3.2.3 / 3.2.4 / 3.2.5 |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** (17 cells) |
| CLI / Build Status Unavailable | Comparable Sales Analysis — Source unavailable / not admitted (0); Sales per Square Foot Analysis — Source unavailable / not admitted (0) |

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no Trainer / CompSales / SPSF sheets. Deferred forecast tabs remain placeholders.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner. Exercise-framing hits: **0**.
- Semantic components **793**; sidecar **793**; embedded `_ComponentMap` **793**.
- Non-source identities **783/783** formulas match the map and have non-empty Notes.
- KPI source facts **10/10** populated.
- Yellow fill: **0**.
- Standardized export/reload: payload equality **True**.

BAV SHA-256: `fc6c072424f62cca90e025e436844d8a9a0c34e3a77881ed06643f423ea870ca` (192536). Rebuild packaging hash differs from the prior official file (`27cf81c5…`, also 192536); formula/input surface is the unchanged component-map and standardized payloads.  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906) — **unchanged** vs Step 3.2.3 / 3.2.4 / 3.2.5.  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69) — unchanged.

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47637 at derive; 53269 after Check recolor) |
| Trainer SHA-256 after Check | `a0e7e02b770112ba3ff7082267eb1b8a1a45059144481000f98dce2f40264110` |
| BAV / component-map / assumptions SHA-256 after derivation and Check | unchanged |
| Trainer-only sidecars | none |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| Check blank | 783 / 0 / 0 / 783 |
| Check correctly completed | 783 / 783 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 783 / 782 / 1 / 0 |

Check summaries did not disclose formulas. Official BAV hash unchanged after Check.

## Excel recalculation

Carried forward verified native Excel recovery `.git/autocycle/excel-verification-kzg9a_ex/result.json` (`status: VERIFIED`) and retained `saved-copy.xlsx`. Verification log: **50** independent references, **50** affected/dependency cells, `formulas_preserved: true`, sheets `Revenue per Store Analysis` and `Store Count Analysis`. Source SHA-256 of that recovery was the prior official BAV `27cf81c5…`.

This repair did not change formulas, inputs or dependencies: component-map SHA, standardized SHA, RPS series and 17 RPS mapped cells are unchanged, and CompSales/SPSF remain unactivated. Native recalculation was therefore not repeated. This **supersedes** the stale Excel-unavailable claim in the prior Step 3.2.6 record (and the carried-forward 3.2.4 / 3.2.5 unavailable narrative): cached-value verification for the unchanged RPS/store-count surface is VERIFIED at kzg9a_ex, not unavailable.

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

| Suite | Result |
|---|---|
| `test_management_kpi_enrichment.py` | **38 passed** (prior 34 retained; added presentation-source vs passage-binding agreement for all four FY2022 identities, store-only `definition_features` propagation into admission, store-only exclusion of DTC mentions, and negative neighboring-DTC / unrelated-strategy cases) |
| identity + admission + reconciliation + history + analysis + management-history | **1438 passed** |
| RPS + operating KPI facts + source availability + Lululemon + Fast Retailing | **457 passed** including `test_protected_artifacts_and_eight_extracts_unchanged` — **50/50** artifacts and **8/8** extracts |
| current build + operating KPI workbook/relationships/analysis + trainer + build CLI/contract | **216 passed** |
| filing CLI + protected-artifact test (explicit) | **12 passed** |

Protected extracts and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable. FY2022 presentation locators and store-only population features are now consistent with the table and definitions. Canonical selection still requires an audited reviser + documentary revision pair that the supplied MD&A does not provide (`selection_limitation`). Review must decide whether that policy remains the admission gate.
- Three SPSF groups are comparison-eligible from supported same-identity 52-week average-ending pairs, but those levels are not handed to the model without canonical selection. Do not read selection-route rejection as genuine source absence of SPSF values.
- FY2022 SPSF historical comparison stays ineligible: average-during-year vs later average-ending (`definition_mismatch` on the correct pairs).
- FY2024 current / FY2025 prior SPSF historical comparison stays ineligible: 53-week excluded vs 52-week included (`calendar_mismatch` on those pairs).
- FY2021 SPSF `$1,443` on FY2023 page 10 has no corpus fiscal-year-end, so it remains metadata only.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

This bounded repair completed FY2022 presentation-source and store-only population-metadata correction through ordinary enrichment, admission and build. It does not close the major Completion: CompSales/SPSF analysis are still not activated.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.


---

# Historical record — Step 3.2.6 (prior presentation-evidence repair)

The following is the prior Step 3.2.6 implementation record (plan `224ff1050e504f4eae9271e2bb018cb7`), preserved. Its claim that presentation was already bound to physical 37 / printed 33 described passage bindings only; `presentation_evidence.source` and store-only `definition_features` were still wrong. Its Excel-unavailable claim is superseded by the kzg9a_ex VERIFIED recovery carried forward above.

# RESULT.md — Step 3.2.6 Repair FY2022 presentation evidence and reassess KPI admission

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.6 — Repair FY2022 presentation evidence and reassess KPI admission  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `224ff1050e504f4eae9271e2bb018cb7`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `0ae4b104ebcec3b367dd3605dc7b3b6a8a450996625bc7582517a38fcbede843` (7571).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. FY2022 CompSales presentation is now bound to page 36 management-use / strategy-assessment statements and the page 37 current-period comparison table without requiring the literal phrase `we use comparable sales`. The four FY2022 `genuine_source_absence` / `presentation_role` adjudications were implementation defects and are removed. Canonical selection still requires a later-audited two-occurrence revision group with a documentary revision link. That remaining gate is a selection-policy / unavailable-assurance decision for Review. This bounded repair does not close the major Completion.

## FY2022 presentation-evidence repair

Ordinary enrichment now recognizes identity-specific management-use sentences and the current-period comparison-table intro. Phrase-match failure on `we use comparable sales` is not treated as missing source disclosure. Unrelated strategy language (`Opening new stores… is an important part of our growth strategy.`) still cannot satisfy presentation, assurance or revision.

| Identity | Management use | Current-period presentation | Population / currency |
|---|---|---|---|
| `comparable_store_sales_growth` (reported) | FY2022 physical 35 / printed 31: `We use comparable store sales to assess the performance of our existing stores…` | FY2022 physical 37 / printed 33 table header + intro: `The below changes in total comparable sales, comparable store sales, and direct to consumer net revenue…` | store-only / reported |
| `comparable_store_sales_growth_constant_dollar` | FY2022 physical 36 / printed 32: `Management uses these adjusted financial measures and constant currency metrics internally when reviewing and assessing financial performance.` | same page 37 table | store-only / constant-dollar |
| `total_comparable_sales_growth` (reported) | FY2022 physical 35 / printed 31: `We use total comparable sales to evaluate the performance of our business from an omni-channel perspective.` (page 36 `just one way of assessing` is recognized as an alternate strategy-assessment sentence) | same page 37 table | store+DTC / reported |
| `total_comparable_sales_growth_constant_dollar` | FY2022 physical 36 / printed 32: same management-use / constant-currency sentence | same page 37 table | store+DTC / constant-dollar |

Store-only versus store-plus-DTC, reported versus constant-currency, and FY2022 versus later stores+e-commerce definitions remain distinct. FY2022 definitions are not equated with FY2023 page 45. Assurance and revision stay unresolved (`unknown` / selection_limitation). Annual-report placement was not treated as audited KPI assurance.

Working-copy `presentation.role=current` with bound evidence is set for all four identities. Admission no longer records `presentation_role` on those occurrences. Generated `group_decisions` contain **0** `presentation` / `genuine_source_absence` failures (was 4 on FY2022). Pages searched on the four FY2022 groups now include 35–37 (constant-dollar 31, 33, 36, 37; reported 31, 33, 35, 37). Cross-filing FY2022 calendar remains FY2023 physical page 33.

## Admission after ordinary build

`prepare_company_input` / `python -m bav build Lululemon` enriched permitted working copies only (`supporting/extracted/`). Protected PDFs, `benchmark/lululemon/extracted/` and authenticated baselines were not written.

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` |
| Documents / reported observations | 4 / **138** (135 original + 3 traced prior-period SPSF) |
| Focus CompSales + SPSF assessments | **31** (24 CompSales, 7 SPSF) |
| Period kind on focus items | **date** (all 31) |
| Definition equivalence (focus) | CompSales **18 equivalent**, **6 different**; SPSF **7 different** |
| FY2022 CompSales presentation | **4/4** `role=current`; `presentation_role` absent from unresolved; **0** `genuine_source_absence` presentation failures |
| Pair assessments | **39** (36 historical, 3 same-period); **7 supported**, **32 unsupported** |
| SPSF pairs | **21** (14 unsupported, **7 supported**) |
| SPSF historical pairs supported | **5** (52-week included, average-ending levels) |
| FY2022-current / FY2023-current SPSF | `unsupported` for `definition_mismatch` (and recorded `period_mismatch`); **`calendar_mismatch` absent** |
| Failure attribution | pair-scoped **79**, occurrence-only **69** (was 73; four false presentation absences removed), canonical-selection **28** |
| SPSF level / historical comparison | **7/7 level admitted**; historical comparison **4 eligible** / **3 ineligible** |
| Group selection | selected **0**, deferred **28** |
| Group level / comparison / canonical | level **28 admitted**; comparison **3 eligible** (SPSF 2023-01-29, 2024-01-28, 2026-02-01) / **25 ineligible**; canonical **28 deferred** |
| Reconciliation | 37 incompatible; 6 singletons; 2 unresolved; revision links recognized **0** |
| StandardizedFinancials management histories | **0** (store-count observations remain 5) |
| Cause class on all 28 groups | **selection_limitation** |

All seven SPSF occurrence calendars, three traced priors and both FY2024 SPSF exclusion bindings (FY2024 physical 40 / printed 34; traced occurrence `cross_filing=true`) are unchanged. Comparison windows remain unbound on SPSF and are not copied onto priors. FY2022 calendar evidence remains FY2023 physical page 33.

Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable (no sheets; Build Status / CLI `Source unavailable / not admitted`). Supported SPSF historical pairs do not enter `StandardizedFinancials` without canonical selection. Selection-route rejection is not treated as genuine source absence. The prior claim that FY2022 CompSales lack documentary presentation evidence is corrected: the source discloses management use and current-period presentation; the earlier `genuine_source_absence` labels were phrase-match defects.

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged. Independent Python series matches prior anchors. Component-map SHA unchanged.

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Scope note still states total-company consolidated revenue includes revenue outside company-operated stores.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192536) |
| Trainer generated by ordinary build | **No** |
| Admission | `supporting/management_kpi_admission.json` (2297112; SHA-256 `eefa42235a3a96797caa8d83289260fe0cd324e57cb3ccd833c80450b7d9f30a`) |
| Page resolution | `supporting/management_kpi_page_resolution.json` (122850; SHA-256 `a27c3d43279a2c146be2a0e6b8ff0e373b0b095a93739b83d5265b9cab118f91`) |
| Standardized | `supporting/standardized.json` (30504; SHA-256 `a1eea9608b0dc60eb5be0a70b47668dc3db6a4e4e4be56cf2bfc431d6447447f`) — unchanged vs Step 3.2.3 / 3.2.4 / 3.2.5 |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** (17 cells) |
| CLI / Build Status Unavailable | Comparable Sales Analysis — Source unavailable / not admitted (0); Sales per Square Foot Analysis — Source unavailable / not admitted (0) |

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no Trainer / CompSales / SPSF sheets. Deferred forecast tabs remain placeholders.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner. Exercise-framing hits: **0**.
- Semantic components **793**; sidecar **793**; embedded `_ComponentMap` **793**.
- Non-source identities **783/783** formulas match the map and have non-empty Notes.
- KPI source facts **10/10** populated.
- Yellow fill: **0**.
- Standardized export/reload: payload equality **True**.

BAV SHA-256: `27cf81c5f6cc71fdeeae46d90825704a7ac4b2e1e90a346464e29ffa17d83e67` (192536).  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906) — **unchanged** vs Step 3.2.3 / 3.2.4 / 3.2.5.  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69) — unchanged.

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47637 at derive; 53269 after Check recolor) |
| Trainer SHA-256 after Check | `fc8a5b4f4f94da0f49fb54a7c3cc8cc82c145cfddda75058e4cd727d17eaed64` |
| BAV / component-map / assumptions SHA-256 after derivation and Check | unchanged |
| Trainer-only sidecars | none |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| Check blank | 783 / 0 / 0 / 783 |
| Check correctly completed | 783 / 783 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 783 / 782 / 1 / 0 |

Check summaries did not disclose formulas. Official BAV hash unchanged after Check.

## Excel recalculation

Microsoft Excel.app is present (16.113; process running). Measured cached-value rewrite was **unavailable** this attempt (same class as Step 3.2.4 / 3.2.5; carried forward unresolved):

- Copy: `/var/folders/…/lulu-kpi-excel.srxmk9ns/Lululemon_BAV_recalc.xlsx`.
- `osascript` `POSIX file … as alias` `open` / `calculate` / `save` / `close` failed with `Parameter error. (-50)`.
- HFS `open workbook workbook file name` returned no active workbook; `make new workbook` also failed with `-50`.
- `tell application "Microsoft Excel" to quit` was canceled (`User canceled. (-128)`); process 34315 remained.
- `open -a "Microsoft Excel"` on the copy left workbook count **0**.
- Copy remained 192536 bytes with the official BAV SHA-256 (`27cf81c5…`); no cached-value expansion occurred.

Command success, unchanged hashes and Python calculations alone do not satisfy this requirement. No CompSales/SPSF formulas were activated. Component-map SHA is unchanged, so RPS formula strings are the unchanged surface. Independent Python `compute_revenue_per_store_series` matches the five supported observations above (tolerance exact). Official BAV hash after the Excel attempt: unchanged.

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

| Suite | Result |
|---|---|
| `test_management_kpi_enrichment.py` | **34 passed** (prior 31 retained; added FY2022 identity-bound management-use / page-37 table, removal of false source-absence claims from the generated admission report, and negative unrelated-strategy language) |
| enrichment + identity + admission + reconciliation + history + analysis + management-history + RPS + protected extracts | **1479 passed** including `test_protected_artifacts_and_eight_extracts_unchanged` — **50/50** artifacts and **8/8** extracts |
| `test_current_build.py` `test_operating_kpi_workbook.py` `test_operating_kpi_relationships.py` `test_operating_kpi_analysis.py` `test_operating_kpi_facts.py` `test_source_availability.py` `test_lululemon_benchmark.py` `test_fast_retailing_benchmark.py` `test_trainer.py` `test_build_cli.py` `test_build_contract.py` | **667 passed** |

Combined affected command: **2146 passed**. Protected extracts and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable. FY2022 presentation evidence is now bound and the four false `genuine_source_absence` labels are removed. Canonical selection still requires an audited reviser + documentary revision pair that the supplied MD&A does not provide (`selection_limitation`). Review must decide whether that policy remains the admission gate.
- Three SPSF groups are comparison-eligible from supported same-identity 52-week average-ending pairs, but those levels are not handed to the model without canonical selection. Do not read selection-route rejection as genuine source absence of SPSF values.
- FY2022 SPSF historical comparison stays ineligible: average-during-year vs later average-ending (`definition_mismatch` on the correct pairs).
- FY2024 current / FY2025 prior SPSF historical comparison stays ineligible: 53-week excluded vs 52-week included (`calendar_mismatch` on those pairs).
- FY2021 SPSF `$1,443` on FY2023 page 10 has no corpus fiscal-year-end, so it remains metadata only.
- Excel cached-value rewrite remains unavailable (Steps 3.2.4, 3.2.5 and this attempt). Formula identity is evidenced by the unchanged component-map hash and independent Python RPS.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

This bounded repair completed FY2022 presentation-evidence recognition and admission reassessment. It does not close the major Completion: CompSales/SPSF analysis are still not activated.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.


---

# Historical record — Step 3.2.5

The following is the prior Step 3.2.5 implementation record, preserved.

# RESULT.md — Step 3.2.5 Repair pair-specific KPI assessments and exclusion evidence

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.5 — Repair pair-specific KPI assessments and exclusion evidence  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `c44b3a842ed0428ca79c4799e21063b2`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `29a81227e26d99e719a24d5793c1abc474ff72a3df35a6eb173069c79f59bfe4` (7974).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Pair assessments now identify the actual occurrence pair for each failure. FY2022-current/FY2023-current SPSF is a definition conflict (average-during-year vs average-ending), not a calendar mismatch: both have 52-week included evidence. FY2024 SPSF exclusion is bound to FY2024 physical page 40 / printed 34 and to the FY2025 traced FY2024 occurrence with explicit cross-filing provenance. Canonical selection still requires a later-audited two-occurrence revision group with a documentary revision link. That remaining gate is a selection-policy / unavailable-assurance decision for Review. This bounded repair does not close the major Completion.

## Pair-specific assessment repair

`assess_reported_observations` evaluates every same-identity pair independently and stores `pair_assessments` on each occurrence and in the assessments payload. `build_group_decisions` no longer attributes aggregated conflicts to `peers[0]`. Occurrence-only gaps (presentation, assurance, revision, local required-comparison reasons) stay locator-scoped. Canonical-selection failures stay group-scoped. Pair failures carry `comparison_pair` of the actual locators.

| Measurement | Result |
|---|---|
| Pair assessments | **39** (36 historical, 3 same-period); **7 supported**, **32 unsupported** |
| SPSF pairs | **21** (14 unsupported, **7 supported**) |
| SPSF historical pairs supported | **5** (52-week included, average-ending levels; period difference recorded, not treated as alignment failure) |
| FY2022-current / FY2023-current SPSF | `unsupported` for `definition_mismatch` only; **`calendar_mismatch` absent** (both 52-week included) |
| False calendar failure on that pair in group decisions | **0** |
| Failure attribution | pair-scoped **79**, occurrence-only **73**, canonical-selection **28** |

One incompatible peer no longer marks every comparison unsupported. FY2023-current vs FY2025-current SPSF is supported (both 52-week included, equivalent average-ending definitions). FY2023-current vs FY2024-current remains unsupported for `calendar_mismatch` (52 included vs 53 excluded). Occurrence-level `comparability` still records any conflict (existing 2-peer tests preserved). `historical_comparison` is eligible when any historical pair is supported under existing alignment rules; SPSF `missing_comparison` remains an occurrence-level fact and does not block level-to-level pair support.

## FY2024 SPSF exclusion evidence

Fiscal-year length alone does not set exclusion. Metric-exclusion passages are complete sentences bound to document, physical pages, printed pages, metric, period and cross-filing flag. Unrelated calendar text (`Fiscal 2024 was a 53-week year.`) does not satisfy exclusion.

| Occurrence | Exclusion | Source | Physical / printed | Cross-filing | Passage |
|---|---|---|---|---|---|
| FY2024 current SPSF (2025-02-02) | True | `LULU_FY2024_Annual_Report.pdf` | 40 / 34 | false | `In fiscal years with 53 weeks the 53rd week of net revenue is excluded from the calculation of sales per square foot.` |
| FY2025 traced FY2024 SPSF (2025-02-02) | True | `LULU_FY2024_Annual_Report.pdf` | 40 / 34 | **true** | same sentence |

All seven SPSF occurrence calendars are unchanged from Step 3.2.4, including FY2022 evidence from FY2023 physical page 33 and the three traced priors. Comparison windows remain unbound on SPSF and are not copied onto priors.

## Admission after ordinary build

`prepare_company_input` / `python -m bav build Lululemon` enriched permitted working copies only (`supporting/extracted/`). Protected PDFs, `benchmark/lululemon/extracted/` and authenticated baselines were not written.

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` |
| Documents / reported observations | 4 / **138** (135 original + 3 traced prior-period SPSF) |
| Focus CompSales + SPSF assessments | **31** (24 CompSales, 7 SPSF) |
| Period kind on focus items | **date** (all 31) |
| Definition equivalence (focus) | CompSales **18 equivalent**, **6 different**; SPSF **7 different** (FY2022 average-during-year vs later average-ending) |
| SPSF level / historical comparison | **7/7 level admitted**; historical comparison **4 eligible** (FY2023 prior, FY2023 current, FY2024 prior, FY2025 current) / **3 ineligible** (FY2022 current definition; FY2024 current and FY2025 prior 53-week) |
| Group selection | selected **0**, deferred **28** |
| Group level / comparison / canonical | level **28 admitted**; comparison **3 eligible** (SPSF 2023-01-29, 2024-01-28, 2026-02-01) / **25 ineligible**; canonical **28 deferred** |
| Reconciliation | 37 incompatible; 6 singletons; 2 unresolved; revision links recognized **0** |
| StandardizedFinancials management histories | **0** (store-count observations remain 5) |
| Cause class on all 28 groups | **selection_limitation** |

FY2022 CompSales still lack a documentary `We use comparable sales` presentation sentence (`genuine_source_absence` / `presentation_role` on four FY2022 identities; pages 31 and 33 searched). Population / geography / currency / denominator differences remain unaligned unless documentary equivalence supports them. Fail-closed audited-reviser selection was not bypassed. Annual-report placement was not treated as audited KPI assurance. Repeated prior-period SPSF levels were not treated as revisions.

Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable (no sheets; Build Status / CLI `Source unavailable / not admitted`). Supported SPSF historical pairs do not enter `StandardizedFinancials` without canonical selection. Selection-route rejection alone is not treated as genuine source absence.

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged. Independent Python series matches prior anchors. Component-map SHA unchanged.

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Scope note still states total-company consolidated revenue includes revenue outside company-operated stores.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192535) |
| Trainer generated by ordinary build | **No** |
| Admission | `supporting/management_kpi_admission.json` (2282212; SHA-256 `4d9088616b259fc90baf6b7e9a63e9da8dd5bba7313a493d835f6ab3257564ad`) |
| Page resolution | `supporting/management_kpi_page_resolution.json` (111622; SHA-256 `93eb0be2e84aa6c318b18d04d594a2d427bf9c84b6b0087391804303f4879417`) |
| Standardized | `supporting/standardized.json` (30504; SHA-256 `a1eea9608b0dc60eb5be0a70b47668dc3db6a4e4e4be56cf2bfc431d6447447f`) — unchanged vs Step 3.2.3 / 3.2.4 |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** (17 cells) |
| CLI / Build Status Unavailable | Comparable Sales Analysis — Source unavailable / not admitted (0); Sales per Square Foot Analysis — Source unavailable / not admitted (0) |

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no Trainer / CompSales / SPSF sheets. Deferred forecast tabs remain placeholders.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner. Exercise-framing hits: **0**.
- Semantic components **793**; sidecar **793**; embedded `_ComponentMap` **793**.
- Non-source identities **783/783** formulas match the map and have non-empty Notes.
- KPI source facts **10/10** populated.
- Yellow fill: **0**.
- Standardized export/reload: payload equality **True**.

BAV SHA-256: `805f0f55c9624a525898ef7b948595b4502749bc31690c7a96ea7489683d897a` (192535).  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906) — **unchanged** vs Step 3.2.3 / 3.2.4.  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69) — unchanged.

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47637 at derive; 53269 after Check recolor) |
| Trainer SHA-256 after Check | `c73f4cf8d2ef2a783074167f505a0919fbf4ba36603cb59876ddaacd36dac2fa` |
| BAV / component-map / assumptions SHA-256 after derivation and Check | unchanged |
| Trainer-only sidecars | none |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| Check blank | 783 / 0 / 0 / 783 |
| Check correctly completed | 783 / 783 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 783 / 782 / 1 / 0 |

Check summaries did not disclose formulas. Official BAV hash unchanged after Check.

## Excel recalculation

Microsoft Excel.app is present. Measured cached-value rewrite was **unavailable** this attempt (same class as Step 3.2.4; carried forward unresolved):

- `osascript` `open` / `calculate` / `save` / `close` on `/tmp/Lululemon_BAV_recalc_325.xlsx` failed with `Parameter error. (-50)`.
- Copy remained 192535 bytes with the official BAV SHA-256 (`805f0f55…`); no cached-value expansion occurred.

Command success alone is insufficient. No CompSales/SPSF formulas were activated. Component-map SHA is unchanged, so RPS formula strings are the unchanged surface. Independent Python `compute_revenue_per_store_series` matches the five supported observations above (tolerance exact). Official BAV hash after the Excel attempt: unchanged.

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

| Suite | Result |
|---|---|
| `test_management_kpi_enrichment.py` + identity + admission | **195 passed** (enrichment **31**; prior 25 retained; added pair attribution, peer-order independence, supported/unsupported coexistence, no false 52-week calendar mismatch, FY2024/traced exclusion bindings, calendar-text exclusion rejection) |
| reconciliation, history, analysis, operating-history, RPS, protected extracts | **1281 passed** including `test_protected_artifacts_and_eight_extracts_unchanged` — **50/50** artifacts and **8/8** extracts |
| `test_current_build.py` `test_operating_kpi_workbook.py` `test_operating_kpi_relationships.py` | **passed** after leftover `pair_outcomes` NameError removed |
| analysis, facts, source availability, Lululemon, Fast Retailing, trainer, build CLI/contract | **passed** |

Protected extracts and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable. Pair-specific assessments and FY2024 exclusion bindings are on the working copies and in `group_decisions` / `pair_assessments`. Canonical selection still requires an audited reviser + documentary revision pair that the supplied MD&A does not provide (`selection_limitation`). Review must decide whether that policy remains the admission gate.
- Three SPSF groups are comparison-eligible from supported same-identity 52-week average-ending pairs, but those levels are not handed to the model without canonical selection. Do not read selection-route rejection as genuine source absence of SPSF values.
- FY2022 SPSF historical comparison stays ineligible: average-during-year vs later average-ending (`definition_mismatch` on the correct pairs).
- FY2024 current / FY2025 prior SPSF historical comparison stays ineligible: 53-week excluded vs 52-week included (`calendar_mismatch` on those pairs). Exclusion itself is now individually bound.
- FY2022 CompSales lack a documentary presentation-role sentence (`genuine_source_absence`).
- FY2021 SPSF `$1,443` on FY2023 page 10 has no corpus fiscal-year-end, so it remains metadata only.
- Excel cached-value rewrite remains unavailable (Step 3.2.4 and this attempt). Formula identity is evidenced by the unchanged component-map hash and independent Python RPS.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

This bounded repair completed pair-specific assessment attribution and FY2024 exclusion bindings. It does not close the major Completion: CompSales/SPSF analysis are still not activated.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.


---

# Historical record — Step 3.2.4

The following is the prior Step 3.2.4 implementation record, preserved.

# RESULT.md — Step 3.2.4 Repair occurrence-specific KPI evidence and reassess admission

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.4 — Repair occurrence-specific KPI evidence and reassess admission  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `d0a5584c530a4b4fb91c4ab2d13d9550`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `c8f5cea2686e435b7f18c6ff451f11b201f45044b2d21285297a09d0692741cd` (7645).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Occurrence calendars, comparison windows and field passages now bind to the actual period and metric they describe. Same-identity SPSF levels were reassessed under existing comparison rules and do not align (FY2022 average-during-year vs later average-ending; 52- vs 53-week years), so historical comparison stays ineligible as documentary ambiguity rather than genuine source absence. Canonical selection still requires a later-audited two-occurrence revision group with a documentary revision link. That remaining gate is a selection-policy / unavailable-assurance decision for Review, not missing source values and not a reason to add a permissive fallback.

## Occurrence-specific repair

Fiscal-year metadata is resolved from each occurrence’s actual period, independently of the presenting filing. Fiscal-year length, metric-specific 53rd-week exclusion and comparison windows remain distinct fields. A 53-week year alone does not establish exclusion.

| Occurrence | Period | Weeks / 53rd-week | Calendar binding | Window |
|---|---|---|---|---|
| FY2022 current SPSF | 2023-01-29 | 52 / included | FY2023 p.33 cross-filing: `Fiscal 2023, 2022, and 2021 were each 52-week years.` | unresolved (none disclosed) |
| FY2023 prior SPSF | 2023-01-29 | 52 / included | FY2023 p.33 | unresolved |
| FY2023 current SPSF | 2024-01-28 | 52 / included | FY2023 p.33 | unresolved |
| FY2024 prior SPSF (FY2023 repeated) | 2024-01-28 | **52 / included** | FY2023 p.33 cross-filing (not the presenting FY2024 53-week year) | not copied from FY2024 |
| FY2024 current SPSF | 2025-02-02 | 53 / excluded | FY2024 p.32: `Fiscal 2024 was a 53-week year.` plus metric exclusion on p.40 | unresolved |
| FY2025 prior SPSF (FY2024 repeated) | 2025-02-02 | **53 / excluded** | FY2024 p.32 cross-filing (not the presenting FY2025 52-week year) | not copied from FY2025 |
| FY2025 current SPSF | 2026-02-01 | 52 / included | FY2025 p.33: `Fiscal 2025 was a 52-week year and fiscal 2024 was a 53-week year.` | unresolved |

All seven current and traced prior SPSF occurrences verified. Presentation roles, original observations and provenance were preserved; no duplicate model facts were added. FY2021 `$1,443` remains metadata only (no corpus fiscal-year-end).

Comparison windows bind only to the CompSales metric and the current/prior periods they describe. FY2024 CompSales retain an empty window (shift **rule** on p.40 is recorded separately; not treated as a completed window). FY2025 CompSales receive `52 weeks ended February 1 2026 vs 52 weeks ended February 2 2025 (not January 26 2025)` from the selected complete sentence, bound to its own page (physical 41 / printed 35), not a pooled 33+41 list and not copied onto SPSF or prior occurrences.

Date passages are complete year-end headers or `We refer to the fiscal year ended … as "YYYY"` clauses bound to printed page 1, not shortest fragments, store-count tables, or a later filing’s comparison window. Presentation recovers `We use sales per square foot … relative to their square footage.` (Identity-H heading junk stripped). Definition matching rejects `Non-comparable sales includes…`. FY2022 pages 36–37 store-only / store+DTC identities remain distinct from FY2023 page 45 stores+e-commerce.

## Admission after ordinary build

`prepare_company_input` enriched permitted working copies only (`supporting/extracted/`). Protected PDFs, `benchmark/lululemon/extracted/` and benchmark artifacts were not written.

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` |
| Documents / reported observations | 4 / **138** (135 original + 3 traced prior-period SPSF) |
| Focus CompSales + SPSF assessments | **31** (24 CompSales, 7 SPSF) |
| Period kind on focus items | **date** (all 31) |
| Physical page mapping on focus items | **31/31 PDF-validated** |
| Definition equivalence (focus) | CompSales **18 equivalent**, **6 different** (FY2022 store/DTC vs later e-commerce); SPSF **7 different** (average-during-year vs average-ending) |
| FY2024 global reported CompSales | `level_admission=admitted`, `historical_comparison=ineligible` (`calendar_mismatch`, `comparison_window_mismatch`) |
| SPSF level / historical comparison | **7/7 level admitted**; **7/7 historical comparison ineligible** — same-identity peers exist but existing calendar/definition rules do not permit comparison (`documentary_ambiguity` / `same_identity_levels_not_aligned`), not genuine source absence |
| Group selection | selected **0**, deferred **28** |
| Group level / comparison / canonical | level **28 admitted**; comparison **28 ineligible**; canonical **28 deferred** |
| Reconciliation | 37 incompatible; 6 singletons; 2 unresolved; revision links recognized **0** |
| StandardizedFinancials management histories | **0** (store-count observations remain 5) |
| Cause class on all 28 groups | **selection_limitation** — unresolved decision: later-audited two-occurrence revision group with a documentary revision link |
| Multi-failure reporting | **28/28** groups record selection **and** independent calendar / window / definition / presentation / assurance / revision / comparison failures |

Fail-closed audited-reviser selection was not bypassed. Annual-report placement was not treated as audited KPI assurance. Repeated prior-period SPSF levels were not treated as revisions.

FY2022 CompSales still lack a documentary `We use comparable sales` presentation sentence (`genuine_source_absence` / `presentation_role` on four FY2022 identities). That is source absence of the presentation phrase, not a selection-route substitute for admission.

### Per-group decisions

All 28 groups: `status=deferred`; `canonical_selection=deferred`; `level_eligibility=admitted`; `comparison_eligibility=ineligible`; cause `selection_limitation`.

| Period | Family | Notes |
|---|---|---|
| 2023-01-29 | CompSales | store-only and store+DTC; FY2022 presentation phrase absent; calendar from FY2023 p.33 |
| 2024-01-28 … 2026-02-01 | CompSales | stores+e-commerce regional/global × reported/constant-dollar; FY2025 window bound to p.41; FY2024 window unresolved |
| 2023-01-29 | SPSF | FY2022 current + FY2023 prior; 52 weeks; definition average-during-year vs average-ending |
| 2024-01-28 | SPSF | FY2023 current + FY2024 prior; both 52 weeks |
| 2025-02-02 | SPSF | FY2024 current + FY2025 prior; both 53 weeks excluded |
| 2026-02-01 | SPSF | FY2025 current; 52 weeks; singleton selection reason |

Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable (no sheets; Build Status / CLI `Source unavailable / not admitted`). Selection-route rejection alone does not satisfy Completion.

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged. Independent Python series matches prior anchors.

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Scope note still states total-company consolidated revenue includes revenue outside company-operated stores.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192536) |
| Trainer generated by ordinary build | **No** |
| Admission | `supporting/management_kpi_admission.json` (2080995; SHA-256 `4a94197709bb7c49566b4f99b5ad15eaf58d2f194cdb0ce52f01e5f6ed9799df`) |
| Page resolution | `supporting/management_kpi_page_resolution.json` (102918; SHA-256 `959a47563a642e7477a6a7575a9a4911577c60c50a245f872d0bbe2e9f96fa2c`) |
| Standardized | `supporting/standardized.json` (30504; SHA-256 `a1eea9608b0dc60eb5be0a70b47668dc3db6a4e4e4be56cf2bfc431d6447447f`) — unchanged vs Step 3.2.3 |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** (17 cells) |
| CLI / Build Status Unavailable | Comparable Sales Analysis — Source unavailable / not admitted (0); Sales per Square Foot Analysis — Source unavailable / not admitted (0) |

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no Trainer / CompSales / SPSF sheets.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner. Exercise-framing hits: **0**.
- Semantic components **793**; sidecar **793**; embedded `_ComponentMap` **793**.
- Non-source identities **783/783** formulas match the map and have non-empty Notes.
- KPI source facts **10/10** populated.
- Yellow fill: **0**.
- Standardized export/reload: payload equality **True**.

BAV SHA-256: `1c43b82e089a9bdca4e14890e4d9817abe0f48e5092caec71b07e7c621b9aa3f` (192536).  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906) — **unchanged** vs Step 3.2.3.  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69) — unchanged.

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47637 at derive; 53269 after Check recolor) |
| Trainer SHA-256 after Check | `3f43a18a9782b37e547dfeaa41ae02e4c529cdea10e043fa08c2659ca1aa0887` |
| BAV / component-map / assumptions SHA-256 after derivation and Check | unchanged |
| Trainer-only sidecars | none |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| Check blank | 783 / 0 / 0 / 783 |
| Check correctly completed | 783 / 783 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 783 / 782 / 1 / 0 |

Check summaries did not disclose formulas. Official BAV hash unchanged after Check.

## Excel recalculation

Microsoft Excel.app is present. Measured cached-value rewrite was **unavailable** this attempt:

- `open -a "Microsoft Excel"` then `calculate` / `save` / `close` exited **0**, but the copy remained 192536 bytes with the official BAV SHA-256 (`1c43b82e…`); no cached-value expansion occurred.
- A subsequent `POSIX file … as alias` `open` failed with `Parameter error. (-50)`.

No CompSales/SPSF formulas were activated. Component-map SHA is unchanged, so RPS formula strings are the unchanged surface. Independent Python `compute_revenue_per_store_series` matches the five supported observations above (tolerance exact). Official BAV hash after the Excel attempt: unchanged.

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m pytest -q core/tests/test_management_kpi_enrichment.py \
  core/tests/test_management_kpi_admission.py \
  core/tests/test_management_kpi_identity.py \
  core/tests/test_management_kpi_reconciliation.py \
  core/tests/test_management_kpi_history.py \
  core/tests/test_management_kpi_analysis.py \
  core/tests/test_operating_kpi_management_history.py \
  core/tests/test_revenue_per_store.py \
  core/tests/test_current_build.py \
  core/tests/test_normalization_candidate_admission.py::test_protected_artifacts_and_eight_extracts_unchanged \
  core/tests/test_operating_kpi_workbook.py \
  core/tests/test_operating_kpi_relationships.py \
  core/tests/test_operating_kpi_analysis.py \
  core/tests/test_operating_kpi_facts.py \
  core/tests/test_source_availability.py \
  core/tests/test_lululemon_benchmark.py \
  core/tests/test_fast_retailing_benchmark.py \
  core/tests/test_trainer.py \
  core/tests/test_build_cli.py \
  core/tests/test_build_contract.py
```

| Suite | Result |
|---|---|
| Combined affected command | **2137 passed** (25 enrichment + remainder) |
| `test_management_kpi_enrichment.py` | **25** — prior 20 retained; added prior-occurrence 52/53-week calendars, metric-specific exclusion, window leakage, complete multiline/cross-page passages and individual bindings, repaired evidence at assessment including contradictory eligibility |
| `test_protected_artifacts_and_eight_extracts_unchanged` | **passed** — **50/50** protected artifacts and **8/8** extracts |

Protected extracts and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable. Occurrence-specific calendars, windows, complete passages and individual document/page bindings are on the working copies and in `group_decisions`. Canonical selection still requires an audited reviser + documentary revision pair that the supplied MD&A does not provide (`selection_limitation`). Review must decide whether that policy remains the admission gate or whether additional audited source evidence is required.
- SPSF historical comparison stays ineligible: same-identity traced levels exist, but existing calendar/definition rules do not permit comparison (`documentary_ambiguity`). FY2022 SPSF uses average square footage during the year; later years use average ending square footage. FY2024 is a 53-week year with metric exclusion.
- FY2022 CompSales lack a documentary presentation-role sentence (`genuine_source_absence`).
- FY2021 SPSF `$1,443` on FY2023 page 10 has no corpus fiscal-year-end, so it remains metadata only.
- Excel cached-value rewrite was unavailable this attempt; formula identity is evidenced by the unchanged component-map hash and independent Python RPS.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

This bounded repair completed occurrence-specific evidence and admission reassessment. It does not close the major Completion: CompSales/SPSF analysis are still not activated.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.


---

# Historical record — Step 3.2.3

The following is the prior Step 3.2.3 implementation record, preserved.

# RESULT.md — Step 3.2.3 Repair documentary support and complete KPI admission decisions

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.3 — Repair documentary support and complete KPI admission decisions  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `4b547c9f1f5f466b86b6ba0027a7774d`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `c3a3c701accfbfa2ffce69ca42c89fbc031a28f632f1bbfa93786c1ee8cad779` (7494).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Documentary passages are now field-specific, FY2024/FY2025 SPSF values and complete date sentences are recovered, prior-period SPSF levels are traced occurrences, and eligibility is internally consistent. Canonical selection still requires a later-audited two-occurrence revision group with a documentary revision link. That remaining gate is a selection-policy / unavailable-assurance decision for Review, not missing source values and not a reason to add a permissive fallback.

## Documentary repair (supplied PDFs)

Ordinary enrichment now requires every supporting passage to be a complete sentence or table row that establishes the field. Any-needle fallbacks, TOC/introductory calendar text, social-impact “as of” dates, leftover Identity-H `$`/`%` marks, and unrelated numeric hits (September 2024, share repurchase) are rejected. Unsupported fields stay absent.

| Filing evidence used | Binding / treatment |
|---|---|
| FY2024/FY2025 physical page 10 | Recovered SPSF value sentences after dollar-mark normalization: `$1,574` / `$1,609` for 2024 and 2023; `$1,426` / `$1,574` for 2025 and 2024. |
| FY2023 physical page 10 | Three-value series `$1,609`, `$1,580`, `$1,443` for 2023 / 2022 / 2021. 2022 prior (`1580`, period `2023-01-29`) added as a traced `presentation.role=prior` occurrence. 2021 left in `prior_period_levels` only (no corpus fiscal-year-end). |
| FY2024 page 10 prior `1609` and FY2025 page 10 prior `1574` | Traced onto working copies with actual periods `2024-01-28` / `2025-02-02`. No revision link or assurance invented. |
| FY2022 / FY2023 covers | Date passages: `For the fiscal year ended January 29, 2023` / `January 28, 2024`. |
| FY2025 pages 33 and 40–41 | Complete comparison-window date: `52 weeks ended February 1 2026` vs `February 2 2025` (not `January 26 2025`). |
| FY2023 physical page 33 | Cross-filing FY2022 calendar: `Fiscal 2023, 2022, and 2021 were each 52-week years.` Fiscal-year length 52; metric 53rd-week exclusion remains a separate fact. |
| FY2024 page 40 | Shift **rule** recorded; comparison-window **label** empty until a completed window exists. Not treated as FY2024’s comparison window. |
| FY2022 pages 36–37 vs FY2023 page 45 | Definition features kept distinct (store-only / store+DTC / stores+e-commerce). Cross-identity definition assessment now records `different` instead of leaving equivalence empty. |

## Admission after ordinary build

`prepare_company_input` enriched permitted working copies only (`supporting/extracted/`). Protected PDFs, `benchmark/lululemon/extracted/` and benchmark artifacts were not written. Original observations, conflicts, superseded occurrences and deferred groups were preserved.

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` |
| Documents / reported observations | 4 / **138** (135 original + 3 traced prior-period SPSF) |
| Focus CompSales + SPSF assessments | **31** (24 CompSales, 7 SPSF) |
| Period kind on focus items | **date** (all 31) |
| Physical page mapping on focus items | **31/31 PDF-validated** |
| FY calendar weeks | FY2022 **52 included** (cross-filing p.33); FY2023 **52 included**; FY2024 **53 excluded**; FY2025 **52 included** |
| Definition equivalence (focus) | CompSales **18 equivalent**, **6 different** (FY2022 store/DTC vs later e-commerce); SPSF **7 different** |
| Contradictory eligible + calendar/window conflict | **0** |
| FY2024 global reported CompSales | `level_admission=admitted`, `historical_comparison=ineligible` (`calendar_mismatch`, `comparison_window_mismatch`) |
| SPSF level / historical comparison | **7/7 level admitted**; **7/7 historical comparison ineligible** (`missing_comparison` = genuine source absence; traced priors are levels, not comparisons) |
| Group selection | selected **0**, deferred **28** |
| Group level / comparison / canonical | level **28 admitted**; comparison **28 ineligible**; canonical **28 deferred** |
| Reconciliation | 38 incompatible pairs; 6 singletons; 1 unresolved pair; revision links recognized **0** |
| StandardizedFinancials management histories | **0** (store-count observations remain 5) |
| Cause class on all 28 groups | **selection_limitation** — unresolved decision: later-audited two-occurrence revision group with a documentary revision link |
| Multi-failure reporting | **28/28** groups record selection **and** independent calendar / window / definition / presentation / assurance / revision / comparison failures |

Documentary `level_eligibility=admitted` does not imply admission to `StandardizedFinancials`. Fail-closed audited-reviser selection was not bypassed. Annual-report placement was not treated as audited KPI assurance. Repeated prior-period SPSF levels were not treated as revisions.

### Traced SPSF occurrences

| Document | Period | Value | Role |
|---|---|---:|---|
| FY2022 | 2023-01-29 | 1580 | current |
| FY2023 | 2023-01-29 | 1580 | prior (FY2023 p.10) |
| FY2023 | 2024-01-28 | 1609 | current |
| FY2024 | 2024-01-28 | 1609 | prior (FY2024 p.10) |
| FY2024 | 2025-02-02 | 1574 | current |
| FY2025 | 2025-02-02 | 1574 | prior (FY2025 p.10) |
| FY2025 | 2026-02-01 | 1426 | current |

### Per-group decisions

All 28 groups: `status=deferred`; `canonical_selection=deferred`; `level_eligibility=admitted`; `comparison_eligibility=ineligible`; cause `selection_limitation`. Every group’s `remaining_failures` include `canonical_selection` plus occurrence-level assurance/revision (and presentation where the “We use …” sentence is absent). CompSales identities with peer years also record calendar and/or comparison-window conflicts. SPSF groups additionally record `historical_comparison` / `genuine_source_absence` and definition differences (average-during-year vs average-ending).

| Period | Family | Population / geography / basis | Pages searched |
|---|---|---|---|
| 2023-01-29 | CompSales | company-operated stores / — / constant-dollar, reported | 31, 33 |
| 2023-01-29 | CompSales | stores + DTC / global / constant-dollar, reported | 31, 33 |
| 2024-01-28 | CompSales | stores + e-commerce / Americas, China Mainland, Rest of World, global × reported/constant-dollar | 33, 39–40, 45 |
| 2025-02-02 | CompSales | stores + e-commerce / Americas, China Mainland, Rest of World, global × reported/constant-dollar | 32–33, 37–38, 40 |
| 2026-02-01 | CompSales | stores + e-commerce / Americas, China Mainland, Rest of World, global × reported/constant-dollar | 33–34, 38–41 |
| 2023-01-29 | SPSF | company-operated stores / reported (FY2022 current + FY2023 prior) | 7, 10, 33, 45 |
| 2024-01-28 | SPSF | company-operated stores / reported (FY2023 current + FY2024 prior) | 10, 32–33, 40, 45 |
| 2025-02-02 | SPSF | company-operated stores / reported (FY2024 current + FY2025 prior) | 10, 32–33, 40–41 |
| 2026-02-01 | SPSF | company-operated stores / reported (FY2025 current) | 10, 33, 40–41 |

Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable (no sheets; Build Status / CLI `Source unavailable / not admitted`). That is the selection-route limitation. The filings contain usable values, dates, definitions and calendar disclosures; they do not contain audited KPI assurance or a documentary revision pair.

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged.

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Independent anchors, standardized reload, and Excel-recalculated cells match (tolerance 1e-8). Scope note still states total-company consolidated revenue includes revenue outside company-operated stores.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192536) |
| Trainer generated by ordinary build | **No** |
| Admission | `supporting/management_kpi_admission.json` (2057642; SHA-256 `5b4b4e16718e43b8a9cfdc04afbfdac9e29e5defbb2cba535d259445638273d5`) |
| Page resolution | `supporting/management_kpi_page_resolution.json` (74288; SHA-256 `c656d27369c38fc41bb002f743c121954f4b8883c3d58f7ae76ea064fdc2b19a`) |
| Standardized | `supporting/standardized.json` (30504; SHA-256 `a1eea9608b0dc60eb5be0a70b47668dc3db6a4e4e4be56cf2bfc431d6447447f`) |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** (17 cells) |
| CLI / Build Status Unavailable | Comparable Sales Analysis — Source unavailable / not admitted (0); Sales per Square Foot Analysis — Source unavailable / not admitted (0) |

Build Status Operating KPIs: Store-count 5/4/4; CompSales unavailable 0; SPSF unavailable 0; Revenue per Store Analysis **Active / available 17**.

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no Trainer / CompSales / SPSF sheets.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner. Exercise-framing hits: **0**.
- Semantic components **793**; sidecar **793**; embedded `_ComponentMap` **793**.
- Non-source identities **783/783** formulas match the map and have non-empty Notes.
- KPI source facts **10/10** populated.
- Yellow fill: **0**.
- Standardized export/reload: payload equality **True**.

BAV SHA-256: `d95b91af40ad78006ba699efb666610c7bdb79576c2a28eb4f7804445f69edd3` (192536).  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906).  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69).

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47636 at derive; 53272 after Check recolor) |
| Trainer SHA-256 after Check | `8f0a8fafd27d47e61e89172bb1856a05fffdf5b720dfa00be23396904222944a` |
| BAV / component-map / assumptions SHA-256 after derivation and Check | unchanged |
| Trainer-only sidecars | none |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| Check blank | 783 / 0 / 0 / 783 |
| Check correctly completed | 783 / 783 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 783 / 782 / 1 / 0 |

Check summaries did not disclose formulas. Official BAV hash unchanged after Check.

## Excel recalculation

Microsoft Excel.app was available. A copy was opened, calculated twice, saved and closed. Official BAV hash not replaced.

| Measurement | Result |
|---|---|
| Command | `osascript` → Excel `open` / `calculate` / `save` / `close` on `/var/folders/.../lulu-kpi-excel.956xhvu5/Lululemon_BAV_recalc.xlsx` |
| Exit | **0** |
| Recalc file | 224941 bytes; SHA-256 `e7ed3b4f0425203eb7d8c1b7e1392313faf18e98966c28de35ee4ec50a6c0404` |
| Formula strings vs published BAV | **1777** unchanged, **0** diffs |
| Period-end / average / change / growth vs independent anchors | **all match** |
| Excel error values on RPS cells | **none** |
| Official BAV hash after Excel | unchanged `d95b91af40ad78006ba699efb666610c7bdb79576c2a28eb4f7804445f69edd3` |

No CompSales/SPSF formulas were activated. Measured Excel evidence is for the unchanged Revenue per Store surface and its dependencies.

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m pytest -q core/tests/test_management_kpi_enrichment.py \
  core/tests/test_management_kpi_admission.py \
  core/tests/test_management_kpi_identity.py \
  core/tests/test_management_kpi_reconciliation.py \
  core/tests/test_management_kpi_history.py \
  core/tests/test_management_kpi_analysis.py \
  core/tests/test_operating_kpi_management_history.py \
  core/tests/test_revenue_per_store.py \
  core/tests/test_current_build.py \
  core/tests/test_normalization_candidate_admission.py::test_protected_artifacts_and_eight_extracts_unchanged \
  core/tests/test_operating_kpi_workbook.py \
  core/tests/test_operating_kpi_relationships.py \
  core/tests/test_operating_kpi_analysis.py \
  core/tests/test_operating_kpi_facts.py \
  core/tests/test_source_availability.py \
  core/tests/test_lululemon_benchmark.py \
  core/tests/test_fast_retailing_benchmark.py \
  core/tests/test_trainer.py \
  core/tests/test_build_cli.py \
  core/tests/test_build_contract.py
```

| Suite | Result |
|---|---|
| Combined affected command | **2132 passed** (20 enrichment + 394 admission/identity/reconciliation/history + 1718 remaining) |
| After final date-passage tighten | enrichment **20 passed**; admission + identity **164 passed**; ordinary rebuild exit **0** |
| `test_management_kpi_enrichment.py` | **20** — prior 14 retained; added missing SPSF value support, complete date passages, unrelated-match rejection, traced prior-period occurrences, complete multi-failure reporting, contradictory eligibility |
| `test_protected_artifacts_and_eight_extracts_unchanged` | **passed** — **50/50** protected artifacts and **8/8** extracts |
| Fast Retailing practice count | **577** |

Protected extracts and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable. Values, definitions, dates, calendar weeks, comparison windows, PDF bindings and traced prior-period SPSF levels are on the working copies and in `group_decisions`. Canonical selection still requires an audited reviser + documentary revision pair that the supplied MD&A does not provide (`selection_limitation`). Review must decide whether that policy remains the admission gate or whether additional audited source evidence is required.
- SPSF historical comparison stays ineligible: traced repeats are levels, not disclosed comparison observations (`genuine_source_absence`).
- FY2021 SPSF `$1,443` on FY2023 page 10 has no corpus fiscal-year-end, so it remains metadata only.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

This bounded repair completed documentary support and admission accounting. It does not close the major Completion: CompSales/SPSF analysis are still not activated.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

---

# Historical record — Step 3.2.2

The following is the prior Step 3.2.2 implementation record, preserved.

# RESULT.md — Step 3.2.2 Complete documentary KPI admission assessment

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.2 — Complete documentary KPI admission assessment  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `6b19f101e21343a5a9506f60164c02ee`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `12726e564dc52349d36cc5a8bc90634a2eae06d3c27569a95fb9a34895b8c092` (7178).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Documentary binding and per-group assessment now consume PDF-validated pages and field-specific passages. Canonical selection still requires a later-audited two-occurrence revision group. That remaining gate is a selection limitation, not missing source values and not a reason to bypass the route.

## Documentary assessment (supplied PDFs)

Ordinary enrichment inspected the supplied FY2022–FY2025 PDFs, bound physical pages onto the 28 focus observations, and replaced page-prefix snippets with field-specific supporting passages (value, definition, calendar). Bindings were re-validated against the PDFs; extract-asserted `physical_page_mapping` remains rejected.

| Filing evidence used | Binding / treatment |
|---|---|
| FY2023 physical page 33 | Explicit “Fiscal 2023, 2022, and 2021 were each 52-week years.” Cross-filing provenance on FY2022 working-copy calendar (`source_file=LULU_FY2023_Annual_Report.pdf`, `physical_page=33`, `cross_filing=true`). FY2022 fiscal-year length = 52; metric 53rd-week exclusion remains a separate fact. |
| FY2024 physical page 40 | Subsequent-year one-week-shift **rule** recorded as `subsequent_year_one_week_shift_rule`. Year length 53; CompSales/SPSF exclude the 53rd week. Not treated as a completed comparison window. |
| FY2025 physical pages 33 and 40–41 | Actual comparison window preserved: `52 weeks ended February 1 2026 vs 52 weeks ended February 2 2025 (not January 26 2025)`. Comparability is not inferred from matching 52-week lengths. |
| FY2022 physical pages 36–37 vs FY2023 physical page 45 | Definition features kept distinct: FY2022 comparable-store and total-comparable (store + DTC) are not aligned to later stores+e-commerce. Reported vs constant-dollar and geographic series remain separate. |
| FY2023 physical page 10 (and later p.10 repeats) | SPSF prior-period **levels** recorded with their actual periods and presentation roles. Company-operated revenue / average ending square-footage scope preserved. No comparison observation or revision link invented. |

Fiscal-year length, metric-specific 53rd-week exclusion, and comparison-window shifts stay distinct fields.

## Admission after ordinary build

`prepare_company_input` enriched permitted working copies only (`supporting/extracted/`). Protected PDFs, `benchmark/lululemon/extracted/` and benchmark artifacts were not written. Original observations, conflicts, superseded occurrences and deferred groups were preserved.

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` |
| Documents / reported observations | 4 / 135 |
| Focus CompSales + SPSF | **28** (24 CompSales, 4 SPSF) |
| Period kind on focus items | **date** (2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01) |
| Physical page mapping on focus items | **28/28 PDF-validated** (none `unresolved`) |
| FY calendar weeks on focus items | FY2022 **52 included** (cross-filing); FY2023 **52 included**; FY2024 **53 excluded**; FY2025 **52 included** |
| Definition equivalence (focus) | CompSales **18 equivalent / not_comparable**, **6 empty / unresolved**; SPSF **4 different / not_comparable** |
| SPSF level / historical comparison | **4/4 level admitted**; **4/4 historical comparison ineligible** (`missing_comparison` = genuine source absence) |
| Group selection | selected **0**, deferred **28** |
| Reconciliation | 24 incompatible pairs; 6 singletons; revision links recognized **0** |
| StandardizedFinancials management histories | **0** (store-count observations remain 5) |
| Cause class on all 28 groups | **selection_limitation** — unresolved decision: later-audited two-occurrence revision group with a documentary revision link |

Annual-report placement was not treated as audited KPI assurance. Repeated prior-period SPSF levels were not treated as revision evidence. Fail-closed audited-reviser selection was not bypassed.

### Per-group decisions

All 28 groups: status `deferred`; cause `selection_limitation`; requirements typically satisfied: `period_date`, `calendar_week_adjustment`, `calendar_reporting_basis`, `definition`, `physical_page_mapping`, `level_admission`. Unresolved selection decision on every group: later-audited two-occurrence revision group with a documentary revision link. SPSF groups additionally record `historical_comparison` / `genuine_source_absence` (need a disclosed historical SPSF comparison observation with its actual window).

| Period | Family | Population / geography / basis | Pages searched |
|---|---|---|---|
| 2023-01-29 | CompSales | company-operated stores / — / constant-dollar | 31, 33 |
| 2023-01-29 | CompSales | company-operated stores / — / reported | 31, 33 |
| 2023-01-29 | CompSales | stores + DTC / global / constant-dollar | 31, 33 |
| 2023-01-29 | CompSales | stores + DTC / global / reported | 31, 33 |
| 2024-01-28 | CompSales | stores + e-commerce / Americas, China Mainland, Rest of World, global × reported/constant-dollar | 33, 39–40, 45 |
| 2025-02-02 | CompSales | stores + e-commerce / Americas, China Mainland, Rest of World, global × reported/constant-dollar | 32–33, 37–38, 40 |
| 2026-02-01 | CompSales | stores + e-commerce / Americas, China Mainland, Rest of World, global × reported/constant-dollar | 33–34, 38–41 |
| 2023-01-29 | SPSF | company-operated stores / reported | 7, 33 |
| 2024-01-28 | SPSF | company-operated stores / reported | 10, 33, 45 |
| 2025-02-02 | SPSF | company-operated stores / reported | 10, 32, 40 |
| 2026-02-01 | SPSF | company-operated stores / reported | 10, 33, 40, 41 |

Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable (no sheets; Build Status / CLI `Source unavailable / not admitted`). That is the selection-route limitation, not a finding that the filings lack usable values, dates, definitions or calendar disclosures.

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged.

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Independent anchors, standardized reload, and Excel-recalculated cells match (tolerance 1e-8). Scope note still states total-company consolidated revenue includes revenue outside company-operated stores.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192536) |
| Trainer generated by ordinary build | **No** |
| Admission | `supporting/management_kpi_admission.json` (1780003; SHA-256 `f7c31d31a6dc531a0934ccc2f5b177d896e5e3d16ba19ed580f18997263cbf89`) |
| Page resolution | `supporting/management_kpi_page_resolution.json` (76272; SHA-256 `22f4766db601156d0e4af46ee60cdc73492f08942db7d7832d9cb6d20cb9ba10`) |
| Standardized | `supporting/standardized.json` (30504; SHA-256 `a1eea9608b0dc60eb5be0a70b47668dc3db6a4e4e4be56cf2bfc431d6447447f`) |
| CLI / Build Status Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** (17 cells) |
| CLI / Build Status Unavailable | Comparable Sales Analysis — Source unavailable / not admitted (0); Sales per Square Foot Analysis — Source unavailable / not admitted (0) |

Build Status Operating KPIs: Store-count 5/4/4; Revenue/store growth comparison 4; CompSales unavailable 0; SPSF unavailable 0; Revenue per Store Analysis **Active / available 17**.

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no Trainer / CompSales / SPSF sheets.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner. Exercise-framing hits: **0**.
- Semantic components **793**; sidecar **793**; embedded `_ComponentMap` **793**.
- Non-source identities **783/783** formulas match the map and have non-empty Notes.
- KPI source facts **10/10** populated.
- Yellow fill: **0**.
- Standardized export/reload: payload equality **True**.

BAV SHA-256: `b6bcc06831ab6a5e1555a254dd4cb3d5a6a49e8ebe7d979599d9a71c1dd20289` (192536).  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906).  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69).

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47639 at derive; 47951 after Check recolor) |
| Trainer SHA-256 after Check | `8322eb3b57bb9da6fe3ae7f39e02aa8a241dbd3c4b970f53c3f9c1581260d54f` |
| BAV / component-map / assumptions SHA-256 after derivation and Check | unchanged |
| Trainer-only sidecars | none |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| `python -m bav check Lululemon` (blank) | 783 / 0 / 0 / 783 |
| Check correctly completed | 783 / 783 / 0 / 0 |
| Check one incorrect RPS practice (`Revenue per Store Analysis!B9` = 0) | 783 / 782 / 1 / 0 |

Check summaries did not disclose formulas. Official BAV hash unchanged after Check.

## Excel recalculation

Microsoft Excel.app was available. A copy was opened, calculated twice, saved and closed. Official BAV hash not replaced.

| Measurement | Result |
|---|---|
| Command | `osascript` → Excel `open` / `calculate` / `save` / `close` on `/var/folders/.../lulu-kpi-excel.jfmjfae4/Lululemon_BAV_recalc.xlsx` |
| Exit | **0** |
| Recalc file | 224974 bytes; SHA-256 `db18163db99f6368d627f44a50dc9023467a1aafdd476399cc6b6cf0f6457861` |
| Formula strings vs published BAV | **1777** unchanged, **0** diffs |
| Period-end / average / change / growth vs independent anchors | **all match** |
| Excel error values on RPS cells | **none** |
| Official BAV hash after Excel | unchanged `b6bcc06831ab6a5e1555a254dd4cb3d5a6a49e8ebe7d979599d9a71c1dd20289` |

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m pytest -q core/tests/test_management_kpi_enrichment.py \
  core/tests/test_management_kpi_admission.py \
  core/tests/test_management_kpi_identity.py \
  core/tests/test_management_kpi_reconciliation.py \
  core/tests/test_management_kpi_history.py \
  core/tests/test_management_kpi_analysis.py \
  core/tests/test_operating_kpi_management_history.py \
  core/tests/test_revenue_per_store.py \
  core/tests/test_current_build.py \
  core/tests/test_normalization_candidate_admission.py::test_protected_artifacts_and_eight_extracts_unchanged \
  core/tests/test_operating_kpi_workbook.py \
  core/tests/test_operating_kpi_relationships.py \
  core/tests/test_operating_kpi_analysis.py \
  core/tests/test_operating_kpi_facts.py \
  core/tests/test_source_availability.py \
  core/tests/test_lululemon_benchmark.py \
  core/tests/test_fast_retailing_benchmark.py \
  core/tests/test_trainer.py \
  core/tests/test_build_cli.py \
  core/tests/test_build_contract.py
```

| Suite | Result |
|---|---|
| Combined command | **2126 passed** in 256.82s |
| `test_management_kpi_enrichment.py` | **14** — protected-path refusal; PDF-consumed bindings; rejection of unsupported and extract-asserted pages; FY2022 calendar from FY2023 p.33; shifted windows not inferred; definition equivalence vs genuine differences; SPSF level vs comparison; fail-closed selection |
| admission / identity / reconciliation / history / analysis | **413** |
| operating-KPI management history / workbook / relationships / analysis / facts / source availability / RPS / current_build | **1246** |
| `test_protected_artifacts_and_eight_extracts_unchanged` | **passed** — **50/50** protected artifacts and **8/8** extracts |
| `test_lululemon_benchmark.py` / `test_fast_retailing_benchmark.py` | **36** / **293** |
| `test_trainer.py` / `test_build_cli.py` / `test_build_contract.py` | **58** / **32** / **23** |

Fast Retailing practice count remains **577**. Protected extracts and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable. Values, definitions, dates, calendar weeks, comparison windows and PDF page bindings are on the working copies and in `group_decisions`; canonical selection still requires an audited reviser + documentary revision pair that the supplied MD&A does not provide (`selection_limitation`).
- SPSF historical comparison stays ineligible without a disclosed comparison observation (`genuine_source_absence`; pages searched recorded on the four SPSF groups).
- Six CompSales focus items still have empty `definition_equivalence` / unresolved comparability; original definition texts were not overwritten.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

---

# Historical record — Step 3.2.1

The following is the prior Step 3.2.1 implementation record, preserved.

# RESULT.md — Step 3.2.1 Complete real-source Lululemon KPI production acceptance

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2.1 — Complete real-source Lululemon KPI production acceptance  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `1f37a5b846a647c38b92fa35667ecc50`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `016f4c9a7ca311d9974b90be5baa048fb7df76f73eb45dc52a821e17f07b7af8` (6533).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change. Activation of Comparable Sales / SPSF analysis still requires a later-audited two-occurrence revision group. The supplied MD&A pages do not provide that. That is a documentary / selection-gate gap, not an implementation defect to bypass.

## Documentary inspection (supplied PDFs)

Printed Form 10-K page numbers were resolved from each PDF footer, not assumed. FY2024 physical page 40 is printed page 34; its extract `fiscal_year_end` is `2025-02-02`.

| Filing | Physical pages searched | Evidence found |
|---|---|---|
| FY2024 `LULU_FY2024_Annual_Report.pdf` | 7–11, 32–35, 40–41, 48 | PHYS 32 / printed 26: fiscal year ends Sunday closest to 31 January; FY2024 is 53 weeks; CompSales exclude the 53rd week. PHYS 33 / printed 27: CompSales +4% excluding the 53rd week. PHYS 40 / printed 34: stores+e-commerce CompSales definition; 53rd-week exclusion; following-year one-week shift; SPSF = company-operated revenue / average ending square footage; 53rd week excluded from SPSF. PHYS 10 / printed 4: SPSF $1,574 (2024) and $1,609 (2023). PHYS 48: auditor report is on the financial statements, not MD&A KPIs. |
| FY2025 | 10, 33, 40–41 | PHYS 33: FY2025 is 52 weeks, FY2024 was 53; CompSales compared on a one-week shift (52 weeks ended 1 Feb 2026 vs 2 Feb 2025, not 26 Jan 2025). PHYS 40–41: same stores+e-commerce definition; total CompSales 2%; regional reported / constant-dollar table. PHYS 10: SPSF 1426. |
| FY2023 | 10, 33, 45 | PHYS 33: FY2023, 2022 and 2021 were each 52 weeks; FY2024 will be 53. PHYS 45: stores+e-commerce CompSales and SPSF average-ending-square-footage definitions; 53rd-week rule. PHYS 10: SPSF $1,609 / $1,580 / $1,443 for 2023 / 2022 / 2021. |
| FY2022 | 8, 31, 36–37 | PHYS 31 / printed 27: total comparable sales 25% / 28% constant-dollar. PHYS 37 / printed 33: comparable **store** sales 16% / 19%; total comparable = store + DTC. PHYS 36: 53rd-week exclusion / following-year shift language. This is not the later stores+e-commerce CompSales identity. |

Missing extract metadata (FY labels, empty calendar-week, unresolved physical pages) is not a missing-source finding. The dates, 52/53-week treatment, definitions and values are on the pages above.

## Working-copy enrichment (ordinary build)

`prepare_company_input` now enriches permitted working copies only (`supporting/extracted/`) via `core/ingestion/management_kpi_enrichment.py`. Protected PDFs, `benchmark/lululemon/extracted/` and benchmark artifacts are not written.

For supported CompSales/SPSF observations the working copy receives, when evidenced:

- `period` FY202n → document `fiscal_year_end` (original label preserved as `original_period_label`)
- `report.reporting_basis` → disclosed fiscal-calendar sentence (original preserved as `original_reporting_basis`)
- `qualifiers.excludes_53rd_week` when that year’s PDF states 52- or 53-week status
- `presentation.role=current` with bound page evidence
- page-resolution sidecar `supporting/management_kpi_page_resolution.json`

Not invented: audited assurance, revision links, SPSF comparison observations, FY2022 52-week qualifier (that year’s PDF does not name FY2022 as 52-week), physical_page_mapping inside extract JSON (extracts still cannot certify a PDF page).

FY2024 printed 34 → physical 40 and FY2024 `fiscal_year_end` `2025-02-02` are in the sidecar. Observation `physical_page_mapping` remains `unresolved` on the admission payload by existing fail-closed parse rules; the sidecar is the PDF-resolved audit record.

## Admission decisions after enrichment

Ordinary build admission (`admit_periods=(2022-01-30,)`):

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` |
| Documents / reported observations | 4 / 135 |
| Focus supported CompSales + SPSF | **28** |
| Period kind on focus items | **date** (`2023-01-29`, `2024-01-28`, `2025-02-02`, `2026-02-01`) |
| Company CompSales calendar week | FY2023 empty on own PDF; FY2023 included; FY2024 excluded; FY2025 included |
| Group selection | selected **0**, deferred **28** |
| StandardizedFinancials management histories | **0** |
| History handoff | `0 evidenced selected occurrence(s)`; 28 deferred groups remain audit-only |

Identities kept distinct: FY2022 comparable-store and total-comparable (DTC) are not collapsed into later stores+e-commerce CompSales. Reported vs constant-dollar and regional series remain separate. SPSF stays a company-operated / average-ending-square-footage **level**; no comparison observation was manufactured (`missing_comparison` remains on SPSF historical comparison).

Exact remaining admission requirement for model handoff: a complete two-occurrence same-period group with a documentary revision link and an **audited** reviser. The supplied MD&A pages do not state that management CompSales/SPSF are audited, and they do not restate a prior-period KPI with revision evidence. Inferring audit from appearance in an annual report is disallowed. This is a source / selection-policy gap, not an extraction-code defect.

Comparable Sales Analysis and Sales per Square Foot Analysis therefore remain unavailable (no sheets; Build Status / CLI `Source unavailable / not admitted`). Partial availability is disclosed.

## Revenue per Store (preserved)

Five period-end observations, distinct average-store denominators, period alignment, USD thousands, missing/zero-input behavior and total-company-revenue scope limitation are unchanged.

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Excel-recalculated cells match these anchors. No Excel errors.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192535 bytes) |
| Trainer generated by ordinary build | **No** |
| New supporting audit | `supporting/management_kpi_page_resolution.json` (30410; SHA-256 `b9e27a058afbf005e929c314a763148849a07dac61b41235887ca0f267dcbbf9`) |
| CLI Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** |
| CLI Unavailable | Comparable Sales Analysis — Source unavailable / not admitted; Sales per Square Foot Analysis — Source unavailable / not admitted |

Build Status Operating KPIs: Store-count 5/4/4; Revenue/store growth comparison 4; CompSales unavailable 0; SPSF unavailable 0; Revenue per Store Analysis **Active / available 17**.

## BAV-only verification

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no Trainer / CompSales / SPSF sheets.
- Visible cells/Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner.
- Semantic components **793**; sidecar **793**; embedded `_ComponentMap` **793**.
- Non-source identities **783/783** formulas match the map and have non-empty Notes.
- KPI source facts **10/10** populated.
- Yellow fill: **0**.

BAV SHA-256: `7872e99c6a172a6e8911eab9afe6901be00c478b43dc963f480d6b04a9ed31c0` (192535).  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906).  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69).

## Explicit Trainer derivation

`derive_trainer_workbook` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47636) |
| BAV / component-map / assumptions SHA-256 after derivation | unchanged |
| Trainer-only sidecars | none |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| Check blank | 783 / 0 / 0 / 783 |
| Check correctly completed | 783 / 783 / 0 / 0 |
| Check one incorrect RPS practice | 783 / 782 / 1 / 0 |

Check summaries did not disclose formulas. Official BAV hash unchanged after Check.

## Excel recalculation

Microsoft Excel.app was available. A copy was opened, calculated twice, saved and closed. Official BAV hash not replaced.

| Measurement | Result |
|---|---|
| Command | `osascript` → Excel `open` / `calculate` / `save` / `close` on `/var/folders/.../lulu-kpi-excel.atvf9ib3/Lululemon_BAV_recalc.xlsx` |
| Exit | **0** |
| Recalc file | 224952 bytes; SHA-256 `c9ac2c335007da2efc0431b3f3e72530e35e531a7ef39902ccc40a5b925c9940` |
| Formula strings vs published BAV | **984** unchanged, **0** diffs |
| Period-end / average / change / growth vs independent anchors | **all match** |
| Excel error values on RPS cells | **none** |
| Official BAV hash after Excel | unchanged `7872e99c6a172a6e8911eab9afe6901be00c478b43dc963f480d6b04a9ed31c0` |

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

| Suite | Result |
|---|---|
| `core/tests/test_management_kpi_enrichment.py` | **7 passed** (protected-path refusal; FY2024 p.34→40; period/calendar enrichment; fail-closed unaudited/no-revision; store vs total vs later CompSales identities; ordinary `prepare_company_input` + RPS anchors) |
| `test_management_kpi_admission.py` `test_management_kpi_identity.py` `test_revenue_per_store.py` `test_current_build.py` `test_protected_artifacts_and_eight_extracts_unchanged` | **191 passed** (includes **50/50** protected artifacts and **8/8** extracts) |
| `test_management_kpi_reconciliation.py` `test_management_kpi_history.py` `test_management_kpi_analysis.py` `test_operating_kpi_management_history.py` plus operating-KPI workbook/analysis/relationships/facts and source availability | **1486 passed** |
| `test_lululemon_benchmark.py` `test_fast_retailing_benchmark.py` `test_trainer.py` `test_build_cli.py` `test_build_contract.py` | **441 passed** plus `test_no_lulu_specific_production_branch` **passed** after removing issuer tokens from production code |

Fast Retailing practice count remains **577**. Protected extracts and authenticated baselines were not replaced.

## Remaining gaps toward Completion

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable on the ordinary build. Values, definitions, fiscal dates and 52/53-week treatment are on the inspected pages and now on working copies; canonical selection still requires an audited reviser + documentary revision pair that the supplied MD&A does not provide.
- FY2022 own PDF does not state FY2022 as a 52-week year, so that year’s calendar-week qualifier stays empty.
- Year-specific definition texts were not overwritten; peer `definition_mismatch` can remain even after period/basis enrichment.
- SPSF historical comparison stays ineligible without a disclosed comparison observation.
- Disclosure-led driver testing and strategy interpretation remain subsequent Session work.
- Earlier deferred normalization / workflow commitments remain deferred.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

---

# Historical record — Step 3.2

The following is the prior Step 3.2 implementation record, preserved.

# RESULT.md — Step 3.2 Complete real-source Lululemon KPI production acceptance

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 3.2 — Complete real-source Lululemon KPI production acceptance  
**Work:** `6743e8167c864555b33c54efb3c41328`  
**Plan:** `ad722ab097464605aea2eb97d0d0f911`  
**Finding:** Complete real-source Lululemon KPI production acceptance  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `28089b961e72b3058d043efb9008e42c7b144d15cc3e3e2837174acb2f5eaf70` (26043).  
SESSION SHA-256 `b37e5b0348b8d6f2210a51f8307511842fcc862ede5059c7ca76687bb4bad4aa` (4944).  
IMPLEMENTATION SHA-256 `3b0dec7a45f97592c8a919dba35aedc98e3af40cfae9b2a0ef55ad58c83d765d` (6020).  
No commit / push / sync / checkpoint / branch change.

## Required plan change

No required plan change.

## Source-admission decisions (Comparable Sales / SPSF)

Ordinary supplied extracts were inspected through extraction → validation → reconciliation → model admission. Values exist in the extracts. Fail-closed admission did **not** select them. This is missing documentary evidence, not an extraction/admission code defect. Protected extracts were not rewritten.

Documents searched (working copies only; `benchmark/lululemon/extracted/` left unchanged):

| Document | Source PDF | Focus observations found |
|---|---|---|
| `LULU_FY2022_management_kpis.json` | `LULU_FY2022_Annual_Report.pdf` | Comparable store sales 16% reported / 19% constant-dollar; total comparable sales 25% / 28%; SPSF 1580. Sections: Item 7 p.27; Item 1 p.3 |
| `LULU_FY2023_management_kpis.json` | `LULU_FY2023_Annual_Report.pdf` | Regional comparable sales (company / Americas / China Mainland / Rest of World); SPSF 1609 on Item 1 p.4. No company-operated comparable-*store* sales metric |
| `LULU_FY2024_management_kpis.json` | `LULU_FY2024_Annual_Report.pdf` | Regional comparable sales; SPSF 1574 on Item 1 p.4. FY2024 noted as 53 weeks |
| `LULU_FY2025_management_kpis.json` | `LULU_FY2025_Annual_Report.pdf` | Regional comparable sales; SPSF 1426 on Item 1 p.4. FY2025 52 weeks vs FY2024 53 weeks |
| `LULU_FY2022.json` … `LULU_FY2025.json` | matching annual reports | Statement/segment extracts; not CompSales/SPSF admission sources |

Also searched page-reference strings present on those management extracts: Form 10-K pp. 2–5, 27–28, 30–34 and Annual Report pp. 2–3.

Admission payload (`admit_periods=(2022-01-30,)`):

| Measurement | Result |
|---|---|
| Status | `admitted_unreconciled` |
| Canonical selection | `deferred` (`deferred_canonical_selection`: later-audited selection remains deferred) |
| Documents / reported observations | 4 / 135 |
| Group selection | selected **0**, deferred **28** |
| Focus CompSales + SPSF assessments | **28** (24 comparable_sales_growth, 4 sales_per_square_foot) |
| Management observations handed to StandardizedFinancials | **0** |
| History handoff | `0 evidenced selected occurrence(s)`; 28 deferred groups remain audit-only |

Exact unmet requirements on all 28 focus items:

- `period_date`: period is an FY label (`FY2022`…`FY2025`), `period_kind=fiscal_year_label`, not an ISO period-end date.
- `calendar_week_adjustment`: empty on 27/28; only FY2024 company `comparable_sales_growth` records `excluded`.
- Presentation / assurance / revision evidence: all `None`.
- Resolved physical page / page: all `None` (extract `page_reference` text is not admitted occurrence evidence).
- CompSales peers: `definition_mismatch`, `calendar_reporting_mismatch`, `peer_period_date`, `peer_calendar_week_adjustment` (FY labels, year-specific definition IDs, channel vs regional reporting basis, 52/53-week mix).
- SPSF: those peer gaps plus `missing_comparison` / `peer_missing_comparison`.

Additional evidence required before admission: ISO period-end dates; calendar-week adjustment for each 52/53-week pair; presentation/assurance/revision sufficient for later-audited canonical selection; resolved physical page; definition-id and reporting-basis alignment across peer years; SPSF comparison linkage. FY labels were not invented and unreconciled observations were not auto-promoted.

Comparable Sales Analysis and Sales per Square Foot Analysis remain explicit unavailable identities (no sheets emitted; Build Status / CLI `Source unavailable / not admitted`).

## Revenue per Store (supported)

Generic historical Revenue per Store uses admitted consolidated revenue and company-operated period-end store history. Period-end and average-store denominators are distinct and are never substituted. Opening average / change / growth stay unavailable. A missing input stays unavailable; a zero denominator is undefined. Total-company revenue divided by company-operated stores includes revenue outside those stores and is not store-only productivity, SPSF, or comparable sales.

Independent reconciliation vs `REVENUE_ANCHORS` (USD thousands) and `INDEPENDENT_STORE_TOTALS` (574 / 655 / 711 / 767 / 811):

| Period | Period-end RPS | Average-store RPS | Adjacent change | Adjacent growth |
|---|---:|---:|---:|---:|
| 2022-01-30 | 10900.029616724738 | unavailable | unavailable | unavailable |
| 2023-01-29 | 12382.470229007633 | 13198.564686737185 | 1482.440612282895 | 0.1360033563586171 |
| 2024-01-28 | 13529.223628691983 | 14083.862371888727 | 1146.7533996843504 | 0.09261103628562929 |
| 2025-02-02 | 13804.597131681878 | 14327.6400541272 | 275.3735029898944 | 0.020353976735656764 |
| 2026-02-01 | 13690.012330456228 | 14071.736375158429 | −114.58480122565015 | −0.008300481363753479 |

Series, standardized reload, and Excel-recalculated cells all match these anchors (tolerance 1e-8). Monetary scale remains `USD in Thousands` (USD). Count units stay independent of monetary scale.

Hardcoded inactive “Revenue per store ratio” in `core/build_status.py` is gone. Availability is evidence-based on emitted `revenue_per_store_*` families. The schedule is listed once under Operating KPIs.

## Ordinary source-bound Lululemon build

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

```bash
python -m bav build Lululemon
```

| Measurement | Result |
|---|---|
| Exit | **0** |
| Output directory | `build/output/Lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` (192536 bytes) |
| Trainer generated by ordinary build | **No** |
| Sidecars | `Lululemon_BAV.component_map.json`, `Lululemon_BAV.assumptions.json`, `rowmap.json`, `build_status.json` |
| Supporting audit | `supporting/standardized.json`, `provenance.json`, `management_kpi_admission.json` present |
| CLI product line | `BAV: Lululemon_BAV.xlsx` |
| CLI Active | Condensed Financials, ALT DuPont, Earnings Quality, Working Capital Analysis, Per Share Analysis, Geographic Segment Analysis, Store Count Analysis, **Revenue per Store Analysis** |
| CLI Unavailable | Comparable Sales Analysis — Source unavailable / not admitted; Sales per Square Foot Analysis — Source unavailable / not admitted |

Build Status (published sheet; one Revenue per Store Analysis row):

| Area | Family / module | Status | Mapped cells |
|---|---|---|---:|
| Historical analysis | Condensed Financials | Active / available | 70 |
| Historical analysis | ALT DuPont | Active / available | 287 |
| Historical analysis | Earnings Quality | Active / available | 53 |
| Historical analysis | Working Capital Analysis | Active / available | 47 |
| Historical analysis | Per Share Analysis | Active / available | 29 |
| Geographic Analysis | (seven families) | Active / available | 102 |
| Operating KPIs | Store-count history / change / growth | Active / available | 5 / 4 / 4 |
| Operating KPIs | Revenue/store growth comparison | Active / available | 4 |
| Operating KPIs | Comparable Sales Analysis | Source unavailable / not admitted | 0 |
| Operating KPIs | Sales per Square Foot Analysis | Source unavailable / not admitted | 0 |
| Operating KPIs | Revenue per Store Analysis | Active / available | 17 |

## BAV-only verification (Trainer unused)

After the ordinary build, before Trainer derivation:

- Sheets include `Overview`, `Build Status`, `Revenue per Store Analysis`; no `Trainer` sheet; no Comparable Sales / SPSF sheets.
- Overview identifies `lululemon athletica inc. (LULU)`, FY2022–FY2026 (5 periods), `USD; USD in Thousands`.
- Visible BAV cells and Notes contain none of: Trainer, Answer Key, exercise, practice, Formula Check, ungraded, learner.
- Semantic components **793**; sidecar `components` **793**; embedded `_ComponentMap` rows **793**.
- Non-source practice identities **783/783** formulas match the semantic map and have non-empty Notes.
- Supplied KPI source facts **10/10** populated.
- Yellow fill count on the BAV: **0**.
- Standardized payload reloads: company `lululemon athletica inc.`, ticker `LULU`, `USD`, `USD in Thousands`, 5 periods. `revenue_per_store_applicable` is true.
- Revenue per Store Notes include period-end vs average-store labels, opening-unavailable language, and the accepted scope note.

BAV SHA-256 after the ordinary rebuild used for derivation: `0020691a3edaee24d7c957fe2b8c307aa2ebdda57f9cd8b05aaba8b664701b9f` (192536).  
Component-map SHA-256: `3384ff9ec9944f7c209dc1f3541ef91e8a6293db24e5a30f9ada8f0121acfc63` (1094906).  
Assumptions SHA-256: `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` (69).

## Explicit Trainer derivation from the same model

`derive_trainer_workbook(company.bav, company.trainer)` on the published BAV:

| Measurement | Result |
|---|---|
| Derived path | `build/output/Lululemon/Lululemon_BAV_Trainer.xlsx` (47636) |
| BAV SHA-256 after derivation | unchanged |
| Component-map SHA-256 | unchanged |
| Assumptions SHA-256 | unchanged |
| Trainer-only sidecars | none (`Lululemon_BAV_Trainer*` is only the xlsx) |
| Active practice cells | **783** blank, **783** bright yellow, **0** comments/hints |
| KPI sources on Trainer | **10** still populated |
| Check blank | total **783**, correct **0**, incorrect **0**, blank **783** |
| Check correctly completed | total **783**, correct **783**, incorrect **0**, blank **0** |
| Check one incorrect RPS practice | total **783**, correct **782**, incorrect **1**, blank **0** |

Check summaries did not disclose formulas, component ids, or hints. Check resolved against the matching `Lululemon_BAV.xlsx`.

## Excel recalculation

Microsoft Excel.app was available. A copy of the published BAV was opened, calculated twice, saved, and closed. The official published BAV hash was not replaced.

| Measurement | Result |
|---|---|
| Command | `osascript` → Microsoft Excel `open` / `calculate` / `save` / `close` on `/tmp/lulu-rps-excel.HOjvNI/Lululemon_BAV_recalc.xlsx` |
| Exit | **0** |
| Recalc file | 224953 bytes; SHA-256 `836076eaffdd468ca1f2d7b2f9e6efb1c97eefbfba9ebf6f9f6fa763d7f242ec` |
| Formula strings vs published BAV | **984** unchanged, **0** diffs |
| Period-end / average / change / growth vs independent anchors | **all match** |
| Store-count and revenue source cells | 574–811 and 6256617–11102600 match anchors |
| Excel error values on RPS cells | **none** |
| Official BAV hash after Excel | unchanged `0020691a3edaee24d7c957fe2b8c307aa2ebdda57f9cd8b05aaba8b664701b9f` |

## Regressions

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

| Suite | Result |
|---|---|
| `core/tests/test_revenue_per_store.py` | **6 passed** (catalog/formulas, inapplicable payloads, missing/zero inputs, no denominator substitution, Lululemon independent anchors, Build Status once/17 cells) |
| `core/tests/test_current_build.py` `test_normalization_candidate_admission.py::test_protected_artifacts_and_eight_extracts_unchanged` plus RPS | **20 passed** (includes **50/50** protected artifacts and **8/8** extracts vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`) |
| `test_operating_kpi_workbook.py` `test_operating_kpi_analysis.py` `test_operating_kpi_relationships.py` `test_operating_kpi_facts.py` | **179 passed** |
| `test_lululemon_benchmark.py` `test_fast_retailing_benchmark.py` `test_trainer.py` `test_build_cli.py` `test_build_contract.py` | **442 passed** |
| `test_management_kpi_admission.py` `test_management_kpi_reconciliation.py` `test_management_kpi_history.py` `test_management_kpi_identity.py` `test_management_kpi_analysis.py` `test_operating_kpi_management_history.py` | **1438 passed** |
| `test_management_kpi_history.py` `test_source_availability.py` `test_operating_kpi_facts.py` `test_operating_kpi_workbook.py` `test_operating_kpi_analysis.py` `test_operating_kpi_relationships.py` | **247 passed** |

Fast Retailing practice count remains **577** (no store history → Revenue per Store stays inapplicable). New current-build outputs were not used to replace protected benchmarks or the eight source extracts.

## Remaining defects / unavailable verification

- Comparable Sales Analysis and Sales per Square Foot Analysis remain unavailable / not admitted on the ordinary Lululemon build. Required additional evidence is listed above. Revenue per Store is Active for the five supported periods.
- Disclosure-led historical driver testing and evidence-backed strategy interpretation remain subsequent Session work.
- Earlier normalization, broader source-workflow, normalized-per-share and other deferred real-company acceptance commitments remain deferred with their ledger evidence.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

---

# Native Excel recovery evidence — 2026-09-20

The prior unavailable native Excel cached-value verification now has two
successful real-workbook attempts on the same stable verification file.
This updates the Excel acceptance evidence only; it does not activate deferred
CompSales/SPSF analysis, close the major Completion, or reach the Session Endpoint.

The original `build/output/Lululemon/Lululemon_BAV.xlsx` remains untouched:
SHA-256 `27cf81c5f6cc71fdeeae46d90825704a7ac4b2e1e90a346464e29ffa17d83e67`.
AutoCycle copied it in place into
`.git/autocycle/excel-workbooks/5dc9d0038b5f6b7cfbc50b3c/autocycle-verification-5dc9d0038b5f6b7cfbc50b3c.xlsx`.
Only that stable copy was opened, recalculated, saved and closed by native Excel.

| Attempt | Result/evidence | Saved snapshot SHA-256 |
| --- | --- | --- |
| First successful real BAV run | `.git/autocycle/excel-verification-1a8_lsvq/result.json` | `22525b539f2e160f5dcf29631aa6019ce81699d642fe9181a59dacdb6c135a7d` |
| Repeated same-path run | `.git/autocycle/excel-verification-kzg9a_ex/result.json` | `d49f89a3fef342376a0832a192a8f450abb99529f28e1fa711b6c24a731eafd5` |

Each attempt's directory contains `excel.log`, `verification.log` and immutable
`saved-copy.xlsx`. Review should inspect the snapshot matching its result hash;
subsequent attempts can update the stable working copy.

`scripts/verify_cached_workbook.py` is the read-only executable acceptance check.
It accepts a separate workbook argument and compares saved native values with
`docs/native-excel-kpi-references.json` (SHA-256
`ca2cc16cf89a721d664f26340c3c1e1b0ca0d9e1d35ef9fbe75db7a92dbe248c`).
The reference data uses the pre-existing independent revenue and company-operated
store-count anchors, independent denominator/change/growth arithmetic, and the
retained unavailable opening observations. It does not read expectations from the
recalculated workbook or invoke production model calculations.

Both real runs returned `VERIFIED`: 50 independent-reference comparisons and
50 affected/dependency cells checked; all 33 affected formulas have independent
references; no missing/error caches on the checked surface; formula and literal
input preservation checked across every sheet, including hidden sheets. Numeric
absolute tolerance remains `1e-8`. Source, saved copy and reference inputs remain
unchanged during read-only verification. A mismatch, formula/input change,
missing/error cache, or unsupported dependency fails with a nonzero exit.

Reproducible invocation after the reviewed helper is installed (the executing
interpreter must have openpyxl):

```sh
/Users/lizhiguo/Documents/Developer/.venv/bin/python ~/.autocycle/excel_verification.py build/output/Lululemon/Lululemon_BAV.xlsx -- /Users/lizhiguo/Documents/Developer/.venv/bin/python scripts/verify_cached_workbook.py '{workbook}' --original build/output/Lululemon/Lululemon_BAV.xlsx --references docs/native-excel-kpi-references.json
```

Permission provenance: the initial real-copy attempt timed out at Excel open
(`-1712`) while access was not granted. A retry returned no workbook object
(`-2753`). A normal macOS open request returned success but Excel still reported
zero workbooks. A normal quit, guarded by a zero-workbook check, succeeded;
reopening through the unchanged native script then produced the two successful
runs above. The user reported no new Grant Access window for these successful
runs. The individual contribution of the normal-open request versus restart to
clearing this expired request was not separately isolated. No security dialog
was operated by automation, no force quit was used, and no sandbox/Full Disk
Access settings were changed. The production helper does not restart Excel.

The generic path fix and measured diagnostic history are recorded in
`docs/excel-permission-diagnosis-2026-09-20.md`. Native execution success alone
was not used as acceptance: the saved-cache verifier ran on the exact stable
copy and retained independently inspectable evidence for Review.

---

# Step 5.1 — Canonical build migration and Drivers corrections

Date: 2026-09-21. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

This append records the bounded Step 5.1 attempt. It does not rewrite prior ledger history and does not close the Session Endpoint.

## Work completed in this attempt

Preserved prior inventory and canonical input migration. Finished remaining company-name build/check wiring, issuer fiscal-year mapping at the data/presentation boundary, Margin prose/figure, lowercase on-disk output, and pre-removal verification. Obsolete duplicate trees were **not** deleted because required native Excel presentation inspection is BLOCKED.

## Canonical input inventory (pre-build hashes, unchanged after build)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `build/input/lululemon/reconciled/standardized.json` | `88021a6274fedf54899b12ee5727ce8985ad50dcb8f0b85e051a746d1dd8d803` | 70646 |
| `build/input/lululemon/reconciled/provenance.json` | `63abff929fafa11b4824c4df4f53c3c058ffc770cae2c28c9125737caa2da462` | 793887 |
| `build/input/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `build/input/lululemon/reconciled/management_kpi_admission.json` | `c5b28f92bae9776a592131ad0463d8fff695265a3f2fbebcfd3d3acd123b38b9` | 2269596 |
| `build/input/lululemon/extracted/LULU_FY2022.json` | `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` | 60110 |
| `build/input/lululemon/extracted/LULU_FY2023.json` | `fcaa9abb417c4f96eb5496c5fc3f1b683b13c17a498c400de869e81880788c05` | 73971 |
| `build/input/lululemon/extracted/LULU_FY2024.json` | `0ddc2893afa892d2e1684a38fdc3a3275bb82ace5d4a237c785ad1246d327c4f` | 72244 |
| `build/input/lululemon/extracted/LULU_FY2025.json` | `fc4ffe8e7ce7f919c815ff4eecdb171d7f75f528a925cbced5814044d8363a10` | 70176 |
| `build/input/lululemon/extracted/LULU_FY2022_management_kpis.json` | `d5288f1d4835fe678b2942158a8b6e55e85deffd4cbd1da12fd353aa5b7b13d7` | 18386 |
| `build/input/lululemon/extracted/LULU_FY2023_management_kpis.json` | `92ec08cf350d90ddd4faf54d7fcec114e70b009a2bfe81285eefd2fb9982ef19` | 21774 |
| `build/input/lululemon/extracted/LULU_FY2024_management_kpis.json` | `3513278b78b1964e38538498ab02bb6b2ec47bcd5187dfa663cb63b56ca89dde` | 22055 |
| `build/input/lululemon/extracted/LULU_FY2025_management_kpis.json` | `386c160d8880f14af900011c993b8f98a94ff700166d80f61c1e760d2346ba78` | 20053 |
| `build/input/lululemon/source/LULU_FY2022_Annual_Report.pdf` | `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 4913067 |
| `build/input/lululemon/source/LULU_FY2023_Annual_Report.pdf` | `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 5848446 |
| `build/input/lululemon/source/LULU_FY2024_Annual_Report.pdf` | `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` | 5953217 |
| `build/input/lululemon/source/LULU_FY2025_Annual_Report.pdf` | `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 6590658 |

Accepted current reconciled `standardized.json` was not replaced by stale `lululemon-live` or benchmark reconciliations. Distinct prior-live bytes are already relocated to `build/input/lululemon/evidence/prior-live/` (`standardized.json` `6c9aad59…51e5`, `provenance.json` `5067c1d0…5951`, `conflicts.json` `d8a33012…978e0`, `management_kpi_admission.json` `ea01edfd…915ef`). Fast Retailing audit extracts already relocated to `build/input/fast_retailing/evidence/_extract/` (five `CFS2021–2025_p1-30.txt` byte-identical to `benchmark/fast_retailing/_extract/`).

## Issuer fiscal mapping (extracted evidence, not calendar year of period-end)

| Period-end | Issuer FY | Calendar year of end-date |
|---|---|---|
| 2022-01-30 | FY2021 | 2022 |
| 2023-01-29 | FY2022 | 2023 |
| 2024-01-28 | FY2023 | 2024 |
| 2025-02-02 | FY2024 (53-week) | 2025 |
| 2026-02-01 | FY2025 | 2026 |

Extracted filing current-period evidence: `LULU_FY2024.json` / `LULU_FY2024_management_kpis.json` have `fiscal_year=2024` and period-end `2025-02-02`. Mapping is applied at `prepare_company_input` and survives export/reload of period-end dates and labels (`core/tests/test_issuer_fiscal.py`: **3 passed**). Overview, Drivers Markdown and all three figures use these labels. Column headers retain actual period-end dates.

## Ordinary build / check (before removal)

```bash
python -m bav build Lululemon
python -m bav check Lululemon
```

| Measurement | Result |
|---|---|
| Build exit | **0** |
| Check exit | **0** |
| Output directory (on-disk name) | `build/output/lululemon/` |
| Primary workbook | `Lululemon_BAV.xlsx` SHA-256 `ac4285e7b2cce648bbc46e9742111f0a12ffac2b1d729b1b173c2fd867a169a4` (227421) |
| Drivers Markdown | `313a0ac193df4621390fc76e41cb26eadd3f057c0bae48693b14b66c583acc79` (4191) |
| Placeholders | Forecast/Valuation/Overview SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (0 bytes each) |
| `figures/drivers/growth.png` | `dd4aae26b7d6fb72ed02890110e04182148c53a40b9717ae9fc355426e2910ce` (63564) |
| `figures/drivers/geography.png` | `7112d2d57cd0e216b5cc416621a3379daf76157758fe5936aab9b50bd07de500` (51504) |
| `figures/drivers/margin.png` | `eebb5cd7783b09e2c41486d7f0667367ec8f0a813d4ee1cb17114d841f007c38` (66103) |
| Supporting | `build_status.json` `4f6ed926…f6e9`; `assumptions.json` `73fbb33f…d21a`; `component_map.json` `0db38272…19f3`; `rowmap.json` `b8d8c9c9…4ca4` |
| Active `lululemon-live` code dependency | **none** |
| Recreated `build/lululemon` or `lululemon-live` | **no** |

## Margin independent reconciliation

Computed from the same validated BAV margin series. Latest period FY2025 (ended 1 February 2026):

| Quantity | Value |
|---|---:|
| Gross margin change | −2.6244 pp |
| Net operating expense burden change | +1.1300 pp |
| Operating-margin change | −3.7544 pp |
| Identity OM = GM − burden | **0.000000e+00** |

Drivers prose: `operating-margin change was -3.75 pp, equal to the gross-margin change (-2.62 pp) minus the net-operating-expense-burden change (+1.13 pp)`. Levels: GM 57.7/55.4/58.3/59.2/56.6%; burden 36.4/39.0/36.1/35.6/36.7%; OM 21.3/16.4/22.2/23.7/19.9%.

Inspected `extracted/*_management_kpis.json` and `reconciled/management_kpi_admission.json`: no admitted gross-margin / operating-margin causal explanations with locators. Recorded as unavailable. No new extraction added.

## Workbook analytical comparison vs pre-migration `build/lululemon/Lululemon_BAV.xlsx`

Non-empty cells 19133 / 19133. Only-current 0, only-pre 0.

| Class | Count |
|---|---:|
| Formula/type changes | **0** |
| Literal changes | **2** |

Intended fiscal-label differences only:

- `Overview!A3`: `Historical coverage: FY2022 – FY2026 (5 periods)` → `Historical coverage: FY2021 – FY2025 (5 periods)`
- `_CheckContext!A3`: embedded standardized period labels FY2022–FY2026 → FY2021–FY2025; numerical values unchanged

Checkpoint `51468d6872d6cc6bfebbe780664003171bcb105c` contains `release/lululemon/Lululemon_Answer_Key.xlsx`. Historical checkpoint discrepancy remains unresolved evidence, not a newly passed comparison. Intended fiscal-label differences are recorded separately above.

## Figures and fonts

`resolve_required_fonts` and renderer-measured word-spacing remain in `core/tests/test_research_drivers.py` (passed). Visual inspection of the three regenerated PNGs: FY labels and period-end dates readable; source notes present; no clipping, overlap, or missing-glyph warnings observed. The extra inter-word spacing from STYLE is visible as wider gaps, not missing glyphs.

## Regressions (path expectations adapted; numerical assertions not weakened)

| Suite | Result |
|---|---|
| `test_issuer_fiscal.py` | **3 passed** |
| `test_current_build.py` `test_research_drivers.py` `test_build_contract.py` `test_reported_margin.py` `test_source_availability.py` | **89 passed** (protected-artifacts test excluded here; it still requires retired release files to be absent) |
| `test_lululemon_benchmark.py` `test_fast_retailing_benchmark.py` `test_management_kpi_admission.py` `test_operating_kpi_facts.py` `test_operating_kpi_analysis.py` `test_operating_kpi_relationships.py` `test_operating_kpi_workbook.py` | **610 passed** |
| `test_trainer.py` `test_build_cli.py` `test_geographic_segment_facts.py` `test_geographic_segment_analysis.py` `test_geographic_segment_workbook.py` `test_revenue_driver.py` `test_source_availability.py` | **193 passed** |

`test_normalization_candidate_admission.py::test_protected_artifacts_and_eight_extracts_unchanged` **failed** because `release/fast_retailing/*` and `release/lululemon/*` still exist. That test already accounts relocation (25) + stayed (5) + retired (20) = 50 and eight extracts. Removal of those retired files is gated on native Excel presentation inspection.

## Native Excel

Overview presentation changed (A3 fiscal coverage). Helper:

```sh
python3 ~/.autocycle/excel_verification.py build/output/lululemon/Lululemon_BAV.xlsx -- python3 /tmp/verify_lululemon_overview_presentation.py '{workbook}' --original build/output/lululemon/Lululemon_BAV.xlsx
```

| Measurement | Result |
|---|---|
| Status | **BLOCKED** |
| Source SHA-256 | `ac4285e7b2cce648bbc46e9742111f0a12ffac2b1d729b1b173c2fd867a169a4` |
| Evidence | `.git/autocycle/excel-verification-z0ozjjfv/result.json` |
| Action | Excel automation timed out (−1712) opening the verification copy. A timeout alone does not establish a permission failure. If Excel shows a Grant Access dialog for that copy, grant that file once and reuse the same path. Copy: `.git/autocycle/excel-workbooks/abe47425be87411eb1fee0c2/autocycle-verification-abe47425be87411eb1fee0c2.xlsx`. |

Retained `.git/autocycle/excel-verification-fb95_r2m/saved-copy.xlsx` belongs to source SHA-256 `f0f46a03f4c2091f8d9a1d3002b37bcda2bd46c6851389d9ebc4171cbf4f1a0c`, not the current workbook. `docs/native-excel-kpi-references.json` `source_sha256` is `27cf81c5f6cc71fdeeae46d90825704a7ac4b2e1e90a346464e29ffa17d83e67`. Neither is applicable to this generation. Prior acceptance and Excel recovery are not granted. No security dialog was operated.

## Removal inventory (not deleted)

| Path | Status | Accounting |
|---|---|---|
| `build/lululemon/` | present (28 files) | obsolete generated tree; pre-migration BAV used for formula/literal compare |
| `build/lululemon-live/` | absent | already gone |
| `build/input/lululemon-live/` | present (4 files) | unique bytes already in `build/input/lululemon/evidence/prior-live/` |
| `build/fast_retailing/` | present (8 files) | obsolete generated tree |
| `build/output/FastRetailing/` | present (8 files) | uppercase/legacy output |
| `build/output/rowmap.json` | present | leftover non-company artifact |
| `benchmark/lululemon/` | present (18 files) | relocated into `build/input/lululemon/` + fixtures; identity in Git |
| `benchmark/fast_retailing/` | present (23 files) | relocated into `build/input/fast_retailing/`; `_extract` in `evidence/_extract/` |
| `release/lululemon/` | present (10 files) | retired in protected-artifact ledger; identity in Git |
| `release/fast_retailing/` | present (10 files) | retired in protected-artifact ledger; identity in Git |

No duplicate was deleted in this attempt.

## Remaining gaps toward Completion

- Native Excel readable inspection of the changed Overview fiscal-label presentation is unresolved (helper BLOCKED, −1712).
- Gated removal of obsolete duplicate trees is therefore not done; `test_protected_artifacts_and_eight_extracts_unchanged` still fails while retired release files remain.
- Post-removal repeat build/check from unchanged canonical inputs is not done.
- Historical checkpoint discrepancy vs `51468d6872d6cc6bfebbe780664003171bcb105c` remains unresolved evidence.
- Earlier normalization, broader source-workflow and normalized-per-share obligations remain deferred.
- KPI native-reference file and fb95 saved-copy are not applicable to the current workbook hash.

## Required plan changes

None. The Excel helper supplied a concrete Action; this attempt did not guess around it or remove duplicates without that gate.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

---

# RESULT.md — Step 7.1 Finish canonical migration verification

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 7.1 — Finish canonical migration verification  
**Work:** `578514d1133a4d2d9ec6a032875cbb2e`  
**Plan:** `1211fbe4423347e3a3b9e9646d981ff7`  
**Finding:** planning-obstacle  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
No commit / push / sync / checkpoint / branch change. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

This append records the bounded Step 7.1 attempt. It does not rewrite prior ledger history, does not close the Session Endpoint, and does not implement Drivers expansion, Word/PDF publication, or BAV-facing rebranding.

## Required plan change

None. Inherited Step 5.1 Completion and unfinished obligations were reused. Native Excel was not retried because a later preserved helper run already produced a saved snapshot and readable Overview inspection, and the current/post-removal workbook is cell-identical to that snapshot.

## Preserved interrupted work inspected

`.git/autocycle/excel-verification-z0ozjjfv/` remains the Step 5.1 open-stage timeout: source SHA-256 `ac4285e7b2cce648bbc46e9742111f0a12ffac2b1d729b1b173c2fd867a169a4`, error `-1712`, no saved snapshot. Helper text treats this as a timeout, not a permission failure.

A later interrupted attempt left `.git/autocycle/excel-verification-3v0t6_ur/`:

| Field | Value |
|---|---|
| Helper status | **VERIFIED** |
| Source SHA-256 | `ac4285e7b2cce648bbc46e9742111f0a12ffac2b1d729b1b173c2fd867a169a4` |
| Copy / snapshot SHA-256 | `3536481334c876cf9911fa0dba7f9d8e72c1332b43b1d54fa5f0ed97dcdd19af` (264020) |
| `excel.log` | `Excel recalculated, saved and closed verification copy` |
| Verifier | repository `scripts/verify_lululemon_overview_presentation.py` (byte-identical to `/tmp/verify_lululemon_overview_presentation.py`) |
| Verifier result | Overview A3 literal `Historical coverage: FY2021 – FY2025 (5 periods)`; formula diffs **0** |
| Native captures | `overview-a3-rect.png` `2b64d382…1513d3`; `overview-lower.png` `dd1211ab…807b68a4b`; `overview-full.png` `76672040…bd5a2f` (hashes match `overview-inspection.json`) |

Re-inspected the A3 crop: formula bar and Overview A3 both read `Historical coverage: FY2021 – FY2025 (5 periods)`; title `Business Analysis and Valuation` / `lululemon athletica inc. (LULU)`; Overview tab active; AutoRecover banner present and not dismissed. Openpyxl literal check alone was not used as presentation acceptance.

## Excel diagnosis this step (no new native attempt)

| Probe | Result |
|---|---|
| Helper | `/Users/lizhiguo/.autocycle/excel_verification.py` present; stable path `.git/autocycle/excel-workbooks/abe47425be87411eb1fee0c2/autocycle-verification-abe47425be87411eb1fee0c2.xlsx` |
| Interpreters | system `python3` 3.14.0; venv `/Users/lizhiguo/Documents/Developer/.venv/bin/python` 3.14.0 |
| Verifiers | `scripts/verify_lululemon_overview_presentation.py` and `scripts/verify_cached_workbook.py` present |
| Excel locate | `/Applications/Microsoft Excel.app/` |
| Excel process | PID 83850 running since 6:28AM; verification copy **not** open (`lsof` empty); lock not held |
| Native attempts this step | **0** of 2. Second attempt not authorized: no open-stage defect remained after the preserved VERIFIED run, and current formulas/literals match that saved copy. Did not force-quit Excel, close other workbooks, overwrite the granted copy, or dismiss the AutoRecover banner. |

## Canonical inventory (unchanged vs Step 5.1)

All 16 recorded Lululemon source / extracted / reconciled files still match Step 5.1 SHA-256 and byte sizes, including `standardized.json` `88021a6274…d803` (70646). Distinct prior-live evidence remains under `build/input/lululemon/evidence/prior-live/` (`standardized.json` `6c9aad59…51e5`; `provenance.json` `5067c1d0…5951`; `conflicts.json` `d8a33012…978e0`; `management_kpi_admission.json` `ea01edfd…915ef`). Fast Retailing audit extracts remain under `build/input/fast_retailing/evidence/_extract/`. Accepted inputs were not overwritten with stale benchmark data.

On-disk company directories are lowercase `build/input/{lululemon,fast_retailing}` and `build/output/{lululemon,fast_retailing}`. `build/output/Lululemon` is the same inode as `build/output/lululemon` on this case-insensitive volume, not a second tree. Runtime resolution uses only `build/input/<slug>` and `build/output/<slug>` (`core/current_build.py`); no silent benchmark / release / uppercase / `lululemon-live` fallback.

## Removal accounting

Obsolete duplicates listed in Step 5.1 were already absent at the start of this attempt (working-tree deletions; not committed). This step did not delete unique upstream evidence. Authenticated 50/50 + 8/8 accounting:

| Class | Count | Disposition |
|---|---:|---|
| Relocated | 25 | content-identical at canonical / fixture destinations; git hashes match C1/C2 |
| Stayed | 5 | `example/` demo artifacts unchanged |
| Retired | 20 | absent from working tree; C1 == C2 in git history |
| Extracts | 8 | relocated Lululemon ordinary + management-KPI JSON match `5e3ef5cf…` |

`test_protected_artifacts_and_eight_extracts_unchanged` **passed without exclusions**.

## Ordinary build / check after removal

```bash
python -m bav build Lululemon
python -m bav check Lululemon
python -m bav check FastRetailing
```

| Measurement | Result |
|---|---|
| Lululemon build / check | **0** / **0** |
| Fast Retailing check | **0** |
| Recreated obsolete paths | **no** (`build/lululemon`, `lululemon-live`, uppercase output, `build/output/rowmap.json`, `benchmark/{lululemon,fast_retailing}`, `release/{lululemon,fast_retailing}` remain absent) |
| Post-build workbook | `9394e45b23dc59904e13e1392c4ddc349113ca0db2b6bdf229d5ff4f305878e0` (227422) |
| vs native saved-copy | nonempty cells **19133 / 19133 same**; formula **0**; literal **0**; hidden-sheet visibility identical |
| Research / figures / supporting | byte-identical to Step 5.1 (`Drivers` `313a0ac1…cc79` 4191; placeholders `e3b0c442…` 0 bytes; growth/geography/margin PNGs `dd4aae26…` / `7112d2d5…` / `eebb5cd7…`; sidecars `4f6ed926…` / `73fbb33f…` / `0db38272…` / `b8d8c9c9…`) |
| Canonical inputs after rebuild | unchanged |

Workbook zip hash differs from inspected source `ac4285e7…` (227421) and the 15:33 rebuild `e52be9b4…` (227422) by xlsx packaging only. Cell identity, not the zip hash, is the applicability evidence.

## Native / reference applicability

| Evidence | Source SHA-256 | Applicable to current cells? |
|---|---|---|
| `excel-verification-3v0t6_ur` saved-copy + Overview captures | `ac4285e7…` | **Yes** — 19133/19133 cell identity including hidden sheets; Overview A3 unchanged |
| `excel-verification-fb95_r2m/saved-copy.xlsx` `1d332daa…` | `f0f46a03…` (prior RESULT) | **No** — formula **0**; literal **4** (Overview 3 + `_CheckContext` 1); only-current **48** Overview; only-fb95 **2** Overview (54 cells; 52 prior Overview diffs plus intended fiscal-label pair). Hash ≠ current |
| `docs/native-excel-kpi-references.json` | `27cf81c5f6cc71fdeeae46d90825704a7ac4b2e1e90a346464e29ffa17d83e67` | **No** — different source hash; recovery not granted |

Changed formulas/dependencies were not observed; native recalculation of the post-removal zip was not required. The presentation change remains the intended Overview fiscal coverage, already natively inspected on the granted copy.

## Checkpoint `51468d6872d6cc6bfebbe780664003171bcb105c`

Retained `release/lululemon/Lululemon_Answer_Key.xlsx` SHA-256 `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` (119554). Current nonempty 19133 vs checkpoint 11122.

| Class | Count |
|---|---:|
| Shared same | 9580 |
| Formula/type changes | **61** (all `_ComponentMap`) / type **0** |
| Literal changes | **802** (`_ComponentMap` 799; Per Share 1; Accounting Judgment 1; `_CheckContext` 1) |
| Only-current | **8690** (later KPI/driver/Overview/Build Status sheets) |
| Only-checkpoint | **679** (Trainer 668; `_ComponentMap` 11) |

Checkpoint has Trainer and no Overview / later KPI-driver sheets. Historical product gap, not a newly passed comparison. Intended fiscal-label change is separate: Overview A3 `FY2021 – FY2025`; column headers keep actual period-end dates including FY2024's 53-week year **2025-02-02**.

Pre-migration `build/lululemon/Lululemon_BAV.xlsx` bytes (`2507ef35…`) are no longer on disk. Step 5.1 measured formula **0**, literal **2** (Overview A3 and `_CheckContext` A3 fiscal labels only) against that tree; this step did not recover those bytes and does not reset that comparison.

## Issuer labels, Margin, figures

Issuer mapping from extracted filings (not calendar year of period-end): 2022-01-30 FY2021; 2023-01-29 FY2022; 2024-01-28 FY2023; 2025-02-02 FY2024 (53-week); 2026-02-01 FY2025. Workbook Overview A3, Drivers table/limits, and all three figures use these labels. Income Statement row 6 dates are 2022-01-30 … 2026-02-01.

Independent Margin from accepted `StandardizedFinancials` (identity OM = GM − net operating-expense burden):

| Period | GM % | Burden % | OM % | Identity |
|---|---:|---:|---:|---:|
| FY2021 | 57.676 | 36.365 | 21.311 | 2.8e-17 |
| FY2022 | 55.389 | 39.010 | 16.379 | −5.6e-17 |
| FY2023 | 58.314 | 36.143 | 22.171 | 5.6e-17 |
| FY2024 | 59.225 | 35.560 | 23.665 | −2.8e-17 |
| FY2025 | 56.601 | 36.690 | 19.911 | 2.8e-17 |

FY2024→FY2025: GM **−2.6244** pp, burden **+1.1300** pp, OM **−3.7544** pp, identity 5.8e-15. Matches Drivers prose. No impairment concept in the accepted IS; management explanations remain unavailable. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

Fonts: Aptos Regular `/Applications/Microsoft Excel.app/Contents/Resources/DFonts/Aptos.ttf`; DengXian Regular `…/Deng.ttf`. `test_figure_word_spacing_uses_required_fonts_and_visible_gaps` passed. Visual re-inspection of the three PNGs: issuer FY labels and period-end dates readable, including FY2024 / 2 Feb 2025; source notes present; word gaps visible; no missing-glyph boxes.

## Regressions

| Suite | Result |
|---|---|
| `test_issuer_fiscal` + `test_current_build` + `test_research_drivers` + `test_build_contract` + `test_reported_margin` + `test_source_availability` + `test_protected_artifacts_and_eight_extracts_unchanged` | **90 passed** (protected included; no exclusions) |
| `test_lululemon_benchmark` + management-KPI admission + operating-KPI facts/analysis/relationships/workbook | **317 passed** |
| `test_trainer` + `test_build_cli` + geographic facts/analysis/workbook + `test_revenue_driver` | **160 passed** |
| `test_fast_retailing_benchmark` | **293 passed** |
| management-KPI history/reconciliation/analysis/identity + learner-ready + revenue-per-store | **382 passed** |

Numerical and evidence assertions were not weakened. Path expectations already used canonical lowercase inputs.

## Preservation

Retained: numerical inputs/formulas, accounting/normalization controls, structured filing handoff, `StandardizedFinancials`, atomic publication, four driver hypotheses, 24 Comparable Sales facts, three SPSF levels, five Revenue per Store periods, 39 pair assessments, five supported SPSF comparisons, 2023-01-29 SPSF disagreement audit-only, excluded/calendar failures, unavailable adjacent SPSF growth, undated FY2021 metadata. Forecast / Valuation / Overview remain 0-byte placeholders. Optional Trainer functionality is unchanged (no Trainer generated). Repository/infrastructure names unchanged.

## Remaining gaps toward Completion

- Expanded Drivers, Word/PDF publication, and product-facing BAV branding remain mandatory Session work after Review; this step neither implemented nor certified them.
- Historical checkpoint discrepancy vs `51468d6872d6cc6bfebbe780664003171bcb105c` remains unresolved evidence.
- Pre-migration `build/lululemon/` bytes are gone; Step 5.1's two intended fiscal-label diffs are the last measured comparison against that tree.
- Earlier normalization, broader source-workflow and normalized-per-share obligations remain deferred.
- KPI native-reference file and fb95 saved-copy remain inapplicable to the current generation hash.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

---

# RESULT.md — Step 7.1.1 Reconcile migration comparison evidence

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 7.1.1 — Reconcile migration comparison evidence  
**Work:** `578514d1133a4d2d9ec6a032875cbb2e`  
**Plan:** `3be8d9b8925d4f34b98e2b85b429d31b`  
**Finding:** planning-obstacle  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `7f6de96abef3ae66efa75f8a65184eec24cad8fa4d31f2424cc7624450b9627f` (36138).  
SESSION SHA-256 `2cb7837b6dac913fbb7538f078c711c47f1503bc4cc2f21d195ff2e8db93b1cf` (5708).  
IMPLEMENTATION SHA-256 `50d57a918b95396fc6d867d0e24c4f53beac6577bcc9e9d7546682e5b21ec586` (7789).  
No commit / push / sync / checkpoint / branch change. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. HEAD `128cac5318639c4a0fac309a8868ef4e2b88808b`.

This append records the bounded Step 7.1.1 continuation after Review of checkpoint `40ccc11256c2887934aa50937990dda840ada842`. It does not rewrite prior ledger history, does not close the Session Endpoint, and does not implement Drivers expansion, Word/PDF publication, or BAV-facing rebranding.

## Required plan change

None. Historical checkpoint differences are now grouped with membership and disposition. The pre-migration SHA-256 remains unrecovered after bounded search; that comparison gate is preserved for Review. Independent KPI expectations were not replaced and `docs/native-excel-kpi-references.json` was not rewritten.

## Isolated checkpoint recovery

Recovered `51468d6872d6cc6bfebbe780664003171bcb105c:release/lululemon/Lululemon_Answer_Key.xlsx` into `.git/autocycle/comparison-7-1-1/checkpoint-51468d68-Lululemon_Answer_Key.xlsx`.

| Field | Value |
|---|---|
| SHA-256 | `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` |
| Bytes | 119554 |
| Git blob | `2708bfb1e126781192ca8aebb0f720e028593b32` |
| `release/lululemon/` restored | **no** |

Compared against current `build/output/lululemon/Lululemon_BAV.xlsx` `9394e45b23dc59904e13e1392c4ddc349113ca0db2b6bdf229d5ff4f305878e0` (227422). Hidden-sheet visibility on shared sheets matches. Defined names empty on both. External links **0**.

## Historical cell accounting

| Class | Count |
|---|---:|
| Shared same | **9580** |
| Shared changed | **863** (formula **61**, literal **802**) |
| Only-current | **8690** |
| Only-checkpoint | **679** |

Membership: `.git/autocycle/comparison-7-1-1/{same-cells.txt,changed-cells.json,only-checkpoint-cells.json,only-current-by-sheet.json,dispositions.json}`.

| Group | n | Cells / membership | Before → after | Disposition |
|---|---:|---|---|---|
| G1 unchanged shared | 9580 | `same-cells.txt` | identical | unchanged |
| G2 `_ComponentMap` formulas at reused coordinates | 61 | `I70:I118`, `I182:I185`, `I208:I215` | row occupancy after catalog growth 486→861 | **relocation** — shared IDs 486/486 formula-identical |
| G3 `_ComponentMap` literals at reused coordinates | 799 | `changed-cells.json[_ComponentMap\|literal]` | shifted ids/order/hints | **relocation** |
| G4 shared-id order renumber | 78 | `component-map-shared-diffs.json` `fields=={order}` | catalog insertion | **intended product change** |
| G5 inventory short_hint | 8 | eight `inventory_*` IDs | “not practiced” → “unavailable without a prior period” | **intended product change** |
| G6 Accounting Judgment A3 | 1 | `Accounting Judgment!A3` | Formula Check sentence removed | **intended product change** (`test_trainer` asserts this) |
| G7 Per Share A2 | 1 | `Per Share Analysis!A2` | “not practice cells” → “supplied source inputs” | **intended product change** |
| G8 `_CheckContext` growth | 2 | `A2` + only-current `A3` | 19706-char JSON → 30000+27514 chunks; added `historical_operating_kpis`; period labels FY2021–FY2025 | **intended product change + fiscal labels** (`CHECK_CONTEXT_CHUNK_SIZE=30000`) |
| G9 Trainer removed | 668 | `only-checkpoint-cells.json[Trainer]` | Trainer sheet absent from BAV | **intended product change** |
| G10 leftover `depends_on` | 11 | `_ComponentMap!L84:L88,L99:L102,L208,L210` | values moved with rows; `only_checkpoint_ids=[]` | **relocation** |
| G11 later analytical sheets | 2113 | Overview 55, Build Status 87, Geographic 471, Store Count 65, CompSales 1113, SPSF 108, RPS 39, Revenue Driver 175 | not in checkpoint | **intended product change**; KPI/driver/compsales independently derived below |
| G12 new `_ComponentMap` rows | 6576 | 375 new IDs | geographic/KPI/driver families | **intended product change** |

No demonstrated numerical defect. No repair.

## Pre-migration SHA-256 `2507ef35930fd4be42a69ac6bef059d97e58fa1ad4a28ee4b866086c4d237bc0`

Bounded search (Git history of `build/lululemon/Lululemon_BAV.xlsx`, all historically named `*.xlsx` blobs, size 227420, `.git/autocycle` snapshots, recorded Excel copies, `/tmp` leftovers, `~/.autocycle`): **0 recovered bytes**. Closest leftover `/tmp/step412-pre/Lululemon_BAV.xlsx` is Step 4.1.1 `bcacf70d…` (228421), not the wanted hash. Previously reported zero formula / two fiscal-label diffs cannot be re-authenticated from recovered bytes. Access needed: the original pre-migration `build/lululemon/Lululemon_BAV.xlsx` bytes. Comparison gate preserved.

## Independent reference applicability

Original `docs/native-excel-kpi-references.json` unchanged SHA-256 `ca2cc16cf89a721d664f26340c3c1e1b0ca0d9e1d35ef9fbe75db7a92dbe248c`; `source_sha256` remains `27cf81c5…`. Those original source bytes are still missing.

Independently derived 50/50 JSON values from `REVENUE_ANCHORS` and `INDEPENDENT_STORE_TOTALS` (USD thousands; company-operated period-end stores; opening N/A). Current vs kzg9a and vs 3v0t6 on those sheets: formulas **33/33**, literals **71/71**. Full current vs 3v0t6: **19133/19133**. Cached 50/50 on 3v0t6, kzg9a, and fb95.

Current-source binding `.git/autocycle/comparison-7-1-1/kpi-binding-current.json` retains original identity and the same 50 values. Official verifier:

```sh
python scripts/verify_cached_workbook.py \
  .git/autocycle/excel-verification-3v0t6_ur/saved-copy.xlsx \
  --original build/output/lululemon/Lululemon_BAV.xlsx \
  --references .git/autocycle/comparison-7-1-1/kpi-binding-current.json
```

**VERIFIED** — 50 independent references, 50 checked cells, `formulas_preserved: true`. Receipt `.git/autocycle/comparison-7-1-1/verify-kpi-binding.json`. Original refs against current remain **BLOCKED** (“different source workbook”) as required: hash alone does not bind.

Driver/compsales original artifacts unchanged. Independently derived store-growth / revenue-growth / RPS / compsales residual / geographic contribution `(Δgeo)/prior_consolidated` from canonical `standardized.json` `88021a62…` (70646): driver JSON **37/37**, compsales JSON **4/4**; 3v0t6 cached **37/37** and **4/4**. Formulas on those sheets identical current/3v0t6/fb95/render-copy. Compsales original source `39914cba…` not recovered.

Native Excel was not re-run: checked formulas and dependencies are unchanged vs the applicable 3v0t6 snapshot.

## Removal gates

**Gate-order breach (recorded, not repaired by later checks):** obsolete trees were already absent at Step 7.1 start (working-tree deletions; not committed). This attempt did not delete again and does not claim later checks prove verification preceded deletion. Acceptance consequence: Review must still treat deletion as having occurred before this historical/KPI reconciliation.

Authenticated 50/50 + 8/8 still hold. Unique generated artifacts not in that ledger and not recovered: pre-migration BAV `2507ef35…`; supporting copies `11e114ca…` / `bf990c16…`. Leftover generated Drivers `9923e74f…` found in `/tmp` and copied only into isolated comparison storage; it is not upstream evidence and was not placed in canonical input. The eight protected extracts remain the canonical extracted JSON.

Obsolete paths still absent. No rebuild (no repair). `python -m bav check Lululemon` **0**; `python -m bav check FastRetailing` **0**.

`test_protected_artifacts_and_eight_extracts_unchanged` + `test_issuer_fiscal` + `test_reported_margin` + `test_source_availability`: **46 passed**, no exclusions.

## Issuer labels, Margin, figures (unchanged carry-forward)

Issuer mapping unchanged: 2022-01-30 FY2021 … 2025-02-02 FY2024 (53-week) … 2026-02-01 FY2025. Overview A3 `FY2021 – FY2025`. `_CheckContext` period labels FY2021–FY2025. Income Statement row 6 dates 2022-01-30 … 2026-02-01. Margin identity and FY2024→FY2025 changes carried forward from Step 7.1. Placeholders remain 0 bytes. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

## Remaining gaps toward Completion

- Pre-migration workbook `2507ef35…` remains missing; that authenticated comparison gate is open.
- Original KPI `source_sha256` `27cf81c5…` bytes remain missing; current applicability is the documented binding plus official verifier, not a rewritten original file.
- Gate-order breach on deletion remains an acceptance consequence for Review.
- Expanded Drivers, Word/PDF publication, and BAV-first presentation remain mandatory subsequent Session work.
- Earlier normalization, broader source-workflow and normalized-per-share obligations remain deferred.

Finishing this bounded continuation does not establish major Completion or the Session Endpoint.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

---

# RESULT.md — Step 7.1.1 Finish retrospective migration reconciliation

**Status:** COMPLETE (this bounded attempt; Review adjudicates Step closure)  
**Step:** 7.1.1 — Finish retrospective migration reconciliation  
**Work:** `578514d1133a4d2d9ec6a032875cbb2e`  
**Plan:** `f3e983eda431424d8a9a3a34f069ddec`  
**Finding:** planning-obstacle  

`TARGET.md` / `SESSION.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start).  
TARGET SHA-256 `7f6de96abef3ae66efa75f8a65184eec24cad8fa4d31f2424cc7624450b9627f` (36138).  
SESSION SHA-256 `c3a9b136234e4dd4ef5d9e0bb3b88ed7ff7db10141a2e2b9bf530246e31e6aa5` (6353).  
IMPLEMENTATION SHA-256 `4396773a8758339c523f18d220ff985f196533b1efbbe9c05b7de8bbc0493b25` (9210).  
No commit / push / sync / checkpoint / branch change. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**.

This append continues work `578514d1133a4d2d9ec6a032875cbb2e` after Review of checkpoint `eb20ec8d23cac61562b8b761284bf7895414abf2`. It does not rewrite prior ledger history, does not close the Session Endpoint, and does not implement Drivers expansion, Word/PDF publication, or BAV-facing rebranding.

## Required plan change

None. Instructions `20260921-181553-000000019` and `20260921-182344-000000020` are already in the current plan/Session. No further plan revision is required for this bounded attempt.

## Authenticated baseline B

| Record | SHA |
|---|---|
| `IMPLEMENT_BASE_SHA` / HEAD / B | `f3e832597657c13752f3fe7615e6c7ac766be4fa` |
| Branch | `checkpoint/20260913-183303` (matches resume-state and `implementation-baseline.json`) |
| Review checkpoint | `eb20ec8d23cac61562b8b761284bf7895414abf2` (parent of B) |
| Reviewed attempt (retained binding) | `128cac5318639c4a0fac309a8868ef4e2b88808b` (parent of Review checkpoint; ancestor of B) |
| `latest-implementation` HEAD | `128cac5318639c4a0fac309a8868ef4e2b88808b` (prior attempt; controller advanced) |

Authentication: branch, ancestry, and checkpoint binding succeeded. Fail-closed was not triggered. Evaluation used `git show` / `git rev-parse` / `git cat-file` / `git hash-object` against B; C1 `3f6f5dde…` / C2 `20d93331…` / extract blob `5e3ef5cf…` are historical Git blobs for relocation provenance, not a replacement baseline. Recovered Answer Key `51468d6872d6cc6bfebbe780664003171bcb105c` and `.git/autocycle/comparison-7-1-1/` remain supplemental historical evidence, not B.

Receipt: `.git/autocycle/comparison-7-1-1/retrospective-acceptance.json` SHA-256 `5c2b914d49e88181e34e2837e3f9d2749e102850355965a22343cee9b7fd6a03` (61227).

## Retrospective acceptance reconciliation

| Requirement | Result | Evidence |
|---|---|---|
| Authenticated Git implementation baseline; no migration-specific replacement B | **Satisfied** | B = `IMPLEMENT_BASE_SHA` = HEAD; 128cac53 retained as reviewed-attempt ancestor |
| 50 protected artifacts + eight extracts vs canonical destinations, relocation hashes, provenance | **Satisfied** | 50/50 and 8/8; destination bytes = historical Git blob (C1=C2 or `5e3ef5cf`); old paths absent; `/build/` destinations gitignored so not in B's tree; three fixture relocations tracked at B and byte-identical |
| Original PDFs under canonical `source/` | **Satisfied** | Four Lululemon + five Fast Retailing PDFs match C1/C2 blobs; source resolution uses `build/input/<slug>/source/` |
| Deletions without identical destinations | **Satisfied** | 20 retired release/generated artifacts absent; Git retains C1/C2 bytes; judged obsolete/generated, not required source |
| Obsolete trees absent; no recreated legacy copy | **Satisfied** | `build/lululemon`, `lululemon-live`, `benchmark/*`, `release/*` absent |
| Cell accounting 9580 / 863 / 8690 / 679 with membership and disposition | **Satisfied** | G1–G12 in `dispositions.json`; no remaining unresolved membership; no numerical defect; no repair |
| 61 `_ComponentMap` formula + 802 literal + Trainer/component-map removals | **Satisfied** | Relocation / intended product change / fiscal-label dispositions unchanged; hidden-sheet visibility and empty defined names carried forward |
| Transient workbook `2507ef35…` recovery/comparison | **Superseded** | Instruction `20260921-181553-000000019`. Not recreated. Absence is not an independent blocker |
| Verification before obsolete-artifact removal | **Superseded (timing only)** | Instruction `20260921-182344-000000020` permits retrospective verification. Original sequence was **not** followed. Later checks do **not** prove the earlier gate ran. Breach remains recorded below |
| 19,133-cell content equivalence, visibility, defined names, no external links, fiscal-coverage inspection | **Satisfied (unchanged surfaces)** | Retained `.git/autocycle/excel-verification-3v0t6_ur/` snapshot `35364813…`; prior full-cell identity 19133/19133 |
| KPI saved-cache: 50 refs / 50 cells, formulas preserved | **Satisfied** | Official verifier **VERIFIED**. Original refs SHA `ca2cc16c…` unchanged (not rewritten). Current-source binding `kpi-binding-current.json` |
| Driver refs 37/37 and compsales 4/4 applicability | **Satisfied** | Independent derivation from REVENUE_ANCHORS, store totals, admitted compsales, and `standardized.json` `88021a62…` (70646): **37/37** and **4/4**. Original source hashes still missing; separately authenticated bindings written; original artifacts not rewritten |
| Native snapshot reuse only where formulas/inputs/dependencies remain applicable | **Satisfied** | Current vs 3v0t6 nonempty cells identical on Revenue Driver, Comparable Sales, Revenue per Store, and Store Count sheets. No new native Excel run |
| Company-name Lululemon build/check, canonical-only runtime, post-removal behavior | **Satisfied** | `python -m bav check Lululemon` **0**; Fast Retailing **0**; no rebuild (no repair); obsolete paths still absent |
| Protected-artifact test without exclusions | **Satisfied** | `test_protected_artifacts_and_eight_extracts_unchanged` plus issuer fiscal / Margin / source-availability: **46 passed** |
| Canonical runtime regressions | **Satisfied** | `test_current_build` + `test_build_cli` + `test_build_contract`: **69 passed** |
| Issuer fiscal labels including FY2024 53-week year; Margin levels/changes | **Satisfied (carried forward)** | Mapping 2022-01-30 FY2021 … 2025-02-02 FY2024 (53-week) … 2026-02-01 FY2025; Margin identity and FY2024→FY2025 changes unchanged; no rebuild |
| Placeholders; `SEGMENT_BRIDGE_TOLERANCE = 0.0` | **Satisfied** | Forecast/Valuation/Overview remain 0-byte `e3b0c442…`; tolerance `0.0` |
| Expanded Drivers, Word/PDF publication, BAV-first presentation | **Unresolved (subsequent Session work)** | Not in this bounded step; not a migration-reconciliation defect |
| Earlier normalization / source-workflow / normalized-per-share | **Deferred** | Unchanged |

## Deletion-before-verification record (preserved)

Obsolete trees were already absent at Step 7.1 start (working-tree deletions; not committed). This attempt did not delete again. The original required sequence — verify, then remove — was not followed. Retrospective verification is now permitted for the already-completed migration; it does not establish that the earlier gate ran. This is a recorded breach of the original timing condition, not a rewritten history and not an independent remaining blocker under instruction `20260921-182344-000000020`.

## Artifact dispositions (50 + 8)

Relocated **25**: working-tree canonical bytes match historical Git blobs; 22 live under gitignored `/build/`; three Lululemon reconciled fixtures are tracked at B (`core/tests/fixtures/ordinary_reconcile/lululemon/{conflicts,provenance,standardized}.json`) and match B. Stayed **5**: `example/` demo artifacts tracked at B, C1, and C2. Retired **20**: absent; historical bytes remain at C1=C2. Extracts **8**: ordinary + management-KPI JSON match blob `5e3ef5cf…`.

No lost required source evidence. No identical-destination mismatch.

## Applicable native / saved-cache verification

Original reference artifacts unchanged vs B:

| Artifact | SHA-256 | `source_sha256` (original, not rewritten) |
|---|---|---|
| `docs/native-excel-kpi-references.json` | `ca2cc16c…dbe248c` | `27cf81c5…` (bytes still missing) |
| `docs/native-excel-revenue-driver-references.json` | `44073234…4727aea` | `f0f46a03…` (bytes still missing) |
| `docs/native-excel-compsales-references.json` | `ae8f7de1…d6fda` | `39914cba…` (bytes still missing) |

Current-source bindings retain those original identities and the same independent expectations. Official verifier against snapshot `35364813…` and current workbook `9394e45b…` (227422):

| Binding | Status | Independent refs | Checked cells | Formulas preserved |
|---|---|---:|---:|---|
| `kpi-binding-current.json` | **VERIFIED** | 50 | 50 | true |
| `driver-binding-current.json` | **VERIFIED** | 37 | 103 | true |
| `compsales-binding-current.json` | **VERIFIED** | 4 | 17 | true |

KPI rerun receipt SHA-256 `f76b1404c69dbe75537984233e9a2a1e3482689ce5c08b805e5f9a4f7701c5bd` matches Review's reproduced `verify-kpi-binding.json`. Driver/compsales receipts: `verify-driver-binding.json` `5f46c363…`; `verify-compsales-binding.json` `eca06ac5…`. Native Excel was not re-run (at most two attempts unused).

## Commands and measured results

| Check | Measured result |
|---|---|
| Baseline authentication | **pass** — B `f3e83259…` |
| Git-first artifact reconciliation | **50/50** protected; **8/8** extracts; obsolete paths absent |
| Independent driver / compsales derivation | **37/37** and **4/4** |
| `scripts/verify_cached_workbook.py` KPI / driver / compsales | **VERIFIED** / **VERIFIED** / **VERIFIED** |
| `python -m bav check Lululemon` | **0** |
| `python -m bav check FastRetailing` | **0** |
| Protected + fiscal + Margin + source-availability | **46 passed**, no exclusions |
| `test_current_build` + CLI + contract | **69 passed** |
| Transient workbook recreated | **no** |
| Rebuild | **no** (no demonstrated defect) |

## Remaining toward Completion

Migration reconciliation for this bounded attempt is returned for Review. Input incorporation does not certify Completion; migration acceptance does not finish the Session Endpoint.

- Expanded historical revenue/component-margin Drivers, seven-part validation, strict company-name Word/PDF publication, and BAV-first presentation remain mandatory subsequent Session work.
- Earlier normalization, broader source-workflow, and normalized-per-share obligations remain deferred.
- No independent remaining migration blocker from the superseded transient-workbook or pre-removal timing conditions. Actual evidence loss, broken provenance, failed verification, and other unmet active requirements were not found.

## Next priority (not started)

Not started. This bounded attempt does not begin the next implementation step.

