# IMPLEMENTATION.md

## Purpose

This file is the handoff boundary between **ChatGPT (planner/reviewer)** and **Cursor (implementer/test runner)**.

- ChatGPT decides architecture, sequencing, acceptance criteria, and whether a committed step matches the plan.
- Cursor implements only the active step and runs the relevant tests/checks.
- The user reviews the local result and creates/pushes the Git commit.
- ChatGPT verifies the pushed commit by code inspection. ChatGPT does not rerun the tests.

Cursor should treat `TARGET.md` and this file as read-only unless the active step explicitly requires documentation changes.

## Current architecture checkpoint

The trainer now produces the intended matched `*_Trainer.xlsx` / `*_Answer_Key.xlsx` pair from one semantic reference model. The Trainer blanks resolved practice cells and keeps them bright yellow; the Answer Key keeps formulas and adds legacy Notes. The semantic component system remains coordinate-free at catalog level through `COMPONENT_CATALOG`, `SemanticMap`, and `ResolvedComponent`.

The previous paired-workbook step is structurally implemented, but code review found that the **underlying reference-model formulas are not yet reliable enough to serve as an answer key**. The next step therefore fixes model integrity before expanding the exercise catalog or adding new UX.

### Review findings that define the next step

1. `cmd_build()` reads `--assumptions` but does not pass the parsed assumptions into `build_training_workbook()`, so CLI-supplied assumptions are silently ignored.
2. Several workbook formulas disagree with the Python-side expected-value logic used by the semantic map:
   - latest-FY NOPAT in the workbook currently collapses to Net Income instead of adding after-tax net interest;
   - the DuPont after-tax cost-of-debt formula uses NOPAT divided by Net Debt, which is not the metric computed by `financial_math.py`;
   - the model labels a historical value as after-tax cost of debt and then taxes it again in the forecast model / scenario engine.
3. Condensed balance-sheet `SUMIF` formulas use the classification rows on `Condensed Financials` but sum same-numbered rows on `Balance Sheet`. Those row numbers are not a stable semantic mapping and can become wrong whenever skipped/total rows differ.
4. DuPont formulas hard-code `Balance Sheet` row `7` as equity in FLEV / Actual ROE instead of resolving the actual equity line semantically.
5. The forecast model only populates the first forecast year, while terminal-value formulas reference year-10 abnormal earnings and discount-factor cells that are blank. This means an Answer Key can contain syntactically valid formulas whose dependency chain is incomplete.
6. Current trainer tests mostly prove file naming, styling, Notes, formula presence, and semantic-map resolution. They do not prove that the formulas in those answer cells are financially coherent or that their referenced cells are populated.
7. `check_component()` can treat an exact formula-string match as the expected value when Excel has no cached result. That fallback is useful for learner checking, but it can also mask a mathematically wrong reference formula during automated tests.

This document does **not** claim that the product is complete. It records the next bounded implementation step only.

## Active implementation step

### Step 2 — Make the existing semantic Answer Key mathematically trustworthy

**Goal**

Repair the reference workbook and shared financial-model logic so the **existing 13 semantic components** produce coherent Excel formulas whose dependencies are populated and whose definitions agree with the Python-side expected values.

Do not expand the component catalog in this step. The purpose is to make the current Answer Key trustworthy before adding more exercises.

**Required changes**

1. **Pass CLI assumptions through correctly.**
   - In `core/__main__.py`, pass the parsed `assumptions` object into `build_training_workbook(data, out, assumptions)`.
   - Add a focused test using a non-default assumption value that visibly changes a generated model input / formula result path, so the test proves the CLI argument is not ignored.

2. **Fix the condensed accounting chain so workbook formulas match the BAV definitions used by Python.**
   - Build explicit historical rows for Net Interest and Net Interest After Tax (or an equivalent semantically clear structure) rather than making NOPAT equal Net Income.
   - Define NOPAT consistently as Net Income plus after-tax net interest using the same sign convention as `compute_anchor()`.
   - Ensure the latest-FY semantic `nopat_fy` formula points to this correct workbook calculation and its expected value still comes from the same financial definition.
   - Do not hard-code an expected numeric answer into the workbook.

3. **Remove positional coupling between the condensed classification table and raw Balance Sheet rows.**
   - Do not use a classification range from one sheet with a same-row-number sum range from another sheet unless a verified one-to-one row mapping exists.
   - Prefer one of these coherent designs:
     - keep each balance-sheet label, classification, and period values together in the condensed classification table and `SUMIF` within that table; or
     - store explicit source-row metadata and build formulas from those resolved source rows.
   - NOWC, NOA, and Net Debt formulas must derive from the classifications actually shown to the user and remain correct if source statement row positions change.
   - Preserve semantic component registration; do not introduce fixed catalog coordinates.

4. **Fix DuPont definitions and remove hard-coded equity row assumptions.**
   - After-tax CoD must use after-tax net interest divided by average Net Debt, matching the definition in `compute_anchor()`.
   - RNOA must remain NOPAT divided by average NOA.
   - Spread must remain RNOA minus after-tax CoD.
   - FLEV must use average Net Debt divided by average Equity.
   - Actual ROE must use Net Income divided by average Equity.
   - Resolve the equity line from standardized/semantic data rather than assuming `Balance Sheet!row 7`.
   - The semantic expected values for `rnoa`, `spread`, and `roe_decomp` must agree with the workbook definitions.

5. **Use one unambiguous cost-of-debt convention across `financial_math.py`, `ri_engine.py`, and the workbook.**
   - Decide whether the stored historical series is pre-tax or after-tax and name it accordingly.
   - Apply tax exactly once.
   - Update variable/field names where necessary to remove the current ambiguity.
   - Keep the economic definition consistent between Python expected values and Excel formulas.
   - Do not silently change unrelated scenario assumptions.

6. **Build a complete ten-year forecast dependency chain before computing terminal value.**
   - Populate Sales, NOPAT Margin, NOPAT, Net Debt / Equity (or the existing equivalent operating-financing bridge), Net Income, Abnormal Earnings, discount factors, and PV of Abnormal Earnings for all forecast years required by the residual-income model.
   - Year-10 terminal value must reference populated year-10 abnormal earnings.
   - PV Terminal Value must discount using a populated year-10 discount factor (or an equivalent explicit formula), not an empty cell.
   - Intrinsic Value and IVPS must therefore trace through populated workbook cells from forecast assumptions to final value.
   - Keep Bear / Base / Bull model construction aligned; only Base semantic components need to remain registered in this step unless already registered elsewhere.

7. **Keep the workbook formula chain aligned with `ri_engine.run_scenario()`.**
   - The same anchor revenue, growth vectors, margin vectors, tax treatment, leverage logic, cost of equity, terminal growth, and share count must produce the same conceptual result in both implementations.
   - If the existing Python engine contains the same discovered bug (for example double-taxing a value already defined as after-tax CoD), fix the shared definition rather than forcing Excel to copy the bug.
   - Do not add a second independent valuation methodology.

8. **Add formula-integrity tests that can fail even when formula strings exist.**
   Add focused tests under `core/tests/` that verify at minimum:
   - CLI assumptions are propagated into the generated model;
   - NOPAT formula uses Net Income plus after-tax net interest and is not merely `=Net Income`;
   - condensed NOWC / NOA / Net Debt do not depend on accidental cross-sheet row-number alignment;
   - DuPont CoD does not use NOPAT as its numerator;
   - FLEV / Actual ROE do not hard-code `Balance Sheet!7` as equity;
   - every required forecast-year cell in the ten-year Base forecast chain is populated;
   - terminal value and PV terminal value reference populated year-10 cells;
   - the 13 registered semantic component formulas have no direct references to required-but-blank cells in their model dependency chain;
   - semantic expected values remain non-null and use the corrected shared financial definitions.

9. **Do not let `check_component()` mask reference-model defects in the new integrity tests.**
   - Existing learner-facing fallback behavior may remain if useful.
   - New reference-model tests must inspect the generated workbook / semantic formulas directly rather than relying only on `check_component()` returning `passed=True`.

10. **Preserve the paired-workbook behavior from Step 1.**
    - Trainer practice cells remain blank bright yellow with no Notes.
    - Answer Key practice cells remain bright yellow with formulas and legacy Notes.
    - Trainer / Answer Key visible structure and styling remain matched.
    - No third user-facing reference workbook returns.

**Files expected to change**

- `core/__main__.py`
- `core/engine/reference_model.py`
- `core/model/financial_math.py` if needed to make the cost-of-debt definition explicit and consistent
- `core/model/ri_engine.py` if needed to remove double taxation / align the forecast math
- `core/tests/test_trainer.py` and/or a new focused reference-model test module

Only change other files if a concrete dependency requires it.

**Do not change**

- `TARGET.md`.
- The paired Trainer / Answer Key product contract.
- `COMPONENT_CATALOG` membership, ordering, or coordinate-free architecture.
- HK manual-ingestion interfaces except where a semantic source-row lookup helper is strictly required.
- The learner-facing Hint/Reveal UX in this step; the adjacent-cell `hint` behavior can be handled separately after reference-model integrity is established.
- Workbook aesthetics except where newly added model rows/columns need the existing shared style.
- Git history. Do not commit, push, reset, rebase, or merge.

**Acceptance criteria**

- `python -m core build ... --assumptions <file>` produces a workbook that actually reflects the supplied assumptions.
- Latest-FY workbook NOPAT uses the same definition and sign convention as Python `compute_anchor()`.
- NOWC, NOA, and Net Debt no longer rely on matching row numbers between unrelated sheet layouts.
- DuPont after-tax CoD, Spread, FLEV, ROE decomposition, and Actual ROE use financially correct numerators/denominators and semantically resolved source rows.
- No cost-of-debt quantity is taxed twice.
- All ten forecast years needed by the residual-income model are populated in each scenario model before terminal value is calculated.
- Terminal value and PV terminal value do not reference blank forecast cells.
- The existing 13 semantic Answer Key cells contain formulas that are internally coherent with their dependency chain and corresponding Python expected-value definitions.
- The matched Trainer / Answer Key generation and styling tests from Step 1 still pass.
- No new coordinate registry or catalog-level hard-coded workbook cell mapping is introduced.

**Testing**

Use a red/green workflow for each discovered defect. Run the smallest relevant test first after each change, then the full current core test suite.

At minimum run and report:

```bash
python -m pytest core/tests/test_trainer.py -v --tb=short
python -m pytest core/tests/ -q --tb=line
```

If a new dedicated reference-model test module is added, run it explicitly before the full suite.

Do not weaken existing tests to make them pass. Do not report formula correctness merely because openpyxl can reopen the file or because the formula string begins with `=`.

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
- Are the reference formulas financially coherent, not merely syntactically present?
- Do workbook formulas and Python expected-value definitions agree?
- Are required forecast dependencies populated before terminal value / IVPS use them?
- Are important cases or requirements missing?
- Did Cursor change unrelated behavior or architecture?
- Do the new/changed tests appear capable of catching the defects identified above?

ChatGPT should not rerun the test suite. Cursor owns test execution; ChatGPT owns independent inspection of the committed implementation.

A verified step may then be marked complete and replaced with the next ChatGPT-authored step.
