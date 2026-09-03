# TARGET.md

## Product target

Build **BAV Excel Trainer — Hong Kong Edition v1** as a **historical financial-analysis trainer**.

The system takes manually supplied Hong Kong company historical financial materials, builds a correct historical BAV analysis, and produces two matching professional Excel workbooks:

1. a **Trainer** workbook in which the learner reconstructs important historical Excel formulas, links, ratios, bridges, and analytical calculations in blank bright-yellow practice cells; and
2. an **Answer Key** workbook in which those same yellow cells contain the correct working Excel formulas and each answer cell has one concise hint in an Excel legacy Note.

The trainer is for learning **historical model construction and dependency logic**, not for transcription of numbers from filings, not for guessing judgment inputs, and not yet for forecasting or valuation.

## v1 boundary

v1 ends at a complete historical analytical model.

```text
provided historical source statements
    -> supplied classification / setup judgments
    -> historical statement links and derived lines
    -> NOPAT / NOWC / NOLA / NOA / Net Debt / Equity
    -> growth / margins / tax / financing metrics
    -> RNOA / after-tax CoD / Spread / FLEV / ROE / DuPont
    -> historical EPS / per-share metrics when required historical share-count data is supplied
    -> coherent historical analysis complete
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

## Learner experience

1. Supply historical company financial data/documents manually.
2. Build the historical reference analysis from those supplied facts and setup judgments.
3. Generate a matched `*_Trainer.xlsx` / `*_Answer_Key.xlsx` pair.
4. In the Trainer, historical source data, classification decisions, and other supplied facts are already populated. The learner fills only selected yellow **historical model-construction formula cells**.
5. Run **Check** when desired. Check scans every active historical practice cell in one pass and recolors it without changing its contents:
   - blank / unentered -> remains yellow;
   - correct -> green;
   - incorrect -> red.
6. When the learner wants the actual formula or a hint, open the matching Answer Key and inspect the formula / legacy Note in the corresponding yellow cell.

The **Answer Key is the sole answer-and-hint mechanism**. Check is validation only. There is no progressive Hint or Reveal Answer workflow.

## What counts as practice

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

## What stays populated

The Trainer should not make the learner re-enter literal data that the system already knows. Keep populated:

- historical source-statement numbers transcribed or imported from filings;
- historical share-count data and market facts when supplied;
- balance-sheet classification choices and other setup/judgment inputs used by the reference model;
- labels, dates, units, formatting, and workbook setup;
- non-practice formulas intentionally outside the current historical training surface.

A literal number or category should not become a practice cell merely because it is editable. The default test is: **does reconstructing this cell teach historical model logic or only data entry?**

## Hard requirements

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
- **HK input is manual in v1.** Automatic HKEX scraping is not required when manual source documents/exports are sufficient.
- **Standardized identity survives round trips.** Identity-bearing fields such as `LineItem.concept` must survive supported standardized-data export/reload.
- **Historical accounting logic is authoritative.** Reformulation and historical DuPont math must remain aligned with the underlying BAV methodology rather than becoming a simplified toy model.

## Historical practice-surface expansion strategy

Expand by coherent historical dependency chains rather than maximizing cell count:

1. **Historical reformulation core:** effective tax, financing result, NOPAT, operating/financial aggregates, NOWC/NOLA/NOA/Net Debt/Equity.
2. **Historical DuPont core:** RNOA, after-tax CoD, Spread, FLEV, decomposed ROE, Actual ROE, growth/margins and related historical ratios.
3. **Multi-period historical completion:** extend meaningful historical formulas across all applicable fiscal periods rather than only one sample period.
4. **Historical per-share analysis:** add EPS/per-share formulas only when actual historical diluted-share data is supplied through the standardized input path.

Forecasting and valuation are separate future product phases, not prerequisites for declaring historical v1 complete.

## Non-goals for v1

- Executing automatic company forecasts as part of a normal historical build.
- Forward revenue, margin, balance-sheet, or earnings forecasts.
- Bear/Base/Bull scenario construction.
- Residual-income, DCF, terminal-value, or forward valuation exercises.
- Treating default growth/margin/leverage assumptions as company-specific forecasts.
- Manually copying historical numbers from filings into yellow practice cells.
- Literal-number-entry exercises whose main skill is transcription.
- Balance-sheet classification as a quiz surface unless explicitly reintroduced later.
- Asking the learner to guess setup/judgment inputs.
- Automatically inventing practice questions.
- Requiring decorative Excel formatting reproduction.
- Automatic HKEX ingestion when manual input is sufficient.
- Per-cell/selected-component Check as the normal workflow.
- Check output revealing expected values/formulas.
- Progressive hints or Reveal-answer commands.
- Hiding active answers/hints in Trainer metadata and calling them inaccessible.

## Definition of done for historical v1

Given supported historical Hong Kong company data, the system produces a matched `*_Trainer.xlsx` and `*_Answer_Key.xlsx` pair whose visible product is a coherent historical BAV analysis.

For every selected historical formula-practice component before Check:

- the Trainer cell is blank bright yellow and contains no Note/comment;
- the Trainer and its associated active metadata contain no withheld answer/hint for that component;
- the corresponding Answer Key cell is bright yellow, contains the correct working formula, and carries a concise non-empty legacy Note.

Historical source data and classification/setup judgments remain populated. Deferred forecast/valuation tabs are hidden placeholders and excluded from practice/Check. Normal historical generation does not run the dormant forecast/scenario engine and does not fabricate forecast assumptions. A single Check action validates all active historical practice cells without disclosing answers.

Historical reformulation and ratio analysis are internally coherent and preserve concept-aware line identity. Historical EPS/per-share analysis is included only where required historical share data is supplied; missing share history is not filled with invented forecast assumptions.

A trustworthy forecast/valuation trainer is explicitly deferred until its assumption/judgment architecture is integrated and separately verified.

## Planning ownership

This file records stable product intent. **ChatGPT owns planning changes to TARGET.md. Cursor should treat it as read-only unless ChatGPT explicitly instructs otherwise.** Implementation details belong in `IMPLEMENTATION.md` and the codebase.
