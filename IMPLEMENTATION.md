# Step 9A — Historical Earnings Quality: Cash Conversion and Accruals

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `5254d6277e71b36af1a0b2dbb5ed07597b88b8ce` (`Step 8.3`). Implement only Step 9A below using red/green TDD. Preserve the trusted-workbook boundary, Step 8A/8B1 classification workflow, Step 8B2 normalization workflow, and workbook-wide non-disclosing Check. Do not begin working-capital interpretation, research-writing evaluation, forecasting, valuation, ROU/deferred-tax alternative modeling, or any later Step 9/10 work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Add the first earnings-quality diagnostic layer: a transparent historical schedule that teaches operating cash-flow conversion, total accruals, and an asset-scaled accrual ratio using only supplied historical facts.

**Architecture:** Keep this checkpoint mechanical and auditable. Add a canonical operating-cash-flow resolver, compute one authoritative Python-side `EarningsQualitySeries`, and render a visible `Earnings Quality` schedule from that series. The schedule is conditional on a resolvable operating-cash-flow line; the asset-scaled extension is conditional on resolvable total assets. Do not infer missing cash-flow facts, invent thresholds, or label a company as having “good” or “bad” earnings quality.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `StandardizedFinancials`, `AnchorMetrics`, `SemanticMap`, `ReferenceModelBuilder`, `CheckContext`, `TrainingWorkbookGenerator`, and workbook-wide Check.

**Spec:** `TARGET.md`, especially the requirements for accruals, cash conversion, quality of earnings, material/applicable-topic gating, historical model auditability, economic interpretation as a later layer, and the prohibition on invented historical inputs.

---

## Review of commit `5254d627`

Step 8B2.2 is implemented coherently:

- nonblank treatment strings must now exactly match the workbook treatment text;
- historical source statements are trusted inputs;
- fixed supplied classifications are trusted inputs;
- non-practice cells on `Condensed Financials`, `ALT DuPont`, and `Earnings Normalization` are protected;
- judgment F:G:H remain learner-controlled on bound case rows;
- trusted-state failure occurs before formula recoloring;
- the base and normalization surfaces remain 25 / 118 and 29 / 138 respectively;
- `RESULT.md` records 170 locally passing tests.

GitHub has no attached CI status for this commit, so the recorded test count is local verification rather than independent CI evidence.

No blocking Step 8B2.2 defect remains from this review. One small pre-existing resolver defect should be fixed while introducing the new cash-flow concept: `core/model/line_resolver.py::_norm_text()` still has duplicated straight-apostrophe entries instead of normalizing curly apostrophes. Step 9A includes that correction with regression coverage.

The next dependency in `TARGET.md` is earnings-quality / accrual-cash-conversion analysis. This checkpoint adds only the mechanical historical calculations. Interpretation of *why* cash conversion changed remains deferred to a later diagnostic step.

---

## Global constraints

- `TARGET.md` is read-only.
- Initial scope remains non-financial operating companies.
- Use only supplied historical facts; do not invent CFO, total assets, normalized cash flow, capex, or other inputs.
- Do not use `Net cash used in investing activities` as a capex proxy.
- Do not treat cash conversion or accrual ratios as automatic “quality scores.”
- Do not add arbitrary good/bad thresholds, traffic lights, or investment conclusions.
- Operating-cash-flow availability controls whether the `Earnings Quality` module exists.
- Total-assets availability controls only the asset-scaled accrual extension; cash-conversion diagnostics must still work without total assets.
- Existing Step 8A/8B1/8B2 judgment mechanics remain unchanged.
- Existing normalization choices must not rewrite reported Net Income, CFO, or historical source statements.
- Existing trusted-state validation remains fail-closed before grading.
- Formula Check remains one workbook-wide action and remains non-disclosing.
- Trainer practice cells remain blank bright yellow with no answer/hint.
- Answer Key practice cells retain working formulas and one legacy Note.
- No new public CLI command.
- No forecasting, valuation, scenario engine, Hint/Reveal, VBA, or free-form grading.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Add canonical operating-cash-flow resolution and fix Unicode apostrophes

**Files:**
- Modify: `core/model/line_resolver.py`
- Modify: `core/tests/test_line_resolver.py`

### 1A. Fix `_norm_text()` apostrophe normalization

Replace the duplicated apostrophe tuple with deliberate typographic normalization:

```python
for ch in ("\u2018", "\u2019", "`", "´"):
    s = s.replace(ch, "'")
```

Preserve all other normalization behavior.

Add a regression proving a label containing a curly apostrophe resolves through an alias containing a straight apostrophe where applicable, e.g. `Shareholders’ equity` -> `total_equity`.

### 1B. Add canonical concept `operating_cash_flow`

Extend `_EXACT_ALIASES` with a narrow final-operating-cash-flow concept:

```python
"operating_cash_flow": frozenset(
    {
        "net cash from operating activities",
        "net cash generated from operating activities",
        "net cash provided by operating activities",
        "net cash flow from operating activities",
        "net cash flows from operating activities",
    }
),
```

Do **not** alias generic `cash generated from operations`; under IFRS that line can be an intermediate subtotal before tax/interest cash flows.

The normal `resolve_line()` priority remains:

```text
1. exact LineItem.concept
2. exact canonical aliases
3. narrow safe patterns
```

No broad substring matching is required for `operating_cash_flow` in this checkpoint.

### TDD

- [ ] Explicit `concept="operating_cash_flow"` resolves even with an unfamiliar display label.
- [ ] Each supported alias resolves.
- [ ] Generic `Cash generated from operations` does not silently resolve.
- [ ] Two equal-priority CFO aliases raise `AmbiguousLineError`.
- [ ] Curly-apostrophe equity regression passes.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

---

## Task 2 — Create authoritative earnings-quality calculations

**Files:**
- Create: `core/model/earnings_quality.py`
- Create: `core/tests/test_earnings_quality.py`

Create:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class EarningsQualityAvailability:
    operating_cash_flow: bool
    total_assets: bool

@dataclass(frozen=True)
class EarningsQualitySeries:
    operating_cash_flow: tuple[float, ...]
    cash_conversion_ratio: tuple[float, ...]
    total_accruals: tuple[float, ...]
    average_total_assets: tuple[float | None, ...]
    accrual_ratio: tuple[float | None, ...]
```

Create:

```python
def earnings_quality_availability(
    financials: StandardizedFinancials,
) -> EarningsQualityAvailability:
    ...
```

Required semantics:

```python
cfo = resolve_line(
    financials.cash_flow,
    "operating_cash_flow",
    required=False,
).item

total_assets = resolve_line(
    financials.balance_sheet,
    "total_assets",
    required=False,
).item
```

Absence returns `False`. Ambiguity must propagate as `AmbiguousLineError`; do not silently disable the module when the source itself is ambiguous.

Create:

```python
def compute_earnings_quality_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> EarningsQualitySeries:
    ...
```

`compute_earnings_quality_series()` requires operating cash flow. If it is unavailable, raise a clear `MissingLineError` rather than fabricating a value.

Use reported Net Income from:

```python
anchor.historical.net_income
```

For period `j`:

```python
cfo[j] = supplied operating cash flow

cash_conversion_ratio[j] = (
    cfo[j] / net_income[j]
    if net_income[j] != 0
    else 0.0
)

total_accruals[j] = net_income[j] - cfo[j]
```

When total assets are available:

```python
average_total_assets[0] = None
accrual_ratio[0] = None

average_total_assets[j] = (
    total_assets[j - 1] + total_assets[j]
) / 2

accrual_ratio[j] = (
    total_accruals[j] / average_total_assets[j]
    if average_total_assets[j] != 0
    else 0.0
)
```

When total assets are unavailable:

```python
average_total_assets = (None, ...)  # one per modeled period
accrual_ratio = (None, ...)
```

### Accounting meaning

Document the definitions precisely:

```text
Cash conversion ratio = CFO / Reported Net Income
Total accruals         = Reported Net Income - CFO
Accrual ratio          = Total accruals / Average Total Assets
```

These are historical diagnostics, not automatic judgments about quality.

### TDD

- [ ] Positive earnings / positive CFO case.
- [ ] CFO greater than Net Income -> negative total accruals.
- [ ] CFO below Net Income -> positive total accruals.
- [ ] Zero Net Income -> cash-conversion ratio exactly `0.0` under this model convention.
- [ ] Total-assets extension uses beginning/ending average and starts only in period 2.
- [ ] Zero average assets -> accrual ratio `0.0`.
- [ ] Missing total assets retains CFO/conversion/accruals but returns `None` for asset-scaled series.
- [ ] Missing CFO raises.
- [ ] Ambiguous CFO raises rather than disabling the module.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
```

---

## Task 3 — Add conditional earnings-quality component families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Test: `core/tests/test_earnings_quality.py`

Add:

```python
QUALITY_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (
    ...
)
```

Use fixed family orders **30–34** so the existing normalization families remain 26–29.

Required families:

```text
30 operating_cash_flow_link
31 cash_conversion_ratio
32 total_accruals
33 average_total_assets
34 accrual_ratio
```

Suggested metadata:

```python
ComponentFamily(
    id="operating_cash_flow_link",
    order=30,
    title="Operating cash flow historical source link",
    short_hint="Link net cash from operating activities for the same fiscal period.",
    semantic_key="quality.operating_cash_flow",
    category="earnings_quality",
    tab_template="Earnings Quality",
)

ComponentFamily(
    id="cash_conversion_ratio",
    order=31,
    title="Cash conversion ratio",
    short_hint="Compare operating cash flow with reported Net Income.",
    semantic_key="quality.cash_conversion_ratio",
    category="earnings_quality",
    tab_template="Earnings Quality",
    depends_on_current=("operating_cash_flow_link", "net_income_link"),
)

ComponentFamily(
    id="total_accruals",
    order=32,
    title="Total accruals",
    short_hint="Reported Net Income minus operating cash flow.",
    semantic_key="quality.total_accruals",
    category="earnings_quality",
    tab_template="Earnings Quality",
    depends_on_current=("operating_cash_flow_link", "net_income_link"),
)

ComponentFamily(
    id="average_total_assets",
    order=33,
    title="Average total assets",
    short_hint="Average beginning and ending reported total assets.",
    semantic_key="quality.average_total_assets",
    category="earnings_quality",
    tab_template="Earnings Quality",
    period_scope="comparable",
)

ComponentFamily(
    id="accrual_ratio",
    order=34,
    title="Accrual ratio",
    short_hint="Scale total accruals by average total assets.",
    semantic_key="quality.accrual_ratio",
    category="earnings_quality",
    tab_template="Earnings Quality",
    period_scope="comparable",
    depends_on_current=("total_accruals", "average_total_assets"),
)
```

Create:

```python
def expand_quality_specs(
    periods: list[date],
    *,
    start_order: int,
    include_asset_scaled: bool,
) -> tuple[ComponentSpec, ...]:
    ...
```

Rules:

- CFO unavailable -> caller does not invoke expansion / uses `()`.
- `operating_cash_flow_link`, `cash_conversion_ratio`, `total_accruals` always expand across all periods when CFO is available.
- `average_total_assets` and `accrual_ratio` expand only when `include_asset_scaled=True`.
- comparable families begin with the second fiscal period.
- concrete `order` remains continuous from `start_order`.
- `family_order` remains the fixed conceptual order 30–34.
- reject duplicate/non-increasing period axes exactly as the existing expansion helpers do.

For the five-year demo with CFO + total assets:

```text
CFO link:              5 cells
Cash conversion:       5 cells
Total accruals:         5 cells
Average total assets:   4 cells
Accrual ratio:          4 cells
Total:                  23 cells
```

---

## Task 4 — Render the `Earnings Quality` schedule

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_earnings_quality.py`

Add constant:

```python
EARNINGS_QUALITY_SHEET = "Earnings Quality"
```

### Builder gating

In `ReferenceModelBuilder.__init__`:

1. compute `self.quality_availability`;
2. if CFO is available, compute `self.quality_series`;
3. if CFO is unavailable, set `self.quality_series = None` and `self.quality_specs = ()`;
4. when CFO is available, expand the core quality specs;
5. add asset-scaled specs only when total assets are available;
6. append quality specs after historical and normalization specs when constructing `expected_specs`.

Concrete component order should begin after the previously active concrete specs:

```python
start_order = len(self.historical_specs) + len(self.normalization_specs) + 1
```

Do not renumber the existing historical or normalization families.

### Workbook layout

Create the visible sheet only when CFO is available.

Use a compact auditable layout:

```text
A1  <Company> — Earnings Quality
A2  Historical cash-conversion and accrual diagnostics. These are mechanical diagnostics, not an automatic quality score.

row 4:
Metric | FY1 | FY2 | ...

row 5  Operating Cash Flow
row 6  Reported Net Income
row 7  Cash Conversion Ratio
row 8  Total Accruals (Net Income - CFO)
```

When total assets are available, add:

```text
row 10 Total Assets
row 11 Average Total Assets
row 12 Accrual Ratio
```

Rows 6 and 10 are trusted populated links, not new practice families.

### Formula rules

For each fiscal period:

**Operating Cash Flow — practice**

```excel
='Cash Flow Statement'!<same-period CFO source cell>
```

**Reported Net Income — populated trusted link**

```excel
='Condensed Financials'!<same-period Net Income cell>
```

**Cash Conversion Ratio — practice**

```excel
=IF(<Reported NI cell>=0,0,<CFO cell>/<Reported NI cell>)
```

**Total Accruals — practice**

```excel
=<Reported NI cell>-<CFO cell>
```

When total assets are available:

**Total Assets — populated trusted link**

```excel
='Balance Sheet'!<same-period Total Assets source cell>
```

**Average Total Assets — practice from FY2 onward**

```excel
=(<prior Total Assets>+<current Total Assets>)/2
```

**Accrual Ratio — practice from FY2 onward**

```excel
=IF(<Average Total Assets>=0,0,<Total Accruals>/<Average Total Assets>)
```

Use the existing number-format conventions:

- CFO, Net Income, Total Accruals, Total Assets, Average Total Assets -> `NUM_FMT`;
- Cash Conversion Ratio -> `0.00x`;
- Accrual Ratio -> `PCT_FMT`.

Register only the five semantic quality families above. Do not make the populated Net Income / Total Assets rows practice cells.

### Answer-Key hints

Hints should teach the mechanics without interpreting the company:

```text
CFO link: pull final net cash from operating activities for the same period.
Cash conversion: CFO / Reported Net Income.
Total accruals: Reported Net Income - CFO.
Average assets: average beginning and ending reported Total Assets.
Accrual ratio: Total Accruals / Average Total Assets.
```

Do not add “healthy”, “poor”, “high quality”, or threshold-based hints.

---

## Task 5 — Extend dynamic expected values and Check

**Files:**
- Modify: `core/model/historical_expected.py`
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/check_context.py`
- Test: `core/tests/test_earnings_quality.py`

### 5A. Expected-value dispatch

Extend:

```python
def expected_value_for_component(
    anchor: AnchorMetrics,
    component: ResolvedComponent,
    *,
    normalization: NormalizationSeries | None = None,
    earnings_quality: EarningsQualitySeries | None = None,
) -> float | str | None:
    ...
```

Add one mapping for the five quality family IDs.

For quality families, require `earnings_quality` rather than silently falling back to stale Answer-Key expected values.

The first-period `None` values for average assets / accrual ratio have no components because those families are `comparable`.

### 5B. Check recomputation

In `check_workbook()` detect whether the loaded semantic map contains any quality family:

```python
quality_family_ids = {family.id for family in QUALITY_COMPONENT_CATALOG}
needs_quality = any(comp.family_id in quality_family_ids for comp in comps)
```

When needed:

```python
earnings_quality = compute_earnings_quality_series(
    financials,
    list(modeled_periods),
    anchor,
)
```

Pass it to `expected_value_for_component()`.

Do not bump `_CheckContext` schema; existing `source_payload` + periods already contain the required facts.

### 5C. Trusted workbook boundary

If any semantic practice cell belongs to `Earnings Quality`:

- require `Earnings Quality` in both Trainer and Answer Key;
- run `_validate_trusted_sheet_cells()` on it;
- exclude only semantic practice coordinates on that sheet;
- keep populated Net Income / Total Assets links, labels, headers, and all other cells trusted.

This must catch tampering with the populated Net Income or Total Assets rows before grading.

### Tests

- [ ] Exact formula passes for each quality family.
- [ ] Equivalent formula with correct cached value passes.
- [ ] Wrong equivalent value fails.
- [ ] Blank remains yellow.
- [ ] Tampering with populated Reported Net Income row fails before recoloring.
- [ ] Tampering with populated Total Assets row fails before recoloring when asset-scaled diagnostics exist.
- [ ] Existing classification and normalization judgment choices still compose with Check.

---

## Task 6 — Integrate Trainer grouping and applicability gating

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `core/tests/test_earnings_quality.py`

Extend the family metadata used by `group_components_by_family()`:

```python
family_meta.update({f.id: f for f in QUALITY_COMPONENT_CATALOG})
```

No separate blanking logic is needed: semantic practice cells must continue to flow through the existing generic practice-cell blanking/decorating path.

Update `TRAINER_INDEX_INSTRUCTION` only enough to state that the learner now completes historical model-construction **and earnings-quality diagnostic** formula schedules. Do not add interpretation claims.

### Applicability tests

**Demo with CFO + Total Assets**

The quality layer is present with all five families.

**CFO available, Total Assets unavailable**

Only these three families exist:

```text
operating_cash_flow_link
cash_conversion_ratio
total_accruals
```

No Average Total Assets or Accrual Ratio practice components are generated.

**CFO unavailable**

- no `Earnings Quality` sheet;
- no quality components;
- historical build still succeeds if the rest of the supplied financials are valid;
- do not invent CFO from other cash-flow subtotals.

**Ambiguous CFO**

Build fails clearly through the resolver rather than silently disabling quality analysis.

---

## Task 7 — Acceptance counts for the illustrative demo

The existing demo has a resolvable operating cash-flow line and total assets, so Step 9A expands the active practice surface by exactly 23 cells / 5 families.

### Base build, no normalization assumptions

Prior:

```text
25 families
118 practice cells
```

Step 9A expected:

```text
30 families
141 practice cells
```

### Normalization build

Prior:

```text
29 families
138 practice cells
```

Step 9A expected:

```text
34 families
161 practice cells
```

Update tests that previously asserted 25/118 or 29/138 only where they represent the active demo product surface.

Do **not** delete regression coverage for the pre-quality surface. Add a CFO-unavailable fixture/build proving that the historical product can still remain at the prior surface when quality inputs are genuinely unavailable.

---

## Task 8 — Documentation and verification

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after verification
- Do not modify: `TARGET.md`

### User-facing wording

Describe Step 9A narrowly:

```text
Historical earnings-quality diagnostics:
- operating cash-flow link
- cash conversion ratio
- total accruals
- average total assets where supplied
- accrual ratio where supplied
```

State explicitly that these are mechanical diagnostics and do not yet explain *why* conversion changed or grade an investment conclusion.

### Verification

Run focused tests:

```bash
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
```

Then existing regression suites:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Then:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual final pass count; do not predeclare it.

### Build verification — base

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
Components resolved: 141
Checked 141 practice cells: 0 correct, 0 incorrect, 141 blank.
30 schedule groups
```

### Build verification — normalization

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
Components resolved: 161
Checked 161 practice cells: 0 correct, 0 incorrect, 161 blank.
34 schedule groups
```

Verify public CLI remains:

```bash
PYTHONPATH=. python -m core --help
```

```text
ingest
build
check
list
```

### `RESULT.md` must record

- actual full-suite pass count;
- canonical CFO resolution coverage;
- curly-apostrophe line-resolution regression;
- quality module applicability rules;
- demo five-family / 23-cell quality expansion;
- base 30 / 141 surface;
- normalization 34 / 161 surface;
- trusted-state protection for populated quality rows;
- no invented CFO or total-assets data;
- no quality thresholds or automatic interpretation;
- forecast/scenario engine still not called;
- `TARGET.md` unchanged.

---

## Definition of done

Step 9A is complete only when:

1. `operating_cash_flow` resolves canonically from explicit concept or narrow final-CFO aliases.
2. Curly apostrophes are normalized correctly by the shared line resolver.
3. Missing CFO disables the earnings-quality module without fabricated data.
4. Ambiguous CFO fails clearly.
5. CFO availability enables cash conversion and total-accrual diagnostics.
6. Total-assets availability independently gates average-assets / accrual-ratio diagnostics.
7. `Earnings Quality` formulas are generated from the authoritative historical reference model.
8. Trainer quality practice cells are blank yellow with no answers/hints.
9. Answer Key quality practice cells contain working formulas + Notes.
10. Dynamic Check recomputes quality expected values from Check context source facts.
11. Non-practice quality-sheet cells are protected by the trusted-state gate.
12. No automatic good/bad quality score or threshold is introduced.
13. Demo base surface is 30 families / 141 cells.
14. Demo normalization surface is 34 families / 161 cells.
15. Full regression suite passes.
16. `TARGET.md` remains unchanged.
17. Forecasting, valuation, and later research interpretation have not begun.

After finishing this checkpoint, stop and report changed files, focused test outputs, full-suite output, and both build/check/list results. Do not commit or push.
