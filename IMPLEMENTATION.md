# Step 9F.1 — Historical Diluted Per-Share Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `8959cad3166067f2281b52479ba7a84b3cb6e63a` (`Step 9E1`, Step 9E.1 complete). Implement only Step 9F.1 below using red/green TDD. Preserve Step 8 judgment behavior, the trusted-workbook boundary, all Step 9A source-completeness / tax / normalization / `#N/A` semantics, the full Step 9B working-capital surface, the full Step 9C profitability-driver/change surface, the full Step 9D ROE-attribution surface, and the Step 9E cash-conversion trend surface. Do not add forecasting, valuation, normalized EPS, basic-vs-diluted dilution attribution, period-end share-count analysis, segment analysis, ROU/deferred-tax alternatives, or company-specific investment conclusions. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Add historical diluted per-share analysis only when actual diluted weighted-average share counts are supplied through the standardized historical input path, so the learner can calculate reported diluted EPS, NOPAT per diluted share, and their basic period-to-period per-share/dilution movements without invented share assumptions.

**Architecture:** Extend `StandardizedFinancials` with one optional explicit historical-share contract rather than hiding share counts in generic metadata or forecast assumptions. Add one focused `PerShareSeries` driven by treatment-conditioned historical Net Income / NOPAT plus supplied diluted weighted-average shares. Add four semantic practice families on a gated `Per Share Analysis` sheet. Check must reconstruct the same share history from `_CheckContext`, dynamically recompute NOPAT-per-share under the current Accounting Judgment treatment, and treat supplied share-count cells as trusted system inputs.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `StandardizedFinancials`, `standardized_to_payload` / `standardized_from_payload`, `HKManualDocumentAdapter`, `AnchorMetrics`, `UNDEFINED_RATIO`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `expected_value_for_component`, `check_workbook`, and trusted-sheet validation.

**Spec:** `TARGET.md`, especially the v1 boundary requiring “historical EPS / per-share metrics when required historical share-count data is supplied”, the rule that historical share counts remain populated source facts rather than transcription practice, the “No invented historical inputs” requirement, and the historical practice-surface expansion strategy’s per-share step.

## Global Constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all existing historical and diagnostic formula families unchanged.
- Preserve current demo behavior when no historical share data is supplied.
- The existing demo JSON must remain share-data-free in this checkpoint; do not change its current 62-family / 259-cell base surface or 66-family / 279-cell normalization surface.
- Historical share counts are supplied facts, not learner practice cells.
- Do not use `assumptions["marketData"]["dilutedShares"]`, dormant forecast defaults, current market-data shares, or any synthetic/fallback share count for historical per-share calculations.
- Do not infer share counts from EPS, equity, market capitalization, stock price, or labels.
- The Step 9F.1 module is applicable only when diluted weighted-average share history is explicitly supplied.
- A completely absent diluted-share history omits the module without error.
- A present-but-incomplete diluted-share history fails closed; do not omit missing years or fabricate zero.
- Diluted weighted-average share counts must be strictly positive in every modeled fiscal period. Zero or negative shares are invalid source data, not `#N/A` denominators.
- Share-count values use `scale_basis="financial_statement_units"`: if financial statements are in millions, share counts are supplied in millions of shares; if statements are in thousands, shares are supplied in thousands of shares. This makes currency-unit / scaled-share division produce currency per share directly without hidden conversion assumptions.
- Any other share scale basis is unsupported in this checkpoint and must fail clearly.
- Preserve signs in Net Income, NOPAT, EPS, and period changes. Do not take absolute values.
- If NOPAT is `#N/A`, NOPAT per diluted share is `#N/A`; do not convert it to zero.
- `Reported Diluted EPS` in this checkpoint means model-calculated historical Net Income divided by supplied diluted weighted-average shares. Do not claim it is an independent reconciliation to a company-reported EPS line unless such a source line is added in a later checkpoint.
- Do not add normalized EPS yet; Step 8B2 normalization remains unchanged.
- Do not add basic-share or basic-vs-diluted dilution analysis yet.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Review of commit `8959cad3`

Step 9E.1 is complete and coherent:

- Earnings Quality now includes period-to-period CFO, cash-conversion, accrual, and accrual-ratio trends;
- undefined ratio inputs propagate to `#N/A` rather than fabricated zeros;
- asset-scaled change diagnostics retain their applicability gate;
- trusted-sheet validation protects generated trend-check cells;
- the base demo is 62 families / 259 cells;
- the normalization demo is 66 families / 279 cells;
- `RESULT.md` records 240 locally passing tests;
- no forecasting or valuation has begun.

The next explicit historical-v1 dependency in `TARGET.md` is per-share analysis when actual historical share-count data is supplied. The current standardized contract has no dedicated historical-share field, and `standardized_to_payload()` currently drops generic metadata from Check reconstruction, so a trustworthy per-share module requires an explicit source contract before any EPS formula is added.

Step 9F.1 establishes that contract and a minimal diluted per-share schedule only.

---

### Task 1: Add an explicit historical diluted-share data contract

**Files:**
- Modify: `core/data/interface.py`
- Modify: `core/data/standardized_io.py`
- Modify: `core/ingestion/manual_hk.py`
- Modify: `core/ingestion/reconciler.py`
- Create: `core/tests/test_per_share.py`

**Interfaces:**
- Produces: `HistoricalShareData` and `StandardizedFinancials.historical_shares`.
- JSON key: `historical_shares`.
- This task must preserve all current inputs that omit the new field.

- [ ] **Step 1: Add the optional data model and failing round-trip tests**

In `core/data/interface.py`, add immediately before `StandardizedFinancials`:

```python
@dataclass
class HistoricalShareData:
    """Explicit historical share-count inputs used by per-share schedules."""

    scale_basis: str = ""
    diluted_weighted_average: dict[date, float | None] = field(default_factory=dict)
```

Then add to `StandardizedFinancials`:

```python
historical_shares: HistoricalShareData | None = None
```

Create `core/tests/test_per_share.py` with a fixture proving an object containing:

```python
HistoricalShareData(
    scale_basis="financial_statement_units",
    diluted_weighted_average={
        date(2024, 12, 31): 1000.0,
        date(2025, 12, 31): 1025.0,
    },
)
```

survives `standardized_to_payload()` -> `standardized_from_payload()` with dates and numeric values unchanged.

Also prove `historical_shares is None` remains valid for legacy payloads.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_per_share.py -k "round_trip or legacy" -v
```

Expected initial state: red because the interface field / serializer does not exist.

- [ ] **Step 2: Serialize and deserialize the new field explicitly**

In `core/data/standardized_io.py`, import `HistoricalShareData` and add focused helpers:

```python
def _serialize_historical_shares(
    shares: HistoricalShareData | None,
) -> dict[str, Any] | None:
    if shares is None:
        return None
    return {
        "scale_basis": shares.scale_basis,
        "diluted_weighted_average": {
            _date_key(period): (None if value is None else float(value))
            for period, value in shares.diluted_weighted_average.items()
        },
    }


def _deserialize_historical_shares(
    payload: object,
) -> HistoricalShareData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_shares must be an object or null")
    return HistoricalShareData(
        scale_basis=str(payload.get("scale_basis") or ""),
        diluted_weighted_average={
            _parse_date(period): (None if value is None else float(value))
            for period, value in (
                payload.get("diluted_weighted_average") or {}
            ).items()
        },
    )
```

Add the field to `standardized_to_payload()` and `standardized_from_payload()`.

For backwards compatibility, emitting `"historical_shares": None` is acceptable, but do not serialize unrelated `metadata` as a substitute.

- [ ] **Step 3: Parse structured JSON/YAML share history**

In `core/ingestion/manual_hk.py`, import `HistoricalShareData` and add:

```python
def _load_historical_shares(payload: dict) -> HistoricalShareData | None:
    raw = payload.get("historical_shares")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("historical_shares must be an object")
    values = raw.get("diluted_weighted_average") or {}
    if not isinstance(values, dict):
        raise ValueError(
            "historical_shares.diluted_weighted_average must be an object"
        )
    return HistoricalShareData(
        scale_basis=str(raw.get("scale_basis") or ""),
        diluted_weighted_average={
            _parse_date(str(period)): (
                None if value is None else float(value)
            )
            for period, value in values.items()
        },
    )
```

Pass `historical_shares=_load_historical_shares(payload)` into `StandardizedFinancials(...)`.

Use this exact structured-input shape in tests:

```json
"historical_shares": {
  "scale_basis": "financial_statement_units",
  "diluted_weighted_average": {
    "2024-12-31": 1000.0,
    "2025-12-31": 1025.0
  }
}
```

Do not add Excel-import share parsing in this checkpoint.

- [ ] **Step 4: Preserve share history through multi-document merge**

In `core/ingestion/reconciler.py`, import `HistoricalShareData` and add a private helper with newest-document period values winning:

```python
def _merge_historical_shares(
    base: StandardizedFinancials,
    supplement: StandardizedFinancials,
) -> None:
    incoming = supplement.historical_shares
    if incoming is None:
        return
    if base.historical_shares is None:
        base.historical_shares = HistoricalShareData(
            scale_basis=incoming.scale_basis,
            diluted_weighted_average=dict(incoming.diluted_weighted_average),
        )
        return
    existing = base.historical_shares
    if existing.scale_basis != incoming.scale_basis:
        raise ValueError(
            "historical share scale_basis mismatch across merged documents: "
            f"{existing.scale_basis!r} != {incoming.scale_basis!r}"
        )
    existing.diluted_weighted_average.update(
        incoming.diluted_weighted_average
    )
```

Call it from `merge_documents()` before reconciliation returns.

Tests must prove:

```text
base no shares + supplement shares -> shares retained
both with same basis -> supplement period values win
basis mismatch -> ValueError
```

- [ ] **Step 5: Run Task 1 tests to green**

```bash
PYTHONPATH=. pytest core/tests/test_per_share.py -k "round_trip or ingest or merge or legacy" -v
```

---

### Task 2: Build one authoritative diluted per-share series

**Files:**
- Create: `core/model/per_share.py`
- Modify: `core/tests/test_per_share.py`

**Interfaces:**
- Consumes: `StandardizedFinancials`, modeled fiscal periods, `AnchorMetrics`.
- Produces: `PerShareSeries`, `per_share_available()`, `compute_per_share_series()`.

- [ ] **Step 1: Write failing model tests**

Create:

```python
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from ..data.interface import StandardizedFinancials
from .financial_math import AnchorMetrics
from .ratio_values import UNDEFINED_RATIO, ratio_or_na


SUPPORTED_SHARE_SCALE_BASIS = "financial_statement_units"


@dataclass(frozen=True)
class PerShareSeries:
    diluted_weighted_average_shares: tuple[float, ...]
    reported_diluted_eps: tuple[float, ...]
    nopat_per_diluted_share: tuple[float | str, ...]
    diluted_eps_change: tuple[float | None, ...]
    diluted_share_count_change: tuple[float | None, ...]
```

Test an ordinary three-period case where Net Income, NOPAT, and diluted shares produce exact expected EPS/per-share values and signed changes.

- [ ] **Step 2: Implement applicability separately from completeness**

Create:

```python
def per_share_available(financials: StandardizedFinancials) -> bool:
    shares = financials.historical_shares
    return bool(
        shares is not None
        and shares.diluted_weighted_average
    )
```

A company with no share object, or an empty diluted-share mapping, is simply not applicable in Step 9F.1.

Do not call completeness validation from `per_share_available()`.

- [ ] **Step 3: Add strict source validation**

Create:

```python
def _required_diluted_share_series(
    financials: StandardizedFinancials,
    periods: list[date],
) -> tuple[float, ...]:
    shares = financials.historical_shares
    if shares is None or not shares.diluted_weighted_average:
        raise ValueError("diluted weighted-average share history is not supplied")
    if shares.scale_basis != SUPPORTED_SHARE_SCALE_BASIS:
        raise ValueError(
            "unsupported historical share scale_basis "
            f"{shares.scale_basis!r}; expected "
            f"{SUPPORTED_SHARE_SCALE_BASIS!r}"
        )

    values: list[float] = []
    for period in periods:
        if period not in shares.diluted_weighted_average:
            raise ValueError(
                "missing diluted weighted-average shares for modeled period "
                f"{period.isoformat()}"
            )
        raw = shares.diluted_weighted_average[period]
        if raw is None:
            raise ValueError(
                "missing diluted weighted-average shares for modeled period "
                f"{period.isoformat()}"
            )
        value = float(raw)
        if value <= 0.0:
            raise ValueError(
                "diluted weighted-average shares must be > 0 for modeled period "
                f"{period.isoformat()}, got {value}"
            )
        values.append(value)
    return tuple(values)
```

Extra historical-share dates outside the modeled axis may remain present and are ignored.

Tests must prove omitted, `None`, zero, negative, and unsupported-scale values fail closed with the affected date / basis visible in the message.

- [ ] **Step 4: Compute the per-share series**

Create:

```python
def compute_per_share_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> PerShareSeries:
    shares = _required_diluted_share_series(financials, periods)
    net_income = tuple(float(v) for v in anchor.historical.net_income)
    nopat = tuple(anchor.historical.nopat)

    if len(net_income) != len(periods) or len(nopat) != len(periods):
        raise ValueError(
            "per-share period axis must match AnchorMetrics historical series length"
        )

    eps = tuple(
        net_income[i] / shares[i]
        for i in range(len(periods))
    )
    nopat_per_share = tuple(
        ratio_or_na(nopat[i], shares[i])
        for i in range(len(periods))
    )

    eps_change: list[float | None] = [None]
    share_change: list[float | None] = [None]
    for i in range(1, len(periods)):
        eps_change.append(eps[i] - eps[i - 1])
        share_change.append(shares[i] - shares[i - 1])

    return PerShareSeries(
        diluted_weighted_average_shares=shares,
        reported_diluted_eps=eps,
        nopat_per_diluted_share=nopat_per_share,
        diluted_eps_change=tuple(eps_change),
        diluted_share_count_change=tuple(share_change),
    )
```

Required semantics:

```text
negative Net Income -> negative EPS retained
negative NOPAT -> negative NOPAT/share retained
NOPAT #N/A -> NOPAT/share #N/A
unchanged shares -> Change in shares = 0.0
falling shares -> negative Change in shares retained
EPS change may be positive or negative; no automatic quality label
```

- [ ] **Step 5: Run model tests to green**

```bash
PYTHONPATH=. pytest core/tests/test_per_share.py -k "series or available or missing or scale or positive" -v
```

---

### Task 3: Add four gated semantic per-share formula families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Modify: `core/tests/test_per_share.py`

**Interfaces:**
- Consumes: `PerShareSeries` from Task 2.
- Produces: `PER_SHARE_COMPONENT_CATALOG`, `expand_per_share_specs()`, and per-share expected-value routing.

- [ ] **Step 1: Add the per-share catalog with orders 67–70**

Add exactly:

```python
PER_SHARE_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ComponentFamily(
        id="reported_diluted_eps",
        order=67,
        title="Reported Diluted EPS",
        short_hint="Reported Net Income divided by diluted weighted-average shares.",
        semantic_key="per_share.reported_diluted_eps",
        category="per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("net_income_link",),
        hints=(
            "Diluted EPS = Reported Net Income / Diluted Weighted-Average Shares.",
            "Share count is a supplied historical input and remains populated.",
        ),
    ),
    ComponentFamily(
        id="nopat_per_diluted_share",
        order=68,
        title="NOPAT per Diluted Share",
        short_hint="Historical NOPAT divided by diluted weighted-average shares.",
        semantic_key="per_share.nopat_per_diluted_share",
        category="per_share",
        tab_template="Per Share Analysis",
        depends_on_current=("nopat_fy",),
        hints=(
            "NOPAT per Diluted Share = NOPAT / Diluted Weighted-Average Shares.",
            "If NOPAT is undefined, the per-share amount is also undefined (#N/A).",
        ),
    ),
    ComponentFamily(
        id="diluted_eps_change",
        order=69,
        title="Change in Diluted EPS",
        short_hint="Current Reported Diluted EPS minus prior EPS.",
        semantic_key="per_share.diluted_eps_change",
        category="per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        depends_on_current=("reported_diluted_eps",),
        depends_on_previous=("reported_diluted_eps",),
        hints=(
            "Change in Diluted EPS = Current EPS - Prior EPS.",
            "Use an absolute per-share change here rather than a growth rate that can become misleading around zero or negative EPS.",
        ),
    ),
    ComponentFamily(
        id="diluted_share_count_change",
        order=70,
        title="Change in Diluted Weighted-Average Shares",
        short_hint="Current diluted weighted-average shares minus prior shares.",
        semantic_key="per_share.diluted_share_count_change",
        category="per_share",
        tab_template="Per Share Analysis",
        period_scope="comparable",
        hints=(
            "Change in Diluted Weighted-Average Shares = Current Shares - Prior Shares.",
            "A positive change is mechanical evidence of a larger diluted share denominator; do not infer the cause automatically.",
        ),
    ),
)
```

- [ ] **Step 2: Add `expand_per_share_specs()`**

Use the same chronological / duplicate-period validation as existing expanders.

```python
def expand_per_share_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
```

For `period_scope == "all"`, use all periods. For `"comparable"`, use indices `1..n-1`. Reject any other scope.

For five periods this must create:

```text
Reported Diluted EPS                 5
NOPAT per Diluted Share              5
Change in Diluted EPS                4
Change in Diluted Weighted-Average Shares 4
Total                               18
```

- [ ] **Step 3: Add expected-value routing**

In `core/model/historical_expected.py`, import `PER_SHARE_COMPONENT_CATALOG` and `PerShareSeries`.

Add:

```python
_PER_SHARE_FAMILY_SERIES = (
    "reported_diluted_eps",
    "nopat_per_diluted_share",
    "diluted_eps_change",
    "diluted_share_count_change",
)
```

Create:

```python
def per_share_expected_series(
    per_share: PerShareSeries,
) -> dict[str, tuple[float | str | None, ...]]:
    series = {
        "reported_diluted_eps": per_share.reported_diluted_eps,
        "nopat_per_diluted_share": per_share.nopat_per_diluted_share,
        "diluted_eps_change": per_share.diluted_eps_change,
        "diluted_share_count_change": per_share.diluted_share_count_change,
    }
    expected_ids = {family.id for family in PER_SHARE_COMPONENT_CATALOG}
    if set(series) != expected_ids:
        missing = sorted(expected_ids - set(series))
        extra = sorted(set(series) - expected_ids)
        raise ValueError(
            f"per_share_expected_series family mismatch; "
            f"missing={missing} extra={extra}"
        )
    return {family_id: series[family_id] for family_id in _PER_SHARE_FAMILY_SERIES}
```

Extend `expected_value_for_component()` with:

```python
per_share: PerShareSeries | None = None,
```

and route `_PER_SHARE_FAMILY_SERIES` before the historical fallback. If a per-share family is requested while `per_share is None`, raise a clear `ValueError`.

- [ ] **Step 4: Test exact catalog shape**

Tests must prove:

```text
catalog IDs exactly the four above
orders exactly [67, 68, 69, 70]
5 periods -> 18 specs
first two families -> all periods
last two -> comparable periods only
expected-series keys exactly equal catalog IDs
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_per_share.py -k "catalog or expand or expected" -v
```

---

### Task 4: Wire the gated per-share module into build and Check

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/check_context.py`
- Modify: `core/trainer/workbook.py`
- Modify: `core/tests/test_per_share.py`

**Interfaces:**
- Consumes: Task 2 `per_share_available()` / `compute_per_share_series()` and Task 3 catalog/specs.
- Produces: gated semantic surface, dynamic treatment-conditioned Check, trusted worksheet boundary.

- [ ] **Step 1: Add builder gating after the Step 9E specs**

Import:

```python
from ..model.per_share import compute_per_share_series, per_share_available
from .component_catalog import expand_per_share_specs
```

After `quality_change_specs` are established:

```python
if per_share_available(self.fin):
    self.per_share_series = compute_per_share_series(
        self.fin,
        self.periods,
        self.anchor,
    )
    self.per_share_specs = expand_per_share_specs(
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
            + 1
        ),
    )
else:
    self.per_share_series = None
    self.per_share_specs = ()
```

Append `self.per_share_specs` to `self.expected_specs` and create `_per_share_spec_index`.

Add `_register_per_share()` following the existing focused registration helpers.

- [ ] **Step 2: Add `Per Share Analysis` only when applicable**

Define:

```python
PER_SHARE_SHEET = "Per Share Analysis"
```

Build it after `Working Capital Analysis` in the normal historical build path when `self.per_share_series is not None`.

Use this layout:

```text
A1  <Company> — Per Share Analysis
A2  Historical per-share diagnostics using supplied diluted weighted-average shares. Share counts are source inputs, not practice cells.
A4  Metric
A5  Reported Net Income
A6  NOPAT
A7  Diluted Weighted-Average Shares
A9  Reported Diluted EPS
A10 NOPAT per Diluted Share
A12 Change in Diluted EPS
A13 Change in Diluted Weighted-Average Shares
```

Rows 5 and 6 are trusted formulas linking to existing `Condensed Financials` rows. Row 7 contains the supplied numeric share-count facts directly from `self.per_share_series.diluted_weighted_average_shares` and is never registered as practice.

For every period `j`:

```python
reported_eps = f"=IF({col}{shares_row}<=0,NA(),{col}{ni_row}/{col}{shares_row})"
nopat_per_share = f"=IF({col}{shares_row}<=0,NA(),{col}{nopat_row}/{col}{shares_row})"
```

Register both practice families.

For `j == 0`, rows 12–13 must contain literal `"N/A"` and must not be registered.

For `j > 0`:

```python
eps_change = f"={col}{eps_row}-{prev_col}{eps_row}"
shares_change = f"={col}{shares_row}-{prev_col}{shares_row}"
```

Register both comparable families.

Use a per-share number format such as:

```text
0.000
```

for EPS / NOPAT-per-share / EPS change, and `#,##0.0;(#,##0.0)` for share counts and share-count changes.

Do not add a generated check row merely to increase surface area; the source counts are already trusted and every four semantic formulas are Check-managed.

- [ ] **Step 3: Extend trusted-sheet validation**

In `core/trainer/check_context.py`, add:

```python
PER_SHARE_SHEET = "Per Share Analysis"
```

During full trusted validation:

```python
per_share_practice = {
    cell for tab, cell in practice_cells if tab == PER_SHARE_SHEET
}
if per_share_practice:
    for wb, label in ((trainer_wb, "Trainer"), (answer_key_wb, "Answer Key")):
        if PER_SHARE_SHEET not in wb.sheetnames:
            raise ValueError(f"{label} is missing Per Share Analysis sheet")
    _validate_trusted_sheet_cells(
        trainer_wb[PER_SHARE_SHEET],
        answer_key_wb[PER_SHARE_SHEET],
        sheet_name=PER_SHARE_SHEET,
        editable_cells=per_share_practice,
    )
```

This must protect the supplied share-count row and source-link rows before any practice-cell recoloring.

- [ ] **Step 4: Extend dynamic Check**

In `core/trainer/checker.py`, import `PER_SHARE_COMPONENT_CATALOG` and `compute_per_share_series`.

Detect whether any per-share family exists in the semantic map. When it does:

```python
per_share = compute_per_share_series(
    financials,
    list(modeled_periods),
    anchor,
)
```

Pass:

```python
per_share=per_share,
```

into `expected_value_for_component()`.

This recomputation must use the current treatment-conditioned `anchor`, so changing a live classification that changes NOPAT must also change `nopat_per_diluted_share` expected values while leaving Reported Diluted EPS and the supplied share-count row unchanged.

- [ ] **Step 5: Add Trainer-index family metadata**

In `core/trainer/workbook.py`, import `PER_SHARE_COMPONENT_CATALOG` and add it to `family_meta` in `group_components_by_family()`.

Do not alter the semantic ordering of existing families.

- [ ] **Step 6: Test gating, trust, dynamic Check, and `#N/A`**

Add regressions proving:

```text
no historical shares -> no Per Share Analysis sheet / no per_share components
shares present but incomplete -> build fails before workbook output
unsupported scale basis -> build fails clearly
share count <= 0 -> build fails clearly
share-enabled five-year demo -> 4 per-share families / 18 new practice cells
first-period change rows -> literal N/A and not practice
Trainer supplied share row -> populated identically to Answer Key
Trainer practice cells -> blank yellow
exact formulas -> green
cached equivalent formulas -> green
incorrect cached values -> red
share-row tamper -> trusted-sheet ValueError before recolor
live classification treatment changing NOPAT -> NOPAT/share dynamic expected changes
NOPAT #N/A -> NOPAT/share expected #N/A; exact/NA equivalent passes, fabricated 0.0 fails
```

For the share-enabled test fixture, copy/ingest the existing demo in memory and assign:

```python
HistoricalShareData(
    scale_basis="financial_statement_units",
    diluted_weighted_average={
        period: 1000.0 + 25.0 * i
        for i, period in enumerate(canonical_fiscal_periods(data))
    },
)
```

Do not edit `example/DEMO_HK_Standardized.json`.

Expected five-year share-enabled surfaces:

```text
without normalization: existing 62/259 + 4 families/18 cells = 66 families / 277 cells
with normalization:    existing 66/279 + 4 families/18 cells = 70 families / 297 cells
```

The ordinary demo without share history must remain exactly:

```text
base: 62 families / 259 cells
normalization: 66 families / 279 cells
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_per_share.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

---

### Task 5: Verify full historical behavior and update docs

**Files:**
- Modify: `RESULT.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `IMPLEMENTATION.md` status only after verification
- Read-only: `TARGET.md`

- [ ] **Step 1: Run the full suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing test count. Do not prestate a new total before the suite runs.

- [ ] **Step 2: Verify unchanged ordinary demo surfaces**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx
PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required ordinary-demo result:

```text
62 families
259 practice cells
fresh Check 0 correct / 0 incorrect / 259 blank
no Per Share Analysis sheet
```

Then:

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

Required ordinary-demo normalization result:

```text
66 families
279 practice cells
fresh Check 0 / 0 / 279 blank
no Per Share Analysis sheet
```

- [ ] **Step 3: Verify a share-enabled build**

Use a short Python test/helper or the test fixture to build the demo with five complete diluted weighted-average share values. Record:

```text
Per Share Analysis present
4 per-share families
18 per-share practice cells
share-enabled base total: 66 families / 277 cells
share-enabled normalization total: 70 families / 297 cells
fresh Check all blank
```

- [ ] **Step 4: Verify CLI remains historical-only**

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

No share-specific CLI is added.

- [ ] **Step 5: Update `RESULT.md` with evidence**

Record:

- actual full-suite count;
- ordinary demo unchanged at 62/259 and 66/279;
- share-enabled demo/fixture at 66/277 and 70/297;
- explicit standardized historical-share round-trip;
- structured JSON ingestion;
- multi-document merge behavior;
- missing / `None` / zero / negative / unsupported-scale fail-closed behavior;
- no-share applicability omission;
- 4 per-share families / 18 five-year cells;
- live classification-conditioned NOPAT/share Check;
- trusted share-row tamper rejection;
- `#N/A` NOPAT/share behavior;
- no normalized EPS, basic/diluted attribution, forecasting, or valuation;
- `TARGET.md` unchanged.

Do not write `Unresolved: none` unless every required regression and verification passes.

- [ ] **Step 6: Update `skills/bav-trainer/SKILL.md`**

Add a concise Step 9F note:

```text
Step 9F.1 — historical diluted per-share foundation
- gated on explicitly supplied diluted weighted-average share history
- share counts remain populated trusted inputs
- Reported Diluted EPS and NOPAT per Diluted Share
- absolute changes in EPS and diluted weighted-average shares
- ordinary demo remains unchanged because it supplies no share history
```

Keep forecasting / valuation deferred.

- [ ] **Step 7: Mark `IMPLEMENTATION.md` complete only after all evidence exists**

Add the final status line only after focused tests, full suite, ordinary demo, share-enabled fixture, trusted-tamper regression, and CLI verification all pass.

---

## Definition of done

Step 9F.1 is complete only when all are true:

1. `StandardizedFinancials` has an explicit optional `HistoricalShareData` field.
2. Structured JSON/YAML input can supply diluted weighted-average share history.
3. Standardized payload round-trip preserves the share history, so `_CheckContext` can reconstruct it.
4. Cross-document merge preserves/merges share history and rejects scale-basis mismatches.
5. No-share companies retain the exact prior workbook surface.
6. Present-but-incomplete share history fails closed.
7. Zero or negative diluted shares fail closed.
8. Unsupported share scale basis fails closed.
9. Share counts remain populated trusted cells, never practice cells.
10. `Per Share Analysis` appears only when valid diluted-share history is supplied.
11. Four per-share formula families exist: Reported Diluted EPS, NOPAT per Diluted Share, Change in Diluted EPS, Change in Diluted Weighted-Average Shares.
12. Five periods create exactly 18 per-share practice cells.
13. `#N/A` NOPAT propagates to NOPAT/share.
14. Dynamic Check recomputes NOPAT/share under the learner’s current classification treatment.
15. Tampering supplied share counts fails before any fill updates.
16. Ordinary demo remains 62/259 base and 66/279 normalization.
17. A five-year share-enabled fixture is 66/277 base and 70/297 normalization.
18. Full tests pass.
19. CLI remains `{ingest, build, check, list}`.
20. `TARGET.md` is unchanged.
21. Normalized EPS, basic-vs-diluted attribution, forecasting, valuation, and investment conclusions have not begun.

After completing Step 9F.1, stop and report changed files, exact test output, ordinary-demo outputs, share-enabled fixture outputs, source-contract/round-trip evidence, dynamic-Check evidence, and any new active historical-model issue found during implementation. Do not proceed to basic-vs-diluted attribution, normalized EPS, forecasting, or valuation, and do not commit or push.