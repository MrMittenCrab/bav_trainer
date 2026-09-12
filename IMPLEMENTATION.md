# Step 9B.1 — Historical Working-Capital Diagnostics Foundation

> **Status:** Step 9B.1 complete. See `RESULT.md` for verification evidence (210 passed; base 36/168; normalization 40/188; Working Capital Analysis gated on nonzero OWCA/OWCL). Do not commit or push from this checkpoint unless the user requests it.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `67f273a7c588c98c875f7cc7a22be0c819d210e1` (`Step 9.5`, Step 9A.5 complete). Implement only Step 9B.1 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, Step 9A earnings-quality diagnostics, historical source completeness, and all established `#N/A` semantics. Do not add automatic good/bad quality labels, seasonality claims, forecasting, valuation, ROU/deferred-tax alternative modeling, segment analysis, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Add an auditable historical working-capital diagnostic schedule that teaches how operating working-capital intensity and incremental working-capital investment move relative to Revenue, while preserving live classification judgment and avoiding unsupported automatic interpretation.

**Architecture:** Reuse the existing authoritative reformulation instead of reclassifying raw balance-sheet labels. Compute one Python `WorkingCapitalSeries` from `AnchorMetrics` using Revenue plus the already classified Operating Working Capital Asset, Operating Working Capital Liability, and NOWC series. Add six semantic formula families and a visible `Working Capital Analysis` sheet only when operating working capital is actually present. Formula Check recomputes expected values from the current live classification treatment, and trusted-sheet validation protects all generated non-practice cells on the new sheet.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `AnchorMetrics`, `BalanceSheetReformulation`, `ratio_or_na`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and trusted-workbook structural validation.

**Spec:** `TARGET.md`, especially working-capital behavior, capital intensity, accounting consistency, research diagnostics, material/applicable-topic gating, the historical dependency graph, and the requirement that interpretation distinguish calculation from unsupported causal claims.

---

## Review of commit `67f273a7`

Step 9A.5 is implemented coherently:

- zero Pretax Income now produces Effective Tax Rate `#N/A` / Excel `NA()`;
- zero amounts that require no tax estimate remain determinately zero;
- nonzero tax-effected amounts propagate undefined ETR rather than inventing a rate;
- normalization source candidates are period-complete before use;
- Step 9A.4 DuPont undefined-ratio behavior is preserved;
- base workbook remains 30 families / 141 practice cells;
- normalization workbook remains 34 families / 161 practice cells;
- `RESULT.md` records 202 locally passing tests;
- GitHub has no attached CI status.

No blocking defect remains on the active historical tax / normalization surface addressed by Step 9A.5.

The next dependency in `TARGET.md` is historical driver interpretation. Start with working capital because the current model already has authoritative, classification-sensitive OWCA / OWCL / NOWC series, but does not yet teach how to relate those balances to sales growth or incremental operating-capital investment.

Step 9B.1 builds the **mechanical diagnostic foundation only**. It does not claim that a ratio movement is automatically good, bad, seasonal, deteriorating, or sustainable.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all existing Step 8 judgment behavior and treatment-conditioned Check.
- Preserve Step 9A earnings-quality sheets/families and applicability gating.
- Preserve historical source completeness and trusted-workbook validation.
- Preserve all current `#N/A` conventions for undefined ratios.
- Working-capital calculations must consume the authoritative classified reformulation; do not classify raw balance-sheet labels a second time.
- Revenue must come from `AnchorMetrics.historical.revenue`; do not resolve a parallel Revenue series independently.
- OWCA, OWCL, and NOWC must come from `AnchorMetrics.reformulation`.
- A zero numerator with nonzero Revenue is a valid numeric zero ratio.
- A zero Revenue denominator makes OWCA / Revenue, OWCL / Revenue, or NOWC / Revenue undefined (`#N/A`).
- First-period changes are non-applicable (`None` in Python; visible `N/A` text in the workbook), not zero.
- A zero change in Revenue makes Incremental NOWC / Change in Revenue undefined (`#N/A`).
- Positive Change in NOWC means additional operating working capital is tied up; negative Change in NOWC means working capital is released. This is an accounting/cash-use interpretation only, not an automatic quality judgment.
- Annual historical data alone must not be described as proving seasonality.
- Do not infer deterioration, channel stuffing, supplier stress, collection quality, inventory obsolescence, or payment stretching automatically from these ratios.
- Do not add free-form automatic grading.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior in this checkpoint.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Define one authoritative working-capital diagnostic series

**Files:**
- Create: `core/model/working_capital.py`
- Test: create `core/tests/test_working_capital.py`

Create:

```python
from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .ratio_values import ratio_or_na


@dataclass(frozen=True)
class WorkingCapitalSeries:
    owca_to_revenue: tuple[float | str, ...]
    owcl_to_revenue: tuple[float | str, ...]
    nowc_to_revenue: tuple[float | str, ...]
    revenue_change: tuple[float | None, ...]
    nowc_change: tuple[float | None, ...]
    incremental_nowc_to_revenue_change: tuple[float | str | None, ...]
```

Create:

```python
def working_capital_applicable(anchor: AnchorMetrics) -> bool:
    ...


def compute_working_capital_series(anchor: AnchorMetrics) -> WorkingCapitalSeries:
    ...
```

### Source series

Use exactly:

```python
revenue = tuple(float(v) for v in anchor.historical.revenue)
owca = tuple(
    float(v)
    for v in anchor.reformulation.category_totals[
        "Operating Working Capital Asset"
    ]
)
owcl = tuple(
    float(v)
    for v in anchor.reformulation.category_totals[
        "Operating Working Capital Liability"
    ]
)
nowc = tuple(float(v) for v in anchor.reformulation.nowc)
```

Require all four series to have the same nonzero length. If not, raise a clear `ValueError` describing the length mismatch.

### Applicability gate

Working-capital diagnostics are applicable when at least one modeled-period OWCA or OWCL balance is nonzero:

```python
return any(v != 0.0 for v in owca) or any(v != 0.0 for v in owcl)
```

Do not gate on labels, keywords, or model guesses.

A company with all-zero OWCA and OWCL is not given this diagnostic sheet in this checkpoint.

### Ratios

For every period `i`:

```python
owca_to_revenue[i] = ratio_or_na(owca[i], revenue[i])
owcl_to_revenue[i] = ratio_or_na(owcl[i], revenue[i])
nowc_to_revenue[i] = ratio_or_na(nowc[i], revenue[i])
```

Required semantics:

```text
OWCA = 0, Revenue = 100 -> 0.0
OWCL = 0, Revenue = 100 -> 0.0
NOWC = 0, Revenue = 100 -> 0.0
Revenue = 0             -> #N/A for all three intensity ratios
```

### Changes

For period zero:

```python
revenue_change[0] = None
nowc_change[0] = None
incremental_nowc_to_revenue_change[0] = None
```

For `i > 0`:

```python
delta_revenue = revenue[i] - revenue[i - 1]
delta_nowc = nowc[i] - nowc[i - 1]
revenue_change[i] = delta_revenue
nowc_change[i] = delta_nowc
incremental_nowc_to_revenue_change[i] = ratio_or_na(
    delta_nowc,
    delta_revenue,
)
```

Required semantics:

```text
ΔNOWC = 0, ΔRevenue = 100 -> 0.0
ΔRevenue = 0              -> #N/A
ΔRevenue < 0              -> retain the mathematically signed ratio
ΔNOWC < 0                 -> retain the negative working-capital release
```

Do not take absolute values.

### TDD

- [ ] Ordinary multi-period fixture returns all six expected series.
- [ ] Zero Revenue yields `#N/A` intensity ratios.
- [ ] Zero numerator with nonzero Revenue yields numeric `0.0`.
- [ ] First-period change values are `None`.
- [ ] Zero ΔRevenue yields incremental ratio `#N/A`.
- [ ] Negative ΔNOWC remains negative.
- [ ] Negative ΔRevenue is not converted to an absolute denominator.
- [ ] Series-length mismatch fails clearly.
- [ ] All-zero OWCA/OWCL makes `working_capital_applicable(...)` false.
- [ ] At least one nonzero OWCA or OWCL makes it true.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
```

---

## Task 2 — Add six semantic working-capital formula families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_working_capital.py`
- Test: `core/tests/test_reference_integrity.py`

### Component catalog

Add a separate catalog rather than folding diagnostics into the original 25-family historical construction core:

```python
WORKING_CAPITAL_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (...)
```

Add:

```python
def expand_working_capital_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    ...
```

Use the same chronological / duplicate-period validation as the other expanders.

Define exactly these six families:

### 1. `owca_to_revenue`

```text
title: Operating working capital assets / Revenue
sheet: Working Capital Analysis
period scope: all
formula concept: OWCA / Revenue
```

Hints:

```text
Operating Working Capital Assets / Revenue measures operating current assets tied up per sales dollar.
A zero Revenue denominator makes the ratio undefined (#N/A).
A higher ratio is not automatically deterioration; diagnose the underlying operating balances before drawing a conclusion.
```

### 2. `owcl_to_revenue`

```text
title: Operating working capital liabilities / Revenue
sheet: Working Capital Analysis
period scope: all
formula concept: OWCL / Revenue
```

Hints:

```text
Operating Working Capital Liabilities / Revenue measures operating current liabilities financing each sales dollar.
A zero Revenue denominator makes the ratio undefined (#N/A).
A higher ratio can finance growth but is not automatically positive; payment behavior and business model matter.
```

### 3. `nowc_to_revenue`

```text
title: NOWC / Revenue
sheet: Working Capital Analysis
period scope: all
formula concept: NOWC / Revenue
```

Hints:

```text
NOWC / Revenue measures net operating working capital tied up per sales dollar.
NOWC = OWCA - OWCL.
Rising intensity means more net working capital is tied up per sales dollar, but the cause must be diagnosed rather than labeled automatically.
```

### 4. `revenue_change`

```text
title: Change in Revenue
sheet: Working Capital Analysis
period scope: comparable
formula concept: Current Revenue - Prior Revenue
```

Hint:

```text
Use the absolute year-on-year change in Revenue, not the percentage growth rate.
```

### 5. `nowc_change`

```text
title: Change in NOWC
sheet: Working Capital Analysis
period scope: comparable
formula concept: Current NOWC - Prior NOWC
```

Hints:

```text
Positive Change in NOWC means additional operating working capital is tied up; negative Change in NOWC means a release.
Do not call the movement good or bad without examining why it occurred.
```

### 6. `incremental_nowc_to_revenue_change`

```text
title: Incremental NOWC / Change in Revenue
sheet: Working Capital Analysis
period scope: comparable
formula concept: Change in NOWC / Change in Revenue
```

Hints:

```text
This ratio measures incremental working-capital investment per unit of incremental sales.
A zero Change in Revenue denominator makes the ratio undefined (#N/A).
Negative or unusually large values are diagnostic signals, not automatic quality labels.
```

### Expected values

In `core/model/historical_expected.py`, import:

```python
from .working_capital import compute_working_capital_series
```

Add a working-capital family-id tuple and:

```python
def working_capital_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    wc = compute_working_capital_series(anchor)
    ...
```

Map exactly:

```python
{
    "owca_to_revenue": wc.owca_to_revenue,
    "owcl_to_revenue": wc.owcl_to_revenue,
    "nowc_to_revenue": wc.nowc_to_revenue,
    "revenue_change": wc.revenue_change,
    "nowc_change": wc.nowc_change,
    "incremental_nowc_to_revenue_change": wc.incremental_nowc_to_revenue_change,
}
```

Extend `expected_value_for_component()` so a component in this new catalog is resolved from `working_capital_expected_series(anchor)`.

No new argument is required on `expected_value_for_component()` because all working-capital diagnostics are fully determined by the already treatment-conditioned `AnchorMetrics`.

### TDD

- [ ] Working-capital catalog contains exactly six unique family IDs.
- [ ] Three intensity families expand across all five demo periods.
- [ ] Three change/incremental families expand only across comparable periods.
- [ ] Five fiscal periods therefore produce exactly 27 working-capital practice cells.
- [ ] `working_capital_expected_series()` keys exactly match the catalog family IDs.
- [ ] Dynamic expected values change when a live classification treatment changes OWCA/OWCL/NOWC.

---

## Task 3 — Wire applicability and ordering into `ReferenceModelBuilder`

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/engine/component_catalog.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_working_capital.py`

Import:

```python
from ..model.working_capital import (
    compute_working_capital_series,
    working_capital_applicable,
)
```

After the existing normalization and earnings-quality setup, compute:

```python
self.working_capital_series = (
    compute_working_capital_series(self.anchor)
    if working_capital_applicable(self.anchor)
    else None
)
```

If applicable, expand specs after all currently active historical / normalization / quality specs:

```python
self.working_capital_specs = expand_working_capital_specs(
    self.periods,
    start_order=(
        len(self.historical_specs)
        + len(self.normalization_specs)
        + len(self.quality_specs)
        + 1
    ),
)
```

Otherwise:

```python
self.working_capital_specs = ()
```

Build:

```python
self.expected_specs = (
    self.historical_specs
    + self.normalization_specs
    + self.quality_specs
    + self.working_capital_specs
)
```

Create an index:

```python
self._working_capital_spec_index = {
    (s.family_id, s.period_index): s
    for s in self.working_capital_specs
}
```

Add a focused registration helper analogous to `_register_quality()`:

```python
def _register_working_capital(...):
    ...
```

Do not modify the meaning/order of existing families.

### Demo acceptance counts

The current five-year demo has operating working capital and earnings-quality inputs. Therefore Step 9B.1 adds:

```text
6 families
27 practice cells
```

Expected demo surfaces become:

```text
base demo:          36 families / 168 practice cells
normalization demo: 40 families / 188 practice cells
```

These are acceptance counts for the current demo, not universal counts for every company because working-capital applicability remains conditional.

### Applicability regression

Create a synthetic otherwise-valid company whose classified OWCA and OWCL are zero in every modeled period.

Require:

```text
working_capital_specs == ()
Working Capital Analysis sheet absent
```

Do not suppress the existing historical, DuPont, or earnings-quality surface merely because working capital is not applicable.

---

## Task 4 — Render the visible `Working Capital Analysis` sheet

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_working_capital.py`
- Test: `core/tests/test_trainer.py`

Add:

```python
WORKING_CAPITAL_SHEET = "Working Capital Analysis"
```

Create the visible sheet only when `self.working_capital_series is not None`.

Call `_build_working_capital_analysis(wb)` after `Earnings Quality` when applicable and before deferred placeholder tabs.

### Header

Use:

```text
A1  Working Capital Analysis
A2  Relate classified operating working capital to Revenue and identify how much incremental NOWC accompanies changes in sales.
A3  These are diagnostics, not automatic judgments. Positive Change in NOWC is an operating cash use; negative Change in NOWC is a release. Annual data alone does not prove seasonality or deterioration.
```

Use the existing workbook aesthetic; do not introduce a new design language.

Row 5 headers:

```text
Metric | FY1 | FY2 | ...
```

### Trusted source-link block

Add four populated, non-practice rows:

```text
Revenue
Operating Working Capital Assets
Operating Working Capital Liabilities
NOWC
```

Link them to the authoritative rows on `Condensed Financials`, not directly to raw source statements.

Required formulas are simple same-period links, for example:

```excel
='Condensed Financials'!B<revenue_row>
='Condensed Financials'!B<owca_row>
='Condensed Financials'!B<owcl_row>
='Condensed Financials'!B<nowc_row>
```

Store the Condensed OWCA and OWCL row numbers in `self.rowmap` if they are not already retained by `_build_condensed()`:

```python
self.rowmap["condensed_owca_row"] = owca_row
self.rowmap["condensed_owcl_row"] = owcl_row
```

Do not duplicate classification logic on the new sheet.

### Practice block

Below the source block create exactly six practice rows:

```text
OWCA / Revenue
OWCL / Revenue
NOWC / Revenue
Change in Revenue
Change in NOWC
Incremental NOWC / Change in Revenue
```

### Intensity formulas

For each fiscal period, use:

```excel
=IF(RevenueCell=0,NA(),OWCACell/RevenueCell)
=IF(RevenueCell=0,NA(),OWCLCell/RevenueCell)
=IF(RevenueCell=0,NA(),NOWCCell/RevenueCell)
```

Use `PCT_FMT`.

Register all three families for all periods.

### Change formulas

For the first fiscal period, write literal:

```text
N/A
```

and do not register a semantic practice component.

For every comparable period:

```excel
=CurrentRevenue-PriorRevenue
=CurrentNOWC-PriorNOWC
```

Use `NUM_FMT`.

### Incremental working-capital formula

For the first fiscal period, write literal:

```text
N/A
```

For each comparable period:

```excel
=IF(ChangeInRevenueCell=0,NA(),ChangeInNOWCCell/ChangeInRevenueCell)
```

Use `PCT_FMT`.

Do not use `IFERROR`.

### Registration

Register every applicable practice formula through `_register_working_capital()` with the Python expected value from `self.working_capital_series`.

No source-link row is a practice cell.

### TDD

- [ ] Sheet is visible when applicable.
- [ ] Sheet is absent when all OWCA/OWCL balances are zero.
- [ ] Four source rows are populated in both Trainer and Answer Key.
- [ ] Source rows link to `Condensed Financials`, not raw balance-sheet rows.
- [ ] Trainer blanks exactly the 27 working-capital practice cells for the five-year demo.
- [ ] Answer Key contains formulas plus legacy Notes for all 27 cells.
- [ ] First-period change/incremental cells are populated `N/A`, not yellow practice cells.
- [ ] Zero Revenue uses `NA()` in intensity formulas.
- [ ] Zero ΔRevenue uses `NA()` in the incremental formula.
- [ ] No `IFERROR(...,0)` or numeric-zero denominator fallback is introduced.

---

## Task 5 — Protect generated working-capital cells under the trusted-workbook boundary

**Files:**
- Modify: `core/trainer/check_context.py`
- Test: `core/tests/test_working_capital.py`
- Test: `core/tests/test_trainer.py`

Add:

```python
WORKING_CAPITAL_SHEET = "Working Capital Analysis"
```

inside the Check-context module or import a non-circular shared constant if an existing pattern supports it cleanly.

During `validate_live_model_structure()`, derive:

```python
working_capital_practice = {
    cell
    for tab, cell in practice_cells
    if tab == WORKING_CAPITAL_SHEET
}
```

If this set is nonempty:

1. require the sheet to exist in both Trainer and Answer Key;
2. call `_validate_trusted_sheet_cells()` for the entire sheet;
3. exclude only the semantic working-capital practice coordinates.

Therefore the following remain trusted and immutable during Check:

- sheet title/instructions;
- period headers;
- four source-link rows;
- first-period `N/A` cells;
- row labels;
- all other non-practice contents.

### Tamper regression

- [ ] Build the demo Trainer/Answer-Key pair.
- [ ] Put an exact correct formula in one working-capital practice cell.
- [ ] Overwrite one generated Revenue/OWCA/OWCL/NOWC source link on the new sheet.
- [ ] Run Check and require `ValueError` before any practice-cell recoloring.
- [ ] Reopen the workbook and prove the practice cell remains yellow.

Also prove a learner may use an equivalent formula in a semantic working-capital practice cell without structural rejection.

---

## Task 6 — Prove live classification treatment flows into working-capital Check

**Files:**
- Modify: `core/tests/test_working_capital.py`
- Modify: `core/tests/test_normalization.py` only if an existing workbook cached-value helper is intentionally reused

This is essential: the new diagnostics must not freeze the Answer-Key reference classification.

Use a fixture containing at least one Step 8 classification judgment whose alternative changes whether a balance-sheet line belongs in OWCA or OWCL versus a financing category.

Required regression:

1. Build Trainer + Answer Key.
2. Record a working-capital expected value under the reference treatment.
3. Change `Accounting Judgment!F` to the allowed alternative.
4. Recompute the authoritative Python anchor with that alternative and prove at least one of OWCA / OWCL / NOWC changes.
5. Put a structurally different learner formula into the affected working-capital practice cell and inject the cached value for the **alternative** treatment.
6. Run `check_workbook()`.
7. Require green.
8. Inject the stale cached reference-treatment result under the alternative treatment.
9. Require red.

This proves working-capital diagnostics use the learner's live classification state rather than static Answer-Key expected values.

Do not add new Check-context answer data for these metrics; the existing source payload + live classification binding is sufficient.

---

## Task 7 — Formula Check regressions for ordinary and undefined working-capital ratios

**Files:**
- Modify: `core/tests/test_working_capital.py`

Add end-to-end Check coverage for:

### Exact formula

A correct exact working-capital formula becomes green.

### Equivalent numeric formula

A structurally different formula with the correct cached numeric result becomes green.

### Incorrect numeric result

A cached numeric result outside tolerance becomes red.

### Undefined intensity ratio

When Revenue is zero:

```text
expected = #N/A
```

Prove:

- exact `NA()`-guarded formula passes;
- equivalent formula with cached `#N/A` passes;
- fabricated cached `0.0` fails.

### Undefined incremental ratio

When ΔRevenue is zero, prove the same `#N/A` / fabricated-zero behavior for `incremental_nowc_to_revenue_change`.

Check output must remain aggregate/non-disclosing.

---

## Task 8 — Update workbook instructions and learner framing

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `README-HK-TRAINER.md` only if it contains a current curriculum/sheet list that would otherwise become stale
- Modify: `skills/bav-trainer/SKILL.md` only if its current user-facing description enumerates active sheets/families
- Test: `core/tests/test_working_capital.py`

The sheet must teach the limits of the diagnostic without supplying a company-specific answer.

Required visible framing:

```text
Positive Change in NOWC = additional operating working capital tied up (cash use).
Negative Change in NOWC = operating working capital released.
NOWC / Revenue and Incremental NOWC / Change in Revenue are diagnostics, not automatic good/bad scores.
Annual data alone does not prove seasonality.
```

Do not insert statements such as:

```text
higher NOWC / Revenue is bad
lower OWCL / Revenue is good
negative incremental NOWC is always good
```

Those claims are not generally valid.

Do not add model-written company-specific causal explanations in this checkpoint.

---

## Task 9 — Full regression and checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after verification passes
- Do not modify: `TARGET.md`

Run focused tests first:

```bash
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
```

Then existing major suites:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_validators.py -v
```

Then run the complete suite:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual pass count; do not hard-code a predicted test total into `RESULT.md`.

### Base demo

Run:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required demo result:

```text
168 practice cells
0 correct / 0 incorrect / 168 blank
36 schedule groups
```

### Normalization demo

Run:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o /tmp/DEMO_NORM_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_NORM_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_NORM_Trainer.xlsx
```

Required demo result:

```text
188 practice cells
0 correct / 0 incorrect / 188 blank
40 schedule groups
```

### CLI

Run:

```bash
PYTHONPATH=. python -m core --help
```

Public commands remain exactly:

```text
ingest
build
check
list
```

### RESULT.md

Record:

- actual full-suite pass count;
- working-capital applicability gate;
- six families / 27 cells on the five-year demo;
- base demo 36 / 168;
- normalization demo 40 / 188;
- OWCA / Revenue, OWCL / Revenue, NOWC / Revenue diagnostics;
- Change in Revenue and Change in NOWC;
- incremental NOWC / Change in Revenue;
- zero-denominator `#N/A` behavior;
- live classification-conditioned Check regression;
- trusted source-link tamper rejection;
- no automatic good/bad quality labeling;
- no seasonality inference;
- `TARGET.md` unchanged;
- forecasting / valuation not begun.

Do not regenerate committed demo XLSX files unless serialized workbook fixtures are intentionally maintained by the repository's current test/release workflow.

---

## Definition of done

Step 9B.1 is complete only when all of the following are true:

1. One authoritative Python working-capital diagnostic series exists.
2. Diagnostics consume the existing classified reformulation rather than reclassifying labels.
3. Working-capital analysis is gated off when OWCA and OWCL are zero across all modeled periods.
4. Applicable companies receive a visible `Working Capital Analysis` sheet.
5. The sheet contains trusted Revenue / OWCA / OWCL / NOWC source links to `Condensed Financials`.
6. OWCA / Revenue, OWCL / Revenue, and NOWC / Revenue are practiced across all modeled periods.
7. Change in Revenue, Change in NOWC, and Incremental NOWC / Change in Revenue are practiced only for comparable periods.
8. Five applicable fiscal periods add exactly six families / 27 practice cells.
9. Zero Revenue or zero Change in Revenue yields `#N/A`, not fabricated zero.
10. First-period change metrics remain non-applicable rather than zero.
11. Positive/negative Change in NOWC retains its accounting sign.
12. Dynamic Check recomputes working-capital expected values from the learner's current classification treatment.
13. Stale reference-treatment working-capital results are rejected after a live classification change.
14. Generated non-practice cells on `Working Capital Analysis` are protected by trusted-sheet validation.
15. Exact and equivalent formulas remain Check-compatible.
16. Base demo reaches 36 families / 168 cells.
17. Normalization demo reaches 40 families / 188 cells.
18. Full test suite passes.
19. No automatic quality score, good/bad label, causal diagnosis, or seasonality conclusion is introduced.
20. `TARGET.md` is unchanged.
21. Forecasting and valuation have not begun.

After completing Step 9B.1, stop and report changed files, exact test output, demo build/check/list output, applicability-gate evidence, and any new active historical-model issue found during implementation. Do not proceed to the next curriculum feature and do not commit or push.
