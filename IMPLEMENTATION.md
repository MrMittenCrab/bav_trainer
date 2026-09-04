# Step 6 Correction — Historical-Only Foundation Before Competency Expansion

> **For Cursor:** Read `TARGET.md` first. The current implementation checkpoint is `6e06db13b917a8e01168c41acda8f8e2224ef60a` (`chat 6 corrected`). That checkpoint contains useful historical-formula expansion but does **not** satisfy Step 6 because forecasting/valuation is still active and the catalog incorrectly contains 27 components. Implement only this correction step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Make the normal BAV Trainer v1 a trustworthy **historical model-construction foundation**: exactly 21 active historical reformulation/DuPont practice components, no normal-path forecast execution or synthesized forecast assumptions, and four hidden deferred forecast/valuation placeholders.

**Architecture:** Preserve the accepted historical accounting engine, semantic component map, sanitized Trainer, Answer Key Notes, and cache-safe workbook-wide Check. Separate the normal historical build path from dormant forecast/valuation scaffolding with an internal-only switch. Keep the historical work already added in `6e06db1`; remove the six forecast/valuation components from all active product surfaces.

**Tech Stack:** Python, pytest, openpyxl, existing OOXML cache-preserving fill patch.

**Spec:** `TARGET.md` at planning commit `a5948ce3472ceb1524ef4adab4e7e43c33854e95` (`Define equity research competency target`). The broader target now defines the eventual product as a progression from accounting novice to junior accounting-based equity-research competence. This step remains deliberately narrow: make the historical foundation correct before adding judgment, diagnostics, forecasting, valuation, or research communication.

## Current checkpoint review

`6e06db1` correctly added much of the intended 21-cell historical reformulation + DuPont work, including authoritative tax/interest fields and historical formulas. Preserve that work.

It also introduced or retained four Step 6 violations that must be corrected:

1. `ReferenceModelBuilder.__init__` still synthesizes default forecast assumptions and eagerly calls `run_scenario()` in the normal build path.
2. `build()` still produces live Bear/Base/Bull and scenario-summary forecast/valuation output.
3. `COMPONENT_CATALOG` contains six deferred forecast/valuation IDs, producing 27 active components instead of 21.
4. tests/docs/`RESULT.md` were changed to validate the incorrect 27-component state.

Step 6 is not accepted until those violations are removed and independently regression-tested.

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve accepted accounting integrity, concept-aware line identity, Trainer/Answer-Key sanitation, and cache-safe Check behavior.
- Preserve the useful historical formula expansion already present in `6e06db1`.
- Normal v1 build must not call `run_scenario()` or synthesize forecast vectors, terminal growth, beta, scenario probabilities, or default diluted shares.
- Do not use forecast defaults to invent historical share-count or per-share data.
- Historical source values and classification/setup judgments remain populated in Trainer.
- Active v1 practice cells are formula-bearing historical model-construction cells only.
- Deferred forecast/valuation tabs must be hidden in both workbooks and absent from semantic practice, Trainer index, CLI list, and Check.
- No public v1 CLI flag may enable deferred forecasting.
- Do not delete the dormant forecast/valuation source code; quarantine it for later BAVGEM integration.
- Do not add classification quizzes, free-form research grading, Hint, Reveal, VBA macros, or Trainer answer metadata in this step.
- Keep component definitions coordinate-free; coordinates resolve at build time.
- Scope statements must not imply that this operating/financing model applies unchanged to banks, insurers, brokers, or other financial institutions.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Write regressions that expose the forecast leak

**Files:**
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_trainer.py`

**Interfaces:**
- Consumes: `build_training_workbook(financials, output_path, assumptions=None)`.
- Proves: normal v1 generation is independent of `run_scenario()` and forecast-shaped configuration.

- [ ] **Step 1: Add the failing normal-build forecast quarantine test**

Add to `core/tests/test_reference_integrity.py` using the existing `_ingest_demo()` helper:

```python
def test_normal_v1_build_does_not_call_run_scenario(tmp_path, monkeypatch):
    import core.engine.reference_model as rm

    def fail(*args, **kwargs):
        raise AssertionError("forecast engine executed in historical-only v1")

    monkeypatch.setattr(rm, "run_scenario", fail)

    data = _ingest_demo()
    trainer, answer = build_training_workbook(
        data,
        tmp_path / "DEMO_HK_Trainer.xlsx",
    )

    assert trainer.exists()
    assert answer.exists()
```

- [ ] **Step 2: Add a no-forecast-assumptions regression**

```python
def test_normal_v1_build_requires_no_forecast_assumptions(tmp_path):
    data = _ingest_demo()
    trainer, answer = build_training_workbook(
        data,
        tmp_path / "DEMO_HK_Trainer.xlsx",
        assumptions={"classificationOverrides": {}},
    )
    assert trainer.exists()
    assert answer.exists()
```

If the Answer-Key assumptions sidecar remains part of the build, load it and assert that normal v1 did not synthesize keys such as `scenarios`, `growthVector`, `marginVector`, `terminalGrowth`, `beta`, or a default `marketData.dilutedShares` block unless the caller explicitly supplied them.

- [ ] **Step 3: Run the focused tests and verify the first test fails on the current code**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "normal_v1_build" -v
```

Expected before implementation: the patched `run_scenario()` raises `AssertionError`.

---

## Task 2 — Quarantine forecast initialization behind an internal switch

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Produces: `ReferenceModelBuilder(..., include_deferred_forecast: bool = False)`.
- Normal caller: `build_training_workbook()` uses the default `False` and exposes no public forecast switch.

- [ ] **Step 1: Add the internal constructor boundary**

Use this signature:

```python
class ReferenceModelBuilder:
    def __init__(
        self,
        financials: StandardizedFinancials,
        assumptions: dict[str, Any] | None = None,
        *,
        include_deferred_forecast: bool = False,
    ):
        self.fin = financials
        self.periods = financials.fiscal_years() or financials.period_dates()
        self.include_deferred_forecast = include_deferred_forecast
        self.assumptions = dict(assumptions or {})
        self.assumptions.setdefault("classificationOverrides", {})
        ...
```

Do not call `_default_assumptions()` in normal mode.

- [ ] **Step 2: Keep historical initialization unconditional and forecast initialization conditional**

Historical setup, including `compute_anchor(... classification_overrides=...)`, must run in both modes.

Only inside:

```python
if self.include_deferred_forecast:
    ...
```

may the builder synthesize the legacy forecast defaults, read `marketData.dilutedShares`, call `run_scenario()`, or populate `_scenario_results` / `_base_result`.

Do not silently enable deferred mode because scenario-shaped keys happen to be present in an assumptions JSON.

- [ ] **Step 3: Run the quarantine regressions**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "normal_v1_build" -v
```

Expected: both tests pass.

---

## Task 3 — Replace normal forecast output with four hidden placeholders

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_trainer.py`

**Interfaces:**
- Normal v1 sheets: historical tabs plus hidden `Model_Bear`, `Model_Base`, `Model_Bull`, `Scenario_Summary` placeholders.
- Deferred internal mode may continue to call the old forecast builders for isolated legacy tests.

- [ ] **Step 1: Write the placeholder test first**

Add:

```python
def test_v1_deferred_tabs_are_hidden_placeholders(tmp_path):
    trainer_path, answer_key_path = _build_pair(tmp_path)
    deferred = {"Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary"}

    for path in (trainer_path, answer_key_path):
        wb = load_workbook(path, data_only=False)
        for name in deferred:
            ws = wb[name]
            assert ws.sheet_state == "hidden"
            assert ws["A1"].value == "Deferred from historical-only v1"
            assert ws.max_row == 1
            assert ws.max_column == 1
        wb.close()
```

Also iterate through all active semantic formulas and assert none contains any deferred sheet name.

- [ ] **Step 2: Change normal `build()` behavior**

When `include_deferred_forecast=False`, build only the historical model sheets normally, then create:

```python
for name in ("Model_Bear", "Model_Base", "Model_Bull", "Scenario_Summary"):
    ws = wb.create_sheet(name)
    ws["A1"] = "Deferred from historical-only v1"
    ws.sheet_state = "hidden"
```

Do not call `_build_model_tab()` or `_build_scenario_summary()` in normal mode.

When `include_deferred_forecast=True`, preserve the legacy experimental forecast builders for internal use only.

- [ ] **Step 3: Run the placeholder regressions**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "deferred or hidden" -v
```

Expected: pass in both Trainer and Answer Key.

---

## Task 4 — Restore the active catalog and public practice surface to exactly 21 historical components

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_trainer.py`

**Interfaces:**
- Public `COMPONENT_CATALOG`: exactly 21 historical components.
- Public SemanticMap / Trainer index / `python -m core list` / Check: same 21 components.
- Optional dormant forecast specs, if still needed internally, must live outside `COMPONENT_CATALOG`.

- [ ] **Step 1: Replace the incorrect 27-component test**

Delete/replace `test_catalog_has_27_components_in_dependency_order` with:

```python
def test_catalog_has_21_historical_components_in_dependency_order():
    assert len(COMPONENT_CATALOG) == 21
    assert [c.order for c in COMPONENT_CATALOG] == list(range(1, 22))
    assert len({c.id for c in COMPONENT_CATALOG}) == 21
    assert len({c.semantic_key for c in COMPONENT_CATALOG}) == 21

    by_id = {c.id: c for c in COMPONENT_CATALOG}
    for spec in COMPONENT_CATALOG:
        for dep in spec.depends_on:
            assert dep in by_id
            assert by_id[dep].order < spec.order
```

Add:

```python
DEFERRED_IDS = {
    "model_sales_y1",
    "model_nopat_y1",
    "model_ae_y1",
    "model_tv",
    "model_ivps",
    "scenario_weighted",
}

assert DEFERRED_IDS.isdisjoint({c.id for c in COMPONENT_CATALOG})
```

Build an Answer Key and assert the same six IDs are absent from its SemanticMap.

- [ ] **Step 2: Make `COMPONENT_CATALOG` exactly this dependency order**

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

Preserve the historical specs already implemented in `6e06db1`.

Remove these IDs from active `COMPONENT_CATALOG`:

```text
model_sales_y1
model_nopat_y1
model_ae_y1
model_tv
model_ivps
scenario_weighted
```

If the internal deferred forecast path still requires `ComponentSpec` objects, keep them in a clearly separate internal `DEFERRED_COMPONENT_SPECS` collection. Do not merge that collection into public catalog/list/check behavior.

- [ ] **Step 3: Keep the authoritative historical registration already added**

For all 21 components, ensure:

- Answer Key cell contains the registered formula;
- SemanticMap formula exactly equals that cell formula;
- expected value is non-`None`;
- historical tax/interest expected values come from `AnchorMetrics`;
- classified aggregates come from `anchor.reformulation.category_totals`;
- NOPAT/NOWC/NOLA/NOA/Net Debt/Equity come from the historical anchor;
- DuPont expected values come from `anchor.dupont` latest comparable period.

Do not duplicate calculation cells merely to create exercises.

- [ ] **Step 4: Run catalog/reference tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "catalog or historical or deferred" -v
```

---

## Task 5 — Correct the Trainer/Check regressions that currently defend the wrong product

**Files:**
- Modify: `core/tests/test_trainer.py`
- Modify: `core/__main__.py`

**Interfaces:**
- Fresh Trainer: 21 blank practice cells.
- Check output: `Checked 21 practice cells: 0 correct, 0 incorrect, 21 blank.`
- CLI: `{ingest,build,check,list}` only.

- [ ] **Step 1: Remove live forecast-input expectations from the populated-input guardrail**

Keep assertions that historical source-statement cells and balance-sheet classifications remain populated and pair-identical.

Remove expectations that normal v1 contains live values such as `Model_Base!B5`, `Model_Base!B6`, `Model_Base!B9`, `Model_Base!G22`, `Model_Base!G39`, or `Scenario_Summary!B4:B6`. Those tabs are now deferred placeholders.

- [ ] **Step 2: Correct three-state Check totals**

In the expanded historical three-state regression, after one correct formula, one wrong formula, and the rest blank, assert:

```python
assert summary.total == 21
assert summary.correct == 1
assert summary.incorrect == 1
assert summary.blank == 19
```

Preserve all existing Step 5 regressions for:

- exact correct formula -> green;
- wrong formula -> red;
- blank -> yellow;
- corrected/re-cleared state refresh;
- equivalent cached formula remaining correct across repeated Checks;
- Check never printing formulas, expected values, or hints.

- [ ] **Step 3: Correct CLI copy without adding a forecast switch**

`python -m core list` must list only the 21 historical components.

No public CLI option may enable `include_deferred_forecast=True`.

The existing `-a/--assumptions` argument may remain because historical configuration such as classification overrides can be supplied, but change its help text from scenario-specific wording to:

```text
Optional historical configuration JSON (e.g. classificationOverrides)
```

`python -m core --help` must continue to expose only:

```text
ingest
build
check
list
```

- [ ] **Step 4: Run the Trainer and CLI regressions**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. python -m core list
PYTHONPATH=. python -m core --help
```

---

## Task 6 — Align docs and regenerate a clean historical demo pair

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`

**Interfaces:**
- Public documentation describes current v1 as a historical model-construction foundation, not a complete equity-research curriculum.
- Future product direction may be mentioned, but forecasting/valuation must not be advertised as active v1 behavior.

- [ ] **Step 1: Align documentation with `TARGET.md`**

Docs should communicate:

```text
end-state goal:
accounting novice -> junior accounting-based equity-research competence

current v1:
historical model-construction foundation for non-financial operating companies

provided in v1:
historical source values + classification/setup judgments

active practice in v1:
historical links + reformulation + ratios + DuPont

deferred:
accounting-judgment exercises + research diagnostics + forecasting + valuation + research conclusion

normal v1 build:
does not execute forecast/scenario engine
```

Do not describe Bear/Base/Bull forecasts, residual-income valuation, terminal value, IVPS, or scenario weighting as active v1 exercises.

Where current copy says `formula/input` for yellow practice cells, use `formula`.

- [ ] **Step 2: Regenerate both demo workbooks through the normal v1 path**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o example/DEMO_HK_Trainer.xlsx
```

Expected CLI build result:

```text
Components resolved: 21
```

- [ ] **Step 3: Audit the regenerated pair with openpyxl/tests**

Verify all of the following:

1. Answer Key SemanticMap has exactly 21 active components.
2. Trainer has 21 blank bright-yellow practice cells and zero Notes on those cells.
3. Answer Key has 21 working-formula bright-yellow practice cells and one non-empty legacy Note on each.
4. historical source values remain populated and pair-identical;
5. classification/setup judgments remain populated and pair-identical;
6. `Model_Bear`, `Model_Base`, `Model_Bull`, `Scenario_Summary` are hidden in both files;
7. each deferred tab contains only `A1 = "Deferred from historical-only v1"`;
8. no active semantic formula references a deferred tab;
9. Trainer has no active answer-bearing hidden sheet or Trainer answer sidecar;
10. generated Answer-Key metadata remains ignored according to the existing `.gitignore` policy.

- [ ] **Step 4: Check the fresh demo**

```bash
PYTHONPATH=. python -m core check --workbook example/DEMO_HK_Trainer.xlsx
```

Expected:

```text
Checked 21 practice cells: 0 correct, 0 incorrect, 21 blank.
```

---

## Task 7 — Full verification and truthful handoff

**Files:**
- Modify: `RESULT.md`

- [ ] **Step 1: Run the complete verification suite**

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

- [ ] **Step 2: Record exact evidence in `RESULT.md`**

Use this structure with actual observed pass counts/results:

```text
Status: Step 6 correction complete

Implementation base:
- 6e06db1 chat 6 corrected

Historical-only boundary:
- normal build calls run_scenario: no
- forecast assumptions required: no
- deferred tabs: four hidden placeholders
- public forecast CLI: none

Active practice:
- component count: 21
- Trainer blank/yellow/no Note: 21/21
- Answer Key formula/yellow/Note: 21/21
- Check fresh result: 0 correct / 0 incorrect / 21 blank

Preservation:
- historical source values populated: yes
- classifications/setup judgments populated: yes
- Trainer answer leakage: none
- repeated cached Check behavior: preserved

Tests:
- record every verification command and exact pass count/result

Unresolved:
- none OR list exact blockers
```

Do not claim `Unresolved: none` unless every acceptance criterion below is verified.

- [ ] **Step 3: Stop**

Do not begin Step 7 curriculum expansion. Do not commit or push.

## Step 6 acceptance criteria

Step 6 is accepted only when all are true:

1. normal v1 build succeeds when `run_scenario()` is patched to fail;
2. normal v1 build requires no forecast/scenario assumptions;
3. four deferred tabs are hidden placeholder-only sheets in both generated workbooks;
4. active catalog/map/index/list/Check contain exactly 21 historical components;
5. six forecast/valuation IDs are absent from active product surfaces;
6. the 21 historical formulas preserve authoritative expected values and exact Answer Key formulas;
7. historical source values and classification/setup judgments remain populated in Trainer;
8. Trainer/Answer-Key/Check/leakage contracts from Step 5 remain intact;
9. full core suite passes;
10. fresh demo Check reports `0 correct / 0 incorrect / 21 blank`;
11. docs describe v1 as a historical foundation and do not overclaim job-readiness;
12. no public forecast-enabling CLI surface exists.

---

# Locked Post-Step-6 Competency Roadmap — Do Not Implement Yet

The following sequence is part of the product direction in `TARGET.md`, but **Cursor must not implement it during the active Step 6 correction**. ChatGPT will rewrite `IMPLEMENTATION.md` one step at a time after each prior checkpoint is implemented and verified.

## Step 7 — Multi-period historical model construction

Move from isolated latest-period practice to coherent historical schedules across all applicable fiscal years.

Competencies:

- cross-sheet historical linking;
- revenue growth and margin calculation;
- effective tax and financing-result history;
- NOPAT / NOWC / NOLA / NOA / Net Debt / Equity across periods;
- RNOA / after-tax CoD / Spread / FLEV / ROE through time;
- historical per-share bridges when actual share data is supplied;
- schedule-level audit and reconciliation.

Success criterion: learner reconstructs a connected multi-year historical model rather than memorizing individual cells.

## Step 8 — Guided accounting judgment and normalization

Introduce selected judgment exercises while retaining short feedback loops.

Competencies:

- operating versus financing classification;
- recurring versus non-recurring treatment;
- earnings normalization;
- leases, stock-based compensation, goodwill/intangibles, deferred taxes, minority interests, acquisitions, and other topics only where material to the supplied company;
- reconciliation of alternative defensible treatments.

Success criterion: learner begins to understand why accounting treatment changes economic interpretation, not merely how to write the downstream formula.

## Step 9 — Historical research diagnostics

Teach the learner to explain what changed and why.

Competencies:

- margin versus turnover/capital-intensity drivers of RNOA;
- working-capital behavior;
- accruals and cash conversion;
- financing versus operating sources of ROE change;
- dilution and per-share economics;
- segment economics where disclosed;
- earnings-quality and accounting consistency diagnostics.

Prefer structured diagnostic exercises over unreliable free-form essay grading.

Success criterion: learner can turn historical calculations into an economic explanation.

## Step 10 — Cross-company robustness

Prove the historical/judgment/diagnostic system on materially different non-financial operating companies rather than only `DEMO_HK`.

At minimum include contrasting business models such as:

- an asset-light company; and
- an asset-heavy or working-capital-intensive company.

Success criterion: semantic identity, accounting logic, exercises, and checks generalize without company-specific coordinate hacks or fabricated inputs.

## Step 11 — Driver-based forecasting

Only after Steps 7–10 are accepted, reintroduce forecasting through trusted BAVGEM assumption/judgment architecture.

Competencies:

- forecast revenue from explicit business drivers;
- forecast margins from historical economics and stated assumptions;
- forecast operating assets/liabilities consistently with activity;
- model financing effects without double-counting;
- separate historical fact from analyst judgment;
- expose sensitivities and scenario logic explicitly.

Do not restore canned default forecast vectors as company-specific forecasts.

Success criterion: every material forecast assumption is explicit, traceable, and economically interpretable.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation and appropriate cross-checks only after the forecast layer is trustworthy.

Competencies:

- cost of equity / capital assumptions;
- abnormal earnings / residual income;
- continuing value / terminal assumptions;
- intrinsic value per share;
- scenario/sensitivity interpretation;
- appropriate valuation cross-checks;
- concise investment conclusion linking accounting analysis, drivers, forecast, valuation, risks, and variant assumptions.

Success criterion: on an unseen non-financial company case, the learner can move from reported accounts to a defensible accounting-based equity-research conclusion with materially reduced scaffolding.

## Roadmap design rule

Do not measure progress primarily by the number of yellow cells. For every future step, define acceptance in terms of **analyst competency demonstrated on an unfamiliar company**, with component counts used only as implementation integrity checks.
