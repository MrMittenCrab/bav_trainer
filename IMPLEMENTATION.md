# Step 9A.3 — Historical Core Source Completeness Hardening

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `142a3718caeaeab54f791928e898601e6d26ec2d` (`Step 9.2`). Implement only Step 9A.3 below using red/green TDD. Preserve Step 8 classification/normalization, the trusted-workbook boundary, and the complete Step 9A earnings-quality surface. Do not begin working-capital interpretation, quality scoring, forecasting, valuation, ROU/deferred-tax alternative modeling, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Remove the remaining period-level missing-to-zero fallbacks from the authoritative historical accounting engine. A historical line used by the active model must distinguish an explicitly supplied zero from a missing value, and a resolved line with a missing modeled-period value must fail clearly before Trainer/Answer-Key generation.

**Architecture:** Centralize one shared required-period-value primitive and use it in the historical income engine, earnings-quality engine, and balance-sheet reformulation. The historical core income concepts become explicit required inputs rather than silently optional zeroes. Balance-sheet detail rows remain company-specific, but every supplied detail row must be complete across modeled periods; reported BS totals remain optional as whole lines, while any total line that exists must be period-complete. Keep the existing component families and workbook layout unchanged.

**Tech Stack:** Python, dataclasses, pytest, existing `StandardizedFinancials`, `LineItem`, `compute_anchor`, `reformulate_balance_sheet`, `ReferenceModelBuilder`, `SemanticMap`, Trainer/Answer-Key generation, and workbook-wide Check.

**Spec:** `TARGET.md`, especially **No invented historical inputs**, historical reference-model correctness, statement linkage, accounting consistency, and the requirement that historical ratios use supplied historical facts rather than fabricated defaults.

---

## Review of commit `142a3718`

Step 9A.2 is implemented coherently:

- cash-conversion and accrual ratios now return `#N/A` / Excel `NA()` when their denominator is exactly zero;
- an explicit zero numerator with a nonzero denominator remains a valid numeric `0.0`;
- reported Net Income is resolved directly for earnings-quality calculations and must be period-complete;
- the quality Net Income series is checked against `AnchorMetrics`;
- exact `NA()` formulas and equivalent cached `#N/A` results are Check-compatible;
- the Step 9A workbook surfaces remain 30 families / 141 cells and 34 families / 161 cells;
- `RESULT.md` records 188 locally passing tests;
- GitHub has no attached CI status.

No blocking defect remains in the new `#N/A` implementation itself.

However, the review exposes one broader historical-engine integrity gap that should be fixed before building working-capital interpretation on top of it.

### Blocking historical-core issue — resolved source values can still silently become zero

`core/model/financial_math.py` still has:

```python
def _val(item: LineItem | None, period: date) -> float:
    if item is None:
        return 0.0
    v = item.values.get(period)
    return float(v) if v is not None else 0.0
```

This means the authoritative historical model can still treat a missing modeled-period value as an actual zero for Revenue, Net Income, Pretax Income, Tax Expense, Interest Expense, or Interest Income.

Step 9A.2 protects Net Income only when the Earnings Quality module is active. If CFO is unavailable and that module is omitted, an incomplete Net Income line can still flow through the core historical model as zero.

`core/model/classification.py` has the same period-level fallback for balance-sheet detail rows and resolved reported totals:

```python
def _val(item: LineItem, period: date) -> float:
    v = item.values.get(period)
    return float(v) if v is not None else 0.0
```

A supplied balance-sheet row with a missing period therefore becomes indistinguishable from an explicitly supplied zero. Reconciliation may catch some cases when totals are present, but it is not a reliable completeness boundary and can be bypassed when reported totals are absent.

`core/data/validators.py::validate_cash_flow()` also uses `... or 0` while summing CFO / CFI / CFF, so a present cash-flow line with a missing period can be treated as zero during source checksum validation.

Finally, `core/model/classification.py::_norm()` still contains the old duplicate straight-apostrophe normalization tuple and does not deliberately normalize curly apostrophes.

Step 9A.3 closes these source-integrity gaps only. It does not add new analysis.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all current visible sheets and component families.
- Preserve base demo surface at 30 families / 141 practice cells.
- Preserve normalization demo surface at 34 families / 161 practice cells.
- Preserve Step 9A `#N/A` denominator semantics.
- Preserve Step 8 judgment behavior and dynamic Check.
- Explicit numeric zero is a valid supplied fact.
- Missing key and explicit `None` are both missing data, never numeric zero.
- Do not invent Revenue, Net Income, Pretax Income, Tax Expense, Interest Expense, Interest Income, balance-sheet detail values, or reported BS totals.
- Completely absent optional reported BS totals remain allowed; reformulation can operate from complete detail rows without them.
- If an optional reported BS total line exists, it must be complete for all modeled periods.
- The six income-statement concepts used by the historical core are required inputs in this checkpoint:
  - `revenue`
  - `net_income`
  - `pretax_income`
  - `tax_expense`
  - `interest_expense`
  - `interest_income`
- If a company genuinely has zero Interest Income or Interest Expense, standardized input must supply an explicit zero-valued line. Absence is not silently interpreted as zero.
- Do not add feature-level availability gating for the 25 historical families in this checkpoint.
- Do not add working-capital interpretation, thresholds, quality labels, forecasting, valuation, scenarios, Hint/Reveal, VBA, or free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Centralize required historical period values

**Files:**
- Create: `core/model/source_values.py`
- Modify: `core/model/earnings_quality.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_earnings_quality.py`

Create:

```python
from __future__ import annotations

from datetime import date

from ..data.interface import LineItem


class MissingHistoricalValueError(ValueError):
    """A resolved historical source line lacks a required modeled-period value."""


def required_period_value(
    item: LineItem,
    period: date,
    *,
    field: str,
) -> float:
    raw = item.values.get(period)
    if raw is None:
        raise MissingHistoricalValueError(
            f"{field} line {item.label!r} has no supplied value "
            f"for modeled period {period.isoformat()}"
        )
    return float(raw)


def required_period_series(
    item: LineItem,
    periods: list[date],
    *,
    field: str,
) -> tuple[float, ...]:
    return tuple(
        required_period_value(item, period, field=field)
        for period in periods
    )
```

Required semantics:

```text
period key absent          -> MissingHistoricalValueError
period key present + None  -> MissingHistoricalValueError
period key present + 0     -> 0.0
period key present + -0.0  -> -0.0 / numerically zero
nonzero number             -> float(number)
```

Do not create any fallback parameter such as `default=0`.

Migrate `core/model/earnings_quality.py` from its private `_required_period_value()` helper to this shared primitive. The Step 9A behavior and error semantics must remain otherwise unchanged.

### TDD

- [ ] Existing incomplete CFO / Total Assets / Net Income tests remain green after migration.
- [ ] Add at least one focused shared-helper regression through a public caller proving explicit `0.0` is accepted and missing/`None` is rejected.
- [ ] Do not directly expose the helper through the public CLI or workbook layer.

---

## Task 2 — Make all historical-core income inputs explicit and period-complete

**Files:**
- Modify: `core/model/financial_math.py`
- Modify: historical test fixtures as required
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

### Required concepts

Change `compute_anchor()` so the six core historical income concepts resolve with `required=True`:

```python
rev_item = resolve_line(is_items, "revenue", required=True).item
ni_item = resolve_line(is_items, "net_income", required=True).item
pretax_item = resolve_line(is_items, "pretax_income", required=True).item
tax_item = resolve_line(is_items, "tax_expense", required=True).item
int_exp_item = resolve_line(is_items, "interest_expense", required=True).item
int_inc_item = resolve_line(is_items, "interest_income", required=True).item
```

Assert all six resolved items are non-`None`, then build each historical series using `required_period_series()`.

Example:

```python
revenues = list(
    required_period_series(
        rev_item,
        periods,
        field="revenue",
    )
)
```

Do the same for:

```text
net_income
pretax_income
tax_expense
interest_expense
interest_income
```

Delete or stop using the legacy `_val()` zero-fallback in this core path.

### Required behavior

For each of the six concepts:

```text
line absent entirely
    -> build fails with MissingLineError

line resolves but one period is omitted
    -> build fails with MissingHistoricalValueError

line resolves but one period is None
    -> build fails with MissingHistoricalValueError

line resolves with explicit 0.0
    -> accepted as an actual supplied zero
```

Do not special-case Interest Income or Interest Expense to zero when their entire line is absent. Test fixtures that intend zero must contain explicit zero-valued lines.

### TDD

Parameterize at least the following:

- [ ] missing Revenue period;
- [ ] missing Net Income period, including a fixture with no CFO so Step 9A cannot be the component that catches it;
- [ ] missing Pretax Income period;
- [ ] missing Tax Expense period;
- [ ] missing Interest Expense period;
- [ ] missing Interest Income period;
- [ ] one whole required line absent;
- [ ] explicit zero Interest Income succeeds;
- [ ] explicit zero Interest Expense succeeds.

For end-to-end cases call `build_training_workbook()` and require failure before a valid pair is produced.

### Fixture policy

If existing tests rely on an absent Interest Income / Interest Expense line merely to mean zero, update the fixture to contain an explicit zero line. Do not weaken production completeness rules to keep a synthetic fixture convenient.

---

## Task 3 — Make balance-sheet reformulation period-complete

**Files:**
- Modify: `core/model/classification.py`
- Modify: `core/tests/test_classification.py`
- Modify: `core/tests/test_reference_integrity.py` if needed

### Detail rows

Every non-subtotal balance-sheet detail row used by `reformulate_balance_sheet()` must contain an explicit value for every modeled period.

Replace:

```python
def _val(item: LineItem, period: date) -> float:
    v = item.values.get(period)
    return float(v) if v is not None else 0.0
```

with the shared `required_period_value()` path.

Inside the classification aggregation loop use a contextual field string, for example:

```python
value = required_period_value(
    item,
    pd,
    field=f"balance_sheet detail {line_identity(item).key()}",
)
totals[decision.category][j] += value
```

A detail row may explicitly contain zero. It may not omit the period.

### Reported totals

Preserve **whole-line optionality** of:

```text
total_assets
total_liabilities
total_equity
```

but change `_optional_total()` semantics:

```text
line not resolved at all
    -> tuple(None, None, ...)

line resolved
    -> every modeled period required
```

Do not let a resolved Total Assets / Total Liabilities / Total Equity row use zero for a missing period.

### TDD

- [ ] Detail row missing one modeled period -> `MissingHistoricalValueError`.
- [ ] Detail row containing explicit `0.0` -> accepted.
- [ ] Total Assets line absent entirely -> current optional behavior preserved.
- [ ] Total Assets line present but one period missing -> fail.
- [ ] Total Liabilities line present but one period missing -> fail.
- [ ] Total Equity line present but one period missing -> fail.
- [ ] A complete balance sheet still produces the same category totals and reformulation values as before.

Do not rely only on the later reconciliation-gap check for completeness.

---

## Task 4 — Fix classification Unicode-apostrophe normalization

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

Current `_norm()` still has the stale tuple:

```python
("'", "'", "`")
```

Replace it with deliberate typographic normalization consistent with the canonical line resolver:

```python
for ch in ("\u2018", "\u2019", "`", "´"):
    s = s.replace(ch, "'")
```

Add regressions showing straight and curly apostrophe spellings behave consistently for classification / explicit label override matching where applicable.

Do not add fuzzy matching or broader punctuation heuristics.

---

## Task 5 — Stop cash-flow checksum validation from inventing zeros

**Files:**
- Modify: `core/data/validators.py`
- Test: existing validator / trainer tests; create a focused test file only if no suitable validator test location exists

`validate_cash_flow()` currently computes:

```python
total = sum(float(_val_item(x, period) or 0) for x in (cfo, cfi, cff))
```

When all four cash-flow summary lines are found, a missing period value on CFO / CFI / CFF must make that period fail validation rather than act as zero.

Use semantics equivalent to:

```python
values = [_val_item(x, period) for x in (cfo, cfi, cff)]
net_value = _val_item(net, period)
if any(value is None for value in values) or net_value is None:
    ok = False
else:
    total = sum(float(value) for value in values)
    ok = abs(total - float(net_value)) <= 1.0
```

Preserve the existing behavior when the summary-line set itself is not available; do not broaden the line-identification heuristic in this checkpoint.

### TDD

- [ ] Complete cash-flow summary passes when it reconciles.
- [ ] Explicit zero CFI/CFF is accepted.
- [ ] Missing CFI period fails that period.
- [ ] `None` CFF period fails that period.
- [ ] Missing net-change period fails that period.

---

## Task 6 — End-to-end no-fabrication regressions

**Files:**
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`
- Test: `core/tests/test_earnings_quality.py`

Add end-to-end tests proving the completeness boundary exists even when downstream optional modules are absent.

### Mandatory regression: missing Net Income with no CFO

Construct financials where:

```text
Net Income line resolves
one modeled-period Net Income value is missing
operating cash-flow line is absent
```

Previously the Earnings Quality module was omitted and `compute_anchor()` could silently convert missing Net Income to zero.

Now:

```python
with pytest.raises(MissingHistoricalValueError, match="net_income"):
    build_training_workbook(...)
```

must fail.

### Mandatory regression: missing BS detail with reported totals absent

Construct a balance sheet with no Total Assets / Total Liabilities / Total Equity rows and one classified detail line missing a modeled-period value.

Previously the missing detail could become zero and no reported-total gap existed to catch it.

Now the reformulation/build must fail with `MissingHistoricalValueError`.

### Preservation

Also prove:

- [ ] explicit zero source values continue through formulas normally;
- [ ] a complete demo still builds unchanged;
- [ ] Step 9A `#N/A` behavior remains intact;
- [ ] normalization and classification judgment composition remains intact.

---

## Task 7 — Documentation and verification

**Files:**
- Modify: `RESULT.md`
- Modify: `README-HK-TRAINER.md` only if it describes missing historical periods as zero/defaulted
- Modify: `skills/bav-trainer/SKILL.md` only if it describes missing historical periods as zero/defaulted
- Modify: `IMPLEMENTATION.md` status only after all tests pass
- Do not modify: `TARGET.md`

Update `RESULT.md` with explicit evidence:

```text
- historical core IS lines are required and period-complete
- missing period value is distinct from explicit numeric zero
- supplied BS detail rows are period-complete
- optional reported BS totals remain optional as whole lines, but complete if present
- cash-flow checksum no longer treats missing component periods as zero
- Step 9A quality #N/A semantics preserved
- base 30 / 141 preserved
- normalization 34 / 161 preserved
```

Do not claim all source availability problems are solved beyond this explicit scope. If any historical code path still performs a missing-value-to-zero conversion, list it under `Unresolved` rather than writing `Unresolved: none`.

### Focused tests

Run:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
```

Then:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count; do not prestate it.

### Demo verification

Base:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required:

```text
30 schedule groups
141 practice cells
0 correct / 0 incorrect / 141 blank
```

Normalization:

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

Required:

```text
34 schedule groups
161 practice cells
0 correct / 0 incorrect / 161 blank
```

Verify CLI:

```bash
PYTHONPATH=. python -m core --help
```

Public commands remain:

```text
ingest
build
check
list
```

GitHub currently has no attached CI status for the implementation branch. Describe verification as local unless CI is separately added.

---

## Definition of done

Step 9A.3 is complete only when:

1. Revenue, Net Income, Pretax Income, Tax Expense, Interest Expense, and Interest Income are explicit required historical-core lines.
2. Every modeled period of each required core income line must contain a supplied numeric value.
3. Explicit zero remains valid and is not confused with missing data.
4. No required core income period is silently converted to zero.
5. Every supplied non-subtotal balance-sheet detail row is period-complete.
6. Optional reported BS totals remain optional as whole lines but are period-complete when present.
7. Cash-flow reconciliation does not substitute zero for missing periods on present summary lines.
8. Classification label normalization handles curly apostrophes consistently.
9. Missing Net Income fails even when CFO is absent and Earnings Quality is not active.
10. Missing BS detail fails even when reported BS totals are absent.
11. Step 9A `#N/A` denominator behavior remains unchanged.
12. Base demo remains 30 families / 141 practice cells.
13. Normalization demo remains 34 families / 161 practice cells.
14. Full test suite passes.
15. `TARGET.md` is unchanged.
16. Working-capital interpretation, forecasting, and valuation have not begun.

After completing Step 9A.3, stop and report changed files, exact test output, demo build/check/list output, and any remaining missing-value fallback found during implementation. Do not proceed to the next curriculum feature and do not commit or push.