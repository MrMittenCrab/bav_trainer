# GOOGL Historical Reference

Internal development reference for Step 9 historical convergence. Evidence is limited to what was inspected in `example/GOOGL_Demo_Integrated_Financials.xlsx` and the current canonical Trainer/Answer Key. Gaps are not filled from general knowledge.

Audit tool: `scripts/audit_reference_workbook.py`  
GOOGL SHA-256 (pre/post inspection): `81faf2882d0df07ecf5def45695431c1935b4f7a94c1e017367596a063063896`  

**Coverage refresh (Step 9N.4):** Exit-gate reconciliation. No remaining concrete high-value historical gap with available source facts; documented deferrals preserved. Lease-repayment module (9N.3) retained. Fast Retailing `expected_specs=491` with `lease_repayment_specs=10`. Exit gate **PASS** — Step 9 complete; next stage is Step 10 driver-based forecasting (not implemented here). See `RESULT.md`.

## Role of the reference

`GOOGL_Demo_Integrated_Financials.xlsx` is the project’s **structural / analytical-depth reference**, not a literal template.

Use it to study how source statements, reformulation, DuPont, earnings-quality analysis, and downstream schedules fit together in one integrated analyst workbook.

Do **not** copy decorative styling, pre-filled answers, quarterly/forecast/valuation/market-monitoring features merely because they exist, pipeline automation, or any company fact not explicitly supplied for a Trainer company.

The Trainer should converge toward the GOOGL workbook’s **integration and historical analytical depth** while preserving Trainer / Answer Key / Check learning mechanics.

## GOOGL workbook inventory

Visible sheets observed (audit + direct label inspection):

| Sheet | Role evidenced |
|---|---|
| Income Statement | As-filed multi-year IS; EPS / diluted shares; **CORE EARNINGS BRIDGE**; quarterly block |
| Balance Sheet | As-filed BS including PPE, operating lease assets/liabilities, goodwill, intangibles, deferred income taxes |
| Cash Flow Statement | As-filed CF including depreciation, **stock-based compensation expense**, purchases of PPE, acquisitions |
| Condensed Financials | NOPAT / NOWC / NOA / Net Debt / Equity; interactive classification table (column L toggles) |
| ALT DuPont | RNOA / margin / turnover / Spread / FLEV / ROE decomposition (linked to Condensed) |
| Earnings Quality | Accruals & cash conversion; Beneish M-Score; Piotroski F-Score; Benford (XBRL-derived) |
| Guidance & Consensus | Management forward statements + consensus ledger |
| Model_Bear / Model_Base / Model_Bull | Forecast drivers, residual-income IVPS, enterprise DCF cross-check |
| Scenario_Summary | Probability-weighted RI valuation, terminal returns, sensitivities |
| Implied Cost of Capital | Price-implied discount rates |
| Valuation Multiples | Historical / forward multiples |

Not evidenced as dedicated structured schedules in the inspected workbook:

- segment P&L / segment ROIC tables (Cloud/YouTube appear only in scenario narrative prose)
- minority / non-controlling interest lines or schedules

## Current Trainer inventory

### Illustrative DEMO surfaces (synthetic; unchanged by Fast Retailing work)

Canonical normalization-enabled demo (`DEMO_HK_Answer_Key.xlsx`, **78 families / 332 cells**) visible surface:

| Sheet / feature | Role |
|---|---|
| Income Statement / Balance Sheet / Cash Flow Statement | Populated historical source facts |
| Condensed Financials | Reformulation schedules (practice formulas) |
| ALT DuPont | RNOA / Spread / FLEV / ROE + FIXED-ASSET INTENSITY CONTEXT + LEASE LIABILITY CONTEXT + LEASE ROU-ASSET CONTEXT when inputs resolve |
| Accounting Judgment | Guided operating/financing treatment (`identity:` selectors) |
| Normalization Judgment + Earnings Normalization | Recurring / non-recurring bridge |
| Earnings Quality | Cash conversion, accruals, optional asset-scaled ratios + trend diagnostics |
| Working Capital Analysis | NOWC intensity / incremental WC diagnostics |
| Profitability / ROE attribution sheets | RNOA margin-turnover and ROE operating/financing change attribution |
| Per Share Analysis | Optional; gated on diluted WAS history (+ normalized EPS bridge when normalization active) |
| Ownership Attribution | Optional; gated on complete parent/NCI profit + equity concepts (absent on ordinary DEMO) |
| Model_* / Scenario_Summary | Hidden deferred placeholders only |

Ordinary / share / cross-company DEMO surfaces (recorded regression counts): `74/312`, `78/332`, `82/346`, `90/384`; services `59/248`, retail `78/331`, manufacturer `74/311`.

### Fast Retailing real-company surface (recorded benchmark; not a new audit)

Distinct from DEMO counts. Post–G1–G7 recorded Stage 4/Check surface:

- **`expected_specs=548`** (blank Check `0/0/548`; filled Check `548/0/0`)
- Module specs (recorded): `lease_specs=18`, `lease_rou_specs=16`, `ownership_specs=34`, `per_share_specs=18`, `per_share_attribution_specs=16`, `fixed_asset_specs=35`, `goodwill_intangibles_specs=58`, `deferred_tax_specs=17`, `capex_specs=10`, `lease_repayment_specs=10`
- Added vs illustrative DEMO when facts resolve: split lease-liability diagnostics, lease ROU-asset intensity, Ownership Attribution (parent/NCI), split-adjusted Per Share Analysis + attribution, goodwill/intangibles intensity context, deferred-tax balance context, PP&E capex practice, lease-repayment cash intensity, cash roll-forward / reported cash reconciliation, reported gross/operating-margin bridge

### Implemented since prior inventory (G3–G6 / related)

| Capability | Status | Notes |
|---|---|---|
| Split lease-liability aggregation | **implemented** | `resolve_lease_liability_source()` accepts unique aggregate **or** exactly one current + one non-current pair summed period-by-period (G3 / 9M.3A) |
| Treatment-conditioned lease interest | **implemented** | Optional `historical_lease.lease_interest_expense`; operating treatment excludes disclosed lease interest from financing net interest; mixed treatment fails closed (G4 / 9M.3B) |
| Parent / NCI attribution + parent ROE | **implemented** | Ownership Attribution schedule when four ownership concepts resolve; per-share numerator uses parent profit when ownership complete (G5 / 9M.3C) |
| Split-adjusted per-share analysis | **implemented** | `historical_shares` with `basis=split_adjusted` drives diluted WAS / EPS practice when share axis resolves (G6 / 9M.3D) |
| Goodwill / intangible intensity & change | **implemented** | ALT DuPont `GOODWILL & INTANGIBLES CONTEXT` when unique BS `goodwill` and/or `intangible_assets` resolve; optional CF `payments_for_intangible_assets` as −reported; no impairment/PPA narrative (9M.5) |
| Acquisition cash / cash-use residual | **implemented (source-gated)** | ALT DuPont `ACQUISITION CASH CONTEXT` when unique CF `acquisition_net_of_cash_acquired` resolves (Lululemon); Fast Retailing / DEMO omit; not FCF, profitability, PPA, or a goodwill roll-forward |
| Share-repurchase cash / cash-use residual | **implemented (source-gated)** | ALT DuPont `SHARE REPURCHASE CONTEXT` when unique CF `repurchase_of_common_stock` resolves (Lululemon); residual additionally requires unique CFO, PP&E-capex and acquisition sources and is omitted rather than zeroed if acquisition is absent; Fast Retailing / DEMO omit; not total distributions, dilution, debt funding, FCF, or a complete cash reconciliation |
| Cash roll-forward / reported cash reconciliation | **implemented (source-gated)** | ALT DuPont `CASH ROLL-FORWARD CONTEXT` when unique explicit CF operating, investing, financing and FX totals resolve (Lululemon + Fast Retailing); teaches `CFO+CFI+CFF+FX`, calculated-minus-reported movement and ending differences, and beginning+movement ending cash; DEMO omits; preserves nonzero reported gaps; no balancing plug, cause claim, BS-cash substitute, or debt-funding inference |
| Reported gross / operating-margin bridge | **implemented (source-gated)** | ALT DuPont `REPORTED MARGIN BRIDGE CONTEXT` when unique explicit IS `gross_profit` and/or `operating_profit`/`operating_income` resolve with revenue (Lululemon + Fast Retailing); teaches gross margin, reported operating margin, net operating-expense burden, and reconstructed operating-margin change = ΔGM − Δburden; DEMO omits; no price/mix/cost inference; reported operating margin remains distinct from BAV NOPAT margin |
| Lease ROU-asset intensity / trend | **implemented** | ALT DuPont `LEASE ROU-ASSET CONTEXT` when unique BS `right_of_use_assets` resolves; average-balance intensity; independent of lease liability (9M.6) |
| PP&E capex / capex-to-revenue | **implemented** | ALT DuPont `PP&E CAPEX CONTEXT` when unique CF `payments_for_ppe` resolves; −reported practice + revenue intensity; no reinvestment bridge (9M.9) |
| Lease repayment cash / intensity | **implemented** | ALT DuPont `LEASE REPAYMENT CONTEXT` when unique CF `repayments_of_lease_liabilities` resolves; −reported practice + revenue intensity; independent of liability/ROU/interest (9N.3) |

## Historical capability gap matrix

| Historical area | GOOGL evidence | Current Trainer | Status | Source facts required | Training adaptation | Proposed Step 9 action |
|---|---|---|---|---|---|---|
| source statements / statement linkage | Income Statement; Balance Sheet; Cash Flow Statement | Same three source sheets; revenue/NI links | implemented | Standardized IS/BS/CF | Keep source populated; practice analytical links | Maintain; no new family needed |
| operating-vs-financing reformulation | Condensed Financials classification table + NOWC/NOA/Net Debt | Condensed Financials practice families | implemented-differently | Classified BS/IS lines | Yellow practice formulas vs GOOGL live SUMIF model | Maintain |
| DuPont / RNOA / Spread / FLEV / ROE | ALT DuPont | ALT DuPont families | implemented | Condensed outputs | Practice formulas + Check | Maintain |
| classification judgment | Condensed Financials column L toggles | Accounting Judgment sheet | implemented-differently | Explicit ambiguous lines / concepts | Guided cases; blank F uses reference | Maintain; expand cases when data supports |
| recurring/non-recurring normalization | Income Statement **CORE EARNINGS BRIDGE** | Normalization Judgment + Earnings Normalization | implemented-differently | Explicit normalization candidates | Treatment-conditioned formulas | Maintain; broaden candidate types carefully |
| cash conversion / accrual analysis | Earnings Quality §A accruals & cash conversion | Earnings Quality + trend diagnostics | implemented-differently | CFO + NI (+ total assets for scaled ratios) | Mechanical diagnostics, not scores | Maintain core; do not auto-port Beneish/Piotroski/Benford |
| working-capital behavior | Condensed NOWC aggregates | Working Capital Analysis sheet | implemented-differently | OWCA/OWCL classifications + Revenue | Dedicated WC diagnostics already stronger for training | Maintain |
| RNOA margin / turnover / asset intensity | ALT DuPont margin & turnover | Profitability drivers + change attribution; fixed-asset intensity context when PP&E+D&A resolve; ALT DuPont `REPORTED MARGIN BRIDGE CONTEXT` when unique explicit IS gross/operating profit resolve with revenue | implemented-differently | NOPAT, Revenue, NOA; optional PP&E+D&A; unique explicit IS `gross_profit` and/or `operating_profit`/`operating_income` for reported-margin bridge | Structured attribution + optional PPE context + source-gated reported margin/burden bridge | Maintain; deepen with lease/capex when contracted |
| ROE operating / financing attribution | ALT DuPont Fin Lev Gain | ROE attribution sheet | implemented-differently | RNOA, Spread, FLEV, equity | Dedicated change attribution | Maintain |
| historical per-share / diluted-share bridge | IS Basic/Diluted EPS & diluted shares outstanding | Optional Per Share Analysis + norm bridge; split-adjusted WAS when share-basis resolver emits `basis=split_adjusted` | implemented-differently | Explicit diluted WAS (+ optional norm); optional audited split restatement for comparable axis | Gate on share history; analytical axis must not overwrite raw share facts | Maintain |
| stock-based compensation / dilution | CF **Stock-based compensation expense**; IS share counts; EQ dilution signal | Diluted-share modules only; no SBC schedule | explicitly deferred (source absent) | CF SBC line and/or SBC disclosure + share history when present | Optional module; omit if absent | Deferred — no SBC on Fast Retailing / ordinary DEMO |
| PP&E / D&A / asset intensity | BS Property and equipment; CF depreciation; CF Purchases of property and equipment | ALT DuPont fixed-asset families when both PP&E and D&A resolve (`FIXED-ASSET INTENSITY CONTEXT`) | implemented-differently | Explicit PP&E (BS) + D&A (CF) + Revenue | Practice formulas on ALT DuPont; gated; no capex inference; D&A/Average PP&E is context only | Maintain; do not claim pure depreciation rate |
| capex / reinvestment bridge | CF **Purchases of property and equipment** | ALT DuPont `PP&E CAPEX CONTEXT`: populated reported CF payments + practice `ppe_capex` (−reported) and `ppe_capex_to_revenue`; **no** reinvestment bridge / depreciation ratios | implemented-differently (bounded); reinvestment explicitly deferred | Explicit CF `payments_for_ppe` (unique exact concept) + Revenue | Optional gated practice; do not infer from investing CF or ΔPPE+D&A; no abs()/sign inference; zero revenue → `#N/A` | Maintain bounded practice; reinvestment deferred (aggregate D&A / no maintenance-disposal split) |
| leases (liability) | BS Operating lease liabilities; Condensed classification rows | Accounting Judgment + ALT DuPont lease-liability families; aggregate **or** split current/non-current sum; treatment-conditioned lease interest when complete note axis exists | implemented-differently | Aggregate `lease_liability` **or** unique `lease_liability_current` + `lease_liability_noncurrent`; optional `lease_interest_expense` note axis; Revenue | Guided classification + intensity/trend; financing net interest conditioned on uniform lease treatment | Maintain |
| leases (ROU / payments) | BS Operating lease assets | ALT DuPont ROU **balance** intensity/trend when unique `right_of_use_assets` resolves; ALT DuPont `LEASE REPAYMENT CONTEXT` when unique CF `repayments_of_lease_liabilities` resolves (−reported + revenue intensity); **no** ROU-amortization or discount-rate diagnostics | implemented-differently (bounded ROU balances + repayment cash) | Explicit `right_of_use_assets`; unique CF `repayments_of_lease_liabilities` for repayment module; FR also supplies `payments_for_rou_assets` (separately deferred) | ROU balance + repayment-cash practice; do not equate Δ liability with amortization/repayments; rates separate | Maintain ROU + repayment; defer discount-rate (rates absent); defer full roll-forward; defer ROU-acquisition payments on materiality |
| goodwill / acquired intangibles / acquisitions | BS Goodwill; Intangible assets; CF acquisitions line | ALT DuPont goodwill/intangibles intensity & change when concepts resolve; optional intangible-payments (−reported); ALT DuPont `ACQUISITION CASH CONTEXT` when unique CF `acquisition_net_of_cash_acquired` resolves (−reported outflow, revenue intensity, and CFO − PP&E capex − outflow); **no** GW-impairment / PPA bridge | implemented-differently (bounded; acquisition-cash source-gated) | Unique `goodwill` / `intangible_assets` (and optional intangible-payment CF) when present; unique explicit CF `acquisition_net_of_cash_acquired` for acquisition-cash (Lululemon supplies; Fast Retailing / DEMO do not) | Optional gated intensity/change + optional gated acquisition-cash; never invent acquisition cash, impairment, or PPA | Maintain bounded goodwill module; acquisition-cash active when explicit CF is unique; Fast Retailing / DEMO remain omitted; GW-impairment / allocation remain deferred |
| share-repurchase cash-use | CF repurchase of common stock | ALT DuPont `SHARE REPURCHASE CONTEXT` when unique CF `repurchase_of_common_stock` resolves (−reported outflow, revenue intensity); residual CFO − PP&E capex − acquisition outflow − repurchase outflow when those unique sources resolve; **no** total-distribution, dilution, treasury, or funding-source inference | implemented-differently (source-gated) | Unique explicit CF `repurchase_of_common_stock` (Lululemon supplies; Fast Retailing / DEMO do not); residual also needs unique CFO, PP&E-capex, and acquisition sources | Optional gated cash-use; never invent repurchase cash or treat missing acquisition as zero | Maintain source-gated practice; Fast Retailing / DEMO remain omitted; do not infer funding source of negative residuals |
| deferred taxes / unusual tax rates | BS Deferred income taxes; CF Deferred income taxes; IS Core bridge tax notes | ALT DuPont deferred-tax balance context when unique DTA+DTL resolve; ETR + pretax norm tax convention remain separate | implemented-differently (bounded) | Unique `deferred_tax_assets` + `deferred_tax_liabilities` (both required) | Optional gated net-position / balance-change practice; no expense or cash-tax inference | Maintain; unusual-rate / CF deferred-tax expense remain deferred |
| minority / non-controlling interests | Not evidenced in inspected workbook | Ownership Attribution + parent ROE + parent-safe per-share numerator when ownership concepts resolve | implemented-differently | `profit_attributable_to_owners`, `profit_attributable_to_nci`, `equity_attributable_to_owners`, `noncontrolling_interests` | Optional gated schedule; consolidated DuPont unchanged | Maintain (Fast Retailing supplies NCI; GOOGL demo did not evidence it) |
| segment economics | Not evidenced as structured segment schedules (only scenario narrative mentions) | Absent | not-evidenced-in-GOOGL | Explicit segment revenue/opex/assets disclosures | Optional module; never invent segments | Priority C / B when segment inputs are designed |
| accounting consistency / reconciliation checks | Source statement arithmetic; EQ screens (Beneish/Piotroski/Benford) | `reconcile_financials` / identity validators; trusted-cell checks; retained cross-filing conflicts; ALT DuPont `CASH ROLL-FORWARD CONTEXT` when unique explicit CF totals, FX, opening/closing cash and reported cash change resolve | implemented-differently (bounded cash roll-forward); forensics explicitly deferred | Existing standardized facts; unique explicit CF operating/investing/financing/FX plus opening, closing and reported change when present | Keep blocking integrity; cash roll-forward teaches calculated-minus-reported gaps without plugs; forensic screens optional later | Maintain integrity checks and source-gated cash roll-forward; Beneish/Piotroski/Benford deferred (curriculum / not-trainer-target) |
| historical interpretation / diagnostics | EQ commentary framing; scenario rationales (forward) | WC / profitability / ROE / EQ change attributions | implemented-differently | Existing computed series | Prefer structured diagnostics over essays | Maintain; further module prompts explicitly deferred (curriculum polish) |

Forward GOOGL sheets (Guidance & Consensus, Model_*, Scenario_Summary, Implied Cost of Capital, Valuation Multiples) are inventoried above and classified **deferred-forward** for roadmap purposes; they are not Step 9 implementation tasks.

## Explicitly deferred / not copied

**deferred-forward**

- Guidance & Consensus ledger
- Model_Bear / Model_Base / Model_Bull forecast engines
- Scenario_Summary probability-weighted RI valuation, terminal value, sensitivities
- Implied Cost of Capital
- Valuation Multiples
- Enterprise DCF / residual-income IVPS / market-price rationalization

**not-trainer-target**

- Pipeline / sentinel / vault / coverage-maintenance behavior implied by the demo workbook’s system narrative
- Full-XBRL Benford populations and other automation-only forensic feeds
- Copying GOOGL decorative styling or pre-filled answer cells into the Trainer

**not-evidenced-in-GOOGL**

- Structured segment economics schedules
- Minority / non-controlling interest schedules (Trainer now supports NCI when a real company supplies facts; GOOGL reference still lacks them)

## Prioritized Step 9 queue

### Materially blocking (exit gate)

1. ~~**Repair historical-v1 active-catalog freeze**~~ — **cleared in Step 9N.2.** Freeze extended through lease repayment in 9N.3 (orders 1–123; goodwill/intangibles 98–111, lease ROU 112–115, deferred tax 116–119, capex 120–121, lease repayment 122–123).
2. ~~**Lease repayment diagnostics**~~ — **cleared in Step 9N.3.** FR CF `repayments_of_lease_liabilities` now drives ALT DuPont practice (`lease_repayment_specs=10`; `expected_specs=491`).

**Queue empty.** No unresolved high-value source-supported historical gap remains. Documented deferrals below are not exit blockers. Step 9 exit gate **PASS** (Step 9N.4); next stage is **Step 10 — driver-based forecasting**.

### Explicitly deferred — source absent

1. GW-impairment / purchase-price-allocation attribution — Fast Retailing / DEMO still have no business-acquisition CF (acquisition-cash omitted). Lululemon supplies unique CF `acquisition_net_of_cash_acquired` and now teaches reported acquisition cash. Goodwill-impairment tagging and purchase-price allocation remain unsupported.
2. SBC expense bridge into dilution / per-share interpretation — no CF SBC on Fast Retailing or ordinary DEMO.
3. Formal segment-economics module — no structured segment input facts/contract (also not-evidenced-in-GOOGL).
4. Lease **discount-rate** analysis — no IBR/discount-rate facts in standardized FR input (separate from repayment cash).

### Explicitly deferred — curriculum / evidence quality (not “missing contract” alone)

1. Further structured interpretation prompts on already-taught modules — major-schedule WC / profitability / ROE / EQ change attributions already satisfy TARGET’s structured-diagnostics preference; essays not required.
2. Capex **reinvestment** / depreciation-linked bridge beyond `ppe_capex` + `ppe_capex_to_revenue` — TARGET capex/D&A/intensity already covered by fixed-asset + capex contexts; FR `depreciation_amortization` is aggregate (ROU amortization risk) without maintenance/disposal split.
3. Complete lease **roll-forward** schedule — needs additions/remeasurements/other plugs beyond CF repayments + balance changes; not a substitute for teaching reported repayment cash.
4. ROU **acquisition-payment** diagnostics (`payments_for_rou_assets`) — separate from liability repayments; mostly immaterial vs ROU stock/revenue (FY2021–FY2024; FY2025 still 0.47% of revenue).
5. Richer tax-adjustment / cash-tax bridge — ETR + deferred-tax balance context suffice for historical tax diagnostics pending reconciling items beyond `income_taxes_paid`/`refunded` alone.
6. Beneish/Piotroski-style screens — mechanical EQ preferred; Benford/XBRL populations not-trainer-target.

### Priority C — TARGET topic not evidenced by GOOGL (aligned with deferrals above)

1. Structured segment economics — deferred pending disclosures + input contract.
2. ~~Minority / non-controlling interests~~ → **implemented** when ownership concepts resolve (Fast Retailing G5).

### Deferred — forecasting / valuation / non-Trainer reference features

1. Driver-based forecasting and scenario models.
2. Residual-income / DCF valuation, ICC, multiples, guidance/consensus.
3. Pipeline automation / monitoring features.

## Step 9M.4 candidate evaluation — goodwill / intangibles / acquisitions

### Resolvers / classification today

- `resolve_line(..., "goodwill"|"intangible_assets"|"payments_for_intangible_assets")` resolves via **exact `LineItem.concept` only** (no label-alias or safe-pattern fallback). Missing/ambiguous inputs follow the omission rules below.
- Classification may treat goodwill/intangible label tokens as operating long-term asset family material; that is structural classification only, not concept resolution and not an acquisition bridge.
- Bounded goodwill/intangibles diagnostic module is implemented on ALT DuPont (Step 9M.5).
- No resolver invents business-acquisition cash, goodwill impairment allocation, or acquired-vs-internally-developed splits.

### Fast Retailing supplied facts (`reconciled/standardized.json`)

Units: **JPY in Millions**. Periods: FY2021–FY2025 (`2021-08-31` … `2025-08-31`). Currency: JPY.

| Concept | Statement | FY2021 → FY2025 values | Sign / nature | Source anchor |
|---|---|---|---|---|
| `goodwill` | BS | `8092, 8092, 8092, 8092, 8092` | Asset balance (level) | CFS BS “Goodwill”; FY2025 CFS p.2 anchor `8,092` |
| `intangible_assets` | BS | `66939, 76621, 87300, 92568, 91606` | Asset balance (level) | CFS BS “Intangible assets”; FY2025 CFS p.2 anchor `91,606` |
| `payments_for_intangible_assets` | CF | `-19624, -28335, -33542, -30260, -27329` | Cash **outflow** (negative as reported) | CFS “Payments for intangible assets”; FY2025 CF page anchor path |
| `impairment_losses` | CF | `16908, 23150, 3958, -1700, 598` | General impairment / reversal line | CFS operating adjustments — **not** goodwill-tagged |

**Supported as reported facts:** goodwill balances; intangible-asset balances; intangible-asset payment cash flows.

**Unsupported / must not invent:** business-combination acquisition cash (no subsidiaries/businesses acquisition CF concept present); goodwill impairment or acquisition accounting explanations; linking `impairment_losses` to goodwill (goodwill is flat across FY2021–FY2025 while impairment fluctuates); acquired-vs-internally-generated intangible split; purchase-price allocation.

Illustrative DEMO supplies only a flat unlabeled Goodwill row (no intangibles / no acquisition CF) — any new module must omit itself there unless explicit concepts resolve after the resolution prerequisite below.

### Verdict on prior Priority A item 1 (full acquisition-cash diagnostics)

The **full** “goodwill / acquired intangibles / acquisition-cash” package **lacks** acquisition-cash and GW-movement facts on Fast Retailing. Fast Retailing / DEMO therefore omit acquisition-cash practice. Lululemon supplies unique CF `acquisition_net_of_cash_acquired` and now exposes reported acquisition cash (outflow, revenue intensity, and CFO − PP&E capex − outflow). Do **not** invent impairment or purchase-price-allocation storytelling.

The **bounded** balance + optional intangible-payments intensity module **is** source-supported and remains implemented.

### Resolution prerequisite (completed in Step 9M.5)

Explicit concept resolution is registered in `core/model/line_resolver.py` for:

1. BS `goodwill`
2. BS `intangible_assets`
3. optional CF `payments_for_intangible_assets`

**Matching rule:** unique exact `LineItem.concept` match only — **no** label-alias or safe-pattern fallback for these three.

---

## Next implementation disposition

**Step 9 historical candidate:** *(none)* — blocking queue empty; deferred topics lack available source facts or are curriculum/materiality deferrals, not concrete exit gaps.

**Next stage:** **Step 10 — Driver-based forecasting** (TARGET). Do not invent further Step 9 historical polish solely to remain in Step 9.

**Problem (cleared, 9N.3):** Fast Retailing CF `repayments_of_lease_liabilities` lacked Trainer repayment diagnostics; now taught via `LEASE REPAYMENT CONTEXT`.

**Distinct from (remain deferred):** lease discount-rate analysis; complete lease roll-forward; ROU acquisition-payment diagnostics.

### Lease-repayment source, sign, and practice (Step 9N.3 — complete)

- Resolver: CF `repayments_of_lease_liabilities` is **explicit-concept-only** (no label/pattern fallback), resolved only from `StandardizedFinancials.cash_flow`.
- Gating: missing, ambiguous, label-only, or wrong-statement sources → module unavailable; no repayment rows or practice specs. Independent of lease-liability / ROU / lease-interest facts.
- Sign: preserve reported cash-flow values as `repayments_reported`; analytical `lease_repayments = -repayments_reported`. Never `abs()` or infer from Δ liability.
- Ratio: `lease_repayments_to_revenue = ratio_or_na(lease_repayments, revenue)`; zero revenue → `UNDEFINED_RATIO` (`#N/A`); missing/`None` required values raise `MissingHistoricalValueError`.
- Workbook: ALT DuPont `LEASE REPAYMENT CONTEXT` with populated reported-repayment links + two practice families per period (`lease_repayment.lease_repayments`, `lease_repayment.lease_repayments_to_revenue`); Answer Key Notes distinguish repayment cash from total lease cost / ROU amortization / liability movement; workbook-wide Check.
- Fast Retailing: `lease_repayment_specs=10`, `expected_specs=491`; FY2021–FY2025 `lease_repayments` anchors `148248, 136889, 140646, 146403, 140483` with independently calculated revenue ratios. Capex specs remain 10; liability/ROU specs and 3+3 conflicts unchanged.
- DEMO unchanged (no `repayments_of_lease_liabilities`).

### Capex source, sign, and practice (Step 9M.9 — complete; preserved)

- Resolver: CF `payments_for_ppe` is **explicit-concept-only** (no label/pattern fallback), resolved only from `StandardizedFinancials.cash_flow`.
- Gating: missing or duplicate CF sources → module unavailable (`capex_applicable` false); no capex rows or practice specs.
- Sign: preserve reported cash-flow values as `payments_reported`; analytical `ppe_capex = -payments_reported`. Never `abs()` or infer sign.
- Ratio: `ppe_capex_to_revenue = ratio_or_na(ppe_capex, revenue)`; zero revenue → `UNDEFINED_RATIO` (`#N/A`); missing/`None` required values raise `MissingHistoricalValueError`.
- Workbook: ALT DuPont `PP&E CAPEX CONTEXT` with populated reported-payment links + two practice families per period (`capex.ppe_capex`, `capex.ppe_capex_to_revenue`); Answer Key Notes; workbook-wide Check.
- Fast Retailing: `capex_specs=10`, `expected_specs=491` (includes lease-repayment specs); FY2021–FY2025 `ppe_capex` anchors `56500, 51271, 61764, 73728, 135535` with independently calculated revenue ratios.
- Reinvestment bridge / other capex diagnostics: **explicitly deferred** (curriculum — see queue).
- DEMO unchanged (no `payments_for_ppe`).

### Explicitly out of scope for the cleared repayment candidate

- Discount-rate / IBR analysis, complete lease roll-forward, ROU acquisition-payment diagnostics
- Interpretation essays, reinvestment bridge, SBC, acquisition, segments, forensics
- Forecasting / valuation
- Source fixture edits unrelated to repayment gating

**Step 9N.4 note:** Exit-gate repair. Criteria 1 and 6 reassessed under the concrete material-gap rule (deferred topics / planner confirmation alone do not fail). All six criteria **PASS**; Step 9 complete; next stage Step 10. Supporting 9N.3 edits to `line_resolver.py`, `test_line_resolver.py`, and `test_capex.py` (481→491) explicitly accepted. Fresh verification: focused **76 passed**; full `core/tests` **587 passed**.

**Step 9N.3 note:** Lease-repayment diagnostics implemented and tested. Catalog freeze orders 1–123. Prior incomplete exit assessment superseded by 9N.4.

**Step 9N.2 note:** Catalog freeze repaired (orders 1–121; suite green). Superseded as the blocking next item by 9N.3 repayment delivery.

**Step 9N.1 note:** Corrected lease-payment dispositions. Balance diagnostics ≠ repayment/amortization. Catalog-freeze blocker since cleared in 9N.2.

**Step 9N note:** Prior exit assessment incorrectly deferred repayments as duplicative of liability amortization; superseded by 9N.1.

**Step 9M.9 note:** Capex-to-revenue practice is implemented and tested. Reinvestment bridge explicitly deferred (curriculum).

**Step 9M.8 note:** Capex CF source resolution + signed `ppe_capex = -payments_reported` contract completed; practice/ratios delivered in 9M.9.

**Step 9M.7 note:** Deferred-tax balance diagnostics are implemented on ALT DuPont when unique exact-concept `deferred_tax_assets` and `deferred_tax_liabilities` both resolve. DEMO remains unchanged. Fast Retailing activates 17 practice cells (`deferred_tax_specs=17`). Deferred-tax expense / cash-tax inference remains deferred.

**Step 9M.6 note:** Lease ROU-asset **balance** intensity / trend diagnostics are implemented on ALT DuPont when unique exact-concept `right_of_use_assets` resolves. DEMO remains unchanged (no ROU concept). Fast Retailing activates 16 practice cells. CF repayment diagnostics delivered in 9N.3; discount-rate and full roll-forward remain separately deferred.

**Step 9M.5 note:** Goodwill / intangible-asset intensity & change diagnostics (optional intangible-payments as −reported) are implemented on ALT DuPont when explicit concepts resolve. DEMO label-only goodwill remains omitted. GW-impairment storytelling remains deferred. Acquisition-cash is now source-gated: Lululemon unique CF `acquisition_net_of_cash_acquired` is taught; Fast Retailing / DEMO remain omitted.

**Step 9M.2.4.1.1.1.24 note:** Share-repurchase cash-use is source-gated on unique explicit CF `repurchase_of_common_stock`. Lululemon teaches −reported outflow, revenue intensity, and CFO − PP&E capex − acquisition outflow − repurchase outflow. Fast Retailing / DEMO remain omitted. Missing acquisition evidence does not become zero. Negative residuals mean selected cash uses exceed reported CFO and do not identify debt funding.

**Step 9K.1 note:** PP&E / D&A asset-intensity diagnostics are implemented-differently on ALT DuPont. Capex source+practice are complete; reinvestment bridge remains deferred.

**Step 9L.1 / 9M.3A–B note:** Lease-liability intensity/trend diagnostics support aggregate **or** split summation; treatment-conditioned lease interest is implemented when a complete reported lease-interest axis exists.

**Step 9M.3C–D note:** Parent/NCI Ownership Attribution and split-adjusted per-share analysis are implemented when their input contracts resolve.

**G1–G7:** remain closed; overlap/supplemental disagreements retained at **3/3** (`benchmark/fast_retailing/conflicts.json` / `BASELINE.md`).
