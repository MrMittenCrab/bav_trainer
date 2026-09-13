# Step 9M.2D — Reporting-Unit Rounding Envelope for Reformulation Integrity

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `290361d34348c730293f3c7a339ff5332eba4626` (`Step 9M.2C`). Implement only Step 9M.2D using red/green TDD. Do not begin G3–G7 accounting-policy work, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Replace the fixed one-unit reformulation-detail tolerance with a mathematically bounded reporting-unit rounding envelope so rounded statement detail can reconcile to rounded published totals without plugs, while material omissions and classification errors still fail closed.

**Architecture:** Keep reported and reconciled source values immutable. `reformulate_balance_sheet()` continues to classify and sum detail exactly as today; only `check_reformulation_integrity()` changes its acceptance boundary. Derive separate asset, liability, and equity tolerances from the number of classified detail observations that contribute to each aggregate: if each displayed amount and its reported total can be rounded by at most half a reporting unit, the worst-case detail-vs-total difference is `0.5 * (detail_count + 1)`. The existing explicit `tolerance` remains a floor, not a replacement. Then rerun the real-company audit and stop at the first new blocker.

**Tech Stack:** Python, pytest, existing `StandardizedFinancials`, `BalanceSheetReformulation`, `reformulate_balance_sheet()`, `check_reformulation_integrity()`, `ReferenceModelBuilder`, Fast Retailing staged audit.

**Spec:** `TARGET.md` historical consistency/audit requirements plus the measured post-9M.2C `ReformulationIntegrityError` in `benchmark/fast_retailing/GAPS.md`. This is a bounded correction to the existing integrity policy; no new design document is required.

## Why this is the next step

Step 9M.2C proves every Fast Retailing non-subtotal balance-sheet row is now classifiable. The next failure is no longer classification; it is the integrity check comparing sums of independently rounded detail lines with independently rounded published totals.

The committed Fast Retailing evidence is systematic:

```text
period   asset detail gap   liability detail gap   equity gap
FY2021   -4                 -6                     +2
FY2022   -8                 -5                     -3
FY2023   -8                 -6                     -1
FY2024   -7                 -5                     -1
FY2025   -8                 -6                     -2
```

The standardized balance sheet contains **16 asset detail rows** and **13 liability detail rows**. Under integer reporting-unit rounding, the theoretical worst-case envelopes are therefore:

```text
assets:      0.5 * (16 + 1) = 8.5 reporting units
liabilities: 0.5 * (13 + 1) = 7.0 reporting units
equity bridge (NOA - Net Debt vs reported equity):
             0.5 * (16 + 13 + 1) = 15.0 reporting units
```

The observed Fast Retailing gaps sit inside those bounds. A fixed tolerance of `1.0` is appropriate for a single published identity such as `Assets = Liabilities + Equity`, but is too strict when many rounded detail observations are summed. Increasing the tolerance to a magic constant such as `8` would be company-specific and would scale poorly; changing source values or adding balancing plugs would violate the project’s source-grounding requirements.

This step therefore introduces a **count-derived rounding envelope**, not a Fast Retailing exception and not a balancing adjustment.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve the Step 9M.1.1 filing-JSON schema, source binding, provenance, and conflict semantics.
- Preserve all Fast Retailing source/extracted/reconciled values; do not edit `benchmark/fast_retailing/reconciled/standardized.json` to make integrity pass.
- Preserve Step 9M.2A Stage-3 balance-sheet identity policy exactly: `validate_balance_sheet()` accepts absolute `Assets - (Liabilities + Equity) <= 1.0` reporting unit and rejects larger residuals.
- Do not add balancing plugs, hidden residual rows, synthetic “rounding” line items, or source mutations.
- Do not weaken classification rules added in Steps 9M.2A–9M.2C.
- `check_reformulation_integrity()` must continue to fail on materially missing asset/liability detail even when the reported top-level balance sheet equation balances.
- Rounding tolerance is derived from detail count, never from ticker/company, observed Fast Retailing residuals, percentage-of-assets thresholds, or a hard-coded `8`/`10`-unit exception.
- Count only detail rows that actually contribute to the relevant reformulation side. `Equity` and `Exclude` rows do not count as asset or liability observations.
- Keep the public signature `check_reformulation_integrity(reform, periods, *, tolerance=DEFAULT_TOLERANCE)` unchanged.
- Existing explicit `tolerance` remains a minimum accepted tolerance; callers that request a larger tolerance retain that behavior.
- Preserve the three Fast Retailing primary-statement overlap conflicts and three supplemental conflicts.
- Preserve G3–G7 behavior. Do not aggregate split leases, alter lease-interest treatment, implement parent/NCI attribution, restate historical shares, or change cross-filing precedence in this checkpoint.
- No forecast/valuation/scenario activation.
- No new workbook formula family.
- Cursor stops after implementation/tests, records the first newly exposed audit blocker, and lets the user run `checkpoint`.

---

### Task 1: Codify the reporting-unit rounding envelope in focused integrity tests

**Files:**
- Modify: `core/tests/test_classification.py`
- Modify: `core/model/classification.py`

**Interfaces:**
- Existing production entry points remain:

```python
def reformulate_balance_sheet(
    fin: StandardizedFinancials,
    periods: list[date],
    *,
    overrides: dict[str, str] | None = None,
) -> BalanceSheetReformulation: ...


def check_reformulation_integrity(
    reform: BalanceSheetReformulation,
    periods: list[date],
    *,
    tolerance: float = DEFAULT_TOLERANCE,
) -> None: ...
```

- Add no new public API.
- A small private helper for count-derived tolerance is allowed.

- [ ] **Step 1: Add an asset-side rounding-envelope acceptance test**

Use four independently reported asset detail rows and one reported total. Four detail rows imply a rounding envelope of:

```text
0.5 * (4 + 1) = 2.5
```

Add a fixture/test equivalent to:

```python
def _asset_rounding_fin(total_assets: float) -> StandardizedFinancials:
    return StandardizedFinancials(
        ticker="ROUND-A",
        company_name="Rounded Assets",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Cash and cash equivalents", 10, 10),
            _li("Trade receivables", 10, 10),
            _li("Inventories", 10, 10),
            _li("Prepaid expenses", 10, 10),
            _li("Total assets", total_assets, total_assets, concept="total_assets"),
        ],
        cash_flow=[],
    )


def test_reformulation_integrity_accepts_count_bounded_asset_rounding():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_asset_rounding_fin(42), periods)
    assert reform.asset_detail_gap == (-2.0, -2.0)
    check_reformulation_integrity(reform, periods)
```

This must fail before the implementation because the current fixed `1.0` tolerance rejects a two-unit gap.

- [ ] **Step 2: Add the immediate outside-envelope rejection case**

Using the same four asset rows:

```python
def test_reformulation_integrity_rejects_asset_gap_above_rounding_envelope():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_asset_rounding_fin(43), periods)
    assert reform.asset_detail_gap == (-3.0, -3.0)
    with pytest.raises(ReformulationIntegrityError, match="asset-detail gap"):
        check_reformulation_integrity(reform, periods)
```

`3.0 > 2.5`, so it must remain a hard failure.

- [ ] **Step 3: Add liability-side boundary tests**

Create four liability detail rows whose labels are already supported by the classifier:

```text
Trade payables
Accrued expenses
Bank borrowings
Lease liabilities
```

Each is `10` in both periods. With `Total liabilities = 42`, require a `-2` liability-detail gap to pass. With `Total liabilities = 43`, require a `-3` gap to fail because the four-row envelope is `2.5`.

Use `concept="total_liabilities"` on the total row. Do not add Total Assets or Total Equity to this focused fixture so the test isolates the liability check.

- [ ] **Step 4: Add the equity-bridge rounding-envelope boundary test**

Create a fixture with two asset and two liability detail rows, no reported Total Assets / Total Liabilities, and a reported `Total equity` only. The four contributing asset/liability observations imply:

```text
0.5 * (2 + 2 + 1) = 2.5
```

Set detail values so `NOA - Net Debt = 20`.

Require:

```text
Total equity = 18  -> equity gap = +2 -> pass
Total equity = 17  -> equity gap = +3 -> fail
```

Use ordinary supported labels, for example:

```text
Trade receivables 10
Property, plant and equipment 20
Trade payables 5
Bank borrowings 5
```

The implied equity is `10 + 20 - 5 - 5 = 20`.

- [ ] **Step 5: Preserve the existing material-omission regression**

Do not change `test_reformulation_detects_equal_asset_liability_omissions()` except, if necessary, strengthen it to assert the omission remains far outside the new count-derived envelope.

Its missing asset and liability detail are `30` each. The test must continue to raise `ReformulationIntegrityError`; this is the key proof that the new policy is not “ignore detail-to-total gaps.”

- [ ] **Step 6: Run the focused tests red**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py \
  -k "rounding_envelope or equal_asset_liability_omissions" -v
```

Expected before implementation:
- the new `-2` acceptance cases fail under the fixed one-unit tolerance;
- the `-3` rejection cases and the 30-unit omission regression remain failures as intended.

---

### Task 2: Implement count-derived integrity tolerances without changing reformulation arithmetic

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

**Interfaces:**
- `BalanceSheetReformulation` shape remains unchanged.
- Derive counts from `reform.decisions`; do not add source/company metadata to the reformulation object.

- [ ] **Step 1: Add explicit side-category constants near the integrity logic**

Use the existing category names exactly:

```python
_ASSET_REFORMULATION_CATEGORIES = frozenset(
    {
        "Operating Working Capital Asset",
        "Operating Long-Term Asset",
        "Financial Asset",
    }
)

_LIABILITY_REFORMULATION_CATEGORIES = frozenset(
    {
        "Operating Working Capital Liability",
        "Operating Long-Term Liability",
        "Financial Liability",
    }
)
```

Do not include `Equity` or `Exclude`.

- [ ] **Step 2: Add one private rounding-envelope helper**

Implement:

```python
def _reporting_rounding_tolerance(
    detail_count: int,
    *,
    base_tolerance: float,
) -> float:
    if detail_count < 0:
        raise ValueError("detail_count must be non-negative")
    if base_tolerance < 0:
        raise ValueError("base_tolerance must be non-negative")
    return max(base_tolerance, 0.5 * (detail_count + 1))
```

Rationale encoded by the formula:
- each of `detail_count` displayed detail values may differ from its unrounded value by at most `0.5` reporting unit;
- the independently displayed total may differ by another `0.5`;
- therefore `abs(sum(displayed_details) - displayed_total)` can legitimately reach `0.5 * (detail_count + 1)`.

Do not round the derived tolerance to an integer and do not inspect Fast Retailing residuals.

- [ ] **Step 3: Derive counts from actual contributing decisions**

Inside `check_reformulation_integrity()` compute:

```python
asset_detail_count = sum(
    1
    for decision in reform.decisions.values()
    if decision.category in _ASSET_REFORMULATION_CATEGORIES
)
liability_detail_count = sum(
    1
    for decision in reform.decisions.values()
    if decision.category in _LIABILITY_REFORMULATION_CATEGORIES
)

asset_tolerance = _reporting_rounding_tolerance(
    asset_detail_count,
    base_tolerance=tolerance,
)
liability_tolerance = _reporting_rounding_tolerance(
    liability_detail_count,
    base_tolerance=tolerance,
)
equity_tolerance = _reporting_rounding_tolerance(
    asset_detail_count + liability_detail_count,
    base_tolerance=tolerance,
)
```

Use those three tolerances only for their corresponding integrity checks.

- [ ] **Step 4: Replace only the comparison thresholds**

The existing gap calculations remain untouched. Change only:

```text
abs(asset_detail_gap) > tolerance
abs(liability_detail_gap) > tolerance
abs(equity_gap) > tolerance
```

to use `asset_tolerance`, `liability_tolerance`, and `equity_tolerance` respectively.

Keep failure messages’ existing gap text. Add the applicable tolerance to each failure message so future audits are self-diagnosing, for example:

```text
2025-08-31: asset-detail gap=-12 (classified assets vs Total Assets; allowed rounding envelope=8.5)
```

Do not change values, category totals, NOA, Net Debt, or implied equity.

- [ ] **Step 5: Preserve explicit caller tolerance as a floor**

Add a focused test showing that a caller-supplied larger tolerance still works:

```python
def test_reformulation_integrity_explicit_tolerance_remains_floor():
    periods = [P1, P2]
    reform = reformulate_balance_sheet(_asset_rounding_fin(46), periods)
    assert reform.asset_detail_gap == (-6.0, -6.0)
    with pytest.raises(ReformulationIntegrityError):
        check_reformulation_integrity(reform, periods)
    check_reformulation_integrity(reform, periods, tolerance=6.0)
```

This prevents the new helper from unexpectedly overriding an explicit caller contract.

- [ ] **Step 6: Run Task 1–2 tests green**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py \
  -k "rounding_envelope or equal_asset_liability_omissions or explicit_tolerance" -v
```

Expected: all selected tests pass.

- [ ] **Step 7: Run the full classification test file**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
```

Expected: all pass, including Steps 9M.2A–9M.2C classification/judgment regressions.

---

### Task 3: Prove Fast Retailing fits the mathematical envelope without source changes

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Read only: `benchmark/fast_retailing/reconciled/standardized.json`
- Read only: `benchmark/fast_retailing/reconciled/provenance.json`
- Read only: `benchmark/fast_retailing/reconciled/conflicts.json`

**Interfaces:**
- Use existing standardized loader, `reformulate_balance_sheet()`, and `check_reformulation_integrity()`.
- Do not create a Fast Retailing-specific tolerance API.

- [ ] **Step 1: Add exact committed gap assertions before calling integrity check**

For the five Fast Retailing periods require the current documentary/reformulation gaps to remain exactly:

```python
assert reform.asset_detail_gap == (-4.0, -8.0, -8.0, -7.0, -8.0)
assert reform.liability_detail_gap == (-6.0, -5.0, -6.0, -5.0, -6.0)
assert reform.equity_gap == (2.0, -3.0, -1.0, -1.0, -2.0)
```

These assertions prove Step 9M.2D accepts the existing reported arithmetic rather than altering it.

- [ ] **Step 2: Assert the contributing detail inventory is stable**

From `reform.decisions`, count categories using the same semantic sets as production and require:

```text
asset detail count = 16
liability detail count = 13
```

Do not count Equity or Exclude rows.

This yields theoretical envelopes:

```text
asset = 8.5
liability = 7.0
equity bridge = 15.0
```

Do not hard-code those tolerances in production code; they are acceptance evidence for this fixture only.

- [ ] **Step 3: Require Fast Retailing reformulation integrity to pass without overrides**

```python
check_reformulation_integrity(reform, periods)
```

No `classificationOverrides`, plugs, or fixture edits are allowed.

- [ ] **Step 4: Run Fast Retailing acceptance tests**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

Expected after Task 2: the previous Stage-4 integrity condition is accepted by the generic rule while source/reconciled values stay identical.

---

### Task 4: Re-run the staged real-company audit and stop at the first newly exposed blocker

**Files:**
- Modify only tests/docs required by the measured result.
- Read: `scripts/audit_fast_retailing_benchmark.py`
- Do not change benchmark source/extracted/reconciled JSON.

**Interfaces:**
- Existing `run_audit()` remains the integration gate.

- [ ] **Step 1: Update the audit-stage regression**

In `core/tests/test_fast_retailing_benchmark.py`, require:

```python
stages = {stage.name: stage for stage in run_audit().stages}
assert stages["1_source_fixture_load"].status == "pass"
assert stages["2_identity_validation"].status == "pass"
assert stages["3_reconciliation"].status == "pass"
```

For Stage 4:
- it must no longer fail with the Step 9M.2C classified-detail `ReformulationIntegrityError`;
- if Stage 4 passes, allow Stage 5+ to expose the next issue;
- if Stage 4 fails for a different reason, record it literally and stop.

Do not pre-assume workbook/Check success.

- [ ] **Step 2: Run the staged audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Capture exactly:

```text
first failing stage
exception class
full exception message
whether ReferenceModelBuilder completed
whether workbook generation was reached
whether blank Check was reached
whether filled Check was reached
```

- [ ] **Step 3: Stop instead of fixing the newly exposed issue**

If the audit reveals a new blocker, do not fix it in Step 9M.2D unless it is demonstrably an implementation error in the rounding-envelope logic above.

In particular, do not opportunistically begin:

```text
G3 split-lease aggregation
G4 lease-interest treatment conditioning
G5 parent/NCI attribution
G6 share-basis restatement/per-share activation
G7 reconciliation-precedence changes
```

The next checkpoint must be selected from measured post-9M.2D evidence.

---

### Task 5: Preserve source, workbook, and historical-product isolation

**Files:**
- Test: `core/tests/test_reference_integrity.py`
- Test: `core/tests/test_fast_retailing_benchmark.py`
- Read only: benchmark and example artifacts

- [ ] **Step 1: Prove classification decisions are unchanged**

The Step 9M.2D production diff must not modify `classify_balance_sheet_line()` behavior. Run the existing focused classifier/judgment tests covering:

```text
G2 generic financial-instrument judgments
G2B residual other-balance judgments
G2C deterministic tax/provision/equity concepts
lease / associate / pension / short-term investment judgments
unknown-row fail-closed behavior
```

Use:

```bash
PYTHONPATH=. pytest \
  core/tests/test_classification.py \
  core/tests/test_reference_integrity.py \
  -q
```

- [ ] **Step 2: Prove source/reconciliation artifacts did not drift**

Run:

```bash
git diff -- \
  benchmark/fast_retailing/source \
  benchmark/fast_retailing/extracted \
  benchmark/fast_retailing/reconciled/standardized.json \
  benchmark/fast_retailing/reconciled/provenance.json \
  benchmark/fast_retailing/reconciled/conflicts.json
```

Expected: no output.

Also confirm the committed conflict counts remain:

```text
primary-statement overlap conflicts = 3
supplemental conflicts = 3
```

- [ ] **Step 3: Prove unrelated example workbook fixtures did not drift**

```bash
git diff -- \
  example/DEMO_HK_Trainer.xlsx \
  example/DEMO_HK_Answer_Key.xlsx \
  example/DEMO_HK_Standardized.json
```

Expected: no output.

- [ ] **Step 4: Verify forecast/valuation isolation**

Run the existing normal-v1 isolation regression used in Steps 9M.2A–9M.2C. Require:

```text
normal historical build does not call scenario execution
active historical family orders remain 1..90
no DCF/residual-income/valuation activation
```

Do not add a new formula family for this integrity-policy change.

---

### Task 6: Update the measured gap record and final verification evidence

**Files:**
- Modify: `benchmark/fast_retailing/GAPS.md`
- Modify: `benchmark/fast_retailing/BASELINE.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status line only after verification

- [ ] **Step 1: Record the integrity-policy resolution separately from G1**

Add a new closed subsection, for example:

```text
G1B — Rounded detail-to-total accumulation — CLOSED in Step 9M.2D
```

Record:
- the old fixed `1.0` reformulation-detail threshold;
- the count-derived formula `max(base_tolerance, 0.5 * (detail_count + 1))`;
- separate asset/liability/equity contributor counts;
- no source mutation or balancing plugs;
- the existing top-level `Assets = Liabilities + Equity <= 1.0` G1 rule remains unchanged.

Do not mark G3–G7 closed.

- [ ] **Step 2: Replace the post-9M.2C blocker section with literal audit evidence**

Use the exact final audit result from Task 4. If all stages pass, state that explicitly and list every reached stage. If another blocker appears, record its exact stage/class/message without proposing its fix inside the evidence section.

- [ ] **Step 3: Update `BASELINE.md` from the regenerated audit**

Run the existing audit script if it writes the baseline automatically; otherwise copy only literal stage output. Do not edit benchmark numerical source facts.

- [ ] **Step 4: Run the focused Step 9M.2D suite**

```bash
PYTHONPATH=. pytest \
  core/tests/test_classification.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Record the exact pass count.

- [ ] **Step 5: Run the full historical regression suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the exact pass count.

- [ ] **Step 6: Re-run source/workbook no-drift checks**

Repeat Task 5 Steps 2–3 after all documentation/audit generation. Source/extracted/reconciled JSON and example workbook files must remain unchanged.

- [ ] **Step 7: Run the Fast Retailing audit as the final behavioral gate**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require the same stage/result as Task 4. If the first blocker changes without code/data changes, stop and investigate nondeterminism instead of recording either result.

- [ ] **Step 8: Mark Step 9M.2D complete only with fresh evidence**

Only after Steps 4–7 succeed, add a compact status line at the top of this file and update `RESULT.md` with:

```text
focused test count
full core test count
Fast Retailing Stage 1–4 status
first newly exposed blocker/stage, if any
asset/liability detail counts and rounding envelopes
source/reconciliation artifact drift: none
conflict counts: 3 / 3
family orders: 1..90
forecast/valuation isolation: pass
```

Do not pre-state counts before the commands run.

- [ ] **Step 9: Stop**

Do not implement the next blocker. Return the implementation/test summary so the user can run `checkpoint`; ChatGPT should then review that checkpoint and select the next step from measured evidence.
