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
