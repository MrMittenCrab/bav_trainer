# Lululemon Gap Map (Step 9M.2)

Evidence-only queue from the untouched FY2022–FY2025 filing-JSON → reconcile → build baseline.
Categories match IMPLEMENTATION.md Task 4:

1. extracted/source-data defect
2. generic ingestion/reconciliation defect
3. generic historical BAV analytical gap
4. qualitative target-research item outside the workbook engine

## Current engine stage

| Stage | Result |
|---|---|
| validate-source (4 filings) | **pass** |
| reconcile | **pass** (overlap=3, supplemental=0, sources=4/4) |
| capex module (G4) | **pass** — stored CF `capital_expenditures` resolves through `payments_for_ppe`; four-period diagnostics available |
| interest source evidence (G9) | **assessed / gated** — standalone `interest_expense` / `interest_income` still **not found**; partial-period condensed links and aggregate CoD eligibility now agree with Python; source completeness remains open |
| ReferenceModelBuilder / build | **pass** — matched Trainer/Answer-Key pair; `expected_specs=273`; lease-ROU (12) and deferred-tax (13) practice cells added; interest-dependent families excluded from practice/Check |

## Gaps (priority order)

### G1 — Unclassified contract / deferred-revenue-like liability (gift cards) — **OPEN**

- **Category:** 3 (generic historical BAV / classifier gap)
- **Stage:** `4_reference_model_builder` / `build`
- **Evidence:** `Unredeemed gift card liability` / `unredeemed_gift_card_liability` with material balances (251,478 → 316,632 USD thousands) fails closed. First build exception names this label.
- **Why it matters:** Blocks any LULU Trainer/Answer-Key. Gift-card / deferred-revenue operating WC liabilities are common for consumer retailers and are pedagogically central to working-capital diagnostics.
- **Proposed next step:** Step **9M.2.1** — add a generic, non-issuer-specific classification (deterministic or guided judgment) for explicit gift-card / unearned-revenue liability concepts, with non-LULU regression coverage.

### G2 — US “Property and equipment” wording + PPE concept identity — **OPEN**

- **Category:** 3 (generic classifier + line-resolver identity)
- **Stage:** build (behind G1); also fixed-asset module gate
- **Evidence:**
  - Classifier does not match label `Property and equipment, net` (no “plant”; “property and equipment” not in LT-asset label rules).
  - Concept on payload is `property_plant_and_equipment`; fixed-asset resolver looks for `property_plant_equipment`.
  - Label alias exact set includes `property and equipment` but normalized label is `property and equipment net`, so PPE fails to resolve even for module probes (`fixed_asset_applicable=False` while D&A resolves).
- **Why it matters:** Capex/depreciation/asset-intensity diagnostics cannot activate; reformulation cannot complete after G1.

### G3 — Exact `common_stock` equity concept — **OPEN**

- **Category:** 3 (generic classifier)
- **Stage:** build (behind G1)
- **Evidence:** `Common stock` / `common_stock` fails closed. Deterministic equity mapping covers `capital_stock` (with “capital stock” label tokens) but not `common_stock`; label equity rules omit bare “common stock” (by design vs redeemable stock).
- **Why it matters:** Ordinary US equity presentations use “Common stock”; reformulation cannot complete without a safe exact-concept rule or guarded label rule.

### G4 — Capex concept naming (`capital_expenditures` vs `payments_for_ppe`) — **CLOSED** (Step 9M.2.4.1.1.1.17)

- **Category:** 3 (generic line-identity / optional-module contract)
- **Stage:** module applicability (post-build)
- **Evidence (before):** CF investing row `Purchase of property and equipment` / stored concept `capital_expenditures` present (−638,657 / −651,865 / −689,232 / −680,802); `capex_applicable=False` because resolver required exact `payments_for_ppe`.
- **Evidence (after):** same stored concept, label, signs, values, and provenance; `capex_applicable=True` via shared explicit-concept alias `capital_expenditures` → `payments_for_ppe`. Independent four-period `ppe_capex` 638657 / 651865 / 689232 / 680802 against supplied revenue 8110518 / 9619278 / 10588126 / 11102600. Round-trip preserves `capital_expenditures`. Interest absence is now availability-gated (G9) rather than a capex reinterpretation.
- **Why it mattered:** Source-supported historical capex intensity was invisible to the learner despite explicit CF facts.

### G5 — Lease ROU and deferred-tax concept aliases — **CLOSED** (Step 9M.2.4.1.1.1.20)

- **Category:** 3 (generic line-identity / optional-module contract)
- **Stage:** module applicability (post-build)
- **Evidence (before):** BS `right_of_use_lease_asset` / “Right-of-use lease assets” and `deferred_tax_asset` / `deferred_tax_liability` present; `lease_rou_applicable=False` and deferred-tax availability False because modules required plural canonical concepts.
- **Evidence (after):** same stored concepts, labels, signs, values, and provenance. Shared explicit-concept aliases `right_of_use_lease_asset` → `right_of_use_assets`, `deferred_tax_asset` → `deferred_tax_assets`, `deferred_tax_liability` → `deferred_tax_liabilities`. Independent four-period ROU 969419 / 1265610 / 1416256 / 1630181, DTA 6402 / 9176 / 17085 / 24037, DTL 55084 / 29522 / 98188 / 52278, net positions −48682 / −20346 / −81103 / −28241. Practice surface 248 → 273 (lease_rou +12, deferred_tax +13). Source links `'Balance Sheet'!B26` / `B21` / `B27`. No inferred lease interest, deferred-tax expense, cash-tax effects, recoverability, or repayment flows.
- **Why it mattered:** Source-supported lease-asset intensity and deferred-tax diagnostics were invisible to the learner despite explicit BS facts.

### G6 — Comparative FY2021 period not on canonical axis — **OPEN (low)** / 2022-01-30 admitted Step 9M.2.4.1.1.1.30; 2021-01-31 still excluded

- **Category:** 2 (generic ingestion/reconciliation period-axis policy) and/or 1 if earlier BS is desired from notes
- **Stage:** reconcile (canonical axis is now five periods via explicit admission)
- **Evidence (before):** FY2022 extracted IS includes 2021-01-31 and 2022-01-30; reconciled axis started at 2023-01-29 (four filing year-ends only).
- **Evidence (Step 9M.2.4.1.1.1.29):** assessment established 2022-01-30 IS/BS/CF eligibility and 2021-01-31 missing-BS ineligibility. Disposable five-period generation produced 486 exercises vs accepted 376 with **0** existing expected-value changes.
- **Evidence (Step 9M.2.4.1.1.1.30):** generic `--admit-period` / `admit_periods` adds a comparative date only when selected IS+BS+CF coverage exists. Default remains filing year-ends. Canonical Lululemon reconcile admits `2022-01-30` only. Axis `2022-01-30, 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01`. Practice map **376 → 486** (+110, removed 0, changed existing expected values 0). Check blank/filled/incorrect-injection `(486,0,0,486)` / `(486,0,0,486)` / `(0,1,485,486)`; Trainer 486 blank yellow without Notes; Answer Key 486 formulas with nonempty Notes; unavailable displays **74 → 101**. CF `change_in_accounts_receivable` omitted on the five-period axis (34→33), not zero-filled. Provenance records `admitted_comparative_periods=["2022-01-30"]` and `excluded_comparative_periods=["2021-01-31"]`; 2021-01-31 observations remain `outside_model_axis`. Fast Retailing remains 577 with unchanged release hashes.
  - **2021-01-31 remains ineligible:** FY2022 IS/CF only; **no BS in any supplied filing or PDF p49**. CF beginning cash is not a substitute BS. Requesting `2021-01-31` is rejected before writing outputs.
- **Why it matters:** 2022-01-30 now supplies opening/comparable history. FY2020/FY2021 BS is still missing, so six-period history stays closed.
- **Proposed next step:** Do not promote 2021-01-31 without a complete selected BS. Parent 9M.2.4.1.1.1 / Step 9 acceptance remain unresolved.

### G7 — Empty `note_facts` (segments, store KPIs, lease maturity detail) — **OPEN**

- **Category:** 1 (extracted/source-data defect) primarily; 4 for qualitative MD&A interpretation
- **Stage:** upstream extraction
- **Evidence:** all four LULU JSON files have `note_facts: []` while share_facts are populated.
- **Why it matters:** Segment economics, store/sq-ft KPIs, and richer lease disclosures cannot enter optional modules until extracted with provenance.

### G8 — Historical interpretation / research narrative — **DEFERRED**

- **Category:** 4
- **Stage:** n/a (outside workbook engine for this step)
- **Evidence:** TARGET.md asks for economic interpretation of WC, RNOA, dilution, etc. Workbook generation is no longer blocked at interest; no LULU-specific qualitative grading layer required here.

### G9 — Required interest lines absent from supplied filings — **OPEN (source completeness)** / engine gated (Step 9M.2.4.1.1.1.19)

- **Category:** 1 (unextracted note facts) and 3 (availability-gated historical analysis)
- **Stage:** `compute_anchor` / `ReferenceModelBuilder` / `build`
- **Evidence (Step 9M.2.4.1.1.1.18):** all four IS pages present only `Other income (expense), net` (4163 / 43059 / 70380 / 28352) between operating income and pretax. No `interest_expense` / `interest_income` / finance-cost/income line. MD&A says other-income changes were “primarily” interest income but gives no isolated amount. Supplemental cash “Interest paid” 116 / 234 / 478 / 1028 (USD thousands; cross-filing consistent) is cash, not IS expense, and is omitted from empty `note_facts`. Revolvers unused (letters of credit only) — not a reported zero. Lease notes disclose operating lease expense, not lease interest. `historical_lease` is null.
- **Evidence (Step 9M.2.4.1.1.1.19):** generic gating plus partial-period repair. Unchanged facts. Missing interest periods display `Source unavailable` on condensed source links (no formula to a blank source cell); reported zero keeps the source formula; fully absent lines stay omitted. Opening-period interest absence does not block a numeric comparable CoD average; any comparable CoD period lacking interest keeps hist-avg unavailable; supported undefined-ratio history still uses 4% and unavailable history does not. Python, workbook formula text, and availability sidecar agree. Net Interest / NIAT / NOPAT / NOPAT Margin / RNOA / After-tax CoD / Spread / ROE decomposed / hist-avg CoD remain `Source unavailable` on Lululemon and are excluded from the practice/Check surface. Independent outputs remain (revenue 8110518 / 9619278 / 10588126 / 11102600; `ppe_capex` 638657 / 651865 / 689232 / 680802). `resolve_line(..., required=True)` still raises `MissingLineError` for explicit interest requests. No invented interest, no 4% fallback for unavailable history, no mixed-line/cash-interest alias.
- **Evidence (Step 9M.2.4.1.1.1.20):** G5 lease-ROU / deferred-tax aliases added 25 practice cells without mutating interest gating. Availability sidecar hash unchanged; 74 `Source unavailable` displays per workbook retained; hist-avg CoD still `absent_line`. Practice/Check surface is now 273 cells and still omits interest-dependent families.
- **Why it matters:** Source-interest completeness remains unresolved. The learning product can now proceed on supported historical analysis without inventing the missing lines.
- **Proposed next step:** Do not infer interest. Optional later `note_facts` capture of Interest paid still would not satisfy standalone IS interest. Remaining Lululemon gaps are G6–G8 and parent Plan closure.

## Closed / non-gaps this step

- Source binding validation for all four PDFs — **pass** (not a source-input defect).
- Deterministic reconciliation with retained overlap conflicts — **pass**.
- Diluted WAS scaled into statement units and bound — **pass** (`basis=reported`).
- No issuer-specific production branch introduced — **pass**.

## Highest-value next implementation step

**Remaining Lululemon historical gaps after gated interest and G5 aliases:** G7 (empty `note_facts`), G6 period-axis, G8 interpretation deferral, and parent Plan closure (A5 / B8 / E10). Source-interest completeness stays unresolved. Do **not** invent interest or declare Step 9 complete.
