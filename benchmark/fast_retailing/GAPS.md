# Fast Retailing Step 9M.0 Gap Queue

Evidence basis for Step 9M.1. Measurement only — no speculative production redesign here.

Categories:
- **A** source-extraction / provenance defect
- **B** generic line-identity / resolver / classifier gap
- **C** accounting-model scope gap
- **D** optional-module input-contract gap
- **E** comparative/restatement/share-basis conflict

## Observed engine stages (26f22b7)

| Stage | Result |
|---|---|
| source fixture load | pass |
| identity validation | pass |
| financial reconciliation | **fail** — BS A ≠ L+E by 1 for FY2023 and FY2024 |
| ReferenceModelBuilder | **fail** — unclassified `Other financial assets` |
| workbook generation / Check | skipped |

## Gaps

### G1 — Published BS totals off by one unit (FY2023, FY2024)

- **Category:** A / C
- **Stage:** `3_reconciliation`
- **Exact mismatch:** `total_assets - (total_liabilities + total_equity) = 1` for `2023-08-31` and `2024-08-31` (FY2025 balances).
- **Source facts:** audited statement totals in CFS2023/CFS2024/CFS2025 primary BS pages (JPY millions).
- **Synthetic coverage:** DEMO/cross-company fixtures always balance; 1-unit published rounding is not covered.
- **Why generalizable:** Real audited statements sometimes publish rounding residuals. The Trainer needs an explicit policy (strict fail vs documented rounding tolerance vs requiring detail-rollforward proof) without inventing balancing plugs.

### G2 — Unclassified generic financial-asset row blocks model construction

- **Category:** B
- **Stage:** `4_reference_model_builder`
- **Exact exception:** `UnclassifiedBalanceSheetLineError: Cannot safely classify balance-sheet line 'Other financial assets'; provide classificationOverrides['Other financial assets']`
- **Source facts:** BS current `Other financial assets` (concept `other_financial_assets_current`) and related generic financial / derivative rows.
- **Synthetic coverage:** DEMO lacks these ambiguous financial instrument rows.
- **Why generalizable:** Many IFRS corporates present generic “other financial assets/liabilities” and derivatives that require guided classification rather than hard failure before any workbook exists.

### G3 — Split lease liabilities omit lease diagnostic module (expected under 9L.1)

- **Category:** D
- **Stage:** module applicability (pre-workbook)
- **Exact behavior:** `lease_liability_availability.ambiguous == True` because current + non-current lease liability rows share concept resolution; module omitted.
- **Source facts:** current lease liabilities `126,830`; non-current `386,670`; Note 17 aggregate present value `513,501` (≠ sum `513,500` by one unit).
- **Synthetic coverage:** manufacturer uses one aggregate lease line; split case is tested to omit diagnostics.
- **Why generalizable:** Primary-statement split presentation is common; optional diagnostics need an explicit aggregation contract (note total vs sum of splits) before enabling the module.

### G4 — Lease income-side consistency not treatment-conditioned

- **Category:** C
- **Stage:** conceptual probe (not first thrown exception)
- **Exact behavior:** Accounting Judgment can reclassify lease liabilities operating vs financial, but `compute_anchor()` net interest still uses reported finance income/costs without isolating Note 17 lease interest `8,464`.
- **Source facts:** Note 17 interest on lease liabilities FY2025 `8,464`; primary finance costs `(12,834)`.
- **Synthetic coverage:** lease judgment tests check NOA/Net Debt movement, not NOPAT/interest consistency.
- **Why generalizable:** Operating-lease treatment for RNOA/Spread analysis generally requires a matching income-side lease-interest policy once lease interest is disclosed.

### G5 — NCI / parent attribution vs total profit and equity

- **Category:** C
- **Stage:** conceptual probe
- **Exact facts:** total profit `459,153` vs parent `433,009` + NCI `26,143` (= `459,152`, one-unit residual); total equity `2,327,501` vs parent equity `2,273,115` + NCI equity `54,385`.
- **Source facts:** CFS2025 IS page 3 and BS page 2.
- **Synthetic coverage:** DEMO has no NCI.
- **Why generalizable:** Parent-attributable earnings/equity must be first-class when NCI is material; totals alone are insufficient for ROE/per-share bridges.

### G6 — Five-year diluted share basis omitted after 3-for-1 split

- **Category:** E / D
- **Stage:** fixture construction / module applicability
- **Exact behavior:** `historical_shares = null` on the five-year model payload; per-share module omitted.
- **Source facts:** 3-for-1 split effective 1 March 2023; FY2025 basic WAS `306,786,602` + dilutive `461,202` → derived diluted WAS `307,247,804`; pre-split WAS in FY2021/FY2022 filings not treated as restated without invention.
- **Synthetic coverage:** share-enabled fixtures assume a comparable series.
- **Why generalizable:** Stock splits require audited restated comparatives (or an explicit restatement contract) before multi-year per-share diagnostics.

### G7 — Overlap conflicts from restated EPS after split

- **Category:** E
- **Stage:** cross-filing precedence
- **Exact conflicts (3 remaining after correcting a 2021 NCI USD misparse):**
  - FY2022 basic/diluted EPS yen amounts restated in CFS2023 vs CFS2022 presentation.
  - FY2024 CF “Others, net” (financing) differs between CFS2024 and CFS2025 comparatives.
- **Source facts:** recorded in `provenance.json` → `conflicts`.
- **Synthetic coverage:** none for audited restatement overlaps.
- **Why generalizable:** Latest-audited-presentation must remain explicit; silent overwrites are forbidden.

## Corrected extraction note (A — closed in 9M.0)

CFS2021 IS line `Non-controlling interests 40 5,836 53,109` was initially misread so that the USD thousands figure `53,109` was treated as JPY millions for FY2021. Corrected to JPY `40` / `5,836`. This was a transcription defect, not an engine defect.

## Step 9M.1 guidance (non-prescriptive)

Required invariants to preserve when planning fixes:

1. Do not invent plugs to force BS identity when published totals disagree by rounding.
2. Generic financial instrument rows must be classifiable via judgment/overrides rather than hard-stopping the whole model.
3. Parent vs NCI earnings and equity must be handled consistently when both are disclosed.
4. Split lease diagnostics need an explicit aggregation contract; do not silently sum.
5. Lease classification treatment and lease-interest income-side treatment must eventually be internally consistent when lease interest is disclosed.
6. Multi-year per-share analysis requires an audited comparable share basis.

Do not implement these fixes in Step 9M.0.
