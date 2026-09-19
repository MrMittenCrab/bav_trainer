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
