# Step 9A.1 — Earnings-Quality Source Completeness Hardening

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `3e4be6976d5b24b090a27a1b60fabda8e3bf3a24` (`Step 9`). Implement only the Step 9A.1 hardening below using red/green TDD. Preserve the Step 8A/8B1 classification workflow, Step 8B2 normalization workflow, Step 8B2.2 trusted-workbook boundary, and the Step 9A earnings-quality formulas and workbook surface. Do not begin working-capital interpretation, quality scoring, research-writing evaluation, forecasting, valuation, ROU/deferred-tax alternative modeling, or later Step 9/10 work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Eliminate the remaining invented-input path in Step 9A. A resolved CFO or Total Assets line must contain an explicitly supplied value for every modeled period used by the active earnings-quality schedule; missing period values must fail clearly instead of being silently converted to zero.

**Architecture:** Keep the current line-level availability gating: a completely absent CFO line disables the Earnings Quality module, and a completely absent Total Assets line disables only the asset-scaled extension. Once a source line resolves, however, it is trusted supplied data and must be complete for the modeled periods. Add one small required-period-value helper inside the earnings-quality model and use it for both CFO and Total Assets. Preserve explicit numeric zero as a valid supplied value and preserve the existing Step 9A zero-denominator conventions.

**Tech Stack:** Python, dataclasses, pytest, existing `StandardizedFinancials`, `LineItem`, `ReferenceModelBuilder`, `compute_earnings_quality_series`, Trainer/Answer-Key generation, and workbook-wide Check.

**Spec:** `TARGET.md`, especially “No invented historical inputs,” material/applicable-topic gating, historical model auditability, and the requirement that the Trainer use supplied historical facts rather than fabricated assumptions.

---

## Review of commit `3e4be697`

The main Step 9A implementation is coherent:

- canonical final operating-cash-flow resolution is narrow and explicit;
- the Unicode-apostrophe resolver defect is fixed;
- the module is omitted when the CFO line is absent;
- Total Assets independently gates the asset-scaled extension;
- CFO / Net Income cash conversion, total accruals, average assets, and accrual ratio are separated into auditable formula families;
- trusted-state validation includes `Earnings Quality` populated cells;
- quality practice cells remain compatible with exact and equivalent-formula Check;
- no quality score, arbitrary threshold, forecasting, or valuation logic was added;
- `RESULT.md` records 183 locally passing tests, with the demo at 30 families / 141 cells without normalization and 34 families / 161 cells with normalization.

GitHub has no attached CI status for this commit, so the recorded tests are local verification rather than independent CI evidence.

Two issues remain before moving to the interpretive earnings-quality layer.

### Blocking issue — missing period values are silently invented as zero

`compute_earnings_quality_series()` currently does this for CFO:

```python
raw = cfo_item.values.get(period)
cfo = 0.0 if raw is None else float(raw)
```

and this for Total Assets:

```python
prev = 0.0 if prev_raw is None else float(prev_raw)
cur = 0.0 if cur_raw is None else float(cur_raw)
```

This makes a resolved but incomplete source line economically indistinguishable from an explicitly supplied zero. It violates the Step 9A / `TARGET.md` requirement not to invent historical inputs.

A completely missing source line and a resolved-but-incomplete source line are different states:

```text
CFO line absent entirely
    -> module not applicable / omit Earnings Quality

CFO line resolved but one modeled period is missing
    -> malformed/incomplete supplied source / fail build

Total Assets line absent entirely
    -> keep CFO diagnostics; omit asset-scaled extension

Total Assets line resolved but one modeled period is missing
    -> malformed/incomplete supplied source / fail build
```

Do not silently replace the last two cases with zero and do not silently downgrade an incomplete Total Assets line to “unavailable.”

### Documentation mismatch

`RESULT.md` currently states:

```text
zero average assets → accrual ratio None
```

but the accepted Step 9A convention and implementation are:

```text
zero average assets → accrual ratio 0.0
```

The test suite also asserts `0.0`. Correct the documentation; do not change this denominator convention in Step 9A.1.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve the Step 9A definitions:
  - Cash conversion ratio = CFO / Reported Net Income;
  - Total accruals = Reported Net Income − CFO;
  - Accrual ratio = Total accruals / Average Total Assets.
- Preserve the current model conventions:
  - Net Income exactly zero -> cash conversion ratio `0.0`;
  - Average Total Assets exactly zero -> accrual ratio `0.0`.
- Distinguish **missing** from explicitly supplied numeric zero.
- Do not invent CFO, Total Assets, capex, working-capital movements, or any other historical value.
- Completely absent CFO still disables the entire Earnings Quality module.
- Completely absent Total Assets still disables only Average Total Assets / Accrual Ratio.
- A resolved but period-incomplete CFO or Total Assets line must fail closed.
- Existing Step 8 classification / normalization treatment mechanics remain unchanged.
- Existing trusted-state validation remains fail-closed before grading.
- Formula Check remains non-disclosing and workbook-wide.
- Do not add thresholds, “good/bad” quality labels, traffic lights, or investment conclusions.
- Do not add working-capital interpretation yet.
- Do not add forecasting, valuation, scenario engine, Hint/Reveal, VBA, or free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Add one explicit required-period-value boundary

**Files:**
- Modify: `core/model/earnings_quality.py`
- Test: `core/tests/test_earnings_quality.py`

Create one focused helper in `core/model/earnings_quality.py`:

```python
def _required_period_value(
    item: LineItem,
    period: date,
    *,
    concept: str,
) -> float:
    raw = item.values.get(period)
    if raw is None:
        raise ValueError(
            f"{concept} line {item.label!r} has no supplied value "
            f"for modeled period {period.isoformat()}"
        )
    return float(raw)
```

Import `LineItem` from `core.data.interface`.

Required semantics:

```text
key absent from item.values -> ValueError
key present with None       -> ValueError
key present with 0          -> 0.0 (valid supplied fact)
key present with -0.0       -> -0.0 / numerically zero (valid supplied fact)
nonzero numeric value       -> float(value)
```

Do not use `value or 0`, `.get(..., 0)`, or any equivalent fallback.

### TDD

- [ ] Unit-test `_required_period_value()` indirectly through `compute_earnings_quality_series()`; direct private-helper testing is unnecessary.
- [ ] CFO line with one modeled period omitted -> clear `ValueError` containing `operating_cash_flow` and the missing date.
- [ ] CFO line with one modeled period explicitly `None` -> same failure.
- [ ] CFO line with an explicitly supplied `0.0` -> succeeds and preserves `0.0`.
- [ ] Run the focused tests red before implementation.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -k "missing or incomplete or zero" -v
```

---

## Task 2 — Remove CFO zero fabrication

**Files:**
- Modify: `core/model/earnings_quality.py`
- Test: `core/tests/test_earnings_quality.py`

Replace:

```python
raw = cfo_item.values.get(period)
cfo = 0.0 if raw is None else float(raw)
```

with:

```python
cfo = _required_period_value(
    cfo_item,
    period,
    concept="operating_cash_flow",
)
```

Do not change the line-level gating in `earnings_quality_availability()`:

```text
no resolvable CFO line -> operating_cash_flow=False
```

The stricter completeness rule begins only after the CFO line resolves.

### Required builder behavior

Add an end-to-end regression:

1. create a financials fixture with a resolvable CFO line;
2. delete one modeled-period CFO value;
3. instantiate `ReferenceModelBuilder` or call `build_training_workbook()`;
4. require the build to raise before writing a valid Trainer/Answer-Key pair;
5. assert the error identifies the CFO concept and missing period.

Do not silently omit the Earnings Quality module in this state.

---

## Task 3 — Remove Total Assets zero fabrication

**Files:**
- Modify: `core/model/earnings_quality.py`
- Test: `core/tests/test_earnings_quality.py`

When `total_assets` resolves, every modeled-period asset value used by the active asset-scaled schedule must be explicitly supplied.

Replace:

```python
prev = 0.0 if prev_raw is None else float(prev_raw)
cur = 0.0 if cur_raw is None else float(cur_raw)
```

with required supplied values.

A simple implementation is to resolve all asset values once:

```python
asset_values = [
    _required_period_value(
        assets_item,
        period,
        concept="total_assets",
    )
    for period in periods
]
```

then calculate:

```python
for j in range(1, n):
    average = (asset_values[j - 1] + asset_values[j]) / 2.0
```

### Required semantics

- Total Assets line absent -> existing `None` series and core CFO diagnostics preserved.
- Total Assets line present + complete -> current asset-scaled behavior preserved.
- Total Assets line present + one period absent/None -> fail clearly; do not omit the extension and do not substitute zero.
- Explicit Total Assets `0.0` remains valid supplied data.
- Two explicitly supplied zero Total Assets periods -> Average Total Assets `0.0`, Accrual Ratio `0.0` under the accepted Step 9A denominator convention.

### Tests

- [ ] Missing first-period Total Assets -> fail.
- [ ] Missing later-period Total Assets -> fail.
- [ ] Explicit zero Total Assets remains accepted.
- [ ] Existing “Total Assets line entirely absent” test remains green and still omits only scaled families.

---

## Task 4 — Prove availability gating and incompleteness are distinct

**Files:**
- Test: `core/tests/test_earnings_quality.py`

Create a compact matrix of end-to-end behavior:

```text
CFO line absent, Total Assets present
    quality_series is None
    quality_specs == ()
    Earnings Quality sheet absent

CFO line present+complete, Total Assets absent
    quality_series exists
    only operating_cash_flow_link / cash_conversion_ratio / total_accruals
    Earnings Quality sheet present

CFO line present+incomplete
    build raises

CFO line present+complete, Total Assets present+incomplete
    build raises

CFO line present+complete, Total Assets present+complete
    all five quality families active
```

Do not encode “incomplete” as ordinary feature unavailability.

This distinction is the central acceptance test of Step 9A.1.

---

## Task 5 — Preserve Check and trusted-state behavior

**Files:**
- Test: `core/tests/test_earnings_quality.py`
- Modify production Check code only if a failing regression proves it is necessary

No Check redesign is expected.

Because new incomplete artifacts should fail during build, normal new Trainer/Answer-Key pairs cannot contain fabricated CFO/asset values. Still verify that dynamic Check remains compatible with the stricter model function.

Required regressions:

- [ ] Normal complete Step 9A workbook still checks fresh as all blank.
- [ ] Exact earnings-quality formula still turns green.
- [ ] Equivalent formula with correct cached result still turns green.
- [ ] Trusted populated Earnings Quality tamper still fails before recoloring.
- [ ] Existing Step 8 judgment choices continue to compose with quality Check.

Do not loosen `_validate_trusted_sheet_cells()` to accommodate missing data.

---

## Task 6 — Correct checkpoint documentation

**Files:**
- Modify: `RESULT.md`
- Modify: `README-HK-TRAINER.md` only if it states or implies missing period values become zero
- Modify: `skills/bav-trainer/SKILL.md` only if it states or implies missing period values become zero
- Modify: `IMPLEMENTATION.md` status only after verification passes
- Do not modify: `TARGET.md`

Correct this inaccurate `RESULT.md` statement:

```text
zero average assets → accrual ratio None
```

to the accepted implemented convention:

```text
zero average assets → accrual ratio 0.0 (explicit Step 9A denominator convention)
```

Add explicit evidence:

```text
- absent CFO line -> quality module omitted
- incomplete resolved CFO line -> build rejected; no zero fabrication
- absent Total Assets line -> asset-scaled extension omitted
- incomplete resolved Total Assets line -> build rejected; no zero fabrication
- explicit numeric zero remains valid supplied data
```

Do not write `Unresolved: none` until the new partial-period regressions pass.

---

## Task 7 — Full verification

Run focused tests:

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

Then the historical/judgment regression suites:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
```

Then the complete suite:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count; do not prestate a new total.

Verify the complete demo build still has the Step 9A surface:

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

Required demo result:

```text
34 schedule groups
161 practice cells
fresh Check: 0 correct / 0 incorrect / 161 blank
```

Verify CLI remains unchanged:

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

GitHub currently has no attached CI checks for the implementation branch, so `RESULT.md` must describe these as local verification unless CI is added separately.

---

## Definition of done

Step 9A.1 is complete only when:

1. A completely absent CFO line still disables the Earnings Quality module.
2. A resolved CFO line missing any modeled-period value fails clearly.
3. Missing CFO period values are never converted to zero.
4. A completely absent Total Assets line still disables only the asset-scaled extension.
5. A resolved Total Assets line missing any modeled-period value fails clearly.
6. Missing Total Assets period values are never converted to zero.
7. Explicit numeric zero remains distinguishable from missing data and remains valid.
8. Zero Net Income still maps to cash conversion ratio `0.0` under the accepted convention.
9. Zero Average Total Assets still maps to accrual ratio `0.0` under the accepted convention.
10. Step 9A demo surfaces remain 30 / 141 and 34 / 161.
11. Trusted-state and judgment regressions remain green.
12. Full test suite passes.
13. `RESULT.md` no longer falsely states that zero average assets produce `None`.
14. `TARGET.md` remains unchanged.
15. Working-capital interpretation, forecasting, valuation, and quality scoring have not begun.

After completing this checkpoint, stop and report changed files, exact test outputs, and any unresolved issue. Do not proceed to the interpretive earnings-quality step and do not commit or push.
