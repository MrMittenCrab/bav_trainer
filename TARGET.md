# TARGET.md

## Product target

Build **BAV Excel Trainer — Hong Kong Edition** as a progressive training system that can take an **accounting novice** toward competence as a junior accounting-based equity-research analyst, with particular strength in Business Analysis and Valuation (BAV).

The end-state learner should be able to receive the historical financial materials of an unfamiliar non-financial company and progressively learn to:

1. trace reported information into a research model;
2. understand three-statement relationships and accounting sign conventions;
3. make and defend material accounting, classification, and normalization judgments;
4. construct and audit historical analytical schedules;
5. explain changes in profitability, capital intensity, financing, cash conversion, and per-share economics;
6. convert historical analysis into explicit forecasts and valuation assumptions;
7. value the equity using BAV-consistent methods and appropriate cross-checks; and
8. communicate a concise, evidence-based investment conclusion.

Formula correctness is necessary but not sufficient. The trainer should optimize for analyst competence: model construction, accounting judgment, economic interpretation, auditability, forecasting discipline, valuation, and research communication.

## Scope boundary

The initial curriculum is for **non-financial operating companies**. Banks, insurers, brokers, and other financial institutions require separate sector-specific accounting and valuation logic.

Hong Kong company input may remain manual. Automatic HKEX scraping is not required when annual reports, interim reports, results materials, Excel exports, Bloomberg exports, or Wind exports are supplied.

Exercises should follow materiality and the information actually supplied. Missing historical facts must not be invented.

## Source-data architecture

The analytical engine does not interpret arbitrary PDFs directly.

For filing-based workflows, the canonical upstream handoff is **source-grounded filing JSON**. Each filing is extracted independently and preserves reported labels, statement sections, periods, currency/unit scale, values, and page-level provenance.

LLM-assisted extraction is permitted upstream, but extraction must remain separate from BAV accounting judgment and analytical modeling. The extractor records what the filing says; BAV determines how accepted reported facts are classified, normalized, reconciled, and analyzed.

The standard filing workflow is:

```text
source documents
    → one extracted JSON per filing
    → deterministic validation
    → deterministic cross-filing reconciliation
    → StandardizedFinancials
    → BAV reference model
    → Answer Key + Trainer
```

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

```text
supplied judgment
    -> guided judgment
    -> independent accounting analysis
    -> historical research diagnostics
    -> driver-based forecasting
    -> valuation
    -> investment interpretation
```

Ambiguous accounting treatments should be taught as alternatives with consequences rather than as one universally correct answer.

## Historical Step 9 — current product stage

The historical-v1 model-construction foundation is release-gated and usable for learning now. Step 9 continues after that baseline: the next work should deepen the historical learning product before forecasting begins.

Current historical capabilities include:

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
- matched Trainer and Answer Key;
- cross-company synthetic robustness tests.

Forecasting, valuation, scenario analysis, and investment conclusions remain deferred while Step 9 historical convergence continues.

## Reference workbook for historical convergence

`example/GOOGL_Demo_Integrated_Financials.xlsx` is the project’s **reference workbook for structural coherence and analytical completeness**.

Use it to study:

- how source statements, reformulation, DuPont, earnings-quality analysis, and downstream analytical schedules fit together;
- how an integrated analyst workbook organizes historical information without fragmenting the model;
- which historically useful analytical sections are still missing from the Trainer;
- how information density and dependency flow can be improved.

It is **not** a literal template.

Do not automatically copy:

- its decorative styling;
- its pre-filled answers instead of training cells;
- pipeline/automation features;
- quarterly, forecasting, scenario, valuation, or market-monitoring features merely because they exist there;
- any source facts not explicitly supplied for the Trainer company.

A feature from the GOOGL workbook should enter the Trainer only when it is historically relevant, pedagogically useful, supported by explicit source facts, and consistent with the Trainer/Answer-Key/Check workflow.

The Trainer should therefore converge toward the GOOGL workbook’s **integration and analytical depth**, while preserving the Trainer’s learning mechanics.

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

The trainer should not require every topic for every company. Optional modules should be gated by materiality and source availability.

## Interpretation is part of the product

For major schedules, the learner should eventually answer not only how a number is calculated but what changed economically and why it matters.

Examples include:

- Was a decline in RNOA caused by lower operating margins or greater NOA intensity?
- Did earnings growth come from operating improvement, leverage, acquisitions, tax effects, or dilution?
- Is cash conversion consistent with reported profitability?
- Does a working-capital movement reflect growth, deterioration, seasonality, or accounting treatment?
- Is an apparent improvement in ROE operating or financing-driven?

The workbook need not grade free-form essays yet. Structured diagnostics and concise explanatory material are preferred until a reliable research-writing evaluation layer exists.

## Historical learner experience

1. Supply historical company source documents or already-extracted filing JSON.
2. Convert each filing into source-grounded structured facts, then validate and reconcile those facts into model-facing historical input.
3. Build the historical reference analysis from accepted facts and setup judgments.
4. Generate a matched `*_Trainer.xlsx` / `*_Answer_Key.xlsx` pair.
5. In the Trainer, source data and supplied facts remain populated. The learner fills selected yellow historical formula cells and guided judgment-response cells.
6. Run **Check** when desired:
   - blank -> yellow;
   - correct -> green;
   - incorrect -> red.
7. Open the matching Answer Key when the learner wants the formula or the concise Note hint. Answer-Key cells remain ordinary white/no-fill; the Answer Key must contain no yellow fill or yellow highlighting anywhere.

The Answer Key is the sole answer-and-hint surface. Check validates only; it does not reveal answers.

## What stays populated

The Trainer should not make the learner re-enter literal data that the system already knows. Keep populated:

- historical source-statement numbers;
- historical share-count data and market facts when supplied;
- labels, dates, units, and workbook setup;
- system-controlled source links or checks intentionally outside the current practice surface;
- supplied setup/judgment facts until the relevant judgment exercise explicitly makes them learner-controlled.

The default test is: **does reconstructing this cell teach historical model logic or only data entry?**

## Hard requirements for the historical product

- **Historical reference-model first.** Trainer formulas come from a complete working historical model.
- **No invented historical inputs.** Historical ratios and per-share metrics use supplied historical facts only.
- **Source-grounded structured handoff.** Filing-based LLM extraction produces one auditable JSON artifact per source filing before BAV standardization; source conflicts/restatements are preserved in audit artifacts.
- **Formula-construction focus.** Practice should teach model logic, not transcription.
- **Exactly two user-facing workbooks.** One Trainer and one matching Answer Key.
- **Trainer contains no active answers or hints.** Active formula-practice cells start blank yellow with no Note/comment.
- **Answer Key contains formula + Note and no yellow.** Matching practice cells contain the correct formula and a concise non-empty Note, but use ordinary white/no-fill formatting. No visible Answer-Key cell may use yellow fill or yellow highlighting.
- **Workbook-wide Check.** One Check validates every active historical practice cell.
- **Check is non-disclosing.** Aggregate counts are allowed; answers/formulas/hints are not printed or inserted.
- **Visual parity.** Trainer and Answer Key share the same visible historical structure and typography except practice contents, Answer-Key Notes, and the intentional fill difference: Trainer practice cells are yellow while Answer-Key counterparts are ordinary white/no-fill.
- **Minimal learner aesthetic.** Fresh visible cells use Aptos Narrow 11, non-bold, black text; ordinary cells are white; only learner-editable/practice cells in the Trainer are bright yellow; the Answer Key contains no yellow fill/highlight. Green/red are reserved for functional Check feedback after validation. No decorative borders or decorative fill colors.
- **Semantic component mapping.** Practice formulas resolve by semantic identity rather than fragile static coordinates.
- **Professional workbook preserved.** Training mode removes only selected learning cells; source facts and non-practice calculations remain populated.
- **Standardized identity survives round trips.** Identity-bearing fields such as `LineItem.concept` survive supported standardized-data export/reload.
- **Historical accounting logic is authoritative.** Reformulation and DuPont math remain aligned with BAV methodology.
- **Non-financial-company scope.** Do not imply the same reformulation is universal for financial institutions.
- **Forecast isolation.** Normal Step 9 builds must not execute dormant forecasting or valuation code.

## Step 9 roadmap before forecasting

Step 9 should proceed in this order:

1. historical reformulation and DuPont foundation;
2. multi-period completion;
3. accounting judgment and normalization;
4. earnings-quality, cash-conversion, working-capital, profitability, financing, and per-share diagnostics;
5. cross-company robustness;
6. learner-ready presentation and practical documentation;
7. **GOOGL historical reference audit:** compare the current Trainer with `GOOGL_Demo_Integrated_Financials.xlsx` and classify historical gaps;
8. **historical convergence:** implement the highest-value missing historical analytical modules supported by explicit data, including where appropriate capex/depreciation/asset intensity, leases, SBC/dilution, goodwill/acquisitions, deferred tax, NCI, segment economics, and consistency checks;
9. **unseen-company / real-company historical validation:** validate the complete source-document → filing-JSON → reconciliation → `StandardizedFinancials` handoff and prove the learning product works beyond synthetic fixtures and the illustrative demo;
10. only after the historical Step 9 curriculum is coherent and usable, reintroduce driver-based forecasting;
11. only after forecasting is separately verified, add valuation, scenarios, and investment conclusions.

Do not jump from the release-gated historical-v1 baseline directly into forecasting merely because the baseline is technically complete.

## Autonomous progression policy

Step 9 remains the highest priority. Autonomous planning should continue historical work while there is a material, source-supported gap in the Step 9 roadmap. Do not advance merely because a convenient implementation milestone has been reached.

However, Step 9 is not open-ended. Do not create low-value historical work merely to remain in Step 9.

### Current analytical focus gate

Until the following three analytical areas are acceptance-complete, autonomous planning should treat them as the **all-things-considered hard priority gate** for future work:

1. **Geographic Analysis** — including the currently in-flight geographic workbook schedules, learner surface, and Check integration;
2. **Operating KPIs**;
3. **Normalization Judgment + Earnings Normalization**.

Apply this gate without fighting the natural dependency order of the codebase. AutoCycle may choose among the three based on prerequisites, implementation dependencies, source availability, risk, and the highest-value next increment. It may also perform bounded work outside the three when that work is necessary to unblock, validate, repair, or preserve one of them or an already-accepted dependency. Such work is part of satisfying the gate, not a detour from it.

While this gate is open, do not start an independent lower-priority analytical module merely because it is convenient. In particular, defer standalone work on **M&A Net Debt / Debt-Like Items Bridge**, **Complete NOPAT / RNOA**, and **Bear / Base / Bull Standalone Forecast** until the three focus areas above are acceptance-complete, except where a bounded dependency is strictly required to support or validate a focus area. Existing stage boundaries still apply, so forecasting/scenario work remains deferred until the historical and forecasting gates elsewhere in this target permit it.

The current geographic workbook-schedule work already advances Priority 1 and should continue naturally rather than being restarted or displaced by this policy.

### Step 9 exit gate

Step 9 is complete when all of the following are true:

- the GOOGL historical reference audit has no unresolved high-value historical gap;
- historically material modules supported by available source facts are implemented, tested, or explicitly deferred with a documented reason;
- the source-document → filing JSON → reconciliation → `StandardizedFinancials` → reference-model → Trainer/Answer-Key path has been demonstrated on real-company data;
- optional historical modules fail closed when required evidence is missing or contradictory;
- historical analytical schedules, learner practice surfaces, Check behavior, provenance, and workbook generation pass their required regression and benchmark tests;
- no known historical defect or missing module materially limits the learner's ability to analyze an unfamiliar non-financial company.

Once this gate is satisfied, the next plan must advance to Step 10 rather than inventing additional historical polish.

A completed roadmap item should not be reopened unless a later regression, benchmark, or new source-supported requirement exposes a concrete defect.

### Step 10 — Driver-based forecasting

Build forecasting only after Step 9 passes its exit gate.

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

The learner should be able to:

- identify the principal historical and forecast value drivers;
- distinguish operating improvement from financing, accounting, tax, acquisition, and dilution effects;
- state the assumptions on which valuation depends;
- identify material risks and variant views;
- connect scenario and sensitivity results to the investment thesis;
- produce a concise, evidence-based investment conclusion.

Prefer structured analytical prompts and verifiable outputs before introducing unrestricted free-form grading.

### Autonomous planning rule

For unattended development, always work on the lowest-numbered incomplete stage:

Step 9 → Step 10 → Step 11 → Step 12.

Within Step 9, apply the **Current analytical focus gate** before the generic highest-value rule. Within any permitted scope, choose the highest-value unresolved dependency or defect, not cosmetic polish.

Advance to the next stage only when the current stage's exit conditions are supported by repository evidence and tests.

If the broader end-state is reached before the requested autocycle count is exhausted, return `DONE` and stop rather than manufacturing additional work.

## Forecast / valuation boundary

Forecasting, residual-income valuation, DCF/cross-check valuation, terminal value, Bear/Base/Bull scenarios, and forward valuation multiples remain deferred during the current Step 9 stage.

This deferral ends automatically when the Step 9 exit gate above is satisfied; no separate product-direction decision is required to begin Step 10.

The repository may retain dormant forecast/valuation scaffolding, but normal historical builds must not execute it or depend on forecast outputs.

Deferred tabs may remain hidden placeholders:

```text
Model_Bear
Model_Base
Model_Bull
Scenario_Summary
```

They must remain excluded from the active semantic practice surface and Check until a future forecasting stage explicitly activates them.

## Definition of done for the current historical baseline

The current historical baseline is complete when supported historical data for a non-financial company produces a matched Trainer/Answer-Key pair in which:

- the historical model is internally coherent;
- source facts remain populated;
- active Trainer formula cells are blank yellow;
- matching Answer-Key cells contain correct formulas and Notes and are ordinary white/no-fill;
- the Answer Key contains no yellow fill/highlight anywhere;
- Check validates the full active surface without disclosing answers;
- optional modules appear only when their required historical facts are supplied;
- normal generation does not run forecasting/valuation code;
- the workbook is usable as a learning product.

This baseline being complete does **not** freeze Step 9. Historical depth, reference-workbook convergence, accounting-analysis breadth, and real-company validation can continue before forecasting begins.

## End-state definition of done

The broader BAV Trainer succeeds only when an accounting novice can progress to solving an unseen non-financial-company research case with materially less scaffolding and can demonstrate all of the following:

- construct and audit the historical accounting model;
- make defensible material accounting/reformulation judgments;
- identify and explain material earnings-quality and accounting issues;
- diagnose historical economic drivers;
- build explicit forecasts linked to those drivers;
- value the equity using BAV-consistent methods and appropriate cross-checks;
- explain key sensitivities, risks, and variant assumptions; and
- communicate a concise, evidence-based investment conclusion.

## Planning ownership

This file records stable product intent. **ChatGPT owns planning changes to TARGET.md. Cursor should treat it as read-only unless ChatGPT explicitly instructs otherwise.** Implementation details belong in `IMPLEMENTATION.md` and the codebase.