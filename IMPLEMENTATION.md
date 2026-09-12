# Step 9B.2 — Historical Working-Capital Driver Decomposition

> **Status:** Step 9B.2 complete. See `RESULT.md` for verification evidence (213 passed; base 41/188; normalization 45/208; OWCA/OWCL driver bridge + trusted DRIVER DECOMPOSITION CHECK). Do not commit or push from this checkpoint unless the user requests it.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `57bcda4af010a70f21bb7515d03486e83e5be936` (`StepB.1`, Step 9B.1 complete). Implement only Step 9B.2 below using red/green TDD. Preserve Step 8 classification/normalization judgment, the trusted-workbook boundary, Step 9A earnings-quality/source-completeness/`#N/A` semantics, and the complete Step 9B.1 Working Capital Analysis surface. Do not add automatic good/bad quality labels, line-item causal inference, seasonality claims, forecasting, valuation, ROU/deferred-tax alternative modeling, segment analysis, or later research-diagnostic work. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Extend the Working Capital Analysis from one net `Change in NOWC` measure into an auditable driver bridge showing how changes in Operating Working Capital Assets and Operating Working Capital Liabilities combine into the net working-capital investment, and how each side moves relative to incremental Revenue.

**Architecture:** Extend the existing `WorkingCapitalSeries`, `WORKING_CAPITAL_COMPONENT_CATALOG`, and `Working Capital Analysis` sheet rather than creating another subsystem. Use only the already treatment-conditioned OWCA / OWCL / NOWC / Revenue series. Add five comparable-period formula families and one generated non-practice reconciliation row. Formula Check must recompute these families from the learner's live classification treatment, while trusted-sheet validation protects the generated reconciliation formula automatically.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `AnchorMetrics`, `WorkingCapitalSeries`, `ratio_or_na`, `ComponentFamily`, `SemanticMap`, `ReferenceModelBuilder`, `historical_expected`, `check_workbook`, and trusted-workbook structural validation.

**Spec:** `TARGET.md`, especially working-capital behavior, accounting consistency, research diagnostics, the historical dependency graph, and the requirement that interpretation distinguish mechanical drivers from unsupported causal or quality claims.

---

## Review of commit `57bcda4a`

Step 9B.1 is implemented coherently:

- `Working Capital Analysis` is gated on nonzero classified OWCA / OWCL;
- OWCA / Revenue, OWCL / Revenue, NOWC / Revenue, Change in Revenue, Change in NOWC, and Incremental NOWC / Change in Revenue are live formula families;
- zero Revenue / zero Change in Revenue produce `#N/A` / Excel `NA()` rather than fabricated zero ratios;
- first-period change metrics remain non-applicable;
- live classification judgment changes dynamic expected values correctly;
- trusted-sheet validation protects generated Working Capital Analysis cells;
- the current five-year demo surfaces are 36 families / 168 cells without normalization and 40 families / 188 cells with normalization;
- `RESULT.md` records 210 locally passing tests;
- GitHub has no attached CI status.

The current sheet answers **how much net working capital changed**, but it does not yet show **which side of the operating working-capital equation produced that change**.

Because:

```text
NOWC = OWCA - OWCL
```

then:

```text
Change in NOWC = Change in OWCA - Change in OWCL
```

This decomposition is the next safe interpretation step. It remains mechanical and auditable: it does not infer whether receivables, inventory, payables, collection quality, purchasing power, or management behavior caused the aggregate movement.

Step 9B.2 therefore adds an **asset-versus-liability driver bridge only**.

---

## Global constraints

- `TARGET.md` is read-only.
- Preserve non-financial-company scope.
- Preserve all existing Step 8 judgment behavior and treatment-conditioned Check.
- Preserve Step 9A earnings-quality, source-completeness, and `#N/A` semantics.
- Preserve Step 9B.1 applicability gating exactly: all-zero OWCA and OWCL omit the Working Capital Analysis sheet.
- Preserve the existing six Step 9B.1 working-capital families unchanged.
- Use only the authoritative treatment-conditioned series from `AnchorMetrics` / `BalanceSheetReformulation`; do not independently reclassify raw balance-sheet labels.
- `Change in OWCA` means current OWCA minus prior OWCA.
- `Change in OWCL` means current OWCL minus prior OWCL.
- `Change in NOWC from Components = Change in OWCA - Change in OWCL`.
- Positive Change in OWCA is additional operating-current-asset investment / cash use; negative Change in OWCA is a release. Do not call either automatically good or bad.
- Positive Change in OWCL is additional operating-liability financing that offsets NOWC investment; negative Change in OWCL reduces that financing and increases cash use. Do not call either automatically good or bad.
- A zero Change in Revenue denominator makes each incremental-side ratio undefined (`#N/A`).
- Retain signed changes and signed denominators. Do not take absolute values.
- When Revenue declines, an incremental ratio may have an unintuitive sign. Preserve the arithmetic and explain that the sign requires interpretation rather than normalizing it away.
- Annual historical data alone must not be described as proving seasonality.
- Do not infer receivables collection problems, inventory obsolescence, channel stuffing, payment stretching, supplier stress, or other line-item causes from aggregate OWCA / OWCL movements.
- Do not automatically rank or label working-capital quality.
- Do not add free-form automatic grading.
- Do not add forecasting, valuation, scenarios, Hint/Reveal, VBA, or new public CLI commands.
- Do not modify dormant forecast/scenario behavior in this checkpoint.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Extend the authoritative working-capital series with side-driver changes

**Files:**
- Modify: `core/model/working_capital.py`
- Test: `core/tests/test_working_capital.py`

Extend `WorkingCapitalSeries` to:

```python
@dataclass(frozen=True)
class WorkingCapitalSeries:
    owca_to_revenue: tuple[float | str, ...]
    owcl_to_revenue: tuple[float | str, ...]
    nowc_to_revenue: tuple[float | str, ...]
    revenue_change: tuple[float | None, ...]
    nowc_change: tuple[float | None, ...]
    incremental_nowc_to_revenue_change: tuple[float | str | None, ...]
    owca_change: tuple[float | None, ...]
    owcl_change: tuple[float | None, ...]
    nowc_change_from_components: tuple[float | None, ...]
    incremental_owca_to_revenue_change: tuple[float | str | None, ...]
    incremental_owcl_to_revenue_change: tuple[float | str | None, ...]
```

Preserve `_source_series()` and `working_capital_applicable()` unchanged unless a failing test demonstrates a real defect.

### First period

Initialize all five new comparable-period series as non-applicable:

```python
owca_change = [None]
owcl_change = [None]
nowc_change_from_components = [None]
incremental_owca = [None]
incremental_owcl = [None]
```

### Comparable periods

Inside the existing `for i in range(1, n)` loop compute:

```python
delta_revenue = revenue[i] - revenue[i - 1]
delta_nowc = nowc[i] - nowc[i - 1]
delta_owca = owca[i] - owca[i - 1]
delta_owcl = owcl[i] - owcl[i - 1]
bridge_nowc = delta_owca - delta_owcl
```

Require the bridge to reconcile to the direct Change in NOWC:

```python
if abs(bridge_nowc - delta_nowc) > 1e-9:
    raise ValueError(
        "working-capital change bridge does not reconcile: "
        f"period_index={i} direct={delta_nowc} bridge={bridge_nowc}"
    )
```

Append:

```python
owca_change.append(delta_owca)
owcl_change.append(delta_owcl)
nowc_change_from_components.append(bridge_nowc)
incremental_owca.append(ratio_or_na(delta_owca, delta_revenue))
incremental_owcl.append(ratio_or_na(delta_owcl, delta_revenue))
```

Continue using the existing direct:

```python
nowc_change.append(delta_nowc)
incremental.append(ratio_or_na(delta_nowc, delta_revenue))
```

Do not derive the direct `nowc_change` from the bridge. Keeping both independently computed series is what makes the reconciliation useful.

### Required semantics

```text
OWCA: 100 -> 130  => Change in OWCA = +30
OWCL:  40 ->  50  => Change in OWCL = +10
NOWC:  60 ->  80  => direct Change in NOWC = +20
bridge             => +30 - +10 = +20
```

Interpret mechanically:

```text
+30 OWCA change = 30 additional operating-current-asset investment
+10 OWCL change = 10 additional operating-liability financing
net cash tied up  = 20 additional NOWC
```

Also preserve:

```text
negative Change in OWCA -> release of operating-current-asset investment
negative Change in OWCL -> reduction in operating-liability financing
zero Change in Revenue  -> both incremental-side ratios are #N/A
negative Change in Revenue -> signed denominator retained
```

### TDD

- [ ] Ordinary fixture returns all five new series correctly.
- [ ] `nowc_change_from_components[i] == nowc_change[i]` for every comparable period.
- [ ] Positive OWCA and positive OWCL changes produce the correct net bridge.
- [ ] Negative OWCA change remains negative.
- [ ] Negative OWCL change remains negative.
- [ ] Zero Change in Revenue yields `#N/A` for both incremental-side ratios.
- [ ] Negative Change in Revenue is retained as a signed denominator.
- [ ] Zero side-driver numerator with nonzero Change in Revenue yields numeric `0.0`.
- [ ] First-period values for all five new series are `None`.
- [ ] A deliberately inconsistent synthetic `AnchorMetrics` / reformulation fixture triggers the reconciliation `ValueError` rather than silently accepting a broken NOWC identity.

Run:

```bash
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
```

---

## Task 2 — Add five semantic driver-decomposition formula families

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_working_capital.py`
- Test: `core/tests/test_reference_integrity.py`

Extend the existing `WORKING_CAPITAL_COMPONENT_CATALOG` with exactly five new families. Keep the six Step 9B.1 family definitions unchanged.

Use family orders `41` through `45`.

### 1. `owca_change`

```text
order: 41
title: Change in Operating Working Capital Assets
sheet: Working Capital Analysis
period scope: comparable
formula concept: Current OWCA - Prior OWCA
```

Dependencies:

```python
depends_on_current=("owca_agg",)
depends_on_previous=("owca_agg",)
```

Hints:

```text
Change in OWCA = Current OWCA - Prior OWCA.
A positive change is additional operating-current-asset investment; a negative change is a release.
Do not infer the underlying receivables/inventory cause from this aggregate alone.
```

### 2. `owcl_change`

```text
order: 42
title: Change in Operating Working Capital Liabilities
sheet: Working Capital Analysis
period scope: comparable
formula concept: Current OWCL - Prior OWCL
```

Dependencies:

```python
depends_on_current=("owcl_agg",)
depends_on_previous=("owcl_agg",)
```

Hints:

```text
Change in OWCL = Current OWCL - Prior OWCL.
A positive change supplies additional operating-liability financing; a negative change reduces that financing.
Do not infer payment quality or supplier pressure from this aggregate alone.
```

### 3. `nowc_change_from_components`

```text
order: 43
title: Change in NOWC from OWCA / OWCL bridge
sheet: Working Capital Analysis
period scope: comparable
formula concept: Change in OWCA - Change in OWCL
```

Dependencies:

```python
depends_on_current=("owca_change", "owcl_change")
```

Hints:

```text
Because NOWC = OWCA - OWCL, Change in NOWC = Change in OWCA - Change in OWCL.
Use this bridge to separate asset investment from operating-liability financing.
The bridge must reconcile to the direct Change in NOWC row.
```

### 4. `incremental_owca_to_revenue_change`

```text
order: 44
title: Incremental OWCA / Change in Revenue
sheet: Working Capital Analysis
period scope: comparable
formula concept: Change in OWCA / Change in Revenue
```

Dependencies:

```python
depends_on_current=("owca_change", "revenue_change")
```

Hints:

```text
This ratio measures incremental operating-current-asset investment per unit of incremental sales.
A zero Change in Revenue denominator makes the ratio undefined (#N/A).
Keep the signed denominator when Revenue falls; do not convert it to an absolute value.
```

### 5. `incremental_owcl_to_revenue_change`

```text
order: 45
title: Incremental OWCL / Change in Revenue
sheet: Working Capital Analysis
period scope: comparable
formula concept: Change in OWCL / Change in Revenue
```

Dependencies:

```python
depends_on_current=("owcl_change", "revenue_change")
```

Hints:

```text
This ratio measures incremental operating-liability financing per unit of incremental sales.
A zero Change in Revenue denominator makes the ratio undefined (#N/A).
A larger value is not automatically good; it only shows that more operating liabilities accompany the sales change.
```

### Expected values

Extend `_WORKING_CAPITAL_FAMILY_SERIES` in `core/model/historical_expected.py` to include the five new family IDs.

Extend `working_capital_expected_series()` with:

```python
"owca_change": wc.owca_change,
"owcl_change": wc.owcl_change,
"nowc_change_from_components": wc.nowc_change_from_components,
"incremental_owca_to_revenue_change": wc.incremental_owca_to_revenue_change,
"incremental_owcl_to_revenue_change": wc.incremental_owcl_to_revenue_change,
```

The existing exact catalog-key equality check must now cover all eleven working-capital families.

### Expected expansion

All five new families are comparable-period families.

For five modeled fiscal periods:

```text
5 new families × 4 comparable periods = 20 new practice cells
```

The complete working-capital module therefore becomes:

```text
11 families
47 practice cells
```

### TDD

- [ ] Working-capital catalog now contains exactly 11 unique family IDs.
- [ ] Existing first six family definitions remain unchanged.
- [ ] Each new family expands across four comparable periods in the five-year demo.
- [ ] Exactly 20 new concrete specs are added.
- [ ] `working_capital_expected_series()` keys exactly equal the 11 catalog IDs.
- [ ] `nowc_change_from_components` expected values equal direct `nowc_change` for all comparable periods.
- [ ] Incremental OWCA / OWCL expected values preserve `#N/A` on zero Change in Revenue.

---

## Task 3 — Add the driver-decomposition section to `Working Capital Analysis`

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_working_capital.py`
- Test: `core/tests/test_reference_integrity.py`

Do not create a new worksheet. Extend `_build_working_capital_analysis()` below the existing Step 9B.1 rows.

Use this fixed layout:

```text
A18  WORKING-CAPITAL DRIVER DECOMPOSITION
A19  Change in OWCA
A20  Change in OWCL
A21  Change in NOWC from Components
A22  Incremental OWCA / Change in Revenue
A23  Incremental OWCL / Change in Revenue
A24  DRIVER DECOMPOSITION CHECK
```

Make row 18 bold as a section heading. Make row 24 bold.

### First period

For the first fiscal period, write visible literal text:

```text
N/A
```

into rows 19 through 24. Do not register first-period practice components for these comparable families.

### Comparable-period formulas

For each `j > 0`, use the existing source-link rows already present on this sheet:

```python
owca_change = f"={col}{owca_row}-{prev_col}{owca_row}"
owcl_change = f"={col}{owcl_row}-{prev_col}{owcl_row}"
nowc_bridge = f"={col}{owca_change_row}-{col}{owcl_change_row}"
incremental_owca = (
    f"=IF({col}{rev_chg_row}=0,NA(),"
    f"{col}{owca_change_row}/{col}{rev_chg_row})"
)
incremental_owcl = (
    f"=IF({col}{rev_chg_row}=0,NA(),"
    f"{col}{owcl_change_row}/{col}{rev_chg_row})"
)
```

Add a generated, non-practice reconciliation formula:

```python
driver_check = (
    f'=IF(ABS({col}{nowc_bridge_row}-{col}{nowc_chg_row})<0.01,'
    f'"OK","CHECK")'
)
```

Required formats:

```text
Change in OWCA                    -> NUM_FMT
Change in OWCL                    -> NUM_FMT
Change in NOWC from Components    -> NUM_FMT
Incremental OWCA / Change Revenue -> PCT_FMT
Incremental OWCL / Change Revenue -> PCT_FMT
DRIVER DECOMPOSITION CHECK        -> general/text result
```

Register only rows 19 through 23 as practice families. Row 24 is a generated trusted model-control formula.

Use the corresponding values from `self.working_capital_series`.

### Rowmap

Add:

```python
self.rowmap["wc_owca_change_row"] = owca_change_row
self.rowmap["wc_owcl_change_row"] = owcl_change_row
self.rowmap["wc_nowc_bridge_row"] = nowc_bridge_row
self.rowmap["wc_incremental_owca_row"] = incremental_owca_row
self.rowmap["wc_incremental_owcl_row"] = incremental_owcl_row
self.rowmap["wc_driver_check_row"] = driver_check_row
```

Do not move or rename any existing Step 9B.1 rowmap keys.

### TDD

- [ ] Existing Step 9B.1 rows/formulas remain at their current locations.
- [ ] New rows 19–23 contain formulas only for comparable periods.
- [ ] First-period rows 19–24 contain literal `N/A`.
- [ ] Row 21 formula is Change in OWCA minus Change in OWCL.
- [ ] Row 24 checks row 21 against the existing direct Change in NOWC row.
- [ ] Zero Change in Revenue uses Excel `NA()` in both new incremental formulas.
- [ ] No `ABS()` is used inside either incremental ratio formula.
- [ ] The driver-check row is not a semantic practice component.

---

## Task 4 — Prove live classification judgment drives the new decomposition

**Files:**
- Modify: `core/tests/test_working_capital.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_normalization.py` only if an existing cached-value helper is intentionally reused

The new formulas must remain treatment-conditioned through the same live classification architecture as Step 9B.1.

### OWCA-side judgment regression

Reuse the existing demo classification case that can move Short-term Investment between Financial Asset and Operating Working Capital Asset.

For one comparable period:

1. identify an `owca_change` or `incremental_owca_to_revenue_change` component;
2. enter an exact or equivalent formula into its Trainer practice cell;
3. run Check under the reference classification;
4. change `Accounting Judgment!F` to the allowed alternative that changes OWCA;
5. run Check again;
6. prove dynamic expected values reflect the new classification treatment rather than the stale reference result.

At least one regression must reject a cached numeric result that was correct under the old treatment but stale under the new treatment.

### OWCL-side unit coverage

Use a focused synthetic `AnchorMetrics` / reformulation fixture to prove that changing OWCL while holding OWCA constant changes:

```text
owcl_change
nowc_change_from_components
incremental_owcl_to_revenue_change
```

with the correct signs.

Do not create a new artificial judgment type solely to obtain an OWCL live-workbook test.

### `#N/A` Check regression

Construct a fixture with zero Change in Revenue and nonzero Change in OWCA or OWCL.

For at least one new incremental family prove:

- [ ] exact Answer-Key formula passes;
- [ ] structurally different formula with cached `#N/A` passes;
- [ ] fabricated numeric `0.0` is rejected.

Use the existing cached-error injection test mechanism.

---

## Task 5 — Protect and audit the new generated decomposition cells

**Files:**
- Modify: `core/tests/test_working_capital.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/trainer/check_context.py` only if the generic existing trusted-sheet mechanism fails a regression

The existing generic trusted validation for `Working Capital Analysis` should already treat all non-practice cells as system-controlled. Do not add a second special-case validator if the generic mechanism works.

Add a regression:

1. build a Trainer / Answer-Key pair with Working Capital Analysis;
2. enter one valid learner practice formula in a new driver family;
3. overwrite one generated `DRIVER DECOMPOSITION CHECK` formula in the Trainer;
4. run Check;
5. require `ValueError` before any recoloring;
6. reopen the workbook and prove the learner practice cell retained its prior yellow fill.

Also prove that learner edits to the new five semantic practice families are not structurally rejected merely because they differ from the Answer-Key formula text.

Do not compare formatting/styles as trusted state; preserve the existing contents-only integrity contract.

---

## Task 6 — Preserve surface ordering and documentation

**Files:**
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after verification
- Modify: `core/trainer/workbook.py` only if a failing list/index test proves the generic working-capital catalog grouping does not include the five appended families
- Do not modify: `TARGET.md`

The existing generic Trainer grouping already reads `WORKING_CAPITAL_COMPONENT_CATALOG`. The five appended families should therefore appear automatically after the six Step 9B.1 families.

Required family order on the Trainer index:

```text
35  Operating working capital assets / Revenue
36  Operating working capital liabilities / Revenue
37  NOWC / Revenue
38  Change in Revenue
39  Change in NOWC
40  Incremental NOWC / Change in Revenue
41  Change in Operating Working Capital Assets
42  Change in Operating Working Capital Liabilities
43  Change in NOWC from OWCA / OWCL bridge
44  Incremental OWCA / Change in Revenue
45  Incremental OWCL / Change in Revenue
```

Update the skill documentation so it no longer describes the working-capital module as only six families / 27 cells.

For the five-year demo, the completed Step 9B.2 surface must be:

```text
base demo:
41 families
188 practice cells

normalization demo:
45 families
208 practice cells
```

These are demo acceptance counts, not universal product constants.

`RESULT.md` must record:

- actual full-suite test count;
- 11 working-capital families / 47 working-capital practice cells on the applicable five-year demo;
- OWCA / OWCL change series;
- NOWC component bridge reconciliation;
- incremental OWCA / OWCL ratios;
- zero Change in Revenue `#N/A` behavior;
- signed declining-Revenue behavior preserved;
- live classification-conditioned expected values preserved;
- trusted driver-check tamper fails before recoloring;
- no causal working-capital diagnosis or quality score introduced;
- base 41 / 188 and normalization 45 / 208 demo surfaces;
- no forecasting or valuation introduced.

---

## Task 7 — Full verification

Run the focused suite first:

```bash
PYTHONPATH=. pytest core/tests/test_working_capital.py -v
```

Then run the main regression suites:

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_earnings_quality.py -v
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_validators.py -v
```

Then run the complete suite:

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Do not state an expected total test count in advance. Record the actual passing count in `RESULT.md`.

### Base build

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx

PYTHONPATH=. python -m core list \
  --workbook /tmp/DEMO_BASE_Trainer.xlsx
```

Required current-demo result:

```text
188 practice cells
0 correct / 0 incorrect / 188 blank
41 schedule groups
```

### Normalization build

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

Required current-demo result:

```text
208 practice cells
0 correct / 0 incorrect / 208 blank
45 schedule groups
```

### Applicability-gate preservation

Build the existing all-zero OWCA / OWCL fixture and prove:

```text
Working Capital Analysis sheet: absent
working-capital components: absent
```

Do not require 41 / 188 counts for a company where the module is inapplicable.

### CLI

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

---

## Definition of done

Step 9B.2 is complete only when:

1. `WorkingCapitalSeries` separately reports Change in OWCA and Change in OWCL.
2. The independently computed component bridge reconciles to direct Change in NOWC.
3. Incremental OWCA / Change in Revenue and Incremental OWCL / Change in Revenue preserve signed arithmetic.
4. Zero Change in Revenue produces `#N/A`, not numeric zero.
5. Five new comparable-period formula families are registered and checked.
6. The existing six Step 9B.1 families remain unchanged.
7. Working Capital Analysis contains a visible asset/liability driver-decomposition section.
8. The generated decomposition check is trusted and tamper-detected before recoloring.
9. Live classification judgment changes the new dynamic expected values where relevant.
10. No automatic good/bad label, causal line-item diagnosis, or seasonality claim is introduced.
11. All-zero OWCA / OWCL still omits the module entirely.
12. Base demo is 41 families / 188 practice cells.
13. Normalization demo is 45 families / 208 practice cells.
14. Fresh Check is all blank on both generated Trainer workbooks.
15. The full test suite passes.
16. CLI remains `{ingest,build,check,list}`.
17. `TARGET.md` is unchanged.
18. Forecasting and valuation have not begun.

After completing Step 9B.2, stop and report changed files, exact test output, demo build/check/list output, decomposition-reconciliation evidence, live-classification evidence, and any new active historical-model issue found during implementation. Do not proceed to line-item causal diagnosis, forecasting, or valuation, and do not commit or push.
