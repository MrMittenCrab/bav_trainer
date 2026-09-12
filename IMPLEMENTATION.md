Status: Step 9J.1 complete — GOOGL historical reference audit

# Step 9J.1 — GOOGL Historical Reference Audit + Convergence Roadmap

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read the revised `TARGET.md` first, then read this plan in full. The accepted implementation base is commit `69e500f5e8d304e7274283f766f3d170fca4ce6c` (`Step 9I1`, learner-ready historical presentation complete). `TARGET.md` was revised by ChatGPT in planning commit `f8e7f688047ab94e98e72ad24ae105d10b426fdc` to make `example/GOOGL_Demo_Integrated_Financials.xlsx` the explicit structural reference for historical convergence. Implement only Step 9J.1 below. This remains **Step 9 historical work**. Do not begin forecasting, valuation, scenarios, or forward-model activation. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Convert the GOOGL integrated workbook from an informal inspiration into an explicit, evidence-based historical reference contract: inspect it read-only, compare it with the current Trainer/Answer-Key product, classify historical gaps, and produce a prioritized Step 9 convergence roadmap without changing active model formulas yet.

**Architecture:** Add one small read-only workbook-audit utility with a synthetic test fixture so the GOOGL inventory is reproducible rather than hand-waved. Use that audit plus direct workbook inspection to write one concise historical reference/gap document. The document must distinguish what the GOOGL workbook actually contains from what `TARGET.md` independently requires. No current historical formula family, worksheet, expected value, Check rule, or practice count should change in this checkpoint.

**Tech Stack:** Python, pytest, openpyxl, existing repository workbooks, current canonical Trainer/Answer-Key pair, and existing Step 9 regression tests.

**Spec:** Revised `TARGET.md`, especially `Reference workbook for historical convergence`, `Historical accounting competence to cover`, and `Step 9 roadmap before forecasting`.

## Global Constraints

- `TARGET.md` is read-only for Cursor in this checkpoint.
- Remain in Step 9. Forecasting and valuation stay deferred.
- Treat `example/GOOGL_Demo_Integrated_Financials.xlsx` as a **read-only reference artifact**.
- Do not modify or regenerate the GOOGL workbook.
- Do not infer a capability merely because its name would be plausible. Record only what the workbook actually evidences.
- When a target topic is not evidenced by the GOOGL workbook, say so explicitly rather than silently filling the gap from general knowledge.
- Preserve active family namespace exactly `1..78`.
- Add no semantic family, practice cell, user-facing worksheet, judgment type, source field, or public CLI command.
- Preserve current surfaces exactly:
  - ordinary demo: `62 / 259`;
  - normalization demo: `66 / 279`;
  - shares only: `70 / 293`;
  - shares + normalization: `78 / 331`;
  - services matrix: `59 / 248`;
  - retail matrix: `78 / 331`;
  - manufacturer matrix: `70 / 293`.
- Preserve fresh workbook style from Step 9I.1: Aptos Narrow 11, white/yellow only, no decorative borders; Check green/red remains functional feedback only.
- Do not expand root `README.md` back into a technical essay. It remains the minimal practical landing page.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

## Accepted Step 9I.1 baseline

Commit `69e500f5` records:

- learner-ready minimal workbook style;
- practical root README;
- active historical family namespace unchanged at `1..78`;
- `292 passed` locally;
- forecasting / valuation still deferred;
- canonical demo and cross-company surfaces preserved.

This checkpoint should therefore answer a different question:

> What useful **historical** structure and analytical depth does the GOOGL integrated workbook contain that the current Trainer should eventually teach, and which parts should not be copied?

---

### Task 1: Add a reproducible read-only workbook inventory utility

**Files:**
- Create: `scripts/audit_reference_workbook.py`
- Create: `core/tests/test_reference_workbook_audit.py`

**Interfaces:**
- Produces: `audit_workbook(path: Path) -> dict`
- Optional CLI:
  `python scripts/audit_reference_workbook.py <workbook.xlsx>`

The audit must never save or mutate the inspected workbook.

- [x] **Step 1: Write a synthetic workbook test first**

In `core/tests/test_reference_workbook_audit.py`, create a temporary workbook with:

```text
Sheet "Income Statement" — visible
  A1 = Revenue
  B1 = 100
  C1 = =B1*1.1

Sheet "Model_Base" — hidden
  A1 = Deferred example
```

Then test:

```python
result = audit_workbook(path)

assert result["workbook"] == path.name
assert [s["name"] for s in result["sheets"]] == [
    "Income Statement",
    "Model_Base",
]
assert result["sheets"][0]["state"] == "visible"
assert result["sheets"][1]["state"] == "hidden"
assert result["sheets"][0]["formula_cells"] == 1
assert result["sheets"][0]["nonempty_cells"] == 3
```

Also require a stable list of representative text labels from the used range.

- [x] **Step 2: Run the test red**

```bash
PYTHONPATH=. pytest core/tests/test_reference_workbook_audit.py -v
```

Expected: fail because the audit utility does not exist.

- [x] **Step 3: Implement the smallest read-only audit**

Implement:

```python
def audit_workbook(path: Path) -> dict:
```

Use `openpyxl.load_workbook(path, data_only=False, read_only=True)`.

Return:

```python
{
    "workbook": path.name,
    "sheets": [
        {
            "name": ws.title,
            "state": ws.sheet_state,
            "max_row": ...,
            "max_column": ...,
            "nonempty_cells": ...,
            "formula_cells": ...,
            "representative_labels": [...],
        },
        ...
    ],
}
```

Rules:

- `nonempty_cells`: cells whose value is not `None`;
- `formula_cells`: string values beginning with `=`;
- `representative_labels`: preserve workbook text exactly; collect the first 40 distinct non-empty string values encountered in columns A–C, in workbook order;
- do not normalize, reinterpret, or rename workbook labels;
- close the workbook;
- never call `save()`.

- [x] **Step 4: Add a simple CLI**

When executed directly:

```bash
python scripts/audit_reference_workbook.py example/GOOGL_Demo_Integrated_Financials.xlsx
```

print deterministic JSON to stdout:

```python
print(json.dumps(audit_workbook(path), indent=2, default=str))
```

No new `python -m core` command is added.

- [x] **Step 5: Run focused tests green**

```bash
PYTHONPATH=. pytest core/tests/test_reference_workbook_audit.py -v
```

Expected: pass.

---

### Task 2: Inventory the GOOGL reference and the current historical product

**Files:**
- Read only: `example/GOOGL_Demo_Integrated_Financials.xlsx`
- Read only: `example/DEMO_HK_Answer_Key.xlsx`
- Create: `docs/GOOGL_HISTORICAL_REFERENCE.md`

**Interfaces:**
- Consumes the audit utility from Task 1.
- Produces a source-grounded reference inventory and historical gap map.

- [x] **Step 1: Record hashes before inspection**

Run:

```bash
shasum -a 256 example/GOOGL_Demo_Integrated_Financials.xlsx
shasum -a 256 example/DEMO_HK_Answer_Key.xlsx
```

Keep both values for end-of-checkpoint verification.

- [x] **Step 2: Run the audit on both workbooks**

```bash
python scripts/audit_reference_workbook.py \
  example/GOOGL_Demo_Integrated_Financials.xlsx \
  > /tmp/googl_reference_inventory.json

python scripts/audit_reference_workbook.py \
  example/DEMO_HK_Answer_Key.xlsx \
  > /tmp/trainer_reference_inventory.json
```

Read both inventories before drafting the document.

- [x] **Step 3: Inspect the actual sheets directly where labels are ambiguous**

Use a short one-off Python inspection with `openpyxl` to print only:

```text
sheet name
sheet visibility
non-empty values in columns A:C
formula/non-formula status
```

for sections necessary to understand the historical structure.

Do not print or reproduce entire worksheets. Do not treat the root README or general model knowledge as evidence for a workbook section that is not actually visible in the GOOGL file.

- [x] **Step 4: Create `docs/GOOGL_HISTORICAL_REFERENCE.md` with exactly these sections**

```markdown
# GOOGL Historical Reference

## Role of the reference
## GOOGL workbook inventory
## Current Trainer inventory
## Historical capability gap matrix
## Explicitly deferred / not copied
## Prioritized Step 9 queue
```

Keep it analytical and concise. This is an internal development reference, not a marketing document.

---

### Task 3: Build the historical capability gap matrix from evidence

**Files:**
- Modify: `docs/GOOGL_HISTORICAL_REFERENCE.md`

**Interfaces:**
- Produces one explicit classification per historical capability.

- [x] **Step 1: Use only these status labels**

Every capability row must use exactly one status:

```text
implemented
implemented-differently
missing-current-data-supported
missing-needs-new-explicit-data
deferred-forward
not-trainer-target
not-evidenced-in-GOOGL
```

Definitions:

- `implemented`: substantially present in current Trainer.
- `implemented-differently`: same analytical purpose exists but is adapted to training mechanics.
- `missing-current-data-supported`: not currently taught, but current standardized historical inputs appear sufficient without inventing facts.
- `missing-needs-new-explicit-data`: useful historical module requires a new explicit source fact/input contract.
- `deferred-forward`: forecasting / scenarios / valuation / forward-looking analysis.
- `not-trainer-target`: pipeline/automation or other functionality that should not become a Trainer feature merely because the reference has it.
- `not-evidenced-in-GOOGL`: required by `TARGET.md`, but the inspected GOOGL workbook does not visibly evidence the topic.

- [x] **Step 2: The matrix must evaluate all of these historical areas**

Create one row for each:

```text
source statements / statement linkage
operating-vs-financing reformulation
DuPont / RNOA / Spread / FLEV / ROE
classification judgment
recurring/non-recurring normalization
cash conversion / accrual analysis
working-capital behavior
RNOA margin / turnover / asset intensity
ROE operating / financing attribution
historical per-share / diluted-share bridge
stock-based compensation / dilution
capex / depreciation / PP&E / asset intensity
leases
goodwill / acquired intangibles / acquisitions
deferred taxes / unusual tax rates
minority / non-controlling interests
segment economics
accounting consistency / reconciliation checks
historical interpretation / diagnostics
```

Columns:

```text
Historical area
GOOGL evidence
Current Trainer
Status
Source facts required
Training adaptation
Proposed Step 9 action
```

- [x] **Step 3: Separate GOOGL evidence from TARGET-driven requirements**

For every row:

- `GOOGL evidence` must cite the actual sheet/section/label observed in the workbook, or say `Not evidenced in inspected workbook`.
- `Current Trainer` must cite the actual current sheet/family/feature, or say absent.
- Do not claim GOOGL contains SBC, segment economics, NCI, or any other topic unless inspection actually supports that claim.

- [x] **Step 4: Treat forward sections as explicitly deferred**

Any GOOGL content involving:

```text
forecast years
Bear/Base/Bull
scenario probabilities
terminal value
residual income valuation
DCF
valuation multiples
market-price rationalization
guidance / consensus
```

must be classified `deferred-forward` for the current roadmap.

Do not translate these into active Step 9 implementation tasks.

- [x] **Step 5: Treat automation / monitoring as not a Trainer target**

Any reference functionality whose purpose is:

```text
coverage maintenance
news monitoring
sentinel / scheduled update
vault / dossier persistence
automation infrastructure
```

must be classified `not-trainer-target` unless a future user request changes product scope.

---

### Task 4: Produce a prioritized historical convergence queue

**Files:**
- Modify: `docs/GOOGL_HISTORICAL_REFERENCE.md`
- Modify: `RESULT.md`
- Modify only if needed for roadmap consistency: `README.md`
- Modify only if needed for roadmap consistency: `skills/bav-trainer/SKILL.md`

**Interfaces:**
- Produces the next Step 9 implementation order; it does not implement those modules yet.

- [x] **Step 1: Use four priority buckets**

The `Prioritized Step 9 queue` must use:

```text
Priority A — historically useful and current-data-supported
Priority B — historically useful but needs explicit new historical inputs
Priority C — TARGET-required historical topic not evidenced by GOOGL
Deferred — forecasting / valuation / non-Trainer reference features
```

- [x] **Step 2: Rank within each bucket by dependency order**

Use this ordering principle:

```text
source facts
-> accounting treatment / classification
-> historical schedule
-> ratio / bridge
-> attribution / interpretation
```

Prefer foundational historical schedules before derivative interpretation exercises.

- [x] **Step 3: Do not preselect a module without evidence**

The first future implementation step after 9J.1 should be the highest-value `Priority A` item revealed by the audit.

If there is no credible Priority A item, the next step should define the smallest explicit historical source-data contract needed for the highest-value Priority B item.

Do not choose forecasting as the fallback.

- [x] **Step 4: Keep root README minimal**

Only touch `README.md` if its `Planned` section still implies forecasting is the next immediate stage.

If changed, limit the edit to one short roadmap statement equivalent to:

```text
Next: continue Step 9 historical convergence using the GOOGL integrated workbook as a structural reference.
Later: forecasting, valuation, scenarios, and investment conclusions.
```

Do not add the gap matrix to the README.

- [x] **Step 5: Update `RESULT.md`**

Record:

```text
Step 9J.1 complete — GOOGL historical reference audit
GOOGL workbook inspected read-only
current Trainer inspected
historical gap matrix created
Priority A / B / C counts
next historical implementation candidate
forecasting / valuation still deferred
GOOGL workbook hash unchanged
TARGET.md unchanged by Cursor
```

Do not claim a capability was implemented merely because it was identified.

---

### Task 5: Verify reference integrity and preserve the historical product

**Files:**
- Test: `core/tests/test_reference_workbook_audit.py`
- Test: existing Step 9 regression modules
- Do not modify: `TARGET.md`
- Do not modify: `example/GOOGL_Demo_Integrated_Financials.xlsx`

- [x] **Step 1: Re-check the reference workbook hashes**

Run:

```bash
shasum -a 256 example/GOOGL_Demo_Integrated_Financials.xlsx
shasum -a 256 example/DEMO_HK_Answer_Key.xlsx
```

The GOOGL SHA-256 must exactly match the value recorded before inspection.

The canonical Answer Key should also remain unchanged in this audit-only checkpoint.

- [x] **Step 2: Run focused audit tests**

```bash
PYTHONPATH=. pytest core/tests/test_reference_workbook_audit.py -v
```

- [x] **Step 3: Run historical release regressions**

```bash
PYTHONPATH=. pytest core/tests/test_learner_ready_presentation.py -v
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -v
PYTHONPATH=. pytest core/tests/test_cross_company_robustness.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
```

- [x] **Step 4: Run the full suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the actual final passing count. The pre-Step-9J.1 baseline is `292 passed`; the count may increase only because of the new audit tests.

- [x] **Step 5: Verify product surfaces are unchanged**

Require:

```text
active family orders = 1..78
base demo = 62 / 259
normalization demo = 66 / 279
shares only = 70 / 293
shares + normalization = 78 / 331
services = 59 / 248
retail = 78 / 331
manufacturer = 70 / 293
CLI = {ingest, build, check, list}
```

No active formula family, workbook sheet, or practice count changes in Step 9J.1.

- [x] **Step 6: Verify Step 9I.1 presentation remains intact**

Fresh canonical Trainer and Answer Key still require:

```text
Aptos Narrow 11
non-bold
ordinary cells white
learner/practice cells yellow
no decorative borders
```

- [x] **Step 7: Verify forecasting remains dormant**

No normal build should execute or expose forecasting/valuation.

Do not unhide:

```text
Model_Bear
Model_Base
Model_Bull
Scenario_Summary
```

Do not add a `forecast` or `value` CLI command.

---

## Definition of done

Step 9J.1 is complete only when all of the following are true:

1. The GOOGL workbook has been inspected read-only with a reproducible audit utility.
2. Its actual sheet/section evidence is documented without filling gaps from general knowledge.
3. The current Trainer has been compared against it.
4. Every required historical topic in this plan has a status in the gap matrix.
5. Forward/valuation features are explicitly separated from current Step 9 work.
6. The next historical implementation candidate is selected by the evidence-based priority rules.
7. The GOOGL workbook is byte-for-byte unchanged.
8. Active Trainer formulas, sheets, counts, Check behavior, and minimal presentation are unchanged.
9. `TARGET.md` remains unchanged by Cursor.
10. Full tests pass.
11. `RESULT.md` records the actual audit outcome and next Step 9 candidate.
12. Cursor performs no Git operations.
