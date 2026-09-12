# Step 9C.1 — Historical RNOA Margin / Turnover Driver Decomposition

> **Status:** Step 9C.1 complete. See `RESULT.md` for verification evidence (219 passed; base 45/204; normalization 49/224; RNOA = Margin × Turnover driver bridge on ALT DuPont). Do not commit or push from this checkpoint unless the user requests it.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `70f2af5de1d2b5938867529ae03a96b7015be9a8` (`Step 9B.2 complete`). Implement only Step 9C.1 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, Step 9A earnings-quality/source-completeness/`#N/A` semantics, and the complete Step 9B working-capital diagnostic surface. Do not add automatic good/bad profitability labels, company-specific causal inference, forecasting, valuation, ROU/deferred-tax alternative modeling, segment analysis, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Add an auditable historical decomposition of RNOA into operating margin and net-operating-asset turnover/capital intensity so the learner can distinguish profitability changes caused by operating margin from those caused by the amount of operating assets required to support Revenue.

**Architecture:** Reuse the authoritative `AnchorMetrics` series and existing `ALT DuPont` schedule. Add one focused `ProfitabilityDriverSeries` plus four comparable-period semantic families: Average NOA, NOA Turnover, NOA Intensity, and RNOA from Margin × Turnover. Append a driver section to `ALT DuPont`; keep the existing direct RNOA formula untouched and add a generated non-practice reconciliation row. Dynamic Formula Check must recompute these diagnostics from the current live classification treatment.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `AnchorMetrics`, `ratio_or_na`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and trusted-sheet validation for `ALT DuPont`.

**Spec:** `TARGET.md`, especially the interpretation requirement: “Was a decline in RNOA caused by lower operating margins or greater NOA intensity?”, historical capital-intensity diagnostics, operating/financing reformulation, and the requirement that formula correctness support economic interpretation without unsupported causal claims.

---

## Review of commit `70f2af5d`

Step 9B.2 is complete and coherent:

- the five-year applicable working-capital module is 11 families / 47 practice cells;
- Change in OWCA and Change in OWCL reconcile mechanically to direct Change in NOWC;
- incremental OWCA / OWCL ratios preserve signed Revenue changes and `#N/A` denominator semantics;
- the generated `DRIVER DECOMPOSITION CHECK` is trusted and tamper-detected;
- live classification treatment changes working-capital dynamic expected values;
- base demo is 41 families / 188 cells;
- normalization demo is 45 families / 208 cells;
- `RESULT.md` records 213 locally passing tests;
- GitHub has no attached CI status.

The next historical diagnostic should move from working-capital mechanics to profitability drivers. The existing `ALT DuPont` already contains NOPAT Margin and direct RNOA, but it does not expose the capital-efficiency term that connects them.

The BAV identity for comparable periods is:

```text
RNOA = NOPAT / Average NOA
     = (NOPAT / Revenue) × (Revenue / Average NOA)
     = NOPAT Margin × NOA Turnover
```

The reciprocal operating-capital-intensity view is:

```text
NOA Intensity = Average NOA / Revenue
```

Step 9C.1 adds this mechanical decomposition only. It must not automatically conclude why margin or capital intensity changed.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all existing Step 8 judgment behavior and treatment-conditioned Check.
- Preserve Step 9A earnings-quality, source-completeness, tax, normalization, and `#N/A` semantics.
- Preserve all 11 Step 9B working-capital families unchanged.
- Preserve the existing direct `RNOA` and `NOPAT Margin` families and formulas unchanged.
- Revenue must come from `AnchorMetrics.historical.revenue` / existing Condensed Revenue.
- NOPAT must come from `AnchorMetrics.historical.nopat` / existing Condensed NOPAT.
- NOA must come from `AnchorMetrics.reformulation.noa` / existing Condensed NOA.
- Average NOA for fiscal period `i > 0` is `(NOA[i - 1] + NOA[i]) / 2`.
- First-period Average NOA / turnover / intensity / driver RNOA are non-applicable because no prior NOA exists.
- `NOA Turnover = Revenue / Average NOA`.
- `NOA Intensity = Average NOA / Revenue`.
- `RNOA from Margin × Turnover = NOPAT Margin × NOA Turnover` when both inputs are defined.
- Zero Average NOA makes NOA Turnover undefined (`#N/A`).
- Zero Revenue makes NOA Intensity and NOPAT Margin undefined (`#N/A`).
- A zero numerator with a valid nonzero denominator remains a valid numeric zero.
- If the margin/turnover decomposition is undefined, do not label that as a failed RNOA reconciliation merely because direct RNOA remains mathematically defined.
- Do not use absolute values to hide negative Revenue, NOA, margin, or turnover signs.
- Do not infer pricing power, cost inflation, asset quality, capacity utilization, acquisition effects, or business-model causes automatically from these ratios.
- Do not add automatic good/bad profitability scoring.
- Do not add free-form automatic grading.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior in this checkpoint.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Define authoritative profitability-driver series

**Files:**
- Create: `core/model/profitability_drivers.py`
- Create: `core/tests/test_profitability_drivers.py`

Create:

```python
from __future__ import annotations

from dataclasses import dataclass

from .financial_math import AnchorMetrics
from .ratio_values import UNDEFINED_RATIO, ratio_or_na


@dataclass(frozen=True)
class ProfitabilityDriverSeries:
    average_noa: tuple[float | None, ...]
    noa_turnover: tuple[float | str | None, ...]
    noa_intensity: tuple[float | str | None, ...]
    rnoa_from_margin_turnover: tuple[float | str | None, ...]
```

Create:

```python
def compute_profitability_driver_series(
    anchor: AnchorMetrics,
) -> ProfitabilityDriverSeries:
    ...
```

### Source series

Use exactly:

```python
revenue = tuple(float(v) for v in anchor.historical.revenue)
noa = tuple(float(v) for v in anchor.reformulation.noa)
margin = tuple(anchor.dupont["NOPAT Margin"])
direct_rnoa = tuple(anchor.dupont["RNOA"])
```

Require all four series to have the same nonzero length. Raise a clear `ValueError` showing each length if they do not.

### First period

Initialize:

```python
average_noa = [None]
noa_turnover = [None]
noa_intensity = [None]
rnoa_from_margin_turnover = [None]
```

### Comparable periods

For every `i > 0`:

```python
average = (noa[i - 1] + noa[i]) / 2.0
turnover = ratio_or_na(revenue[i], average)
intensity = ratio_or_na(average, revenue[i])

if margin[i] == UNDEFINED_RATIO or turnover == UNDEFINED_RATIO:
    driver_rnoa: float | str = UNDEFINED_RATIO
else:
    driver_rnoa = float(margin[i]) * float(turnover)
```

Append those values.

### Reconciliation semantics

When `driver_rnoa` is numeric, direct RNOA must also be numeric and must reconcile:

```python
if driver_rnoa != UNDEFINED_RATIO:
    if direct_rnoa[i] == UNDEFINED_RATIO:
        raise ValueError(
            "RNOA driver bridge is numeric while direct RNOA is undefined: "
            f"period_index={i} driver={driver_rnoa}"
        )
    if abs(float(driver_rnoa) - float(direct_rnoa[i])) > 1e-9:
        raise ValueError(
            "RNOA margin/turnover bridge does not reconcile: "
            f"period_index={i} direct={direct_rnoa[i]} driver={driver_rnoa}"
        )
```

When `driver_rnoa == #N/A`, do **not** require direct RNOA to be `#N/A`. Example: Revenue can be zero while Average NOA is nonzero, making the margin/turnover decomposition undefined even though direct `NOPAT / Average NOA` may still be numerically defined.

### Required semantics

```text
Revenue = 200
NOPAT Margin = 10%
Average NOA = 100
NOA Turnover = 2.0x
NOA Intensity = 0.5x
RNOA from drivers = 20%
```

Also preserve:

```text
Average NOA = 0 -> NOA Turnover #N/A
Revenue = 0     -> NOA Intensity #N/A and existing NOPAT Margin #N/A
Revenue = 0, Average NOA != 0 -> NOA Turnover may be numeric 0.0
zero Revenue does not force direct RNOA itself to #N/A
```

### TDD

- [ ] ordinary multi-period fixture returns all four series correctly;
- [ ] first-period values are all `None`;
- [ ] zero Average NOA makes NOA Turnover `#N/A`;
- [ ] zero Revenue makes NOA Intensity `#N/A`;
- [ ] zero Revenue with nonzero Average NOA keeps NOA Turnover at numeric `0.0`;
- [ ] numeric margin × turnover reconciles to direct RNOA;
- [ ] undefined driver RNOA does not falsely raise when direct RNOA is numeric;
- [ ] a deliberately inconsistent numeric RNOA fixture raises the reconciliation `ValueError`;
- [ ] source-series length mismatch fails clearly.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_profitability_drivers.py -v
```

---

## Task 2 — Add four profitability-driver semantic families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_profitability_drivers.py`
- Test: `core/tests/test_reference_integrity.py`

Create a separate catalog so the original historical-construction core and existing diagnostic catalogs remain unchanged:

```python
PROFITABILITY_DRIVER_COMPONENT_CATALOG: tuple[ComponentFamily, ...] = (...)
```

Add:

```python
def expand_profitability_driver_specs(
    periods: list[date],
    *,
    start_order: int,
) -> tuple[ComponentSpec, ...]:
    ...
```

Use the same duplicate/chronological-period validation as the other expanders.

All four families use `period_scope="comparable"` and tab `ALT DuPont`.

### 1. `average_noa`

```text
family order: 46
title: Average Net Operating Assets
formula concept: (Prior NOA + Current NOA) / 2
```

Dependencies:

```python
depends_on_current=("noa_agg",)
depends_on_previous=("noa_agg",)
```

Hints:

```text
Average NOA = (Beginning NOA + Ending NOA) / 2.
Use the same Average NOA denominator as direct RNOA.
```

### 2. `noa_turnover`

```text
family order: 47
title: Net Operating Asset Turnover
formula concept: Revenue / Average NOA
```

Dependencies:

```python
depends_on_current=("revenue_link", "average_noa")
```

Hints:

```text
NOA Turnover = Revenue / Average NOA.
Higher turnover means more Revenue is generated per unit of net operating assets, but the cause requires separate analysis.
A zero Average NOA denominator makes the ratio undefined (#N/A).
```

### 3. `noa_intensity`

```text
family order: 48
title: Net Operating Asset Intensity
formula concept: Average NOA / Revenue
```

Dependencies:

```python
depends_on_current=("average_noa", "revenue_link")
```

Hints:

```text
NOA Intensity = Average NOA / Revenue.
It expresses how much net operating asset investment supports each unit of Revenue.
A zero Revenue denominator makes the ratio undefined (#N/A).
```

### 4. `rnoa_margin_turnover`

```text
family order: 49
title: RNOA from Margin × Turnover
formula concept: NOPAT Margin × NOA Turnover
```

Dependencies:

```python
depends_on_current=("nopat_margin", "noa_turnover")
```

Hints:

```text
RNOA = NOPAT Margin × NOA Turnover when both terms are defined.
This separates operating profitability per sales dollar from operating-asset efficiency.
If either required driver is undefined, the decomposition is also undefined (#N/A).
```

### Expected values

In `core/model/historical_expected.py`, import the new catalog and:

```python
from .profitability_drivers import compute_profitability_driver_series
```

Add:

```python
_PROFITABILITY_DRIVER_FAMILY_SERIES = (
    "average_noa",
    "noa_turnover",
    "noa_intensity",
    "rnoa_margin_turnover",
)
```

Create:

```python
def profitability_driver_expected_series(
    anchor: AnchorMetrics,
) -> dict[str, tuple[float | str | None, ...]]:
    drivers = compute_profitability_driver_series(anchor)
    series = {
        "average_noa": drivers.average_noa,
        "noa_turnover": drivers.noa_turnover,
        "noa_intensity": drivers.noa_intensity,
        "rnoa_margin_turnover": drivers.rnoa_from_margin_turnover,
    }
    expected_ids = {
        family.id for family in PROFITABILITY_DRIVER_COMPONENT_CATALOG
    }
    if set(series) != expected_ids:
        ...
    return {
        family_id: series[family_id]
        for family_id in _PROFITABILITY_DRIVER_FAMILY_SERIES
    }
```

Use the same explicit missing/extra `ValueError` pattern as the other expected-series helpers.

Extend `expected_value_for_component()` with a profitability-driver branch before falling back to historical core families.

### Expansion acceptance

For five fiscal periods:

```text
4 families × 4 comparable periods = 16 practice cells
```

TDD:

- [ ] new catalog contains exactly four unique IDs;
- [ ] all four families are comparable-period families;
- [ ] five demo periods expand to exactly 16 concrete specs;
- [ ] expected-series keys exactly equal catalog IDs;
- [ ] existing historical / normalization / quality / working-capital catalog definitions remain unchanged;
- [ ] `rnoa_margin_turnover` expected values reconcile to direct RNOA whenever numeric.

---

## Task 3 — Wire profitability drivers into `ReferenceModelBuilder`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_profitability_drivers.py`
- Test: `core/tests/test_reference_integrity.py`

Import:

```python
from ..model.profitability_drivers import compute_profitability_driver_series
```

and:

```python
from .component_catalog import expand_profitability_driver_specs
```

After existing historical / normalization / quality / working-capital specs are established, always compute:

```python
self.profitability_driver_series = compute_profitability_driver_series(self.anchor)
self.profitability_driver_specs = expand_profitability_driver_specs(
    self.periods,
    start_order=(
        len(self.historical_specs)
        + len(self.normalization_specs)
        + len(self.quality_specs)
        + len(self.working_capital_specs)
        + 1
    ),
)
```

Then append:

```python
self.expected_specs = (
    self.historical_specs
    + self.normalization_specs
    + self.quality_specs
    + self.working_capital_specs
    + self.profitability_driver_specs
)
```

Create:

```python
self._profitability_driver_spec_index = {
    (s.family_id, s.period_index): s
    for s in self.profitability_driver_specs
}
```

Add a registration helper analogous to `_register_working_capital()`:

```python
def _register_profitability_driver(
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
    spec = self._profitability_driver_spec_index[(family_id, period_index)]
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

Do not create a new worksheet.

---

## Task 4 — Append the RNOA driver section to `ALT DuPont`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_profitability_drivers.py`
- Test: `core/tests/test_reference_integrity.py`

Keep all existing `ALT DuPont` rows and formulas unchanged. Append the new section after the existing `Actual ROE` row.

Derive rows dynamically:

```python
driver_section_row = actual_row + 2
average_noa_row = driver_section_row + 1
turnover_row = driver_section_row + 2
intensity_row = driver_section_row + 3
driver_rnoa_row = driver_section_row + 4
driver_check_row = driver_section_row + 5
```

Labels:

```text
RNOA DRIVER DECOMPOSITION
Average NOA
NOA Turnover
NOA Intensity
RNOA from Margin × Turnover
RNOA DRIVER CHECK
```

Make the section label and check label bold.

### First fiscal period

Write literal visible `N/A` in all five metric/check rows. Do not register first-period practice components.

### Comparable-period formulas

For every `j > 0`:

```python
average_noa = (
    f"=('Condensed Financials'!{src_prev}{noa_r}+"
    f"'Condensed Financials'!{src_col}{noa_r})/2"
)
turnover = (
    f"=IF({out_col}{average_noa_row}=0,NA(),"
    f"'Condensed Financials'!{src_col}{rev_r}/{out_col}{average_noa_row})"
)
intensity = (
    f"=IF('Condensed Financials'!{src_col}{rev_r}=0,NA(),"
    f"{out_col}{average_noa_row}/'Condensed Financials'!{src_col}{rev_r})"
)
driver_rnoa = f"={out_col}{margin_row}*{out_col}{turnover_row}"
```

Use number formats:

```text
Average NOA -> NUM_FMT
NOA Turnover -> "0.00x"
NOA Intensity -> "0.00x"
RNOA from Margin × Turnover -> PCT_FMT
```

Register rows `average_noa_row`, `turnover_row`, `intensity_row`, and `driver_rnoa_row` as the four new formula families.

### Reconciliation formula

The check must distinguish an unavailable decomposition from a genuine inconsistency:

```python
driver_check = (
    f'=IF(ISNA({out_col}{driver_rnoa_row}),"N/A",'
    f'IF(ISNA({out_col}{rnoa_row}),"CHECK",'
    f'IF(ABS({out_col}{driver_rnoa_row}-{out_col}{rnoa_row})<0.0000001,'
    f'"OK","CHECK")))'
)
```

This row is generated non-practice logic.

Required behavior:

```text
numeric driver RNOA == direct RNOA -> OK
driver decomposition #N/A          -> N/A
driver numeric but direct #N/A     -> CHECK
numeric mismatch                    -> CHECK
```

Do not use `IFERROR(...,"OK")` or convert undefined ratios to zero.

Add rowmap entries:

```python
self.rowmap["dupont_average_noa_row"] = average_noa_row
self.rowmap["dupont_noa_turnover_row"] = turnover_row
self.rowmap["dupont_noa_intensity_row"] = intensity_row
self.rowmap["dupont_driver_rnoa_row"] = driver_rnoa_row
self.rowmap["dupont_driver_check_row"] = driver_check_row
```

TDD:

- [ ] all existing ALT DuPont labels/formulas remain at their prior coordinates;
- [ ] new section appears after Actual ROE;
- [ ] first-period cells show literal `N/A`;
- [ ] comparable Average NOA uses prior/current Condensed NOA;
- [ ] turnover guards zero Average NOA with `NA()`;
- [ ] intensity guards zero Revenue with `NA()`;
- [ ] driver RNOA multiplies existing NOPAT Margin by new NOA Turnover;
- [ ] reconciliation returns `OK` for ordinary demo periods;
- [ ] reconciliation returns `N/A` when the decomposition itself is undefined;
- [ ] reconciliation row is not a practice component;
- [ ] Answer Key has formulas + Notes for the 16 new practice cells;
- [ ] Trainer has those cells blank bright yellow with no comments.

---

## Task 5 — Prove classification-conditioned profitability drivers

**Files:**
- Modify: `core/tests/test_profitability_drivers.py`
- Modify: `core/tests/test_reference_integrity.py`

Use the existing live classification judgment machinery. Select an existing balance-sheet case whose alternative treatment changes NOA, such as a line moving between Financial Asset and Operating Working Capital Asset.

Prove that changing `Accounting Judgment!F` changes current-state expected values for:

```text
Average NOA
NOA Turnover
NOA Intensity
RNOA from Margin × Turnover
direct RNOA
```

Formula Check must:

- accept exact formulas under either allowed classification treatment;
- accept equivalent formulas whose cached values match the current treatment;
- reject a stale cached value generated under the previous treatment.

Do not change `_CheckContext` schema. These diagnostics derive entirely from the classification-conditioned `AnchorMetrics` already recomputed by Check.

---

## Task 6 — Protect generated reconciliation and preserve `#N/A` behavior

**Files:**
- Modify: `core/tests/test_profitability_drivers.py`
- Modify: `core/tests/test_reference_integrity.py`
- Production code: only if a failing test proves current generic trusted-sheet validation is insufficient

`ALT DuPont` is already a trusted sheet outside semantic practice cells. The new `RNOA DRIVER CHECK` row must therefore be protected automatically.

Add regressions covering:

### Trusted-row tamper

1. Build a Trainer/Answer-Key pair.
2. Enter one valid new profitability-driver formula in a Trainer practice cell.
3. Overwrite one comparable-period `RNOA DRIVER CHECK` formula.
4. Run Check.
5. Require structural `ValueError` before recoloring.
6. Reopen Trainer and prove the learner practice cell remains yellow.

### Undefined decomposition

Create a fixture with zero Revenue but nonzero Average NOA:

```text
NOPAT Margin -> #N/A
NOA Turnover -> numeric 0.0
NOA Intensity -> #N/A
RNOA from Margin × Turnover -> #N/A
```

The generated reconciliation must show `N/A`, not `CHECK` or `OK`.

### Formula Check `#N/A`

For one undefined new ratio:

- exact formula -> green;
- structurally different formula with cached `#N/A` -> green;
- fabricated cached `0.0` when expected `#N/A` -> red.

Reuse the existing cached-error test helper rather than creating production-only logic.

---

## Task 7 — Update trainer/index metadata and acceptance counts

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: count assertions in relevant tests

Import `PROFITABILITY_DRIVER_COMPONENT_CATALOG` in `core/trainer/workbook.py` and include it in `family_meta` so `core list` and the Trainer index render the four new schedules correctly.

Do not change grouping semantics for existing families.

Five-year acceptance surfaces after Step 9C.1:

```text
base demo:          45 families / 204 practice cells
normalization demo: 49 families / 224 practice cells
```

Profitability-driver contribution:

```text
4 families / 16 practice cells
```

Update `skills/bav-trainer/SKILL.md` to describe the new historical profitability-driver surface as:

```text
RNOA margin / NOA-turnover decomposition and NOA intensity
```

Do not claim that the trainer automatically explains the business cause of margin or turnover changes.

---

## Task 8 — Full verification and checkpoint evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all verification passes
- Do not modify: `TARGET.md`

Run focused suites:

```bash
PYTHONPATH=. pytest core/tests/test_profitability_drivers.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
```

Then run the complete suite:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual pass count; do not predeclare it.

Verify base build:

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
204 practice cells
0 correct / 0 incorrect / 204 blank
45 schedule groups
```

Verify normalization build:

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
224 practice cells
0 correct / 0 incorrect / 224 blank
49 schedule groups
```

Verify CLI remains unchanged:

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

`RESULT.md` must record:

- actual full-suite pass count;
- 4 profitability-driver families / 16 practice cells in the five-year demo;
- Average NOA calculation;
- NOA Turnover and NOA Intensity;
- RNOA = NOPAT Margin × NOA Turnover reconciliation when defined;
- undefined decomposition yields `N/A` rather than a false failure;
- live-classification treatment changes NOA-based dynamic expected values;
- generated RNOA driver-check tamper fails before recoloring;
- exact/equivalent `#N/A` formulas pass and fabricated `0.0` fails;
- base 45 / 204 surface;
- normalization 49 / 224 surface;
- no automatic causal diagnosis, forecasting, or valuation introduced;
- `TARGET.md` unchanged.

---

## Definition of done

Step 9C.1 is complete only when:

1. Average NOA is an explicit comparable-period formula family.
2. NOA Turnover is an explicit comparable-period formula family.
3. NOA Intensity is an explicit comparable-period formula family.
4. RNOA from NOPAT Margin × NOA Turnover is an explicit comparable-period formula family.
5. Numeric driver RNOA reconciles to direct RNOA within tolerance.
6. Undefined margin/turnover decomposition remains `#N/A` and does not create a false reconciliation failure.
7. Zero Average NOA produces `#N/A` turnover.
8. Zero Revenue produces `#N/A` intensity.
9. Existing direct RNOA and NOPAT Margin formulas remain unchanged.
10. Live classification treatment dynamically changes NOA-based driver expecteds.
11. Generated `RNOA DRIVER CHECK` is trusted non-practice logic and tampering fails before recoloring.
12. The five-year profitability-driver module is 4 families / 16 practice cells.
13. Base demo is 45 families / 204 practice cells.
14. Normalization demo is 49 families / 224 practice cells.
15. Full test suite passes.
16. `TARGET.md` is unchanged.
17. No automatic profitability-quality judgment, company-specific causal inference, forecasting, or valuation has been introduced.

After completing Step 9C.1, stop and report changed files, exact test output, demo build/check/list output, RNOA reconciliation evidence, live-classification evidence, and any new active historical-model issue found during implementation. Do not proceed to forecasting or valuation, and do not commit or push.
