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
| interest source evidence (G9) | **assessed / gated** — standalone `interest_expense` / `interest_income` still **not found**; engine now omits interest-dependent outputs instead of failing the workbook |
| ReferenceModelBuilder / build | **pass** — matched Trainer/Answer-Key pair; `expected_specs=248`; interest-dependent families excluded from practice/Check |

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

### G5 — Lease ROU and deferred-tax concept aliases — **OPEN**

- **Category:** 3 (generic line-identity)
- **Stage:** module applicability
- **Evidence:**
  - BS has `right_of_use_lease_asset` / “Right-of-use lease assets” but `lease_rou_applicable=False` (resolver concept `right_of_use_assets`).
  - BS has `deferred_tax_asset` / `deferred_tax_liability` but deferred-tax module expects pluralized concept forms; availability False.
- **Why it matters:** Lease asset intensity and deferred-tax diagnostics stay fail-closed despite source lines.

### G6 — Comparative FY2021 period not on canonical axis — **OPEN (low)**

- **Category:** 2 (generic ingestion/reconciliation period-axis policy) and/or 1 if earlier BS is desired from notes
- **Stage:** reconcile
- **Evidence:** FY2022 extracted IS includes 2021-01-31 and 2022-01-30; reconciled axis starts at 2023-01-29 (four filing year-ends only). Plan target range FY2021–FY2025 is only partly realized.
- **Why it matters:** Shorter history for growth/DuPont bridges; not a build blocker.

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
- **Evidence (Step 9M.2.4.1.1.1.19):** generic source-availability gating. Unchanged facts. Python and Excel agree: Net Interest / NIAT / NOPAT / NOPAT Margin / RNOA / After-tax CoD / Spread / ROE decomposed / hist-avg CoD display `Source unavailable` and are excluded from the 248-cell practice/Check surface. Independent outputs remain (revenue 8110518 / 9619278 / 10588126 / 11102600; `ppe_capex` 638657 / 651865 / 689232 / 680802). `resolve_line(..., required=True)` still raises `MissingLineError` for explicit interest requests. No invented interest, no 4% fallback, no mixed-line/cash-interest alias.
- **Why it matters:** Source-interest completeness remains unresolved. The learning product can now proceed on supported historical analysis without inventing the missing lines.
- **Proposed next step:** Do not infer interest. Optional later `note_facts` capture of Interest paid still would not satisfy standalone IS interest. Remaining Lululemon gaps are G5–G8 and parent Plan closure.

## Closed / non-gaps this step

- Source binding validation for all four PDFs — **pass** (not a source-input defect).
- Deterministic reconciliation with retained overlap conflicts — **pass**.
- Diluted WAS scaled into statement units and bound — **pass** (`basis=reported`).
- No issuer-specific production branch introduced — **pass**.

## Highest-value next implementation step

**Remaining Lululemon historical gaps after gated interest:** G5 (lease ROU / deferred-tax concept aliases), G7 (empty `note_facts`), G6 period-axis, G8 interpretation deferral, and parent Plan closure (A5 / B8 / E10). Source-interest completeness stays unresolved. Do **not** invent interest or declare Step 9 complete.
