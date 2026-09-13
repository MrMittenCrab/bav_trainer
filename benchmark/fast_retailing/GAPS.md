# Fast Retailing Gap Queue

Evidence basis for Step 9M.2D. Measurement only for remaining gaps — no speculative production redesign here.

Categories:
- **A** source-extraction / provenance defect
- **B** generic line-identity / resolver / classifier gap
- **C** accounting-model scope gap
- **D** optional-module input-contract gap
- **E** comparative/restatement/share-basis conflict

## Observed engine stages (Step 9M.2D)

| Stage | Result |
|---|---|
| source fixture load | pass |
| identity validation | pass |
| financial reconciliation | **pass** (G1 closed) |
| ReferenceModelBuilder | **pass** (G1B rounding envelope; G2/G2B/G2C closed) |
| workbook generation | **pass** |
| blank Check | **pass** (0/294 correct; 294 blank) |
| filled Check | **pass** (294/294 correct) |

## Gaps

### G1 — Published BS totals off by one unit (FY2023, FY2024) — **CLOSED in Step 9M.2A**

- **Category:** A / C
- **Stage:** `3_reconciliation`
- **Resolution:** `validate_balance_sheet` now accepts an absolute residual of at most **1.0** reporting unit without plugs or source mutation. Residuals strictly above `1.0` still fail.
- **Evidence:** Fast Retailing Stage 3 passes; standardized payload unchanged.

### G1B — Rounded detail-to-total accumulation — **CLOSED in Step 9M.2D**

- **Category:** C
- **Stage:** `4_reference_model_builder` (`check_reformulation_integrity`)
- **Prior policy:** fixed absolute tolerance of `1.0` reporting unit for asset-detail,
  liability-detail, and equity-bridge gaps (too strict once many independently rounded
  detail lines are summed against independently rounded published totals).
- **Resolution:** count-derived reporting-unit rounding envelope
  `max(base_tolerance, 0.5 * (detail_count + 1))`, with separate asset / liability /
  equity-bridge contributor counts from classified reformulation decisions
  (`Equity` / `Exclude` do not count as asset or liability observations). Explicit
  caller `tolerance` remains a floor. No plugs, no source mutation, no company-specific
  constant. Top-level Stage-3 G1 rule `Assets = Liabilities + Equity` absolute residual
  `<= 1.0` is unchanged.
- **Fast Retailing evidence (unchanged arithmetic):** asset gaps
  `(-4, -8, -8, -7, -8)`, liability gaps `(-6, -5, -6, -5, -6)`, equity gaps
  `(+2, -3, -1, -1, -2)` with 16 asset + 13 liability detail rows → envelopes
  8.5 / 7.0 / 15.0. Gaps sit inside those bounds; integrity now passes.
- **Material omission still fails:** equal asset/liability omissions of 30 remain outside
  the count-derived envelope and still raise `ReformulationIntegrityError`.

### G2 — Unclassified generic financial-instrument rows — **CLOSED in Step 9M.2A**

- **Category:** B
- **Stage:** `4_reference_model_builder`
- **Resolution:** Explicit side-aware financial-instrument concepts (`other_financial_assets_current`, `financial_assets_noncurrent`, derivative asset/liability variants, etc.) now classify as guided Accounting Judgment cases (`ambiguous=True`, financial default + side-appropriate operating alternative). Vague labels without usable concept evidence still fail closed.
- **Evidence:** known G2 rows no longer appear in Stage-4 failure messages; synthetic judgment cases generate for all four side-aware codes.

### G2B — Residual other asset/liability concepts — **CLOSED in Step 9M.2B**

- **Category:** B
- **Stage:** `4_reference_model_builder`
- **Resolution:** Exact current/non-current residual concepts
  (`other_current_assets`, `other_noncurrent_assets`, `other_current_liabilities`,
  `other_noncurrent_liabilities`) now produce guided operating-vs-financial Accounting
  Judgment cases (operating default). Bare labels `Other assets` / `Other liabilities`
  without those concepts still fail closed. No company-specific production rule.
- **Evidence:** Fast Retailing residual rows classify with the four new judgment codes;
  Stage 4 no longer fails on `Other assets` / `Other liabilities`.

### G2C — Deterministic tax/provision/equity concepts — **CLOSED in Step 9M.2C**

- **Category:** B
- **Stage:** `4_reference_model_builder`
- **Resolution:** Exact standardized concepts classify deterministically
  (`ambiguous=False`, no new judgment templates):
  - `current_tax_liabilities` → Operating Working Capital Liability
  - `provisions_current` → Operating Working Capital Liability
  - `provisions_noncurrent` → Operating Long-Term Liability
  - `capital_stock` / `capital_surplus` / `other_components_of_equity` /
    `noncontrolling_interests` → Equity
  Classification is concept-driven with compatible label-family guards; no broad
  label fallback; no company-specific production rule. **G5 remains open** despite
  NCI → Equity structural classification (parent attribution / ROE / per-share logic
  unchanged).
- **Evidence:** every Fast Retailing non-subtotal BS detail row is classifiable;
  Stage 4 no longer fails on `Current tax liabilities` or the other six concepts.

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
- **Source facts:** recorded in `reconciled/conflicts.json` (and mirrored conflict count in provenance).
- **Synthetic coverage:** none for audited restatement overlaps.
- **Why generalizable:** Latest-audited-presentation must remain explicit; silent overwrites are forbidden.

## Post-9M.2D audit result

- **Stages 1–7:** all **pass**
  - Stage 4: `expected_specs=294 lease_specs=0 fixed_asset_specs=35`
  - Stage 6 blank Check: `correct=0 incorrect=0 blank=294 total=294`
  - Stage 7 filled Check: `correct=294 total=294`
- **First failing stage / exception:** none
- **ReferenceModelBuilder completed:** yes
- **Workbook generation / blank Check / filled Check:** reached and passed
- **Note:** G3–G7 remain open as measured product/accounting gaps (split-lease
  module omitted, lease-interest treatment, NCI attribution, share-basis / per-share
  omission, restatement conflicts). They are no longer the first thrown Stage-4
  exception; select the next checkpoint from these remaining substantive gaps.

## Corrected extraction note (A — closed in 9M.0)

CFS2021 IS line `Non-controlling interests 40 5,836 53,109` was initially misread so that the USD thousands figure `53,109` was treated as JPY millions for FY2021. Corrected to JPY `40` / `5,836`. This was a transcription defect, not an engine defect.

## Guidance for later checkpoints

1. Do not invent plugs to force BS identity when published totals disagree by rounding (G1 policy already encodes `<= 1.0` acceptance).
2. Vague unsupported rows (e.g. bare `Other assets`) should remain fail-closed or receive an explicit guided contract — do not auto-classify from the word `other` alone.
3. Parent vs NCI earnings and equity must be handled consistently when both are disclosed.
4. Split lease diagnostics need an explicit aggregation contract; do not silently sum.
5. Lease classification treatment and lease-interest income-side treatment must eventually be internally consistent when lease interest is disclosed.
6. Multi-year per-share analysis requires an audited comparable share basis.
