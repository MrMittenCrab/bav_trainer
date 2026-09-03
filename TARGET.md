# TARGET.md

## Product target

Build **BAV Excel Trainer — Hong Kong Edition**: a training system that takes manually supplied Hong Kong company financial materials, builds the full BAV model, and produces two matching professional Excel workbooks:

1. a **Trainer** workbook in which every substantive cell the learner must complete is blank and highlighted bright yellow; and
2. an **Answer Key** workbook in which the same yellow cells contain the correct Excel formulas or inputs and each answer cell has one concise hint in an Excel legacy Note (the yellow sticky note shown on hover).

The trainer is for learning the actual BAV modelling workflow, not for generating artificial exercises.

## Learner experience

1. Supply company financial data/documents manually.
2. Build a complete reference BAV model from those inputs.
3. Generate a matched `*_Trainer.xlsx` / `*_Answer_Key.xlsx` pair from that one model.
4. Complete the blank yellow cells in the Trainer workbook in dependency order.
5. When feedback is needed, open the matching Answer Key: inspect the real formula/input in the corresponding yellow cell and hover over that same cell's Note for the hint.
6. Optionally use **Check** for binary validation of a Trainer entry. Check must not reveal the answer, expected value, or hint and must not modify the practice cell.

The **Answer Key is the sole answer-and-hint mechanism**. There is no progressive Hint or Reveal Answer workflow in the target product.

## Hard requirements

- **Reference-model first.** The system must derive trainer answers from a complete model, not from hand-authored answer keys.
- **Exactly two user-facing workbooks.** One build must produce a clearly named Trainer workbook and its matching Answer Key. Internal metadata or non-Excel sidecars may remain implementation details, but a third reference workbook must not be required from the user.
- **Trainer contains no answers or hints.** Every practice cell in the Trainer is blank bright yellow with no Note/comment. No adjacent visible hint cells are allowed. Hidden Trainer worksheets and Trainer-associated sidecars must not contain withheld practice formulas, expected answer values, `short_hint` text, detailed hints, or any other answer-bearing copy of the Answer Key. Locator/status metadata may remain if it contains no answer or hint content.
- **Answer Key contains formula/input + Note.** Every corresponding yellow practice cell in the Answer Key contains the correct working formula or input and a non-empty Excel legacy Note with one concise hint. Formula answers remain inspectable formulas rather than hard-coded displayed results.
- **Answers and hints are co-located.** The formula/input is in the Answer Key practice cell and the hint is the legacy Note attached to that same cell. Do not place hints in adjacent cells or use modern threaded comments as a substitute.
- **No Hint / Reveal product surface.** Do not expose progressive Hint or Reveal Answer commands, buttons, macros, or normal workflow instructions. Opening the Answer Key is how the learner asks for either the hint or the answer.
- **Check is optional and non-disclosing.** If retained, Check may use the matching Answer Key or reference model internally, but its user-facing result is limited to validation such as correct/incorrect and non-answer dependency warnings. It must not return or print the expected formula, expected value, or hint, and must not insert the answer into the Trainer.
- **Visual parity.** The two workbooks must have identical visible sheet structure, cell locations, fonts, fills, borders, alignments, number formats, row heights, and column widths except for the intentionally blank versus completed practice-cell contents and Answer Key Notes.
- **Reference aesthetic.** Match the supplied Oshkosh workbook's restrained financial-model style: Aptos Narrow, 20-point bold worksheet titles, 11-point body text, black text on a white base, bright-yellow practice/answer cells, and thin borders used for headers, sections, and totals. Preserve appropriate financial number formats.
- **Short feedback loop.** The learner can always get the answer and hint immediately by opening the Answer Key; no macro, terminal action, or hidden reveal state is required.
- **Semantic component mapping.** Trainer logic must resolve components by semantic identity at build time rather than depending on fragile hard-coded workbook coordinates. Any semantic metadata stored with the Trainer must be locator-only and non-answer-bearing.
- **Professional workbook preserved.** Training mode should remove only the substantive work the learner is meant to practise; formatting, source data, labels, worksheet setup, and non-practice calculations should already be done.
- **HK input is manual in v1.** Automatic HKEX scraping is not required for the first usable version. Manual filings or Excel/Bloomberg/Wind-style exports can feed a standardized interface.
- **Standardized identity survives round trips.** If ingestion produces standardized JSON, identity-bearing fields such as `LineItem.concept` must survive export/reload rather than being silently discarded.
- **Full BAV logic is the source of truth.** Accounting reformulation, DuPont analysis, forecasting, residual-income valuation, DCF/cross-check logic, and scenario analysis should remain aligned with the underlying BAV model rather than becoming a simplified toy model.

## Non-goals for v1

- Automatically inventing practice questions or exercises.
- Requiring the learner to reproduce decorative Excel formatting.
- Automatic HKEX ingestion when manual document input is sufficient.
- Requiring macros or CLI commands to see the answer or its hint.
- Progressive hint levels inside the Trainer.
- Reveal-answer buttons or commands that write the solution into the Trainer.
- Hiding answers or hints in Trainer metadata and calling them inaccessible.
- Giving the implementation agent freedom to redesign the product while implementing a bounded step.

## Definition of done

A real Hong Kong company can be supplied through the supported manual input path and the system produces a matched `*_Trainer.xlsx` and `*_Answer_Key.xlsx` pair from one complete BAV model.

For every semantic practice component:

- the Trainer cell is blank bright yellow and contains no Note/comment;
- the Trainer workbook and its associated metadata contain no withheld formula, expected answer value, or hint text for that component;
- the corresponding Answer Key cell is bright yellow, contains the correct working formula/input, and carries a non-empty concise legacy Excel Note.

The pair shares the same professional Oshkosh-derived visible structure and working BAV logic. No user-facing `*_reference.xlsx` exists. The Answer Key is the only hint/answer surface. Optional Check, if retained, is binary/non-disclosing. Semantic mapping remains coordinate-free at design time, and supported standardized-data round trips preserve concept-aware line identity.

## Planning ownership

This file records stable product intent. **ChatGPT owns planning changes to TARGET.md. Cursor should treat it as read-only unless ChatGPT explicitly instructs otherwise.** Implementation details belong in `IMPLEMENTATION.md` and the codebase.
