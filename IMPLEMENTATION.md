# Step 6 — Historical-Only v1: Quarantine Forecasting and Complete the Historical Formula Core

> **For Cursor:** Read `TARGET.md` first. Step 5 is accepted at implementation commit `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`). Implement only this active step using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Turn the current mixed historical/forecast builder into a trustworthy **historical-only v1**. A normal build must not execute the forecast/scenario engine or fabricate forecast assumptions. It should produce a coherent 21-component historical reformulation + DuPont practice surface, while retaining hidden deferred tab names for future integration.

**Architecture:** Preserve the existing historical accounting engine, formula-only semantic component map, sanitized Trainer, Answer Key Notes, and cache-safe workbook-wide Check. Add an explicit internal boundary between the historical build path and the dormant forecast/valuation scaffolding. The normal Trainer build uses the historical path only; forecast code can remain testable behind an internal opt-in but is not exposed through the v1 CLI or active workbooks.

**Tech Stack:** Python, pytest, openpyxl, existing OOXML cache-preserving fill patch.

**Spec:** `TARGET.md` as updated in planning commit `bafc3c4` (`Quarantine forecast engine from historical v1`).

## Current checkpoint review

Latest accepted implementation commit: `1db2b333100e1f81115286f26b381c8a795a7f0c` (`chat 5 corrected`). It reports 81 passing core tests and correctly implements the Step 5 Trainer / Answer Key / Check contract.

One architecture problem remains important for the new v1 boundary: `ReferenceModelBuilder.__init__` currently synthesizes default forecast assumptions and eagerly calls `run_scenario()` for Bear/Base/Bull before any workbook is built. Therefore merely hiding forecast tabs would still make the historical product depend on untrusted forecast logic. Step 6 must remove that dependency from the normal v1 path.

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve accepted Step 3 accounting integrity, Step 4 concept-aware identity, and Step 5 Trainer / Answer Key / Check behavior.
- Normal v1 build must not call `run_scenario()` or synthesize forecast vectors/terminal-growth assumptions.
- Do not use `marketData.dilutedShares` or any forecast default to invent historical EPS/share data.
- Historical source values and balance-sheet classification choices stay populated in Trainer.
- Practice cells are formula-bearing historical model-construction cells only.
- Deferred forecast/valuation tabs must be hidden in both workbooks and absent from active semantic practice, Trainer index, CLI list, and Check.
- No public v1 CLI flag may enable deferred forecasting.
- Do not delete the forecast/valuation source code; quarantine it for later BAVGEM integration.
- Do not add literal-input components, dynamic classification exercises, Hint, Reveal, VBA macros, or Trainer answer metadata.
- Keep component definitions coordinate-free; coordinates resolve at build time.
- Do not weaken existing identity/accounting/Check regressions.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Separate the normal historical build path from deferred forecasting

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

### Required interface

Add an internal builder switch:

```python
class ReferenceModelBuilder:
    def __init__(
        self,
        financials: StandardizedFinancials,
        assumptions: dict[str, Any] | None = None,
        *,
        include_deferred_forecast: bool = False,
    ):
        ...
```

`build_training_workbook()` must use the default `False`. Do not add a CLI flag for it.

### Normal historical initialization

When `include_deferred_forecast=False`:

- do not call `_default_assumptions()`;
- do not call `run_scenario()`;
- do not populate `_scenario_results` / `_base_result` from forecast math;
- preserve only configuration needed by historical work, especially `classificationOverrides` when supplied;
- do not require `marketData`, `scenarios`, growth vectors, margin vectors, beta, terminal growth, or diluted shares.

A minimal historical config is sufficient:

```python
self.assumptions = dict(assumptions or {})
self.assumptions.setdefault("classificationOverrides", {})
```

When `include_deferred_forecast=True`, preserve the old forecast scaffolding behavior so its source code remains available for later work. This flag is internal/deferred only.

### TDD — prove v1 cannot accidentally execute forecasting

Write first:

```python
def test_normal_v1_build_does_not_call_run_scenario(tmp_path, monkeypatch):
    import core.engine.reference_model as rm

    def fail(*args, **kwargs):
        raise AssertionError("forecast engine executed in historical-only v1")

    monkeypatch.setattr(rm, "run_scenario", fail)
    data = _ingest_demo()
    trainer, answer = build_training_workbook(
        data, tmp_path / "DEMO_HK_Trainer.xlsx"
    )
    assert trainer.exists()
    assert answer.exists()
```

Also add:

```python
def test_normal_v1_build_requires_no_forecast_assumptions(tmp_path):
    data = _ingest_demo()
    trainer, answer = build_training_workbook(
        data, tmp_path / "DEMO_HK_Trainer.xlsx", assumptions={"classificationOverrides": {}}
    )
    assert trainer.exists() and answer.exists()
```

If an Answer-Key assumptions sidecar is still emitted, assert it contains no synthesized `scenarios`, growth/margin vectors, beta, terminal growth, or default diluted-shares block unless the caller explicitly supplied them.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "historical or forecast or scenario or assumptions" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "forecast or historical" -v
```

---

## Task 2 — Replace live forecast output in v1 with hidden deferred placeholders

**Files:**
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_trainer.py`

### Normal v1 workbook shape

When `include_deferred_forecast=False`, build the historical sheets normally, then create these hidden placeholders:

```text
Model_Bear
Model_Base
Model_Bull
Scenario_Summary
```

Each placeholder should contain only a small non-financial marker such as:

```text
A1 = "Deferred from historical-only v1"
```

Do not populate company forecasts, valuations, scenario probabilities, terminal values, or per-share outputs on these v1 placeholder sheets.

Set:

```python
ws.sheet_state = "hidden"
```

in the Answer Key before the Trainer is copied, so both workbooks inherit identical hidden state.

When `include_deferred_forecast=True`, the existing `_build_model_tab()` / `_build_scenario_summary()` code may still build the experimental forecast workbook for direct internal tests; that mode is not part of the v1 product.

### TDD

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
        wb.close()
```

Add a regression proving every active historical semantic formula is independent of those four sheet names.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "deferred or hidden or parity" -v
```

---

## Task 3 — Make the active semantic catalog historical-only

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_trainer.py`

Remove these deferred IDs from active `COMPONENT_CATALOG`:

```text
model_sales_y1
model_nopat_y1
model_ae_y1
model_tv
model_ivps
scenario_weighted
```

The normal v1 historical build must not register them.

`python -m core list`, the Trainer index, the Answer Key semantic map, and workbook-wide Check must therefore contain historical components only.

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

Build the pair and assert the same against `load_semantic_map(answer_key_path)` and captured CLI `list` output.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "catalog or list or deferred" -v
```

---

## Task 4 — Expose authoritative historical expected values needed by the expanded practice surface

**Files:**
- Modify: `core/model/financial_math.py`
- Test: `core/tests/test_reference_integrity.py`

Extend `AnchorMetrics` with:

```python
effective_tax_rate: float
net_interest: float
net_interest_after_tax: float
```

Populate from the existing historical `etr`, `net_int`, and `niat` series at the latest fiscal period. Do not recompute them in the workbook builder.

Regression:

```python
anchor.net_interest_after_tax == pytest.approx(
    anchor.net_interest * (1 - anchor.effective_tax_rate)
)
anchor.nopat == pytest.approx(latest_net_income + anchor.net_interest_after_tax)
```

Resolve historical source rows with production line-resolution logic, never fixed row positions.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "tax or interest or nopat" -v
```

---

## Task 5 — Expand the active catalog to the 21-cell historical reformulation + DuPont core

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

Use exactly this active dependency order:

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

Keep the existing seven historical IDs and add the fourteen missing IDs. Hints should describe the financial relationship without dumping the exact formula.

Register the exact formulas already present in `Condensed Financials` and `ALT DuPont`; do not create duplicate calculation cells just to make exercises.

Authoritative expected values:

- tax/net interest/after-tax interest -> new `AnchorMetrics` fields;
- classified aggregate rows -> `self.anchor.reformulation.category_totals[category][last]`;
- NOPAT/NOWC/NOLA/NOA/Net Debt/Equity -> existing `AnchorMetrics` values;
- DuPont rows -> `self.anchor.dupont[...]` latest comparable period.

Catalog regressions:

```python
assert len(COMPONENT_CATALOG) == 21
assert [c.order for c in COMPONENT_CATALOG] == list(range(1, 22))
assert len({c.id for c in COMPONENT_CATALOG}) == 21
assert len({c.semantic_key for c in COMPONENT_CATALOG}) == 21
```

For every component, assert each dependency has a lower order.

Reference-map regression: every registered formula must exactly equal the corresponding Answer Key cell formula and have a non-`None` expected value.

### Preserve supplied inputs

Add assertions that every historical source statement cell and every balance-sheet classification cell is identical between Trainer and Answer Key. These cells must not become blank practice inputs.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "catalog or historical or classification or source" -v
```

---

## Task 6 — Make Check and public surfaces historical-only

**Files:**
- Modify: `core/tests/test_trainer.py`
- Modify: `core/__main__.py` only if help/list text needs correction

A fresh v1 Trainer must produce:

```text
Checked 21 practice cells: 0 correct, 0 incorrect, 21 blank.
```

The Answer Key semantic map must contain 21 components and every component must point to a visible historical sheet (`Condensed Financials` or `ALT DuPont` for this step). No component may point to a deferred placeholder.

Preserve Step 5 behavior:

- exact correct formula -> green;
- wrong formula -> red;
- blank -> yellow;
- corrected/re-cleared cells refresh on subsequent Check;
- cached equivalent formula remains correct across repeated Checks;
- Check never prints formulas, expected values, or hints.

`python -m core --help` still exposes `{ingest,build,check,list}` only. Do not add a forecast option.

### Verify

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. python -m core --help
```

---

## Task 7 — Align docs, examples, and handoff evidence

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Regenerate/update: `example/DEMO_HK_Trainer.xlsx`
- Regenerate/update: `example/DEMO_HK_Answer_Key.xlsx`

Docs must say:

```text
provided: historical source values + setup/classification judgments
practice: historical links, reformulation formulas, ratios, DuPont
hidden placeholders: forecasting and valuation
normal v1 build: does not execute forecast/scenario engine
future: forecasting returns only after trusted BAVGEM assumptions/judgment integration
```

Do not advertise Bear/Base/Bull forecasts, residual-income valuation, DCF, terminal value, or forward valuation as current v1 functionality.

Regenerated demo pair must show:

- 21 active historical practice components;
- deferred tabs hidden and placeholder-only;
- no active forecast/valuation formulas or Notes;
- Trainer 21 blank yellow practice cells with no Notes;
- Answer Key 21 formula + legacy Note practice cells;
- source data and classification judgments populated in Trainer.

## Full verification

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

Then audit `/tmp/DEMO_HK_Trainer.xlsx` and its matching Answer Key with openpyxl:

1. 21 active semantic components only;
2. Trainer 21 blank/yellow/no-Note practice cells;
3. Answer Key 21 formula/yellow/non-empty legacy-Note cells;
4. source statement cells populated and pair-identical;
5. classification cells populated and pair-identical;
6. four deferred tabs hidden in both files and contain only the v1 deferred marker;
7. no active formula references a deferred tab;
8. Check reports `0 correct, 0 incorrect, 21 blank` on fresh build;
9. no `hint`, `reveal`, or forecast CLI surface;
10. no Trainer answer-bearing hidden sheets/sidecars;
11. generated demo metadata remains ignored as specified by `.gitignore`.

## Acceptance criteria

Step 6 is accepted only when all are true:

1. Normal v1 build succeeds when `run_scenario()` is patched to fail.
2. Normal v1 build requires no forecast/scenario assumptions.
3. Deferred tabs exist only as hidden placeholders in the generated v1 pair.
4. Active catalog/map/index/Check contain exactly 21 historical components.
5. Forecast/valuation IDs are absent from active product surfaces.
6. Historical reformulation formulas use authoritative expected values and exact Answer Key formulas.
7. Historical DuPont formulas preserve the accepted accounting equations.
8. Historical source values and classification judgments remain populated in Trainer.
9. Trainer / Answer Key / Check / leakage contracts from Step 5 remain intact.
10. Full core suite and demo build succeed.

## RESULT.md handoff

Record:

```text
Status: Step 6 complete

Implementation checkpoint:
- based on 1db2b333

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
- source values populated: yes
- classifications populated: yes
- Trainer answer leakage: none
- repeated cached Check: preserved

Tests:
- list every command and exact pass count/result

Unresolved:
- none OR exact blockers
```

Do not commit or push after updating `RESULT.md`.
