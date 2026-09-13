# Step 9K.1 — PP&E / D&A Asset-Intensity Diagnostics

**Status: COMPLETE** — Fixed-asset intensity on ALT DuPont (orders 79–86); surfaces 70/294, 74/314, 78/328, 86/366; cross-company unchanged; no capex; GOOGL/TARGET hashes unchanged. See `RESULT.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first, then `docs/GOOGL_HISTORICAL_REFERENCE.md`, then this plan in full. The accepted implementation base is commit `8b5df8b9a97962111693bd906fc6a32171fec61f` (`step 9j1`, Step 9J.1 complete). Implement only Step 9K.1 below using red/green TDD. This remains **Step 9 historical convergence**. Do not begin forecasting, valuation, scenarios, or forward-model activation. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Add the first historical fixed-asset diagnostic layer supported by the current Trainer data: link PP&E and combined depreciation-and-amortisation source facts into the existing ALT DuPont sheet, then teach average PP&E, PP&E turnover/intensity, PP&E change, and D&A intensity without inventing capex or pretending combined D&A is a pure PP&E depreciation rate.

**Architecture:** Add a focused `FixedAssetSeries` driven only by explicitly supplied PP&E and D&A lines plus existing Revenue. Gate the module on **both** PP&E and D&A being resolvable and period-complete. Add eight semantic families, orders `79..86`, appended to the existing ALT DuPont sheet after ROE attribution so the workbook becomes more integrated rather than adding another user-facing worksheet. Dynamic Check recomputes the same values from the trusted source statements. Capex is deliberately excluded from this checkpoint because the canonical Trainer supplies no explicit capex line and the repository has no explicit capex sign/source contract yet.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `LineItem` / `StandardizedFinancials`, `resolve_line`, `required_period_value`, `ratio_or_na`, `ReferenceModelBuilder`, component catalogs, `historical_expected`, `check_workbook`, semantic map, trusted-workbook validation, and the current canonical demo.

**Spec:** `TARGET.md` sections `Historical accounting competence to cover`, `Interpretation is part of the product`, `Reference workbook for historical convergence`, and `Step 9 roadmap before forecasting`; plus the Priority A queue in `docs/GOOGL_HISTORICAL_REFERENCE.md`.

## Review of Step 9J.1

Step 9J.1 is accepted as the implementation base:

- the GOOGL workbook was audited read-only;
- the GOOGL and canonical Answer-Key hashes were unchanged;
- no active formula family / worksheet / practice count changed;
- the full suite was recorded at `294 passed`;
- the gap matrix identified fixed-asset analysis as the next Priority A historical module;
- forecasting / valuation remained deferred.

One scope refinement is required before implementation: the canonical demo has `Property, plant and equipment` and `Depreciation and amortisation`, but **does not contain an explicit capex / purchases-of-PP&E line**. Therefore Step 9K.1 must not infer capex from `Net cash used in investing activities`, must not use `ABS()` to manufacture a capex amount, and must not call combined D&A a pure PP&E depreciation rate. A later Step 9 checkpoint can add a capex reinvestment bridge only after an explicit source/sign contract exists.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- `example/GOOGL_Demo_Integrated_Financials.xlsx` remains read-only and must not be regenerated.
- Remain in Step 9. Forecasting, valuation, scenarios, guidance/consensus, multiples, and investment conclusions remain deferred.
- Add no new user-facing worksheet. Put the new section on `ALT DuPont` after the existing ROE attribution block.
- Preserve Step 9I.1 presentation: Aptos Narrow 11, white/yellow only in a fresh workbook, no decorative borders; Check green/red remains functional feedback only.
- Preserve Trainer / Answer Key / Check separation and all trusted-cell rules.
- Preserve non-financial-company scope.
- Preserve source signs. No `ABS()` or `IFERROR(...,0)` in practice formulas.
- Missing optional module inputs omit the module; a resolved required line with a missing modeled-period value fails closed through `MissingHistoricalValueError`.
- Do not add capex aliases, capex formulas, capex ratios, or a capex input field in this checkpoint.
- Do not infer PP&E or D&A from totals or category aggregates. Resolve the explicit source lines.
- Do not automatically label a company “capital intensive”, “underinvesting”, “overinvesting”, or “high quality”. These are mechanical historical diagnostics only.
- Combined D&A may include intangible amortisation. The workbook and Notes must call it `D&A`, not `Depreciation Rate`.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

### Task 1: Extend canonical line resolution for PP&E and D&A

**Files:**
- Modify: `core/model/line_resolver.py`
- Modify: `core/tests/test_line_resolver.py`

**Interfaces:**
- Adds canonical concepts:
  - `property_plant_equipment`
  - `depreciation_amortization`
- Produces the same `ResolvedLine` contract used by all existing historical modules.

- [ ] **Step 1: Add failing resolver tests**

Add tests covering all of the following:

```python
ppe = resolve_line(
    [_item("Property, plant and equipment", 100, 110)],
    "property_plant_equipment",
    required=True,
)
assert ppe.item is not None
assert ppe.item.label == "Property, plant and equipment"

ppe_concept = resolve_line(
    [_item("Fixed assets", 100, 110, concept="property_plant_equipment")],
    "property_plant_equipment",
    required=True,
)
assert ppe_concept.item is not None
assert ppe_concept.item.label == "Fixed assets"

da = resolve_line(
    [_item("Depreciation and amortisation", 10, 11)],
    "depreciation_amortization",
    required=True,
)
assert da.item is not None
```

Also require:

- US spelling `Depreciation and amortization` resolves;
- explicit `LineItem.concept` outranks a label alias;
- two exact aliases at the same priority raise `AmbiguousLineError`;
- an unrelated `Net cash used in investing activities` line does **not** resolve as either new concept.

- [ ] **Step 2: Run resolver tests red**

```bash
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

Expected before implementation: fail because the two concepts are unknown.

- [ ] **Step 3: Add narrow aliases only**

Extend `_EXACT_ALIASES` with normalized exact aliases:

```python
"property_plant_equipment": frozenset({
    "property plant and equipment",
    "property and equipment",
    "net property plant and equipment",
}),
"depreciation_amortization": frozenset({
    "depreciation and amortisation",
    "depreciation and amortization",
}),
```

Do not add broad substring matching such as generic `property`, `equipment`, `depreciation`, or `amortization` patterns. Do not add a capex concept in this task.

- [ ] **Step 4: Run resolver tests green**

```bash
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

---

### Task 2: Add the fixed-asset model with strict availability and `#N/A` semantics

**Files:**
- Create: `core/model/fixed_asset.py`
- Create: `core/tests/test_fixed_asset.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class FixedAssetAvailability:
    ppe: bool
    depreciation_amortization: bool

@dataclass(frozen=True)
class FixedAssetSeries:
    ppe: tuple[float, ...]
    depreciation_amortization: tuple[float, ...]
    average_ppe: tuple[float | None, ...]
    ppe_turnover: tuple[float | str | None, ...]
    ppe_intensity: tuple[float | str | None, ...]
    ppe_change: tuple[float | None, ...]
    da_to_revenue: tuple[float | str, ...]
    da_to_average_ppe: tuple[float | str | None, ...]


def fixed_asset_availability(
    financials: StandardizedFinancials,
) -> FixedAssetAvailability:
    ...


def fixed_asset_applicable(financials: StandardizedFinancials) -> bool:
    ...


def compute_fixed_asset_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> FixedAssetSeries:
    ...
```

The module is applicable only when **both** PP&E and D&A resolve. A company with PP&E but no D&A, or D&A but no PP&E, keeps the module absent.

- [ ] **Step 1: Write failing model tests**

Use the canonical demo plus small synthetic fixtures. Require:

```text
canonical demo applicable: yes
PP&E-only fixture applicable: no
D&A-only fixture applicable: no
```

For the canonical demo, FY2022 must satisfy:

```python
average_ppe[1] == pytest.approx((3200.0 + 3400.0) / 2.0)
ppe_turnover[1] == pytest.approx(9200.0 / 3300.0)
ppe_intensity[1] == pytest.approx(3300.0 / 9200.0)
ppe_change[1] == pytest.approx(200.0)
da_to_revenue[1] == pytest.approx(368.0 / 9200.0)
da_to_average_ppe[1] == pytest.approx(368.0 / 3300.0)
```

First-period expectations:

```python
average_ppe[0] is None
ppe_turnover[0] is None
ppe_intensity[0] is None
ppe_change[0] is None
da_to_average_ppe[0] is None
```

`ppe[0]`, `depreciation_amortization[0]`, and `da_to_revenue[0]` remain defined.

Add denominator tests:

- zero Revenue -> `ppe_intensity` / `da_to_revenue` become `#N/A`;
- zero Average PP&E -> `ppe_turnover` / `da_to_average_ppe` become `#N/A`;
- numeric zero D&A with valid denominators remains numeric zero;
- no sign normalization: negative supplied D&A remains negative in D&A ratios.

Add completeness tests: once PP&E or D&A resolves, a missing modeled-period value must raise `MissingHistoricalValueError`.

- [ ] **Step 2: Run the model tests red**

```bash
PYTHONPATH=. pytest core/tests/test_fixed_asset.py -v
```

- [ ] **Step 3: Implement the model**

Use `resolve_line()` and `required_period_value()` for both source lines. Use `anchor.historical.revenue` for Revenue and require its length to equal `len(periods)`.

For `j >= 1`:

```python
average = (ppe[j - 1] + ppe[j]) / 2.0
ppe_turnover = ratio_or_na(revenue[j], average)
ppe_intensity = ratio_or_na(average, revenue[j])
ppe_change = ppe[j] - ppe[j - 1]
da_to_average_ppe = ratio_or_na(da[j], average)
```

For every period:

```python
da_to_revenue = ratio_or_na(da[j], revenue[j])
```

Do not compute capex, net investment, or a PP&E roll-forward residual.

- [ ] **Step 4: Run model tests green**

```bash
PYTHONPATH=. pytest core/tests/test_fixed_asset.py -v
```

---

### Task 3: Add eight semantic families, orders 79–86

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_fixed_asset.py`
- Test: `core/tests/test_historical_v1_exit_gate.py`

**Interfaces:**
- Adds `FIXED_ASSET_COMPONENT_CATALOG`.
- Adds `expand_fixed_asset_specs(periods, *, start_order)`.
- Adds `fixed_asset_expected_series(fixed_asset)`.

Add exactly these families:

| Order | Family id | Title | Scope |
|---:|---|---|---|
| 79 | `ppe_source_link` | Property, Plant & Equipment | all |
| 80 | `da_source_link` | Depreciation & Amortisation | all |
| 81 | `average_ppe` | Average PP&E | comparable |
| 82 | `ppe_turnover` | PP&E Turnover | comparable |
| 83 | `ppe_intensity` | PP&E Intensity | comparable |
| 84 | `ppe_change` | Change in PP&E | comparable |
| 85 | `da_to_revenue` | D&A / Revenue | all |
| 86 | `da_to_average_ppe` | D&A / Average PP&E | comparable |

Dependencies:

```text
average_ppe -> current + previous ppe_source_link
ppe_turnover -> revenue_link + average_ppe
ppe_intensity -> revenue_link + average_ppe
ppe_change -> current + previous ppe_source_link
da_to_revenue -> da_source_link + revenue_link
da_to_average_ppe -> da_source_link + average_ppe
```

Hints must state:

- PP&E Turnover = Revenue / Average PP&E;
- PP&E Intensity = Average PP&E / Revenue;
- D&A / Average PP&E is a context ratio, **not automatically a pure PP&E depreciation rate**, because the supplied D&A line may include intangible amortisation;
- no ratio implies a good/bad investment conclusion by itself.

- [ ] **Step 1: Write catalog-expansion tests**

For five periods require:

```text
8 families
35 concrete practice cells
5 + 5 + 4 + 4 + 4 + 4 + 5 + 4 = 35
family orders exactly 79..86
```

Also require duplicate and non-chronological periods to fail in the same style as existing expanders.

- [ ] **Step 2: Implement catalog + expected routing**

Add `_FIXED_ASSET_FAMILY_SERIES` in `historical_expected.py` and map all eight fields exactly. `fixed_asset_expected_series()` must validate catalog equality the same way as the existing quality / WC / per-share helpers.

Extend `expected_value_for_component()` with:

```python
fixed_asset: FixedAssetSeries | None = None
```

Route fixed-asset families before falling back to `historical_expected_series()`. Requesting a fixed-asset family without `fixed_asset` must raise a clear `ValueError`.

- [ ] **Step 3: Update the active-family namespace test**

Add `FIXED_ASSET_COMPONENT_CATALOG` to the Step 9H exit-gate `ACTIVE_CATALOGS` tuple and change the frozen namespace assertion from:

```text
1..78
```

to:

```text
1..86
```

Do not renumber any existing family.

- [ ] **Step 4: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_fixed_asset.py -v
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -v
```

---

### Task 4: Integrate the diagnostics into ALT DuPont without a new sheet

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_fixed_asset.py`
- Test: `core/tests/test_trainer.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- `ReferenceModelBuilder.fixed_asset_series: FixedAssetSeries | None`
- `ReferenceModelBuilder.fixed_asset_specs: tuple[ComponentSpec, ...]`
- No new worksheet constant.

- [ ] **Step 1: Gate the module in `ReferenceModelBuilder.__init__`**

After the existing Step 9F specs are constructed, compute:

```python
if fixed_asset_applicable(self.fin):
    self.fixed_asset_series = compute_fixed_asset_series(
        self.fin,
        self.periods,
        self.anchor,
    )
    self.fixed_asset_specs = expand_fixed_asset_specs(
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
            + len(self.normalized_per_share_specs)
            + 1
        ),
    )
else:
    self.fixed_asset_series = None
    self.fixed_asset_specs = ()
```

Append `fixed_asset_specs` last in `expected_specs`. Add `_fixed_asset_spec_index` and `_register_fixed_asset()` following the existing catalog-specific registration pattern.

- [ ] **Step 2: Append one integrated section to `ALT DuPont`**

At the end of the current ROE attribution block, append:

```text
FIXED-ASSET INTENSITY CONTEXT
Property, Plant & Equipment
Depreciation & Amortisation
Average PP&E
PP&E Turnover
PP&E Intensity
Change in PP&E
D&A / Revenue
D&A / Average PP&E
FIXED-ASSET INTENSITY CHECK
```

Do not create a `Fixed Asset Analysis` sheet.

Resolve source rows with the canonical resolver and `workbook_row_for()`:

```python
ppe_resolved = resolve_line(
    self.fin.balance_sheet,
    "property_plant_equipment",
    required=True,
)
da_resolved = resolve_line(
    self.fin.cash_flow,
    "depreciation_amortization",
    required=True,
)
```

Source-link formulas must point to the actual `Balance Sheet` and `Cash Flow Statement` rows for the same fiscal period.

For the first period:

- register PP&E source link;
- register D&A source link;
- register D&A / Revenue;
- write literal `N/A` for Average PP&E, PP&E Turnover, PP&E Intensity, Change in PP&E, D&A / Average PP&E, and the generated check;
- do not register those comparable-only cells.

For `j >= 1` use formulas equivalent to:

```text
Average PP&E = (Prior PP&E + Current PP&E) / 2
PP&E Turnover = Revenue / Average PP&E
PP&E Intensity = Average PP&E / Revenue
Change in PP&E = Current PP&E - Prior PP&E
D&A / Revenue = D&A / Revenue
D&A / Average PP&E = D&A / Average PP&E
```

Denominator formulas must return `NA()` when the denominator is zero. Do not use `IFERROR` or `ABS` in practice formulas.

- [ ] **Step 3: Add one generated trusted identity check**

For comparable periods add a non-practice row:

```text
PP&E Turnover × PP&E Intensity = 1
```

If either input is `#N/A`, display `N/A`; otherwise `OK` when the product is within `1e-7` of `1`, else `CHECK`.

This row is trusted, not a practice family. Reuse the existing generic ALT DuPont trusted-sheet boundary; do **not** add a new trusted-sheet special case.

- [ ] **Step 4: Add rowmap keys**

Add:

```text
dupont_ppe_source_row
dupont_da_source_row
dupont_average_ppe_row
dupont_ppe_turnover_row
dupont_ppe_intensity_row
dupont_ppe_change_row
dupont_da_to_revenue_row
dupont_da_to_average_ppe_row
dupont_fixed_asset_check_row
```

- [ ] **Step 5: Add the catalog to Trainer family metadata**

Import `FIXED_ASSET_COMPONENT_CATALOG` in `core/trainer/workbook.py` and merge it into `family_meta` so the Trainer index gets the correct titles, dependencies, family orders, and Notes.

Do not add styling exceptions. Step 9I.1 minimal styling owns presentation.

- [ ] **Step 6: Add integration tests**

On the canonical demo with no normalization assumptions require:

```text
70 families / 294 practice cells
fixed-asset families = 8
fixed-asset cells = 35
ALT DuPont contains the fixed-asset section
fresh Check = 0 correct / 0 incorrect / 294 blank
```

On a synthetic PP&E-only company require the module to be absent and no fixed-asset family ids in the semantic map.

Tamper the generated fixed-asset check row and require trusted validation to fail before recolor.

- [ ] **Step 7: Run integration tests**

```bash
PYTHONPATH=. pytest core/tests/test_fixed_asset.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
```

---

### Task 5: Make Formula Check recompute fixed-asset expecteds from trusted source facts

**Files:**
- Modify: `core/trainer/checker.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_fixed_asset.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Check uses the same `FixedAssetSeries` definition as the reference builder.
- No new Check mode or public CLI option.

- [ ] **Step 1: Add fixed-asset family detection**

Include `{family.id for family in FIXED_ASSET_COMPONENT_CATALOG}` in the checker’s family routing.

After Check reconstructs `financials`, `periods`, and the current `anchor`, compute:

```python
fixed_asset = (
    compute_fixed_asset_series(financials, periods, anchor)
    if fixed_asset_applicable(financials)
    else None
)
```

Pass `fixed_asset=fixed_asset` into `expected_value_for_component()`.

Do not compute any capex series.

- [ ] **Step 2: Add Check acceptance tests**

For one fixed-asset numeric family:

1. exact Answer-Key formula -> green;
2. numerically equivalent formula with matching cached value -> green;
3. fabricated wrong numeric result -> red;
4. zero-denominator fixture producing `#N/A`: exact formula and equivalent `=NA()` -> green; fabricated `0` -> red.

Also verify a source-statement tamper is rejected by trusted validation before recolor.

- [ ] **Step 3: Run checker regressions**

```bash
PYTHONPATH=. pytest core/tests/test_fixed_asset.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

---

### Task 6: Update canonical counts, documentation, and committed workbooks

**Files:**
- Modify: `core/tests/test_historical_v1_exit_gate.py`
- Modify: `core/tests/test_cross_company_robustness.py`
- Modify affected exact-count assertions in `core/tests/test_trainer.py`, `core/tests/test_per_share.py`, `core/tests/test_per_share_attribution.py`, `core/tests/test_normalized_per_share.py`
- Modify: `docs/GOOGL_HISTORICAL_REFERENCE.md`
- Modify: `README.md`
- Modify: `README-HK-TRAINER.md` only where current feature/count statements require it
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Do not modify: `example/DEMO_HK_Standardized.json`
- Do not modify: `example/DEMO_HK_Assumptions.json`
- Do not modify: `TARGET.md`
- Do not modify: `example/GOOGL_Demo_Integrated_Financials.xlsx`

- [ ] **Step 1: Update only the surfaces that actually gain the module**

Because the canonical demo contains both PP&E and D&A, update exact expectations to:

```text
base demo:                    70 families / 294 cells
normalization demo:           74 / 314
shares only:                  78 / 328
shares + normalization:       86 / 366
canonical committed demo:     74 / 314
active family namespace:      1..86
```

The three Step 9G synthetic robustness fixtures contain PP&E but no D&A and therefore remain unchanged:

```text
services:      59 / 248
retail:        78 / 331
manufacturer:  70 / 293
```

Do not mechanically replace every occurrence of `70`, `78`, `293`, or `331`; distinguish canonical/share-derived fixtures from the unchanged cross-company fixtures.

- [ ] **Step 2: Update the GOOGL gap document precisely**

In `docs/GOOGL_HISTORICAL_REFERENCE.md`, split the current combined fixed-asset row conceptually:

```text
PP&E / D&A / asset intensity -> implemented-differently after Step 9K.1
capex / reinvestment bridge -> still missing-needs-new-explicit-data
```

State explicitly that capex remains deferred until an explicit capex source/sign convention is defined. Do not claim Step 9K.1 implemented capex.

- [ ] **Step 3: Keep root README practical**

Add one concise item under `What works now` for:

```text
PP&E / D&A fixed-asset intensity diagnostics when both source lines are supplied
```

Do not add formulas, family counts, the gap matrix, or a technical design essay to root `README.md`.

- [ ] **Step 4: Regenerate canonical workbooks through the public build path**

```bash
python -m core build example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx
```

Do not manually edit the `.xlsx` files.

- [ ] **Step 5: Verify committed canonical pair**

Require:

```text
74 families
314 practice cells
fresh Trainer Check = 0 / 0 / 314 blank
fresh visible style remains Aptos Narrow 11, white/yellow, no borders
Trainer has no answer-bearing sidecars
```

- [ ] **Step 6: Update `RESULT.md`**

Record at minimum:

```text
Step 9K.1 complete — PP&E / D&A asset-intensity diagnostics
8 new families / 35 cells on five-year applicable data
active family namespace 1..86
canonical base/norm/share surfaces
cross-company surfaces unchanged because D&A absent
capex not implemented
GOOGL workbook unchanged
TARGET.md unchanged
full pytest count
forecasting / valuation deferred
```

---

### Task 7: Final verification

**Files:**
- Modify `IMPLEMENTATION.md` status only after every check is green.

- [ ] **Step 1: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_fixed_asset.py -v
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_cross_company_robustness.py -v
PYTHONPATH=. pytest core/tests/test_per_share.py -v
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
PYTHONPATH=. pytest core/tests/test_learner_ready_presentation.py -v
PYTHONPATH=. pytest core/tests/test_reference_workbook_audit.py -v
```

- [ ] **Step 2: Run the full suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count only. Do not prestate it.

- [ ] **Step 3: Verify public CLI**

Require exactly:

```text
ingest
build
check
list
```

No `forecast`, `value`, `hint`, or `reveal` command.

- [ ] **Step 4: Verify GOOGL and TARGET integrity**

Record before/after SHA-256 for:

```text
TARGET.md
example/GOOGL_Demo_Integrated_Financials.xlsx
```

Both must be unchanged.

- [ ] **Step 5: Verify no capex inference slipped in**

Search the new production changes and require no logic that derives capex from:

```text
Net cash used in investing activities
absolute value of investing cash flow
PP&E change + D&A
```

Step 9K.1 ends at PP&E / D&A historical context. A future checkpoint must define an explicit capex source contract before adding reinvestment formulas.

- [ ] **Step 6: Mark complete and stop**

Add a concise status line at the top of `IMPLEMENTATION.md` only after all verification passes. Do not prepare or implement forecasting in this checkpoint.

---

## Definition of Done

Step 9K.1 is complete only when:

1. PP&E and D&A resolve canonically and ambiguities fail closed.
2. The module appears only when both source lines are supplied and period-complete.
3. Eight new families occupy orders `79..86` without renumbering existing families.
4. Five-year applicable data produces exactly `35` new practice cells.
5. The new section is integrated into `ALT DuPont`; no extra user-facing worksheet is created.
6. PP&E Turnover and PP&E Intensity use Average PP&E and are exact inverses when defined.
7. D&A / Average PP&E is described as context only, not a pure PP&E depreciation rate.
8. Zero denominators yield `#N/A`, not fabricated zero.
9. Source signs are preserved; practice formulas use no `ABS()` or `IFERROR(...,0)`.
10. Dynamic Check validates all new families and trusted-cell tamper protection still runs before recolor.
11. Canonical surfaces become `70/294`, `74/314`, `78/328`, and `86/366` as specified.
12. Step 9G cross-company surfaces remain unchanged because their fixtures do not supply D&A.
13. The canonical demo pair is regenerated from source and remains learner-ready under the Step 9I.1 style contract.
14. Capex / reinvestment is **not** implemented or inferred.
15. GOOGL reference workbook and `TARGET.md` remain unchanged.
16. Forecasting / valuation remain dormant and deferred.
17. Full tests pass and the actual count is recorded.
18. Cursor performs no Git commit/push operations.
