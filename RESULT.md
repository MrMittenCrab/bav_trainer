# RESULT.md — Step 3.2.7 Select supported management disclosures through production admission

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
