# TARGET.md

## Product target

Build **BAV Excel Trainer — Hong Kong Edition** as a progressive training system that can take an **accounting novice** toward competence as a junior accounting-based equity-research analyst, with particular strength in **Business Analysis and Valuation (BAV)**.

The trainer should eventually prepare a learner to receive the historical financial materials of a non-financial listed company and independently:

1. trace reported information into a research model;
2. understand the three-statement relationships and accounting sign conventions;
3. make and defend material accounting, classification, and normalization judgments;
4. construct and audit historical analytical schedules;
5. explain changes in profitability, capital intensity, financing, cash conversion, and per-share economics;
6. convert historical analysis into explicit forecasts and valuation assumptions; and
7. communicate the resulting investment implications clearly enough for junior equity-research work.

**Formula correctness is necessary but not sufficient.** The end-state product must progressively teach accounting judgment, economic interpretation, model auditability, forecasting discipline, valuation, and research communication.

## Employment competency target

A learner who completes the full curriculum should be able to perform the core work expected of a postgraduate junior equity-research hire rather than merely reproduce spreadsheet syntax.

The target standard is:

> Given a company's financial statements, relevant notes, and market facts, the learner can build and audit a historical accounting model, identify material accounting distortions, reformulate reported results consistently, diagnose the economic drivers and quality of performance, construct explicit forecasts from those drivers, value the equity, and explain what matters for an investment decision.

The trainer should therefore optimize for **analyst competencies**, not raw exercise count. Component counts are implementation acceptance tests, not the product definition of progress.

## Scope boundary

The initial curriculum is for **non-financial operating companies**. Banks, insurers, brokers, and other financial institutions require separate sector-specific accounting and valuation logic and are outside the initial competency scope.

Hong Kong company input remains manual where appropriate. Automatic HKEX scraping is not required when supplied annual reports, interim reports, results materials, Excel exports, Bloomberg exports, or Wind exports are sufficient.

## Curriculum progression

The learner should progress through three levels of scaffolding.

### Level 1 — Guided model construction

The system supplies source financials, accounting classifications, market facts, and setup judgments. The learner reconstructs formulas, links, reformulation schedules, ratios, bridges, and analytical calculations.

Purpose: learn statement linkage, dependency logic, model structure, and BAV mechanics without being blocked by unfamiliar accounting judgments.

### Level 2 — Analyst judgment

The system still supplies source facts, but selected classification, normalization, and accounting-treatment decisions become explicit exercises. The learner must choose and defend treatments and reconcile the resulting model.

Purpose: move from mechanical spreadsheet construction to accounting analysis.

### Level 3 — Research application

The learner receives company filings/source extracts and must build the historical analytical model, identify accounting distortions, interpret performance drivers, forecast the business, value the company, and produce a concise investment-oriented conclusion.

Purpose: approximate junior equity-research work on an unfamiliar company.

Early stages may supply judgment inputs. Later stages must progressively remove that scaffolding. The intended progression is:

```text
supplied judgment
    -> guided judgment
    -> independent accounting analysis
    -> driver-based forecasting
    -> valuation
    -> investment interpretation
```

Ambiguous accounting treatments should be taught as alternatives with consequences rather than falsely presented as one universally correct answer.

## Accounting competence required for research

The curriculum should eventually cover, where material and applicable:

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

The trainer should not require every topic for every company. Exercises should follow materiality and the information actually supplied.

## Interpretation is part of the product

For major schedules, the learner should eventually answer not only **how the number is calculated**, but **what changed economically and why it matters**.

Examples include:

- Was a decline in RNOA caused by lower operating margins or greater NOA intensity?
- Did earnings growth come from operating improvement, leverage, acquisitions, tax effects, or dilution?
- Is cash conversion consistent with reported profitability?
- Does a working-capital movement reflect growth, deterioration, seasonality, or accounting treatment?
- Is an apparent improvement in ROE operating or financing-driven?

The initial workbook need not grade free-form essays. Structured diagnostics and concise explanatory material are preferred until a reliable research-writing evaluation layer is designed.

---

## Historical v1 — model-construction foundation

The current v1 is the **historical model-construction foundation**, not the complete equity-research curriculum.

It takes manually supplied historical financial materials, builds a correct historical BAV analysis, and produces two matching professional Excel workbooks:

1. a **Trainer** workbook in which the learner reconstructs selected historical Excel formulas, links, ratios, bridges, and analytical calculations in blank bright-yellow practice cells; and
2. an **Answer Key** workbook in which those same yellow cells contain the correct working Excel formulas and each answer cell has one concise hint in an Excel legacy Note.

The v1 objective is to establish trustworthy historical model mechanics and dependency logic before judgment, forecasting, valuation, and investment interpretation are layered on top.

## v1 boundary

v1 ends at a coherent **historical accounting-model foundation**:

```text
provided historical source statements
    -> supplied classification / setup judgments
    -> historical statement links and derived lines
    -> NOPAT / NOWC / NOLA / NOA / Net Debt / Equity
    -> growth / margins / tax / financing metrics
    -> RNOA / after-tax CoD / Spread / FLEV / ROE / DuPont
    -> historical EPS / per-share metrics when required historical share-count data is supplied
    -> historical accounting-model foundation complete
```

Forecasting, residual-income valuation, DCF/cross-check valuation, terminal value, Bear/Base/Bull scenarios, and forward valuation multiples are **deferred from v1**.

The existing forecasting/valuation source code may remain in the repository as dormant scaffolding for later integration, but the **normal v1 build path must not execute that forecasting/valuation engine, synthesize forecast assumptions, or depend on forecast outputs in order to produce the historical product**.

When forecasting is reintroduced, prefer integration with the trusted BAVGEM forecasting/assumption architecture and explicit analyst judgment rather than inventing an assumption-free forecasting system.

## Deferred forecast/valuation tabs

The v1 workbooks may retain these tab names so the workbook can evolve later:

```text
Model_Bear
Model_Base
Model_Bull
Scenario_Summary
```

For v1 they are **hidden deferred placeholders**, not live company forecasts or valuation outputs. They must be hidden in both Trainer and Answer Key and excluded from the Trainer index, semantic practice surface, and workbook-wide Check.

A normal v1 build must succeed even if the dormant forecast engine is unavailable or deliberately fails. Hidden deferred tabs must not affect historical formulas, historical expected values, historical build success, or Check.

No public v1 CLI option should enable the deferred forecasting system.

## v1 learner experience

1. Supply historical company financial data/documents manually.
2. Build the historical reference analysis from supplied facts and setup judgments.
3. Generate a matched `*_Trainer.xlsx` / `*_Answer_Key.xlsx` pair.
4. In the Trainer, historical source data, classification decisions, and other supplied facts are already populated. The learner fills only selected yellow **historical model-construction formula cells**.
5. Run **Check** when desired. Check scans every active historical practice cell in one pass and recolors it without changing its contents:
   - blank / unentered -> remains yellow;
   - correct -> green;
   - incorrect -> red.
6. When the learner wants the actual formula or a hint, open the matching Answer Key and inspect the formula / legacy Note in the corresponding yellow cell.

The **Answer Key is the sole answer-and-hint mechanism**. Check is validation only. There is no progressive Hint or Reveal Answer workflow.

## What counts as v1 practice

A v1 practice cell should teach how historical analysis is constructed from already-supplied information. High-value practice includes:

- cross-sheet links connecting historical source statements to analytical schedules;
- effective tax, net-interest, and NOPAT calculations;
- operating/financing reformulation and category aggregates;
- NOWC, NOLA, NOA, Net Debt, and reformulated Equity identities;
- historical revenue growth and profitability margins;
- RNOA, after-tax cost of debt, Spread, FLEV, ROE decomposition, Actual ROE, and related historical ratios;
- historical EPS or per-share calculations when actual historical share-count data is present;
- historical reconciliation/check formulas that teach model logic.

The practice surface should follow the historical dependency graph: upstream links and reformulation before downstream ratios.

## What stays populated in v1

The Trainer should not make the learner re-enter literal data that the system already knows. Keep populated:

- historical source-statement numbers transcribed or imported from filings;
- historical share-count data and market facts when supplied;
- balance-sheet classification choices and other setup/judgment inputs used by the reference model;
- labels, dates, units, formatting, and workbook setup;
- non-practice formulas intentionally outside the current historical training surface.

A literal number or category should not become a practice cell merely because it is editable. The default test is: **does reconstructing this cell teach historical model logic or only data entry?**

Supplying classifications in v1 is a deliberate beginner scaffold, not the end-state design. Later analyst-level modules should progressively turn material classification and normalization decisions into guided judgment exercises.

## Hard requirements for v1

- **Historical reference-model first.** Trainer formulas must come from a complete working historical model, not hand-authored answer keys.
- **Historical build independence.** Normal v1 generation must not call the deferred forecast/scenario engine or require scenario assumptions, forecast vectors, terminal growth, beta, or forward valuation inputs.
- **No invented historical inputs.** Historical ratios and per-share metrics must use supplied historical data. Do not use forecast defaults or fabricated assumptions to fill missing historical facts.
- **Formula-construction focus.** v1 practice consists of formula-bearing historical model-construction cells. Do not add literal-number transcription or classification quizzes merely to increase exercise count.
- **Forecast/valuation deferred.** v1 does not claim to build or teach a trustworthy forward forecast or valuation model. Deferred forecast/valuation tabs are hidden placeholders rather than trusted outputs.
- **Exactly two user-facing workbooks.** One build produces a clearly named Trainer and matching Answer Key; no third reference workbook is required.
- **Trainer contains no answers or hints.** Every active practice cell starts blank bright yellow with no Note/comment. Hidden Trainer sheets and Trainer-associated sidecars must not contain withheld active-practice formulas, expected values, or hints.
- **Answer Key contains formula + Note.** Every corresponding active practice cell contains the correct working formula and a non-empty legacy Excel Note.
- **Workbook-wide Check.** One Check scans every active historical practice cell; deferred forecast/valuation cells are not checked.
- **Check colors only.** Blank stays yellow, correct becomes green, incorrect becomes red; re-running Check recomputes current state without changing learner contents.
- **Check is non-disclosing.** Aggregate counts are allowed; formulas, expected values, hints, and answers are not printed or inserted.
- **No Hint / Reveal product surface.** Opening the Answer Key is how the learner gets the formula or hint.
- **Visual parity.** Trainer and Answer Key share the same visible historical workbook structure and formatting except blank/completed practice contents and Answer Key Notes. Deferred tabs have the same hidden state in both.
- **Reference aesthetic.** Match the supplied professional-model style: Aptos Narrow, 20-point bold worksheet titles, 11-point body text, black text on white, bright-yellow practice cells, restrained thin borders, and appropriate financial number formats.
- **Semantic component mapping.** Historical practice formulas resolve by semantic identity at build time rather than fragile static coordinates.
- **Professional workbook preserved.** Training mode removes only selected historical calculation formulas; source data, classifications, labels, setup, formatting, and non-practice calculations remain populated.
- **Standardized identity survives round trips.** Identity-bearing fields such as `LineItem.concept` must survive supported standardized-data export/reload.
- **Historical accounting logic is authoritative.** Reformulation and historical DuPont math must remain aligned with the underlying BAV methodology rather than becoming a simplified toy model.
- **Non-financial-company scope.** Do not imply that the operating/financing reformulation is a universal template for banks, insurers, brokers, or other financial institutions.

## Historical practice-surface expansion strategy

Expand by coherent historical dependency chains rather than maximizing cell count:

1. **Historical reformulation core:** effective tax, financing result, NOPAT, operating/financial aggregates, NOWC/NOLA/NOA/Net Debt/Equity.
2. **Historical DuPont core:** RNOA, after-tax CoD, Spread, FLEV, decomposed ROE, Actual ROE, growth/margins and related historical ratios.
3. **Multi-period historical completion:** extend meaningful historical formulas across all applicable fiscal periods rather than only one sample period.
4. **Historical per-share analysis:** add EPS/per-share formulas only when actual historical diluted-share data is supplied through the standardized input path.
5. **Accounting-analysis layer:** introduce guided classification, normalization, earnings-quality, accrual/cash-conversion, and other material accounting judgments.
6. **Research diagnostics:** teach the learner to explain historical changes through margins, turnover/capital intensity, financing, cash conversion, dilution, and other company-specific drivers.
7. **Cross-company robustness:** prove the curriculum on multiple materially different non-financial companies rather than optimizing around one demo company.
8. **Forecasting:** reintroduce explicit driver-based forecasts only after historical analysis is trustworthy and BAVGEM's assumption/judgment architecture is integrated.
9. **Valuation and research conclusion:** add BAV/residual-income valuation, appropriate cross-checks, scenario reasoning, and concise investment interpretation only after the forecast layer is separately verified.

## Non-goals for v1

- Executing automatic company forecasts as part of a normal historical build.
- Forward revenue, margin, balance-sheet, or earnings forecasts.
- Bear/Base/Bull scenario construction.
- Residual-income, DCF, terminal-value, or forward valuation exercises.
- Treating default growth/margin/leverage assumptions as company-specific forecasts.
- Manually copying historical numbers from filings into yellow practice cells.
- Literal-number-entry exercises whose main skill is transcription.
- Balance-sheet classification as a quiz surface in the initial guided stage.
- Asking the learner to guess setup/judgment inputs before the relevant judgment module exists.
- Automatically inventing practice questions.
- Requiring decorative Excel formatting reproduction.
- Automatic HKEX ingestion when manual input is sufficient.
- Per-cell/selected-component Check as the normal workflow.
- Check output revealing expected values/formulas.
- Progressive hints or Reveal-answer commands.
- Hiding active answers/hints in Trainer metadata and calling them inaccessible.
- Claiming v1 alone makes the learner job-ready for equity research.

## Definition of done for historical v1

Given supported historical data for a non-financial Hong Kong listed company, the system produces a matched `*_Trainer.xlsx` and `*_Answer_Key.xlsx` pair whose visible product is a coherent historical BAV model-construction foundation.

For every selected historical formula-practice component before Check:

- the Trainer cell is blank bright yellow and contains no Note/comment;
- the Trainer and its associated active metadata contain no withheld answer/hint for that component;
- the corresponding Answer Key cell is bright yellow, contains the correct working formula, and carries a concise non-empty legacy Note.

Historical source data and classification/setup judgments remain populated. Deferred forecast/valuation tabs are hidden placeholders and excluded from practice/Check. Normal historical generation does not run the dormant forecast/scenario engine and does not fabricate forecast assumptions. A single Check action validates all active historical practice cells without disclosing answers.

Historical reformulation and ratio analysis are internally coherent and preserve concept-aware line identity. Historical EPS/per-share analysis is included only where required historical share data is supplied; missing share history is not filled with invented forecast assumptions.

Completing v1 means the **historical model-construction foundation is trustworthy**. It does not yet establish independent accounting judgment, forecasting competence, valuation competence, or full research readiness.

## End-state definition of done

The broader BAV Trainer is successful only when an accounting novice can progress to solving an unseen non-financial-company research case with materially less scaffolding and can demonstrate all of the following:

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
