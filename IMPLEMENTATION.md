# Step 7 Correction — Period-Axis Integrity and Trainer Metadata Hygiene

> **Status:** Step 7 correction complete — period-axis integrity and metadata hygiene

> **For Cursor:** Read `TARGET.md` first. The accepted Step 7 implementation is commit `598948d3f0ac8651c0be86cf660073c96cfca20a` (`chat 7 Multi-Period Historical Model Construction`). Implement only this correction using red/green TDD. Run the exact verification commands, update `RESULT.md`, and stop. Do not begin Step 8. Do not commit or push; the user owns the implementation checkpoint commit.

**Goal:** Make the Step 7 multi-period historical foundation trustworthy when source periods arrive out of order, and make repeated Trainer generation incapable of leaving stale answer-bearing Trainer metadata beside the workbook.

**Architecture:** Canonicalize fiscal periods exactly once at the model boundary, before historical series, component expansion, workbook construction, and DuPont dependency logic consume the axis. Lower-level period expansion should reject non-chronological input rather than silently repairing it. Trainer generation should explicitly delete stale Trainer-only sidecars while preserving the matching Answer Key metadata used by Check and `list --workbook`.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing semantic map and cache-preserving Check implementation.

**Spec:** `TARGET.md`, especially the requirements that historical accounting logic be authoritative, historical inputs not be invented, Trainer-associated answer stores not leak answers, and the historical practice surface preserve true dependency logic.

## Why this correction is required

### Problem 1 — Period order is assumed rather than enforced

`ReferenceModelBuilder` currently derives `self.periods` directly from `financials.fiscal_years()` / `period_dates()`. `StandardizedFinancials` preserves the incoming list order, while JSON, Excel, and document-merging paths do not guarantee oldest-to-newest ordering.

Step 7 comparative formulas use `j - 1` as the immediately preceding fiscal year. Therefore an input ordered:

```text
2025 | 2024 | 2023
```

can silently make 2024 Sales Growth compare 2024 against 2025 and can make RNOA/FLEV/ROE use the wrong beginning-period denominator. The Python expected-value engine consumes the same period order, so Answer Key and Check can agree with the same incorrect chronology. This is a model-integrity defect, not merely a display-order issue.

### Problem 2 — Stale Trainer sidecars can survive regeneration

The normal build does not create a new Trainer component-map sidecar, but an old `*_Trainer.component_map.json`, `*_Trainer.trainer.json`, or Trainer assumptions sidecar can remain in an existing output directory. `load_semantic_map()` prefers a sidecar when present, so stale Trainer metadata can both retain answer-bearing data and cause `python -m core list --workbook ...Trainer.xlsx` to read obsolete semantics.

The current fresh-directory tests do not cover cleanup of pre-existing Trainer sidecars.

## Global constraints

- `TARGET.md` is read-only during implementation.
- Preserve all accepted Step 7 behavior: 25 conceptual schedule families and 118 concrete practice cells for the five-year demo.
- Preserve every Step 6/7 forecast-quarantine regression.
- Normal historical build must not execute `run_scenario()` or require forecast assumptions.
- Keep all four deferred forecast/valuation tabs hidden and placeholder-only.
- Do not expose any public forecast switch.
- Historical source values and classification/setup judgments remain populated.
- `Reported Equity`, `Total Capital`, and `CHECK` remain populated non-practice guardrails.
- Trainer practice cells remain blank/yellow/no-Note; Answer Key practice cells remain formula/yellow/Note.
- Check remains workbook-wide, non-disclosing, and cache-safe.
- No accounting-judgment exercises, research diagnostics, forecasting, valuation, Hint, Reveal, or VBA.
- No fixed five-year assumption in production code.
- Do not fabricate historical share-count/EPS data.
- Do not silently infer CAGR or irregular-period behavior in this correction.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Task 1 — Establish one authoritative fiscal-period axis

**Files:**
- Create: `core/model/period_axis.py`
- Modify: `core/engine/reference_model.py`
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Produces: `canonical_fiscal_periods(financials) -> list[date]`.
- Preserves: existing `StandardizedFinancials` input object and date-keyed `LineItem.values` mappings.
- Guarantees: model-facing periods are unique, chronological, and contiguous for annual comparative calculations.

- [ ] **Step 1: Write failing descending-period regression tests**

Construct a valid synthetic `StandardizedFinancials` whose `periods` are deliberately supplied newest-to-oldest:

```text
FY2025
FY2024
FY2023
```

Use distinct Revenue, Net Income, and balance-sheet values so wrong-period references are observable.

Build the Trainer/Answer Key pair and assert:

```text
workbook historical columns: 2023, 2024, 2025
SemanticMap period_index 0: 2023
SemanticMap period_index 1: 2024
SemanticMap period_index 2: 2025
```

Also assert:

- 2024 Sales Growth references 2024 and 2023 Revenue;
- 2025 Sales Growth references 2025 and 2024 Revenue;
- 2024 RNOA references 2024 NOPAT and 2024/2023 NOA;
- Python expected values match those chronological calculations.

Do not hard-code workbook row numbers. Resolve components/rows through the SemanticMap and existing row-map interfaces.

- [ ] **Step 2: Verify the regression fails against the current implementation**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "descending or chronological" -v
```

Expected before implementation: the model preserves descending input order and one or more chronology assertions fail.

- [ ] **Step 3: Add the period-axis module**

Create:

```python
from __future__ import annotations

from datetime import date

from ..data.interface import StandardizedFinancials


class PeriodAxisError(ValueError):
    """Historical fiscal-period axis is not suitable for comparative modeling."""


def canonical_fiscal_periods(
    financials: StandardizedFinancials,
) -> list[date]:
    ...
```

Required behavior:

1. Prefer non-interim fiscal periods:

```python
annual = [p.end_date for p in financials.periods if not p.is_interim]
raw = annual or [p.end_date for p in financials.periods]
```

2. Reject an empty period set with `PeriodAxisError`.

3. Reject duplicate period-end dates with a clear error containing `duplicate`.

4. Return periods sorted oldest -> newest.

5. When the annual path is used, reject missing fiscal years for now. For each adjacent pair:

```python
current.year == previous.year + 1
```

If not, raise `PeriodAxisError` explaining that contiguous annual fiscal periods are required for multi-period growth/DuPont calculations.

6. Do not mutate `financials.periods`.

7. Do not add CAGR, stub-period, 53-week-year, or irregular-period logic in this correction.

- [ ] **Step 4: Make `ReferenceModelBuilder` consume only the canonical axis**

Replace direct `financials.fiscal_years() or financials.period_dates()` use in `ReferenceModelBuilder.__init__` with:

```python
self.periods = canonical_fiscal_periods(financials)
```

This assignment must happen before:

- `compute_anchor()`;
- `expand_historical_specs()`;
- historical source-sheet generation;
- Condensed Financials construction;
- ALT DuPont construction.

The `LineItem.values` dictionaries are keyed by dates, so reordering the axis must only alter column/dependency order, not source values.

- [ ] **Step 5: Add duplicate and gapped-history regressions**

Duplicate periods:

```python
with pytest.raises(PeriodAxisError, match="duplicate"):
    ReferenceModelBuilder(financials_with_duplicate_fy)
```

Gapped annual history:

```text
FY2021
FY2023
```

must fail with a message containing `contiguous` rather than silently treating the two-year movement as one-year Sales Growth.

- [ ] **Step 6: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "period or chronological or descending or duplicate or contiguous" -v
```

---

## Task 2 — Prove the fix through a supported Excel ingestion path

**Files:**
- Test: `core/tests/test_reference_integrity.py` or `core/tests/test_trainer.py`
- Modify production ingestion code only if the model-boundary fix exposes a demonstrated ingestion defect.

**Interfaces:**
- Consumes: existing `ExcelExportAdapter` and normal `build_training_workbook()` path.
- Produces: a regression proving supported newest-to-oldest Excel headers still build chronologically.

- [ ] **Step 1: Create a temporary supported Excel input**

Build a small workbook with supported tabs and date columns deliberately ordered newest to oldest, for example:

```text
Line Item | 2025-12-31 | 2024-12-31 | 2023-12-31
```

Include enough valid IS/BS/CF lines to pass current source and reformulation integrity checks.

- [ ] **Step 2: Ingest through the normal Excel path**

Use `ExcelExportAdapter` or `HKManualDocumentAdapter` exactly as the public build path would.

Do not manually reorder the returned financials in the test.

- [ ] **Step 3: Build and assert chronological model output**

Assert the resulting Answer Key has historical headers oldest -> newest and that the 2024/2025 comparative formulas reference their true preceding fiscal year.

This test protects the real supported input workflow, not only direct synthetic object construction.

- [ ] **Step 4: Run the focused Excel regression**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "excel and descending" -v
```

---

## Task 3 — Defensively protect concrete component expansion

**Files:**
- Modify: `core/engine/component_catalog.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- `expand_historical_specs(periods)` continues to expand already-canonical dates.
- It must reject invalid order rather than silently sorting.

- [ ] **Step 1: Write failing direct-expansion tests**

Add:

```python
with pytest.raises(ValueError, match="increasing|chronological"):
    expand_historical_specs([fy2025, fy2024])

with pytest.raises(ValueError, match="duplicate"):
    expand_historical_specs([fy2024, fy2024])

assert len(expand_historical_specs([fy2023, fy2024, fy2025])) == 68
```

- [ ] **Step 2: Verify the descending/duplicate tests fail before implementation**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "expand_historical and period" -v
```

- [ ] **Step 3: Add a small input-contract guard**

At the beginning of `expand_historical_specs(periods)`, validate that:

- dates are unique;
- each date is strictly greater than the preceding date.

Do not sort inside this function. Sorting belongs at the `StandardizedFinancials` -> model boundary. This lower-level helper should fail loudly if a caller violates the chronological-axis contract.

Do not add a fixed five-year rule.

- [ ] **Step 4: Run the full component-expansion tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "period_aware or expand_historical" -v
```

The existing five-year demo count must remain 118 and the three-period count 68.

---

## Task 4 — Remove stale Trainer answer-bearing sidecars on every build

**Files:**
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_trainer.py`

**Interfaces:**
- Produces: idempotent Trainer-only sidecar cleanup.
- Preserves: matching Answer Key `.component_map.json` and `.assumptions.json` sidecars.

- [ ] **Step 1: Write the failing stale-sidecar regression**

Before a normal build, create these files at the intended Trainer output path:

```text
DEMO_HK_Trainer.component_map.json
DEMO_HK_Trainer.trainer.json
DEMO_HK_Trainer.assumptions.json
```

Put obvious sentinel strings in them:

```text
SECRET_OLD_FORMULA
SECRET_OLD_HINT
```

Run the normal build into the same output directory.

Assert all three Trainer-side files no longer exist after generation.

Also assert:

```text
DEMO_HK_Answer_Key.component_map.json exists
DEMO_HK_Answer_Key.assumptions.json exists
```

- [ ] **Step 2: Verify the regression fails before implementation**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "stale and sidecar" -v
```

- [ ] **Step 3: Add one explicit cleanup helper**

In `core/trainer/workbook.py`, add a small helper such as:

```python
def remove_trainer_sidecars(trainer_path: Path) -> None:
    for suffix in (
        ".component_map.json",
        ".trainer.json",
        ".assumptions.json",
    ):
        trainer_path.with_suffix(suffix).unlink(missing_ok=True)
```

If `Path.with_suffix()` does not produce the current naming convention correctly for every suffix, use the existing sidecar path helpers or construct the paths explicitly from `trainer_path.stem`. Test the exact filenames rather than assuming.

The helper must be idempotent.

- [ ] **Step 4: Invoke cleanup in the normal Trainer generation path**

Call the cleanup as part of normal generation so rebuilding into an existing directory always converges to the same safe result.

Do not delete any Answer Key sidecar.

- [ ] **Step 5: Verify Trainer-path `list` cannot read stale metadata**

After the stale-sidecar build test, call:

```python
main(["list", "--workbook", str(trainer_path)])
```

Capture stdout and assert:

- current output contains 25 schedule-family lines;
- current five-year ranges/counts are represented;
- `SECRET_OLD_FORMULA` is absent;
- `SECRET_OLD_HINT` is absent.

Keep the existing fresh-directory test that proves a normal build does not create a Trainer semantic sidecar.

- [ ] **Step 6: Run focused Trainer metadata tests**

```bash
PYTHONPATH=. pytest core/tests/test_trainer.py -k "sidecar or list or leak" -v
```

---

## Task 5 — Preserve all accepted Step 7 behavior

**Files:**
- Modify production files only when a demonstrated regression requires it.
- Test: existing full test suite.

- [ ] **Step 1: Re-run the Step 7 practice-surface checks**

The five-year demo must still satisfy:

```text
25 conceptual families
18 all-period families × 5 cells
7 comparable families × 4 cells
118 concrete practice cells
25 Trainer index rows
```

- [ ] **Step 2: Preserve Trainer / Answer Key contracts**

Verify:

```text
Trainer:    118 blank + yellow + no Note
Answer Key: 118 formula + yellow + non-empty Note
fresh Check: 0 correct / 0 incorrect / 118 blank
```

- [ ] **Step 3: Preserve historical and audit scaffolding**

Historical source statements, classification decisions, `Reported Equity`, `Total Capital`, and `CHECK` must remain populated and pair-consistent.

- [ ] **Step 4: Preserve deferred forecast quarantine**

At minimum rerun regressions proving:

- monkeypatched `run_scenario()` is never executed by normal build;
- all four deferred tabs are hidden placeholders in both workbooks;
- no active component points to a deferred tab;
- no public Hint/Reveal/forecast path is introduced.

- [ ] **Step 5: Preserve cache-safe Check behavior**

Do not weaken or remove the existing equivalent-formula/cached-value repeated-Check regression.

---

## Task 6 — Full verification, evidence, and stop

**Files:**
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` only to mark this correction complete after all verification succeeds.

- [ ] **Step 1: Run focused new regressions**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -k "period or chronological or descending or duplicate or contiguous" -v
PYTHONPATH=. pytest core/tests/test_trainer.py -k "period or sidecar or list" -v
```

Record the actual focused results.

- [ ] **Step 2: Run the full standalone test files**

```bash
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

Record exact pass counts.

- [ ] **Step 3: Run the complete core suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the exact pass count.

- [ ] **Step 4: Verify the public demo workflow**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -o /tmp/DEMO_HK_Trainer.xlsx
```

Expected:

```text
Components resolved: 118
```

Then:

```bash
PYTHONPATH=. python -m core check \
  --workbook /tmp/DEMO_HK_Trainer.xlsx
```

Expected:

```text
Checked 118 practice cells: 0 correct, 0 incorrect, 118 blank.
```

Then:

```bash
PYTHONPATH=. python -m core list --workbook /tmp/DEMO_HK_Trainer.xlsx
```

Expected: 25 resolved schedule groups covering 118 concrete cells total.

- [ ] **Step 5: Update `RESULT.md` with observed evidence**

Use this structure with actual results rather than predicted numbers:

```text
Status: Step 7 correction complete — period-axis integrity and metadata hygiene

Implementation base:
- 598948d3 Step 7 multi-period historical model

Period-axis audit:
- descending input canonicalized oldest -> newest: yes
- supported descending Excel input canonicalized: yes
- duplicate fiscal periods rejected: yes
- gapped annual histories rejected: yes
- comparative formulas use true previous fiscal year: yes

Trainer metadata audit:
- stale Trainer component-map sidecar removed: yes
- stale Trainer trainer.json removed: yes
- stale Trainer assumptions sidecar removed: yes
- Answer Key semantic metadata preserved: yes
- Trainer list resolves current 25 families: yes
- Trainer answer leakage: none

Demo preservation:
- fiscal periods: 5
- conceptual families: 25
- concrete practice cells: 118
- Trainer index rows: 25
- fresh Check: 0 correct / 0 incorrect / 118 blank

Tests:
- record every required command and exact observed pass count/result

Unresolved:
- none OR list exact blockers
```

- [ ] **Step 6: Mark this plan complete and stop**

Only after all tests and audits pass, change the status at the top of this file to indicate the correction is complete and leave Step 8 as the next locked roadmap step.

Do not start Step 8 in the same implementation session.

## Correction acceptance criteria

The Step 7 correction is accepted only when all are true:

1. every normal historical build derives one chronological, unique fiscal-period axis before historical model math or component expansion;
2. descending supported inputs build oldest -> newest without mutating source data;
3. duplicate fiscal dates fail clearly;
4. gapped annual histories fail rather than masquerading as one-period growth/comparatives;
5. `expand_historical_specs()` rejects non-increasing direct input rather than silently sorting;
6. comparative Sales Growth/RNOA/CoD/FLEV/ROE dependencies reference the true preceding fiscal year;
7. stale Trainer `.component_map.json`, `.trainer.json`, and `.assumptions.json` files are removed during regeneration;
8. Answer Key semantic/assumptions sidecars remain intact;
9. `list --workbook Trainer.xlsx` resolves current Answer Key semantics rather than stale Trainer data;
10. Step 7 remains 25 conceptual families / 118 concrete cells on the five-year demo;
11. workbook-wide Check remains non-disclosing and cache-safe;
12. normal historical build remains completely forecast-independent;
13. full core tests pass;
14. `RESULT.md` records actual verification evidence;
15. Step 8 remains unimplemented.

---

# Locked Post-Correction Roadmap — Do Not Implement Yet

## Step 8 — Guided accounting judgment and normalization

After this correction is independently reviewed and accepted, introduce selected accounting-treatment decisions while retaining a short feedback loop: operating versus financing classification, recurring versus non-recurring treatment, normalization, leases, stock-based compensation, goodwill/intangibles, deferred taxes, minority interests, acquisitions, and other topics only where material to the supplied company.

The design goal is to teach **why treatment changes economic interpretation**, not to turn ambiguous accounting into arbitrary multiple-choice trivia.

## Step 9 — Historical research diagnostics

Teach the learner to explain what changed and why: margin versus turnover/capital-intensity drivers of RNOA, working-capital behavior, accrual/cash conversion, operating versus financing sources of ROE change, dilution, segment economics, and earnings-quality/accounting consistency signals.

## Step 10 — Cross-company robustness

Validate the historical/judgment/diagnostic system on materially different non-financial companies, including at least one asset-light and one asset-heavy or working-capital-intensive business.

## Step 11 — Driver-based forecasting

Reintroduce forecasting only through explicit, traceable BAVGEM-style analyst assumptions and business drivers. Do not restore canned default vectors as company-specific forecasts.

## Step 12 — BAV valuation and research conclusion

Add residual-income/BAV valuation, appropriate cross-checks, sensitivities, and a concise evidence-based investment conclusion only after the forecast layer is separately trusted.

## Historical note

The detailed Step 7 multi-period implementation plan completed at commit `598948d3f0ac8651c0be86cf660073c96cfca20a` remains available in Git history. This file now intentionally contains only the active correction and the locked subsequent roadmap so Cursor has one unambiguous instruction surface.
