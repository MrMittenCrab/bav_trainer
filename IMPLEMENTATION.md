# Step 9A.4 — Historical DuPont Undefined-Ratio Hardening

> **Status:** Step 9A.4 complete. See `RESULT.md` for verification evidence (197 passed; base 30/141; normalization 34/161; DuPont zero denominators → `#N/A` / `NA()`). Do not commit or push from this checkpoint unless the user requests it.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `fea4b384495e9cc6d5ae6359a1e10ad7c7dc5618` (`Step 9.3`, Step 9A.3 complete). Implement only Step 9A.4 below using red/green TDD. Preserve Step 8 classification/normalization, the trusted-workbook boundary, Step 9A earnings-quality diagnostics, and Step 9A.3 historical source-completeness rules. Do not begin working-capital interpretation, quality scoring, forecasting, valuation, ROU/deferred-tax alternative modeling, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Stop the active historical DuPont model from representing mathematically undefined ratios as numeric zero. Zero numerators remain valid zero results when the denominator is nonzero; zero denominators produce Excel/Python `#N/A`, and dependent DuPont metrics propagate that undefined state instead of manufacturing apparently meaningful profitability or leverage values.

**Architecture:** Introduce one shared historical-ratio sentinel/helper that can be used by both Step 9A earnings-quality ratios and the core DuPont engine without circular imports. Keep source completeness, formula families, workbook layout, semantic component identities, and Formula Check unchanged. Change only denominator-zero semantics and dependent-ratio propagation on the existing active historical surface.

**Tech Stack:** Python, pytest, openpyxl, existing `AnchorMetrics`, `HistoricalSeries`, `ReferenceModelBuilder`, `SemanticMap`, `historical_expected`, `check_workbook`, and the existing `#N/A` Check behavior established in Step 9A.2.

**Spec:** `TARGET.md`, especially historical accounting correctness, BAV/DuPont methodology, accounting consistency, research diagnostics, the rule against invented historical inputs, and the requirement that formula correctness reflect economically meaningful model logic rather than convenient numeric defaults.

---

## Review of commit `fea4b384`

Step 9A.3 is implemented coherently:

- required historical income lines are explicit and period-complete;
- supplied balance-sheet detail rows are period-complete;
- optional reported BS totals remain optional as whole lines but complete when present;
- cash-flow checksum validation no longer invents zero for missing periods;
- explicit numeric zero remains distinct from missing data;
- the base workbook remains 30 families / 141 practice cells;
- the normalization workbook remains 34 families / 161 practice cells;
- `RESULT.md` records 195 locally passing tests;
- GitHub has no attached CI status.

The new completeness boundary is suitable for proceeding, but one active historical-model defect should be fixed before adding interpretation on top of the ratios.

### Blocking semantic issue — active DuPont zero denominators still become numeric zero

`core/model/financial_math.py` still contains denominator guards such as:

```python
nopat[0] / revenues[0] if revenues[0] else 0
rnoa = nopat[i] / avg(noa, i) if avg(noa, i) else 0
cod = niat[i] / avg(net_debt, i) if avg(net_debt, i) else 0
flev = avg(net_debt, i) / avg(equity, i) if avg(equity, i) else 0
actual = ni[i] / avg(equity, i) if avg(equity, i) else 0
revenues[i] / revenues[i - 1] - 1 if revenues[i - 1] else 0
```

The generated `ALT DuPont` formulas mirror this with `IF(denominator=0,0,...)`.

A zero denominator does not imply a 0% return, 0% growth rate, 0% cost of debt, or zero leverage ratio. These values are undefined. Step 9A.2 already established the correct product convention for undefined ratios: Python expected value `"#N/A"` and Excel `NA()`.

The current behavior can therefore teach a false economic conclusion. For example:

```text
Average Net Debt = 0
Net Interest After Tax = 10
```

currently reports:

```text
After-tax CoD = 0%
```

rather than undefined. That fabricated 0% then contaminates Spread and decomposed ROE.

### Documentation inconsistency exposed by Step 9A.3

`core/engine/component_catalog.py` still tells the learner:

```text
Missing optional interest lines are treated as zero.
```

Step 9A.3 deliberately changed the historical-core contract: Interest Expense and Interest Income are required explicit source lines, with explicit numeric zero when the economic amount is zero. The hint must no longer state the old behavior.

Step 9A.4 fixes these two active-surface issues only.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all current visible sheets and component families.
- Preserve base demo surface at 30 families / 141 practice cells.
- Preserve normalization demo surface at 34 families / 161 practice cells.
- Preserve Step 8 judgment behavior and treatment-conditioned Check.
- Preserve Step 9A earnings-quality formulas and applicability gating.
- Preserve Step 9A.3 required-source and period-completeness rules.
- Explicit zero numerator with a nonzero denominator is a valid numeric `0.0` ratio.
- Zero denominator produces the undefined-ratio sentinel `#N/A`; never numeric `0.0` merely to avoid division by zero.
- First-period non-applicability remains `None` where a metric requires a prior period.
- `Spread` and decomposed ROE must propagate `#N/A` when required upstream ratios are undefined.
- Do not convert source facts, balance-sheet values, or non-ratio accounting amounts to `#N/A` merely because their value is zero.
- Do not alter the existing effective-tax-rate convention in this checkpoint. Effective-tax/NOPAT propagation is a separate accounting-design issue and is not required to fix the DuPont denominator defect.
- Do not change the dormant deferred forecast/scenario system in this checkpoint.
- Do not add working-capital interpretation, thresholds, automatic good/bad labels, forecasting, valuation, scenarios, Hint/Reveal, VBA, or free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Centralize the undefined-ratio sentinel

**Files:**
- Create: `core/model/ratio_values.py`
- Modify: `core/model/earnings_quality.py`
- Test: `core/tests/test_earnings_quality.py`
- Test: `core/tests/test_reference_integrity.py`

Create:

```python
from __future__ import annotations

UNDEFINED_RATIO = "#N/A"


def ratio_or_na(numerator: float, denominator: float) -> float | str:
    """Return a historical ratio, or #N/A when its denominator is zero."""
    if denominator == 0.0:
        return UNDEFINED_RATIO
    return float(numerator) / float(denominator)
```

Do not add epsilon/tolerance behavior. Historical Excel formulas test exact zero denominators, so Python must use the same exact-zero convention.

Move the shared sentinel ownership out of `core/model/earnings_quality.py`:

```python
from .ratio_values import UNDEFINED_RATIO, ratio_or_na
```

Migrate the two Step 9A ratio calculations to `ratio_or_na()` without changing their behavior:

```python
cash_conversion_ratio = CFO / Net Income
accrual_ratio = Total Accruals / Average Total Assets
```

Required preservation:

```text
numerator 0, denominator 10  -> 0.0
denominator 0                -> "#N/A"
first-period accrual ratio   -> None
```

### TDD

- [ ] Existing Step 9A zero-denominator tests remain green.
- [ ] Existing explicit-zero numerator tests remain green.
- [ ] Add a direct/public-caller regression proving `ratio_or_na(0.0, 10.0) == 0.0` and denominator zero yields `#N/A` through an actual model caller; do not add a CLI surface for the helper.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
```

---

## Task 2 — Apply undefined semantics to Python DuPont calculations

**Files:**
- Modify: `core/model/financial_math.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py` if an existing DuPont test location is more suitable

Import:

```python
from .ratio_values import UNDEFINED_RATIO, ratio_or_na
```

`AnchorMetrics.dupont` already permits:

```python
dict[str, list[float | str | None]]
```

Keep that interface.

### NOPAT Margin

For every fiscal period:

```python
margin = ratio_or_na(nopat[i], revenues[i])
```

Required:

```text
NOPAT = 0, Revenue = 100 -> 0.0
Revenue = 0             -> #N/A
```

### Sales Growth

For `i > 0`:

```python
base = ratio_or_na(revenues[i], revenues[i - 1])
sales_growth = UNDEFINED_RATIO if base == UNDEFINED_RATIO else base - 1.0
```

Required:

```text
prior Revenue = 0 -> #N/A
current Revenue = 0, prior Revenue != 0 -> -100%
```

The first period remains `None` because there is no prior comparable year.

### RNOA

For `i > 0`:

```python
average_noa = avg(noa, i)
rnoa = ratio_or_na(nopat[i], average_noa)
```

Zero average NOA -> `#N/A`.

### After-tax Cost of Debt

For `i > 0`:

```python
average_net_debt = avg(net_debt, i)
cod = ratio_or_na(niat[i], average_net_debt)
```

Zero average Net Debt -> `#N/A`.

### FLEV

For `i > 0`:

```python
average_net_debt = avg(net_debt, i)
average_equity = avg(equity, i)
flev = ratio_or_na(average_net_debt, average_equity)
```

Zero average Equity -> `#N/A`.

### Actual ROE

For `i > 0`:

```python
actual = ratio_or_na(ni[i], average_equity)
```

Zero average Equity -> `#N/A`.

### Dependent metrics

Do not attempt arithmetic on `#N/A` strings.

Use explicit propagation:

```python
if rnoa == UNDEFINED_RATIO or cod == UNDEFINED_RATIO:
    spread = UNDEFINED_RATIO
else:
    spread = rnoa - cod

if (
    rnoa == UNDEFINED_RATIO
    or flev == UNDEFINED_RATIO
    or spread == UNDEFINED_RATIO
):
    decomposed = UNDEFINED_RATIO
else:
    decomposed = rnoa + flev * spread
```

The dependency semantics are therefore:

```text
undefined RNOA -> undefined Spread -> undefined decomposed ROE
undefined CoD  -> undefined Spread -> undefined decomposed ROE
undefined FLEV -> undefined decomposed ROE
```

`Actual ROE` is independently calculated and may remain numeric even if decomposed ROE is undefined, provided its own denominator is nonzero.

### Historical average CoD

`cod_series` must no longer assume every comparable-period CoD is numeric.

Only numeric CoD observations may enter the existing dormant historical-average-CoD scalar:

```python
numeric_cod = [
    value
    for value in cod_series
    if isinstance(value, (int, float))
]
```

Preserve the current dormant fallback behavior when no numeric CoD exists. Do not redesign the deferred forecasting architecture in this checkpoint.

### TDD

Add focused Python-side regressions for:

- [ ] NOPAT Margin with zero Revenue -> `#N/A`.
- [ ] Sales Growth with zero prior Revenue -> `#N/A`.
- [ ] Sales Growth with zero current Revenue and nonzero prior Revenue -> `-1.0`.
- [ ] RNOA with zero average NOA -> `#N/A`.
- [ ] After-tax CoD with zero average Net Debt -> `#N/A`.
- [ ] FLEV with zero average Equity -> `#N/A`.
- [ ] Actual ROE with zero average Equity -> `#N/A`.
- [ ] Spread propagates undefined RNOA or CoD.
- [ ] Decomposed ROE propagates undefined RNOA / CoD / FLEV.
- [ ] Zero numerator with nonzero denominator remains numeric zero for RNOA, CoD, FLEV where mathematically applicable, and Actual ROE.
- [ ] First-period non-applicable metrics remain `None` exactly as before.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "dupont or rnoa or flev or roe or sales_growth or nopat_margin or cost_of_debt" -v
```

---

## Task 3 — Make Excel DuPont formulas use `NA()` for zero denominators

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

Change only the historical `ALT DuPont` denominator guards.

### Sales Growth

Replace the zero fallback:

```excel
=IF(PriorRevenue=0,0,CurrentRevenue/PriorRevenue-1)
```

with:

```excel
=IF(PriorRevenue=0,NA(),CurrentRevenue/PriorRevenue-1)
```

### NOPAT Margin

Replace:

```excel
=IF(Revenue=0,0,NOPAT/Revenue)
```

with:

```excel
=IF(Revenue=0,NA(),NOPAT/Revenue)
```

### RNOA

Replace the average-NOA zero branch with `NA()`.

### After-tax CoD

Replace the average-Net-Debt zero branch with `NA()`.

### FLEV

Replace the average-Equity zero branch with `NA()`.

### Actual ROE

Replace the average-Equity zero branch with `NA()`.

### Spread / decomposed ROE

Keep their direct formulas:

```text
Spread = RNOA - After-tax CoD
ROE    = RNOA + FLEV * Spread
```

Excel will naturally propagate `#N/A` from upstream cells. Do not wrap these formulas in `IFERROR(...,0)` or otherwise convert errors back to zero.

### First-period behavior

Preserve existing first-period applicability:

- NOPAT Margin remains an active first-period formula.
- Sales Growth / RNOA / CoD / Spread / FLEV / decomposed ROE / Actual ROE remain non-applicable in the first fiscal period where currently designed.

### TDD

- [ ] Assert each denominator-guarded Answer-Key formula uses `NA()` rather than `0` in its zero-denominator branch.
- [ ] Assert normal nonzero-denominator demo formulas are otherwise unchanged.
- [ ] Assert formula family counts and coordinates do not change.

---

## Task 4 — Prove Formula Check handles historical `#N/A` ratios correctly

**Files:**
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_trainer.py` or reuse existing cached-value injection helpers
- Modify: `core/tests/test_normalization.py` only if the existing helper for cached Excel errors is intentionally shared there; prefer moving generic test support rather than duplicating production behavior

Step 9A.2 already proved `check_workbook()` can compare cached Excel `#N/A` against an expected `#N/A` for earnings-quality formulas. Add equivalent historical-DuPont coverage so this behavior cannot regress by family type.

Required regressions:

### Exact formula

1. Build a fixture producing one undefined historical DuPont ratio.
2. Enter the exact Answer-Key formula into that Trainer practice cell.
3. Run Check.
4. Require the cell to become green.

### Equivalent formula with cached `#N/A`

1. Put a structurally different formula into the same practice cell.
2. Inject cached Excel value `#N/A` using the existing test mechanism.
3. Run Check.
4. Require green.

### Fabricated numeric zero

1. Put an equivalent-looking formula/cached result that yields numeric `0.0` where expected is `#N/A`.
2. Run Check.
3. Require red.

The Check remains non-disclosing; do not print expected values in CLI output.

---

## Task 5 — Correct learner-facing historical ratio hints

**Files:**
- Modify: `core/engine/component_catalog.py`
- Test: `core/tests/test_reference_integrity.py` or a catalog-focused existing test

### Remove stale Step 9A.3 contradiction

For `net_interest_fy`, remove:

```text
Missing optional interest lines are treated as zero.
```

Replace it with a statement consistent with the current source contract, for example:

```text
Use the explicitly supplied Interest Expense and Interest Income lines with the model's sign convention.
```

Do not imply that absent interest lines are automatically zero.

### Add denominator semantics to ratio hints

Where concise and useful, add one final hint to the denominator-sensitive families:

```text
A zero denominator makes this ratio undefined (#N/A), not 0%.
```

Applicable families:

- Sales Growth
- NOPAT Margin
- RNOA
- After-tax CoD
- FLEV
- Actual ROE

For Spread and decomposed ROE, state instead that an undefined required upstream ratio propagates into the result.

Keep hints concise. Do not turn Notes into accounting essays.

---

## Task 6 — Regression and surface preservation

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after implementation and verification
- Modify: `README-HK-TRAINER.md` only if an existing statement explicitly documents the old zero-denominator behavior
- Do not modify: `TARGET.md`

Run focused suites first:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Then the remaining existing integrity suites:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_validators.py -v
```

Then:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count. Do not hard-code an expected new total before running the tests.

### Base build

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required unchanged surface:

```text
141 practice cells
0 correct / 0 incorrect / 141 blank
30 schedule groups
```

### Normalization build

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

Required unchanged surface:

```text
161 practice cells
0 correct / 0 incorrect / 161 blank
34 schedule groups
```

### CLI

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

---

## Task 7 — Update checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status line after all verification passes
- Do not modify: `TARGET.md`

`RESULT.md` must record:

- actual full-suite test count;
- source-completeness behavior from Step 9A.3 remains green;
- Step 9A earnings-quality `#N/A` behavior remains green;
- Sales Growth zero denominator -> `#N/A`;
- NOPAT Margin zero denominator -> `#N/A`;
- RNOA zero denominator -> `#N/A`;
- After-tax CoD zero denominator -> `#N/A`;
- FLEV zero denominator -> `#N/A`;
- Actual ROE zero denominator -> `#N/A`;
- Spread / decomposed ROE undefined propagation -> pass;
- explicit zero numerator with nonzero denominator -> numeric zero preserved;
- Formula Check exact/equivalent `#N/A` behavior -> pass;
- fabricated numeric zero where `#N/A` expected -> rejected;
- stale optional-interest hint removed;
- base 30 / 141 preserved;
- normalization 34 / 161 preserved;
- `TARGET.md` unchanged;
- no working-capital interpretation, forecasting, or valuation introduced.

Do not report `Unresolved: none` unless no new active historical-surface issue is found during implementation.

It is acceptable to keep these explicitly deferred items listed if still present:

- effective-tax-rate zero-denominator convention and any downstream NOPAT implications;
- dormant deferred-forecast defaults/fallbacks;
- working-capital/driver interpretation;
- quality scoring;
- forecasting and valuation.

---

## Definition of done

Step 9A.4 is complete only when all of the following are true:

1. No active DuPont ratio uses numeric `0.0` solely because its denominator is zero.
2. Zero numerator with nonzero denominator still produces a legitimate numeric `0.0`.
3. Sales Growth uses `#N/A` when prior Revenue is zero.
4. NOPAT Margin uses `#N/A` when Revenue is zero.
5. RNOA uses `#N/A` when average NOA is zero.
6. After-tax CoD uses `#N/A` when average Net Debt is zero.
7. FLEV and Actual ROE use `#N/A` when average Equity is zero.
8. Spread propagates undefined RNOA or CoD.
9. Decomposed ROE propagates undefined RNOA, CoD/Spread, or FLEV.
10. Python expected values and Excel `NA()` formulas agree.
11. Formula Check accepts exact and equivalent cached `#N/A` results and rejects fabricated numeric zero.
12. Step 9A earnings-quality behavior remains unchanged.
13. Step 9A.3 source completeness remains unchanged.
14. The net-interest hint no longer claims absent interest lines are automatically zero.
15. Base surface remains 30 families / 141 practice cells.
16. Normalization surface remains 34 families / 161 practice cells.
17. Full test suite passes.
18. `TARGET.md` is unchanged.
19. Working-capital interpretation, forecasting, and valuation have not begun.

After completing Step 9A.4, stop and report changed files, exact test output, demo build/check/list output, and any new active historical-model issue found during implementation. Do not proceed to the next curriculum feature and do not commit or push.