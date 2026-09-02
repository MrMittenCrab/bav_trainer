# IMPLEMENTATION.md

## Purpose

This file is the handoff boundary between **ChatGPT (planner/reviewer)** and **Cursor (implementer/test runner)**.

- ChatGPT decides architecture, sequencing, acceptance criteria, and whether a committed step matches the plan.
- Cursor implements only the active step and runs the relevant tests/checks.
- The user reviews the local result and creates/pushes the Git commit.
- ChatGPT verifies the pushed commit by code inspection. ChatGPT does not rerun the tests.

Cursor should treat `TARGET.md` and this file as read-only unless the active step explicitly requires documentation changes.

## Current architecture checkpoint

The trainer has already moved from a coordinate-based component registry toward a semantic component system. Current runtime code uses `COMPONENT_CATALOG`, `SemanticMap` / `ResolvedComponent`, embedded component maps, and shared financial-model logic rather than the former `TRAINER_COMPONENTS` coordinate registry.

This document does **not** claim that the product is complete. It records the workflow and the next bounded implementation step only.

## Active implementation step

### Step 1 — Generate a matched Trainer and Answer Key workbook pair

**Goal**

Change one HK-company build so it produces two user-facing Excel files from the same semantic reference model:

- `*_Trainer.xlsx`: all semantic practice cells blank and bright yellow; and
- `*_Answer_Key.xlsx`: the same cells bright yellow, populated with the correct Excel formulas or inputs, and carrying concise hints in Excel legacy Notes.

The two files must otherwise be visually and structurally identical and must follow the supplied Oshkosh workbook's financial-model aesthetic.

**Required changes**

1. Update the build orchestration and CLI so an output named `<Company>_Trainer.xlsx` also produces `<Company>_Answer_Key.xlsx`. If the supplied trainer output stem does not end in `_Trainer`, append `_Trainer` for the trainer file and `_Answer_Key` for the answer file. Report both paths on successful completion.
2. Build the complete model directly as the Answer Key (or promote the completed internal reference model to that name), then derive the Trainer from it. Do not require a third user-facing `*_reference.xlsx` file.
3. Continue using `SemanticMap` / `ResolvedComponent` as the sole authority for which cells are practice cells and what formula, input, and hint belongs to each cell. Do not introduce a coordinate registry.
4. In the Trainer workbook, for every resolved practice component:
   - remove the answer formula or input;
   - apply solid bright-yellow fill `#FFFF00`;
   - preserve the cell's font, border, alignment, protection, and number format; and
   - do not add a Note, threaded comment, adjacent hint cell, or visible answer.
5. In the Answer Key workbook, for every resolved practice component:
   - retain the working Excel formula or correct input rather than replacing it with a displayed value;
   - apply the same solid bright-yellow fill `#FFFF00`; and
   - attach a non-empty legacy Excel Note using the component's concise `short_hint`, with the first detailed hint as fallback when `short_hint` is empty. Use a stable author such as `BAV Trainer`.
6. Remove the present blue practice-cell fill and visible adjacent hint-cell behavior from generated workbooks. Existing optional Check, Hint, and Reveal commands may remain, but their operation must not be required to access the static Answer Key and must not reintroduce visible hint columns during initial generation.
7. Apply one shared Oshkosh-derived style profile to both outputs:
   - Aptos Narrow throughout generated visible sheets;
   - 20-point bold worksheet titles;
   - 11-point body text;
   - black text on a white base;
   - bright yellow only for learner-input/answer areas; and
   - restrained thin borders for headers, section boundaries, and totals, while preserving appropriate currency, percentage, multiple, and date formats.
8. Ensure both output files have the same visible worksheet names/order, freeze panes, gridline setting, merged ranges, widths, heights, and practice-cell styling. Hidden semantic metadata may be retained in both files when needed by Check/Hint/Reveal.
9. Update `README-HK-TRAINER.md` and CLI help/output examples only as needed to describe the paired files accurately. Do not broaden the documentation rewrite beyond this behavior.

**Do not change**

- HK manual-ingestion behavior or standardized financial-data interfaces.
- BAV accounting reformulation, DuPont, forecast, residual-income, DCF, cross-check, or scenario mathematics.
- The semantic component catalog's coordinate-free design.
- Component dependency ordering or the meaning of existing hints.
- Unrelated workbook layout, architecture, refactors, or features.
- Git history. Do not commit, push, reset, rebase, or merge.

**Acceptance criteria**

- A demo build creates both `DEMO_HK_Trainer.xlsx` and `DEMO_HK_Answer_Key.xlsx`, and no separate reference workbook is needed by the user.
- For every resolved component, the Trainer cell is blank, has solid fill `#FFFF00`, and has no Note/comment.
- For every resolved component, the Answer Key cell contains the expected working formula or input, has the same solid fill `#FFFF00`, and has a non-empty legacy Note with the expected hint text.
- No generated visible sheet contains the former adjacent hint-cell text added by `_strip_practice_formulas`.
- Corresponding practice cells have identical font, border, alignment, protection, and number format in both files.
- Visible worksheet names/order, merged ranges, column widths, row heights, and sheet display settings match between the pair.
- Generated visible sheets use Aptos Narrow, with 20-point bold titles and 11-point body text where those roles apply.
- Existing semantic-map loading still resolves all catalog components from both workbooks.
- Retained Check, Hint, and Reveal commands either continue to work with the new Answer Key path or are adjusted so their existing tests remain valid without creating a third reference workbook.
- Both files open successfully in Excel-compatible readers without repair warnings.

**Testing**

Update or add focused tests under `core/tests/` for:

1. paired output naming and existence;
2. Trainer blank/yellow/no-Note behavior for every semantic component;
3. Answer Key formula-or-input/yellow/legacy-Note behavior for every semantic component;
4. corresponding-cell style parity and visible sheet-structure parity;
5. Oshkosh-derived font/title/body conventions; and
6. retained semantic-map and optional Check/Hint/Reveal compatibility.

Run the smallest relevant trainer test module first, then the repository's existing relevant test suite. Do not weaken tests to make them pass. Report the exact commands and results.

**Git boundary**

Do not commit, push, reset, rebase, merge, or otherwise change Git history.

## Cursor execution rules

1. Read the active step before editing.
2. Inspect the existing implementation first.
3. Treat the stated requirements and acceptance criteria as authoritative.
4. Make the smallest coherent change that satisfies the step.
5. Preserve existing architecture and conventions unless the step explicitly changes them.
6. Do not add unrelated cleanup, refactors, abstractions, or features.
7. If the instruction conflicts with the repository, report the conflict instead of silently redesigning the solution.
8. Run the relevant tests/checks after implementation.
9. Fix failures caused by the change.
10. At completion report:
   - files changed;
   - what was implemented;
   - tests/checks run and results;
   - anything not tested or unresolved.
11. Do not propose the next product step.

## ChatGPT verification protocol

After the user pushes the commit, ChatGPT should inspect the latest GitHub commit and compare it with the active step in this file.

Verification asks:

- Does the code actually implement every acceptance criterion?
- Are important cases or requirements missing?
- Did Cursor change unrelated behavior or architecture?
- Do the new/changed tests appear to exercise the intended behavior?
- Is the implementation internally coherent with the surrounding code?

ChatGPT should not rerun the test suite. Cursor owns test execution; ChatGPT owns independent inspection of the committed implementation.

A verified step may then be marked complete and replaced with the next ChatGPT-authored step.
