# Step 9D.1 — Historical ROE Operating / Financing Attribution

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `2ba3e65accbce9584aad8f6be74ad14c5ac7bfd6` (`step 9C2`, Step 9C.2 complete). Implement only Step 9D.1 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, all Step 9A source-completeness / tax / normalization / `#N/A` semantics, the complete Step 9B working-capital diagnostics, and the complete Step 9C RNOA level/change attribution surface. Do not add company-specific causal claims, automatic good/bad profitability or leverage labels, forecasting, valuation, segment analysis, ROU/deferred-tax alternative modeling, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Extend historical DuPont analysis from RNOA drivers to an exact operating-versus-financing attribution of ROE, so the learner can distinguish changes in operating return from changes caused by financial leverage and financing spread without inventing causal explanations.

**Architecture:** Keep the existing direct `ROE (decomposed) = RNOA + FLEV × Spread` formula unchanged. Add one focused `ROEAttributionSeries` that exposes the financing contribution at each comparable period and attributes period-to-period decomposed-ROE change into Operating Effect (`ΔRNOA`), Leverage Effect, and Spread Effect using symmetric midpoint weights. Add seven semantic families to the existing `ALT DuPont` sheet plus generated non-practice reconciliation checks. Dynamic Check must recompute all values under the learner's current classification treatment, while existing trusted-sheet validation protects the generated checks automatically.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `AnchorMetrics`, `ProfitabilityChangeSeries`, `UNDEFINED_RATIO`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and trusted-sheet validation for `ALT DuPont`.

**Spec:** `TARGET.md`, especially the interpretation requirement “Is an apparent improvement in ROE operating or financing-driven?”, operating/financing reformulation, RNOA / after-tax cost of debt / Spread / FLEV / ROE decomposition, historical dependency order, and the rule that diagnostic arithmetic must be distinguished from unsupported causal claims.

## Global Constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all existing Step 8 judgment behavior and treatment-conditioned Check.
- Preserve all Step 9A source-completeness, tax, normalization, and `#N/A` semantics.
- Preserve all 11 Step 9B working-capital families unchanged.
- Preserve all Step 9C.1 profitability-driver and Step 9C.2 profitability-change families unchanged.
- Use only the authoritative treatment-conditioned `AnchorMetrics`; do not resolve or reclassify source statements again.
- Preserve the existing level identity `ROE (decomposed) = RNOA + FLEV × Spread` unchanged.
- Define `Financing Contribution to ROE = FLEV × Spread` only when both inputs are defined.
- Change attribution begins only when two consecutive comparable ROE periods exist. In a five-period history this means fiscal-period indices `2, 3, 4`.
- First fiscal period is non-applicable for financing-contribution level analysis because FLEV / Spread are non-applicable there.
- First fiscal period and first comparable fiscal period are non-applicable for ROE change attribution.
- `Operating Effect on Change in ROE = Change in RNOA`.
- Attribute the change in `FLEV × Spread` symmetrically: do not assign the interaction term arbitrarily to leverage or spread.
- Preserve signs. Do not take absolute values of RNOA, FLEV, Spread, changes, or effects.
- Undefined required driver values propagate to `#N/A`; never fabricate zero effects.
- A numeric zero FLEV or Spread with the other input defined may produce a numeric zero financing contribution. Do not short-circuit `0 × #N/A` to zero; undefined inputs remain undefined.
- `Actual ROE` remains an independent reported-equity diagnostic. This checkpoint attributes **decomposed ROE**, not Actual ROE.
- Do not infer debt-policy quality, funding stress, management intent, cost-of-capital changes, or capital-allocation quality automatically from the arithmetic attribution.
- Do not add automatic quality scoring or free-form automatic grading.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Review of commit `2ba3e65a`

Step 9C.2 is complete and coherent:

- six RNOA-change families attribute direct `ΔRNOA` to NOPAT-Margin and NOA-Turnover effects;
- midpoint weighting gives an exact order-neutral product-change attribution;
- undefined Margin / Turnover inputs propagate to `#N/A` rather than fabricated zero effects;
- the generated `RNOA CHANGE DRIVER CHECK` is trusted and tamper-detected;
- live classification changes turnover-sensitive dynamic expected values;
- base demo is 51 families / 222 practice cells;
- normalization demo is 55 families / 242 practice cells;
- `RESULT.md` records 226 locally passing tests;
- GitHub has no attached CI status.

The remaining historical interpretation gap is the next question explicitly named in `TARGET.md`: whether an ROE movement is operating or financing-driven.

The current model already calculates:

```text
ROE = RNOA + FLEV × Spread
```

so define the financing contribution:

```text
Financing Contribution = FLEV × Spread
```

For period-to-period changes:

```text
Change in ROE
= Change in RNOA
+ Change in (FLEV × Spread)
```

Decompose the financing-product change symmetrically:

```text
Leverage Effect
= (FLEV_t - FLEV_(t-1))
  × (Spread_t + Spread_(t-1)) / 2

Spread Effect
= (Spread_t - Spread_(t-1))
  × (FLEV_t + FLEV_(t-1)) / 2

Financing Effect
= Leverage Effect + Spread Effect

Change in ROE from Drivers
= Operating Effect + Financing Effect
```

where:

```text
Operating Effect = Change in RNOA
```

This is exact when all required inputs are defined. It is an arithmetic attribution, not a causal model of financing policy.

---

### Task 1: Add authoritative ROE operating / financing attribution series

**Files:**
- Create: `core/model/roe_attribution.py`
- Create: `core/tests/test_roe_attribution.py`

**Interfaces:**
- Consumes: `AnchorMetrics`, `compute_profitability_change_series(anchor)`, `UNDEFINED_RATIO`.
- Produces: `ROEAttributionSeries` and `compute_roe_attribution_series(anchor)`.

- [ ] **Step 1: Write the failing data-model and ordinary-case test**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .profitability_change import compute_profitability_change_series
from .ratio_values import UNDEFINED_RATIO


@dataclass(frozen=True)
class ROEAttributionSeries:
    financing_contribution_to_roe: tuple[float | str | None, ...]
    roe_change: tuple[float | str | None, ...]
    operating_effect_on_roe_change: tuple[float | str | None, ...]
    leverage_effect_on_roe_change: tuple[float | str | None, ...]
    spread_effect_on_roe_change: tuple[float | str | None, ...]
    financing_effect_on_roe_change: tuple[float | str | None, ...]
    roe_change_from_drivers: tuple[float | str | None, ...]
```

Test an ordinary numeric case such as:

```text
Prior RNOA   = 12%
Current RNOA = 15%
Prior FLEV   = 0.40x
Current FLEV = 0.50x
Prior Spread = 4%
Current Spread = 6%
Prior ROE    = 13.6%
Current ROE  = 18.0%
```

Expected:

```text
Prior financing contribution   = 0.40 × 0.04 = 0.016
Current financing contribution = 0.50 × 0.06 = 0.030
Direct Change in ROE           = 0.044
Operating Effect               = 0.030
Leverage Effect                = 0.10 × 0.05 = 0.005
Spread Effect                  = 0.02 × 0.45 = 0.009
Financing Effect               = 0.014
Change in ROE from Drivers     = 0.044
```

- [ ] **Step 2: Run the focused test and verify red state**

```bash
PYTHONPATH=. pytest core/tests/test_roe_attribution.py -v
```

Expected: fail because `core.model.roe_attribution` does not yet exist.

- [ ] **Step 3: Implement source-series validation and helpers**

Create:

```python
def _difference_or_na(current, prior) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)


def _product_or_na(left, right) -> float | str:
    if left == UNDEFINED_RATIO or right == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(left) * float(right)
```

Then begin:

```python
def compute_roe_attribution_series(
    anchor: AnchorMetrics,
) -> ROEAttributionSeries:
    profitability_change = compute_profitability_change_series(anchor)
    rnoa = tuple(anchor.dupont["RNOA"])
    flev = tuple(anchor.dupont["FLEV"])
    spread = tuple(anchor.dupont["Spread"])
    roe = tuple(anchor.dupont["ROE (decomposed)"])

    lengths = {
        "RNOA": len(rnoa),
        "FLEV": len(flev),
        "Spread": len(spread),
        "ROE (decomposed)": len(roe),
        "RNOA change": len(profitability_change.rnoa_change),
    }
    if len(set(lengths.values())) != 1 or lengths["RNOA"] == 0:
        raise ValueError(
            "ROE-attribution series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )
```

- [ ] **Step 4: Implement financing-contribution level series**

Initialize:

```python
n = len(rnoa)
financing_contribution: list[float | str | None] = [None] * n
```

For `i >= 1`:

```python
contribution = _product_or_na(flev[i], spread[i])
financing_contribution[i] = contribution

if contribution != UNDEFINED_RATIO:
    if rnoa[i] == UNDEFINED_RATIO or roe[i] == UNDEFINED_RATIO:
        raise ValueError(
            "ROE financing contribution is numeric while level ROE identity is undefined: "
            f"period_index={i} contribution={contribution}"
        )
    level_roe = float(rnoa[i]) + float(contribution)
    if abs(level_roe - float(roe[i])) > 1e-9:
        raise ValueError(
            "ROE operating/financing level bridge does not reconcile: "
            f"period_index={i} direct={roe[i]} bridge={level_roe}"
        )
```

Do not define a financing contribution for index `0` because FLEV / Spread are non-applicable there.

- [ ] **Step 5: Implement change-attribution series**

Initialize:

```python
roe_change: list[float | str | None] = [None] * n
operating_effect: list[float | str | None] = [None] * n
leverage_effect: list[float | str | None] = [None] * n
spread_effect: list[float | str | None] = [None] * n
financing_effect: list[float | str | None] = [None] * n
driver_change: list[float | str | None] = [None] * n
```

For every `i >= 2`:

```python
direct_delta = _difference_or_na(roe[i], roe[i - 1])
operating = profitability_change.rnoa_change[i]
assert operating is not None

roe_change[i] = direct_delta
operating_effect[i] = operating

required_financing = (
    flev[i],
    flev[i - 1],
    spread[i],
    spread[i - 1],
)
if any(value == UNDEFINED_RATIO for value in required_financing):
    leverage_effect[i] = UNDEFINED_RATIO
    spread_effect[i] = UNDEFINED_RATIO
    financing_effect[i] = UNDEFINED_RATIO
else:
    leverage_value = (
        (float(flev[i]) - float(flev[i - 1]))
        * (float(spread[i]) + float(spread[i - 1]))
        / 2.0
    )
    spread_value = (
        (float(spread[i]) - float(spread[i - 1]))
        * (float(flev[i]) + float(flev[i - 1]))
        / 2.0
    )
    financing_value = leverage_value + spread_value

    leverage_effect[i] = leverage_value
    spread_effect[i] = spread_value
    financing_effect[i] = financing_value
```

Then:

```python
if operating == UNDEFINED_RATIO or financing_effect[i] == UNDEFINED_RATIO:
    driver_change[i] = UNDEFINED_RATIO
else:
    driver_change[i] = float(operating) + float(financing_effect[i])
```

- [ ] **Step 6: Add independent financing-change and total-ROE reconciliation checks**

When `financing_effect[i]` is numeric and both financing-contribution levels are numeric:

```python
current_contribution = financing_contribution[i]
prior_contribution = financing_contribution[i - 1]
assert current_contribution is not None
assert prior_contribution is not None

if (
    current_contribution != UNDEFINED_RATIO
    and prior_contribution != UNDEFINED_RATIO
):
    direct_financing_change = (
        float(current_contribution) - float(prior_contribution)
    )
    if abs(float(financing_effect[i]) - direct_financing_change) > 1e-9:
        raise ValueError(
            "ROE financing-effect attribution does not reconcile: "
            f"period_index={i} direct={direct_financing_change} "
            f"driver={financing_effect[i]}"
        )
```

When `driver_change[i]` is numeric:

```python
if direct_delta == UNDEFINED_RATIO:
    raise ValueError(
        "ROE driver attribution is numeric while direct ROE change is undefined: "
        f"period_index={i} driver={driver_change[i]}"
    )
if abs(float(driver_change[i]) - float(direct_delta)) > 1e-9:
    raise ValueError(
        "ROE operating/financing change attribution does not reconcile: "
        f"period_index={i} direct={direct_delta} driver={driver_change[i]}"
    )
```

If the driver attribution is `#N/A`, do not require direct ROE change to be `#N/A`.

- [ ] **Step 7: Return all seven series**

```python
return ROEAttributionSeries(
    financing_contribution_to_roe=tuple(financing_contribution),
    roe_change=tuple(roe_change),
    operating_effect_on_roe_change=tuple(operating_effect),
    leverage_effect_on_roe_change=tuple(leverage_effect),
    spread_effect_on_roe_change=tuple(spread_effect),
    financing_effect_on_roe_change=tuple(financing_effect),
    roe_change_from_drivers=tuple(driver_change),
)
```

- [ ] **Step 8: Add edge-case tests**

Add tests proving:

```text
index 0 financing contribution                        -> None
indices 0 and 1 all change-attribution series        -> None
numeric zero FLEV with defined Spread                -> financing contribution 0.0
numeric zero Spread with defined FLEV                -> financing contribution 0.0
FLEV #N/A or Spread #N/A                             -> financing contribution #N/A
0 × #N/A                                              -> #N/A, not 0.0
unchanged RNOA                                        -> Operating Effect 0.0
unchanged FLEV with all financing inputs defined      -> Leverage Effect 0.0
unchanged Spread with all financing inputs defined    -> Spread Effect 0.0
negative FLEV / Spread changes                        -> signed effects retained
undefined current/prior FLEV or Spread                -> financing effects #N/A
undefined Operating Effect                            -> total driver Change in ROE #N/A
numeric driver attribution + mismatched direct ROE    -> ValueError
numeric financing effects + mismatched contribution   -> ValueError
series-length mismatch                                -> clear ValueError
```

- [ ] **Step 9: Run focused tests to green**

```bash
PYTHONPATH=. pytest core/tests/test_roe_attribution.py -v
```

Expected: all tests pass.

---

### Task 2: Add seven semantic ROE-attribution families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_roe_attribution.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: `ROEAttributionSeries` from Task 1.
- Produces: seven semantic families and dynamic expected values.

- [ ] **Step 1: Add a separate component catalog**

Create:

```python
ROE_ATTRIBUTION_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (...)
```

Use family orders `56` through `62`.

Define exactly:

```text
56  financing_contribution_to_roe
57  roe_change
58  operating_effect_on_roe_change
59  leverage_effect_on_roe_change
60  spread_effect_on_roe_change
61  financing_effect_on_roe_change
62  roe_change_from_drivers
```

`financing_contribution_to_roe` is a `comparable` family (`i >= 1`). The remaining six are `post_comparable` families (`i >= 2`).

- [ ] **Step 2: Define the financing-contribution family**

```python
ComponentFamily(
    id="financing_contribution_to_roe",
    order=56,
    title="Financing Contribution to ROE",
    short_hint="FLEV multiplied by Spread.",
    semantic_key="roe_attribution.financing_contribution",
    category="roe_attribution",
    tab_template="ALT DuPont",
    period_scope="comparable",
    depends_on_current=("flev", "spread"),
    hints=(
        "Financing Contribution to ROE = FLEV × Spread.",
        "A positive contribution raises decomposed ROE above RNOA; a negative contribution lowers it.",
        "Do not call the contribution good or bad without understanding leverage and financing economics.",
    ),
)
```

- [ ] **Step 3: Define the six post-comparable change families**

```python
ComponentFamily(
    id="roe_change",
    order=57,
    title="Direct Change in Decomposed ROE",
    short_hint="Current decomposed ROE minus prior decomposed ROE.",
    semantic_key="roe_attribution.roe_change",
    category="roe_attribution",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("roe_decomp",),
    depends_on_previous=("roe_decomp",),
    hints=(
        "Direct Change in ROE = Current decomposed ROE - Prior decomposed ROE.",
    ),
)
```

```python
ComponentFamily(
    id="operating_effect_on_roe_change",
    order=58,
    title="Operating Effect on Change in ROE",
    short_hint="The direct Change in RNOA from the prior diagnostic section.",
    semantic_key="roe_attribution.operating_effect",
    category="roe_attribution",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("rnoa_change",),
    hints=(
        "Operating Effect on Change in ROE = Change in RNOA.",
        "Use the existing direct RNOA-change result; do not reassign financing effects into the operating term.",
    ),
)
```

```python
ComponentFamily(
    id="leverage_effect_on_roe_change",
    order=59,
    title="Leverage Effect on Change in ROE",
    short_hint="Change in FLEV multiplied by midpoint Spread.",
    semantic_key="roe_attribution.leverage_effect",
    category="roe_attribution",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("flev", "spread"),
    depends_on_previous=("flev", "spread"),
    hints=(
        "Leverage Effect = Change in FLEV × average of current and prior Spread.",
        "Midpoint weighting gives an exact order-neutral attribution of the financing product change.",
    ),
)
```

```python
ComponentFamily(
    id="spread_effect_on_roe_change",
    order=60,
    title="Spread Effect on Change in ROE",
    short_hint="Change in Spread multiplied by midpoint FLEV.",
    semantic_key="roe_attribution.spread_effect",
    category="roe_attribution",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("spread", "flev"),
    depends_on_previous=("spread", "flev"),
    hints=(
        "Spread Effect = Change in Spread × average of current and prior FLEV.",
        "Do not interpret Spread movement as a specific financing-policy cause without additional evidence.",
    ),
)
```

```python
ComponentFamily(
    id="financing_effect_on_roe_change",
    order=61,
    title="Financing Effect on Change in ROE",
    short_hint="Leverage Effect plus Spread Effect.",
    semantic_key="roe_attribution.financing_effect",
    category="roe_attribution",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=(
        "leverage_effect_on_roe_change",
        "spread_effect_on_roe_change",
    ),
    hints=(
        "Financing Effect = Leverage Effect + Spread Effect.",
        "This equals the change in FLEV × Spread when all required inputs are defined.",
    ),
)
```

```python
ComponentFamily(
    id="roe_change_from_drivers",
    order=62,
    title="Change in ROE from Operating + Financing Drivers",
    short_hint="Operating Effect plus Financing Effect.",
    semantic_key="roe_attribution.roe_change_from_drivers",
    category="roe_attribution",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=(
        "operating_effect_on_roe_change",
        "financing_effect_on_roe_change",
    ),
    hints=(
        "Change in ROE from Drivers = Operating Effect + Financing Effect.",
        "When all required terms are defined, this must reconcile to Direct Change in Decomposed ROE.",
    ),
)
```

- [ ] **Step 4: Add a dedicated spec expander**

Create:

```python
def expand_roe_attribution_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    ...
```

Validate duplicate / non-chronological periods exactly as the other expanders do.

Expansion rule:

```python
if family.period_scope == "comparable":
    indices = range(1, len(periods))
elif family.period_scope == "post_comparable":
    indices = range(2, len(periods))
else:
    raise ValueError(
        f"unsupported ROE-attribution period_scope {family.period_scope!r}"
    )
```

Use `concrete_component_id()` and existing current/previous dependency expansion.

For five fiscal periods:

```text
Financing Contribution: 1 family × 4 comparable periods = 4 cells
Change attribution:      6 families × 3 post-comparable periods = 18 cells
Total Step 9D.1:         7 families / 22 practice cells
```

- [ ] **Step 5: Add expected-series mapping**

In `core/model/historical_expected.py`, import:

```python
from ..engine.component_catalog import ROE_ATTRIBUTION_COMPONENT_CATALOG
from .roe_attribution import compute_roe_attribution_series
```

Add:

```python
_ROE_ATTRIBUTION_FAMILY_SERIES = (
    "financing_contribution_to_roe",
    "roe_change",
    "operating_effect_on_roe_change",
    "leverage_effect_on_roe_change",
    "spread_effect_on_roe_change",
    "financing_effect_on_roe_change",
    "roe_change_from_drivers",
)
```

Create:

```python
def roe_attribution_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    values = compute_roe_attribution_series(anchor)
    series = {
        "financing_contribution_to_roe": values.financing_contribution_to_roe,
        "roe_change": values.roe_change,
        "operating_effect_on_roe_change": values.operating_effect_on_roe_change,
        "leverage_effect_on_roe_change": values.leverage_effect_on_roe_change,
        "spread_effect_on_roe_change": values.spread_effect_on_roe_change,
        "financing_effect_on_roe_change": values.financing_effect_on_roe_change,
        "roe_change_from_drivers": values.roe_change_from_drivers,
    }
    expected_ids = {family.id for family in ROE_ATTRIBUTION_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "roe_attribution_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _ROE_ATTRIBUTION_FAMILY_SERIES
    }
```

Extend `expected_value_for_component()` with an ROE-attribution branch before falling back to the historical core families.

- [ ] **Step 6: Add catalog/expansion regressions**

Add tests proving:

```text
catalog IDs are exactly the seven listed above
family orders are 56..62
one family is comparable; six are post_comparable
five fiscal periods expand to exactly 22 concrete specs
expected-series keys exactly equal catalog IDs
existing Step 9C.1 / Step 9C.2 catalogs remain unchanged
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_roe_attribution.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "roe_attribution or financing_contribution" -v
```

---

### Task 3: Wire ROE attribution into `ReferenceModelBuilder`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_roe_attribution.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: `compute_roe_attribution_series()` and `expand_roe_attribution_specs()`.
- Produces: registered semantic practice components on `ALT DuPont`.

- [ ] **Step 1: Add imports and builder state**

Import:

```python
from ..model.roe_attribution import compute_roe_attribution_series
```

and:

```python
from .component_catalog import expand_roe_attribution_specs
```

After existing profitability-change setup:

```python
self.roe_attribution_series = compute_roe_attribution_series(self.anchor)
self.roe_attribution_specs = expand_roe_attribution_specs(
    self.periods,
    start_order=(
        len(self.historical_specs)
        + len(self.normalization_specs)
        + len(self.quality_specs)
        + len(self.working_capital_specs)
        + len(self.profitability_driver_specs)
        + len(self.profitability_change_specs)
        + 1
    ),
)
```

Append:

```python
self.expected_specs = (
    self.historical_specs
    + self.normalization_specs
    + self.quality_specs
    + self.working_capital_specs
    + self.profitability_driver_specs
    + self.profitability_change_specs
    + self.roe_attribution_specs
)
```

Create:

```python
self._roe_attribution_spec_index = {
    (s.family_id, s.period_index): s
    for s in self.roe_attribution_specs
}
```

- [ ] **Step 2: Add a focused registration helper**

```python
def _register_roe_attribution(
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
    spec = self._roe_attribution_spec_index[(family_id, period_index)]
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

- [ ] **Step 3: Run builder-focused tests and verify red state**

Before adding worksheet formulas, run:

```bash
PYTHONPATH=. pytest core/tests/test_roe_attribution.py core/tests/test_reference_integrity.py -k "roe_attribution or financing_contribution" -v
```

Expected: fail because expected semantic components are not yet registered.

---

### Task 4: Extend `ALT DuPont` with ROE operating / financing attribution

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_roe_attribution.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: existing local rows `rnoa_row`, `spread_row`, `flev_row`, `roe_row`, `direct_rnoa_change_row`, and Step 9C.2 `change_check_row` inside `_build_dupont()`.
- Produces: seven practice rows plus two generated trusted reconciliation rows.

- [ ] **Step 1: Add the level-attribution section after Step 9C.2**

Immediately after the Step 9C.2 section, create rows relative to its existing `change_check_row`:

```python
roe_section_row = change_check_row + 2
financing_contribution_row = roe_section_row + 1
roe_level_check_row = roe_section_row + 2
roe_change_section_row = roe_section_row + 4
direct_roe_change_row = roe_change_section_row + 1
operating_effect_row = roe_change_section_row + 2
leverage_effect_row = roe_change_section_row + 3
spread_effect_row = roe_change_section_row + 4
financing_effect_row = roe_change_section_row + 5
driver_roe_change_row = roe_change_section_row + 6
roe_change_check_row = roe_change_section_row + 7
```

Labels:

```text
ROE OPERATING / FINANCING ATTRIBUTION
Financing Contribution to ROE
ROE LEVEL ATTRIBUTION CHECK

ROE CHANGE ATTRIBUTION
Direct Change in Decomposed ROE
Operating Effect on Change in ROE
Leverage Effect on Change in ROE
Spread Effect on Change in ROE
Financing Effect on Change in ROE
Change in ROE from Drivers
ROE CHANGE ATTRIBUTION CHECK
```

Make both section headers and both generated check labels bold.

- [ ] **Step 2: Add first-period / applicability literals**

For fiscal-period index `0`:

```text
Financing Contribution to ROE -> N/A
ROE LEVEL ATTRIBUTION CHECK    -> N/A
all change-attribution rows    -> N/A
ROE CHANGE ATTRIBUTION CHECK   -> N/A
```

For fiscal-period index `1`:

```text
Financing Contribution to ROE -> active formula
ROE LEVEL ATTRIBUTION CHECK    -> active generated check
all change-attribution rows    -> N/A
ROE CHANGE ATTRIBUTION CHECK   -> N/A
```

Do not register practice components where the catalog says the period is non-applicable.

- [ ] **Step 3: Add financing-contribution level formula and generated check**

For every `j >= 1`:

```python
financing_contribution = f"={out_col}{flev_row}*{out_col}{spread_row}"
level_check = (
    f'=IF(OR(ISNA({out_col}{rnoa_row}),'
    f'ISNA({out_col}{financing_contribution_row}),'
    f'ISNA({out_col}{roe_row})),"N/A",'
    f'IF(ABS({out_col}{rnoa_row}+{out_col}{financing_contribution_row}'
    f'-{out_col}{roe_row})<0.0000001,"OK","CHECK"))'
)
```

Write the financing contribution with `PCT_FMT`.

Register:

```python
self._register_roe_attribution(
    "financing_contribution_to_roe",
    j,
    "ALT DuPont",
    financing_contribution_row,
    out_col_idx,
    financing_contribution,
    expected,
)
```

Do **not** register `ROE LEVEL ATTRIBUTION CHECK`; it is a generated non-practice cell and existing trusted `ALT DuPont` validation must protect it.

- [ ] **Step 4: Add post-comparable change formulas**

For every `j >= 2`, let:

```python
prev_col = self._col(2 + j - 1)
```

Use:

```python
direct_roe_change = f"={out_col}{roe_row}-{prev_col}{roe_row}"
operating_effect = f"={out_col}{direct_rnoa_change_row}"
leverage_effect = (
    f"=({out_col}{flev_row}-{prev_col}{flev_row})*"
    f"(({out_col}{spread_row}+{prev_col}{spread_row})/2)"
)
spread_effect = (
    f"=({out_col}{spread_row}-{prev_col}{spread_row})*"
    f"(({out_col}{flev_row}+{prev_col}{flev_row})/2)"
)
financing_effect = f"={out_col}{leverage_effect_row}+{out_col}{spread_effect_row}"
driver_roe_change = f"={out_col}{operating_effect_row}+{out_col}{financing_effect_row}"
roe_change_check = (
    f'=IF(OR(ISNA({out_col}{driver_roe_change_row}),'
    f'ISNA({out_col}{direct_roe_change_row})),"N/A",'
    f'IF(ABS({out_col}{driver_roe_change_row}-{out_col}{direct_roe_change_row})'
    f'<0.0000001,"OK","CHECK"))'
)
```

Apply `PCT_FMT` to all six practice rows.

Do not wrap the effect formulas in `IFERROR(...,0)`. Excel must naturally propagate `#N/A` from undefined required inputs.

- [ ] **Step 5: Register the six post-comparable families**

For each `j >= 2`, register:

```text
roe_change
operating_effect_on_roe_change
leverage_effect_on_roe_change
spread_effect_on_roe_change
financing_effect_on_roe_change
roe_change_from_drivers
```

Use the matching fields from `self.roe_attribution_series`.

Do not register `ROE CHANGE ATTRIBUTION CHECK`.

- [ ] **Step 6: Store rowmap entries**

Add:

```python
self.rowmap["dupont_financing_contribution_row"] = financing_contribution_row
self.rowmap["dupont_roe_level_attribution_check_row"] = roe_level_check_row
self.rowmap["dupont_direct_roe_change_row"] = direct_roe_change_row
self.rowmap["dupont_operating_roe_effect_row"] = operating_effect_row
self.rowmap["dupont_leverage_roe_effect_row"] = leverage_effect_row
self.rowmap["dupont_spread_roe_effect_row"] = spread_effect_row
self.rowmap["dupont_financing_roe_effect_row"] = financing_effect_row
self.rowmap["dupont_driver_roe_change_row"] = driver_roe_change_row
self.rowmap["dupont_roe_change_attribution_check_row"] = roe_change_check_row
```

- [ ] **Step 7: Add worksheet-formula regressions**

Assert:

```text
financing contribution formula = FLEV × Spread
level check compares RNOA + financing contribution with decomposed ROE
operating effect links to the existing Direct Change in RNOA row
leverage effect uses ΔFLEV × midpoint Spread
spread effect uses ΔSpread × midpoint FLEV
financing effect sums leverage + spread effects
driver ROE change sums operating + financing effects
change check compares driver Change in ROE with direct decomposed-ROE change
no ABS() appears in any practice effect/change formula
no IFERROR(...,0) or other zero fallback is introduced
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_roe_attribution.py core/tests/test_reference_integrity.py -k "roe_attribution or financing_contribution" -v
```

Expected: green.

---

### Task 5: Prove dynamic Check, `#N/A`, and trusted-sheet behavior

**Files:**
- Modify: `core/tests/test_roe_attribution.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_trainer.py` only if a generic cached-value helper is needed

**Interfaces:**
- Consumes: normal `check_workbook()` dynamic expected-value recomputation.
- Produces: regressions proving Step 9D.1 participates in the existing live/trusted model boundary.

- [ ] **Step 1: Add live-classification regression**

Reuse an existing classification judgment fixture such as the lease-liability treatment switch where changing:

```text
Financial Liability
-> Operating Long-Term Liability
```

changes treatment-conditioned Net Debt / NOA while leaving reported source facts unchanged.

Assert that at least these Step 9D.1 expected values change under the alternate treatment where mathematically applicable:

```text
Financing Contribution to ROE
Leverage Effect on Change in ROE
Financing Effect on Change in ROE
Change in ROE from Drivers
```

Then enter formulas/cached values consistent with the learner's selected treatment and require Check to mark them green.

- [ ] **Step 2: Add undefined-input regression**

Build a fixture where one required FLEV or Spread period is `#N/A` under existing historical semantics.

Assert Python expected values propagate:

```text
Financing Contribution -> #N/A
Leverage / Spread Effects when required period is undefined -> #N/A
Financing Effect -> #N/A
Driver Change in ROE -> #N/A when financing attribution is required
```

Do not fabricate `0.0`.

- [ ] **Step 3: Add exact/equivalent `#N/A` Check regression**

For one Step 9D.1 practice cell whose expected result is `#N/A`:

1. exact Answer-Key formula -> green;
2. structurally different learner formula with cached `#N/A` -> green;
3. learner formula / cached numeric `0.0` -> red.

Reuse the existing cached-error injection helper rather than adding production-only evaluation logic.

- [ ] **Step 4: Add trusted generated-check tamper regressions**

Build a normal Trainer/Answer-Key pair, put one valid Step 9D.1 learner formula in a practice cell, then separately tamper:

```text
ROE LEVEL ATTRIBUTION CHECK
ROE CHANGE ATTRIBUTION CHECK
```

in the Trainer.

For each tamper:

```python
with pytest.raises(ValueError, match="Trusted workbook cell was modified"):
    check_workbook(trainer_path)
```

Reopen the workbook and prove the learner practice cell remains yellow: no partial recoloring before structural failure.

No `check_context.py` production change should be needed because `ALT DuPont` is already a trusted sheet outside semantic practice cells.

- [ ] **Step 5: Run focused Check tests**

```bash
PYTHONPATH=. pytest core/tests/test_roe_attribution.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "roe_attribution or financing_contribution or trusted" -v
```

Expected: green.

---

### Task 6: Integrate family metadata and preserve the curriculum surface

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: count assertions in `core/tests/test_reference_integrity.py`, `core/tests/test_trainer.py`, and other tests that intentionally pin the complete demo surface

- [ ] **Step 1: Add ROE-attribution catalog to Trainer family metadata**

Import:

```python
ROE_ATTRIBUTION_COMPONENT_CATALOG
```

and extend `group_components_by_family()`:

```python
family_meta.update({f.id: f for f in ROE_ATTRIBUTION_COMPONENT_CATALOG})
```

The `list` command / Trainer index must display the seven new schedules in orders `56..62`.

- [ ] **Step 2: Update demo acceptance counts**

Step 9D.1 adds:

```text
7 families
22 practice cells
```

Therefore the five-year demo surfaces become:

```text
base demo:
58 families
244 practice cells

normalization demo:
62 families
264 practice cells
```

Update only assertions/documentation that intentionally pin the complete current demo surface. Do not hard-code these counts into generic company logic.

- [ ] **Step 3: Update skill documentation**

Update `skills/bav-trainer/SKILL.md` to state that the historical diagnostic surface now includes:

```text
Financing Contribution to ROE = FLEV × Spread
ROE change attribution = Operating Effect + Financing Effect
Financing Effect = Leverage Effect + Spread Effect
```

Retain the warning that these are arithmetic diagnostics, not automatic judgments about leverage quality or financing policy.

---

### Task 7: Full regression and checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all verification passes
- Do not modify: `TARGET.md`

- [ ] **Step 1: Run focused new suites**

```bash
PYTHONPATH=. pytest core/tests/test_roe_attribution.py -v
PYTHONPATH=. pytest core/tests/test_profitability_change.py -v
PYTHONPATH=. pytest core/tests/test_profitability_drivers.py -v
```

- [ ] **Step 2: Run existing high-risk regressions**

```bash
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

- [ ] **Step 3: Run the complete suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count in `RESULT.md`; do not predict it in advance.

- [ ] **Step 4: Verify the base demo**

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
Components resolved: 244
Checked 244 practice cells: 0 correct, 0 incorrect, 244 blank.
58 schedule groups
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
Components resolved: 264
Checked 264 practice cells: 0 correct, 0 incorrect, 264 blank.
62 schedule groups
```

- [ ] **Step 6: Verify CLI scope**

```bash
PYTHONPATH=. python -m core --help
```

Public commands must remain:

```text
ingest
build
check
list
```

- [ ] **Step 7: Update checkpoint evidence**

`RESULT.md` must record:

```text
actual full-suite pass count
base 58 / 244 surface
normalization 62 / 264 surface
Financing Contribution = FLEV × Spread
Operating Effect = Change in RNOA
Leverage Effect midpoint attribution
Spread Effect midpoint attribution
Financing Effect = Leverage + Spread effects
Operating + Financing effects reconcile to direct decomposed-ROE change when defined
undefined FLEV / Spread states propagate to #N/A
live classification-conditioned ROE attribution passes Check
generated ROE level/change checks are trusted and tamper-detected
no automatic leverage-quality or financing-policy judgment added
forecasting and valuation not begun
TARGET.md unchanged
```

Only after all verification passes, prepend a concise completion-status line to `IMPLEMENTATION.md`. Do not rewrite the plan body.

---

## Definition of done

Step 9D.1 is complete only when all of the following are true:

1. `Financing Contribution to ROE = FLEV × Spread` exists as a comparable-period formula family.
2. The level bridge `RNOA + Financing Contribution = ROE (decomposed)` reconciles when defined.
3. Direct Change in Decomposed ROE exists only for post-comparable periods.
4. Operating Effect equals direct Change in RNOA.
5. Leverage Effect uses `ΔFLEV × midpoint Spread`.
6. Spread Effect uses `ΔSpread × midpoint FLEV`.
7. Leverage Effect + Spread Effect equals the change in financing contribution when defined.
8. Financing Effect equals Leverage Effect + Spread Effect.
9. Operating Effect + Financing Effect equals Direct Change in Decomposed ROE when defined.
10. Undefined required FLEV / Spread / RNOA states propagate to `#N/A`; no fabricated zero effect is introduced.
11. `0 × #N/A` remains undefined; only fully defined zero products become numeric `0.0`.
12. First-period / first-comparable applicability remains explicit `N/A`, not numeric zero.
13. Live classification judgment changes relevant Step 9D.1 dynamic expected values.
14. Exact and equivalent formulas continue to pass under dynamic Check, including expected `#N/A` cases.
15. Tampering either generated ROE attribution check fails before any learner-cell recoloring.
16. Existing Step 8, Step 9A, Step 9B, and Step 9C families remain unchanged.
17. Base demo surface is 58 families / 244 practice cells.
18. Normalization demo surface is 62 families / 264 practice cells.
19. Full test suite passes.
20. CLI remains `{ingest,build,check,list}` only.
21. `TARGET.md` is unchanged.
22. No forecasting, valuation, segment analysis, automatic leverage-quality judgment, or company-specific financing causality has been introduced.

After completing Step 9D.1, stop and report changed files, exact test output, demo build/check/list output, level/change reconciliation evidence, live-classification evidence, and any new active historical-model issue found during implementation. Do not proceed to forecasting or valuation, and do not commit or push.
