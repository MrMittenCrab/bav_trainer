# Step 9H.1 — Historical v1 Exit Gate and Canonical Artifact Refresh

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first. The accepted implementation base is commit `76ec6f26ef663a7c65d7fd23604e9ea6c1a45977` (`Step 9G1`, Step 9G.1 complete). Implement only Step 9H.1 below using red/green TDD. This is a historical-v1 release gate, not a curriculum expansion. Preserve all Step 8 judgment behavior, the trusted-workbook boundary, Step 9A source-completeness / tax / normalization / `#N/A` semantics, Step 9B working-capital diagnostics, Step 9C profitability drivers/change attribution, Step 9D ROE attribution, Step 9E cash-conversion trends, Step 9F per-share / normalized-per-share analysis, and Step 9G cross-company robustness. Do not add forecasting, valuation, new accounting topics, new semantic families, new public CLI commands, or new user-facing worksheets. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Close the historical-v1 foundation with one explicit release gate that proves the hard product contract end-to-end, refreshes the committed canonical demo workbooks from the current builder, and removes stale documentation before any forecasting work begins.

**Architecture:** Add one focused exit-gate test module that composes existing public build/check/list paths rather than introducing a second validation system. The gate verifies active-catalog integrity, Trainer/Answer-Key separation, non-disclosing Check behavior, dormant forecast isolation, optional-module gating, and representative cross-company builds. Production model code should remain unchanged unless the gate exposes a genuine generalized defect. Refresh `example/DEMO_HK_Trainer.xlsx` and `example/DEMO_HK_Answer_Key.xlsx` from the accepted current builder, then align `README-HK-TRAINER.md`, `skills/bav-trainer/SKILL.md`, and `RESULT.md` with the actual historical-v1 surface.

**Tech Stack:** Python, pytest, openpyxl, existing component catalogs, `ReferenceModelBuilder`, `build_training_workbook`, `load_semantic_map`, `group_components_by_family`, `check_workbook`, existing cross-company fixtures, and the public CLI in `core.__main__`.

**Spec:** `TARGET.md`, especially the hard requirements and “Definition of done for historical v1”. This checkpoint should establish that the historical model-construction foundation is trustworthy; it must not claim forecasting competence, valuation competence, full independent accounting judgment, or full equity-research readiness.

## Global Constraints

- `TARGET.md` is read-only. Record its SHA-256 before work and require the same SHA-256 after verification.
- Preserve non-financial-company scope.
- Add no new active formula family. The active family-order namespace remains exactly `1..78` across the existing catalogs.
- Add no new user-facing worksheet, source field, judgment type, practice cell, public CLI command, Hint/Reveal surface, forecast, scenario, or valuation output.
- Preserve current ordinary-demo surfaces exactly:
  - no assumptions / no share history: `62 families / 259 practice cells`;
  - normalization assumptions / no share history: `66 / 279`.
- Preserve current share-enabled surfaces exactly:
  - shares / no normalization: `70 / 293`;
  - shares + normalization: `78 / 331`.
- Preserve Step 9G.1 synthetic robustness surfaces:
  - asset-light services: `59 / 248`;
  - inventory retail: `78 / 331`;
  - capital-intensive manufacturer: `70 / 293`.
- Synthetic fixtures remain synthetic robustness evidence, not empirical real-company validation.
- Normal historical builds must not execute `run_scenario`, `weighted_ivps`, or any dormant forecast/valuation path.
- Deferred tabs remain hidden placeholders in both Trainer and Answer Key and remain excluded from the semantic practice map and Check.
- Trainer practice cells remain blank bright yellow with no Note/comment. Answer-Key practice cells retain the working formula and a non-empty legacy Note.
- Trainer-associated answer-bearing sidecars remain absent after build.
- Check may recolor cells only; it must not replace, clear, or rewrite learner-entered formulas.
- Check output remains non-disclosing: aggregate counts are allowed, but formulas, expected values, and hints must not be printed.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Accepted Step 9G.1 baseline

Commit `76ec6f26` records:

- `281 passed` locally;
- three synthetic non-financial archetypes build, fresh-Check, and fully-filled-Check successfully;
- ordinary demo remains `62/259` and `66/279`;
- share-enabled surfaces remain `70/293` and `78/331`;
- all deferred forecast/valuation tabs remain hidden placeholders;
- production model code was unchanged by Step 9G.1;
- forecasting and valuation have not begun.

`README-HK-TRAINER.md` is now materially stale: it still describes the product as Step 7–9A and reports obsolete `161/141` component counts. The committed demo `.xlsx` files also need to be regenerated from the current accepted builder so the repository example matches the documented product.

---

### Task 1: Add the historical-v1 active-catalog release gate

**Files:**
- Create: `core/tests/test_historical_v1_exit_gate.py`
- Read only: `core/engine/component_catalog.py`

**Interfaces:**
- Consumes all active `ComponentFamily` catalogs.
- Produces one release-gate assertion that the active historical family namespace is complete, unique, and separate from deferred forecast/valuation specs.

- [ ] **Step 1: Add the catalog list explicitly**

In the new test module import:

```python
from core.engine.component_catalog import (
    COMPONENT_CATALOG,
    NORMALIZATION_COMPONENT_CATALOG,
    QUALITY_COMPONENT_CATALOG,
    WORKING_CAPITAL_COMPONENT_CATALOG,
    PROFITABILITY_DRIVER_COMPONENT_CATALOG,
    PROFITABILITY_CHANGE_COMPONENT_CATALOG,
    ROE_ATTRIBUTION_COMPONENT_CATALOG,
    QUALITY_CHANGE_COMPONENT_CATALOG,
    PER_SHARE_COMPONENT_CATALOG,
    PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
    NORMALIZED_PER_SHARE_COMPONENT_CATALOG,
    DEFERRED_COMPONENT_SPECS,
)
```

Define:

```python
ACTIVE_CATALOGS = (
    COMPONENT_CATALOG,
    NORMALIZATION_COMPONENT_CATALOG,
    QUALITY_COMPONENT_CATALOG,
    WORKING_CAPITAL_COMPONENT_CATALOG,
    PROFITABILITY_DRIVER_COMPONENT_CATALOG,
    PROFITABILITY_CHANGE_COMPONENT_CATALOG,
    ROE_ATTRIBUTION_COMPONENT_CATALOG,
    QUALITY_CHANGE_COMPONENT_CATALOG,
    PER_SHARE_COMPONENT_CATALOG,
    PER_SHARE_ATTRIBUTION_COMPONENT_CATALOG,
    NORMALIZED_PER_SHARE_COMPONENT_CATALOG,
)
```

- [ ] **Step 2: Write the release-gate assertions**

```python
def test_historical_v1_active_catalog_namespace_is_frozen():
    families = [family for catalog in ACTIVE_CATALOGS for family in catalog]
    ids = [family.id for family in families]
    orders = [family.order for family in families]

    assert len(ids) == len(set(ids))
    assert len(orders) == len(set(orders))
    assert sorted(orders) == list(range(1, 79))

    deferred_ids = {spec.id for spec in DEFERRED_COMPONENT_SPECS}
    assert deferred_ids.isdisjoint(ids)
    assert all(family.category not in {"forecasting", "valuation"} for family in families)
```

Do not renumber existing families to make the test pass. If the assertion fails, identify an accidental catalog regression.

- [ ] **Step 3: Run the focused test**

```bash
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py::test_historical_v1_active_catalog_namespace_is_frozen -v
```

Expected: pass on the accepted Step 9G.1 implementation.

---

### Task 2: Prove normal historical builds are independent of dormant forecasting

**Files:**
- Modify: `core/tests/test_historical_v1_exit_gate.py`
- Production code only if the test exposes a real generalized leak.

**Interfaces:**
- Consumes the public `build_training_workbook` path and Step 9G.1 fixtures.
- Proves that normal historical generation does not execute dormant scenario/valuation functions.

- [ ] **Step 1: Add a fail-fast forecast stub**

```python
def _forecast_must_not_run(*args, **kwargs):
    raise AssertionError("dormant forecast/valuation engine executed during historical build")
```

- [ ] **Step 2: Parameterize representative normal builds**

Use:

```python
from core.tests.cross_company_fixtures import (
    asset_light_services_case,
    inventory_retail_case,
    capital_intensive_manufacturer_case,
)
from core.tests.test_per_share import _share_enabled_demo, DEMO_ASSUMPTIONS
```

Cover at minimum:

```text
ordinary demo + normalization assumptions
asset-light services
inventory retail (shares + normalization)
capital-intensive manufacturer (shares only)
```

- [ ] **Step 3: Monkeypatch the imported dormant functions in the builder module**

```python
def test_normal_historical_build_never_executes_dormant_forecast(monkeypatch, tmp_path):
    import core.engine.reference_model as reference_model

    monkeypatch.setattr(reference_model, "run_scenario", _forecast_must_not_run)
    monkeypatch.setattr(reference_model, "weighted_ivps", _forecast_must_not_run)
    # Build the representative cases through build_training_workbook(...).
```

Every normal build must succeed. Do not enable `include_deferred_forecast=True` anywhere in this test.

- [ ] **Step 4: Assert deferred tabs and semantic exclusion for every build**

For each Answer Key and Trainer:

```python
for name in DEFERRED_TAB_NAMES:
    assert wb[name].sheet_state == "hidden"
    assert wb[name]["A1"].value == DEFERRED_PLACEHOLDER

assert not any(
    comp.tab in DEFERRED_TAB_NAMES
    or comp.category in {"forecasting", "valuation"}
    for comp in smap.all_ordered()
)
```

Run:

```bash
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -k dormant -v
```

---

### Task 3: Prove the two-workbook / Answer-Key-only answer contract at release level

**Files:**
- Modify: `core/tests/test_historical_v1_exit_gate.py`
- Reuse: `core/tests/test_trainer.py`

**Interfaces:**
- Consumes a canonical demo build with `DEMO_HK_Assumptions.json`.
- Proves the visible Trainer/Answer-Key contract for every active semantic practice cell.

- [ ] **Step 1: Build the canonical demo in a temporary directory**

Use the same public path as the README:

```python
trainer, answer = build_training_workbook(
    data,
    tmp_path / "DEMO_HK_Trainer.xlsx",
    assumptions,
)
smap = load_semantic_map(answer)
assert len(group_components_by_family(smap)) == 66
assert len(smap.all_ordered()) == 279
```

- [ ] **Step 2: Check every active practice cell in both workbooks**

For each resolved component:

```python
row, col = parse_cell_ref(comp.cell)
trainer_cell = trainer_wb[comp.tab].cell(row=row, column=col)
answer_cell = answer_wb[comp.tab].cell(row=row, column=col)

assert trainer_cell.value is None
assert trainer_cell.comment is None
assert _fill_rgb(trainer_cell) == "FFFF00"

assert answer_cell.value == comp.formula
assert answer_cell.comment is not None
assert (answer_cell.comment.text or "").strip()
assert _fill_rgb(answer_cell) == "FFFF00"
```

Use or import the existing `_fill_rgb` helper; do not create a different color convention.

- [ ] **Step 3: Require Trainer answer-bearing sidecars to be absent**

```python
for suffix in (".component_map.json", ".trainer.json", ".assumptions.json"):
    assert not trainer.with_suffix(suffix).exists()
```

The matching Answer Key may retain its existing internal/sidecar metadata used by Check.

- [ ] **Step 4: Verify Check changes color only**

Choose one numeric practice component, enter its exact Answer-Key formula, save, and record the formula string. Run `check_workbook(trainer)` twice. Require:

```text
cell value after first Check == entered formula
cell value after second Check == entered formula
fill after Check == green
cached-result behavior remains covered by existing test_trainer regression
```

Also leave a second component blank and require it remains `None` and yellow after Check.

- [ ] **Step 5: Preserve the non-disclosure CLI regression**

Do not create a new Check output path. Run the existing focused non-disclosure test from `test_trainer.py` as part of Task 6.

---

### Task 4: Refresh the committed canonical demo workbooks

**Files:**
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Do not modify: `example/DEMO_HK_Standardized.json`
- Do not modify: `example/DEMO_HK_Assumptions.json`

**Interfaces:**
- Consumes the accepted public build command.
- Produces committed example binaries matching the current `66 families / 279 cells` normalization-enabled demo surface.

- [ ] **Step 1: Regenerate from source inputs, not by editing Excel manually**

Run:

```bash
python -m core build example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx
```

- [ ] **Step 2: Verify the regenerated pair**

Run a short Python verification using repository APIs:

```python
from pathlib import Path
from core.trainer.semantic_io import load_semantic_map
from core.trainer.workbook import group_components_by_family
from core.trainer.checker import check_workbook

trainer = Path("example/DEMO_HK_Trainer.xlsx")
answer = Path("example/DEMO_HK_Answer_Key.xlsx")
smap = load_semantic_map(answer)
assert len(group_components_by_family(smap)) == 66
assert len(smap.all_ordered()) == 279
summary = check_workbook(trainer)
assert (summary.correct, summary.incorrect, summary.blank) == (0, 0, 279)
```

- [ ] **Step 3: Verify no stale Trainer sidecars were left behind**

```python
for suffix in (".component_map.json", ".trainer.json", ".assumptions.json"):
    assert not Path("example/DEMO_HK_Trainer.xlsx").with_suffix(suffix).exists()
```

Do not manually paste formulas into the committed Trainer.

---

### Task 5: Bring user-facing documentation up to the actual historical-v1 state

**Files:**
- Modify: `README-HK-TRAINER.md`
- Modify: `skills/bav-trainer/SKILL.md`
- Modify: `RESULT.md`
- Do not modify: `TARGET.md`

**Interfaces:**
- Documents the accepted product honestly without implying forecasting, valuation, or real-company empirical validation.

- [ ] **Step 1: Replace stale Step 7–9A capability language in `README-HK-TRAINER.md`**

The current README still reports obsolete `161/141` component counts. Update it so the current capability description includes:

```text
historical reformulation + DuPont
classification judgment
earnings normalization
cash-conversion / accrual diagnostics and trends
working-capital diagnostics
RNOA margin/turnover and change attribution
ROE operating/financing attribution
optional diluted per-share analysis
optional normalized diluted-EPS bridge
synthetic cross-company robustness matrix
```

Explicitly state:

```text
Historical v1 foundation: release-gated by Step 9H.1
Forecasting: deferred
Valuation: deferred
Investment conclusion: deferred
Real-company empirical validation: not established by the synthetic matrix
```

- [ ] **Step 2: Fix Quick Start counts exactly**

The README must say:

```text
with DEMO_HK_Assumptions.json: 66 families / 279 practice cells
without assumptions:           62 families / 259 practice cells
```

The illustrative demo has no historical share input, so `Per Share Analysis` is absent in both demo builds.

- [ ] **Step 3: Update the skill frontmatter and product loop**

Remove the stale description ending at Step 9A. The skill should describe the current historical-v1 surface and retain the current optional-gating language.

Keep these exact regression facts visible somewhere in the skill:

```text
ordinary demo: 62/259 base, 66/279 with normalization
share-enabled: 70/293 base, 78/331 with normalization
cross-company synthetic matrix: services 59/248, retail 78/331, manufacturer 70/293
```

- [ ] **Step 4: Do not overclaim completion**

Use “historical-v1 model-construction foundation complete/release-gated”, not “BAV Trainer complete” or “job-ready”. Preserve the distinction in `TARGET.md` between historical model mechanics and the broader forecasting/valuation/research curriculum.

---

### Task 6: Run the historical-v1 exit suite and record evidence

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all checks pass.

- [ ] **Step 1: Record `TARGET.md` SHA-256 before final verification**

```bash
shasum -a 256 TARGET.md
```

Keep the value in the terminal/output notes and compare it after all work. Do not edit `TARGET.md`.

- [ ] **Step 2: Run focused exit-gate tests**

```bash
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -v
PYTHONPATH=. pytest core/tests/test_cross_company_robustness.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_normalization.py -v
PYTHONPATH=. pytest core/tests/test_per_share.py -v
PYTHONPATH=. pytest core/tests/test_per_share_attribution.py -v
PYTHONPATH=. pytest core/tests/test_normalized_per_share.py -v
```

- [ ] **Step 3: Run the full historical suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual passing count. Do not prestate the new count.

- [ ] **Step 4: Re-run the canonical demo release checks**

Require:

```text
base demo:          62 families / 259 cells / 0 correct / 0 incorrect / 259 blank
normalization demo: 66 families / 279 cells / 0 correct / 0 incorrect / 279 blank
canonical committed demo pair: 66 / 279 / 0-0-279 blank
shares only:        70 / 293
shares + norm:      78 / 331
services matrix:    59 / 248
retail matrix:      78 / 331
manufacturer matrix:70 / 293
```

- [ ] **Step 5: Verify the public CLI remains exactly four commands**

Run:

```bash
python -m core --help
```

Require only:

```text
ingest
build
check
list
```

Do not add a `forecast`, `value`, `hint`, or `reveal` command.

- [ ] **Step 6: Re-check `TARGET.md` SHA-256**

```bash
shasum -a 256 TARGET.md
```

It must exactly match the value recorded in Step 1.

- [ ] **Step 7: Update `RESULT.md` with release-gate evidence**

Record:

```text
Status: Step 9H.1 complete — historical v1 exit gate
actual full pytest count
active family namespace 1..78 unique
normal build forecast isolation verified
Trainer/Answer-Key practice contract verified across all canonical demo cells
Check formula-preservation / non-disclosure verified
canonical demo workbooks regenerated from source
all exact surface counts above
cross-company matrix remains synthetic, not empirical company validation
forecasting / valuation remain deferred
TARGET.md unchanged
```

- [ ] **Step 8: Mark this plan complete only after every verification is green**

Add a concise status line at the top of `IMPLEMENTATION.md`. Do not prepare or implement forecasting in this checkpoint.

---

## Definition of Done

Step 9H.1 is complete only when all of the following are true:

1. Active historical family IDs and orders are unique and the family-order namespace is exactly `1..78`.
2. Deferred forecast/valuation specs are not active historical families.
3. Representative normal builds succeed even when `run_scenario` and `weighted_ivps` are patched to fail immediately if called.
4. Deferred forecast/valuation tabs remain hidden placeholders and are absent from the semantic practice surface.
5. Every canonical demo Trainer practice cell is blank bright yellow with no Note/comment.
6. Every matching Answer-Key practice cell contains the authoritative formula and a non-empty legacy Note.
7. Trainer answer-bearing sidecars are absent.
8. Check does not alter learner-entered formula contents and remains non-disclosing.
9. Canonical committed demo workbooks are regenerated from current source code and verify at `66 families / 279 cells / 0-0-279 blank`.
10. Ordinary demo surfaces remain `62/259` and `66/279`.
11. Share-enabled surfaces remain `70/293` and `78/331`.
12. Step 9G.1 matrix surfaces remain `59/248`, `78/331`, and `70/293`.
13. `README-HK-TRAINER.md` and `skills/bav-trainer/SKILL.md` no longer contain obsolete Step 7–9A capability/count claims.
14. Documentation states that historical v1 is release-gated but forecasting, valuation, full research readiness, and empirical real-company validation remain outside this checkpoint.
15. Public CLI remains exactly `{ingest, build, check, list}`.
16. Full `core/tests/` suite passes.
17. `TARGET.md` SHA-256 is unchanged.
18. Cursor performs no git commit/push/reset/rebase/merge operations.

Stop after reporting Step 9H.1 verification. Do not begin the forecasting layer in the same implementation checkpoint.
