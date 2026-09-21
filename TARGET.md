# TARGET.md

## Product target

Build a complete Business Analysis and Valuation equity-research system, presented as **BAV**. The Excel workbook is the core analytical and source-traceability product; canonical Markdown, figures and Word/PDF publications support it. Trainer is an optional secondary derivative.

The intended product relationship is:

source-grounded company evidence → complete BAV analytical model → professional `<Company>_BAV.xlsx` with reproducible Markdown research, figures and Word/PDF publication

The completed model also supports an optional derivative `<Company>_BAV_Trainer.xlsx`. Neither BAV build nor publication requires Trainer generation.

The BAV workbook is the authoritative analytical model. It replaces the former Answer Key concept and must not present itself as an answer key, exercise or Trainer. Its front page is a concise product and company-analysis summary.

Product-facing CLI help, documentation, workbook opening and publication wording use BAV as the primary name. Preserve optional Trainer functionality. Do not rename the repository, Git remote or unrelated infrastructure for branding.

The secondary Trainer supports progression from accounting novice toward competence as a junior accounting-based equity-research analyst. Training-specific framing, blank yellow practice cells, Check instructions and exercise-oriented presentation belong in the Trainer.

The complete research system should enable an analyst to:

1. trace reported information into a research model;
2. understand three-statement relationships and accounting sign conventions;
3. make and defend material accounting, classification and normalization judgments;
4. construct and audit historical analytical schedules;
5. explain changes in profitability, capital intensity, financing, cash conversion and per-share economics;
6. convert historical analysis into explicit forecasts and valuation assumptions;
7. value the equity using BAV-consistent methods and appropriate cross-checks; and
8. communicate a concise, evidence-based investment conclusion.

Formula correctness is necessary but not sufficient. The product must support accounting judgment, economic interpretation, auditability, forecasting discipline, valuation and research communication.

Historical accounting analysis, normalization and reformulation, NOA, NOPAT, forecasting, valuation and investment interpretation remain long-term goals. A bounded Session need not complete every later stage.

## Research output architecture

The canonical build architecture separates persistent upstream inputs from generated outputs:

- `build/input/<company>/source/`: original source filings.
- `build/input/<company>/extracted/`: filing-level ordinary financial and management KPI extraction.
- `build/input/<company>/reconciled/`: accepted company-level reconciled data and admission evidence.
- `build/output/<company>/`: generated workbook, research, figures, supporting build artifacts and published documents.

All company directory names are lowercase, including `lululemon` and `fast_retailing`. Human-facing filenames may retain normal capitalization.

The completed Lululemon build contains:

- `build/output/lululemon/Lululemon_BAV.xlsx`
- `build/output/lululemon/research/Lululemon_Drivers.md`
- `build/output/lululemon/research/Lululemon_Forecast.md`
- `build/output/lululemon/research/Lululemon_Valuation.md`
- `build/output/lululemon/research/Lululemon_Overview.md`
- `build/output/lululemon/figures/drivers/growth.png`
- `build/output/lululemon/figures/drivers/geography.png`
- `build/output/lululemon/figures/drivers/margin.png`
- `build/output/lululemon/supporting/build_status.json`
- `build/output/lululemon/supporting/assumptions.json`
- `build/output/lululemon/supporting/component_map.json`
- `build/output/lululemon/supporting/rowmap.json`

`python -m bav build Lululemon` reads the canonical Lululemon input and writes only under `build/output/lululemon/`. `python -m bav check Lululemon` checks that canonical output without requiring paths. `python -m bav publish Lululemon` renders canonical analysis and referenced figures into Word and PDF under `build/output/lululemon/`. These company-name interfaces generalize to supported companies. Build remains the primary product command; Check is diagnostic. Internal lookup may normalize company names to lowercase slugs.

Benchmark and release are uses of canonical outputs, represented through Git tracking, tags or release packaging, not separate company data architectures. After canonical paths and dependencies are verified, remove obsolete generated artifacts and duplicate legacy, benchmark and release company trees, including obsolete Trainer and Answer Key outputs. Preserve original filings and canonical upstream data. Compatibility copies or symlinks require an active supported interface; do not maintain alternate active build architectures. Runtime must not silently fall back to obsolete benchmark, release or other legacy company paths.

Root `README.md` documents the workbook / research / figures / publication architecture. Root `STYLE.md` is the single source of truth for human-facing BAV presentation and language conventions, applied to Markdown research, generated figures and rendered publications. Do not duplicate its specification in README or individual modules.

The research module sequence is Drivers, Forecast, Valuation, Overview:

- Drivers: historical business, operating and financial analysis.
- Forecast: forward estimates and assumptions.
- Valuation: standalone valuation.
- Overview: cross-module synthesis.

Module names use one word unless a one-word name would be genuinely unclear. The current historical-only Session strengthens Drivers; Forecast, Valuation and Overview files remain zero-content placeholders, without headings, explanatory text, TODOs, templates or analysis.

Research and figures must be reproducible from the same validated BAV inputs as the workbook. Preserve calculations, source references, reconciliations and validation controls; do not maintain a separate uncontrolled numerical dataset. Figures use Matplotlib and one centralized style implementation derived from STYLE.md.

Publication is downstream of analysis and must not duplicate analytical logic or maintain a second manually edited report. Use a standard maintainable Markdown-to-document toolchain where it meets actual rendering requirements. Word and PDF must be generated entirely from the CLI, without manual post-processing, and preserve headings, tables, equations, captions, source notes, meaningful structure and readable page layout. Resolve referenced canonical figures correctly; missing figures, broken references or conversion failures must fail clearly. Apply established styling and omit internal implementation/debug material from teammate-facing reports. Verify output readability and reproducibility.

Preserve the existing validated workbook. Presentation changes may support Drivers and the BAV product hierarchy, including a concise company-analysis front page; this does not authorize a general workbook redesign or removal of audit evidence.

## Scope boundary

The initial curriculum is for **non-financial operating companies**. Banks, insurers, brokers, and other financial institutions require separate sector-specific accounting and valuation logic.

Hong Kong company input may remain manual. Automatic HKEX scraping is not required when annual reports, interim reports, results materials, Excel exports, Bloomberg exports, or Wind exports are supplied.

Analysis and exercises should follow materiality and the information actually supplied. Missing historical facts must not be invented.

BAV supplies source-grounded equity-research analysis and historical target-assessment evidence for the current Lululemon M&A teamwork project. Identify historical growth and margin drivers, recurring versus episodic components, robust relationships and unresolved explanations. This scope does not authorize buyer-specific analysis, a deal recommendation, forecasting, valuation, price targets, scenarios or forward projections. Existing Fast Retailing analytical controls and regression coverage remain preserved; Fast Retailing is a regression case, not an additional strategy project.

## Source-data architecture

The analytical engine does not interpret arbitrary PDFs directly.

`build/input/<company>/` contains all persistent upstream data needed to reproduce the BAV output. For Lululemon, `source/` holds original filings; `extracted/` holds ordinary financial and management KPI filing JSON, such as `LULU_FY2022.json` and `LULU_FY2022_management_kpis.json`; `reconciled/` holds `standardized.json`, `provenance.json`, `conflicts.json` and `management_kpi_admission.json`.

`build/input/lululemon/reconciled/standardized.json` remains the canonical company model consumed by the BAV build. Integrate useful existing upstream evidence into this architecture without retaining duplicate identical files or a separate `lululemon-live` tree. Use the same structure for `fast_retailing`.

Preserve issuer fiscal-year labels and actual period-end dates as distinct information at the canonical data/presentation boundary. Workbook presentation, Markdown and figures use the same issuer fiscal-year mapping; never derive issuer fiscal year from the calendar year of the period-end date.

For filing-based workflows, the canonical upstream handoff is **source-grounded filing JSON**. Each filing is extracted independently and preserves reported labels, statement sections, periods, currency/unit scale, values, and page-level provenance.

LLM-assisted extraction is permitted upstream, but extraction must remain separate from BAV accounting judgment and analytical modeling. The extractor records what the filing says; BAV determines how accepted reported facts are classified, normalized, reconciled, and analyzed.

The standard filing workflow is:

source documents → one extracted JSON per filing → deterministic validation → deterministic cross-filing reconciliation → `StandardizedFinancials` → complete BAV reference model → professional BAV workbook → optional derivative Trainer

Canonical Markdown research and reusable figures consume the same validated analytical outputs, with traceability to the workbook and source evidence.

Cross-filing differences, restatements, and source conflicts must be recorded rather than silently overwritten. Later audited presentations may take deterministic precedence, but the superseded observations remain in provenance.

`StandardizedFinancials` remains the model-facing contract. Source paths, page references, extraction evidence, conflicts, and discarded observations remain separate audit artifacts.

PDF/LLM extraction may later be automated through an external model/API, but the BAV accounting engine must remain provider-independent and consume validated structured data rather than model responses directly.

## Curriculum progression

The learner should progress through three levels.

### Level 1 — Guided model construction

The system supplies source financials, accounting classifications, market facts, and setup judgments. The learner reconstructs formulas, links, reformulation schedules, ratios, bridges, and analytical calculations.

### Level 2 — Analyst judgment

The system still supplies source facts, but selected classification, normalization, and accounting-treatment decisions become explicit exercises. The learner chooses and defends treatments and reconciles the resulting model.

### Level 3 — Research application

The learner receives company filings/source extracts and must build the historical analytical model, identify accounting distortions, interpret performance drivers, forecast the business, value the company, and produce a concise investment-oriented conclusion.

The intended progression is:

supplied judgment → guided judgment → independent accounting analysis → historical research diagnostics → driver-based forecasting → valuation → investment interpretation

Ambiguous accounting treatments should be taught as alternatives with consequences rather than as one universally correct answer.

## Historical Step 9 — current product stage

The historical-v1 model-construction foundation is release-gated and usable for learning now. Step 9 continues after that baseline toward a professional historical BAV product and its secondary training derivative.

Preserve existing historical capabilities:

- multi-period source links and reformulated statements;
- NOPAT, NOWC, NOLA, NOA, Net Debt, and reformulated Equity;
- historical growth, margins, effective tax, financing metrics, RNOA, Spread, FLEV, ROE, and DuPont;
- guided Accounting Judgment for supported classification alternatives;
- guided recurring/non-recurring earnings normalization;
- cash-conversion and accrual diagnostics and trends;
- working-capital diagnostics and driver decomposition;
- RNOA margin/turnover and change attribution;
- ROE operating/financing attribution;
- historical diluted per-share analysis when actual diluted weighted-average share history is supplied;
- normalized diluted EPS when both share history and normalization cases are supplied;
- workbook-wide Check;
- completed reference-model formulas and Notes with a matched Trainer;
- cross-company synthetic robustness tests.

Forecasting, valuation, scenario analysis, and investment conclusions remain deferred while Step 9 historical convergence continues.

## Reference workbook for historical convergence

`example/GOOGL_Demo_Integrated_Financials.xlsx` is the project’s **reference workbook for structural coherence and analytical completeness**.

Use it to study:

- how source statements, reformulation, DuPont, earnings-quality analysis, and downstream analytical schedules fit together;
- how an integrated analyst workbook organizes historical information without fragmenting the model;
- which historically useful analytical sections are still missing from the BAV;
- how information density and dependency flow can be improved.

It is **not** a literal template.

Do not automatically copy:

- its decorative styling;
- its populated calculations into Trainer practice cells;
- pipeline/automation features;
- quarterly, forecasting, scenario, valuation, or market-monitoring features merely because they exist there;
- any source facts not explicitly supplied for the company.

A feature from the GOOGL workbook should enter the BAV only when it is historically relevant, analytically useful and supported by explicit source facts. Trainer derivation should preserve the relevant semantic mapping and Check behavior.

The BAV should converge toward the reference workbook’s integration and analytical depth. The Trainer retains its learning mechanics as a derivative.

## Historical accounting competence to cover

Step 9 should continue toward coverage of these topics where material and supported by supplied facts:

- three-statement linkage and accounting sign conventions;
- operating versus financing classification;
- recurring versus transitory / non-recurring items;
- earnings normalization;
- accruals, cash conversion, and quality of earnings;
- working-capital behavior;
- revenue growth and margin analysis;
- capex, depreciation, asset intensity, and turnover;
- leases;
- stock-based compensation and dilution;
- goodwill, acquired intangibles, and acquisitions;
- deferred taxes and unusual tax rates;
- minority / non-controlling interests;
- historical share counts and per-share bridges;
- segment economics where disclosed;
- accounting consistency checks and detection of suspicious or internally inconsistent results;
- operating/financing reformulation under the BAV framework;
- RNOA, after-tax cost of debt, Spread, FLEV, ROE decomposition, and related profitability diagnostics.

The product should not require every topic for every company. Optional modules should be gated by materiality and source availability.

## Interpretation is part of the product

Major schedules should explain what changed economically and why it matters, as well as how a number is calculated.

The historical decomposition is the primary analytical object. Strengthen the existing Drivers analysis through this sequence:

reported outcome → decomposition → measurable components / admitted KPIs → historical contribution analysis → reconstruction of actual results → residuals and contradictions → source and management-disclosure check → interpretation

For each material outcome, answer: what happened, what moved it mathematically, and what explains those arithmetic movements? State the relationship or formula, calculate across available historical periods, compare implied changes with reported changes, and expose unexplained components. Prefer a few economically meaningful, source-supported decompositions over weak ratio catalogues.

Revenue analysis retains or improves the existing driver tree using admitted geography/segment, footprint, comparable-sales, channel or other operational evidence where available. Quantify geographic contributions and test footprint versus intensity relationships without inventing missing components. Company-wide revenue per store is a historical intensity proxy, not pure store productivity when digital or other channels contribute. Preserve channel, currency, calendar and definition distinctions.

Margin analysis explicitly follows the three-question structure. State historical revenue, gross profit, gross margin, SG&A burden, other material operating items, operating profit and operating margin. Where disclosed, use:

Operating margin = Gross margin − SG&A / Revenue − impairment or asset-related charges / Revenue − other reported operating items / Revenue.

Bridge changes with consistent signs and denominators in percentage points or basis points. Reconcile levels and changes to reported operating margin and show any residual. Do not hide disclosed components in an aggregate operating burden or invent undisclosed subcomponents.

After establishing the arithmetic, trace explanations such as mix, markdowns, freight, input costs, occupancy, geographic mix and leverage/deleverage to source evidence. Preserve management explanations as attributed statements; measure causal contributions only where disclosures support the calculation. Inspect existing extracts and admission evidence first, extending source extraction through existing controls only for necessary gaps.

For each non-trivial proposed driver relationship, historical validation tests direction, magnitude, reconstruction, residual, stability across periods, contradictions and the disclosure check. Use compact bridges or tables. Validation tests the decomposition against observed history; it is not a separate predictive model. Do not add statistically elaborate models unsupported by the historical sample.

Clearly distinguish accounting identity, reported historical fact, management explanation or strategy, observed historical relationship, economically plausible causal hypothesis and inference not established by evidence. An accounting identity or correlation alone does not establish a causal driver. Reconsider unsupported explanations or state that evidence is insufficient.

Use this history to identify informative versus weak relationships, recurring versus episodic movements, accounting growth versus underlying operating improvement, and sourced claims versus inference. Methods generalize across companies; benchmark issuers do not justify issuer-specific analytical rules. Apply the same approach beyond revenue and margin only where a material outcome and available evidence justify it.

Other interpretation questions include:

- Was a decline in RNOA caused by lower operating margins or greater NOA intensity?
- Did earnings growth come from operating improvement, leverage, acquisitions, tax effects, or dilution?
- Is cash conversion consistent with reported profitability?
- Does a working-capital movement reflect growth, deterioration, seasonality, or accounting treatment?
- Is an apparent improvement in ROE operating or financing-driven?

The workbook need not grade free-form essays yet. Structured diagnostics and concise explanatory material are preferred until a reliable research-writing evaluation layer exists.

## Historical learner experience

1. Supply historical company source documents or already-extracted filing JSON.
2. Convert each filing into source-grounded structured facts, then validate and reconcile those facts into model-facing historical input.
3. Build the complete historical BAV analysis from accepted facts and setup judgments.
4. Produce `<Company>_BAV.xlsx` as the default professional deliverable.
5. Optionally derive `<Company>_BAV_Trainer.xlsx` from the same completed model.
6. In the Trainer, source data and supplied facts remain populated. The learner fills selected yellow historical formula cells and guided judgment-response cells.
7. Run **Check** when desired: blank cells remain yellow, correct cells become green and incorrect cells become red.
8. Consult the matching BAV for correct formulas and concise analytical Notes. The BAV uses ordinary white/no-fill cells and contains no yellow fill or yellow highlighting.

The BAV is the authoritative formula-and-Note reference. Check validates only; it does not reveal answers. The BAV must remain professionally presented rather than adopting learning instructions.

## What stays populated

The Trainer should not make the learner re-enter literal data that the system already knows. Keep populated:

- historical source-statement numbers;
- historical share-count data and market facts when supplied;
- labels, dates, units, and workbook setup;
- system-controlled source links or checks intentionally outside the current practice surface;
- supplied setup/judgment facts until the relevant judgment exercise explicitly makes them learner-controlled.

The default test is: **does reconstructing this cell teach historical model logic or only data entry?**

## Hard requirements for the historical product

- **Historical reference-model first.** The professional BAV contains the complete working historical model; Trainer formulas derive from it.
- **No invented historical inputs.** Historical ratios, KPIs and per-share metrics use supplied historical facts only. Synthetic fixtures are not production evidence.
- **Source-grounded structured handoff.** Filing-based LLM extraction produces one auditable JSON artifact per source filing before BAV standardization; source conflicts/restatements are preserved in audit artifacts.
- **Professional default deliverable.** Ordinary company builds produce `<Company>_BAV.xlsx`. Successful builds and intermediate Session progress do not require Trainer generation.
- **Secondary Trainer.** Preserve optional derivation of `<Company>_BAV_Trainer.xlsx` from the completed model. Do not add unnecessary CLI commands solely for this distinction.
- **Formula-construction focus.** Practice should teach model logic, not transcription.
- **Trainer contains no active answers or hints.** Active formula-practice cells start blank yellow with no Note/comment.
- **BAV contains formulas and analytical Notes, with no yellow.** Cells corresponding to Trainer practice contain correct formulas and concise non-empty Notes, using ordinary white/no-fill formatting.
- **Workbook-wide Check.** One Check validates every active historical practice cell.
- **Check is non-disclosing.** Aggregate counts are allowed; answers/formulas/hints are not printed or inserted.
- **Shared analytical structure.** BAV and Trainer retain corresponding analytical identities and schedules. Opening presentation and learning instructions may differ according to product purpose.
- **Restrained presentation.** Preserve Aptos Narrow 11, black text and ordinary white cells for the existing analytical surface. Bright yellow denotes only Trainer practice; green/red denote functional Check feedback. Avoid decorative borders and fills. Professional opening and analytical presentation should materially improve understanding. STYLE.md governs research presentation; Session 4 does not require restyling the preserved analytical workbook.
- **Semantic component mapping.** Practice formulas resolve by semantic identity rather than fragile static coordinates.
- **Professional workbook preserved.** Trainer derivation removes only selected learning cells and adds training presentation; it must not mutate the BAV. Source facts and non-practice calculations remain populated.
- **Standardized identity survives round trips.** Identity-bearing fields such as `LineItem.concept` survive supported standardized-data export/reload.
- **Historical accounting logic is authoritative.** Reformulation and DuPont math remain aligned with BAV methodology.
- **Non-financial-company scope.** Do not imply the same reformulation is universal for financial institutions.
- **Forecast isolation.** Normal Step 9 builds must not execute dormant forecasting or valuation code.

## Step 9 roadmap before forecasting

The historical roadmap retains:

1. historical reformulation and DuPont foundation;
2. multi-period completion;
3. accounting judgment and normalization;
4. earnings-quality, cash-conversion, working-capital, profitability, financing, and per-share diagnostics;
5. cross-company robustness;
6. professional BAV presentation, derivative Trainer and practical documentation;
7. **GOOGL historical reference audit:** compare the historical model with `GOOGL_Demo_Integrated_Financials.xlsx` and classify historical gaps;
8. **historical convergence:** implement the highest-value missing historical analytical modules supported by explicit data, including where appropriate capex/depreciation/asset intensity, leases, SBC/dilution, goodwill/acquisitions, deferred tax, NCI, segment economics, and consistency checks;
9. **unseen-company / real-company historical validation:** validate the complete source-document → filing-JSON → reconciliation → `StandardizedFinancials` handoff and prove the professional model and derivative Trainer work beyond synthetic fixtures and the illustrative demo;
10. only after historical Step 9 is coherent and usable, reintroduce driver-based forecasting;
11. only after forecasting is separately verified, add valuation, scenarios, and investment conclusions.

SESSION.md specifies the current Endpoint and Priority within this destination. Full normalization, NOA and NOPAT completion need not precede historical driver-and-strategy analysis unless directly necessary for it.

Do not jump from the release-gated historical-v1 baseline directly into forecasting merely because the baseline is technically complete.

## Autonomous progression policy

Step 9 remains the current historical stage. Autonomous planning should continue material, source-supported work within the Session Endpoint and Priority. Do not advance merely because a convenient implementation milestone has been reached.

Step 9 is not open-ended. Do not create low-value historical work merely to remain in Step 9.

### Current analytical focus gate

The former three-area hard priority gate is superseded by the explicit BAV-first Session direction. Endpoint and Priority belong in SESSION.md.

Preserve accepted Geographic Analysis, Operating KPIs and Normalization Judgment / Earnings Normalization work. Unfinished normalization and broader accounting work remain open long-term obligations; do not represent deferral as completion.

Preserve already accepted accounting, ingestion, geographic, KPI, normalization, provenance, workbook and regression work unless a demonstrated defect prevents the Session Endpoint.

Historical Net Debt / Debt-Like Items Bridge, Complete NOPAT / RNOA and forecasting remain deferred unless a bounded historical dependency is directly necessary for the current Endpoint. Historical Lululemon M&A target assessment is permitted within the Scope boundary; buyer-specific analysis and deal recommendations remain excluded.

### Step 9 exit gate

Step 9 is complete when all of the following are true:

- the GOOGL historical reference audit has no unresolved high-value historical gap;
- historically material modules supported by available source facts are implemented, tested, or explicitly deferred with a documented reason;
- the source-document → filing JSON → reconciliation → `StandardizedFinancials` → reference-model → professional BAV → derivative Trainer path has been demonstrated on real-company data;
- optional historical modules fail closed when required evidence is missing or contradictory;
- historical analytical schedules, learner practice surfaces, Check behavior, provenance, and workbook generation pass their required regression and benchmark tests;
- no known historical defect or missing module materially limits analysis of an unfamiliar non-financial company.

Once this gate is satisfied, subsequent authorized planning should advance toward Step 10 rather than inventing additional historical polish. It must still respect an explicit Session boundary; completing a Session does not automatically start another.

A completed roadmap item should not be reopened unless a later regression, benchmark, or new source-supported requirement exposes a concrete defect.

### Step 10 — Driver-based forecasting

Build forecasting only after Step 9 passes its exit gate and the active Session permits forecasting.

The forecasting system should:

- begin from the verified historical analytical model;
- forecast explicit operating drivers rather than extrapolating outputs mechanically;
- link revenue, margins, working capital, capex, depreciation, taxes, financing, and share-count assumptions to the relevant historical diagnostics;
- distinguish supplied assumptions, learner assumptions, and calculated outputs;
- preserve accounting identities and historical/forecast continuity;
- make key assumptions auditable and suitable for learner practice;
- support a coherent base case before introducing alternative scenarios.

Step 10 is complete when an unfamiliar supported company can move from verified historical analysis to an internally coherent, driver-based forecast with tested formulas, assumptions, and accounting links.

### Step 11 — Valuation and scenarios

Only after Step 10 is verified, add valuation and scenario analysis.

The valuation system should:

- consume the verified historical and forecast model rather than duplicate it;
- implement BAV-consistent valuation methods and appropriate cross-checks;
- make cost-of-capital, terminal-value, and other material valuation assumptions explicit;
- support disciplined Bear / Base / Bull scenarios by changing economically meaningful drivers;
- expose major sensitivities without creating arbitrary scenario complexity;
- reconcile valuation outputs to per-share equity value and relevant market inputs.

Step 11 is complete when valuation is internally reconciled, scenario differences can be traced to explicit assumptions, and major sensitivities are visible and testable.

### Step 12 — Investment interpretation

Only after historical analysis, forecasting, and valuation are verified, build the final research interpretation layer.

The analyst, and subsequently the learner, should be able to:

- identify the principal historical and forecast value drivers;
- distinguish operating improvement from financing, accounting, tax, acquisition, and dilution effects;
- state the assumptions on which valuation depends;
- identify material risks and variant views;
- connect scenario and sensitivity results to the investment thesis;
- produce a concise, evidence-based investment conclusion.

Prefer structured analytical prompts and verifiable outputs before introducing unrestricted free-form grading.

### Autonomous planning rule

Use the existing AutoCycle Completion and Review control loop.

Within the active Session, choose the smallest direct work that materially advances its Endpoint, governed by its Priority. Prefer meaningful end-to-end product capability and reuse of adequate working subsystems.

Defer infrastructure refinement, hypothetical edge-case hardening, cosmetic work and abstractions that are unnecessary for the Endpoint.

The long-term stage order remains Step 9 → Step 10 → Step 11 → Step 12. Advance only when stage exit conditions are supported by evidence and the active Session permits that scope.

`DONE` requires the Session Endpoint and current plan acceptance, not merely publication or consumption of instructions. Never start a new Session automatically.

## Forecast / valuation boundary

Forecasting, residual-income valuation, DCF/cross-check valuation, terminal value, Bear/Base/Bull scenarios, and forward valuation multiples remain deferred during the current Step 9 stage.

Historical relationships must not become forward assumptions in a historical-only Session. Later forecasting requires both the Step 9 exit gate and a Session permitting that work.

The repository may retain dormant forecast/valuation scaffolding, but normal historical builds must not execute it or depend on forecast outputs.

Deferred tabs may remain hidden placeholders: `Model_Bear`, `Model_Base`, `Model_Bull`, `Scenario_Summary`.

They must remain excluded from the active semantic practice surface and Check until a future forecasting stage explicitly activates them.

## Definition of done for the current historical baseline

The BAV-first historical baseline is complete when supported historical data for a non-financial company produces a professional BAV and permits derivation of a matching Trainer in which:

- the historical model is internally coherent;
- source facts remain populated;
- the default deliverable is the professional BAV without required Trainer generation;
- active Trainer formula cells are blank yellow;
- matching BAV cells contain correct formulas and analytical Notes and are ordinary white/no-fill;
- the BAV contains no yellow fill/highlight or exercise framing;
- Check validates the full active Trainer surface without disclosing answers;
- optional modules appear only when their required historical facts are supplied;
- normal generation does not run forecasting/valuation code;
- the BAV is usable as professional historical analysis and the derivative Trainer is usable for learning.

This baseline being complete does **not** freeze Step 9. Historical depth, reference-workbook convergence, accounting-analysis breadth, and real-company validation can continue within authorized Sessions before forecasting begins.

## End-state definition of done

The broader BAV research system succeeds when an unfamiliar supported non-financial company can be analyzed through a professional, auditable research workbook, canonical Markdown modules, reusable figures and shareable Word/PDF publications that enable the analyst to:

- construct and audit the historical accounting model;
- make defensible material accounting/reformulation judgments;
- identify and explain material earnings-quality and accounting issues;
- diagnose historical economic drivers;
- build explicit forecasts linked to those drivers;
- value the equity using BAV-consistent methods and appropriate cross-checks;
- explain key sensitivities, risks, and variant assumptions; and
- communicate a concise, evidence-based investment conclusion.

The secondary Trainer should enable an accounting novice to progress toward solving such an unseen-company research case with materially less scaffolding.

## Planning ownership

This file records stable product intent. Target changes require explicit human instruction. ChatGPT owns planning publication; Cursor must never modify `TARGET.md`, `SESSION.md` or `IMPLEMENTATION.md`.

SESSION.md holds the current Endpoint and Priority. IMPLEMENTATION.md holds current bounded execution guidance. RESULT.md records implementation completion and measured verification.
