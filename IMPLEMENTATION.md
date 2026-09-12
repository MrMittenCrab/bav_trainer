# Step 9F.2 — Historical Diluted EPS Earnings / Share-Count Attribution

> **Status:** COMPLETE — Step 9F.2 verified locally (259 passed). Ordinary demo unchanged at 62/259 and 66/279; share-enabled fixture 70/293 and 74/313. See `RESULT.md`. Do not commit/push from the agent.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `7e9afb1a37081e8340e5e94cc9db8976de6cfa65` (`Step 9F1`, Step 9F.1 complete). Implement only Step 9F.2 below using red/green TDD. Preserve Step 8 judgment behavior, the trusted-workbook boundary, all Step 9A source-completeness / tax / normalization / `#N/A` semantics, the full Step 9B working-capital surface, the full Step 9C profitability-driver/change surface, the full Step 9D ROE-attribution surface, the Step 9E cash-conversion trend surface, and the complete Step 9F.1 diluted per-share foundation. Do not add normalized EPS, basic-vs-diluted attribution, period-end share-count analysis, forecasting, valuation, segment analysis, ROU/deferred-tax alternatives, or company-specific investment conclusions. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Extend the Step 9F.1 per-share foundation into an exact historical attribution of period-to-period diluted EPS change between reported-earnings movement and the diluted weighted-average share-count denominator, so the learner can distinguish earnings-driven per-share change from share-count-driven per-share change without inventing causal explanations.

**Architecture:** Keep all Step 9F.1 formulas and the historical-share input contract unchanged. Add one focused `PerShareAttributionSeries` that consumes the already validated `PerShareSeries` plus treatment-conditioned reported Net Income from `AnchorMetrics`. Attribute `Change in Diluted EPS` exactly by treating EPS as `Net Income × (1 / Diluted Shares)` and applying the same symmetric midpoint product-change method already used in the RNOA and ROE attribution layers. Add four comparable-period semantic families to the existing `Per Share Analysis` worksheet plus one generated non-practice reconciliation row. Existing trusted-sheet validation should protect that generated row automatically.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `AnchorMetrics`, `PerShareSeries`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and existing trusted-sheet validation for `Per Share Analysis`.

**Spec:** `TARGET.md`, especially the requirements to explain whether earnings growth came from operating improvement, leverage, acquisitions, tax effects, or **dilution**; historical EPS/per-share analysis only when actual historical share-count data is supplied; structured diagnostics before free-form causal claims; and the rule that historical source facts such as share counts stay populated rather than becoming transcription exercises.

## Global Constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve Step 9F.1 `HistoricalShareData` and `StandardizedFinancials.historical_shares` exactly; no source-schema expansion in this checkpoint.
- Preserve the only supported share scale basis: `financial_statement_units`.
- Preserve the Step 9F.1 rule that diluted weighted-average shares must be explicitly supplied, complete for every modeled fiscal period, and strictly positive.
- Preserve Step 9F.1 gating: absent / empty historical shares omit `Per Share Analysis` and every per-share family.
- Preserve existing Step 9F.1 families and formulas unchanged:
  - `reported_diluted_eps`
  - `nopat_per_diluted_share`
  - `diluted_eps_change`
  - `diluted_share_count_change`
- This checkpoint attributes **reported diluted EPS**, not normalized EPS.
- Use reported Net Income from the treatment-conditioned `AnchorMetrics.historical.net_income` / existing `Per Share Analysis` Net Income row.
- Use diluted weighted-average shares from the trusted Step 9F.1 share row. Share-count levels remain populated, system-controlled inputs and never become practice cells.
- Define `EPS = Net Income × Inverse Diluted Shares`, where `Inverse Diluted Shares = 1 / Diluted Weighted-Average Shares`.
- Use an exact symmetric midpoint decomposition; do not assign the interaction term arbitrarily to earnings or share count.
- Preserve signs. Do not use `ABS()` in practice formulas.
- A larger diluted weighted-average share denominator is not automatically a negative business-quality conclusion. With positive earnings it mechanically pressures EPS; with losses the sign can reverse. Preserve the arithmetic rather than forcing an intuitive sign.
- Do not infer why share count changed (issuance, buybacks, options, SBC, convertibles, M&A consideration, etc.).
- Do not call the share-count effect “SBC dilution” or any other specific cause without supplied evidence.
- Do not add EPS growth-rate exercises in this checkpoint. Continue using absolute EPS change to avoid misleading percentage growth around zero / negative EPS.
- Do not add normalized EPS, basic shares, period-end shares, share-price data, valuation multiples, or market-cap calculations.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Review of commit `7e9afb1a`

Step 9F.1 is complete and establishes the required historical-share foundation:

- `HistoricalShareData` supplies diluted weighted-average share history with an explicit scale basis;
- standardized JSON round-trip and structured JSON/YAML ingestion preserve historical shares;
- multi-document merging handles historical-share restatements and rejects scale-basis conflicts;
- missing, incomplete, non-positive, or unsupported-scale share history fails closed;
- share counts are trusted populated inputs on `Per Share Analysis` rather than practice cells;
- `Reported Diluted EPS = Reported Net Income / Diluted WAS`;
- `NOPAT per Diluted Share = NOPAT / Diluted WAS`;
- absolute Change in Diluted EPS and Change in Diluted WAS are practice families;
- no-share demo builds remain unchanged at 62 families / 259 cells without normalization and 66 / 279 with normalization;
- share-enabled five-year builds contain 66 families / 277 cells without normalization and 70 / 297 with normalization;
- `RESULT.md` records 252 locally passing tests;
- GitHub has no attached CI status.

The remaining per-share interpretation gap is explicit in `TARGET.md`: when EPS changes, the learner should be able to distinguish movement in reported earnings from movement in the diluted-share denominator.

For each comparable period, let:

```text
N_t = Reported Net Income in current period
N_p = Reported Net Income in prior period
S_t = Current diluted weighted-average shares
S_p = Prior diluted weighted-average shares
q_t = 1 / S_t
q_p = 1 / S_p

EPS_t = N_t × q_t
EPS_p = N_p × q_p
```

Use the exact symmetric midpoint identity:

```text
Earnings Effect
= (N_t - N_p) × (q_t + q_p) / 2

Share-Count Effect
= (q_t - q_p) × (N_t + N_p) / 2

Change in EPS from Drivers
= Earnings Effect + Share-Count Effect
= EPS_t - EPS_p
```

This is exact and order-neutral. It is an arithmetic attribution, not a causal explanation of why earnings or share count changed.

---

### Task 1: Add authoritative diluted-EPS attribution series

**Files:**
- Create: `core/model/per_share_attribution.py`
- Create: `core/tests/test_per_share_attribution.py`

**Interfaces:**
- Consumes: `AnchorMetrics`, `PerShareSeries`.
- Produces: `PerShareAttributionSeries` and `compute_per_share_attribution_series(anchor, per_share)`.

- [ ] **Step 1: Write the failing data-model and ordinary-case test**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .per_share import PerShareSeries


@dataclass(frozen=True)
class PerShareAttributionSeries:
    reported_net_income_change: tuple[float | None, ...]
    earnings_effect_on_diluted_eps_change: tuple[float | None, ...]
    share_count_effect_on_diluted_eps_change: tuple[float | None, ...]
    diluted_eps_change_from_drivers: tuple[float | None, ...]
```

In `core/tests/test_per_share_attribution.py`, use either a focused synthetic `AnchorMetrics` fixture or the existing Step 9F.1 helpers from `core/tests/test_per_share.py`.

Test this simple arithmetic case:

```text
Prior Net Income = 100
Current Net Income = 120
Prior diluted WAS = 100
Current diluted WAS = 110

Prior EPS = 1.000000
Current EPS = 1.090909...
Direct Change in EPS = +0.090909...

Change in Net Income = +20
Earnings Effect = 20 × ((1/110 + 1/100) / 2)
                = +0.190909...
Share-Count Effect = (1/110 - 1/100) × ((120 + 100) / 2)
                   = -0.100000
Driver Change = +0.090909...
```

- [ ] **Step 2: Run the focused test and verify red state**

```bash
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
```

Expected: fail because `core.model.per_share_attribution` does not yet exist.

- [ ] **Step 3: Implement source-series validation**

Create:

```python
def compute_per_share_attribution_series(
    anchor: AnchorMetrics,
    per_share: PerShareSeries,
) -> PerShareAttributionSeries:
    net_income = tuple(float(v) for v in anchor.historical.net_income)
    shares = tuple(float(v) for v in per_share.diluted_weighted_average_shares)
    direct_eps = tuple(float(v) for v in per_share.reported_diluted_eps)
    direct_eps_change = tuple(per_share.diluted_eps_change)

    lengths = {
        "net_income": len(net_income),
        "diluted_weighted_average_shares": len(shares),
        "reported_diluted_eps": len(direct_eps),
        "diluted_eps_change": len(direct_eps_change),
    }
    if len(set(lengths.values())) != 1 or lengths["net_income"] == 0:
        raise ValueError(
            "per-share attribution series length mismatch: "
            + ", ".join(f"{name}={n}" for name, n in lengths.items())
        )

    for i, value in enumerate(shares):
        if value <= 0.0:
            raise ValueError(
                "per-share attribution requires positive diluted weighted-average "
                f"shares: period_index={i} shares={value}"
            )
```

This defensive positive-share check does not replace Step 9F.1 source validation; it protects the attribution function from malformed direct calls.

- [ ] **Step 4: Implement non-applicable first period and exact midpoint attribution**

Initialize:

```python
n = len(net_income)
net_income_change: list[float | None] = [None] * n
earnings_effect: list[float | None] = [None] * n
share_count_effect: list[float | None] = [None] * n
driver_change: list[float | None] = [None] * n
```

For every `i >= 1`:

```python
prior = i - 1
current_inverse_shares = 1.0 / shares[i]
prior_inverse_shares = 1.0 / shares[prior]

ni_delta = net_income[i] - net_income[prior]
earnings_value = (
    ni_delta
    * (current_inverse_shares + prior_inverse_shares)
    / 2.0
)
share_value = (
    (current_inverse_shares - prior_inverse_shares)
    * (net_income[i] + net_income[prior])
    / 2.0
)
driver_value = earnings_value + share_value

net_income_change[i] = ni_delta
earnings_effect[i] = earnings_value
share_count_effect[i] = share_value
driver_change[i] = driver_value
```

Do not take absolute values and do not force the share-count effect negative.

- [ ] **Step 5: Add independent reconciliation validation**

For every `i >= 1`:

```python
direct = direct_eps_change[i]
if direct is None:
    raise ValueError(
        "per-share attribution requires comparable diluted EPS change: "
        f"period_index={i}"
    )
if abs(driver_value - float(direct)) > 1e-9:
    raise ValueError(
        "diluted EPS earnings/share-count attribution does not reconcile: "
        f"period_index={i} direct={direct} driver={driver_value}"
    )
```

Also validate the supplied level series before the change attribution:

```python
for i in range(n):
    recomputed = net_income[i] / shares[i]
    if abs(recomputed - direct_eps[i]) > 1e-9:
        raise ValueError(
            "reported diluted EPS level does not reconcile before attribution: "
            f"period_index={i} direct={direct_eps[i]} recomputed={recomputed}"
        )
```

Return:

```python
return PerShareAttributionSeries(
    reported_net_income_change=tuple(net_income_change),
    earnings_effect_on_diluted_eps_change=tuple(earnings_effect),
    share_count_effect_on_diluted_eps_change=tuple(share_count_effect),
    diluted_eps_change_from_drivers=tuple(driver_change),
)
```

- [ ] **Step 6: Add edge-case tests**

Add tests proving:

```text
first period                                      -> all four attribution values None
unchanged Net Income                              -> Earnings Effect = 0.0
unchanged diluted shares                          -> Share-Count Effect = 0.0
positive earnings + rising shares                 -> Share-Count Effect negative
negative earnings + rising shares                 -> Share-Count Effect may be positive
falling shares                                    -> sign follows exact reciprocal arithmetic
negative Net Income change                        -> signed Earnings Effect retained
zero Net Income in either/both periods            -> numeric arithmetic, not #N/A
non-positive supplied share level                 -> ValueError
series-length mismatch                            -> clear ValueError
inconsistent reported EPS level                   -> ValueError
inconsistent direct EPS-change series             -> ValueError
```

For the two inconsistency tests, construct a `PerShareSeries` directly with one intentionally altered `reported_diluted_eps` or `diluted_eps_change` value. Do not weaken Step 9F.1 computation to make the inconsistency possible.

- [ ] **Step 7: Run focused tests to green**

```bash
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
```

Expected: all tests pass.

---

### Task 2: Add four semantic diluted-EPS attribution families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_per_share_attribution.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: `PerShareAttributionSeries` from Task 1 and existing Step 9F.1 per-share families.
- Produces: four comparable-period semantic families and dynamic expected-value routing.

- [ ] **Step 1: Add a separate attribution catalog**

Create:

```python
PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (...)
```

Keep `PER_SHARE_COMPONENT_CATALOG` unchanged. Use family orders `71` through `74`. All four new families use:

```text
tab: Per Share Analysis
category: per_share_attribution
period_scope: comparable
```

Define exactly:

#### Family 71 — `reported_net_income_change`

```python
ComponentFamily(
    id="reported_net_income_change",
    order=71,
    title="Change in Reported Net Income",
    short_hint="Current Reported Net Income minus prior Reported Net Income.",
    semantic_key="per_share_attribution.reported_net_income_change",
    category="per_share_attribution",
    tab_template="Per Share Analysis",
    period_scope="comparable",
    depends_on_current=("net_income_link",),
    depends_on_previous=("net_income_link",),
    hints=(
        "Change in Reported Net Income = Current Net Income - Prior Net Income.",
        "This is the earnings-numerator movement used in diluted-EPS attribution.",
    ),
)
```

#### Family 72 — `earnings_effect_on_diluted_eps_change`

```python
ComponentFamily(
    id="earnings_effect_on_diluted_eps_change",
    order=72,
    title="Earnings Effect on Change in Diluted EPS",
    short_hint="Change in Net Income multiplied by midpoint inverse diluted shares.",
    semantic_key="per_share_attribution.earnings_effect",
    category="per_share_attribution",
    tab_template="Per Share Analysis",
    period_scope="comparable",
    depends_on_current=("reported_net_income_change",),
    hints=(
        "Earnings Effect = Change in Net Income × average of current and prior inverse diluted shares.",
        "Inverse diluted shares means 1 / diluted weighted-average shares.",
        "This is an arithmetic numerator effect, not a causal explanation of why earnings changed.",
    ),
)
```

#### Family 73 — `share_count_effect_on_diluted_eps_change`

```python
ComponentFamily(
    id="share_count_effect_on_diluted_eps_change",
    order=73,
    title="Share-Count Effect on Change in Diluted EPS",
    short_hint="Change in inverse diluted shares multiplied by midpoint Reported Net Income.",
    semantic_key="per_share_attribution.share_count_effect",
    category="per_share_attribution",
    tab_template="Per Share Analysis",
    period_scope="comparable",
    depends_on_current=("diluted_share_count_change", "net_income_link"),
    depends_on_previous=("net_income_link",),
    hints=(
        "Share-Count Effect = Change in (1 / diluted shares) × average current/prior Net Income.",
        "Rising share count is not forced to a negative effect; losses can reverse the sign mechanically.",
        "Do not infer whether the share-count movement came from issuance, SBC, options, M&A, or buybacks without separate evidence.",
    ),
)
```

#### Family 74 — `diluted_eps_change_from_drivers`

```python
ComponentFamily(
    id="diluted_eps_change_from_drivers",
    order=74,
    title="Change in Diluted EPS from Earnings + Share-Count Effects",
    short_hint="Earnings Effect plus Share-Count Effect.",
    semantic_key="per_share_attribution.diluted_eps_change_from_drivers",
    category="per_share_attribution",
    tab_template="Per Share Analysis",
    period_scope="comparable",
    depends_on_current=(
        "earnings_effect_on_diluted_eps_change",
        "share_count_effect_on_diluted_eps_change",
    ),
    hints=(
        "Change in Diluted EPS from Drivers = Earnings Effect + Share-Count Effect.",
        "The driver total must reconcile exactly to the direct Change in Diluted EPS.",
    ),
)
```

- [ ] **Step 2: Add the expander**

Create:

```python
def expand_per_share_attribution_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
```

Use the same duplicate and strictly chronological period validation as `expand_per_share_specs()`.

All four families use:

```python
indices = range(1, len(periods))
```

Resolve current / previous practice-family dependencies with `concrete_component_id()` exactly like the existing expanders.

For five modeled periods:

```text
4 families × 4 comparable periods = 16 new practice cells
```

- [ ] **Step 3: Add expected-value routing without a second per-share recomputation path**

In `core/model/historical_expected.py`, import:

```python
PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG
PerShareAttributionSeries
compute_per_share_attribution_series
```

Add:

```python
_PER_SHARE_ATTRIBUTION_FAMILY_SERIES = (
    "reported_net_income_change",
    "earnings_effect_on_diluted_eps_change",
    "share_count_effect_on_diluted_eps_change",
    "diluted_eps_change_from_drivers",
)
```

Create:

```python
def per_share_attribution_expected_series(
    anchor: AnchorMetrics,
    per_share: PerShareSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    attribution = compute_per_share_attribution_series(anchor, per_share)
    series = {
        "reported_net_income_change": attribution.reported_net_income_change,
        "earnings_effect_on_diluted_eps_change": (
            attribution.earnings_effect_on_diluted_eps_change
        ),
        "share_count_effect_on_diluted_eps_change": (
            attribution.share_count_effect_on_diluted_eps_change
        ),
        "diluted_eps_change_from_drivers": (
            attribution.diluted_eps_change_from_drivers
        ),
    }
    expected_ids = {
        family.id for family in PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG
    }
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            "per_share_attribution_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {
        family_id: series[family_id]
        for family_id in _PER_SHARE_ATTRIBUTION_FAMILY_SERIES
    }
```

Extend `expected_value_for_component()` before the Step 9F.1 per-share branch:

```python
if family_id in _PER_SHARE_ATTRIBUTION_FAMILY_SERIES:
    if per_share is None:
        raise ValueError(
            f"Per-share-attribution family {family_id!r} requires a PerShareSeries"
        )
    series = per_share_attribution_expected_series(anchor, per_share)
elif family_id in _PER_SHARE_FAMILY_SERIES:
    ...
```

Do not add another source-data or share-series argument to `expected_value_for_component()`.

- [ ] **Step 4: Add catalog/expected tests**

Prove:

```text
PER_SHARE_COMPONENT_CATALOG remains exactly the Step 9F.1 four families
PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG contains exactly four unique IDs
orders are exactly 71, 72, 73, 74
all four attribution families are comparable-period
five periods expand to exactly 16 attribution specs
expected-series keys exactly equal attribution-catalog IDs
driver EPS change equals Step 9F.1 direct diluted_eps_change for every comparable period
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "per_share or attribution" -v
```

---

### Task 3: Wire attribution into `ReferenceModelBuilder`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_per_share_attribution.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Consumes: `self.per_share_series` from Step 9F.1.
- Produces: `self.per_share_attribution_series`, attribution specs, semantic registrations, and the visible worksheet attribution section.

- [ ] **Step 1: Compute attribution only when Step 9F.1 is applicable**

Import:

```python
from ..model.per_share_attribution import compute_per_share_attribution_series
from .component_catalog import expand_per_share_attribution_specs
```

Immediately after the existing Step 9F.1 `per_share_series / per_share_specs` gating:

```python
if self.per_share_series is not None:
    self.per_share_attribution_series = compute_per_share_attribution_series(
        self.anchor,
        self.per_share_series,
    )
    self.per_share_attribution_specs = expand_per_share_attribution_specs(
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
            + 1
        ),
    )
else:
    self.per_share_attribution_series = None
    self.per_share_attribution_specs = ()
```

Append the new specs after `self.per_share_specs` in `self.expected_specs`.

Create:

```python
self._per_share_attribution_spec_index = {
    (s.family_id, s.period_index): s
    for s in self.per_share_attribution_specs
}
```

- [ ] **Step 2: Add the registration helper**

Create next to `_register_per_share()`:

```python
def _register_per_share_attribution(
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
    spec = self._per_share_attribution_spec_index[(family_id, period_index)]
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

- [ ] **Step 3: Extend the existing `Per Share Analysis` sheet**

Do not create another worksheet. Extend `_build_per_share_analysis()` below the Step 9F.1 rows.

Preserve all existing Step 9F.1 coordinates:

```text
row 5  Reported Net Income
row 6  NOPAT
row 7  Diluted Weighted-Average Shares
row 9  Reported Diluted EPS
row 10 NOPAT per Diluted Share
row 12 Change in Diluted EPS
row 13 Change in Diluted Weighted-Average Shares
```

Add:

```text
A15  DILUTED EPS CHANGE ATTRIBUTION
A16  Change in Reported Net Income
A17  Earnings Effect on Change in Diluted EPS
A18  Share-Count Effect on Change in Diluted EPS
A19  Diluted EPS Change from Drivers
A20  DILUTED EPS CHANGE ATTRIBUTION CHECK
```

Make rows 15 and 20 bold.

Use existing `per_share_fmt` for rows 17–19 and `NUM_FMT` for row 16.

- [ ] **Step 4: Write first-period non-applicable cells**

For period index `0`, write literal:

```text
N/A
```

into rows 16–20. Do not register first-period attribution components.

- [ ] **Step 5: Write the exact comparable-period workbook formulas**

For each `j > 0`:

```python
prev_col = self._col(2 + j - 1)

net_income_change_f = f"={col}{ni_row}-{prev_col}{ni_row}"

earnings_effect_f = (
    f"={col}{net_income_change_row}*"
    f"((1/{col}{shares_row}+1/{prev_col}{shares_row})/2)"
)

share_count_effect_f = (
    f"=((1/{col}{shares_row})-(1/{prev_col}{shares_row}))*"
    f"(({col}{ni_row}+{prev_col}{ni_row})/2)"
)

driver_eps_change_f = (
    f"={col}{earnings_effect_row}+{col}{share_count_effect_row}"
)

attribution_check_f = (
    f'=IF(ABS({col}{driver_eps_change_row}-{col}{eps_chg_row})'
    f'<0.0000001,"OK","CHECK")'
)
```

Do not use `ABS()` in any practice formula. `ABS()` is allowed only in the generated non-practice reconciliation check.

Do not reference normalized earnings. Use the existing Reported Net Income row.

- [ ] **Step 6: Register all four comparable families**

For each `j > 0`, register the formulas against:

```python
attribution = self.per_share_attribution_series
assert attribution is not None

attribution.reported_net_income_change[j]
attribution.earnings_effect_on_diluted_eps_change[j]
attribution.share_count_effect_on_diluted_eps_change[j]
attribution.diluted_eps_change_from_drivers[j]
```

Each value must be non-`None` for comparable periods.

- [ ] **Step 7: Store rowmap entries**

Add:

```python
self.rowmap["per_share_attribution_net_income_change_row"] = net_income_change_row
self.rowmap["per_share_attribution_earnings_effect_row"] = earnings_effect_row
self.rowmap["per_share_attribution_share_count_effect_row"] = share_count_effect_row
self.rowmap["per_share_attribution_driver_eps_change_row"] = driver_eps_change_row
self.rowmap["per_share_attribution_check_row"] = attribution_check_row
```

- [ ] **Step 8: Add workbook-layout and formula tests**

For a five-period share-enabled fixture, prove:

```text
Per Share Analysis still uses Step 9F.1 rows 5/6/7/9/10/12/13 unchanged
attribution heading is row 15
four practice rows are 16–19
check row is 20 and is not a semantic practice cell
first-period rows 16–20 contain literal N/A
all four attribution families have four comparable cells
practice formulas contain no ABS()
share-count-effect formula uses current/prior inverse share levels, not simple raw share-count change multiplication
answer-key driver change reconciles to direct diluted_eps_change expected value
Trainer attribution practice cells are blank yellow
share-count level row remains populated and trusted
```

---

### Task 4: Extend dynamic Check and Trainer family metadata

**Files:**
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/workbook.py`
- Do **not** modify `core/trainer/check_context.py` unless a failing test proves a real generic trusted-sheet defect.
- Test: `core/tests/test_per_share_attribution.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Consumes: existing Step 9F.1 `compute_per_share_series()` dynamic Check path.
- Produces: attribution families visible to `list` / Trainer index and dynamically checked from current live workbook state.

- [ ] **Step 1: Make dynamic Check recognize both per-share catalogs**

In `core/trainer/checker.py`, import `PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG` and change the family-ID set to:

```python
per_share_family_ids = {
    family.id
    for family in (
        *PER_SHARE_COMPONENT_CATALOG,
        *PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
    )
}
```

Continue computing exactly one `PerShareSeries`:

```python
per_share = compute_per_share_series(
    financials,
    list(modeled_periods),
    anchor,
)
```

Do not create a second source reconstruction path for attribution. `expected_value_for_component()` will derive the attribution series from this same `per_share` object plus the live treatment-conditioned `anchor`.

- [ ] **Step 2: Add attribution family metadata to Trainer/list grouping**

In `core/trainer/workbook.py`, import `PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG` and add:

```python
family_meta.update(
    {f.id: f for f in PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG}
)
```

Do not change grouping semantics for other families.

- [ ] **Step 3: Rely on existing Per Share trusted-sheet validation**

The current trusted-sheet rule already validates every non-practice cell on `Per Share Analysis` whenever that sheet has practice cells. Because row 20 is not a practice component, the new reconciliation check should automatically be trusted.

Add a regression proving:

1. build a share-enabled Trainer/Answer Key pair;
2. enter an exact correct attribution practice formula;
3. tamper the generated `DILUTED EPS CHANGE ATTRIBUTION CHECK` formula;
4. run Check;
5. Check raises `ValueError` matching `Trusted workbook cell was modified: Per Share Analysis`;
6. the learner formula remains yellow because structural failure occurs before recolor.

Do not add a one-off check-row validator if the generic trusted-sheet rule already passes this test.

- [ ] **Step 4: Add live-state Check regressions**

Prove:

```text
exact attribution formula -> green
equivalent formula with matching cached value -> green
wrong formula/cached value -> red
share-count row tamper -> ValueError before recolor
no-share workbook -> attribution families absent and no Per Share Analysis sheet
```

Also prove the attribution responds to current source state reconstructed by Check. Because Step 9F.2 uses reported Net Income and supplied historical shares, no new Accounting Judgment treatment should change Reported Net Income itself; the existing live-classification exercises must still compose and Check successfully alongside the new attribution cells.

Do not invent a treatment dependency that does not economically exist.

---

### Task 5: Preserve gating, counts, and all prior curriculum surfaces

**Files:**
- Modify tests only as needed for new expected counts on **share-enabled** fixtures.
- Preserve ordinary no-share demo assertions.

- [ ] **Step 1: Preserve no-share builds exactly**

For the current five-year `DEMO_HK_Standardized.json`, which intentionally contains no historical share data:

```text
without normalization:
62 families / 259 practice cells
Per Share Analysis absent

with normalization:
66 families / 279 practice cells
Per Share Analysis absent
```

These counts must not change in Step 9F.2.

- [ ] **Step 2: Update share-enabled expected surfaces**

Step 9F.1 share-enabled surface:

```text
without normalization: 66 families / 277 cells
with normalization:    70 families / 297 cells
```

Step 9F.2 adds:

```text
4 families × 4 comparable periods = 16 practice cells
```

Therefore the expected five-year share-enabled surfaces become:

```text
without normalization: 70 families / 293 cells
with normalization:    74 families / 313 cells
```

The combined per-share module becomes:

```text
8 per-share/per-share-attribution families
34 practice cells
```

Do not change the demo JSON merely to make these families appear in the default demo.

- [ ] **Step 3: Preserve all earlier module definitions**

Regression tests must confirm no unintended family-definition changes to:

```text
25 historical core families
4 normalization families
5 quality-level families
4 quality-change families
11 working-capital families
4 RNOA-level driver families
6 RNOA-change families
7 ROE-attribution families
4 Step 9F.1 per-share families
```

---

### Task 6: Verification

Run focused tests first:

```bash
PYTHONPATH=. pytest core/tests/test_per_share.py -v
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "per_share or attribution" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Then run the entire suite:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Do not prestate the final test count. Record the actual result in `RESULT.md`.

### Ordinary no-share demo

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
259 practice cells
62 families
fresh Check 0 / 0 / 259
Per Share Analysis absent
```

### Ordinary no-share normalization demo

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
279 practice cells
66 families
fresh Check 0 / 0 / 279
Per Share Analysis absent
```

### Share-enabled five-year fixture

Use the existing `_share_enabled_demo()` helper or an equivalent temporary standardized payload that adds:

```python
HistoricalShareData(
    scale_basis="financial_statement_units",
    diluted_weighted_average={
        FY2021: 1000.0,
        FY2022: 1025.0,
        FY2023: 1050.0,
        FY2024: 1075.0,
        FY2025: 1100.0,
    },
)
```

Required surfaces:

```text
without normalization: 293 practice cells / 70 families
with normalization:    313 practice cells / 74 families
fresh Check: all blank, zero correct, zero incorrect
```

Verify the share-enabled Answer Key shows exact reconciliation for every comparable period:

```text
Earnings Effect + Share-Count Effect
= Diluted EPS Change from Drivers
= direct Change in Diluted EPS
```

Verify CLI remains:

```bash
PYTHONPATH=. python -m core --help
```

with only the existing public commands:

```text
ingest
build
check
list
```

---

### Task 7: Documentation and checkpoint report

**Files:**
- Modify: `RESULT.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `IMPLEMENTATION.md` status only after verification
- Do not modify: `TARGET.md`

- [ ] **Step 1: Update `RESULT.md` with actual evidence**

Record:

- actual full-suite pytest count;
- ordinary no-share base and normalization counts unchanged;
- share-enabled base / normalization counts;
- exact midpoint earnings/share-count attribution identity;
- positive-earnings + rising-shares sign test;
- negative-earnings sign-reversal test;
- generated reconciliation-row tamper detection;
- share-level tamper failure before recolor;
- exact/equivalent/wrong Check behavior;
- no-share gating;
- confirmation that normalized EPS, basic-vs-diluted analysis, forecasting, and valuation remain deferred.

Do not write `Unresolved: none` unless every required verification actually passes.

- [ ] **Step 2: Update the trainer skill documentation**

Add Step 9F.2 to `skills/bav-trainer/SKILL.md`:

```text
Historical diluted-EPS attribution (when share history is supplied):
- direct absolute EPS change remains the reference result
- reported-earnings effect uses midpoint inverse shares
- share-count effect uses midpoint reported Net Income
- the two effects reconcile exactly to direct diluted-EPS change
- attribution is mechanical, not a causal explanation of issuance/SBC/buybacks
```

Update share-enabled surface counts only. Preserve no-share demo counts.

- [ ] **Step 3: Mark this plan complete only after verification**

Add a concise completion status at the top of `IMPLEMENTATION.md` only after all required tests and build/check/list verification pass.

Do not commit or push. Stop and report changed files, exact test output, share-enabled/no-share surface counts, reconciliation evidence, trusted-sheet tamper evidence, and any new active historical-model issue discovered.

---

## Definition of Done

Step 9F.2 is complete only when all of the following are true:

1. Step 9F.1 source schema and per-share formulas remain unchanged.
2. No share history still means no `Per Share Analysis` sheet or per-share families.
3. Share-enabled history adds exactly four attribution families / 16 comparable practice cells for five periods.
4. Change in Reported Net Income is explicit and auditable.
5. Earnings Effect uses `ΔNet Income × midpoint inverse shares`.
6. Share-Count Effect uses `Δinverse shares × midpoint Net Income`.
7. Earnings Effect + Share-Count Effect reconciles to direct Change in Diluted EPS for every comparable period.
8. Signs are preserved; rising shares are not hard-coded as a negative effect.
9. Negative-earnings sign reversal is tested and accepted as valid arithmetic.
10. Share-count levels remain populated trusted source inputs and never become practice cells.
11. Generated attribution-check formulas are trusted and tamper-detected before recolor.
12. Exact and equivalent learner formulas pass; wrong formulas fail.
13. Ordinary no-share surfaces remain 62/259 and 66/279.
14. Share-enabled five-year surfaces become 70/293 and 74/313.
15. The full test suite passes.
16. `TARGET.md` is unchanged.
17. Normalized EPS, basic-vs-diluted attribution, period-end shares, forecasting, and valuation have not been introduced.

After completing Step 9F.2, stop and report. Do not begin normalized per-share analysis, forecasting, or valuation, and do not commit or push.