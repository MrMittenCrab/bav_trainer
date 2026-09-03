# TARGET.md

## Product target

Build **BAV Excel Trainer — Hong Kong Edition**: a training system that takes manually supplied Hong Kong company financial materials, builds the full BAV model, and produces two matching professional Excel workbooks:

1. a **Trainer** workbook in which the learner reconstructs the model's important Excel formulas, links, ratios, bridges, and valuation calculations in blank bright-yellow practice cells; and
2. an **Answer Key** workbook in which those same yellow cells contain the correct working Excel formulas and each answer cell has one concise hint in an Excel legacy Note (the yellow sticky note shown on hover).

The trainer is for learning **financial-model construction and dependency logic**, not for transcription of numbers from filings and not for artificial quiz questions.

## Learner experience

1. Supply company financial data/documents manually.
2. Build a complete reference BAV model from those inputs.
3. Generate a matched `*_Trainer.xlsx` / `*_Answer_Key.xlsx` pair from that one model.
4. In the Trainer, source financial data, classifications, market data, and scenario assumptions are already populated. The learner fills only the yellow **model-construction formula cells**.
5. Run **Check** when desired. Check scans **every practice cell in the Trainer in one pass** and recolors it without changing its contents:
   - blank / unentered → remains yellow;
   - correct → green;
   - incorrect → red.
6. When the learner wants the actual formula or a hint, open the matching Answer Key: inspect the real formula in the corresponding yellow cell and hover over that same cell's Note for the hint.

The **Answer Key is the sole answer-and-hint mechanism**. Check is validation only. There is no progressive Hint or Reveal Answer workflow.

## What counts as practice

A practice cell should teach how the model is constructed from already-supplied information. High-value practice includes:

- cross-sheet formula links that connect source statements to model schedules;
- accounting reformulation formulas and operating/financing aggregates;
- growth, margin, return, leverage, spread, and other analytical ratios;
- forecast formulas that transform assumptions into projected financials;
- residual-income, DCF/cross-check, terminal-value, and per-share valuation formulas;
- scenario weighting, valuation multiples, and reconciliation/check formulas when they teach model logic.

The practice surface should follow the model's dependency graph: upstream construction cells should appear before downstream ratios and valuation outputs.

## What stays populated

The Trainer should not make the learner manually re-enter literal data that the system already knows. Unless a later product decision explicitly changes this, keep these populated in both workbooks:

- historical source-statement numbers transcribed or imported from filings;
- market-data inputs such as price, shares, rates, and other supplied external facts;
- scenario assumptions such as growth, margins, probabilities, beta, terminal growth, and similar hard-coded drivers;
- balance-sheet classification choices and other setup/judgment inputs used by the reference model;
- labels, dates, units, formatting, and workbook setup;
- non-practice formulas that are intentionally outside the current training surface.

A literal number or category should not become a practice cell merely because it is editable. The default test is: **does reconstructing this cell teach model logic or only data entry?**

## Hard requirements

- **Reference-model first.** The system must derive trainer formulas from a complete working model, not from hand-authored answer keys.
- **Formula-construction focus.** The v1 practice surface consists of formula-bearing model construction cells. Do not add literal-number transcription or classification quizzes merely to increase exercise count.
- **Exactly two user-facing workbooks.** One build must produce a clearly named Trainer workbook and its matching Answer Key. Internal build metadata may exist while constructing the pair, but the learner-facing product must not require a third reference workbook.
- **Trainer contains no answers or hints.** Every practice cell starts blank bright yellow with no Note/comment. No adjacent visible hint cells are allowed. Hidden Trainer worksheets and Trainer-associated sidecars must not contain withheld practice formulas, expected answer values, `short_hint` text, detailed hints, or any other answer-bearing copy of the Answer Key.
- **Answer Key contains formula + Note.** Every corresponding yellow practice cell in the Answer Key contains the correct working formula and a non-empty Excel legacy Note with one concise hint. Formula answers remain inspectable formulas rather than hard-coded displayed results.
- **Answers and hints are co-located.** The formula is in the Answer Key practice cell and the hint is the legacy Note attached to that same cell. Do not place hints in adjacent cells or use modern threaded comments as a substitute.
- **Workbook-wide Check.** One Check action scans every semantic practice cell in the Trainer. It does not require the learner to select a component or check cells one at a time.
- **Check colors only.** Check must preserve the learner's cell contents and apply exactly three practice states: blank/unentered stays yellow, correct becomes green, incorrect becomes red. Re-running Check must recompute all states from current cell contents, so corrected answers can turn green and cleared answers return to yellow.
- **Check is non-disclosing.** Check must not insert, print, return, display, or store in the Trainer any expected formula, expected value, hint, or answer explanation. Its user-facing output may report aggregate counts such as correct / incorrect / blank, but not reference answers.
- **No Hint / Reveal product surface.** Do not expose progressive Hint or Reveal Answer commands, buttons, macros, or workflow instructions. Opening the Answer Key is how the learner gets either the hint or the answer.
- **Visual parity.** At build time the two workbooks must have identical visible sheet structure, cell locations, fonts, borders, alignments, number formats, row heights, and column widths except for the intentionally blank versus completed practice-cell contents and Answer Key Notes. Practice fills initially match yellow; after Check, only Trainer practice-cell fills may differ by becoming green/red/yellow according to validation state.
- **Reference aesthetic.** Match the supplied Oshkosh workbook's restrained financial-model style: Aptos Narrow, 20-point bold worksheet titles, 11-point body text, black text on a white base, bright-yellow practice/answer cells, and thin borders used for headers, sections, and totals. Preserve appropriate financial number formats.
- **Short feedback loop.** The learner can validate the entire workbook with one Check action and can get the formula/hint immediately by opening the Answer Key. Check must not require revealing answers inside the Trainer.
- **Semantic component mapping.** Trainer generation and Check must resolve practice formulas by semantic identity rather than depending on fragile hard-coded workbook coordinates. The Trainer itself does not retain answer-bearing semantic metadata; Check reads the matching Answer Key/reference metadata externally.
- **Professional workbook preserved.** Training mode removes only the formula cells selected for practice; source data, classifications, assumptions, labels, worksheet setup, formatting, and non-practice calculations remain populated.
- **HK input is manual in v1.** Automatic HKEX scraping is not required for the first usable version. Manual filings or Excel/Bloomberg/Wind-style exports can feed a standardized interface.
- **Standardized identity survives round trips.** If ingestion produces standardized JSON, identity-bearing fields such as `LineItem.concept` must survive export/reload rather than being silently discarded.
- **Full BAV logic is the source of truth.** Accounting reformulation, DuPont analysis, forecasting, residual-income valuation, DCF/cross-check logic, and scenario analysis should remain aligned with the underlying BAV model rather than becoming a simplified toy model.

## Practice-surface expansion strategy

Expand the trainer by coherent dependency chains rather than by maximizing cell count.

1. **Historical reformulation + DuPont:** source data and classifications supplied; learner constructs operating/financing aggregates, NOPAT, NOA/net debt/equity, RNOA, cost of debt, spread, leverage, ROE decomposition, and related ratios.
2. **Forecast construction:** assumptions supplied; learner constructs forecast sales, margins, operating assets, financing, NOPAT/net income, and related forecast schedules.
3. **Valuation construction:** learner constructs residual income, discounting, terminal value, intrinsic value, per-share value, scenario weighting, multiples/cross-checks, and reconciliations.

Do not move to the next chain until the preceding chain is coherent and verified.

## Non-goals for v1

- Manually copying historical numbers from filings into yellow practice cells.
- Literal-number-entry exercises whose main skill is transcription.
- Balance-sheet classification as a quiz surface unless explicitly reintroduced later.
- Asking the learner to guess supplied scenario assumptions or market inputs.
- Automatically inventing practice questions or exercises.
- Requiring the learner to reproduce decorative Excel formatting.
- Automatic HKEX ingestion when manual document input is sufficient.
- Per-cell or selected-component Check as the normal workflow.
- Check output that reveals the expected value/formula.
- Progressive hint levels inside the Trainer.
- Reveal-answer buttons or commands that write the solution into the Trainer.
- Hiding answers or hints in Trainer metadata and calling them inaccessible.
- Giving the implementation agent freedom to redesign the product while implementing a bounded step.

## Definition of done

A real Hong Kong company can be supplied through the supported manual input path and the system produces a matched `*_Trainer.xlsx` and `*_Answer_Key.xlsx` pair from one complete BAV model.

For every selected formula-practice component before Check:

- the Trainer cell is blank bright yellow and contains no Note/comment;
- the Trainer workbook and its associated files contain no withheld formula, expected answer value, or hint text for that component;
- the corresponding Answer Key cell is bright yellow, contains the correct working formula, and carries a non-empty concise legacy Excel Note.

All source data, classifications, market data, scenario assumptions, and other non-practice inputs remain populated in the Trainer. A single Check action scans all practice cells without changing their contents: blank cells are yellow, correct cells are green, and incorrect cells are red. Re-running Check fully refreshes those states. Check does not disclose reference answers or hints.

The pair shares the same professional Oshkosh-derived visible structure and working BAV logic. No user-facing `*_reference.xlsx` exists. The Answer Key is the only hint/answer surface. Hint and Reveal commands/macros/APIs do not exist in the trainer product. Semantic mapping remains coordinate-free at design time, and supported standardized-data round trips preserve concept-aware line identity.

## Planning ownership

This file records stable product intent. **ChatGPT owns planning changes to TARGET.md. Cursor should treat it as read-only unless ChatGPT explicitly instructs otherwise.** Implementation details belong in `IMPLEMENTATION.md` and the codebase.
