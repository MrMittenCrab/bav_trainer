# Step 9C.2 — Historical RNOA Change Attribution

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `536d5e6d3348de7619789f618fe661ab1cce9fca` (`Step 9C1`, Step 9C.1 complete). Implement only Step 9C.2 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, all Step 9A source-completeness / tax / normalization / `#N/A` semantics, the complete Step 9B working-capital diagnostics, and the complete Step 9C.1 RNOA level decomposition. Do not add company-specific causal claims, automatic good/bad profitability labels, forecasting, valuation, segment analysis, ROU/deferred-tax alternative modeling, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Convert the existing RNOA level decomposition into an exact historical change attribution so the learner can quantify how much of a period-to-period RNOA movement came from NOPAT Margin versus NOA Turnover, without inventing causal explanations.

**Architecture:** Keep Step 9C.1 level drivers unchanged. Add one focused `ProfitabilityChangeSeries` that consumes the already treatment-conditioned NOPAT Margin, NOA Turnover, and direct RNOA series. Attribute product changes symmetrically with midpoint weights so `Change in RNOA = Margin Effect + Turnover Effect` exactly when both driver periods are defined. Add six post-comparable formula families to `ALT DuPont` plus one generated non-practice reconciliation row. Dynamic Check must recompute all values under the learner's current classification treatment, while trusted-sheet validation protects the generated reconciliation formula automatically.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `AnchorMetrics`, `ProfitabilityDriverSeries`, `UNDEFINED_RATIO`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and existing trusted-sheet validation for `ALT DuPont`.

**Spec:** `TARGET.md`, especially the interpretation requirement “Was a decline in RNOA caused by lower operating margins or greater NOA intensity?”, the historical dependency graph, capital-intensity diagnostics, accounting consistency, and the rule that diagnostic arithmetic must be distinguished from unsupported causal claims.

## Global Constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all existing Step 8 judgment behavior and treatment-conditioned Check.
- Preserve all Step 9A source-completeness and established `#N/A` semantics.
- Preserve all 11 Step 9B working-capital families unchanged.
- Preserve all four Step 9C.1 profitability-driver families and their formulas unchanged.
- Use only the authoritative treatment-conditioned `AnchorMetrics`; do not resolve or reclassify source statements again.
- The level identity remains `RNOA = NOPAT Margin × NOA Turnover` where defined.
- Change attribution begins only when two consecutive **comparable** RNOA periods exist. In a five-period history this means fiscal-period indices `2, 3, 4`.
- First fiscal period and first comparable fiscal period are non-applicable for RNOA change attribution.
- Use an exact symmetric midpoint decomposition; do not assign the interaction term arbitrarily to Margin or Turnover.
- Preserve signs. Do not take absolute values of margins, turnover, changes, or effects.
- Undefined required driver values propagate to `#N/A`; never fabricate zero effects.
- A zero change in one driver with all other required values defined produces a numeric zero effect.
- Do not interpret the Margin Effect as pricing/cost causality automatically.
- Do not interpret the Turnover Effect as asset-quality, utilization, acquisition, or working-capital causality automatically.
- NOA Intensity remains a useful reciprocal diagnostic from Step 9C.1, but this checkpoint attributes RNOA changes using NOA Turnover because the multiplicative identity is `Margin × Turnover`.
- Do not add automatic quality scoring or free-form automatic grading.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Review of commit `536d5e6d`

Step 9C.1 is complete and coherent:

- `ALT DuPont` now exposes Average NOA, NOA Turnover, NOA Intensity, and RNOA from Margin × Turnover;
- the level driver RNOA reconciles to direct RNOA whenever the decomposition is defined;
- zero Average NOA / Revenue use established `#N/A` semantics;
- live classification changes the treatment-conditioned Average NOA / turnover / intensity / driver RNOA;
- the generated `RNOA DRIVER CHECK` is trusted and tamper-detected;
- base demo is 45 families / 204 practice cells;
- normalization demo is 49 families / 224 practice cells;
- `RESULT.md` records 219 locally passing tests;
- GitHub has no attached CI status.

The remaining gap is that Step 9C.1 shows **driver levels**, but the target question is about **driver changes**. Comparing two RNOA periods mechanically requires attributing the change in a product:

```text
RNOA_t = Margin_t × Turnover_t
RNOA_(t-1) = Margin_(t-1) × Turnover_(t-1)
```

Use the symmetric midpoint identity:

```text
Margin Effect
= (Margin_t - Margin_(t-1))
  × (Turnover_t + Turnover_(t-1)) / 2

Turnover Effect
= (Turnover_t - Turnover_(t-1))
  × (Margin_t + Margin_(t-1)) / 2

Change in RNOA
= Margin Effect + Turnover Effect
```

This is exact, order-neutral, and avoids hiding the interaction term inside one driver. It is an arithmetic attribution, not a causal model.

---

### Task 1: Add authoritative RNOA change-attribution series

**Files:**
- Create: `core/model/profitability_change.py`
- Test: `core/tests/test_profitability_change.py`

**Interfaces:**
- Consumes: `AnchorMetrics`, `compute_profitability_driver_series(anchor)`, `UNDEFINED_RATIO`.
- Produces: `ProfitabilityChangeSeries` and `compute_profitability_change_series(anchor)`.

- [ ] **Step 1: Write the failing data-model and ordinary-case test**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .profitability_drivers import compute_profitability_driver_series
from .ratio_values import UNDEFINED_RATIO


@dataclass(frozen=True)
class ProfitabilityChangeSeries:
    nopat_margin_change: tuple[float | str | None, ...]
    noa_turnover_change: tuple[float | str | None, ...]
    rnoa_change: tuple[float | str | None, ...]
    margin_effect_on_rnoa: tuple[float | str | None, ...]
    turnover_effect_on_rnoa: tuple[float | str | None, ...]
    rnoa_change_from_drivers: tuple[float | str | None, ...]
```

Test an ordinary numeric case where:

```text
Prior Margin    = 10%
Current Margin  = 12%
Prior Turnover  = 2.0x
Current Turnover= 2.5x
Prior RNOA      = 20%
Current RNOA    = 30%
```

Expected:

```text
Margin change   = +2.0%
Turnover change = +0.5x
Margin effect   = 0.02 × 2.25 = 0.045
Turnover effect = 0.50 × 0.11 = 0.055
Driver ΔRNOA    = 0.100
Direct ΔRNOA    = 0.100
```

- [ ] **Step 2: Run the focused test and verify red state**

```bash
PYTHONPATH=. pytest core/tests/test_profitability_change.py -v
```

Expected: fail because the module / series does not yet exist.

- [ ] **Step 3: Implement source-series validation and non-applicable periods**

Create:

```python
def compute_profitability_change_series(
    anchor: AnchorMetrics,
) -> ProfitabilityChangeSeries:
    drivers = compute_profitability_driver_series(anchor)
    margin = tuple(anchor.dupont["NOPAT Margin"])
    turnover = tuple(drivers.noa_turnover)
    direct_rnoa = tuple(anchor.dupont["RNOA"])

    lengths = {
        "NOPAT Margin": len(margin),
        "NOA Turnover": len(turnover),
        "RNOA": len(direct_rnoa),
    }
    if len(set(lengths.values())) != 1 or lengths["RNOA"] == 0:
        raise ValueError(
            "profitability-change series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    n = len(direct_rnoa)
    margin_change: list[float | str | None] = [None] * n
    turnover_change: list[float | str | None] = [None] * n
    rnoa_change: list[float | str | None] = [None] * n
    margin_effect: list[float | str | None] = [None] * n
    turnover_effect: list[float | str | None] = [None] * n
    driver_change: list[float | str | None] = [None] * n
```

Do not compute attribution for indices `0` or `1`.

- [ ] **Step 4: Implement exact symmetric midpoint attribution**

Inside:

```python
for i in range(2, n):
```

use a local helper:

```python
def difference_or_na(current, prior) -> float | str:
    if current == UNDEFINED_RATIO or prior == UNDEFINED_RATIO:
        return UNDEFINED_RATIO
    return float(current) - float(prior)
```

Then:

```python
margin_delta = difference_or_na(margin[i], margin[i - 1])
turnover_delta = difference_or_na(turnover[i], turnover[i - 1])
direct_delta = difference_or_na(direct_rnoa[i], direct_rnoa[i - 1])

margin_change[i] = margin_delta
turnover_change[i] = turnover_delta
rnoa_change[i] = direct_delta

required = (
    margin[i],
    margin[i - 1],
    turnover[i],
    turnover[i - 1],
)
if any(value == UNDEFINED_RATIO for value in required):
    margin_effect[i] = UNDEFINED_RATIO
    turnover_effect[i] = UNDEFINED_RATIO
    driver_change[i] = UNDEFINED_RATIO
else:
    margin_effect_value = (
        (float(margin[i]) - float(margin[i - 1]))
        * (float(turnover[i]) + float(turnover[i - 1]))
        / 2.0
    )
    turnover_effect_value = (
        (float(turnover[i]) - float(turnover[i - 1]))
        * (float(margin[i]) + float(margin[i - 1]))
        / 2.0
    )
    driver_delta = margin_effect_value + turnover_effect_value

    margin_effect[i] = margin_effect_value
    turnover_effect[i] = turnover_effect_value
    driver_change[i] = driver_delta
```

- [ ] **Step 5: Add reconciliation validation**

When `driver_change[i]` is numeric:

```python
if direct_delta == UNDEFINED_RATIO:
    raise ValueError(
        "RNOA change attribution is numeric while direct RNOA change is undefined: "
        f"period_index={i} driver={driver_change[i]}"
    )
if abs(float(driver_change[i]) - float(direct_delta)) > 1e-9:
    raise ValueError(
        "RNOA change attribution does not reconcile: "
        f"period_index={i} direct={direct_delta} driver={driver_change[i]}"
    )
```

If the driver attribution is `#N/A`, do not require the direct RNOA change to be `#N/A`. This preserves the Step 9C.1 case where Revenue can make Margin / Turnover decomposition undefined while direct RNOA remains numeric.

Return all six tuple series.

- [ ] **Step 6: Add edge-case tests**

Add tests proving:

```text
indices 0 and 1                               -> all six new series are None
unchanged Margin with defined Turnover        -> Margin Effect = 0.0
unchanged Turnover with defined Margin        -> Turnover Effect = 0.0
negative Margin change                        -> signed negative effect retained
negative Turnover change                      -> signed negative effect retained
undefined current/prior Margin                -> both effects and driver ΔRNOA #N/A
undefined current/prior Turnover              -> both effects and driver ΔRNOA #N/A
undefined driver attribution + numeric direct -> allowed, no false reconciliation error
numeric driver attribution + mismatched RNOA  -> ValueError
series-length mismatch                        -> clear ValueError
```

- [ ] **Step 7: Run focused tests to green**

```bash
PYTHONPATH=. pytest core/tests/test_profitability_change.py -v
```

Expected: all tests pass.

---

### Task 2: Add six semantic RNOA-change families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_profitability_change.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: `ProfitabilityChangeSeries` from Task 1.
- Produces: six semantic families and dynamic expected values.

- [ ] **Step 1: Add a separate catalog**

Create:

```python
PROFITABILITY_CHANGE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (...)
```

Use family orders `50` through `55`. All six families are applicable only from period index `2` onward.

Define exactly:

```text
50  nopat_margin_change
51  noa_turnover_change
52  rnoa_change
53  rnoa_margin_effect
54  rnoa_turnover_effect
55  rnoa_change_from_drivers
```

Family details:

```python
ComponentFamily(
    id="nopat_margin_change",
    order=50,
    title="Change in NOPAT Margin",
    short_hint="Current NOPAT Margin minus prior comparable NOPAT Margin.",
    semantic_key="profitability_change.nopat_margin_change",
    category="profitability_change",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("nopat_margin",),
    depends_on_previous=("nopat_margin",),
    hints=(
        "Change in NOPAT Margin = Current Margin - Prior Margin.",
        "This is an arithmetic movement, not a causal explanation of pricing or costs.",
    ),
)
```

```python
ComponentFamily(
    id="noa_turnover_change",
    order=51,
    title="Change in NOA Turnover",
    short_hint="Current NOA Turnover minus prior comparable NOA Turnover.",
    semantic_key="profitability_change.noa_turnover_change",
    category="profitability_change",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("noa_turnover",),
    depends_on_previous=("noa_turnover",),
    hints=(
        "Change in NOA Turnover = Current Turnover - Prior Turnover.",
        "A lower turnover is mechanically consistent with greater NOA intensity when the reciprocal is defined, but the business cause requires separate analysis.",
    ),
)
```

```python
ComponentFamily(
    id="rnoa_change",
    order=52,
    title="Direct Change in RNOA",
    short_hint="Current direct RNOA minus prior comparable direct RNOA.",
    semantic_key="profitability_change.rnoa_change",
    category="profitability_change",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("rnoa",),
    depends_on_previous=("rnoa",),
    hints=(
        "Direct Change in RNOA = Current RNOA - Prior RNOA.",
    ),
)
```

```python
ComponentFamily(
    id="rnoa_margin_effect",
    order=53,
    title="Margin Effect on Change in RNOA",
    short_hint="Change in Margin multiplied by midpoint NOA Turnover.",
    semantic_key="profitability_change.rnoa_margin_effect",
    category="profitability_change",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("nopat_margin_change", "noa_turnover"),
    depends_on_previous=("noa_turnover",),
    hints=(
        "Margin Effect = Change in Margin × average of current and prior NOA Turnover.",
        "Midpoint weighting gives an exact order-neutral product-change attribution.",
    ),
)
```

```python
ComponentFamily(
    id="rnoa_turnover_effect",
    order=54,
    title="Turnover Effect on Change in RNOA",
    short_hint="Change in NOA Turnover multiplied by midpoint NOPAT Margin.",
    semantic_key="profitability_change.rnoa_turnover_effect",
    category="profitability_change",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("noa_turnover_change", "nopat_margin"),
    depends_on_previous=("nopat_margin",),
    hints=(
        "Turnover Effect = Change in NOA Turnover × average of current and prior NOPAT Margin.",
        "Do not reinterpret this aggregate effect as a specific asset-management cause without further evidence.",
    ),
)
```

```python
ComponentFamily(
    id="rnoa_change_from_drivers",
    order=55,
    title="Change in RNOA from Margin + Turnover Effects",
    short_hint="Margin Effect plus Turnover Effect.",
    semantic_key="profitability_change.rnoa_change_from_drivers",
    category="profitability_change",
    tab_template="ALT DuPont",
    period_scope="post_comparable",
    depends_on_current=("rnoa_margin_effect", "rnoa_turnover_effect"),
    hints=(
        "Driver Change in RNOA = Margin Effect + Turnover Effect.",
        "When both driver periods are defined, this must reconcile to Direct Change in RNOA.",
    ),
)
```

- [ ] **Step 2: Add a custom expander**

Create:

```python
def expand_profitability_change_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
```

Use the same duplicate-date and strict-chronology validation as existing expanders.

Every family uses:

```python
indices = range(2, len(periods))
```

because the attribution requires current and prior **comparable** RNOA periods.

When resolving `depends_on_previous`, use `periods[j - 1]`; current dependencies use `periods[j]`.

- [ ] **Step 3: Add expected-series mapping**

In `core/model/historical_expected.py` import:

```python
PROFITABILITY_CHANGE_COMPONENT_CATALOG
```

and:

```python
from .profitability_change import compute_profitability_change_series
```

Add:

```python
_PROFITABILITY_CHANGE_FAMILY_SERIES = (
    "nopat_margin_change",
    "noa_turnover_change",
    "rnoa_change",
    "rnoa_margin_effect",
    "rnoa_turnover_effect",
    "rnoa_change_from_drivers",
)
```

Create:

```python
def profitability_change_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    changes = compute_profitability_change_series(anchor)
    series = {
        "nopat_margin_change": changes.nopat_margin_change,
        "noa_turnover_change": changes.noa_turnover_change,
        "rnoa_change": changes.rnoa_change,
        "rnoa_margin_effect": changes.margin_effect_on_rnoa,
        "rnoa_turnover_effect": changes.turnover_effect_on_rnoa,
        "rnoa_change_from_drivers": changes.rnoa_change_from_drivers,
    }
    expected_ids = {
        family.id for family in PROFITABILITY_CHANGE_COMPONENT_CATALOG
    }
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "profitability_change_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _PROFITABILITY_CHANGE_FAMILY_SERIES
    }
```

Extend `expected_value_for_component()` with a profitability-change branch before the historical-core fallback.

- [ ] **Step 4: Add catalog/expansion tests**

Required assertions:

```text
catalog IDs unique                                     -> 6
family orders                                          -> 50..55
all period_scope values                                -> post_comparable
5 modeled fiscal periods                              -> 18 concrete specs
expected-series keys                                   -> exact catalog IDs
existing Step 9C.1 profitability-driver catalog        -> unchanged
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_profitability_change.py core/tests/test_reference_integrity.py -k "profitability_change or rnoa_change" -v
```

---

### Task 3: Wire Step 9C.2 into `ReferenceModelBuilder`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_profitability_change.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: Task 1 series + Task 2 specs.
- Produces: registered semantic practice components on `ALT DuPont`.

- [ ] **Step 1: Add imports and builder state**

Import:

```python
from ..model.profitability_change import compute_profitability_change_series
```

and:

```python
from .component_catalog import expand_profitability_change_specs
```

After Step 9C.1 profitability-driver setup, add:

```python
self.profitability_change_series = compute_profitability_change_series(self.anchor)
self.profitability_change_specs = expand_profitability_change_specs(
    self.periods,
    start_order=(
        len(self.historical_specs)
        + len(self.normalization_specs)
        + len(self.quality_specs)
        + len(self.working_capital_specs)
        + len(self.profitability_driver_specs)
        + 1
    ),
)
```

Append `self.profitability_change_specs` to `self.expected_specs`.

Create:

```python
self._profitability_change_spec_index = {
    (s.family_id, s.period_index): s
    for s in self.profitability_change_specs
}
```

- [ ] **Step 2: Add registration helper**

Create:

```python
def _register_profitability_change(
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
    spec = self._profitability_change_spec_index[(family_id, period_index)]
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

- [ ] **Step 3: Prove semantic-map completeness before rendering**

Add a test constructing `ReferenceModelBuilder` on the demo and assert:

```text
profitability_change_specs count = 18
expected_specs include all 6 new family IDs
no duplicate semantic IDs
```

Run the focused test and verify it fails before Task 4 renders/registers the sheet cells.

---

### Task 4: Add the RNOA change-attribution section to `ALT DuPont`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_profitability_change.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: existing `margin_row`, `rnoa_row`, Step 9C.1 `turnover_row`, and Task 3 registration helper.
- Produces: six practice rows + one generated trusted check row.

- [ ] **Step 1: Define the section immediately below Step 9C.1**

After `driver_check_row`, define:

```python
change_section_row = driver_check_row + 2
margin_change_row = change_section_row + 1
turnover_change_row = change_section_row + 2
direct_rnoa_change_row = change_section_row + 3
margin_effect_row = change_section_row + 4
turnover_effect_row = change_section_row + 5
driver_change_row = change_section_row + 6
change_check_row = change_section_row + 7
```

Labels:

```text
RNOA CHANGE ATTRIBUTION
Change in NOPAT Margin
Change in NOA Turnover
Direct Change in RNOA
Margin Effect on RNOA Change
Turnover Effect on RNOA Change
RNOA Change from Drivers
RNOA CHANGE DRIVER CHECK
```

Make the section heading and check-row label bold.

- [ ] **Step 2: Render non-applicable cells**

For fiscal-period indices `0` and `1`, write literal:

```text
N/A
```

into all six attribution rows and the generated check row.

Do not register semantic practice components for those periods.

- [ ] **Step 3: Render exact midpoint formulas for `j >= 2`**

Use same-sheet references to the existing rows:

```python
prev_col = self._col(2 + j - 1)
out_col = self._col(2 + j)

margin_change_f = (
    f"={out_col}{margin_row}-{prev_col}{margin_row}"
)
turnover_change_f = (
    f"={out_col}{turnover_row}-{prev_col}{turnover_row}"
)
direct_rnoa_change_f = (
    f"={out_col}{rnoa_row}-{prev_col}{rnoa_row}"
)
margin_effect_f = (
    f"={out_col}{margin_change_row}*"
    f"(({out_col}{turnover_row}+{prev_col}{turnover_row})/2)"
)
turnover_effect_f = (
    f"={out_col}{turnover_change_row}*"
    f"(({out_col}{margin_row}+{prev_col}{margin_row})/2)"
)
driver_change_f = (
    f"={out_col}{margin_effect_row}+{out_col}{turnover_effect_row}"
)
```

Let Excel naturally propagate `#N/A`; do not wrap practice formulas in `IFERROR(...,0)`.

Use `PCT_FMT` for Margin change, direct RNOA change, both effects, and driver RNOA change. Use `"0.00x"` for NOA Turnover change.

- [ ] **Step 4: Add a generated non-practice reconciliation formula**

Use:

```python
change_check_f = (
    f'=IF(OR(ISNA({out_col}{driver_change_row}),'
    f'ISNA({out_col}{direct_rnoa_change_row})),"N/A",'
    f'IF(ABS({out_col}{driver_change_row}-{out_col}{direct_rnoa_change_row})'
    f'<0.0000001,"OK","CHECK"))'
)
```

This cell is **not** a practice component. Existing trusted `ALT DuPont` validation must therefore protect it automatically.

Important semantic rule:

```text
driver #N/A + direct numeric -> check displays N/A, not CHECK
numeric driver + mismatched direct -> check displays CHECK
numeric driver + reconciled direct -> check displays OK
```

- [ ] **Step 5: Register six practice families**

For each `j >= 2`, register all six formulas against `self.profitability_change_series`.

Expected handling pattern:

```python
expected = changes.margin_effect_on_rnoa[j]
assert expected is not None
self._register_profitability_change(
    "rnoa_margin_effect",
    j,
    "ALT DuPont",
    margin_effect_row,
    out_col_idx,
    margin_effect_f,
    expected if isinstance(expected, str) else float(expected),
)
```

Use the analogous mapping for all six rows.

- [ ] **Step 6: Store rowmap entries**

Add:

```python
self.rowmap["dupont_margin_change_row"] = margin_change_row
self.rowmap["dupont_turnover_change_row"] = turnover_change_row
self.rowmap["dupont_direct_rnoa_change_row"] = direct_rnoa_change_row
self.rowmap["dupont_margin_effect_row"] = margin_effect_row
self.rowmap["dupont_turnover_effect_row"] = turnover_effect_row
self.rowmap["dupont_rnoa_change_from_drivers_row"] = driver_change_row
self.rowmap["dupont_rnoa_change_check_row"] = change_check_row
```

- [ ] **Step 7: Test formulas and first-period behavior**

Assert:

```text
indices 0 and 1 -> literal N/A in all new rows
indices 2..4 -> six formulas present
midpoint formulas contain no ABS and no IFERROR
RNOA CHANGE DRIVER CHECK is generated but not in SemanticMap
all 18 practice components are on ALT DuPont
```

---

### Task 5: Prove dynamic Check, undefined-state behavior, and trusted reconciliation

**Files:**
- Modify: `core/tests/test_profitability_change.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_normalization.py` only if reusing the existing cached-error injection helper is the established test pattern.

- [ ] **Step 1: Prove live classification conditioning**

Use an existing Accounting Judgment alternative that changes NOA across periods. Build a Trainer/Answer-Key pair, change only `Accounting Judgment!F`, and prove dynamic expected values for at least:

```text
noa_turnover_change
rnoa_turnover_effect
rnoa_change_from_drivers
```

change consistently with the new treatment.

Do not modify generated `ALT DuPont` source/model cells directly.

- [ ] **Step 2: Prove exact and equivalent numeric formulas pass**

For one ordinary numeric Step 9C.2 practice cell:

1. exact Answer-Key formula -> green;
2. structurally different formula with the correct cached numeric result -> green;
3. incorrect cached numeric result -> red.

- [ ] **Step 3: Prove `#N/A` behavior**

Construct a supported fixture where one required margin or turnover observation is undefined.

Require:

```text
relevant driver effect expected value -> #N/A
RNOA Change from Drivers              -> #N/A
RNOA CHANGE DRIVER CHECK              -> N/A
exact formula                          -> green
structurally different cached #N/A    -> green
fabricated cached 0.0                 -> red
```

- [ ] **Step 4: Prove generated-check tamper fails before recoloring**

1. Enter one otherwise correct learner formula into a Step 9C.2 practice cell.
2. Overwrite one `RNOA CHANGE DRIVER CHECK` formula in Trainer.
3. Run Check.
4. Require `ValueError` from trusted-sheet validation.
5. Reopen the Trainer and prove the practice cell retained its prior yellow fill.

- [ ] **Step 5: Run focused integration suites**

```bash
PYTHONPATH=. pytest \
  core/tests/test_profitability_change.py \
  core/tests/test_profitability_drivers.py \
  core/tests/test_reference_integrity.py \
  -v
```

Expected: green.

---

### Task 6: Integrate family metadata and preserve product UX

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Test: `core/tests/test_trainer.py`

- [ ] **Step 1: Add the new catalog to Trainer family metadata**

Import:

```python
PROFITABILITY_CHANGE_COMPONENT_CATALOG
```

and extend `group_components_by_family()`:

```python
family_meta.update(
    {f.id: f for f in PROFITABILITY_CHANGE_COMPONENT_CATALOG}
)
```

Do not change existing family titles, orders, or metadata.

- [ ] **Step 2: Update trainer instruction copy minimally**

If the Trainer index instruction currently refers generically to historical diagnostic schedules, no rewrite is required. Only change it if Step 9C.2 families would otherwise be inaccurately described.

- [ ] **Step 3: Update skill documentation**

Update `skills/bav-trainer/SKILL.md` to state that the historical diagnostic surface now includes exact RNOA change attribution between Margin and NOA Turnover. Do not claim company-specific causal diagnosis.

- [ ] **Step 4: Test list/index grouping**

Assert all six new families appear exactly once in family grouping and in order `50..55` after Step 9C.1 families.

---

### Task 7: Full regression and checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all verification passes
- Do not modify: `TARGET.md`

- [ ] **Step 1: Run focused suites**

```bash
PYTHONPATH=. pytest core/tests/test_profitability_change.py -v
PYTHONPATH=. pytest core/tests/test_profitability_drivers.py -v
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

- [ ] **Step 2: Run complete test suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual pass count. Do not invent an expected test count in advance.

- [ ] **Step 3: Verify base demo**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required five-year surface after Step 9C.2:

```text
50 formula families
220 practice cells
fresh Check: 0 correct / 0 incorrect / 220 blank
```

Derivation:

```text
Step 9C.1 base       45 families / 204 cells
Step 9C.2 addition    6 families /  18 cells
-------------------------------------------
New base              51? NO — verify family arithmetic carefully before finalizing.
```

**Important correction:** Step 9C.1 base has 45 families. Adding six families yields **51 families**, not 50. The required base surface is therefore:

```text
51 formula families
222 practice cells
fresh Check: 0 / 0 / 222 blank
```

Do not weaken tests to match any stale count elsewhere.

- [ ] **Step 4: Verify normalization demo**

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
55 formula families
242 practice cells
fresh Check: 0 / 0 / 242 blank
```

Derivation:

```text
Step 9C.1 normalization 49 families / 224 cells
Step 9C.2 addition       6 families /  18 cells
----------------------------------------------
New normalization       55 families / 242 cells
```

- [ ] **Step 5: Verify CLI remains unchanged**

```bash
PYTHONPATH=. python -m core --help
```

Public commands must remain exactly:

```text
ingest
build
check
list
```

- [ ] **Step 6: Update `RESULT.md` with evidence**

Record:

- actual full-suite pass count;
- base 51 / 222 surface;
- normalization 55 / 242 surface;
- six new RNOA-change families / 18 cells on five-year demo;
- midpoint Margin Effect + Turnover Effect reconciliation;
- undefined-driver propagation to `#N/A`;
- dynamic classification-conditioned attribution;
- exact/equivalent formula Check behavior;
- trusted `RNOA CHANGE DRIVER CHECK` tamper detection;
- Step 9C.1 level decomposition unchanged;
- Step 9B and Step 9A regression preservation;
- CLI unchanged;
- `TARGET.md` unchanged;
- forecasting / valuation not begun.

---

## Definition of Done

Step 9C.2 is complete only when all of the following are true:

1. RNOA changes are attributed with the exact symmetric midpoint identity.
2. Margin Effect + Turnover Effect reconciles to direct Change in RNOA whenever the level decomposition is defined.
3. The attribution starts only at the third modeled fiscal period in a normal five-year history.
4. Undefined Margin / Turnover inputs propagate to `#N/A`; no fabricated zero effects appear.
5. Zero driver change with valid inputs remains numeric zero.
6. Signs are preserved; no absolute-value normalization is introduced.
7. The workbook exposes six new practice families on `ALT DuPont` and one generated non-practice reconciliation row.
8. The generated `RNOA CHANGE DRIVER CHECK` is trusted and tamper-detected before any recoloring.
9. Dynamic Check recomputes Step 9C.2 expecteds under current live classification treatment.
10. Exact formulas and equivalent formulas with the same current-state result both pass.
11. Equivalent cached `#N/A` passes and fabricated `0.0` fails when the expected state is undefined.
12. All four Step 9C.1 families remain unchanged.
13. All 11 Step 9B working-capital families remain unchanged.
14. Base demo is 51 families / 222 practice cells.
15. Normalization demo is 55 families / 242 practice cells.
16. Full test suite passes.
17. CLI remains `{ingest, build, check, list}` only.
18. `TARGET.md` is unchanged.
19. No automatic causal interpretation, profitability-quality score, forecasting, or valuation has been introduced.

After completing Step 9C.2, stop and report changed files, exact test output, demo build/check/list output, midpoint-attribution reconciliation evidence, live-classification evidence, and any new active historical-model issue found during implementation. Do not proceed to ROE operating-versus-financing attribution, forecasting, or valuation, and do not commit or push.