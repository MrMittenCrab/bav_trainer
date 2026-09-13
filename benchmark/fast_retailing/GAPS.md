# Fast Retailing Gap Queue

Evidence basis for Step 9M.3E. Measurement only for remaining gaps — no speculative production redesign here.

Categories:
- **A** source-extraction / provenance defect
- **B** generic line-identity / resolver / classifier gap
- **C** accounting-model scope gap
- **D** optional-module input-contract gap
- **E** comparative/restatement/share-basis conflict

## Observed engine stages (Step 9M.3E)

| Stage | Result |
|---|---|
| source fixture load | pass |
| identity validation | pass |
| financial reconciliation | **pass** (G1 closed) |
| ReferenceModelBuilder | **pass** (380 specs; ownership_specs=34; lease_specs=18; per_share_specs=18) |
| workbook generation | **pass** |
| blank Check | **pass** (0/380 correct; 380 blank) |
| filled Check | **pass** (380/380 correct) |

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

### G3 — Split lease-liability aggregation contract — **CLOSED in Step 9M.3A**

- **Category:** D
- **Stage:** module applicability / lease diagnostics
- **Resolution:** `resolve_lease_liability_source()` prefers one unique explicit
  `lease_liability` aggregate when present; otherwise accepts exactly one
  `lease_liability_current` plus one `lease_liability_noncurrent` and sums them
  period-by-period. Python expected values and workbook `lease_liability_source_link`
  formulas use the same source rows. Duplicate/partial/unclear presentations remain
  fail-closed. Generic duplicate `lease_liability` concepts remain ambiguous (9L.1).
- **Fast Retailing evidence:** source mode `split`; FY2025 diagnostic total
  `126,830 + 386,670 = 513,500`; Note 17 `lease_liability_total` remains `513,501`
  as independent provenance (one-unit difference preserved — no plug / no note
  substitution / no source mutation). `lease_specs=18`; Stages 1–7 pass with
  `expected_specs=312`. Two distinct lease Accounting Judgment cases remain.
- **G4 remains open:** this step changes only the historical liability diagnostic
  source contract; it does not condition interest expense/income on lease
  classification treatment.

### G4 — Treatment-conditioned lease interest — **CLOSED in Step 9M.3B**

- **Category:** C
- **Stage:** `compute_anchor` / Condensed net-interest formulas
- **Resolution:** Optional model-only `historical_lease.lease_interest_expense`
  is populated only from a complete unambiguous axis of reported
  `lease_interest_expense` note facts. Under uniform operating lease treatment,
  financing net interest excludes disclosed lease interest
  (`reported_net_interest - lease_interest_expense`). Under uniform financial
  treatment, reported net interest is unchanged. Mixed current/non-current lease
  treatment with one aggregate interest series raises
  `InconsistentLeaseTreatmentError` (Excel: `NA()`). No ABS/plugs/allocation;
  raw finance-cost lines and Note 17 lease-liability balance remain untouched.
- **Fast Retailing evidence:** FY2021–FY2025 lease interest
  `4847 / 4757 / 5187 / 6507 / 8464`; default operating net interest equals
  reported primary net interest minus that series; all-financial override restores
  reported net interest and raises NOA/Net Debt/NOPAT accordingly; diagnostic BS
  lease total remains `513500` vs Note 17 `513501`. Stages 1–7 pass with
  `expected_specs=312` (no new practice family).

### G5 — Parent / NCI attribution and parent ROE — **CLOSED in Step 9M.3C**

- **Category:** C
- **Stage:** optional Ownership Attribution schedule / per-share numerator
- **Resolution:** Four canonical concepts
  (`profit_attributable_to_owners`, `profit_attributable_to_nci`,
  `equity_attributable_to_owners`, `noncontrolling_interests`) resolve uniquely.
  Optional module computes bridges (tolerance `1.5` reporting units) and Parent ROE
  = parent profit / average parent equity. Consolidated BAV DuPont / NOA / Net Debt /
  NOPAT unchanged. Per-share earnings numerator uses parent profit when ownership is
  complete; partial/ambiguous ownership fails closed; no ownership → consolidated NI.
- **Fast Retailing evidence:** FY2025 profit bridge gap `-1`, equity bridge gap `-1`
  (accepted); `ownership_specs=34`; parent-attributable per-share numerator active under G6.
- **Synthetic coverage:** whole-owned companies retain prior EPS; NCI+shares fixtures
  use parent profit numerator.

### G6 — Five-year diluted share basis omitted after 3-for-1 split — CLOSED in Step 9M.3D

- **Category:** E / D → closed
- **Stage:** fixture construction / module applicability → resolved by share-basis resolver
- **Resolution:** Accept validated derived diluted WAS (`basic + dilutive`); infer one
  integer 3-for-1 factor from the audited FY2022 same-period restatement anchored by
  `RESTATED_COMPARATIVE` diluted EPS; analytically restate FY2021 only; emit
  `historical_shares` in financial-statement units with `basis=split_adjusted`.
- **Fast Retailing evidence:** actual-share axis
  `306871785, 306969624, 307138870, 307231804, 307247804` → statement units
  `306.871785 … 307.247804`; `per_share_specs=18`; `per_share_attribution_specs=16`;
  `expected_specs=380`; FY2025 EPS ≈ `1409.32`.
- **Preserved:** raw share facts; G7 overlap/supplemental conflicts unchanged (3 / 3).

### G7 — Overlap conflicts from restated EPS after split — **CLOSED in Step 9M.3E**

- **Category:** E → closed
- **Stage:** cross-filing precedence
- **Resolution:** Deterministic selection with **retained disagreements**. Closure means
  selected values and precedence reasons are verified and locked; it does **not** mean
  source values agree or that conflict records disappear. Both observations remain in
  reconciliation and serialized audit payloads (`conflicts.json` / provenance).
- **Selected primary presentations (3 overlap conflicts):**
  - FY2022 basic EPS: `2675.30 → 891.77` via `restated_comparative_precedence`
    (CFS2022 current vs CFS2023 restated comparative).
  - FY2022 diluted EPS: `2671.29 → 890.43` via `restated_comparative_precedence`
    (CFS2022 current vs CFS2023 restated comparative).
  - FY2024 CF financing “Others, net”: `85 → 63` via `later_audited_presentation`
    (CFS2024 current vs CFS2025 comparative). No cause inferred for the cash-flow
    difference beyond the recorded later audited presentation.
- **Supplemental disagreements (3):** FY2022 `basic_weighted_average_shares`,
  `diluted_eps`, and `dilutive_shares` remain source-bound after share-basis resolution
  (`cross_filing_supplemental_disagreement`). Counts stay `overlap=3` /
  `supplemental=3`.
- **Share axis (G6, unchanged):** validated split-adjusted `historical_shares` model
  axis is analytical; raw reported share facts and conflict artifacts are unchanged.
- **Evidence:** Stages 1–7 pass; `expected_specs=380`; blank Check `0/0/380`; filled
  Check `380/0/0`.

## Post-9M.3E audit result

- **Stages 1–7:** all **pass**
  - Stage 4: `expected_specs=380 lease_specs=18 ownership_specs=34 per_share_specs=18 per_share_attribution_specs=16 fixed_asset_specs=35`
  - Stage 6 blank Check: `correct=0 incorrect=0 blank=380 total=380`
  - Stage 7 filled Check: `correct=380 total=380`
- **First failing stage / exception:** none
- **Note:** G7 closed by verified retained-conflict policy; conflict records remain.

## Corrected extraction note (A — closed in 9M.0)

CFS2021 IS line `Non-controlling interests 40 5,836 53,109` was initially misread so that the USD thousands figure `53,109` was treated as JPY millions for FY2021. Corrected to JPY `40` / `5,836`. This was a transcription defect, not an engine defect.

## Guidance for later checkpoints

1. Do not invent plugs to force BS identity when published totals disagree by rounding (G1 policy already encodes `<= 1.0` acceptance).
2. Vague unsupported rows (e.g. bare `Other assets`) should remain fail-closed or receive an explicit guided contract — do not auto-classify from the word `other` alone.
3. Parent vs NCI earnings and equity are first-class when both are disclosed (G5 closed); parent ROE is separate from consolidated DuPont ROE.
4. Split lease diagnostics use an explicit aggregate-or-split source contract (G3 closed); do not silently invent aggregates from vague labels.
5. Lease classification treatment and disclosed lease-interest income-side treatment are linked when a complete reported lease-interest axis exists (G4 closed).
6. Multi-year per-share analysis uses an audited comparable share basis (G6 closed); the per-share numerator remains ownership-safe under G5.
7. Restatement / later-presentation conflicts remain recorded with both observations even after deterministic selection (G7 closed).
