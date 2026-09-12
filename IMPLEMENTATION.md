# Step 9A.5 — Historical Tax and Normalization Undefined-State Hardening

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `8c7dcb9007c58f5d9cb4b8fc25a6b6ecc9897722` (`Step 9.3`, Step 9A.4 complete). Implement only Step 9A.5 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, Step 9A earnings-quality diagnostics, Step 9A.3 source completeness, and Step 9A.4 DuPont `#N/A` semantics. Do not begin working-capital interpretation, automatic quality scoring, forecasting, valuation, ROU/deferred-tax alternative modeling, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Remove the remaining active historical tax-rate and normalization cases where an undefined or missing source state is silently converted to numeric zero. A zero pretax-income denominator must produce an undefined effective tax rate, dependent tax-effected amounts must propagate that state only when the tax rate is actually needed, and explicitly configured normalization source lines must be complete across every modeled period.

**Architecture:** Reuse the Step 9A.4 `#N/A` sentinel rather than inventing a second undefined-value representation. Widen the historical tax-dependent series to permit `#N/A`, align Python and Excel formulas, and preserve mathematically determinate zero cases: zero net interest needs no tax rate, and a zero pretax normalization adjustment needs no tax rate. Enforce normalization-candidate period completeness both when cases are constructed and when dynamic Check recomputes them from `_CheckContext`.

**Tech Stack:** Python, pytest, openpyxl, existing `ratio_values.py`, `source_values.py`, `AnchorMetrics`, `HistoricalSeries`, `NormalizationSeries`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and existing cached-`#N/A` Check support.

**Spec:** `TARGET.md`, especially **No invented historical inputs**, historical accounting correctness, accounting consistency, earnings normalization, operating/financing reformulation, and the requirement that formula correctness reflect economically meaningful model logic.

---

## Review of commit `8c7dcb90`

Step 9A.4 is implemented coherently:

- active DuPont zero denominators now produce Python `#N/A` and Excel `NA()`;
- undefined RNOA / CoD / FLEV states propagate into dependent DuPont metrics;
- explicit zero numerators with nonzero denominators remain numeric zero;
- Step 9A earnings-quality `#N/A` behavior is preserved;
- base workbook remains 30 families / 141 practice cells;
- normalization workbook remains 34 families / 161 practice cells;
- `RESULT.md` records 197 locally passing tests;
- GitHub has no attached CI status.

Two active historical integrity gaps remain before interpretation should be built on top of these measures.

### Gap 1 — zero Pretax Income still manufactures a 0% effective tax rate

`core/model/financial_math.py` currently computes:

```python
etr = [(-tax[i] / pretax[i]) if pretax[i] else 0.0 for i in range(n)]
```

and `Condensed Financials` mirrors it with:

```excel
=IF(PretaxIncome=0,0,-TaxExpense/PretaxIncome)
```

A zero denominator does not imply a 0% effective tax rate. It is undefined. The fabricated 0% is then used to tax-effect Net Interest and therefore affects NOPAT, historical DuPont ratios, and earnings normalization.

The correct historical convention should match Step 9A.4:

```text
Pretax Income = 0 -> Effective Tax Rate = #N/A
```

However, downstream propagation should remain economically minimal:

```text
Net Interest = 0
ETR = #N/A
-> Net Interest After Tax = 0
```

because no tax rate is needed to tax-effect a zero financing amount.

Likewise:

```text
Pretax Normalization Adjustment = 0
ETR = #N/A
-> After-tax Normalization Adjustment = 0
```

because no adjustment exists to tax-effect.

### Gap 2 — configured normalization source lines can still fabricate missing periods as zero

`core/model/normalization.py` currently contains both:

```python
value = item.values.get(period)
if value is None:
    continue
```

while deciding whether a candidate is nonzero, and later:

```python
reported = items_by_case[case.id].values.get(period)
signed = 0.0 if reported is None else float(reported)
```

A configured normalization candidate with an omitted / `None` modeled-period source value can therefore be suppressed or normalized as if the missing fact were an explicit zero. This violates the source-completeness rule established in Step 9A.3.

Step 9A.5 closes these two active-state gaps only.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all current visible sheets and component families.
- Preserve base demo surface at 30 families / 141 practice cells.
- Preserve normalization demo surface at 34 families / 161 practice cells.
- Preserve Step 8 judgment behavior and treatment-conditioned Check.
- Preserve Step 9A earnings-quality formulas and applicability gating.
- Preserve Step 9A.3 required-source / period-completeness rules.
- Preserve Step 9A.4 DuPont `#N/A` semantics.
- Explicit numeric zero is a supplied fact, not missing data.
- Pretax Income equal to zero makes Effective Tax Rate undefined; do not substitute 0%.
- A zero amount that would otherwise be multiplied by `(1 - tax_rate)` remains zero even when the tax rate is undefined, because no tax-effect estimate is required.
- A nonzero amount requiring an undefined tax rate produces `#N/A` and propagates to dependent values.
- Do not invent a tax rate, statutory rate, prior-year rate, normalized rate, or fallback percentage.
- Normalization candidates remain explicit assumptions; do not infer candidates from labels.
- Every configured normalization source line that survives selector resolution must be complete for every modeled period, even if the case would later be suppressed as all-zero.
- Do not change the dormant deferred forecast/scenario system in this checkpoint.
- Do not add working-capital interpretation, thresholds, automatic good/bad labels, forecasting, valuation, scenarios, Hint/Reveal, VBA, or free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Make Effective Tax Rate undefined when Pretax Income is zero

**Files:**
- Modify: `core/model/financial_math.py`
- Modify: `core/model/ratio_values.py` only if a small propagation helper materially reduces duplication
- Test: `core/tests/test_reference_integrity.py`

### Type contract

Widen the tax-dependent historical series:

```python
@dataclass(frozen=True)
class HistoricalSeries:
    revenue: list[float]
    net_income: list[float]
    pretax_income: list[float]
    tax_expense: list[float]
    effective_tax_rate: list[float | str]
    net_interest: list[float]
    net_interest_after_tax: list[float | str]
    nopat: list[float | str]
```

Widen the corresponding latest-period `AnchorMetrics` fields:

```python
nopat: float | str
effective_tax_rate: float | str
net_interest_after_tax: float | str
```

Do not widen unrelated balance-sheet amounts.

### Effective Tax Rate

Replace the numeric-zero fallback with the shared ratio convention:

```python
etr = [
    ratio_or_na(-tax[i], pretax[i])
    for i in range(n)
]
```

Required behavior:

```text
Tax Expense = 0, Pretax Income = 100   -> 0.0
Tax Expense = -20, Pretax Income = 100 -> 0.20
Pretax Income = 0                       -> #N/A
```

Do not special-case `0/0` as 0%; it remains undefined.

### TDD

- [ ] Zero Pretax Income with zero Tax Expense -> historical ETR `#N/A`.
- [ ] Zero Pretax Income with nonzero Tax Expense -> historical ETR `#N/A`.
- [ ] Zero Tax Expense with nonzero Pretax Income -> numeric `0.0` ETR.
- [ ] Existing ordinary positive/negative Pretax Income cases preserve current signed tax-rate math.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "effective_tax or pretax" -v
```

---

## Task 2 — Propagate undefined ETR through Net Interest After Tax and NOPAT only when needed

**Files:**
- Modify: `core/model/financial_math.py`
- Modify: `core/tests/test_reference_integrity.py`

For every period, derive Net Interest After Tax with this exact semantic rule:

```python
if net_int[i] == 0.0:
    niat_value: float | str = 0.0
elif etr[i] == UNDEFINED_RATIO:
    niat_value = UNDEFINED_RATIO
else:
    niat_value = net_int[i] * (1.0 - float(etr[i]))
```

Then derive NOPAT:

```python
if niat_value == UNDEFINED_RATIO:
    nopat_value: float | str = UNDEFINED_RATIO
else:
    nopat_value = ni[i] + float(niat_value)
```

Do not convert an undefined tax-effected financing amount to zero.

Required examples:

```text
Pretax = 0, Net Interest = 0
-> ETR #N/A
-> Net Interest After Tax 0
-> NOPAT = Net Income

Pretax = 0, Net Interest = 10
-> ETR #N/A
-> Net Interest After Tax #N/A
-> NOPAT #N/A
```

### DuPont propagation

Because NOPAT may now be `#N/A`, update `ratio_or_na()` or the local DuPont caller so an undefined numerator propagates cleanly instead of attempting `float("#N/A")`.

Preferred `ratio_values.py` contract:

```python
def ratio_or_na(
    numerator: float | str,
    denominator: float | str,
) -> float | str:
    if numerator == UNDEFINED_RATIO or denominator == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    if float(denominator) == 0.0:
        return UNDEFINED_RATIO
    return float(numerator) / float(denominator)
```

Keep the exact-zero denominator rule; do not add epsilon behavior.

Required preservation:

- Sales Growth remains independent of NOPAT / ETR.
- NOPAT Margin becomes `#N/A` when NOPAT is `#N/A`.
- RNOA becomes `#N/A` when NOPAT is `#N/A`.
- Spread / decomposed ROE continue to propagate through existing Step 9A.4 logic.
- Actual ROE remains based on Net Income and average Equity and may remain numeric when NOPAT is undefined.

### TDD

- [ ] Undefined ETR + zero Net Interest -> NIAT 0 and numeric NOPAT.
- [ ] Undefined ETR + nonzero Net Interest -> NIAT and NOPAT `#N/A`.
- [ ] Undefined NOPAT propagates into NOPAT Margin and RNOA.
- [ ] Actual ROE remains numeric when its own denominator is valid.
- [ ] Normal ETR periods preserve all previous values.

---

## Task 3 — Align `Condensed Financials` Excel formulas with Python tax semantics

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/engine/component_catalog.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py` if needed

### Source-row contract cleanup

Step 9A.3 made all six historical income concepts required. Reflect that invariant in `_build_condensed()`:

```python
pretax_src = self._resolved_source_row(
    self.fin.income_statement,
    "pretax_income",
    required=True,
)
tax_src = self._resolved_source_row(
    self.fin.income_statement,
    "tax_expense",
    required=True,
)
int_exp_src = self._resolved_source_row(
    self.fin.income_statement,
    "interest_expense",
    required=True,
)
int_inc_src = self._resolved_source_row(
    self.fin.income_statement,
    "interest_income",
    required=True,
)
```

The fallback branches that manufacture `=0` because these rows are absent are no longer reachable under the active historical contract. Remove or simplify them rather than documenting them as supported behavior.

### Effective Tax Rate formula

Generate:

```excel
=IF(PretaxIncome=0,NA(),-TaxExpense/PretaxIncome)
```

Never generate `IF(PretaxIncome=0,0,...)`.

### Net Interest After Tax formula

Generate the workbook equivalent of the Python rule:

```excel
=IF(NetInterest=0,0,IF(ISNA(EffectiveTaxRate),NA(),NetInterest*(1-EffectiveTaxRate)))
```

Do not use `IFERROR(...,0)`.

### NOPAT

Keep:

```excel
=NetIncome+NetInterestAfterTax
```

Excel will naturally propagate `#N/A` when NIAT is undefined.

### Hints

Add concise guidance to the existing component Notes:

- Effective Tax Rate: zero Pretax Income makes the ratio undefined (`#N/A`).
- Net Interest After Tax: a zero Net Interest amount remains zero even if ETR is undefined; otherwise undefined ETR propagates.
- NOPAT: undefined tax-effected Net Interest propagates to NOPAT.

Do not add interpretation beyond the mechanical accounting convention.

### TDD

- [ ] Effective-tax Answer-Key formula uses `NA()` on zero Pretax Income.
- [ ] NIAT formula contains the zero-Net-Interest short-circuit and `ISNA(ETR)` propagation.
- [ ] NOPAT remains a direct dependency on Net Income + NIAT.
- [ ] No active Condensed formula contains an absent-interest `=0` fallback.
- [ ] Formula families / coordinates / counts remain unchanged.

---

## Task 4 — Require normalization candidate period completeness

**Files:**
- Modify: `core/model/normalization.py`
- Modify: `core/tests/test_normalization.py`

Import the shared source-completeness primitive:

```python
from .source_values import required_period_series, required_period_value
```

### Build-time case construction

Replace the current `_line_has_nonzero_value()` missing-as-zero behavior.

Preferred helper:

```python
def _candidate_period_values(
    item: LineItem,
    periods: list[date],
) -> tuple[float, ...]:
    return required_period_series(
        item,
        periods,
        field=f"normalization candidate {line_identity(item).key()}",
    )
```

For every configured candidate:

1. resolve the selector;
2. reject duplicate identity as today;
3. require an explicit value for every modeled period;
4. only then suppress the case if every supplied value is exactly zero.

This means a candidate with four zeros and one missing year must fail, not disappear.

### Dynamic computation

`compute_normalization_series()` must independently require every selected candidate's modeled-period value:

```python
reported = required_period_value(
    items_by_case[case.id],
    period,
    field=f"normalization candidate {case.line_identity}",
)
```

Do not retain:

```python
0.0 if reported is None else float(reported)
```

This second check is required because Formula Check reconstructs minimal cases from `_CheckContext` rather than calling `normalization_cases()` again.

### TDD

- [ ] Configured candidate with one omitted period -> `MissingHistoricalValueError` during case construction/build.
- [ ] Configured candidate with one explicit `None` period -> `MissingHistoricalValueError`.
- [ ] All periods explicitly zero -> candidate still suppressed.
- [ ] Mixed explicit zeros/nonzero values -> case remains active.
- [ ] Dynamic `compute_normalization_series()` independently rejects a missing period in a manually constructed case.
- [ ] Existing duplicate/selector/identity regressions remain green.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_normalization.py -k "missing or complete or zero or candidate" -v
```

---

## Task 5 — Make normalization tax effects respect undefined ETR

**Files:**
- Modify: `core/model/normalization.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/model/historical_expected.py` only if type annotations require widening
- Test: `core/tests/test_normalization.py`

### NormalizationSeries types

Widen only the tax-dependent fields:

```python
@dataclass(frozen=True)
class NormalizationSeries:
    pretax_adjustment: tuple[float, ...]
    after_tax_adjustment: tuple[float | str, ...]
    normalized_nopat: tuple[float | str, ...]
    normalized_net_income: tuple[float | str, ...]
```

### Python calculation

For each period:

```python
if pretax_adj == 0.0:
    after: float | str = 0.0
elif hist.effective_tax_rate[j] == UNDEFINED_RATIO:
    after = UNDEFINED_RATIO
else:
    after = pretax_adj * (1.0 - float(hist.effective_tax_rate[j]))
```

Then:

```python
reported_nopat = hist.nopat[j]
normalized_nopat = (
    UNDEFINED_RATIO
    if reported_nopat == UNDEFINED_RATIO or after == UNDEFINED_RATIO
    else float(reported_nopat) + float(after)
)

normalized_net_income = (
    UNDEFINED_RATIO
    if after == UNDEFINED_RATIO
    else float(hist.net_income[j]) + float(after)
)
```

Required behavior:

```text
ETR #N/A + pretax adjustment 0
-> after-tax adjustment 0
-> normalized Net Income = reported Net Income
-> normalized NOPAT follows reported NOPAT state

ETR #N/A + nonzero pretax adjustment
-> after-tax adjustment #N/A
-> normalized Net Income #N/A
-> normalized NOPAT #N/A
```

Delete the current `hist.effective_tax_rate[j] or 0.0` fallback.

### Excel formula

Change the `Earnings Normalization` after-tax bridge to:

```excel
=IF(PretaxNormalizationAdjustment=0,0,
   IF(ISNA(EffectiveTaxRate),NA(),
      PretaxNormalizationAdjustment*(1-EffectiveTaxRate)))
```

Keep normalized NOPAT / Net Income as direct additions so Excel propagates upstream `#N/A` naturally.

Do not replace errors with zero or a default tax rate.

### TDD

- [ ] Undefined ETR + zero adjustment -> after-tax adjustment 0.
- [ ] Undefined ETR + nonzero adjustment -> after-tax adjustment `#N/A`.
- [ ] Normalized Net Income stays reported when adjustment is zero.
- [ ] Normalized Net Income becomes `#N/A` when a nonzero adjustment cannot be tax-effected.
- [ ] Normalized NOPAT follows the reported-NOPAT undefined state.
- [ ] Answer-Key after-tax normalization formula contains both the zero-adjustment short-circuit and `ISNA(ETR)` guard.
- [ ] Existing ordinary demo normalization values remain unchanged.

---

## Task 6 — Prove Formula Check handles tax-dependent `#N/A` correctly

**Files:**
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_normalization.py`

Use the existing cached-Excel-error injection mechanism established for Step 9A.2 / 9A.4.

### Historical Effective Tax Rate

For a fixture with zero Pretax Income:

1. exact Answer-Key ETR formula -> green;
2. structurally different formula with cached `#N/A` -> green;
3. cached numeric `0.0` -> red.

### Tax-dependent historical amount

For a fixture with zero Pretax Income and nonzero Net Interest:

1. NIAT expected `#N/A`;
2. NOPAT expected `#N/A`;
3. equivalent cached `#N/A` formulas pass;
4. fabricated numeric zero fails.

### Normalization amount

For zero Pretax Income plus a nonzero Non-recurring normalization adjustment:

1. after-tax normalization adjustment expected `#N/A`;
2. normalized Net Income expected `#N/A`;
3. exact/equivalent `#N/A` formulas pass;
4. numeric-zero substitutes fail.

Check output remains aggregate/non-disclosing.

---

## Task 7 — Full regression and checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all verification passes
- Do not modify: `TARGET.md`

Run focused suites:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
```

Then the existing integrity suites:

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_validators.py -v
```

Then:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count; do not invent an expected total in advance.

Verify the ordinary base demo:

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required ordinary-demo surface:

```text
141 practice cells
0 correct / 0 incorrect / 141 blank
30 schedule groups
```

Verify the normalization demo:

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

Required ordinary-demo normalization surface:

```text
161 practice cells
0 correct / 0 incorrect / 161 blank
34 schedule groups
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

Update `RESULT.md` with:

- actual test count;
- zero Pretax Income -> Effective Tax Rate `#N/A` / `NA()`;
- zero Net Interest short-circuit preserved;
- nonzero Net Interest + undefined ETR -> NIAT/NOPAT `#N/A`;
- normalization candidate period completeness enforced;
- zero normalization adjustment short-circuit preserved;
- nonzero normalization adjustment + undefined ETR -> tax-dependent normalization values `#N/A`;
- exact/equivalent Check accepts correct cached `#N/A` and rejects fabricated zero;
- base 30 / 141 preserved;
- normalization 34 / 161 preserved;
- `TARGET.md` unchanged;
- no working-capital interpretation, forecasting, or valuation introduced.

---

## Definition of done

Step 9A.5 is complete only when all of the following are true:

1. Zero Pretax Income never produces a fabricated 0% Effective Tax Rate.
2. Python uses `#N/A` and Excel uses `NA()` for undefined ETR.
3. Zero Net Interest remains a determinate zero after-tax amount even when ETR is undefined.
4. Nonzero Net Interest with undefined ETR produces undefined NIAT and NOPAT.
5. DuPont metrics receiving undefined NOPAT propagate `#N/A` correctly.
6. Every configured normalization candidate is period-complete before all-zero suppression.
7. Dynamic normalization recomputation independently rejects missing candidate-period values.
8. Zero pretax normalization adjustment remains zero even when ETR is undefined.
9. Nonzero pretax normalization adjustment with undefined ETR produces `#N/A`, not a 0%-tax fallback.
10. Formula Check accepts exact/equivalent correct `#N/A` states and rejects numeric-zero substitutes.
11. Ordinary demo outputs remain 30 families / 141 practice cells.
12. Ordinary normalization demo remains 34 families / 161 practice cells.
13. Full test suite passes.
14. `TARGET.md` is unchanged.
15. Working-capital interpretation, quality scoring, forecasting, and valuation have not begun.

After completing Step 9A.5, stop and report changed files, exact test output, demo build/check/list output, and any new active historical-model issue found during implementation. Do not proceed to the next curriculum feature and do not commit or push.
