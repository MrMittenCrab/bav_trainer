# Step 9F.3 — Historical Normalized Diluted EPS Bridge

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `1e0d412b26ab1103e19ab547c0b3acca3bb09591` (`Step 9F2`, Step 9F.2 complete). Implement only Step 9F.3 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, all Step 9A source-completeness / tax / normalization / `#N/A` semantics, Step 9B working-capital diagnostics, Step 9C profitability drivers/change attribution, Step 9D ROE attribution, Step 9E cash-conversion trends, and the complete Step 9F.1–9F.2 per-share surface. Do not add basic-vs-diluted analysis, period-end share counts, forecasting, valuation, segment analysis, ROU/deferred-tax alternatives, automatic investment conclusions, or company-specific causal claims. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Connect the existing earnings-normalization bridge to the existing diluted per-share module so the learner can distinguish reported diluted EPS from normalized diluted EPS and see how changes in normalization adjustments affect period-to-period per-share economics.

**Architecture:** Add a focused `NormalizedPerShareSeries` that consumes the existing `NormalizationSeries` and `PerShareSeries`; do not create new historical inputs. Gate the new surface on **both** active normalization cases and valid historical diluted weighted-average shares. Add four semantic families to the existing `Per Share Analysis` sheet plus generated level/change reconciliation rows. Dynamic Check must recompute normalized per-share expecteds from the learner's current Normalization Judgment treatment, while the existing trusted-sheet boundary protects populated cross-sheet links and reconciliation formulas.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `NormalizationSeries`, `PerShareSeries`, `UNDEFINED_RATIO`, `ratio_or_na`, `ComponentFamily`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and trusted-sheet validation for `Per Share Analysis`.

**Spec:** `TARGET.md`, especially historical EPS/per-share analysis when actual share-count data is supplied, recurring/non-recurring earnings normalization, the requirement to explain per-share economics, structured diagnostics before free-form interpretation, and the no-invented-historical-input rule.

## Global Constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve Step 9F.1 historical-share schema and scale basis exactly; no new share fields.
- Preserve Step 9F.1 and Step 9F.2 formulas, families, row meanings, and Check behavior unchanged.
- New normalized-per-share practice is present only when:
  1. `per_share_available(financials)` is true; and
  2. active normalization cases exist, so `NormalizationSeries` is present.
- Share history without normalization keeps the Step 9F.2 surface unchanged.
- Normalization without share history keeps `Per Share Analysis` absent.
- No share history and no normalization keep the ordinary demo unchanged.
- Use only `NormalizationSeries.after_tax_adjustment`, `NormalizationSeries.normalized_net_income`, and the existing trusted diluted weighted-average share series.
- Do not recalculate normalization candidates or tax effects independently in the per-share module.
- `Normalized Diluted EPS = Normalized Net Income / Diluted Weighted-Average Shares`.
- `Normalization Adjustment per Diluted Share = After-Tax Normalization Adjustment / Diluted Weighted-Average Shares`.
- Level identity: `Reported Diluted EPS + Normalization Adjustment per Diluted Share = Normalized Diluted EPS` when defined.
- Change identity: `Change in Reported Diluted EPS + Normalization Effect on EPS Change = Change in Normalized Diluted EPS` when defined.
- `Normalization Effect on EPS Change = Current Adjustment per Share - Prior Adjustment per Share`.
- Preserve Step 9A.5 undefined-tax semantics. If a nonzero normalization adjustment requires an undefined tax rate, the after-tax adjustment is `#N/A`; normalized per-share outputs that depend on it are also `#N/A`.
- If the pretax normalization adjustment is zero, the existing normalization layer keeps the after-tax adjustment numeric `0.0` even when the tax rate is undefined; normalized EPS therefore remains equal to reported EPS.
- Do not replace `#N/A` with zero and do not use `IFERROR(...,0)`.
- Preserve signs. Do not use `ABS()` in practice formulas. `ABS()` is allowed only inside generated reconciliation checks.
- Share-count levels remain trusted populated inputs, never practice cells.
- Normalization Judgment remains the only learner treatment input controlling normalization; do not add a second treatment input on `Per Share Analysis`.
- Do not add EPS growth rates, basic shares, period-end shares, share-price data, valuation multiples, or market-cap calculations.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or public CLI commands.
- Do not modify dormant forecast/scenario behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Review of commit `1e0d412b`

Step 9F.2 is complete and coherent:

- Step 9F.1 provides trusted, complete, strictly positive diluted weighted-average shares;
- reported diluted EPS and NOPAT per diluted share remain treatment-aware historical formulas;
- Step 9F.2 exactly attributes diluted-EPS change between reported-Net-Income movement and diluted-share-count movement using midpoint weights;
- ordinary no-share demo remains 62 families / 259 cells without normalization and 66 / 279 with normalization;
- share-enabled five-year fixture is 70 families / 293 cells without normalization and 74 / 313 with normalization;
- `RESULT.md` records 259 locally passing tests;
- no normalized diluted EPS is currently exposed despite normalized Net Income already being computed by Step 8B2.

The next dependency-aligned gap is therefore to connect existing normalized earnings to existing diluted-share history without introducing any new source facts or causal labels.

For each fiscal period:

```text
A_t = After-Tax Normalization Adjustment
NI_t = Reported Net Income
NNI_t = Normalized Net Income = NI_t + A_t
S_t = Diluted Weighted-Average Shares

Reported EPS_t = NI_t / S_t
Adjustment per Share_t = A_t / S_t
Normalized EPS_t = NNI_t / S_t

Reported EPS_t + Adjustment per Share_t = Normalized EPS_t
```

For comparable periods:

```text
Change in Normalized EPS_t
= Normalized EPS_t - Normalized EPS_(t-1)

Normalization Effect on EPS Change_t
= Adjustment per Share_t - Adjustment per Share_(t-1)

Change in Reported EPS_t
+ Normalization Effect on EPS Change_t
= Change in Normalized EPS_t
```

These are accounting bridges, not judgments that normalized earnings are inherently superior.

---

### Task 1: Add authoritative normalized-per-share series

**Files:**
- Create: `core/model/normalized_per_share.py`
- Create: `core/tests/test_normalized_per_share.py`

**Interfaces:**
- Consumes: `NormalizationSeries`, `PerShareSeries`, `UNDEFINED_RATIO`, `ratio_or_na`.
- Produces: `NormalizedPerShareSeries` and `compute_normalized_per_share_series(normalization, per_share)`.

- [ ] **Step 1: Write the failing data-model and ordinary-case test**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass

from .normalization import NormalizationSeries
from .per_share import PerShareSeries
from .ratio_values import UNDEFINED_RATIO, ratio_or_na


@dataclass(frozen=True)
class NormalizedPerShareSeries:
    normalization_adjustment_per_diluted_share: tuple[float | str, ...]
    normalized_diluted_eps: tuple[float | str, ...]
    normalized_diluted_eps_change: tuple[float | str | None, ...]
    normalization_effect_on_diluted_eps_change: tuple[float | str | None, ...]
```

Use a three-period ordinary case such as:

```text
Shares:                  100, 100, 110
Reported EPS:            1.00, 1.20, 1.20
After-tax adjustment:    0,  10,   11
Normalized Net Income:   100,130,  143

Adjustment/share:        0.00, 0.10, 0.10
Normalized EPS:          1.00, 1.30, 1.30
Normalized EPS change:   N/A, +0.30, 0.00
Normalization effect:    N/A, +0.10, 0.00
```

Assert both level and change identities numerically.

- [ ] **Step 2: Run the focused test and verify red state**

```bash
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
```

Expected: fail because `core.model.normalized_per_share` does not exist.

- [ ] **Step 3: Implement length and share validation**

Use:

```python
def compute_normalized_per_share_series(
    normalization: NormalizationSeries,
    per_share: PerShareSeries,
) -> NormalizedPerShareSeries:
    shares = tuple(float(v) for v in per_share.diluted_weighted_average_shares)
    reported_eps = tuple(float(v) for v in per_share.reported_diluted_eps)
    reported_eps_change = tuple(per_share.diluted_eps_change)
    after_tax = tuple(normalization.after_tax_adjustment)
    normalized_ni = tuple(normalization.normalized_net_income)

    lengths = {
        "shares": len(shares),
        "reported_eps": len(reported_eps),
        "reported_eps_change": len(reported_eps_change),
        "after_tax_adjustment": len(after_tax),
        "normalized_net_income": len(normalized_ni),
    }
    if len(set(lengths.values())) != 1 or lengths["shares"] == 0:
        raise ValueError(
            "normalized-per-share series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )
    for i, value in enumerate(shares):
        if value <= 0.0:
            raise ValueError(
                "normalized per-share analysis requires positive diluted shares: "
                f"period_index={i} shares={value}"
            )
```

- [ ] **Step 4: Implement level series and fail-closed reconciliation**

For each period:

```python
adjustment_ps = tuple(
    ratio_or_na(after_tax[i], shares[i]) for i in range(len(shares))
)
normalized_eps = tuple(
    ratio_or_na(normalized_ni[i], shares[i]) for i in range(len(shares))
)
```

When both are numeric, validate:

```python
bridge = reported_eps[i] + float(adjustment_ps[i])
if abs(bridge - float(normalized_eps[i])) > 1e-9:
    raise ValueError(
        "normalized diluted EPS level bridge does not reconcile: "
        f"period_index={i} bridge={bridge} normalized={normalized_eps[i]}"
    )
```

Undefined-state consistency must also fail closed:

```python
if (adjustment_ps[i] == UNDEFINED_RATIO) != (
    normalized_eps[i] == UNDEFINED_RATIO
):
    raise ValueError(
        "normalized diluted EPS undefined state is inconsistent: "
        f"period_index={i} adjustment={adjustment_ps[i]} "
        f"normalized={normalized_eps[i]}"
    )
```

- [ ] **Step 5: Implement comparable-period change series**

Use a local helper:

```python
def _difference_or_na(current, prior) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)
```

Initialize first period as `None`; for `i >= 1`:

```python
normalized_change[i] = _difference_or_na(
    normalized_eps[i], normalized_eps[i - 1]
)
normalization_effect[i] = _difference_or_na(
    adjustment_ps[i], adjustment_ps[i - 1]
)
```

When both change values are numeric, require the existing reported EPS change to be present and reconcile:

```python
reported_change = reported_eps_change[i]
if reported_change is None:
    raise ValueError(
        "normalized per-share analysis requires comparable reported EPS change: "
        f"period_index={i}"
    )
bridge = float(reported_change) + float(normalization_effect[i])
if abs(bridge - float(normalized_change[i])) > 1e-9:
    raise ValueError(
        "normalized diluted EPS change bridge does not reconcile: "
        f"period_index={i} bridge={bridge} normalized={normalized_change[i]}"
    )
```

If one of the two normalized change series is `#N/A`, require the other to be `#N/A`; never fabricate a numeric bridge from an undefined normalization state.

- [ ] **Step 6: Add edge-case tests**

Cover exactly:

```text
first period change rows                              -> None
zero normalization adjustment                         -> adjustment/share 0.0; normalized EPS = reported EPS
negative normalization adjustment                     -> signed negative per-share adjustment retained
nonzero adjustment #N/A from tax semantics             -> adjustment/share #N/A; normalized EPS #N/A
zero adjustment with otherwise undefined tax state     -> numeric 0.0 adjustment/share; normalized EPS numeric
current or prior normalized EPS #N/A                   -> normalized EPS change #N/A
current or prior adjustment/share #N/A                 -> normalization effect #N/A
unchanged adjustment/share                             -> normalization effect 0.0
length mismatch                                        -> ValueError
non-positive shares                                    -> ValueError
inconsistent level bridge                              -> ValueError
inconsistent change bridge                             -> ValueError
```

Construct malformed direct dataclass inputs only for fail-closed unit tests; do not weaken upstream normalization/per-share validation.

- [ ] **Step 7: Run focused tests to green**

```bash
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
```

---

### Task 2: Add four normalized-per-share semantic families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_normalized_per_share.py`

**Interfaces:**
- Consumes: `NormalizedPerShareSeries` from Task 1.
- Produces: four semantic families and expected-value routing.

- [ ] **Step 1: Add `NORMALIZED_PER_SHARE_COMPONENT_CATALOG`**

Use family orders `75` through `78`:

```python
NORMALIZED_PER_SHARE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="normalization_adjustment_per_diluted_share",
        order=75,
        title="Normalization Adjustment per Diluted Share",
        short_hint="After-tax normalization adjustment divided by diluted weighted-average shares.",
        semantic_key="normalized_per_share.adjustment_per_diluted_share",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("after_tax_normalization_adjustment",),
        hints=(
            "Normalization Adjustment per Diluted Share = After-Tax Normalization Adjustment / Diluted Weighted-Average Shares.",
            "The sign is preserved; a positive normalization adjustment raises normalized EPS relative to reported EPS.",
        ),
    ),
    ComponentFamily(
        id="normalized_diluted_eps",
        order=76,
        title="Normalized Diluted EPS",
        short_hint="Normalized Net Income divided by diluted weighted-average shares.",
        semantic_key="normalized_per_share.normalized_diluted_eps",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("normalized_net_income",),
        hints=(
            "Normalized Diluted EPS = Normalized Net Income / Diluted Weighted-Average Shares.",
            "Use the current Normalization Judgment treatment; do not create a second treatment assumption here.",
        ),
    ),
    ComponentFamily(
        id="normalized_diluted_eps_change",
        order=77,
        title="Change in Normalized Diluted EPS",
        short_hint="Current normalized diluted EPS minus prior normalized diluted EPS.",
        semantic_key="normalized_per_share.normalized_diluted_eps_change",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("normalized_diluted_eps",),
        depends_on_previous=("normalized_diluted_eps",),
        hints=(
            "Change in Normalized Diluted EPS = Current Normalized EPS - Prior Normalized EPS.",
            "Undefined normalized EPS in either period makes the change undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="normalization_effect_on_diluted_eps_change",
        order=78,
        title="Normalization Effect on Change in Diluted EPS",
        short_hint="Change in normalization adjustment per diluted share.",
        semantic_key="normalized_per_share.normalization_effect_on_diluted_eps_change",
        category="normalized_per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("normalization_adjustment_per_diluted_share",),
        depends_on_previous=("normalization_adjustment_per_diluted_share",),
        hints=(
            "Normalization Effect on EPS Change = Current Adjustment per Share - Prior Adjustment per Share.",
            "Reported EPS Change + this normalization effect must reconcile to Change in Normalized Diluted EPS when defined.",
        ),
    ),
)
```

- [ ] **Step 2: Add `expand_normalized_per_share_specs()`**

Follow existing chronological validation. `all` families use every period; `comparable` families use indices `1..n-1`. Reject unsupported scopes rather than silently guessing.

- [ ] **Step 3: Add expected-series routing**

In `core/model/historical_expected.py`:

```python
_NORMALIZED_PER_SHARE_FAMILY_SERIES = (
    "normalization_adjustment_per_diluted_share",
    "normalized_diluted_eps",
    "normalized_diluted_eps_change",
    "normalization_effect_on_diluted_eps_change",
)
```

Add:

```python
def normalized_per_share_expected_series(
    normalization: NormalizationSeries,
    per_share: PerShareSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    values = compute_normalized_per_share_series(normalization, per_share)
    ...
```

Route these families **before** ordinary per-share families in `expected_value_for_component()`. Require both `normalization` and `per_share`; raise a clear `ValueError` if either is absent.

- [ ] **Step 4: Run focused catalog/expected tests**

```bash
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
```

---

### Task 3: Gate normalized-per-share specs and series correctly in `ReferenceModelBuilder`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_normalized_per_share.py`
- Test: `core/tests/test_normalization.py`
- Test: `core/tests/test_per_share.py`

- [ ] **Step 1: Add imports**

Import:

```python
from ..model.normalized_per_share import compute_normalized_per_share_series
from .component_catalog import expand_normalized_per_share_specs
```

- [ ] **Step 2: Create specs without reordering existing normalization computation**

The current builder computes `normalization_series` after semantic-spec/index construction. Do **not** restructure that existing lifecycle merely for this step.

After Step 9F.2 per-share specs are prepared, define:

```python
if self.per_share_series is not None and self.normalization_cases:
    self.normalized_per_share_specs = expand_normalized_per_share_specs(
        self.periods,
        start_order=(
            len(self.historical_specs)
            + len(self.normalization_specs)
            + len(self.quality_specs)
            + len(self.working_capital_specs)
            + len(self.profitability_driver_specs)
            + len(self.profitability_change_specs)
            + len(self.roe_attribution_specs)
            + len(self.quality_change_specs)
            + len(self.per_share_specs)
            + len(self.per_share_attribution_specs)
            + 1
        ),
    )
else:
    self.normalized_per_share_specs = ()
```

Append these specs to `self.expected_specs` and create `_normalized_per_share_spec_index`.

- [ ] **Step 3: Compute the series after existing `self.normalization_series` initialization**

Immediately after the current `self.normalization_series = (...)` block:

```python
if (
    self.normalized_per_share_specs
    and self.normalization_series is not None
    and self.per_share_series is not None
):
    self.normalized_per_share_series = compute_normalized_per_share_series(
        self.normalization_series,
        self.per_share_series,
    )
else:
    self.normalized_per_share_series = None
```

Do not call `compute_normalization_series()` a second time.

- [ ] **Step 4: Add registration helper**

Add `_register_normalized_per_share(...)` mirroring the existing per-share registration helpers and indexing `_normalized_per_share_spec_index`.

- [ ] **Step 5: Add gating tests**

Prove:

```text
no shares + no normalization       -> no Per Share Analysis; no normalized-per-share specs
normalization + no shares          -> existing normalization only; no Per Share Analysis
shares + no normalization          -> Step 9F.2 surface unchanged; no normalized-per-share specs
shares + normalization             -> all four normalized-per-share families present
```

For the five-year fixtures, acceptance surfaces are:

```text
ordinary base (no shares)                 62 families / 259 cells
ordinary normalization (no shares)        66 families / 279 cells
shares, no normalization                  70 families / 293 cells
shares + normalization                    78 families / 331 cells
```

The new checkpoint adds exactly four families / eighteen practice cells only to the share+normalization case.

---

### Task 4: Extend `Per Share Analysis` with normalized-EPS bridge

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_normalized_per_share.py`
- Test: `core/tests/test_reference_integrity.py`

- [ ] **Step 1: Preserve all existing Step 9F.1–9F.2 rows/formulas**

Do not move or rewrite rows 5–20 of the current `Per Share Analysis` sheet. Append the new section after the Step 9F.2 attribution block.

Use:

```text
row 22  NORMALIZED DILUTED EPS BRIDGE
row 23  After-Tax Normalization Adjustment          (trusted populated link)
row 24  Normalized Net Income                       (trusted populated link)
row 25  Normalization Adjustment per Diluted Share (practice)
row 26  Normalized Diluted EPS                      (practice)
row 27  NORMALIZED EPS LEVEL CHECK                  (trusted generated)
row 29  Change in Normalized Diluted EPS            (practice; comparable only)
row 30  Normalization Effect on Change in Diluted EPS (practice; comparable only)
row 31  NORMALIZED EPS CHANGE CHECK                 (trusted generated)
```

Build this section only when `self.normalized_per_share_series is not None`.

- [ ] **Step 2: Populate trusted normalization links**

Use existing row-map entries from `Earnings Normalization`:

```python
after_tax_src = self.rowmap["earnings_norm_after_tax_row"]
normalized_ni_src = self.rowmap["earnings_norm_ni_row"]
```

Remember `Earnings Normalization` period columns begin at column C (`3 + j`), while `Per Share Analysis` period columns begin at B (`2 + j`). For each `j`:

```python
norm_col = self._col(3 + j)
after_tax_link = (
    f"='Earnings Normalization'!{norm_col}{after_tax_src}"
)
normalized_ni_link = (
    f"='Earnings Normalization'!{norm_col}{normalized_ni_src}"
)
```

These cells are system-controlled context, not practice.

- [ ] **Step 3: Add level practice formulas and check**

For each period:

```python
adjustment_ps_f = (
    f"=IF({col}{shares_row}<=0,NA(),"
    f"{col}{after_tax_adjustment_row}/{col}{shares_row})"
)
normalized_eps_f = (
    f"=IF({col}{shares_row}<=0,NA(),"
    f"{col}{normalized_ni_row}/{col}{shares_row})"
)
level_check_f = (
    f'=IF(OR(ISNA({col}{adjustment_ps_row}),ISNA({col}{normalized_eps_row})),'
    f'"N/A",IF(ABS({col}{eps_row}+{col}{adjustment_ps_row}-'
    f'{col}{normalized_eps_row})<0.0000001,"OK","CHECK"))'
)
```

Register only rows 25 and 26 as practice. Do not register the two populated links or row 27.

- [ ] **Step 4: Add comparable-period change formulas and check**

First period rows 29–31 are literal `N/A` and not practice.

For `j >= 1`:

```python
normalized_eps_change_f = (
    f"={col}{normalized_eps_row}-{prev_col}{normalized_eps_row}"
)
normalization_effect_f = (
    f"={col}{adjustment_ps_row}-{prev_col}{adjustment_ps_row}"
)
change_check_f = (
    f'=IF(OR(ISNA({col}{normalized_eps_change_row}),'
    f'ISNA({col}{normalization_effect_row})),"N/A",'
    f'IF(ABS({col}{eps_chg_row}+{col}{normalization_effect_row}-'
    f'{col}{normalized_eps_change_row})<0.0000001,"OK","CHECK"))'
)
```

Register rows 29 and 30 only.

- [ ] **Step 5: Add rowmap entries**

Add stable row-map keys for all populated/practice/check rows in the new section so integrity tests do not depend on hard-coded scanning.

- [ ] **Step 6: Verify undefined-state formula behavior**

Use a fixture where Pretax Income is zero in a period and a nonzero non-recurring normalization adjustment is selected. Prove:

```text
After-Tax Normalization Adjustment       -> #N/A
Adjustment per Diluted Share             -> #N/A
Normalized Net Income                    -> #N/A
Normalized Diluted EPS                   -> #N/A
relevant comparable change cells         -> #N/A
level/change generated checks             -> "N/A"
```

Use another fixture with zero normalization adjustment and zero Pretax Income. Prove the adjustment per share remains numeric `0.0` and normalized EPS equals reported EPS.

---

### Task 5: Extend dynamic Check and trusted-sheet tests

**Files:**
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_normalized_per_share.py`
- Test: `core/tests/test_normalization.py`

- [ ] **Step 1: Include the new catalog in per-share detection**

In `checker.py`, include `NORMALIZED_PER_SHARE_COMPONENT_CATALOG` in the family set that triggers `compute_per_share_series()`.

The checker already reconstructs `normalization` before per-share values. Pass both existing objects to `expected_value_for_component()`; do not add a second normalization recomputation.

- [ ] **Step 2: Add family metadata to Trainer index**

Import and merge `NORMALIZED_PER_SHARE_COMPONENT_CATALOG` in `core/trainer/workbook.py::group_components_by_family()`.

- [ ] **Step 3: Rely on existing trusted `Per Share Analysis` validation**

Do not add a new trusted-sheet branch. Existing validation already treats every non-practice cell on `Per Share Analysis` as trusted. Add regression tests proving tampering with either:

```text
After-Tax Normalization Adjustment link
Normalized Net Income link
NORMALIZED EPS LEVEL CHECK
NORMALIZED EPS CHANGE CHECK
```

fails before any practice-cell recoloring.

- [ ] **Step 4: Test live Normalization Judgment recomputation**

Using the share-enabled demo plus `DEMO_HK_Assumptions.json`:

1. choose the supplied non-recurring treatment;
2. enter an exact or equivalent normalized-EPS practice formula;
3. run Check and verify green;
4. change Normalization Judgment column F for the restructuring case to `Recurring`;
5. keep the stale cached normalized-EPS value;
6. run Check and verify it becomes red because dynamic expected normalized earnings changed;
7. update to the new correct value and verify green.

This must work without altering the reported diluted EPS family.

- [ ] **Step 5: Test `#N/A` Formula Check behavior**

For an expected `#N/A` normalized-per-share cell, prove:

```text
exact Answer-Key formula     -> green
equivalent =NA() cached #N/A -> green
fabricated cached 0.0        -> red
```

Use the existing cached-value injection helper; do not add another mechanism.

---

### Task 6: Full regression verification and documentation

**Files:**
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after implementation succeeds
- Do not modify: `TARGET.md`

- [ ] **Step 1: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
PYTHONPATH=. pytest core/tests/test_per_share.py -v
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

- [ ] **Step 2: Run the full historical suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing-test count in `RESULT.md`; do not pre-invent it.

- [ ] **Step 3: Verify ordinary demo remains unchanged**

```bash
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_BASE_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_BASE_Trainer.xlsx
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Require:

```text
62 families
259 practice cells
fresh Check 0 correct / 0 incorrect / 259 blank
Per Share Analysis absent
```

Then:

```bash
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -a example/DEMO_HK_Assumptions.json -o /tmp/DEMO_NORM_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_NORM_Trainer.xlsx
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_NORM_Trainer.xlsx
```

Require:

```text
66 families
279 practice cells
fresh Check 0 correct / 0 incorrect / 279 blank
Per Share Analysis absent
```

- [ ] **Step 4: Verify share-enabled surfaces**

Use the existing in-memory share-enabled demo helper rather than modifying `example/DEMO_HK_Standardized.json`.

Require:

```text
shares + no normalization:
70 families / 293 cells
Step 9F.3 families absent

shares + normalization:
78 families / 331 cells
four Step 9F.3 families / 18 cells
fresh Check 0 correct / 0 incorrect / 331 blank
```

- [ ] **Step 5: Verify CLI and deferred boundary**

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

Normal build must not execute forecast/scenario code.

- [ ] **Step 6: Update documentation**

Update `skills/bav-trainer/SKILL.md` to state:

```text
Step 9F.3 is gated on both explicit diluted weighted-average share history and active normalization cases.
Reported EPS remains reported.
Normalized EPS uses the current Normalization Judgment treatment.
Reported EPS + normalization adjustment/share reconciles to normalized EPS.
Reported EPS change + normalization effect reconciles to normalized EPS change.
No automatic claim is made that normalized EPS is economically superior or more predictive.
```

Update `RESULT.md` with exact test results, all four surface cases, `#N/A` evidence, live-treatment Check evidence, and trusted-link/check tamper evidence.

---

## Definition of done

Step 9F.3 is complete only when all of the following are true:

1. Ordinary no-share demo surfaces remain exactly 62/259 and 66/279.
2. Share-only surface remains exactly 70/293.
3. Share+normalization surface becomes exactly 78 families / 331 practice cells.
4. The four new normalized-per-share families appear only when both shares and normalization are present.
5. No new historical share inputs or assumptions are invented.
6. `Normalization Adjustment per Diluted Share` uses the existing after-tax normalization adjustment.
7. `Normalized Diluted EPS` uses the existing normalized Net Income.
8. The generated level bridge reconciles reported EPS + adjustment/share to normalized EPS when defined.
9. The generated change bridge reconciles reported EPS change + normalization effect to normalized EPS change when defined.
10. Zero normalization adjustment remains numeric zero and leaves normalized EPS equal to reported EPS.
11. Undefined nonzero tax-effected normalization propagates `#N/A` through normalized per-share values and Check.
12. Exact/equivalent `#N/A` formulas pass Check and fabricated zero fails.
13. Changing Normalization Judgment changes normalized-per-share dynamic expected values without changing reported EPS.
14. Tampering populated normalization links or generated reconciliation checks fails before recoloring.
15. Step 9F.1–9F.2 formulas remain unchanged.
16. `TARGET.md` remains unchanged.
17. Full `core/tests/` passes.
18. CLI remains `{ingest, build, check, list}` and normal build still does not run forecasting/valuation.
19. No basic-vs-diluted analysis, period-end share-count analysis, causal dilution labels, forecasting, valuation, or investment conclusions are introduced.

After completing Step 9F.3, stop and report changed files, exact test output, the four surface counts, normalized-EPS level/change reconciliation evidence, live Normalization Judgment evidence, `#N/A` evidence, and any new active historical-model issue found during implementation. Do not proceed to forecasting or valuation, and do not commit or push.