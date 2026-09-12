# Step 9E.1 — Historical Cash-Conversion Trend Diagnostics

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `787a1b97b6e2c6664b7e81304165c6757ca325b6` (`Step 9D1`, Step 9D.1 complete). Implement only Step 9E.1 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, all Step 9A source-completeness / tax / normalization / `#N/A` semantics, the complete Step 9B working-capital diagnostics, the complete Step 9C RNOA level/change attribution surface, and the complete Step 9D ROE operating/financing attribution surface. Do not add company-specific causal claims, automatic good/bad earnings-quality labels, forecasting, valuation, historical share-count schema changes, segment analysis, ROU/deferred-tax alternative modeling, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Extend the existing Earnings Quality schedule from level diagnostics into period-to-period cash-conversion trends so the learner can see how Operating Cash Flow, cash conversion, and accrual measures moved over time without turning mechanical changes into unsupported quality judgments.

**Architecture:** Keep the existing `EarningsQualitySeries` and five Step 9A formula families unchanged. Add one focused `EarningsQualityChangeSeries` that consumes the already validated quality series and produces four change series. Add four new semantic families after the current Step 9D surface, append a trend section to the existing `Earnings Quality` worksheet, and reuse the existing dynamic Check / trusted-sheet architecture. The Total-Assets-dependent accrual-ratio change family remains gated exactly like the existing asset-scaled quality extension.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `EarningsQualitySeries`, `UNDEFINED_RATIO`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and existing trusted-sheet validation for `Earnings Quality`.

**Spec:** `TARGET.md`, especially the requirements to explain changes in cash conversion, cover accruals / cash conversion / quality of earnings, diagnose whether cash conversion is consistent with reported profitability, follow material/applicable-topic gating, and keep structured diagnostics separate from unsupported causal or investment-quality claims.

## Global Constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all existing Step 8 judgment behavior and treatment-conditioned Check.
- Preserve all Step 9A source-completeness, tax, normalization, and `#N/A` semantics.
- Preserve all Step 9B, Step 9C, and Step 9D families/formulas unchanged.
- Preserve the original five `QUALITY_COMPONENT_CATALOG` families unchanged.
- The new trend module is applicable only when the existing Earnings Quality module is applicable, i.e. Operating Cash Flow resolves and is complete.
- If Operating Cash Flow is absent, there is no `Earnings Quality` sheet and there must be no Step 9E.1 families.
- If Total Assets is absent, the three core change families remain applicable but `Change in Accrual Ratio` is omitted from the semantic practice surface.
- First-period differences are non-applicable, not numeric zero.
- `Change in Accrual Ratio` additionally requires two defined comparable accrual-ratio observations, so fiscal-period indices `0` and `1` are non-applicable.
- If either the current or prior ratio is undefined (`#N/A`), the corresponding ratio change is also `#N/A`.
- A numeric zero difference is a valid `0.0`; do not convert unchanged metrics to `#N/A`.
- Preserve signs. Do not take absolute values of CFO changes, conversion changes, accrual changes, or accrual-ratio changes.
- Do not automatically label higher/lower cash conversion, accruals, or accrual ratio as good, bad, improving, deteriorating, sustainable, or suspicious.
- Do not infer collection quality, inventory issues, supplier behavior, earnings manipulation, seasonality, or management intent from these aggregate changes.
- Do not add automatic quality scoring or free-form automatic grading.
- Do not add forecasting, valuation, scenarios, historical diluted-share schema work, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Review of commit `787a1b97`

Step 9D.1 is complete and coherent:

- Financing Contribution to ROE is exposed as `FLEV × Spread`;
- historical decomposed-ROE changes are split into Operating, Leverage, and Spread effects;
- midpoint weighting provides exact order-neutral financing-product attribution;
- undefined financing inputs propagate to `#N/A` rather than fabricated zero effects;
- level and change reconciliation checks are trusted and tamper-detected;
- live classification changes financing-sensitive dynamic expected values;
- base demo is 58 families / 244 practice cells;
- normalization demo is 62 families / 264 practice cells;
- `RESULT.md` records 232 locally passing tests;
- GitHub has no attached CI status.

The remaining historical interpretation gap explicitly named in `TARGET.md` is cash conversion. Step 9A currently shows the level diagnostics:

```text
Cash Conversion Ratio = CFO / Reported Net Income
Total Accruals         = Reported Net Income - CFO
Accrual Ratio          = Total Accruals / Average Total Assets
```

but the learner still has to inspect the rows manually to determine what changed over time.

Step 9E.1 adds **trend arithmetic only**:

```text
Change in CFO
Change in Cash Conversion Ratio
Change in Total Accruals
Change in Accrual Ratio
```

It does not decide whether those movements represent better or worse earnings quality.

---

### Task 1: Add authoritative earnings-quality change series

**Files:**
- Create: `core/model/earnings_quality_change.py`
- Create: `core/tests/test_earnings_quality_change.py`

**Interfaces:**
- Consumes: `EarningsQualitySeries`, `UNDEFINED_RATIO`.
- Produces: `EarningsQualityChangeSeries` and `compute_earnings_quality_change_series(earnings_quality)`.

- [ ] **Step 1: Write the failing data-model and ordinary-case test**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass

from .earnings_quality import EarningsQualitySeries
from .ratio_values import UNDEFINED_RATIO


@dataclass(frozen=True)
class EarningsQualityChangeSeries:
    operating_cash_flow_change: tuple[float | None, ...]
    cash_conversion_ratio_change: tuple[float | str | None, ...]
    total_accruals_change: tuple[float | None, ...]
    accrual_ratio_change: tuple[float | str | None, ...]
```

Use a three- or four-period synthetic `EarningsQualitySeries` and verify ordinary differences.

Example:

```text
CFO:                  80 -> 90 -> 120
Cash Conversion:     0.80 -> 0.75 -> 1.00
Total Accruals:      20 -> 30 -> 0
Accrual Ratio:       N/A-period -> 0.10 -> 0.04
```

Expected changes:

```text
Change CFO:              None, +10, +30
Change Cash Conversion:  None, -0.05, +0.25
Change Total Accruals:   None, +10, -30
Change Accrual Ratio:    None, None, -0.06
```

- [ ] **Step 2: Run focused tests and verify red state**

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality_change.py -v
```

Expected: fail because `core.model.earnings_quality_change` does not yet exist.

- [ ] **Step 3: Implement one undefined-aware difference helper**

Create:

```python
def _difference_or_na(current, prior) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)
```

Do not introduce tolerance or zero-default behavior.

- [ ] **Step 4: Implement series-length validation and first-period semantics**

Create:

```python
def compute_earnings_quality_change_series(
    earnings_quality: EarningsQualitySeries,
) -> EarningsQualityChangeSeries:
    cfo = tuple(earnings_quality.operating_cash_flow)
    conversion = tuple(earnings_quality.cash_conversion_ratio)
    accruals = tuple(earnings_quality.total_accruals)
    accrual_ratio = tuple(earnings_quality.accrual_ratio)

    lengths = {
        "operating_cash_flow": len(cfo),
        "cash_conversion_ratio": len(conversion),
        "total_accruals": len(accruals),
        "accrual_ratio": len(accrual_ratio),
    }
    if len(set(lengths.values())) != 1 or lengths["operating_cash_flow"] == 0:
        raise ValueError(
            "earnings-quality change series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    n = len(cfo)
    cfo_change: list[float | None] = [None] * n
    conversion_change: list[float | str | None] = [None] * n
    accruals_change: list[float | None] = [None] * n
    accrual_ratio_change: list[float | str | None] = [None] * n
```

- [ ] **Step 5: Implement core comparable-period changes**

For every `i >= 1`:

```python
cfo_change[i] = float(cfo[i]) - float(cfo[i - 1])
conversion_change[i] = _difference_or_na(
    conversion[i],
    conversion[i - 1],
)
accruals_change[i] = float(accruals[i]) - float(accruals[i - 1])
```

- [ ] **Step 6: Implement asset-scaled accrual-ratio changes**

The existing no-Total-Assets path represents `accrual_ratio` as all `None`.

Detect applicability with:

```python
has_accrual_ratio = any(
    value is not None
    for value in accrual_ratio[1:]
)
```

If `has_accrual_ratio` is true, for every `i >= 2`:

```python
current = accrual_ratio[i]
prior = accrual_ratio[i - 1]
if current is None or prior is None:
    raise ValueError(
        "earnings-quality accrual-ratio change requires consecutive comparable values: "
        f"period_index={i} current={current!r} prior={prior!r}"
    )
accrual_ratio_change[i] = _difference_or_na(current, prior)
```

If Total Assets are absent, leave the entire `accrual_ratio_change` series as `None`.

- [ ] **Step 7: Return all four series**

```python
return EarningsQualityChangeSeries(
    operating_cash_flow_change=tuple(cfo_change),
    cash_conversion_ratio_change=tuple(conversion_change),
    total_accruals_change=tuple(accruals_change),
    accrual_ratio_change=tuple(accrual_ratio_change),
)
```

- [ ] **Step 8: Add edge-case tests**

Add tests proving:

```text
index 0 all core changes                         -> None
indices 0 and 1 accrual-ratio change             -> None
unchanged numeric metric                         -> 0.0
negative CFO change                              -> signed negative value
negative accrual change                          -> signed negative value
current conversion #N/A                          -> conversion change #N/A
prior conversion #N/A                            -> conversion change #N/A
current accrual ratio #N/A                       -> accrual-ratio change #N/A
prior accrual ratio #N/A                         -> accrual-ratio change #N/A
no Total Assets / all accrual ratios None        -> all accrual-ratio changes None
inconsistent partially missing accrual-ratio row -> clear ValueError
series-length mismatch                           -> clear ValueError
```

- [ ] **Step 9: Run focused tests to green**

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality_change.py -v
```

---

### Task 2: Add four semantic cash-conversion trend families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_earnings_quality_change.py`
- Test: `core/tests/test_earnings_quality.py`

**Interfaces:**
- Consumes: `EarningsQualityChangeSeries` from Task 1.
- Produces: four semantic families and dynamic expected values.

- [ ] **Step 1: Add a separate quality-change catalog**

Add after `ROE_ATTRIBUTION_COMPONENT_CATALOG` / its expander and before deferred specs:

```python
QUALITY_CHANGE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (...)
```

Use family orders `63` through `66` and tab `Earnings Quality`.

Define exactly:

```python
ComponentFamily(
    id="operating_cash_flow_change",
    order=63,
    title="Change in Operating Cash Flow",
    short_hint="Current CFO minus prior CFO.",
    semantic_key="quality_change.operating_cash_flow_change",
    category="earnings_quality_change",
    tab_template="Earnings Quality",
    period_scope="comparable",
    depends_on_current=("operating_cash_flow_link",),
    depends_on_previous=("operating_cash_flow_link",),
    hints=(
        "Change in CFO = Current Operating Cash Flow - Prior Operating Cash Flow.",
        "A positive or negative movement is mechanical evidence only; interpret it alongside profitability and business conditions.",
    ),
)
```

```python
ComponentFamily(
    id="cash_conversion_ratio_change",
    order=64,
    title="Change in Cash Conversion Ratio",
    short_hint="Current cash conversion ratio minus prior ratio.",
    semantic_key="quality_change.cash_conversion_ratio_change",
    category="earnings_quality_change",
    tab_template="Earnings Quality",
    period_scope="comparable",
    depends_on_current=("cash_conversion_ratio",),
    depends_on_previous=("cash_conversion_ratio",),
    hints=(
        "Change in Cash Conversion Ratio = Current CFO/Net Income ratio - Prior ratio.",
        "If either period's ratio is undefined, the change is also undefined (#N/A).",
        "Do not automatically label a higher ratio as better quality without investigating why it changed.",
    ),
)
```

```python
ComponentFamily(
    id="total_accruals_change",
    order=65,
    title="Change in Total Accruals",
    short_hint="Current Total Accruals minus prior Total Accruals.",
    semantic_key="quality_change.total_accruals_change",
    category="earnings_quality_change",
    tab_template="Earnings Quality",
    period_scope="comparable",
    depends_on_current=("total_accruals",),
    depends_on_previous=("total_accruals",),
    hints=(
        "Change in Total Accruals = Current (Net Income - CFO) - Prior (Net Income - CFO).",
        "Retain the sign; do not convert accrual movements to absolute values.",
        "The direction alone is not an automatic earnings-quality verdict.",
    ),
)
```

```python
ComponentFamily(
    id="accrual_ratio_change",
    order=66,
    title="Change in Accrual Ratio",
    short_hint="Current accrual ratio minus prior comparable accrual ratio.",
    semantic_key="quality_change.accrual_ratio_change",
    category="earnings_quality_change",
    tab_template="Earnings Quality",
    period_scope="post_comparable",
    depends_on_current=("accrual_ratio",),
    depends_on_previous=("accrual_ratio",),
    hints=(
        "Change in Accrual Ratio = Current Accrual Ratio - Prior Accrual Ratio.",
        "This family is available only when reported Total Assets support the existing accrual-ratio schedule.",
        "Undefined current or prior ratios propagate to #N/A.",
    ),
)
```

- [ ] **Step 2: Add `expand_quality_change_specs()`**

Create:

```python
def expand_quality_change_specs(
    periods: list[date],
    *,
    start_order: int,
    include_asset_scaled: bool,
) -> tuple[ComponentSpec, ...]:
```

Requirements:

- reject duplicate or non-increasing periods exactly like existing expanders;
- if `include_asset_scaled` is false, omit `accrual_ratio_change`;
- `comparable` -> `range(1, len(periods))`;
- `post_comparable` -> `range(2, len(periods))`;
- build dependencies with the existing `concrete_component_id()` pattern;
- reject any unexpected period scope explicitly.

For five modeled periods:

```text
with Total Assets:
3 comparable families × 4 periods + 1 post-comparable × 3 periods = 15 cells
4 families

without Total Assets:
3 comparable families × 4 periods = 12 cells
3 families
```

- [ ] **Step 3: Add expected-series mapping**

In `core/model/historical_expected.py`, import:

```python
QUALITY_CHANGE_COMPONENT_CATALOG
```

and:

```python
from .earnings_quality_change import compute_earnings_quality_change_series
```

Add:

```python
_QUALITY_CHANGE_FAMILY_SERIES = (
    "operating_cash_flow_change",
    "cash_conversion_ratio_change",
    "total_accruals_change",
    "accrual_ratio_change",
)
```

Create:

```python
def earnings_quality_change_expected_series(
    earnings_quality: EarningsQualitySeries,
) -> dict[str, tuple[float | str | None, ...]]:
    changes = compute_earnings_quality_change_series(earnings_quality)
    series = {
        "operating_cash_flow_change": changes.operating_cash_flow_change,
        "cash_conversion_ratio_change": changes.cash_conversion_ratio_change,
        "total_accruals_change": changes.total_accruals_change,
        "accrual_ratio_change": changes.accrual_ratio_change,
    }
    expected_ids = {family.id for family in QUALITY_CHANGE_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "earnings_quality_change_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _QUALITY_CHANGE_FAMILY_SERIES
    }
```

- [ ] **Step 4: Route dynamic expected values through the existing quality object**

In `expected_value_for_component()`, before the existing `_QUALITY_FAMILY_SERIES` branch:

```python
if family_id in _QUALITY_CHANGE_FAMILY_SERIES:
    if earnings_quality is None:
        raise ValueError(
            f"Earnings-quality-change family {family_id!r} "
            "requires an EarningsQualitySeries"
        )
    series = earnings_quality_change_expected_series(earnings_quality)
```

Keep every other expected-value branch unchanged.

- [ ] **Step 5: Extend the Check quality-family detector**

In `core/trainer/checker.py`, import:

```python
QUALITY_CHANGE_COMPONENT_CATALOG
```

Replace the old detector with:

```python
quality_family_ids = {
    family.id
    for family in (
        *QUALITY_COMPONENT_CATALOG,
        *QUALITY_CHANGE_COMPONENT_CATALOG,
    )
}
```

The same `compute_earnings_quality_series()` result must serve both level and change families. Do not create a second source-resolution path inside Check.

- [ ] **Step 6: Add focused catalog / expected-value tests**

Prove:

```text
QUALITY_CHANGE_COMPONENT_CATALOG contains exactly 4 unique IDs
orders are exactly 63,64,65,66
five periods + assets -> 15 concrete specs
five periods without assets -> 12 concrete specs
accrual_ratio_change absent when assets are unavailable
expected-series keys exactly equal the 4 catalog IDs
quality-change expected values use the passed EarningsQualitySeries
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality_change.py core/tests/test_earnings_quality.py -v
```

---

### Task 3: Wire quality-change specs into `ReferenceModelBuilder`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_earnings_quality_change.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: `compute_earnings_quality_change_series()`, `expand_quality_change_specs()`.
- Produces: builder state and semantic registrations for Step 9E.1.

- [ ] **Step 1: Add imports**

Import:

```python
from ..model.earnings_quality_change import compute_earnings_quality_change_series
```

and:

```python
expand_quality_change_specs
```

- [ ] **Step 2: Compute the quality-change series only when the existing quality module is active**

After `self.roe_attribution_specs` are established, add:

```python
if self.quality_series is not None:
    self.quality_change_series = compute_earnings_quality_change_series(
        self.quality_series
    )
    self.quality_change_specs = expand_quality_change_specs(
        self.periods,
        start_order=(
            len(self.historical_specs)
            + len(self.normalization_specs)
            + len(self.quality_specs)
            + len(self.working_capital_specs)
            + len(self.profitability_driver_specs)
            + len(self.profitability_change_specs)
            + len(self.roe_attribution_specs)
            + 1
        ),
        include_asset_scaled=self.quality_availability.total_assets,
    )
else:
    self.quality_change_series = None
    self.quality_change_specs = ()
```

Do not renumber existing families or move Step 9E.1 before existing diagnostic specs.

- [ ] **Step 3: Append specs and index them**

Append to `self.expected_specs`:

```python
+ self.quality_change_specs
```

Create:

```python
self._quality_change_spec_index = {
    (s.family_id, s.period_index): s
    for s in self.quality_change_specs
}
```

- [ ] **Step 4: Add a registration helper**

Create alongside `_register_quality()`:

```python
def _register_quality_change(
    self,
    family_id: str,
    period_index: int,
    tab: str,
    row: int,
    col: int,
    formula: str,
    expected: float | str,
    related: list[str] | None = None,
) -> None:
    spec = self._quality_change_spec_index[(family_id, period_index)]
    self.semantic_map.register(
        spec,
        tab,
        row,
        col,
        formula,
        expected,
        related_cells=related,
    )
```

- [ ] **Step 5: Add builder-state tests**

Prove:

```text
CFO unavailable -> quality_change_series is None and quality_change_specs == ()
CFO available + assets available -> four quality-change families present
CFO available + assets absent -> exactly three quality-change families present
existing quality specs/families remain unchanged
```

Run focused tests before workbook-layout work.

---

### Task 4: Append the cash-conversion trend section to `Earnings Quality`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_earnings_quality_change.py`
- Test: `core/tests/test_earnings_quality.py`

**Interfaces:**
- Consumes: existing Earnings Quality level rows plus `self.quality_change_series`.
- Produces: Step 9E.1 worksheet formulas and semantic registrations.

- [ ] **Step 1: Refactor the current Total-Assets early return**

`_build_earnings_quality()` currently returns immediately when `total_assets` is unavailable. Replace that early return with conditional construction of rows 10–12, then continue to the trend section in both asset and no-asset cases.

Do not change the current formulas or registration behavior of rows 5–12.

Use:

```python
assets_row = None
avg_assets_row = None
accrual_ratio_row = None

if self.quality_availability.total_assets:
    ... existing asset-scaled construction unchanged ...
```

Store the same rowmap keys only when those rows exist.

- [ ] **Step 2: Add a fixed trend section**

Below the existing quality rows use exactly:

```text
A14  EARNINGS QUALITY TREND DIAGNOSTICS
A15  Change in Operating Cash Flow
A16  Change in Cash Conversion Ratio
A17  Change in Total Accruals
A18  Change in Accrual Ratio
A19  EARNINGS QUALITY CHANGE CHECK
```

Make rows 14 and 19 bold.

Use `self.quality_change_series`; raise `RuntimeError` if the sheet is being built while that series is unexpectedly `None`.

- [ ] **Step 3: Preserve non-applicable cells as visible literals**

For fiscal-period index `0`:

```text
rows 15,16,17,18,19 -> literal "N/A"
```

For row 18 (`Change in Accrual Ratio`):

- index `1` -> literal `"N/A"`;
- if Total Assets are absent -> literal `"N/A"` for every period;
- do not register semantic practice cells where the family is not applicable.

- [ ] **Step 4: Add comparable core change formulas**

For every `j >= 1`:

```python
col = self._col(2 + j)
prev_col = self._col(2 + j - 1)

cfo_change_f = f"={col}{cfo_row}-{prev_col}{cfo_row}"
conversion_change_f = (
    f"={col}{conversion_row}-{prev_col}{conversion_row}"
)
accruals_change_f = f"={col}{accruals_row}-{prev_col}{accruals_row}"
```

Use formats:

```text
Change in CFO             -> NUM_FMT
Change in Cash Conversion -> "0.00x"
Change in Total Accruals  -> NUM_FMT
```

Do not wrap ratio differences in `IFERROR`; Excel must naturally propagate `#N/A`.

Register:

```text
operating_cash_flow_change
cash_conversion_ratio_change
total_accruals_change
```

using `_register_quality_change()` and the current period index.

- [ ] **Step 5: Add accrual-ratio change formulas only when asset-scaled quality exists**

When Total Assets are available, for every `j >= 2`:

```python
assert accrual_ratio_row is not None
accrual_ratio_change_f = (
    f"={col}{accrual_ratio_row}-{prev_col}{accrual_ratio_row}"
)
```

Format as `PCT_FMT` and register `accrual_ratio_change`.

- [ ] **Step 6: Add one generated non-practice consistency check**

For every `j >= 1`, use the identity:

```text
Total Accruals = Net Income - CFO
```

so:

```text
Change in Total Accruals
= Change in Net Income - Change in CFO
```

Use a generated formula in row 19:

```python
change_check_f = (
    f'=IF(ABS({col}{accruals_change_row}-'
    f'(({col}{ni_row}-{prev_col}{ni_row})-{col}{cfo_change_row}))'
    f'<0.01,"OK","CHECK")'
)
```

This row is **not** a practice family.

The existing trusted-sheet validator already protects all non-practice cells on `Earnings Quality`; do not modify `check_context.py` unless a failing regression proves that assumption wrong.

- [ ] **Step 7: Store rowmap entries**

Add:

```python
self.rowmap["quality_change_cfo_row"] = cfo_change_row
self.rowmap["quality_change_conversion_row"] = conversion_change_row
self.rowmap["quality_change_accruals_row"] = accruals_change_row
self.rowmap["quality_change_accrual_ratio_row"] = accrual_ratio_change_row
self.rowmap["quality_change_check_row"] = change_check_row
```

The accrual-ratio change row exists visually even when its practice family is gated off, so the rowmap key may always be recorded.

- [ ] **Step 8: Add workbook regressions**

Prove:

```text
existing rows/formulas 5–12 remain unchanged
trend section appears whenever CFO quality module appears
first-period trend cells are literal N/A
asset-present demo registers 15 trend practice cells
asset-absent fixture registers 12 trend practice cells
asset-absent row18 is N/A across all periods
no CFO -> no Earnings Quality sheet and no trend section
change-check row is populated but never a practice cell
```

---

### Task 5: Prove Formula Check and trusted-sheet behavior for the trend section

**Files:**
- Modify: `core/tests/test_earnings_quality_change.py`
- Modify: `core/tests/test_earnings_quality.py`
- Modify: `core/tests/test_reference_integrity.py` only if that is the established location for one integrity assertion

- [ ] **Step 1: Add exact-formula Check regression**

Build a normal pair, enter one exact Step 9E.1 formula, run Check, and require exactly that cell to become green.

- [ ] **Step 2: Add undefined change regression**

Use at least three periods and make one Net Income period exactly zero so one current/prior cash-conversion ratio is `#N/A`.

Require:

```text
cash_conversion_ratio_change expected -> #N/A
Answer-Key formula is a direct difference that naturally propagates #N/A
exact formula -> green
structurally different formula + cached #N/A -> green
fabricated 0.0 -> red
```

Reuse the existing cached-value injection helper already used by Step 9A tests rather than creating production evaluator logic.

- [ ] **Step 3: Add trusted check-row tamper regression**

1. Build Trainer/Answer Key.
2. Put a valid formula into one Step 9E.1 practice cell and verify it is still yellow before Check.
3. Overwrite one populated `EARNINGS QUALITY CHANGE CHECK` formula in Trainer.
4. Run Check.
5. Require `ValueError` for trusted Earnings Quality modification.
6. Reopen Trainer and prove the learner practice cell remains yellow: no partial recoloring.

Do not modify production trusted-sheet code unless this test fails for a real reason.

- [ ] **Step 4: Preserve composition with classification and normalization**

Extend or add an end-to-end composition test where:

- Accounting Judgment has a valid alternative treatment;
- Normalization Judgment has a valid treatment;
- one historical classification-sensitive formula, one normalization formula, and one Step 9E.1 formula are entered;
- Check grades all three without interference.

The quality-change formula does not itself need to be classification-sensitive; the test proves coexistence of all active modules.

---

### Task 6: Add Trainer index metadata and update product documentation

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Test: `core/tests/test_earnings_quality_change.py`
- Test: `core/tests/test_trainer.py`

- [ ] **Step 1: Add the new catalog to Trainer family metadata**

Import:

```python
QUALITY_CHANGE_COMPONENT_CATALOG
```

Then extend `family_meta`:

```python
family_meta.update({f.id: f for f in QUALITY_CHANGE_COMPONENT_CATALOG})
```

Do not alter existing family metadata ordering.

- [ ] **Step 2: Verify Trainer/List dependency labels**

For the four new schedules, verify:

```text
Change in Operating Cash Flow -> depends on operating_cash_flow_link
Change in Cash Conversion Ratio -> depends on cash_conversion_ratio
Change in Total Accruals -> depends on total_accruals
Change in Accrual Ratio -> depends on accrual_ratio
```

The Trainer index should show their actual fiscal-period scope and practice cells through the existing grouping logic.

- [ ] **Step 3: Update `skills/bav-trainer/SKILL.md`**

Update the product-loop documentation to reflect that the historical diagnostic surface now includes:

```text
Step 9A — earnings-quality level diagnostics
Step 9B — working-capital diagnostics / driver bridge
Step 9C — RNOA margin / turnover level and change attribution
Step 9D — ROE operating / financing attribution
Step 9E.1 — cash-conversion / accrual trend diagnostics
```

Remove stale language claiming working-capital/driver interpretation is still wholly deferred.

Keep these still deferred:

```text
company-specific causal diagnosis
historical per-share expansion where share data is not yet supplied
forecasting
valuation
investment conclusion
ROU/deferred-tax alternative modeling
```

Do not rewrite old release history; update only the current product description / scope statements.

---

### Task 7: Full regression and acceptance evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all verification passes
- Do not modify: `TARGET.md`

- [ ] **Step 1: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality_change.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
```

- [ ] **Step 2: Run integrity / Trainer suites**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
```

- [ ] **Step 3: Run the complete suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual final pass count; do not invent it in advance.

- [ ] **Step 4: Verify the five-year base demo**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required Step 9E.1 surface:

```text
62 formula families
259 practice cells
fresh Check: 0 correct / 0 incorrect / 259 blank
62 schedule groups
```

Reason:

```text
Step 9D.1 base: 58 families / 244 cells
Step 9E.1:      +4 families / +15 cells
new base:        62 families / 259 cells
```

- [ ] **Step 5: Verify the normalization demo**

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
66 formula families
279 practice cells
fresh Check: 0 correct / 0 incorrect / 279 blank
66 schedule groups
```

- [ ] **Step 6: Verify no-asset and no-CFO gating**

Using existing focused fixtures:

```text
CFO absent:
- Earnings Quality sheet absent
- all existing quality families absent
- all Step 9E.1 quality-change families absent

CFO present, Total Assets absent:
- Earnings Quality sheet present
- existing three non-asset quality families preserved
- Step 9E.1 has exactly 3 families / 12 practice cells
- accrual_ratio_change absent from SemanticMap
- visual Change in Accrual Ratio row remains N/A for all periods
```

- [ ] **Step 7: Verify public CLI remains unchanged**

```bash
PYTHONPATH=. python -m core --help
```

Required public commands remain:

```text
ingest
build
check
list
```

- [ ] **Step 8: Update `RESULT.md`**

Record:

- actual full-suite pass count;
- base 62 / 259 preservation;
- normalization 66 / 279 preservation;
- four cash-conversion trend families when Total Assets are available;
- three trend families when Total Assets are absent;
- no-CFO omission behavior;
- `#N/A` propagation in ratio changes;
- trusted `EARNINGS QUALITY CHANGE CHECK` tamper failure before recolor;
- exact/equivalent formulas remain eligible;
- no automatic quality labels or causal diagnosis;
- CLI unchanged;
- `TARGET.md` unchanged;
- forecasting / valuation / historical-share schema work not begun.

---

## Definition of done

Step 9E.1 is complete only when all of the following are true:

1. Operating Cash Flow change is practiced across comparable periods.
2. Cash Conversion Ratio change is practiced across comparable periods.
3. Total Accruals change is practiced across comparable periods.
4. Accrual Ratio change is practiced only when Total Assets support the existing accrual-ratio schedule.
5. First-period core changes are non-applicable, not zero.
6. First two Accrual Ratio change periods are non-applicable.
7. Undefined current/prior ratios propagate to `#N/A`.
8. Numeric unchanged metrics produce `0.0` changes.
9. Signs are preserved; no absolute-value normalization is introduced.
10. The generated Earnings Quality change check is trusted and tamper-detected before any fill change.
11. Existing five Step 9A quality families/formulas remain unchanged.
12. CFO-absent builds omit the quality-change module entirely.
13. Total-Assets-absent builds retain the three core trend families and omit only the accrual-ratio-change family.
14. Dynamic Check reuses the same authoritative EarningsQualitySeries rather than resolving source facts a second time.
15. Five-year base demo is 62 families / 259 practice cells.
16. Five-year normalization demo is 66 families / 279 practice cells.
17. Full test suite passes.
18. Public CLI remains `{ingest,build,check,list}`.
19. `TARGET.md` remains unchanged.
20. No automatic earnings-quality verdict, causal working-capital diagnosis, forecasting, valuation, per-share schema expansion, or investment conclusion has been introduced.

After completing Step 9E.1, stop and report changed files, exact test output, base/normalization build-check-list output, gating evidence, `#N/A` change evidence, trusted-check tamper evidence, and any new active historical-model issue found during implementation. Do not proceed to the next curriculum feature and do not commit or push.