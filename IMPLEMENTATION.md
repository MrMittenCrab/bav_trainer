# IMPLEMENTATION.md

## Purpose

This file is the handoff boundary between **ChatGPT (planner/reviewer)** and **Cursor (implementer/test runner)**.

- ChatGPT decides architecture, sequencing, acceptance criteria, and whether a committed step matches the plan.
- Cursor implements only the active step and runs the relevant tests/checks.
- The user reviews the local result and creates/pushes the Git commit.
- ChatGPT verifies the pushed commit by code inspection. ChatGPT does not rerun the tests.
- Cursor must update `RESULT.md` before handoff so the exact test commands/results are visible in the committed checkpoint.

Cursor should treat `TARGET.md` and this file as read-only unless the active step explicitly requires documentation changes.

## Current architecture checkpoint

Step 2 substantially improved the reference workbook: CLI assumptions now flow into the build; the condensed workbook contains Net Interest / Net Interest After Tax; balance-sheet classifications and values are colocated; DuPont no longer hard-codes equity row 7; the model now populates a ten-year residual-income chain; and the Python scenario engine no longer taxes an already-after-tax cost of debt a second time.

However, independent code review found that **the underlying source-line resolver is still duplicated and ambiguous**, so the Answer Key is not yet trustworthy enough to move on to expanding the exercise catalog.

### Review findings from commit `56b03a8` (`chat step 2`)

1. **The Python anchor still selects the wrong tax line in the supplied demo.** `financial_math._find_line()` performs unrestricted substring matching, and `compute_anchor()` calls `_find_line(is_items, "tax", "income tax")`. In `DEMO_HK_Standardized.json`, `Profit before tax` appears before `Income tax expense`, so the generic fragment `tax` resolves the pretax-profit row as the tax-expense row. That makes Python ETR, NIAT, NOPAT, historical CoD, and downstream scenario expected values wrong even though the workbook-side tax lookup was improved.
2. **Workbook and Python use different source-line resolvers.** `reference_model.py` now has `_source_row()` with one set of aliases while `financial_math.py` still has `_find_line()` with another. This is the root cause of definition drift: a future label can resolve to different source data in Excel and Python.
3. **Net-interest workbook logic incorrectly requires both interest expense and interest income.** If a company reports finance costs but no separate finance income line (or vice versa), `Net Interest` is left blank. Python treats a missing line as zero, so workbook and Python diverge for a valid input shape.
4. **Equity fallback is inconsistent.** `compute_anchor()` falls back to `NOA - Net Debt` when it cannot find an equity line, but `ReferenceModelBuilder._equity_bs_row()` raises an exception unless a label contains `total equity` or `shareholders`. A valid HK input such as `Equity attributable to owners of the Company`, or a standardized input without a separate equity total, can therefore build in Python but fail when generating the workbook.
5. **The new integrity tests remain demo-shape/string tests rather than true source-resolution tests.** They verify that formulas exist and that the ten-year chain is populated, but they do not catch the demo tax-line error above, do not test missing optional interest lines, and do not test equity fallback. `test_semantic_formulas_have_no_blank_required_refs` also does not actually inspect the direct references of all 13 semantic formulas; it mainly verifies formula presence plus two Y10 cells.
6. **The handoff contains no Step 2 test report.** `RESULT.md` still reports Step 1, and the GitHub commit has no CI statuses. ChatGPT therefore cannot independently confirm what Cursor ran for Step 2 from the committed checkpoint.

This document does **not** claim that the product is complete. The next bounded step removes the duplicated source-resolution logic and adds independent fixtures that can catch these failures before the project expands.

## Active implementation step

### Step 2B — Unify financial-line resolution and prove workbook/Python parity

**Goal**

Make source-statement line selection a single canonical operation used by both Python expected-value calculations and Excel reference-model construction. Then add independent tests for misleading labels, missing optional lines, shuffled row order, and equity fallback so the current 13 semantic Answer Key components are based on the same underlying financial facts.

Do **not** add new trainer components in this step.

## Required changes

### 1. Create one canonical line-item resolver

Create `core/model/line_resolver.py` as the single source of truth for resolving the financial statement concepts needed by the current model.

Use this public interface (names may be adjusted only if an existing project convention clearly conflicts):

```python
@dataclass(frozen=True)
class ResolvedLine:
    item: LineItem | None
    index: int | None


def resolve_line(
    items: list[LineItem],
    concept: str,
    *,
    required: bool = False,
) -> ResolvedLine:
    ...
```

The initial canonical concepts are:

```text
revenue
net_income
pretax_income
tax_expense
interest_expense
interest_income
total_equity
```

Resolution order must be:

1. exact normalized `LineItem.concept` match when an explicit concept is supplied in standardized data;
2. exact normalized label aliases;
3. narrowly defined safe label-pattern aliases where exact labels are insufficient;
4. return `(None, None)` for an optional concept that is not present;
5. raise a clear error for a required concept that is absent;
6. raise a clear ambiguity error when two lines match at the same priority rather than silently taking the first row.

Do **not** use unrestricted generic aliases such as `"tax"` for `tax_expense` or `"sales"` for revenue when they can match `Profit before tax` or `Cost of sales`.

At minimum support these label families:

- revenue: `Revenue`, `Turnover`, safe revenue/sales variants that do not match `Cost of sales`;
- net income: `Profit for the year`, `Net income`, `Net profit`;
- pretax income: `Profit before tax`, `Profit before taxation`, `Pretax income`;
- tax expense: `Income tax expense`, `Tax expense`, `Taxation`;
- interest expense: `Finance cost`, `Finance costs`, `Interest expense`;
- interest income: `Finance income`, `Interest income`;
- total equity: `Total equity`, `Shareholders' equity`, `Shareholders' funds`, `Equity attributable to owners of the Company` and equivalent normalized punctuation/case variants.

Keep the resolver small and deterministic; do not turn this step into a general accounting ontology.

### 2. Make `financial_math.compute_anchor()` use only the canonical resolver

Modify `core/model/financial_math.py` so `compute_anchor()` no longer uses `_find_line()` for the concepts listed above.

Required behavior:

- `revenue`, `net_income`, and `pretax_income` should use the shared resolver.
- `tax_expense` must never resolve `Profit before tax` merely because it contains the word `tax`.
- `interest_expense` and `interest_income` remain optional and individually default to zero when absent.
- ETR stays `-tax_expense / pretax_income` when pretax income is nonzero; otherwise `0.0`, matching the current sign convention.
- Net interest stays `-(interest_expense + interest_income)` with a missing optional line treated as zero.
- NOPAT remains `Net Income + Net Interest After Tax`.
- `total_equity` should use the shared resolver when present; when absent, retain the existing `NOA - Net Debt` fallback.

Remove or stop using `_find_line()` for these model concepts so there are not two competing resolution systems.

### 3. Make `ReferenceModelBuilder` use the same resolved lines and the same fallbacks

Modify `core/engine/reference_model.py` so it no longer independently guesses these source rows with `_source_row()` fragments.

For source-sheet formulas, derive the source row from the index returned by `resolve_line()` and the known source-sheet start row (`7` in the current builder), or create one focused helper that converts `ResolvedLine.index` to the workbook row. The important requirement is that Python and Excel resolve the **same `LineItem`** before any formula is built.

#### Historical income statement behavior

- Build Net Income, Pretax Income, Tax Expense, Interest Expense, and Interest Income from the canonical resolutions.
- Interest Expense and Interest Income are optional independently.
- Build `Net Interest` for all supported input shapes:
  - both present: `=-(Interest Expense + Interest Income)`;
  - expense only: `=-Interest Expense`;
  - income only: `=-Interest Income`;
  - neither: `=0`.
- Build ETR as a populated formula/value consistent with Python:
  - when tax and pretax are available, use a zero-safe formula such as `=IF(Pretax=0,0,-Tax/Pretax)`;
  - when one is unavailable, use `=0` rather than leaving a required dependency blank.
- Net Interest After Tax and NOPAT must therefore remain populated even when one optional interest line is absent.

#### Equity behavior

Add/retain a clearly labelled historical `Equity` row in `Condensed Financials` for every period:

- if canonical `total_equity` is resolved, link the corresponding Balance Sheet values;
- otherwise calculate `Equity = NOA - Net Debt`, matching `compute_anchor()`.

Make DuPont FLEV and Actual ROE reference this condensed Equity row. Remove `_equity_bs_row()` and direct dependence on a specially named raw Balance Sheet equity row.

This produces one identical equity definition for Python and workbook logic and allows valid inputs without a literal `Total equity` line.

### 4. Add independent source-resolution fixtures that would fail the current commit

Extend `core/tests/test_reference_integrity.py` (or split source-resolution tests into `core/tests/test_line_resolver.py` if that keeps responsibilities clearer).

Add tests for all of these cases:

1. **Demo tax regression.** Independently select the exact demo labels `Profit before tax` and `Income tax expense`, compute the latest-year ETR / NIAT / NOPAT directly from their numeric fixture values, and assert `compute_anchor(...).nopat` matches that result. This test must fail on commit `56b03a8` because the current Python resolver selects `Profit before tax` as the tax line.
2. **Misleading labels and row order.** Build a synthetic income statement where `Profit before tax` appears before `Income tax expense`, and where `Cost of sales` appears before `Revenue`. Resolve `tax_expense` and `revenue` correctly regardless of ordering.
3. **Explicit concept wins.** A `LineItem` with `concept="tax_expense"` must outrank a label-only candidate.
4. **Missing interest income.** Build a valid `StandardizedFinancials` fixture with finance costs but no finance-income line. `compute_anchor()` and the generated Answer Key must both produce populated Net Interest, NIAT, and NOPAT rather than a blank dependency.
5. **Missing interest expense / income-only case.** Verify the inverse optional case as well.
6. **Equity alias.** A Balance Sheet line named `Equity attributable to owners of the Company` must build successfully and drive the same equity values in Python and `Condensed Financials`.
7. **Equity absent fallback.** Remove any explicit total-equity line from a synthetic fixture. The build must still succeed and both Python and workbook must use `NOA - Net Debt`.
8. **Ambiguity.** Two same-priority candidates for a required canonical concept must raise a deterministic ambiguity error rather than silently using whichever row happens to come first.

Tests must construct synthetic `LineItem` / `StandardizedFinancials` objects directly where possible. Do not create many permanent fixture files just to vary one label.

### 5. Strengthen formula-dependency integrity checks

The current `test_semantic_formulas_have_no_blank_required_refs` is too weak for its name. Replace or strengthen it so it actually examines the generated Answer Key dependency slice.

At minimum it must directly verify:

- the 13 semantic cells contain the registered formulas;
- historical NOPAT references populated Net Income and NIAT cells;
- DuPont RNOA / CoD / Spread / FLEV / ROE cells reference populated historical cells;
- Base Y1 Sales / NOPAT / AE reference populated inputs;
- year-10 AE and discount factor are populated before terminal value;
- terminal value, PV terminal value, intrinsic value, IVPS, and scenario-weighted IVPS reference populated cells/ranges.

A small test-only A1-reference extractor is acceptable. Do not implement a general Excel formula engine. The purpose is to detect required blank precedents, not to evaluate arbitrary Excel syntax.

### 6. Preserve the improvements already made in Step 2

Do not regress:

- CLI `--assumptions` propagation;
- colocated condensed balance-sheet classification/value table;
- corrected DuPont mathematical definitions;
- the single after-tax CoD convention;
- ten-year Bear/Base/Bull forecast population;
- paired Trainer / Answer Key generation;
- blank yellow/no-Note Trainer practice cells;
- yellow/formula/legacy-Note Answer Key cells;
- semantic component catalog membership/order and coordinate-free design.

### 7. Make the test handoff visible to ChatGPT

Before reporting completion, overwrite `RESULT.md` with the current step result. It must contain:

```text
Status: Step 2B complete | blocked
Files changed: ...
Tests run:
- <exact command> -> <exact pass/fail count>
- ...
Unresolved: ...
```

Do not leave the Step 1 report in place after implementing Step 2B. Cursor still must not commit or push; the user will checkpoint the working tree.

## Files expected to change

- Create: `core/model/line_resolver.py`
- Modify: `core/model/financial_math.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_reference_integrity.py`
- Create or modify: `core/tests/test_line_resolver.py` only if tests are cleaner separated
- Modify: `RESULT.md`

Only modify `core/model/ri_engine.py` if the new independent parity tests expose a concrete remaining mismatch.

## Do not change

- `TARGET.md`.
- `COMPONENT_CATALOG` membership or ordering.
- The Trainer / Answer Key product contract.
- The Hint/Reveal UX or adjacent-cell hint behavior in this step.
- Workbook aesthetics except where the new condensed Equity row needs the existing shared style.
- HK automatic scraping or unrelated ingestion features.
- Git history. Do not commit, push, reset, rebase, merge, or delete branches.

## Acceptance criteria

- The supplied demo resolves `Income tax expense` as tax expense; `Profit before tax` is never selected as the tax-expense line.
- Python latest-year demo NOPAT equals an independently calculated fixture value using the actual tax-expense row, not merely a value produced by the same resolver under test.
- Python and workbook source selection use the same canonical resolver for revenue, net income, pretax income, tax expense, interest expense, interest income, and total equity.
- A company with only interest expense, only interest income, both, or neither produces a populated Net Interest → NIAT → NOPAT chain consistent with Python.
- A company with an equity alias or no explicit equity line builds successfully; Python and workbook use the same equity values/fallback.
- Reordering source statement rows does not change which canonical financial facts are selected.
- Ambiguous same-priority source lines fail loudly instead of silently changing the model.
- No required direct precedent in the current 13-component Answer Key dependency slice is blank.
- All Step 1 paired-workbook tests and Step 2 ten-year/model-integrity tests remain green according to Cursor's committed `RESULT.md` report.
- No new coordinate registry or duplicated financial-line resolver is introduced.

## Testing

Use red/green TDD. The first new test should reproduce the current demo tax-selection bug before production code changes.

Run the focused resolver tests first, then reference-integrity tests, then the existing trainer module, then the full current core suite. At minimum report:

```bash
python -m pytest core/tests/test_line_resolver.py -v --tb=short
```

If you keep all resolver tests in `test_reference_integrity.py`, replace that first command with the exact focused node/test selection used.

Then run:

```bash
python -m pytest core/tests/test_reference_integrity.py -v --tb=short
python -m pytest core/tests/test_trainer.py -v --tb=short
python -m pytest core/tests/ -q --tb=line
```

Do not weaken existing tests to make them pass. Do not use `check_component()` success as proof that the reference formula is financially correct.

## Git boundary

Do not commit, push, reset, rebase, merge, or otherwise change Git history.

## Cursor execution rules

1. Read the active step before editing.
2. Inspect the existing implementation first.
3. Write the failing regression test for the demo tax-resolution defect before changing production code.
4. Make the smallest coherent change that fixes the root cause rather than patching individual labels in two places.
5. Preserve existing architecture and conventions unless the step explicitly changes them.
6. Do not add unrelated cleanup, refactors, abstractions, or features.
7. If the instruction conflicts with the repository, report the conflict instead of silently redesigning the solution.
8. Run the relevant tests/checks after implementation.
9. Fix failures caused by the change.
10. Update `RESULT.md` with exact test evidence and unresolved items.
11. At completion report files changed, behavior implemented, tests/checks run, and anything unresolved.
12. Do not propose the next product step.
13. Do not commit, push, reset, rebase, merge, or delete branches.

## ChatGPT verification protocol

After the user checkpoints/pushes the implementation, ChatGPT should inspect the latest commit against this step and `RESULT.md`.

Verification asks:

- Is there now exactly one canonical financial-line resolver used by both Python and workbook construction?
- Does the demo tax regression genuinely prove that `Profit before tax` cannot become tax expense?
- Do missing optional interest-line tests cover both one-sided cases?
- Does equity alias/fallback behavior match between Python and Excel?
- Are ambiguity and row-order independence tested?
- Are the 13 semantic formula dependency chains checked for populated direct precedents?
- Did Cursor preserve all Step 1/Step 2 behavior?
- Does `RESULT.md` contain current, exact test commands/results rather than a stale previous-step report?

ChatGPT should not rerun the test suite. Cursor owns test execution; ChatGPT owns independent code inspection.

A verified step may then be replaced with the next ChatGPT-authored product step.
