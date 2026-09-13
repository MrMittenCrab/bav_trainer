# GOOGL Historical Reference

Internal development reference for Step 9 historical convergence. Evidence is limited to what was inspected in `example/GOOGL_Demo_Integrated_Financials.xlsx` and the current canonical Trainer/Answer Key. Gaps are not filled from general knowledge.

Audit tool: `scripts/audit_reference_workbook.py`  
GOOGL SHA-256 (pre/post inspection): `81faf2882d0df07ecf5def45695431c1935b4f7a94c1e017367596a063063896`  
Canonical Answer Key SHA-256: `5392f571144ad72a4de623f02fc6aaabd6f91fa2c877a4a66be6ccbd70af49f4`

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

Canonical normalization-enabled demo (`DEMO_HK_Answer_Key.xlsx`, 74 families / 314 cells) visible surface:

| Sheet / feature | Role |
|---|---|
| Income Statement / Balance Sheet / Cash Flow Statement | Populated historical source facts |
| Condensed Financials | Reformulation schedules (practice formulas) |
| ALT DuPont | RNOA / Spread / FLEV / ROE + FIXED-ASSET INTENSITY CONTEXT when PP&E and D&A resolve |
| Accounting Judgment | Guided operating/financing treatment |
| Normalization Judgment + Earnings Normalization | Recurring / non-recurring bridge |
| Earnings Quality | Cash conversion, accruals, optional asset-scaled ratios + trend diagnostics |
| Working Capital Analysis | NOWC intensity / incremental WC diagnostics |
| Profitability / ROE attribution sheets | RNOA margin-turnover and ROE operating/financing change attribution |
| Per Share Analysis | Optional; gated on diluted WAS history (+ normalized EPS bridge when normalization active) |
| Model_* / Scenario_Summary | Hidden deferred placeholders only |

Ordinary / share / cross-company surfaces: `70/294`, `74/314`, `78/328`, `86/366`; services `59/248`, retail `78/331`, manufacturer `70/293`.

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
| historical per-share / diluted-share bridge | IS Basic/Diluted EPS & diluted shares outstanding | Optional Per Share Analysis + norm bridge | implemented-differently | Explicit diluted WAS (+ optional norm) | Gate on share history | Maintain |
| stock-based compensation / dilution | CF **Stock-based compensation expense**; IS share counts; EQ dilution signal | Diluted-share modules only; no SBC schedule | missing-current-data-supported | CF SBC line and/or SBC disclosure + share history when present | Optional module; omit if absent | Priority A after lease foundation, or Priority B if stricter SBC contract needed |
| PP&E / D&A / asset intensity | ALT DuPont FIXED-ASSET INTENSITY CONTEXT (PP&E, D&A, average PP&E, turnover, intensity, change, D&A ratios) | ALT DuPont fixed-asset families 79–86 when both PP&E and D&A resolve | implemented-differently | Explicit PP&E (BS) + D&A (CF) + Revenue | Practice formulas on ALT DuPont; gated; no capex inference; D&A/Average PP&E is context only | Maintain; do not claim pure depreciation rate |
| capex / reinvestment bridge | CF **Purchases of property and equipment** | Absent | missing-needs-new-explicit-data | Explicit capex / purchases-of-PP&E source + sign contract | Optional gated module after contract exists | Priority B — deferred until explicit capex contract |
| leases | BS Operating lease assets / Operating lease liabilities; Condensed classification rows | Lease concept on Accounting Judgment; no lease analytics sheet | implemented-differently | Lease asset/liability lines | Keep judgment; add lease intensity diagnostics later | Priority A deepen as diagnostics |
| goodwill / acquired intangibles / acquisitions | BS Goodwill; Intangible assets; CF acquisitions line | Often classified as OLTA; no acquisition/goodwill bridge | missing-current-data-supported | Goodwill, intangibles, acquisition CF/lines when present | Optional gated module | Priority A (after lease intensity) |
| deferred taxes / unusual tax rates | BS Deferred income taxes; CF Deferred income taxes; IS Core bridge tax notes (e.g. Tax Act remasurement) | Effective tax rate + pretax norm tax convention | missing-current-data-supported | Deferred tax BS/CF lines and/or explicit tax-adjustment candidates | Optional tax-quality diagnostics; do not invent | Priority A/B depending on explicit tax-adjustment contract |
| minority / non-controlling interests | Not evidenced in inspected workbook | Absent | not-evidenced-in-GOOGL | Explicit NCI lines when a company has them | Optional gated module per TARGET | Priority C until a real-company case supplies NCI |
| segment economics | Not evidenced as structured segment schedules (only scenario narrative mentions) | Absent | not-evidenced-in-GOOGL | Explicit segment revenue/opex/assets disclosures | Optional module; never invent segments | Priority C / B when segment inputs are designed |
| accounting consistency / reconciliation checks | Source statement arithmetic; EQ screens (Beneish/Piotroski/Benford) | `reconcile_financials` / identity validators; trusted-cell checks | implemented-differently | Existing standardized facts | Keep blocking integrity; forensic screens optional later | Priority B for forensic screens (Benford needs XBRL population — likely not-trainer-target) |
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
- Minority / non-controlling interest schedules

## Prioritized Step 9 queue

### Priority A — historically useful and current-data-supported

1. Lease intensity / lease-liability diagnostics building on existing lease classification judgment.
2. Goodwill / acquired intangibles / acquisition cash diagnostics when those lines are supplied.
3. SBC expense bridge into dilution / per-share interpretation when CF SBC + share history are supplied.
4. Deferred-tax / unusual-tax diagnostics when deferred-tax lines or explicit tax adjustments are supplied.
5. Further structured historical interpretation prompts on modules already taught.

### Priority B — historically useful but needs explicit new historical inputs

1. Capex / reinvestment bridge (requires explicit purchases-of-PP&E / capex source and sign contract; not inferred from investing cash flow or PP&E change + D&A).
2. Formal segment-economics input contract + optional module.
3. Richer tax-adjustment candidate schema beyond current normalization scopes.
4. Optional Beneish/Piotroski-style screens only if pedagogically justified and computable from standardized facts (not XBRL scrapes).

### Priority C — TARGET-required historical topic not evidenced by GOOGL

1. Minority / non-controlling interests (await a company with explicit NCI facts).
2. Structured segment economics (await disclosures + input contract; not evidenced as GOOGL schedules).

### Deferred — forecasting / valuation / non-Trainer reference features

1. Driver-based forecasting and scenario models.
2. Residual-income / DCF valuation, ICC, multiples, guidance/consensus.
3. Pipeline automation / monitoring features.

**Next historical implementation candidate (evidence rule):** Priority A item 1 — **lease intensity / lease-liability diagnostics**, building on existing lease classification without inventing ROU alternatives or activating forecasting.

**Step 9K.1 note:** PP&E / D&A asset-intensity diagnostics are now implemented-differently on ALT DuPont. Capex remains explicitly deferred until a source/sign contract exists.
