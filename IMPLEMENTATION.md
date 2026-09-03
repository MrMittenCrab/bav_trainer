# Step 6 — Historical-Only v1: Hide Forecasting and Complete the Historical Formula Core

> **For Cursor:** Read `TARGET.md` first. Step 5 is accepted at implementation commit `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`). The previous Step 6 plan is superseded by the historical-only v1 decision. Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Make the generated v1 Trainer / Answer Key a trustworthy **historical-analysis product**. Hide forecast/valuation tabs and remove them from the active practice/check surface, while expanding the historical reformulation + DuPont formula chain to a coherent 21-cell core.

**Architecture:** Keep the existing historical reference-model construction, formula-only `ComponentSpec` / `SemanticMap`, sanitized Trainer, Answer Key Notes, and cache-safe workbook-wide Check. Forecast/valuation code may remain in `ReferenceModelBuilder` as dormant scaffolding, but v1 must not register those formulas as practice components or expose their sheets as normal workbook tabs. Do not redesign forecasting in this step.

**Tech Stack:** Python, pytest, openpyxl, existing OOXML cache-preserving Check fill patch.

**Spec:** `TARGET.md` as updated in planning commit `ae7591b` (`Define historical-only v1 product boundary`).

---

## Current checkpoint and product decision

Latest accepted implementation commit: `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`).

Step 5 already provides:

- matched Trainer / Answer Key workbooks;
- blank yellow formula-practice cells in Trainer;
- formula + legacy Note in Answer Key;
- workbook-wide Check: blank yellow / correct green / incorrect red;
- cache-safe OOXML recoloring;
- no Hint / Reveal surface;
- no answer-bearing Trainer metadata or Trainer answer sidecars;
- 81 reported passing core tests.

The v1 boundary is now:

```text
historical source data + supplied setup/classification judgments
    -> historical formula construction
    -> historical reformulation
    -> historical ratios / DuPont / EPS where supported
    -> historical analysis complete
```

Forecasting and valuation are **not part of v1 completion**.

The current builder still creates:

```text
Model_Bear
Model_Base
Model_Bull
Scenario_Summary
```

and currently registers six forecasting/valuation semantic components. Those must become dormant/hidden for v1.

Do not delete the forecast/valuation engine in this step. Do not claim it is correct for arbitrary companies. Leave it available for a later BAVGEM-architecture integration phase.

---

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve accepted Step 3 accounting integrity, Step 4 concept-aware identity, and Step 5 Trainer / Answer Key / Check behavior.
- v1 practice cells must be historical formula-bearing model-construction cells.
- Historical source statement values remain populated in Trainer.
- Balance-sheet classification choices remain populated in Trainer.
- Do not use forecast defaults or `marketData.dilutedShares` to invent historical EPS/share data.
- Forecast/valuation sheets must be hidden in both Trainer and Answer Key.
- Forecast/valuation components must not appear in the Trainer index, `python -m core list`, semantic active practice map, or workbook-wide Check.
- Do not add literal-input components, dynamic classification exercises, or an exercise DSL.
- Keep component definitions coordinate-free; coordinates resolve at build time.
- Do not reintroduce Hint, Reveal, VBA macros, Trainer answer metadata, or Trainer answer sidecars.
- Do not add HKEX/SEC automation.
- Do not redesign forecast or residual-income mathematics in this step.
- Do not weaken existing tests.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Target active practice surface after this step

The active v1 semantic catalog must contain exactly **21 historical components**:

```text
 1 effective_tax_rate_fy
 2 net_interest_fy
 3 net_interest_after_tax_fy
 4 nopat_fy

 5 owca_agg
 6 owcl_agg
 7 nowc_agg
 8 olta_agg
 9 oltl_agg
10 nola_agg
11 noa_agg
12 financial_assets_agg
13 financial_liabilities_agg
14 net_debt
15 equity_reformulated_fy

16 rnoa
17 after_tax_cod
18 spread
19 flev
20 roe_decomp
21 actual_roe
```

Remove these six deferred components from the active `COMPONENT_CATALOG` and stop registering them in v1:

```text
model_sales_y1
model_nopat_y1
model_ae_y1
model_tv
model_ivps
scenario_weighted
```

The underlying forecast/valuation workbook formulas may remain on hidden sheets, but they are not v1 exercises and not part of Check.

---

## Task 1 — Enforce the historical-only visible workbook boundary

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/workbook.py` only if visibility parity is cleaner there
- Test: `core/tests/test_trainer.py`

### Required hidden sheets

After build, both Trainer and Answer Key must have these sheet states:

```text
Model_Bear        -> hidden
Model_Base        -> hidden
Model_Bull        -> hidden
Scenario_Summary  -> hidden
```

Use ordinary Excel hidden state unless an existing workbook constraint requires `veryHidden`. Do not delete the sheets in this step.

Historical/source sheets and the Trainer index remain visible.

### Required isolation

Historical formulas must not reference the hidden forecast/valuation sheets.

Add a regression that scans the active historical semantic formulas and asserts none contains:

```text
Model_Bear
Model_Base
Model_Bull
Scenario_Summary
```

### TDD

Write first:

```python
def test_forecast_and_valuation_sheets_are_hidden_in_v1_pair(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    deferred = {"Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary"}
    for path in (trainer_path, answer_key_path):
        wb = load_workbook(path, data_only=False)
        for name in deferred:
            assert name in wb.sheetnames
            assert wb[name].sheet_state == "hidden"
        assert wb["Condensed Financials"].sheet_state == "visible"
        assert wb["ALT DuPont"].sheet_state == "visible"
        wb.close()
```

Also assert visible sheet-name parity between Trainer and Answer Key remains intact.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "hidden or visible or parity" -v
```

---

## Task 2 — Remove deferred forecast/valuation components from active v1 practice

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_trainer.py`
- Test: `core/tests/test_reference_integrity.py`

### Catalog rule

`COMPONENT_CATALOG` is the **active v1 practice catalog**. It must contain historical formulas only.

Remove the six deferred forecast/valuation `ComponentSpec`s listed above from the active catalog.

Do not replace them with dummy/disabled entries. The forecast/valuation source code itself remains available elsewhere in the repository for future work.

### Registration rule

Remove/disable the corresponding `_register(...)` calls inside:

```text
_build_model_tab()
_build_scenario_summary()
```

Do not remove the underlying workbook formulas or scenario calculations in this step.

### Public surfaces

After this task:

```bash
python -m core list
```

must list historical components only.

The generated Trainer index must list historical components only.

`check_workbook()` must scan only historical components because the matching Answer Key semantic map contains only historical active components.

### TDD

Add assertions equivalent to:

```python
DEFERRED = {
    "model_sales_y1",
    "model_nopat_y1",
    "model_ae_y1",
    "model_tv",
    "model_ivps",
    "scenario_weighted",
}
assert DEFERRED.isdisjoint({c.id for c in COMPONENT_CATALOG})
```

Build the pair and assert the semantic Answer Key map also excludes all six.

Capture CLI `list` output and assert none of the deferred IDs/titles appears.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "catalog or list or deferred" -v
```

---

## Task 3 — Expose authoritative historical expected values for the missing income-reformulation formulas

**Files:**
- Modify: `core/model/financial_math.py`
- Test: `core/tests/test_reference_integrity.py`

### Required anchor fields

Extend `AnchorMetrics` with:

```python
effective_tax_rate: float
net_interest: float
net_interest_after_tax: float
```

Populate them from the existing authoritative historical series already computed inside `compute_anchor()`:

```python
etr
net_int
niat
```

using the latest historical period.

Do not duplicate/recompute the accounting math in `ReferenceModelBuilder`.

### TDD regression

Assert for demo financials:

```python
anchor.net_interest_after_tax == pytest.approx(
    anchor.net_interest * (1 - anchor.effective_tax_rate)
)
anchor.nopat == pytest.approx(latest_net_income + anchor.net_interest_after_tax)
```

Use production line-resolution semantics rather than fixed row positions.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "tax or interest or nopat" -v
```

---

## Task 4 — Expand the active coordinate-free catalog to the 21-cell historical core

**Files:**
- Modify: `core/engine/component_catalog.py`
- Test: `core/tests/test_trainer.py`

### Required dependency order

Use this active catalog sequence:

```text
 1 effective_tax_rate_fy
 2 net_interest_fy
 3 net_interest_after_tax_fy       <- effective_tax_rate_fy, net_interest_fy
 4 nopat_fy                        <- net_interest_after_tax_fy

 5 owca_agg
 6 owcl_agg
 7 nowc_agg                        <- owca_agg, owcl_agg
 8 olta_agg
 9 oltl_agg
10 nola_agg                        <- olta_agg, oltl_agg
11 noa_agg                         <- nowc_agg, nola_agg
12 financial_assets_agg
13 financial_liabilities_agg
14 net_debt                        <- financial_assets_agg, financial_liabilities_agg
15 equity_reformulated_fy          <- noa_agg, net_debt

16 rnoa                            <- nopat_fy, noa_agg
17 after_tax_cod                   <- net_interest_after_tax_fy, net_debt
18 spread                          <- rnoa, after_tax_cod
19 flev                            <- net_debt, equity_reformulated_fy
20 roe_decomp                      <- rnoa, spread, flev
21 actual_roe                      <- equity_reformulated_fy
```

Retain existing IDs for the seven already-active historical components.

Add concise conceptual hints for the 14 new historical formulas. Hints explain relationships but do not simply reveal the cell formula.

### TDD

Assert:

```python
assert len(COMPONENT_CATALOG) == 21
assert [c.order for c in COMPONENT_CATALOG] == list(range(1, 22))
assert len({c.id for c in COMPONENT_CATALOG}) == 21
assert len({c.semantic_key for c in COMPONENT_CATALOG}) == 21
```

For every dependency, assert dependency order is lower than child order.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "catalog" -v
```

---

## Task 5 — Register the complete historical reformulation core from existing workbook formulas

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

### General rule

Do not create duplicate workbook calculations merely to create exercises. Register the formulas already used to construct the reference workbook.

Use the latest fiscal-year cell for this first coherent historical-core step.

### Register these existing Condensed Financials formulas

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

Expected values must come from authoritative Python-side historical math:

- tax / net interest / after-tax net interest -> `AnchorMetrics` fields from Task 3;
- category aggregate rows -> `self.anchor.reformulation.category_totals[category][last]`;
- NOPAT/NOWC/NOLA/NOA/Net Debt/Equity -> existing `AnchorMetrics` values.

Each semantic map formula must equal the exact formula already stored in the corresponding Answer Key cell.

### Keep setup inputs populated

Balance-sheet classification cells stay populated in Trainer and Answer Key.

Add a regression comparing every classification row between the pair and asserting Trainer still contains the same valid category as Answer Key.

Historical source statement values must likewise remain populated and identical between the pair.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "historical or classification or source" -v
```

---

## Task 6 — Register the full latest-comparable historical DuPont chain

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`

### Required active DuPont formulas

`ALT DuPont` already computes:

```text
RNOA
After-tax CoD
Spread
FLEV
ROE (decomposed)
Actual ROE
```

Keep existing registrations for:

```text
rnoa
spread
roe_decomp
```

Add:

```text
after_tax_cod
flev
actual_roe
```

Use the exact existing workbook formulas and expected values from `self.anchor.dupont` for the latest comparable historical period.

Do not alter the accepted equations:

```text
RNOA            = NOPAT / average NOA
After-tax CoD   = Net Interest After Tax / average Net Debt
Spread          = RNOA - After-tax CoD
FLEV            = average Net Debt / average reformulated Equity
ROE decomposed  = RNOA + FLEV * Spread
Actual ROE      = Net Income / average reformulated Equity
```

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "dupont or cod or flev or roe" -v
```

---

## Task 7 — Prove workbook-wide Check is historical-only

**Files:**
- Modify: `core/tests/test_trainer.py`

### Required behavior

A fresh v1 Trainer build must report:

```text
21 total historical practice cells
0 correct
0 incorrect
21 blank
```

when checked before learner input.

The existing yellow/green/red and repeated-cache behavior must remain intact for historical formula cells.

Add a regression that reads the Answer Key semantic map and proves every active component tab is one of the historical visible model sheets; no active component may point to a hidden deferred forecast/valuation sheet.

Check output must not mention hidden forecast/valuation components.

### Hardening regression

Retain/add the Step 5 OOXML regression proving Check changes only fill/style references needed for validation while preserving formula text and cached values.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. python -m core check --workbook /tmp/DEMO_HK_Trainer.xlsx
```

---

## Task 8 — Align docs and examples with historical-only v1

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Regenerate/update: `example/DEMO_HK_Trainer.xlsx`
- Regenerate/update: `example/DEMO_HK_Answer_Key.xlsx`
- Modify: `RESULT.md`

### Documentation contract

Docs must describe v1 as historical analysis only.

State explicitly:

```text
provided: historical source values + setup/classification judgments
practice: historical formulas, links, reformulation, ratios, DuPont
hidden/deferred: forecasting and valuation
```

Do not advertise Bear/Base/Bull, residual-income valuation, DCF, terminal value, or forward scenario practice as current v1 functionality.

You may state that forecast/valuation code remains experimental/deferred and will be revisited through the trusted BAVGEM forecasting architecture.

### Example audit

Regenerate the example pair and inspect with openpyxl:

- historical sheets visible;
- `Model_Bear`, `Model_Base`, `Model_Bull`, `Scenario_Summary` hidden in both;
- Trainer index contains exactly 21 active historical components;
- Trainer practice cells blank/yellow/no Note;
- Answer Key practice cells formula/yellow/legacy Note;
- source and classification cells remain populated;
- no Trainer answer-bearing sidecars;
- generated metadata stays ignored per `.gitignore`.

Do not add historical EPS in this step by using the forecast `dilutedShares` assumption. The current standardized interface does not yet define authoritative historical diluted-share history. Record this as the next historical-v1 expansion item rather than inventing data.

---

## Task 9 — Full regression and handoff evidence

**Files:**
- Modify: `RESULT.md`

Run at minimum:

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
PYTHONPATH=. python -m core --help
```

Expected high-level artifact result:

```text
Trainer / Answer Key pair exists
21 active historical semantic components
forecast/valuation tabs hidden in both
forecast/valuation components absent from active map/index/Check
fresh Trainer Check = 21 blank
historical source data/classifications populated
Trainer active practice cells blank/yellow/no Note
Answer Key active practice cells formula/yellow/Note
Hint/Reveal absent
```

`RESULT.md` must record exact test counts and artifact checks.

Do not commit or push.

---

## Acceptance criteria

Step 6 is accepted only if all are true:

1. v1 active catalog/map contains exactly 21 historical formula components.
2. The six previous forecast/valuation components are absent from active catalog, semantic map, Trainer index, CLI list, and Check.
3. `Model_Bear`, `Model_Base`, `Model_Bull`, and `Scenario_Summary` are hidden in both Trainer and Answer Key.
4. Historical/source sheets remain visible and visually matched between the pair.
5. Historical source numbers remain populated in Trainer.
6. Balance-sheet classification/setup judgments remain populated in Trainer.
7. The 15 historical reformulation formulas and six DuPont formulas are registered from the actual Answer Key cells.
8. Every active historical Trainer practice cell is blank yellow/no Note immediately after build.
9. Every active historical Answer Key practice cell contains the working formula, yellow fill, and non-empty legacy Note.
10. Workbook-wide Check scans only the 21 historical cells and preserves Step 5 cache-safe color behavior.
11. No historical EPS is fabricated from the forecast/default diluted-share assumption.
12. Docs/examples present v1 as historical-only and forecast/valuation as deferred.
13. Full core regression suite passes and demo build/audit succeeds.

## Next step after acceptance

Do **not** proceed automatically.

After Step 6 is accepted, ChatGPT should review the historical workbook as a product. The likely next historical-v1 work is:

1. extend meaningful historical formulas across all applicable fiscal periods rather than only latest-FY/latest-comparable cells; and
2. add historical EPS/per-share practice only after the standardized input path carries authoritative historical diluted-share data.

Forecasting/valuation remains deferred until a separate design explicitly integrates a trusted assumptions/judgment architecture, preferably the existing BAVGEM forecasting architecture.
