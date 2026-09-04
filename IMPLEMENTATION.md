# Step 7 — Multi-Period Historical Model Construction

> **For Cursor:** Read `TARGET.md` first. Step 6 is accepted at implementation commit `5b9f1eff72fab1139644b17312b31052ab9fff5e` (`chat 6: Historical-Only Foundation Before Competency Expansion (correction)`). Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, regenerate the demo pair, and stop. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Turn the current latest-period historical exercise set into a coherent **multi-period historical modeling curriculum**. The learner should construct whole historical schedules left-to-right across every applicable fiscal period, including statement links, reformulation, growth/margins, and DuPont, while the normal build remains completely independent of forecasting/valuation.

**Architecture:** Keep `COMPONENT_CATALOG` as the conceptual family catalog, but make the built SemanticMap period-aware. Expand each family into concrete period-specific practice cells at build time. This avoids hard-coding a fixed number of years and preserves semantic identity across companies with different historical depth. The Trainer index and `list` command should present **schedule families**, not pretend that 100+ period cells are 100+ separate concepts; Check still validates every concrete yellow cell.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing semantic map + OOXML cache-preserving Check.

**Spec:** `TARGET.md`, especially `Curriculum progression`, `Historical practice-surface expansion strategy`, and the locked Step 7 roadmap. Step 7 is still **Level 1 — Guided model construction**: source facts and classifications remain supplied. Do not start accounting-judgment exercises, research diagnostics, forecasting, or valuation.

## Current checkpoint review

Accepted Step 6 checkpoint: `5b9f1eff`.

The Step 6 correction now has the intended historical-only boundary:

- public practice catalog contains 21 historical latest-period components;
- normal build does not execute `run_scenario()`;
- normal build requires no forecast assumptions;
- four forecast/valuation tabs are hidden placeholders;
- committed `RESULT.md` reports 90 passing core tests, 21 resolved components, and fresh Check `0/0/21`;
- no GitHub Actions/commit-status checks are configured, so preserve the local verification discipline in this plan.

Static review found no blocker that requires another Step 6 correction. One handoff-quality issue is minor: `RESULT.md` records the full-suite result rather than exact standalone pass counts for `test_reference_integrity.py` and `test_trainer.py`. Step 7 should again record exact standalone counts.

## Learning design for Step 7

Do **not** measure Step 7 as “increase from 21 to N exercises.” The unit of learning is a historical **schedule**.

The learner should construct these 25 conceptual families in dependency order:

```text
 1 revenue_link                  all periods
 2 net_income_link               all periods

 3 effective_tax_rate_fy         all periods
 4 net_interest_fy               all periods
 5 net_interest_after_tax_fy     all periods
 6 nopat_fy                      all periods

 7 owca_agg                      all periods
 8 owcl_agg                      all periods
 9 nowc_agg                      all periods
10 olta_agg                      all periods
11 oltl_agg                      all periods
12 nola_agg                      all periods
13 noa_agg                       all periods
14 financial_assets_agg          all periods
15 financial_liabilities_agg     all periods
16 net_debt                      all periods
17 equity_reformulated_fy        all periods

18 sales_growth                  comparable periods only (second FY onward)
19 nopat_margin                  all periods

20 rnoa                          comparable periods only
21 after_tax_cod                 comparable periods only
22 spread                        comparable periods only
23 flev                          comparable periods only
24 roe_decomp                    comparable periods only
25 actual_roe                    comparable periods only
```

For `n` fiscal periods, the concrete practice-cell count is therefore:

```text
18*n + 7*(n-1) = 25*n - 7
```

`example/DEMO_HK_Standardized.json` has five fiscal years, so its expected Step 7 count is:

```text
25*5 - 7 = 118 practice cells
```

This **118 is a demo integrity check, not the definition of learner progress**.

### Period-specific dependency rules

Current-period dependencies use the same fiscal year. Previous-period dependencies use the immediately preceding fiscal year.

```text
revenue_link:                 none
net_income_link:              none

effective_tax_rate_fy:       none (pretax/tax source links stay populated)
net_interest_fy:              none (interest source links stay populated)
net_interest_after_tax_fy:    current effective_tax_rate_fy + current net_interest_fy
nopat_fy:                     current net_income_link + current net_interest_after_tax_fy

owca_agg:                     none
owcl_agg:                     none
nowc_agg:                     current owca_agg + current owcl_agg
olta_agg:                     none
oltl_agg:                     none
nola_agg:                     current olta_agg + current oltl_agg
noa_agg:                      current nowc_agg + current nola_agg
financial_assets_agg:         none
financial_liabilities_agg:    none
net_debt:                     current financial_assets_agg + current financial_liabilities_agg
equity_reformulated_fy:       current noa_agg + current net_debt

sales_growth:                 current revenue_link + previous revenue_link
nopat_margin:                 current nopat_fy + current revenue_link

rnoa:                         current nopat_fy + current noa_agg + previous noa_agg
after_tax_cod:                current net_interest_after_tax_fy + current net_debt + previous net_debt
spread:                       current rnoa + current after_tax_cod
flev:                         current net_debt + previous net_debt + current equity_reformulated_fy + previous equity_reformulated_fy
roe_decomp:                   current rnoa + current spread + current flev
actual_roe:                   current net_income_link + current equity_reformulated_fy + previous equity_reformulated_fy
```

The first fiscal period has no `sales_growth`, `rnoa`, `after_tax_cod`, `spread`, `flev`, `roe_decomp`, or `actual_roe` practice component because there is no beginning-period denominator/comparison.

Historical share-count / EPS practice remains conditional on **actual supplied historical share data**. The current standardized demo has no dedicated share-history series. Do not invent one, do not reuse forecast `dilutedShares`, and do not add fake EPS exercises merely to expand Step 7.

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve every accepted Step 6 forecast-quarantine regression.
- Normal v1 build must still succeed when `run_scenario()` is monkeypatched to fail.
- Keep all four deferred forecast/valuation tabs hidden and placeholder-only.
- Do not expose any public forecast switch.
- Historical source numbers and classification/setup judgments remain populated.
- Pretax-income, tax-expense, interest-expense, and interest-income link rows remain populated scaffolding in Step 7; only Revenue and Net Income become explicit cross-sheet link practice families.
- `Reported Equity`, `Total Capital`, and `CHECK` rows remain populated non-practice audit guardrails. The learner should use them to audit the schedule rather than reconstruct those guardrails in this step.
- No accounting-classification quizzes, normalization judgments, free-form research grading, forecasting, valuation, Hint, Reveal, or VBA.
- No static workbook coordinates in the catalog.
- No fixed five-year assumption in production code. Five years is only the demo fixture.
- Do not add historical EPS/per-share exercises without actual supplied historical share-count data.
- Preserve source checksum, line-identity, reformulation-integrity, and cache-safe Check behavior.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Expose authoritative historical income-series values

**Files:**
- Modify: `core/model/financial_math.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Produces: an explicit historical series object used by period-specific expected values.
- Preserves: existing latest-period scalar fields on `AnchorMetrics` for backward compatibility and dormant forecast tests.

- [ ] **Step 1: Write a failing historical-series test**

Add a regression that ingests the five-year demo and checks full historical series rather than only latest scalars.

Use this interface:

```python
@dataclass(frozen=True)
class HistoricalSeries:
    revenue: list[float]
    net_income: list[float]
    pretax_income: list[float]
    tax_expense: list[float]
    effective_tax_rate: list[float]
    net_interest: list[float]
    net_interest_after_tax: list[float]
    nopat: list[float]
```

and add:

```python
historical: HistoricalSeries
```

to `AnchorMetrics`.

Test at minimum:

```python
assert len(anchor.historical.revenue) == len(periods)
assert len(anchor.historical.nopat) == len(periods)
assert anchor.historical.revenue[-1] == pytest.approx(anchor.revenue)
assert anchor.historical.net_interest[-1] == pytest.approx(anchor.net_interest)
assert anchor.historical.effective_tax_rate[-1] == pytest.approx(anchor.effective_tax_rate)
assert anchor.historical.net_interest_after_tax[-1] == pytest.approx(anchor.net_interest_after_tax)
assert anchor.historical.nopat[-1] == pytest.approx(anchor.nopat)

for j in range(len(periods)):
    assert anchor.historical.net_interest_after_tax[j] == pytest.approx(
        anchor.historical.net_interest[j] * (1 - anchor.historical.effective_tax_rate[j])
    )
    assert anchor.historical.nopat[j] == pytest.approx(
        anchor.historical.net_income[j] + anchor.historical.net_interest_after_tax[j]
    )
```

Use production `resolve_line()` / `_val()` logic for expected source values; do not hard-code demo row numbers.

- [ ] **Step 2: Run the test and verify it fails before implementation**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "historical_series" -v
```

Expected before implementation: `AnchorMetrics` has no `historical` field.

- [ ] **Step 3: Implement `HistoricalSeries` from the arrays already computed inside `compute_anchor()`**

Do not recompute the formulas in `ReferenceModelBuilder`. Populate `HistoricalSeries` directly from the existing `revenues`, `ni`, `pretax`, `tax`, `etr`, `net_int`, `niat`, and `nopat` arrays.

Keep existing scalar fields populated from the last element so dormant forecast code remains compatible.

- [ ] **Step 4: Run focused and full financial-math/reference tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "historical_series or anchor_exposes_tax" -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -q
```

Record the exact pass count for the full file later in `RESULT.md`.

---

## Task 2 — Add period-aware component families and concrete spec expansion

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/semantic_map.py`
- Modify: `core/engine/map_embed.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- `COMPONENT_CATALOG`: 25 conceptual `ComponentFamily` objects.
- `expand_historical_specs(periods) -> tuple[ComponentSpec, ...]`: concrete period-specific specs.
- Concrete IDs are stable and period-qualified.
- `SemanticMap` validates against builder-supplied concrete specs rather than a global fixed-count catalog.

- [ ] **Step 1: Write failing expansion tests**

Introduce two dataclasses with clear separation between curriculum concept and workbook cell:

```python
@dataclass(frozen=True)
class ComponentFamily:
    id: str
    order: int
    title: str
    short_hint: str
    semantic_key: str
    category: str
    tab_template: str
    period_scope: str = "all"           # "all" | "comparable"
    depends_on_current: tuple[str, ...] = ()
    depends_on_previous: tuple[str, ...] = ()
    hints: tuple[str, ...] = ()
    tolerance: float = 0.01


@dataclass(frozen=True)
class ComponentSpec:
    id: str
    family_id: str
    order: int
    family_order: int
    title: str
    short_hint: str
    semantic_key: str
    category: str
    tab_template: str
    period_index: int | None = None
    period_end: str = ""
    depends_on: tuple[str, ...] = ()
    hints: tuple[str, ...] = ()
    tolerance: float = 0.01
    scenario: str = ""
```

Keep `DEFERRED_COMPONENT_SPECS` as concrete dormant `ComponentSpec` objects with blank/default historical-period metadata.

Use stable concrete IDs:

```python
def concrete_component_id(family_id: str, period: date) -> str:
    return f"{family_id}__{period.strftime('%Y%m%d')}"
```

and concrete semantic keys:

```text
<family semantic key>.<YYYY-MM-DD>
```

Test the five demo periods directly:

```python
specs = expand_historical_specs(periods)
assert len(COMPONENT_CATALOG) == 25
assert [f.order for f in COMPONENT_CATALOG] == list(range(1, 26))
assert len(specs) == 118
assert [s.order for s in specs] == list(range(1, 119))
assert len({s.id for s in specs}) == 118
assert len({s.semantic_key for s in specs}) == 118
```

Also test a three-period synthetic date list:

```python
assert len(expand_historical_specs(periods[:3])) == 68  # 25*3 - 7
```

For every concrete dependency:

```python
by_id = {s.id: s for s in specs}
for spec in specs:
    for dep in spec.depends_on:
        assert dep in by_id
        assert by_id[dep].order < spec.order
```

Assert no comparable family is instantiated at `period_index == 0`.

- [ ] **Step 2: Run the expansion tests and verify failure**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "period_aware or expand_historical" -v
```

Expected before implementation: period-aware family/spec interfaces do not exist.

- [ ] **Step 3: Replace the current 21 latest-period family definitions with the 25-family catalog above**

Preserve the accepted hints/financial definitions from Step 6 where applicable. Add `revenue_link`, `net_income_link`, `sales_growth`, and `nopat_margin`.

Use the exact family dependency rules from the `Learning design for Step 7` section. `expand_historical_specs()` must translate family dependencies into concrete current/previous-period IDs.

Do not put the dormant six forecast/valuation definitions back into `COMPONENT_CATALOG`.

- [ ] **Step 4: Make `SemanticMap` independent of the global static catalog**

Change construction to accept expected concrete specs:

```python
class SemanticMap:
    def __init__(self, expected_specs: tuple[ComponentSpec, ...] = ()) -> None:
        self._expected_specs = tuple(expected_specs)
        ...
```

`validate_complete()` must iterate `self._expected_specs`, not `COMPONENT_CATALOG`.

Extend `ResolvedComponent` and workbook embedding with:

```text
family_id
family_order
period_index
period_end
```

`SemanticMap.from_workbook()` / JSON loading must round-trip those fields. For backward compatibility with an older map lacking them, use sensible defaults (`family_id=id`, `family_order=order`, `period_index=None`, `period_end=""`) rather than crashing.

Update `_ComponentMap` headers in `core/engine/map_embed.py` accordingly.

- [ ] **Step 5: Add a semantic-map round-trip test**

Create/serialize/load a small period-aware map and assert the four new metadata fields survive JSON and embedded-workbook round trips.

- [ ] **Step 6: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "period_aware or expand_historical or semantic" -v
```

---

## Task 3 — Build and register the complete multi-period historical schedules

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- `ReferenceModelBuilder.historical_specs`: concrete specs from `expand_historical_specs(self.periods)`.
- `_register_historical(family_id, period_index, ...)`: resolves the correct concrete spec.
- `_register_deferred(...)`: keeps dormant forecast registration isolated from the active historical spec index.

- [ ] **Step 1: Write a failing five-year build regression**

Build the normal demo pair and assert:

```python
smap = load_semantic_map(answer_key_path)
assert len(smap.all_ordered()) == 118

families = {c.family_id for c in smap.all_ordered()}
assert families == {f.id for f in COMPONENT_CATALOG}

for family in COMPONENT_CATALOG:
    comps = [c for c in smap.all_ordered() if c.family_id == family.id]
    expected = 5 if family.period_scope == "all" else 4
    assert len(comps) == expected
```

For every component, assert the Answer Key cell formula exactly equals `comp.formula` and `expected_value is not None`.

- [ ] **Step 2: Run it and verify current Step 6 fails at 21 components**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "multi_period_practice" -v
```

- [ ] **Step 3: Wire the expanded specs into `ReferenceModelBuilder`**

After resolving `self.periods`:

```python
self.historical_specs = expand_historical_specs(self.periods)
self.semantic_map = SemanticMap(expected_specs=self.historical_specs)
self._historical_spec_index = {
    (s.family_id, s.period_index): s
    for s in self.historical_specs
}
```

Add:

```python
def _register_historical(
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
    spec = self._historical_spec_index[(family_id, period_index)]
    self.semantic_map.register(
        spec, tab, row, col, formula, expected, related_cells=related
    )
```

Keep dormant forecast registration separate:

```python
def _register_deferred(...):
    ...  # resolve only from DEFERRED_COMPONENT_SPECS
```

Update the six legacy forecast registration sites to call `_register_deferred`. Do not let deferred IDs fall through the active historical lookup.

- [ ] **Step 4: Add Revenue to the condensed historical source-link block**

Resolve `revenue` with production line-resolution logic and add a `Revenue` row alongside the existing linked historical rows.

For every fiscal period register:

```text
revenue_link
net_income_link
```

with the exact cross-sheet formulas and authoritative expected values from `anchor.historical`.

Pretax Income, Tax Expense, Interest Expense, and Interest Income rows remain populated non-practice scaffolding in Step 7.

- [ ] **Step 5: Register all 15 reformulation families for every fiscal period**

Replace latest-only registrations with a loop over `j in range(self._n)` for:

```text
effective_tax_rate_fy
net_interest_fy
net_interest_after_tax_fy
nopat_fy
owca_agg
owcl_agg
nowc_agg
olta_agg
oltl_agg
nola_agg
noa_agg
financial_assets_agg
financial_liabilities_agg
net_debt
equity_reformulated_fy
```

Expected values must come from:

```text
anchor.historical.*                         income reformulation
anchor.reformulation.category_totals       classified aggregates
anchor.reformulation.nowc / nola / noa     operating identities
anchor.reformulation.net_debt              net debt
anchor.reformulation.implied_equity        reformulated equity
```

Do not calculate expected values from Excel cell contents.

`Reported Equity`, `Total Capital`, and `CHECK` remain populated and outside the practice map.

- [ ] **Step 6: Rebuild `ALT DuPont` as a true historical schedule**

Use columns `B...` for **all** fiscal periods; do not skip the first date header.

Rows must be:

```text
Sales Growth
NOPAT Margin
RNOA
After-tax CoD
Spread
FLEV
ROE (decomposed)
Actual ROE
```

For every fiscal period:

- `NOPAT Margin` has a formula and active practice component.
- `Sales Growth` is active only from the second fiscal period onward.
- the six DuPont ratio rows are active only from the second fiscal period onward.
- first-period cells for non-applicable comparative metrics should display a clear non-practice marker such as `N/A`; they must not be yellow and must not enter the SemanticMap.

Use robust zero guards where a denominator can be zero, consistent with Python expected-value behavior.

Register `sales_growth`, `nopat_margin`, and all six DuPont families with `anchor.dupont[...]` expected values for the matching period index.

- [ ] **Step 7: Verify formula dependencies, not just counts**

Add tests that inspect a middle and final fiscal period. At minimum assert:

- FY2023 Sales Growth references FY2023 and FY2022 Revenue link cells;
- FY2024 RNOA references FY2024 NOPAT plus FY2024/FY2023 NOA;
- FY2025 After-tax CoD references FY2025 NIAT plus FY2025/FY2024 Net Debt;
- FY2025 FLEV references FY2025/FY2024 Net Debt and Equity;
- FY2025 ROE decomposition references the same-period RNOA, Spread, and FLEV cells;
- FY2025 Actual ROE references FY2025 Net Income and FY2025/FY2024 Equity.

Do not assert fragile absolute coordinates; obtain resolved cells/rows from the SemanticMap and row map.

- [ ] **Step 8: Run full reference integrity tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
```

Record the exact pass count.

---

## Task 4 — Present schedules as schedules in the Trainer index and CLI

**Files:**
- Modify: `core/trainer/workbook.py`
- Modify: `core/__main__.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- SemanticMap remains cell-level for Check.
- Trainer index is family-level: 25 conceptual schedule rows for the five-year demo, not 118 rows.
- `python -m core list` lists the 25 conceptual families.
- `python -m core list --workbook ...` lists 25 resolved schedule groups with their actual cell ranges/counts.

- [ ] **Step 1: Write a failing grouped-index test**

Open a built Trainer and assert the Trainer index contains one row per conceptual family, ordered 1–25.

Use these columns:

```text
Order
Schedule
Period scope
Tab
Practice cells
Depends on
```

For the demo, assert:

```python
assert index_family_rows == 25
```

and check examples:

```text
Revenue historical source link     5 cells
NOPAT                               5 cells
Sales Growth                        4 cells
RNOA                                4 cells
```

- [ ] **Step 2: Implement a small grouping helper**

Group `ResolvedComponent`s by `family_id`, sort groups by `family_order`, and sort each group's cells by `period_index`.

Render `Practice cells` as a compact horizontal range when cells are on one row and contiguous; otherwise use a comma-separated list. Do not assume fixed row numbers.

`Period scope` should communicate the actual built coverage, for example:

```text
2021–2025 (5 cells)
2022–2025 (4 cells)
```

Use `period_end` metadata; do not parse years from cell coordinates.

`Depends on` should show **family IDs**, not the full period-qualified concrete dependency IDs.

Update the Trainer instruction to make the learning model explicit:

```text
Complete each historical schedule left-to-right in dependency order.
Each schedule is one modeling concept repeated across fiscal periods.
Run Check to validate every yellow cell in the workbook.
```

- [ ] **Step 3: Update CLI list behavior**

Without `--workbook`, list the 25 family definitions and show their scope:

```text
[all periods]
[second period onward]
```

With `--workbook`, group the resolved SemanticMap by `family_id` and print one line per family with actual tab, cell range, and concrete cell count.

Do not add a new `--expanded` mode in this step; YAGNI.

- [ ] **Step 4: Run Trainer/CLI focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "index or list or family or schedule" -v
PYTHONPATH=. python -m core list
```

Expected default list: 25 conceptual historical families only; no forecast/valuation families.

---

## Task 5 — Preserve short-feedback-loop Check behavior across the full multi-period surface

**Files:**
- Modify: `core/tests/test_trainer.py`
- Modify: `core/trainer/checker.py` only if a demonstrated regression requires it

**Interfaces:**
- Five-year demo fresh Check total: 118.
- Existing exact-formula, equivalent-cached-formula, color refresh, and non-disclosure contracts remain unchanged.

- [ ] **Step 1: Update fresh-workbook assertions**

For the five-year demo:

```python
assert len(smap.all_ordered()) == 118
```

Fresh Check must report:

```text
Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.
```

Trainer audit:

```text
118 blank yellow practice cells
0 Notes/comments on those practice cells
```

Answer Key audit:

```text
118 formula-bearing yellow practice cells
118 non-empty legacy Notes
```

- [ ] **Step 2: Add a multi-period correction-cycle test**

Use the SemanticMap rather than hard-coded coordinates.

Fill all five `nopat_fy` components with their exact Answer Key formulas. Put a wrong formula into one `sales_growth` component. Leave the rest blank.

Assert:

```python
summary.total == 118
summary.correct == 5
summary.incorrect == 1
summary.blank == 112
```

Then replace the wrong Sales Growth formula with its correct formula and rerun Check:

```python
summary.correct == 6
summary.incorrect == 0
summary.blank == 112
```

Then clear one NOPAT cell and rerun:

```python
summary.correct == 5
summary.incorrect == 0
summary.blank == 113
```

Verify green/red/yellow fills at each stage.

- [ ] **Step 3: Preserve cache-safe equivalent-formula behavior**

Do not weaken or delete the existing OOXML cached-value regression. It must still pass with the larger SemanticMap.

- [ ] **Step 4: Re-run Step 6 quarantine/leakage tests**

At minimum rerun regressions proving:

- patched `run_scenario()` is never executed by normal build;
- deferred tabs are four hidden placeholders in Trainer and Answer Key;
- no active component points to a deferred tab;
- Trainer contains no `_ComponentMap`, `_Ref*`, answer-bearing sidecar, formulas, expected values, or Notes for active practice;
- source values/classifications remain populated and pair-identical.

- [ ] **Step 5: Run the full Trainer test file**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Record the exact pass count.

---

## Task 6 — Align docs, regenerate demos, and verify Step 7 end-to-end

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

**Interfaces:**
- Current v1 description becomes “multi-period historical model-construction foundation.”
- Step 8 accounting judgment remains explicitly deferred.

- [ ] **Step 1: Update documentation without overclaiming**

Docs should say:

```text
current Step 7 capability:
- historical schedules across all supplied fiscal years
- cross-sheet Revenue / Net Income links
- reformulation across periods
- Sales Growth / NOPAT Margin
- multi-period DuPont from the second comparable year onward
- workbook-wide Check across every concrete period cell

learner view:
- 25 conceptual schedule families
- period-specific yellow cells inside each schedule

still deferred:
- classification/normalization judgment exercises
- earnings-quality diagnostics
- forecasting
- valuation
- investment conclusion
```

Do not describe 118 as 118 separate skills. Explain that it is 25 concepts instantiated across five demo fiscal years.

- [ ] **Step 2: Regenerate the committed demo pair**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o example/DEMO_HK_Trainer.xlsx
```

Expected:

```text
Components resolved: 118
```

- [ ] **Step 3: Run the full verification suite**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_identity.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/ -q
PYTHONPATH=. python -m core build example/DEMO_HK_Standardized.json -o /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core list
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx
PYTHONPATH=. python -m core --help
```

Expected build/check/list outcomes:

```text
Components resolved: 118
Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.
python -m core list -> 25 conceptual historical families
python -m core list --workbook ... -> 25 resolved schedule groups / 118 concrete cells total
python -m core --help -> {ingest,build,check,list} only
```

- [ ] **Step 4: Perform final workbook audit**

Verify with openpyxl/tests:

1. SemanticMap has 118 concrete components for the five-year demo.
2. Those components group into exactly 25 family IDs.
3. 18 all-period families each have 5 cells.
4. 7 comparable families each have 4 cells.
5. Trainer index has 25 schedule rows, not 118 conceptual rows.
6. Trainer has 118 blank/yellow/no-Note practice cells.
7. Answer Key has 118 formula/yellow/non-empty-Note practice cells.
8. Revenue and Net Income links are practice across all five years.
9. historical source statements and classifications remain populated.
10. `Reported Equity`, `Total Capital`, and `CHECK` remain populated audit guardrails.
11. first-year comparative DuPont/growth cells are non-practice `N/A` markers.
12. all four deferred forecast/valuation tabs remain hidden and placeholder-only.
13. no active formula references a deferred tab.
14. normal build still succeeds if `run_scenario()` raises.
15. no Trainer answer leakage or Trainer answer-bearing sidecars.
16. generated Answer-Key metadata remains ignored according to `.gitignore`.

- [ ] **Step 5: Update `RESULT.md` with exact evidence**

Use this structure with actual observed numbers:

```text
Status: Step 7 complete

Implementation base:
- 5b9f1eff Step 6 correction

Historical schedule model:
- fiscal periods in demo: 5
- conceptual families: 25
- all-period families: 18
- comparable-period families: 7
- concrete practice cells: 118
- Trainer index rows: 25

Practice audit:
- Trainer blank/yellow/no Note: 118/118
- Answer Key formula/yellow/Note: 118/118
- fresh Check: 0 correct / 0 incorrect / 118 blank

Preservation:
- source values populated: yes
- classifications/setup judgments populated: yes
- reported-equity/check guardrails populated: yes
- forecast engine called by normal build: no
- deferred tabs: four hidden placeholders
- Trainer answer leakage: none
- repeated cached Check: preserved

Tests:
- record every command above and exact pass count/result, including standalone reference-integrity and trainer test-file counts

Unresolved:
- none OR list exact blockers
```

- [ ] **Step 6: Stop**

Do not begin Step 8. Do not add accounting-judgment exercises. Do not commit or push.

## Step 7 acceptance criteria

Step 7 is accepted only when all are true:

1. component architecture expands dynamically from conceptual families to period-specific concrete specs without fixed-year coordinates;
2. five-year demo resolves exactly 118 concrete practice cells grouped into 25 conceptual schedule families;
3. two-, three-, and five-period expansion logic follows `25*n - 7` where applicable and does not assume five years in production code;
4. Revenue and Net Income cross-sheet links are practiced across every supplied fiscal period;
5. the 15 historical reformulation families are practiced across every supplied fiscal period;
6. Sales Growth is practiced from the second period onward and NOPAT Margin across all periods;
7. all six DuPont families are calculated and practiced for every comparable period, not only the latest year;
8. period-specific dependencies correctly reference current and previous periods as defined above;
9. first-period non-comparable cells are clear non-practice markers;
10. Trainer index and CLI present schedules as 25 concepts rather than 118 unrelated tasks;
11. workbook-wide Check correctly validates all 118 demo cells and preserves repeated/cached behavior;
12. normal historical build remains forecast-independent and the four deferred tabs remain hidden placeholders;
13. source facts/classifications and audit guardrails remain populated;
14. no historical shares/EPS are fabricated from forecast assumptions;
15. full test suite and regenerated demo pair pass the required audits;
16. docs continue to frame Step 7 as a guided historical foundation, not job-readiness or independent accounting judgment.

---

# Locked Post-Step-7 Roadmap — Do Not Implement Yet

## Step 8 — Guided accounting judgment and normalization

Next, introduce selected accounting-treatment decisions while retaining a short feedback loop: operating versus financing classification, recurring versus non-recurring treatment, normalization, leases, stock-based compensation, goodwill/intangibles, deferred taxes, minority interests, acquisitions, and other topics only where material to the supplied company.

The design goal will be to teach **why treatment changes economic interpretation**, not to turn ambiguous accounting into arbitrary multiple-choice trivia.

## Step 9 — Historical research diagnostics

Teach the learner to explain what changed and why: margin versus turnover/capital-intensity drivers of RNOA, working-capital behavior, accrual/cash conversion, operating versus financing sources of ROE change, dilution, segment economics, and earnings-quality/accounting consistency signals.

## Step 10 — Cross-company robustness

Validate the historical/judgment/diagnostic system on materially different non-financial companies, including at least one asset-light and one asset-heavy or working-capital-intensive business.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit, traceable BAVGEM-style analyst assumptions and business drivers. Do not restore canned default vectors as company-specific forecasts.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, appropriate cross-checks, sensitivities, and a concise evidence-based investment conclusion only after the forecast layer is separately trusted.
