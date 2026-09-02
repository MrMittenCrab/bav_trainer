# TARGET.md

## Product target

Build **BAV Excel Trainer — Hong Kong Edition**: a training system that takes manually supplied Hong Kong company financial materials, builds the full BAV model, and produces two matching professional Excel workbooks:

1. a **Trainer** workbook in which every substantive cell the learner must complete is blank and highlighted yellow; and
2. an **Answer Key** workbook in which the same yellow cells contain the correct Excel formulas or inputs and each answer cell has a concise hint in an Excel legacy Note (the yellow sticky note shown on hover).

The trainer is for learning the actual BAV modelling workflow, not for generating artificial exercises.

## Learner experience

1. Supply company financial data/documents manually.
2. Build a complete reference BAV model from those inputs.
3. Generate a matched pair of user-facing workbooks from that one model.
4. Complete the blank yellow cells in the Trainer workbook in dependency order.
5. Open the matching Answer Key whenever feedback is needed; inspect the real Excel formula or input and hover over its Note for a concise hint.
6. Optionally use existing Check, Hint, or Reveal tooling, but do not require macros or command-line actions to use the two-workbook learning flow.

## Hard requirements

- **Reference-model first.** The system must derive trainer answers from a complete model, not from hand-authored answer keys.
- **Exactly two user-facing workbooks.** One build must produce a clearly named Trainer workbook and its matching Answer Key. Internal metadata or non-Excel sidecars may remain implementation details, but a third reference workbook must not be required from the user.
- **Yellow means learner work.** In the Trainer workbook, every substantive formula or input intentionally withheld for practice must be blank and use the same bright-yellow fill. Source data, labels, and non-practice formulas must remain populated.
- **Answers and hints are co-located.** In the Answer Key, every corresponding yellow cell must contain the correct formula or input and a non-empty Excel legacy Note with a concise hint. Do not place hints in adjacent cells or use modern threaded comments as a substitute.
- **Answers remain separate.** The Trainer workbook must not embed visible answers or hints. The learner chooses when to open the separate Answer Key.
- **Real Excel logic.** Formula answers must remain working, inspectable Excel formulas rather than hard-coded displayed results.
- **Visual parity.** The two workbooks must have identical visible sheet structure, cell locations, fonts, fills, borders, alignments, number formats, row heights, and column widths except for the intentionally blank versus completed practice-cell contents and Answer Key Notes.
- **Reference aesthetic.** Match the supplied Oshkosh workbook's restrained financial-model style: Aptos Narrow, 20-point bold worksheet titles, 11-point body text, black text on a white base, bright-yellow practice/answer cells, and thin borders used for headers, sections, and totals. Preserve appropriate financial number formats.
- **Short feedback loop.** The Answer Key and its cell Notes must be usable immediately without macros or command-line actions. Existing Check, Hint, and Reveal tooling may remain as optional aids.
- **Semantic component mapping.** Trainer logic must resolve components by semantic identity at build time rather than depending on fragile hard-coded workbook coordinates.
- **Professional workbook preserved.** Training mode should remove only the substantive work the learner is meant to practise; formatting, source data, labels, worksheet setup, and non-practice calculations should already be done.
- **HK input is manual in v1.** Automatic HKEX scraping is not required for the first usable version. Manual filings or Excel/Bloomberg/Wind-style exports can feed a standardized interface.
- **Full BAV logic is the source of truth.** Accounting reformulation, DuPont analysis, forecasting, residual-income valuation, DCF/cross-check logic, and scenario analysis should remain aligned with the underlying BAV model rather than becoming a simplified toy model.

## Non-goals for v1

- Automatically inventing practice questions or exercises.
- Requiring the learner to reproduce decorative Excel formatting.
- Automatic HKEX ingestion when manual document input is sufficient.
- Requiring macros or CLI commands to see the answer or its hint.
- Showing hints in separate visible columns or cells.
- Giving the implementation agent freedom to redesign the product while implementing a bounded step.

## Definition of done

A real Hong Kong company can be supplied through the supported manual input path and the system produces a matched `*_Trainer.xlsx` and `*_Answer_Key.xlsx` pair. Every semantic practice cell is blank yellow in the Trainer and completed yellow with a concise Excel Note in the Answer Key. Both files share the same professional Oshkosh-derived aesthetic and working BAV logic, and neither depends on fixed cell coordinates or corrupts the workbook. Optional Check, Hint, and Reveal tooling continues to work if retained.

## Planning ownership

This file records stable product intent. **ChatGPT owns planning changes to TARGET.md. Cursor should treat it as read-only unless ChatGPT explicitly instructs otherwise.** Implementation details belong in `IMPLEMENTATION.md` and the codebase.
