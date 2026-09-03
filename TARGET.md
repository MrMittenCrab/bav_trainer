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
4. Complete any number of blank yellow practice cells in the Trainer workbook.
5. Run **Check** when desired. Check scans **every practice cell in the Trainer in one pass** and recolors it without changing its contents:
   - blank / unentered → remains yellow;
   - correct → green;
   - incorrect → red.
6. When the learner wants the actual answer or a hint, open the matching Answer Key: inspect the real formula/input in the corresponding yellow cell and hover over that same cell's Note for the hint.

The **Answer Key is the sole answer-and-hint mechanism**. Check is validation only. There is no progressive Hint or Reveal Answer workflow.

## Hard requirements

- **Reference-model first.** The system must derive trainer answers from a complete model, not from hand-authored answer keys.
- **Exactly two user-facing workbooks.** One build must produce a clearly named Trainer workbook and its matching Answer Key. Internal build metadata may exist while constructing the pair, but the learner-facing product must not require a third reference workbook.
- **Trainer contains no answers or hints.** Every practice cell starts blank bright yellow with no Note/comment. No adjacent visible hint cells are allowed. Hidden Trainer worksheets and Trainer-associated sidecars must not contain withheld practice formulas, expected answer values, `short_hint` text, detailed hints, or any other answer-bearing copy of the Answer Key.
- **Answer Key contains formula/input + Note.** Every corresponding yellow practice cell in the Answer Key contains the correct working formula or input and a non-empty Excel legacy Note with one concise hint. Formula answers remain inspectable formulas rather than hard-coded displayed results.
- **Answers and hints are co-located.** The formula/input is in the Answer Key practice cell and the hint is the legacy Note attached to that same cell. Do not place hints in adjacent cells or use modern threaded comments as a substitute.
- **Workbook-wide Check.** One Check action scans every semantic practice cell in the Trainer. It does not require the learner to select a component or check cells one at a time.
- **Check colors only.** Check must preserve the learner's cell contents and apply exactly three practice states: blank/unentered stays yellow, correct becomes green, incorrect becomes red. Re-running Check must recompute all states from current cell contents, so corrected answers can turn green and cleared answers return to yellow.
- **Check is non-disclosing.** Check must not insert, print, return, display, or store in the Trainer any expected formula, expected value, hint, or answer explanation. Its user-facing output may report aggregate counts such as correct / incorrect / blank, but not the reference answers.
- **No Hint / Reveal product surface.** Do not expose progressive Hint or Reveal Answer commands, buttons, macros, or workflow instructions. Opening the Answer Key is how the learner gets either the hint or the answer.
- **Visual parity.** At build time the two workbooks must have identical visible sheet structure, cell locations, fonts, borders, alignments, number formats, row heights, and column widths except for the intentionally blank versus completed practice-cell contents and Answer Key Notes. Practice fills initially match yellow; after Check, only Trainer practice-cell fills may differ by becoming green/red/yellow according to validation state.
- **Reference aesthetic.** Match the supplied Oshkosh workbook's restrained financial-model style: Aptos Narrow, 20-point bold worksheet titles, 11-point body text, black text on a white base, bright-yellow practice/answer cells, and thin borders used for headers, sections, and totals. Preserve appropriate financial number formats.
- **Short feedback loop.** The learner can validate the entire workbook with one Check action and can get the answer/hint immediately by opening the Answer Key. Check must not require revealing answers inside the Trainer.
- **Semantic component mapping.** Trainer generation and Check must resolve components by semantic identity rather than depending on fragile hard-coded workbook coordinates. The Trainer itself does not need to retain answer-bearing semantic metadata; Check may read the matching Answer Key/reference metadata externally.
- **Professional workbook preserved.** Training mode should remove only the substantive work the learner is meant to practise; formatting, source data, labels, worksheet setup, and non-practice calculations should already be done.
- **HK input is manual in v1.** Automatic HKEX scraping is not required for the first usable version. Manual filings or Excel/Bloomberg/Wind-style exports can feed a standardized interface.
- **Standardized identity survives round trips.** If ingestion produces standardized JSON, identity-bearing fields such as `LineItem.concept` must survive export/reload rather than being silently discarded.
- **Full BAV logic is the source of truth.** Accounting reformulation, DuPont analysis, forecasting, residual-income valuation, DCF/cross-check logic, and scenario analysis should remain aligned with the underlying BAV model rather than becoming a simplified toy model.

## Non-goals for v1

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

For every semantic practice component before Check:

- the Trainer cell is blank bright yellow and contains no Note/comment;
- the Trainer workbook and its associated files contain no withheld formula, expected answer value, or hint text for that component;
- the corresponding Answer Key cell is bright yellow, contains the correct working formula/input, and carries a non-empty concise legacy Excel Note.

A single Check action then scans all practice cells without changing their contents: blank cells are yellow, correct cells are green, and incorrect cells are red. Re-running Check fully refreshes those states. Check does not disclose reference answers or hints.

The pair shares the same professional Oshkosh-derived visible structure and working BAV logic. No user-facing `*_reference.xlsx` exists. The Answer Key is the only hint/answer surface. Hint and Reveal commands/macros/APIs do not exist in the trainer product. Semantic mapping remains coordinate-free at design time, and supported standardized-data round trips preserve concept-aware line identity.

## Planning ownership

This file records stable product intent. **ChatGPT owns planning changes to TARGET.md. Cursor should treat it as read-only unless ChatGPT explicitly instructs otherwise.** Implementation details belong in `IMPLEMENTATION.md` and the codebase.
