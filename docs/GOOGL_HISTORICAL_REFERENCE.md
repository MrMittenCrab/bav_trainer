# GOOGL Historical Reference

Internal development reference for Step 9 historical convergence. Evidence is limited to what was inspected in `example/GOOGL_Demo_Integrated_Financials.xlsx` and the current canonical Trainer/Answer Key. Gaps are not filled from general knowledge.

Audit tool: `scripts/audit_reference_workbook.py`  
GOOGL SHA-256 (pre/post inspection): `81faf2882d0df07ecf5def45695431c1935b4f7a94c1e017367596a063063896`  

**Coverage refresh (Step 9M.5):** Inventory, gap matrix, and queue below incorporate Fast Retailing G1–G7 closure evidence and measured Step 9M.5 goodwill/intangibles activation (`expected_specs=438`).

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
| ALT DuPont | RNOA / Spread / FLEV / ROE + FIXED-ASSET INTENSITY CONTEXT + LEASE LIABILITY CONTEXT when inputs resolve |
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

- **`expected_specs=438`** (blank Check `0/0/438`; filled Check `438/0/0`)
- Module specs (recorded): `lease_specs=18`, `ownership_specs=34`, `per_share_specs=18`, `per_share_attribution_specs=16`, `fixed_asset_specs=35`, `goodwill_intangibles_specs=58`
- Added vs illustrative DEMO when facts resolve: split lease-liability diagnostics, Ownership Attribution (parent/NCI), split-adjusted Per Share Analysis + attribution, goodwill/intangibles intensity context

### Implemented since prior inventory (G3–G6 / related)

| Capability | Status | Notes |
|---|---|---|
| Split lease-liability aggregation | **implemented** | `resolve_lease_liability_source()` accepts unique aggregate **or** exactly one current + one non-current pair summed period-by-period (G3 / 9M.3A) |
| Treatment-conditioned lease interest | **implemented** | Optional `historical_lease.lease_interest_expense`; operating treatment excludes disclosed lease interest from financing net interest; mixed treatment fails closed (G4 / 9M.3B) |
| Parent / NCI attribution + parent ROE | **implemented** | Ownership Attribution schedule when four ownership concepts resolve; per-share numerator uses parent profit when ownership complete (G5 / 9M.3C) |
| Split-adjusted per-share analysis | **implemented** | `historical_shares` with `basis=split_adjusted` drives diluted WAS / EPS practice when share axis resolves (G6 / 9M.3D) |
| Goodwill / intangible intensity & change | **implemented** | ALT DuPont `GOODWILL & INTANGIBLES CONTEXT` when unique BS `goodwill` and/or `intangible_assets` resolve; optional CF `payments_for_intangible_assets` as −reported; no acquisition/impairment narrative (9M.5) |

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
| RNOA margin / turnover / asset intensity | ALT DuPont margin & turnover | Profitability drivers + change attribution; fixed-asset intensity context when PP&E+D&A resolve | implemented-differently | NOPAT, Revenue, NOA; optional PP&E+D&A | Structured attribution + optional PPE context | Maintain; deepen with lease/capex when contracted |
| ROE operating / financing attribution | ALT DuPont Fin Lev Gain | ROE attribution sheet | implemented-differently | RNOA, Spread, FLEV, equity | Dedicated change attribution | Maintain |
| historical per-share / diluted-share bridge | IS Basic/Diluted EPS & diluted shares outstanding | Optional Per Share Analysis + norm bridge; split-adjusted WAS when share-basis resolver emits `basis=split_adjusted` | implemented-differently | Explicit diluted WAS (+ optional norm); optional audited split restatement for comparable axis | Gate on share history; analytical axis must not overwrite raw share facts | Maintain |
| stock-based compensation / dilution | CF **Stock-based compensation expense**; IS share counts; EQ dilution signal | Diluted-share modules only; no SBC schedule | missing-current-data-supported | CF SBC line and/or SBC disclosure + share history when present | Optional module; omit if absent | Priority A when SBC facts exist; Fast Retailing / DEMO currently lack SBC lines |
| PP&E / D&A / asset intensity | BS Property and equipment; CF depreciation; CF Purchases of property and equipment | ALT DuPont fixed-asset families when both PP&E and D&A resolve (`FIXED-ASSET INTENSITY CONTEXT`) | implemented-differently | Explicit PP&E (BS) + D&A (CF) + Revenue | Practice formulas on ALT DuPont; gated; no capex inference; D&A/Average PP&E is context only | Maintain; do not claim pure depreciation rate |
| capex / reinvestment bridge | CF **Purchases of property and equipment** | Absent as dedicated practice module (PPE/D&A context only) | missing-needs-new-explicit-data | Explicit `payments_for_ppe` / purchases-of-PP&E source + sign contract | Optional gated module; do not infer from investing CF or ΔPPE+D&A | Priority B — contract can be defined from explicit CF concept; still separate from next candidate |
| leases (liability) | BS Operating lease liabilities; Condensed classification rows | Accounting Judgment + ALT DuPont lease-liability families; aggregate **or** split current/non-current sum; treatment-conditioned lease interest when complete note axis exists | implemented-differently | Aggregate `lease_liability` **or** unique `lease_liability_current` + `lease_liability_noncurrent`; optional `lease_interest_expense` note axis; Revenue | Guided classification + intensity/trend; financing net interest conditioned on uniform lease treatment | Maintain |
| leases (ROU / payments) | BS Operating lease assets | ROU BS line may classify as OLTA; **no** ROU intensity schedule; **no** lease-payment / discount-rate diagnostics | missing-current-data-supported | Explicit `right_of_use_assets`; optional lease-payment CF lines when present | Optional gated module after liability foundation (now done) | Priority A remaining lease gap |
| goodwill / acquired intangibles / acquisitions | BS Goodwill; Intangible assets; CF acquisitions line | ALT DuPont goodwill/intangibles intensity & change when concepts resolve; optional intangible-payments (−reported); **no** acquisition-cash / GW-impairment bridge | implemented-differently (bounded) | Unique `goodwill` / `intangible_assets` (and optional intangible-payment CF) when present; acquisition CF only when explicitly supplied | Optional gated intensity/change module; never invent acquisition or GW-impairment stories | Maintain bounded module; acquisition-cash remains deferred until explicit facts |
| deferred taxes / unusual tax rates | BS Deferred income taxes; CF Deferred income taxes; IS Core bridge tax notes | Effective tax rate + pretax norm tax convention; no DTA/DTL diagnostic schedule | missing-current-data-supported | Deferred tax BS/CF lines and/or explicit tax-adjustment candidates | Optional tax-quality / balance diagnostics; do not invent | Priority A after next candidate / when contracted |
| minority / non-controlling interests | Not evidenced in inspected workbook | Ownership Attribution + parent ROE + parent-safe per-share numerator when ownership concepts resolve | implemented-differently | `profit_attributable_to_owners`, `profit_attributable_to_nci`, `equity_attributable_to_owners`, `noncontrolling_interests` | Optional gated schedule; consolidated DuPont unchanged | Maintain (Fast Retailing supplies NCI; GOOGL demo did not evidence it) |
| segment economics | Not evidenced as structured segment schedules (only scenario narrative mentions) | Absent | not-evidenced-in-GOOGL | Explicit segment revenue/opex/assets disclosures | Optional module; never invent segments | Priority C / B when segment inputs are designed |
| accounting consistency / reconciliation checks | Source statement arithmetic; EQ screens (Beneish/Piotroski/Benford) | `reconcile_financials` / identity validators; trusted-cell checks; retained cross-filing conflicts | implemented-differently | Existing standardized facts | Keep blocking integrity; forensic screens optional later | Priority B for forensic screens (Benford needs XBRL population — likely not-trainer-target) |
| historical interpretation / diagnostics | EQ commentary framing; scenario rationales (forward) | WC / profitability / ROE / EQ change attributions | implemented-differently | Existing computed series | Prefer structured diagnostics over essays | Priority A — extend interpretation on new historical modules |

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

### Priority A — historically useful and current-data-supported

1. Lease ROU-asset intensity / trend diagnostics when unique `right_of_use_assets` resolves (liability aggregation foundation is done).
2. SBC expense bridge into dilution / per-share interpretation when CF SBC + share history are supplied (not present on Fast Retailing or ordinary DEMO today).
3. Deferred-tax balance / net-position diagnostics when unique DTA/DTL (and/or explicit tax-adjustment candidates) are supplied.
4. Further structured historical interpretation prompts on modules already taught.
5. Acquisition-cash / GW-impairment attribution only when those facts are separately and explicitly supplied (not present on Fast Retailing today).

### Priority B — historically useful but needs explicit new historical inputs

1. Capex / reinvestment bridge (requires explicit purchases-of-PP&E / `payments_for_ppe` source and sign contract; not inferred from investing cash flow or PP&E change + D&A). Fast Retailing already discloses `payments_for_ppe`, but the Trainer module/contract is not yet implemented.
2. Formal segment-economics input contract + optional module.
3. Richer tax-adjustment candidate schema beyond current normalization scopes.
4. Optional Beneish/Piotroski-style screens only if pedagogically justified and computable from standardized facts (not XBRL scrapes).
5. Lease-payment / discount-rate analysis only with an explicit payment and rate contract (do not invent from ROU + liability).

### Priority C — TARGET-required historical topic not evidenced by GOOGL

1. Structured segment economics (await disclosures + input contract; not evidenced as GOOGL schedules).
2. ~~Minority / non-controlling interests~~ → **moved to implemented** when ownership concepts resolve (Fast Retailing G5).

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

The **full** “goodwill / acquired intangibles / acquisition-cash” package **lacks** acquisition-cash and GW-movement facts on Fast Retailing. Do **not** implement acquisition or impairment storytelling.

The **bounded** balance + optional intangible-payments intensity module **is** source-supported and remains the single next implementation candidate.

### Resolution prerequisite (completed in Step 9M.5)

Explicit concept resolution is registered in `core/model/line_resolver.py` for:

1. BS `goodwill`
2. BS `intangible_assets`
3. optional CF `payments_for_intangible_assets`

**Matching rule:** unique exact `LineItem.concept` match only — **no** label-alias or safe-pattern fallback for these three.

---

## Next historical implementation candidate (exactly one)

**Name:** Lease ROU-asset intensity / trend diagnostics

### Minimum input contract

Unique explicit BS `right_of_use_assets` (no label fallback). Revenue from existing anchor. Optional payment/discount-rate lines remain deferred until separately contracted.

### Missing / ambiguous-input behavior

- No unique ROU concept → omit module (fail closed).
- Do not invent ROU from lease liability or note totals.

### Explicitly out of scope for this candidate

- Lease-payment / discount-rate schedules
- Acquisition-cash / GW-impairment narratives
- Capex bridge, SBC, deferred-tax schedule, segments, forecasting/valuation

**Step 9M.5 note:** Goodwill / intangible-asset intensity & change diagnostics (optional intangible-payments as −reported) are implemented on ALT DuPont when explicit concepts resolve. DEMO label-only goodwill remains omitted. Fast Retailing activates 58 practice cells (`expected_specs=438`). Acquisition-cash and GW-impairment storytelling remain deferred.

**Step 9K.1 note:** PP&E / D&A asset-intensity diagnostics are implemented-differently on ALT DuPont. Capex remains Priority B until the dedicated module/contract is implemented.

**Step 9L.1 / 9M.3A–B note:** Lease-liability intensity/trend diagnostics support aggregate **or** split summation; treatment-conditioned lease interest is implemented when a complete reported lease-interest axis exists. ROU-asset diagnostics and lease-payment/discount-rate analysis remain deferred.

**Step 9M.3C–D note:** Parent/NCI Ownership Attribution and split-adjusted per-share analysis are implemented when their input contracts resolve.

**G1–G7:** remain closed; overlap/supplemental disagreements retained at **3/3** (`benchmark/fast_retailing/conflicts.json` / `BASELINE.md`).
