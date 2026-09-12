# Step 9A.2 — Undefined-Ratio and Net-Income Source Hardening

> **Status:** Step 9A.2 complete. See `RESULT.md` for verification evidence (188 passed; base 30/141; normalization 34/161; zero denominators → `#N/A` / `NA()`). Do not commit or push from this checkpoint unless the user requests it.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `0ca165067c049106c8ad12018eaac9acca5cfffc` (`Step 9A.1`). Implement only Step 9A.2 below using red/green TDD. Preserve the Step 8 classification/normalization workflow, the trusted-workbook boundary, and the Step 9A earnings-quality schedule. Do not begin working-capital interpretation, quality scoring, research-writing evaluation, forecasting, valuation, ROU/deferred-tax alternative modeling, or later Step 9/10 work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Remove the last misleading numeric fallbacks in Step 9A. Zero denominators must produce an explicitly undefined ratio rather than a fabricated `0.0`, and reported Net Income used by earnings-quality diagnostics must be explicitly supplied for every modeled period instead of relying on `compute_anchor()`'s legacy missing-value fallback.

**Architecture:** Keep the existing Step 9A schedule and component families. Represent mathematically undefined active ratios with the literal expected value `#N/A` and Excel `NA()`, because active SemanticMap components may not have `expected_value=None`. Continue using `None` only for genuinely non-applicable first-period comparable metrics that have no practice component. Resolve and validate reported Net Income directly inside the earnings-quality model, then require it to agree with `anchor.historical.net_income`.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `StandardizedFinancials`, `LineItem`, `AnchorMetrics`, `SemanticMap`, `ReferenceModelBuilder`, `check_workbook`, and OOXML cached-value handling.

**Spec:** `TARGET.md`, especially “No invented historical inputs,” formula correctness, accounting competence, historical model auditability, and the requirement that diagnostics teach economically correct meanings rather than mechanically convenient numbers.

---

## Review of commit `0ca16506`

Step 9A.1 correctly closes the missing-CFO / missing-Total-Assets fabrication path:

- a completely absent CFO line still omits the module;
- a resolved but period-incomplete CFO line fails;
- a completely absent Total Assets line still omits only the scaled extension;
- a resolved but period-incomplete Total Assets line fails;
- explicitly supplied numeric zero remains distinguishable from missing data;
- the Step 9A demo surface remains 30 families / 141 practice cells without normalization and 34 / 161 with normalization;
- `RESULT.md` records 186 passing local tests;
- GitHub still has no attached CI status.

Two issues remain before moving to the interpretive quality layer.

### Issue 1 — zero denominators are being taught as a numeric zero ratio

Current Step 9A conventions are:

```text
Net Income = 0           -> Cash Conversion Ratio = 0.0
Average Total Assets = 0 -> Accrual Ratio = 0.0
```

Those are not valid ratio values. Division by zero is undefined. A learner seeing `0.00x` or `0.0%` is being taught a false economic result rather than an unavailable ratio.

Correct behavior:

```text
Net Income = 0           -> Cash Conversion Ratio = #N/A
Average Total Assets = 0 -> Accrual Ratio = #N/A
```

Do not use `0.0`, infinity, an arbitrary cap, or a quality label.

### Issue 2 — reported Net Income completeness is still inherited from a legacy zero fallback

`compute_earnings_quality_series()` reads:

```python
ni = float(anchor.historical.net_income[j])
```

but `compute_anchor()` currently obtains historical values through `_val()`, which converts a missing period value to `0.0`.

Normal `build_training_workbook()` source validation already catches many malformed Net Income inputs, but the earnings-quality model itself should not depend on that outer gate for its “no invented historical inputs” invariant. Direct model use must also fail closed.

Step 9A.2 validates the reported Net Income line explicitly inside the quality model and verifies that the supplied values agree with the supplied `AnchorMetrics`.

### Test-quality cleanup

The Step 9A.1 availability matrix contains broad `pytest.raises(Exception)` assertions for malformed Total Assets. Replace these with `ValueError` or a more specific existing exception. A regression should not pass because of an unrelated exception type.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve the existing Step 9A definitions:
  - Cash Conversion Ratio = CFO / Reported Net Income;
  - Total Accruals = Reported Net Income − CFO;
  - Accrual Ratio = Total Accruals / Average Total Assets.
- Preserve source-line availability gating:
  - no CFO line -> no Earnings Quality module;
  - no Total Assets line -> core CFO diagnostics only.
- Preserve fail-closed completeness for resolved CFO and Total Assets lines.
- Add the same explicit completeness rule for reported Net Income used by Step 9A.
- An explicitly supplied numeric zero remains valid source data.
- A zero denominator does **not** imply a zero ratio.
- Use `#N/A` only for mathematically undefined active ratios.
- Keep first-period Average Total Assets / Accrual Ratio as structurally non-applicable (`None` in the Python series, no comparable practice component for FY1).
- Do not add thresholds, traffic lights, “good/bad” quality labels, scores, or investment conclusions.
- Do not add working-capital interpretation yet.
- No forecasting, valuation, scenario engine, Hint/Reveal, VBA, or free-form grading.
- Formula Check remains one workbook-wide, non-disclosing action.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Add an explicit undefined-ratio representation

**Files:**
- Modify: `core/model/earnings_quality.py`
- Modify: `core/tests/test_earnings_quality.py`

Add one module-level constant:

```python
UNDEFINED_RATIO = "#N/A"
```

Change the dataclass types to permit the sentinel where an active ratio is undefined:

```python
@dataclass(frozen=True)
class EarningsQualitySeries:
    operating_cash_flow: tuple[float, ...]
    cash_conversion_ratio: tuple[float | str, ...]
    total_accruals: tuple[float, ...]
    average_total_assets: tuple[float | None, ...]
    accrual_ratio: tuple[float | str | None, ...]
```

Do not use `None` for an active zero-denominator ratio because `SemanticMap.validate_complete()` treats `expected_value=None` as a failed build. `None` remains reserved for the first period of comparable asset-scaled metrics, for which no component is created.

### Required semantics

```text
CFO=80, NI=100             -> cash conversion 0.8
CFO=0, NI=100              -> cash conversion 0.0
CFO=80, NI=0               -> cash conversion "#N/A"
CFO=0, NI=0                -> cash conversion "#N/A"

Accruals=30, Avg Assets=300 -> accrual ratio 0.10
Accruals=0, Avg Assets=300  -> accrual ratio 0.0
Avg Assets=0                -> accrual ratio "#N/A"
```

The numerator may legitimately be zero. Only the denominator controls undefined-ratio behavior.

### TDD

- [ ] Replace the existing zero-Net-Income `0.0` assertion with `UNDEFINED_RATIO`.
- [ ] Replace the existing zero-average-assets `0.0` assertion with `UNDEFINED_RATIO`.
- [ ] Add explicit zero-numerator/nonzero-denominator cases that still return numeric `0.0`.
- [ ] Run the focused tests red before production changes.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -k "zero or undefined or denominator" -v
```

---

## Task 2 — Make the Python earnings-quality series mathematically correct

**Files:**
- Modify: `core/model/earnings_quality.py`
- Test: `core/tests/test_earnings_quality.py`

Change:

```python
conversion.append(0.0 if ni == 0.0 else cfo / ni)
```

to:

```python
conversion.append(
    UNDEFINED_RATIO if ni == 0.0 else cfo / ni
)
```

Change:

```python
if average == 0.0:
    ratios.append(0.0)
else:
    ratios.append(accruals[j] / average)
```

to:

```python
if average == 0.0:
    ratios.append(UNDEFINED_RATIO)
else:
    ratios.append(accruals[j] / average)
```

Do not change Total Accruals. `Net Income - CFO` remains well-defined when either input is explicitly zero.

Do not convert `#N/A` back into a numeric value anywhere in `historical_expected.py` or Check.

---

## Task 3 — Require explicitly supplied reported Net Income

**Files:**
- Modify: `core/model/earnings_quality.py`
- Modify: `core/tests/test_earnings_quality.py`

Inside `compute_earnings_quality_series()`, resolve reported Net Income directly:

```python
net_income_item = resolve_line(
    financials.income_statement,
    "net_income",
    required=True,
).item
assert net_income_item is not None
```

Build an explicit source series using the existing required-period helper:

```python
net_income_values = [
    _required_period_value(
        net_income_item,
        period,
        concept="net_income",
    )
    for period in periods
]
```

Use `net_income_values[j]` for cash conversion and total accruals rather than silently trusting the AnchorMetrics vector.

Then verify source/anchor consistency before calculations:

```python
for j, source_ni in enumerate(net_income_values):
    anchor_ni = float(anchor.historical.net_income[j])
    if abs(source_ni - anchor_ni) > 1e-9:
        raise ValueError(
            "earnings-quality reported Net Income does not match AnchorMetrics "
            f"for modeled period {periods[j].isoformat()}"
        )
```

The quality layer must not silently combine CFO from one source state with Net Income from a stale or differently computed anchor.

### Required tests

- [ ] Net Income line present but one modeled-period key absent -> `ValueError` containing `net_income` and the period date.
- [ ] Net Income line present with explicit `None` -> same failure.
- [ ] Net Income explicitly `0.0` -> source completeness passes; cash conversion becomes `#N/A`.
- [ ] Deliberately construct an `AnchorMetrics` object/source mismatch (or mutate the source after computing the anchor) -> clear mismatch `ValueError`.
- [ ] Normal complete input remains unchanged numerically.

Do not modify global `compute_anchor()` behavior in this checkpoint. This task makes the Step 9A module independently source-safe without broadening scope into a historical-engine refactor.

---

## Task 4 — Render undefined ratios correctly in Excel

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_earnings_quality.py`

Change Cash Conversion Ratio formulas from:

```excel
=IF(B6=0,0,B5/B6)
```

to:

```excel
=IF(B6=0,NA(),B5/B6)
```

Change Accrual Ratio formulas from:

```excel
=IF(C11=0,0,C8/C11)
```

to:

```excel
=IF(C11=0,NA(),C8/C11)
```

Preserve the existing number formats. Excel error values should visibly show `#N/A`, making the undefined denominator explicit.

When registering quality components, pass the Python expected value unchanged. `SemanticMap` already permits `float | str | None`, and `"#N/A"` is a valid non-None expected value.

### Workbook tests

- [ ] Build a fixture with zero reported Net Income and verify the Answer Key cash-conversion formula contains `NA()` rather than a zero fallback.
- [ ] Build a fixture with zero Average Total Assets and verify the accrual-ratio formula contains `NA()`.
- [ ] Verify normal nonzero demo formulas remain structurally identical except for the denominator guard.
- [ ] Trainer practice cells remain blank yellow.

---

## Task 5 — Verify Formula Check handles `#N/A` without disclosure

**Files:**
- Modify: `core/tests/test_earnings_quality.py`
- Modify production Check code only if a failing regression proves necessary

`_values_match()` already falls back to case-insensitive string comparison when numeric conversion fails. Preserve that behavior.

Add regressions for an active zero-denominator quality component:

### Exact formula

Insert the exact Answer-Key formula containing `NA()` into the Trainer practice cell.

Required:

```text
Check -> correct
```

### Equivalent formula / cached error

Using the existing OOXML cached-value test helper, inject an equivalent formula whose cached result is `#N/A`.

Required:

```text
expected = "#N/A"
cached   = "#N/A"
Check -> correct
```

If the current helper cannot encode an Excel error cached value safely, extend the **test helper** minimally rather than weakening production Check.

### Wrong numeric fallback

Inject:

```excel
=0
```

with cached `0.0` for a zero-denominator ratio.

Required:

```text
Check -> incorrect
```

This proves the new semantics are not merely cosmetic workbook formulas.

---

## Task 6 — Tighten broad exception regressions

**Files:**
- Modify: `core/tests/test_earnings_quality.py`

Replace the Step 9A.1 assertions:

```python
with pytest.raises(Exception):
    ...
```

with at least:

```python
with pytest.raises(ValueError):
    ...
```

Where the production path has a stable meaningful error message, assert it as well.

Do not make tests pass on unrelated runtime errors, assertion failures, or programming exceptions.

This is a test-hardening task only; do not restructure the historical engine to force a particular error source if the build already fails closed correctly.

---

## Task 7 — Documentation and checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `README-HK-TRAINER.md` if it documents zero-denominator conventions
- Modify: `skills/bav-trainer/SKILL.md` if it documents zero-denominator conventions
- Modify: `IMPLEMENTATION.md` status only after verification passes
- Do not modify: `TARGET.md`

Replace any statement that says:

```text
zero Net Income -> cash conversion ratio 0.0
zero Average Total Assets -> accrual ratio 0.0
```

with:

```text
zero Net Income -> cash conversion ratio #N/A (undefined denominator)
zero Average Total Assets -> accrual ratio #N/A (undefined denominator)
```

Record explicitly:

```text
- missing CFO / Total Assets / Net Income are never fabricated as zero
- explicit numeric zero remains a valid supplied historical fact
- zero numerator with nonzero denominator remains a valid 0.0 ratio
- zero denominator produces #N/A, not 0.0
- Step 9A demo surfaces remain unchanged
```

GitHub currently has no attached CI checks for this branch, so continue to label test results as local verification.

---

## Task 8 — Full verification

Run focused quality tests:

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

Run the historical/judgment regression suites:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
```

Then:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing total.

Verify the unchanged Step 9A demo surface:

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
fresh Check: 0 correct / 0 incorrect / 141 blank
```

Verify normalization composition:

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
fresh Check: 0 correct / 0 incorrect / 161 blank
```

Verify CLI remains:

```text
ingest
build
check
list
```

---

## Definition of done

Step 9A.2 is complete only when:

1. Resolved CFO, Total Assets, and reported Net Income lines require explicit values for every modeled period they supply to Step 9A.
2. Missing historical facts are never converted to numeric zero by the earnings-quality module.
3. Explicit numeric zero remains a valid source fact.
4. A zero numerator with a valid nonzero denominator produces numeric `0.0`.
5. A zero Net Income denominator produces `#N/A` Cash Conversion Ratio.
6. A zero Average Total Assets denominator produces `#N/A` Accrual Ratio.
7. Excel Answer Key formulas use `NA()` for zero denominators.
8. Formula Check marks correct `#N/A` formulas/results green and rejects a fabricated numeric-zero fallback.
9. First-period Average Total Assets / Accrual Ratio remain non-applicable rather than active `#N/A` practice cells.
10. Broad `pytest.raises(Exception)` assertions added in Step 9A.1 are removed.
11. Base demo remains 30 families / 141 practice cells.
12. Normalization demo remains 34 families / 161 practice cells.
13. Full test suite passes.
14. `TARGET.md` remains unchanged.
15. Working-capital interpretation, quality scoring, forecasting, and valuation have not begun.

After completing this checkpoint, stop and report changed files and exact verification output. Do not commit or push.
