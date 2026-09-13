# Step 9M.3B — Treatment-Conditioned Lease Interest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `3f12963f1563d08a99a665e3b90db81c54e88c9c` (`Step 9M.3A`). Implement only Step 9M.3B using red/green TDD. Do not begin G5 NCI attribution, G6 share-basis/per-share work, G7 reconciliation-policy changes, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Close G4 by carrying an explicit, source-grounded historical lease-interest series into the model and making net interest / NOPAT respond consistently to the learner's lease-liability operating-versus-financial treatment.

**Architecture:** Add one optional typed `HistoricalLeaseData` field to the model-only `StandardizedFinancials` contract. Filing reconciliation may populate it only from a complete, unambiguous full-axis series of reported `lease_interest_expense` note facts; provenance remains outside the model payload. `compute_anchor()` then uses the Step 9M.3A lease source descriptor plus the actual reformulation decisions: operating lease treatment removes disclosed lease interest from financing net interest, financial treatment leaves reported finance costs intact, and a mixed current/non-current lease treatment fails closed because one aggregate lease-interest disclosure cannot be allocated safely. The reference workbook must use the same source series and live classification cells so Python expected values, Excel formulas, and Check remain treatment-consistent.

**Tech Stack:** Python dataclasses, existing `StandardizedFinancials` / standardized JSON IO, filing reconciler/standardizer, lease source resolver, balance-sheet reformulation, `compute_anchor()`, `ReferenceModelBuilder`, semantic map / Check context, pytest, Fast Retailing benchmark audit.

**Spec:** `TARGET.md` source-grounded historical accounting / lease-analysis requirements plus G4 in `benchmark/fast_retailing/GAPS.md`. This step extends the existing G3 lease contract; it must not invent lease-interest data or change unrelated accounting policies.

## Why this is the next step

Step 9M.3A closes G3 and leaves Fast Retailing Stages 1–7 green with `expected_specs=312` and `lease_specs=18`. The remaining G4 defect is now isolated: lease liabilities can be reclassified between operating and financing, but the income side still treats all reported finance costs as financing regardless of that choice.

Fast Retailing has a complete reported note series already preserved in source-bound provenance:

```text
period       lease_interest_expense
FY2021       4,847
FY2022       4,757
FY2023       5,187
FY2024       6,507
FY2025       8,464
```

The primary FY2025 finance-cost line is `12,834` (expense magnitude represented as a negative statement line). Under the BAV reformulation:

```text
financial lease treatment:
    financing net interest includes lease interest

operating lease treatment:
    lease interest remains an operating cost
    therefore financing net interest excludes the disclosed lease-interest amount
```

Given the existing sign convention `reported_net_interest = -(interest_expense + interest_income)`, the operating-treatment adjustment is:

```text
analytical_net_interest = reported_net_interest - lease_interest_expense
```

No source number is rewritten. Net income remains reported net income; only its operating/financing decomposition changes.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve the filing-JSON extraction schema and all source/provenance/conflict evidence.
- Preserve the Step 9M.3A aggregate-or-split lease-liability source contract exactly.
- Do not promote the Note 17 lease-liability *balance* total (`513,501`) into the balance sheet; G3 continues to use `126,830 + 386,670 = 513,500` for the FY2025 diagnostic balance.
- `lease_interest_expense` is a separate reported note fact and may enter the model only through the explicit optional historical lease-data contract in this step.
- Never use `ABS()`, plugs, interpolation, proportional allocation, or inferred lease-interest values.
- Populate historical lease interest only when every modeled period has at least one `reported` observation and all repeated reported observations for that period agree numerically.
- `derived` supplemental facts do not satisfy the model input contract.
- If the lease-interest axis is missing, incomplete, or conflicting, leave `historical_lease=None`; existing companies without the disclosure remain model-equivalent.
- Preserve raw finance-cost / finance-income source lines exactly.
- Default supplied lease classification remains the existing operating treatment; do not change the judgment registry options.
- If all resolved lease-liability source rows are operating, exclude disclosed lease interest from financing net interest.
- If all resolved lease-liability source rows are financial, keep reported net interest unchanged.
- If a split lease source is classified partly operating and partly financial while only one aggregate lease-interest series is available, fail closed with a clear deterministic error; do not allocate the interest between current and non-current liabilities.
- No company/ticker-specific branches in production code.
- Do not add a new active formula family merely to display the disclosed lease-interest source. Active family orders remain `1..90`; expected component count should remain `312` for Fast Retailing unless an existing dynamic judgment mechanism changes it.
- Preserve G1/G1B/G2/G2B/G2C/G3 behavior and all G5–G7 behavior.
- Forecasting / valuation remain isolated.
- Cursor stops after implementation/tests and reports literal verification output; the user runs `checkpoint`.

---

### Task 1: Add the model-only historical lease-interest contract

**Files:**
- Modify: `core/data/interface.py`
- Modify: `core/data/__init__.py`
- Modify: `core/data/standardized_io.py`
- Test: `core/tests/test_filing_reconciler.py`
- Test: `core/tests/test_reference_integrity.py` only if that file already owns standardized round-trip assertions; otherwise keep round-trip tests in the existing standardized-IO test location.

**Interfaces:**

Add exactly:

```python
@dataclass
class HistoricalLeaseData:
    """Explicit reported historical lease-note inputs used by lease treatment."""

    lease_interest_expense: dict[date, float | None] = field(default_factory=dict)
```

Add to `StandardizedFinancials` as a new optional field **at the end of the dataclass's existing default fields** to minimize positional-constructor breakage:

```python
historical_lease: HistoricalLeaseData | None = None
```

Serialized model-only JSON key:

```json
"historical_lease": {
  "lease_interest_expense": {
    "2021-08-31": 4847.0,
    "2022-08-31": 4757.0
  }
}
```

or `null`.

- [ ] **Step 1: Add backward-compatible standardized-IO tests**

Require all of the following:

```python
# Existing payload with no historical_lease key
fin = standardized_from_payload(existing_payload)
assert fin.historical_lease is None

# Explicit null
payload["historical_lease"] = None
assert standardized_from_payload(payload).historical_lease is None

# Explicit series round-trip
fin.historical_lease = HistoricalLeaseData(
    lease_interest_expense={P1: 10.0, P2: 12.0}
)
payload = standardized_to_payload(fin)
assert payload["historical_lease"]["lease_interest_expense"] == {
    P1.isoformat(): 10.0,
    P2.isoformat(): 12.0,
}
restored = standardized_from_payload(payload)
assert restored.historical_lease == fin.historical_lease
```

Do not add source file/page/hash fields to `HistoricalLeaseData` or standardized JSON.

- [ ] **Step 2: Add malformed-shape rejection tests**

Require `ValueError` when `historical_lease` is non-null but not an object, or when `lease_interest_expense` is not an object. Preserve the existing permissive date/value conventions only to the extent already used by `HistoricalShareData`; do not add unrelated parser redesign in this checkpoint.

- [ ] **Step 3: Run the contract tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_reference_integrity.py -k "historical_lease or standardized_round" -v
```

If the repository's actual standardized round-trip tests live elsewhere, run that exact existing test file instead of moving tests gratuitously.

- [ ] **Step 4: Implement serializer/deserializer symmetry**

Mirror the existing `HistoricalShareData` helpers:

```python
def _serialize_historical_lease(
    lease: HistoricalLeaseData | None,
) -> dict[str, Any] | None:
    if lease is None:
        return None
    return {
        "lease_interest_expense": {
            _date_key(period): (None if value is None else float(value))
            for period, value in lease.lease_interest_expense.items()
        }
    }


def _deserialize_historical_lease(payload: object) -> HistoricalLeaseData | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError("historical_lease must be an object or null")
    series = payload.get("lease_interest_expense") or {}
    if not isinstance(series, dict):
        raise ValueError("historical_lease.lease_interest_expense must be an object")
    return HistoricalLeaseData(
        lease_interest_expense={
            _parse_date(period): (None if value is None else float(value))
            for period, value in series.items()
        }
    )
```

Wire the field into both `standardized_to_payload()` and `standardized_from_payload()`.

- [ ] **Step 5: Run Task 1 green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_reference_integrity.py -k "historical_lease or standardized_round" -v
```

---

### Task 2: Promote only a complete, unambiguous reported lease-interest axis

**Files:**
- Modify: `core/ingestion/filing_standardizer.py`
- Modify: `core/tests/test_filing_reconciler.py`
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Generated benchmark output expected to change only where legitimate:
  - `benchmark/fast_retailing/reconciled/standardized.json`

**Interfaces:**

Add private helper:

```python
def _historical_lease(
    reconciled: ReconciledCompanyData,
) -> HistoricalLeaseData | None:
    ...
```

`standardize_reconciled()` passes its result into `StandardizedFinancials(historical_lease=...)`.

- [ ] **Step 1: Add a complete-axis promotion test**

Build a two-period reconciled fixture with reported note observations:

```text
fact_type = lease_interest_expense
P1 = 10
P2 = 12
```

Repeated agreeing observations are allowed. Require:

```python
fin = standardize_reconciled(reconciled)
assert fin.historical_lease is not None
assert fin.historical_lease.lease_interest_expense == {P1: 10.0, P2: 12.0}
```

- [ ] **Step 2: Add the four fail-closed gating cases**

Require `historical_lease is None` for each independent case:

```text
one modeled period missing
only a derived lease_interest_expense fact for one period
two reported observations for the same period disagree numerically
only a differently named supplemental fact is present
```

Do not select a later filing when repeated supplemental lease-interest facts disagree: supplemental facts still have no presentation-role precedence contract.

- [ ] **Step 3: Add Fast Retailing source-axis assertions**

After generic reconciliation/standardization, require the exact full-axis reported series:

```python
assert fin.historical_lease is not None
assert fin.historical_lease.lease_interest_expense == {
    date(2021, 8, 31): 4847.0,
    date(2022, 8, 31): 4757.0,
    date(2023, 8, 31): 5187.0,
    date(2024, 8, 31): 6507.0,
    date(2025, 8, 31): 8464.0,
}
```

Also require the FY2025 provenance observation to remain a source-bound reported note fact from Note 17; the standardized field contains only model-relevant values, not provenance.

- [ ] **Step 4: Run the standardizer tests red**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_fast_retailing_benchmark.py -k "historical_lease or lease_interest" -v
```

- [ ] **Step 5: Implement conservative promotion**

Use only observations satisfying all of:

```text
obs.kind == "note"
obs.fact.status == "reported"
obs.fact.fact_type == "lease_interest_expense"
obs.fact.period == modeled period
```

For each modeled period:

```python
observations = [...]
if not observations:
    return None
distinct = {float(obs.fact.value) for obs in observations}
if len(distinct) != 1:
    return None
series[period] = next(iter(distinct))
```

Return `HistoricalLeaseData(lease_interest_expense=series)` only when every modeled period succeeds. Preserve reported signs exactly; do not call `abs()`.

- [ ] **Step 6: Regenerate generic Fast Retailing reconciliation output**

```bash
PYTHONPATH=. python -m core reconcile \
  benchmark/fast_retailing/extracted \
  --source-root benchmark/fast_retailing/source \
  -o /tmp/fr-9m3b
```

Compare:

```bash
diff -u benchmark/fast_retailing/reconciled/provenance.json /tmp/fr-9m3b/provenance.json
diff -u benchmark/fast_retailing/reconciled/conflicts.json /tmp/fr-9m3b/conflicts.json
diff -u benchmark/fast_retailing/reconciled/standardized.json /tmp/fr-9m3b/standardized.json
```

Expected:

```text
provenance.json: no change
conflicts.json: no change
standardized.json: only the new historical_lease model field is a legitimate change
```

If statement values, share data, labels, periods, or any existing standardized field changes, stop and investigate before copying the artifact.

Copy only the validated `/tmp/fr-9m3b/standardized.json` back to the benchmark canonical path.

- [ ] **Step 7: Run Task 2 green**

```bash
PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_fast_retailing_benchmark.py -k "historical_lease or lease_interest" -v
```

---

### Task 3: Make Python net interest / NOPAT treatment-conditioned

**Files:**
- Modify: `core/model/lease_liability.py`
- Modify: `core/model/financial_math.py`
- Modify: `core/tests/test_lease_liability.py`
- Modify: `core/tests/test_classification.py` only if an existing anchor-level lease-treatment fixture is already located there; do not duplicate fixtures unnecessarily.

**Interfaces:**

Break the existing runtime type-only cycle first. In `lease_liability.py`, change the `AnchorMetrics` import to `TYPE_CHECKING` and use a quoted annotation so `financial_math.py` can safely import lease-source helpers.

Add:

```python
class InconsistentLeaseTreatmentError(ValueError):
    """Resolved lease rows do not share one supported operating/financial treatment."""


def lease_liability_treatment(
    financials: StandardizedFinancials,
    reformulation: BalanceSheetReformulation,
) -> str | None:
    """Return 'operating', 'financial', or None; raise for mixed/unsupported treatment."""
```

Contract:

```text
no usable lease source -> None
all source decisions == Operating Long-Term Liability -> "operating"
all source decisions == Financial Liability -> "financial"
mixed operating/financial -> InconsistentLeaseTreatmentError
any other category on a resolved lease source -> InconsistentLeaseTreatmentError
```

- [ ] **Step 1: Add treatment-resolution tests for aggregate and split sources**

Require:

```text
one aggregate lease row, supplied operating default -> operating
one aggregate overridden financial -> financial
current + non-current both operating -> operating
current + non-current both financial -> financial
split one operating / one financial -> raises InconsistentLeaseTreatmentError
```

Use `reformulate_balance_sheet()` plus normal override selectors so the test exercises the production decision objects, not a fabricated category list.

- [ ] **Step 2: Add anchor math tests with explicit lease-interest data**

For a small two-period fixture with:

```text
reported net interest before lease adjustment = 20 each period
reported lease interest = 5 each period
numeric tax rate = 20%
```

require:

```python
operating = compute_anchor(fin, periods)
assert operating.historical.net_interest == [15.0, 15.0]

financial = compute_anchor(
    fin,
    periods,
    classification_overrides={...all lease source identities...: "Financial Liability"},
)
assert financial.historical.net_interest == [20.0, 20.0]

# After-tax financing interest / NOPAT difference is the after-tax lease interest.
assert financial.historical.net_interest_after_tax[1] - operating.historical.net_interest_after_tax[1] == pytest.approx(4.0)
assert financial.historical.nopat[1] - operating.historical.nopat[1] == pytest.approx(4.0)
```

Use existing sign conventions in the fixture; do not reverse statement signs merely to obtain those values.

- [ ] **Step 3: Add missing-data backward-compatibility regression**

For the same lease-liability fixture with `historical_lease=None`, require `compute_anchor()` to produce the pre-9M.3B reported-net-interest behavior under both supplied and alternative balance-sheet classification. This preserves companies that do not disclose a usable lease-interest split.

- [ ] **Step 4: Add incomplete explicit series failure**

If `historical_lease` is explicitly present but one modeled period is absent/`None`, `compute_anchor()` must fail with the repository's existing historical missing-value error rather than treating the missing lease interest as zero.

- [ ] **Step 5: Run Python treatment tests red**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py -k "lease_treatment or lease_interest or mixed" -v
```

- [ ] **Step 6: Implement the minimal treatment helper**

Use the exact Step 9M.3A source descriptor:

```python
source = resolve_lease_liability_source(financials)
if source is None:
    return None
categories = {reformulation.decisions[idx].category for idx in source.indices}
if categories == {"Operating Long-Term Liability"}:
    return "operating"
if categories == {"Financial Liability"}:
    return "financial"
raise InconsistentLeaseTreatmentError(...)
```

Do not infer treatment from labels. Do not allocate aggregate interest by current/non-current balance weights.

- [ ] **Step 7: Implement treatment-conditioned net interest in `compute_anchor()`**

Keep a local reported series first:

```python
reported_net_int = [-(ie + ii) for ie, ii in zip(int_exp, int_inc)]
```

If `fin.historical_lease is None`, use `reported_net_int` unchanged.

If it is present, require a complete numeric modeled-period `lease_interest_expense` series. Resolve lease treatment from the already-built `reform`:

```python
if treatment == "operating":
    net_int = [reported - lease for reported, lease in zip(reported_net_int, lease_interest)]
elif treatment == "financial":
    net_int = list(reported_net_int)
elif treatment is None:
    net_int = list(reported_net_int)
```

Then feed that `net_int` through the **existing** effective-tax, after-tax-interest, NOPAT, cost-of-debt, Spread, FLEV, and decomposed-ROE calculations. Do not add a second DuPont engine.

- [ ] **Step 8: Run Task 3 green plus existing lease/classification regressions**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py core/tests/test_classification.py -k "lease or net_interest or nopat" -v
```

---

### Task 4: Make the reference workbook use the same disclosed lease interest and live treatment

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/tests/test_lease_liability.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify `core/trainer/check_context.py` only if required by a failing dynamic-Check regression; standardized payload round-trip should normally carry the new field automatically.

**Interfaces:**
- No new active semantic component family.
- Existing families `net_interest_fy`, `net_interest_after_tax_fy`, `nopat_fy`, and downstream historical families remain authoritative.
- Existing lease judgment cells in `Accounting Judgment` remain the learner treatment controls.

- [ ] **Step 1: Add a visible but non-practice supplemental source row**

When `fin.historical_lease` exists, the Income Statement source sheet must preserve the disclosed note input in a clearly separated supplemental section rather than hard-coding it inside formulas. Require a layout equivalent to:

```text
[existing primary income-statement rows]

SUPPLEMENTAL DISCLOSURES
Lease interest expense (reported note)     4,847  4,757  ...  8,464
```

Record its row in `self.rowmap` under a stable internal key such as:

```text
supplemental_lease_interest_expense_row
```

This row is populated/trusted source context, not a yellow practice cell and not a new formula family.

Companies with `historical_lease=None` get no extra source row and retain byte/structure behavior except for unavoidable unrelated metadata timestamps if any; tests should compare semantics rather than volatile ZIP metadata.

- [ ] **Step 2: Add the disclosed lease-interest context link in Condensed Financials**

When available, add a non-practice row immediately after the existing Interest Income row:

```text
Lease Interest Expense (disclosed)
```

Each period cell links to the supplemental source row on `Income Statement`. Store its row in the local `row_nums` mapping so the net-interest formula never embeds numeric constants.

- [ ] **Step 3: Record live classification-row identities while building the balance-sheet classification table**

During the existing classification loop, retain a private mapping:

```python
classification_row_by_identity[line_identity(item).key()] = row
```

Use `resolve_lease_liability_source(self.fin)` to obtain the exact aggregate/split source items and indices, then map those identities to the corresponding live classification cells in column B.

Do not search for rows by display label; Fast Retailing legitimately has two `Lease liabilities` rows.

- [ ] **Step 4: Add formula tests for operating, financial, and mixed split treatment**

For a split two-period fixture with historical lease interest, require the `net_interest_fy` formula to reference:

```text
reported Interest Expense cell
reported Interest Income cell
Lease Interest Expense (disclosed) row
both exact lease classification cells
```

Semantics must be:

```text
all lease rows operating -> subtract disclosed lease interest
all lease rows financial -> subtract zero
mixed/unsupported -> NA() in Excel rather than silently selecting either treatment
```

For one aggregate lease source, require the same rule using its one classification cell.

For `historical_lease=None`, require the old formula exactly:

```text
=-(Interest Expense + Interest Income)
```

- [ ] **Step 5: Implement one live adjustment expression**

Construct the Excel adjustment from the source descriptor and classification rows. Equivalent semantics for a split source:

```excel
=-(<interest expense>+<interest income>)
 -IF(
      AND(<lease class 1>="Operating Long-Term Liability",
          <lease class 2>="Operating Long-Term Liability"),
      <disclosed lease interest>,
      IF(
         AND(<lease class 1>="Financial Liability",
             <lease class 2>="Financial Liability"),
         0,
         NA()
      )
   )
```

Do not hard-code Fast Retailing row numbers or values. The aggregate-source path uses the same structure with one classification cell.

- [ ] **Step 6: Add live Check treatment-switch regression**

Build a Trainer/Answer Key from a split fixture with explicit historical lease interest.

1. Fill all active practice formulas under the supplied operating lease treatment and require `incorrect == 0`, `blank == 0`.
2. Set **both** lease judgment choices to `Financial Liability`, recompute Check context through the existing treatment-aware path, fill the current expected formulas, and require `incorrect == 0`, `blank == 0`.
3. Confirm raw lease-liability diagnostic values are unchanged by the treatment switch.
4. Confirm Net Debt/NOA and Net Interest/NOPAT expected values change in the directions specified by Task 3.

- [ ] **Step 7: Add mixed-treatment fail-closed regression**

Set one Fast Retailing-style split lease row to `Financial Liability` and leave the other operating. Require Check/model recomputation to reject the configuration with `InconsistentLeaseTreatmentError`; the workbook net-interest formula itself must resolve to `NA()` under Excel semantics. Do not auto-synchronize or silently choose one row's treatment in this checkpoint.

- [ ] **Step 8: Run Task 4 green**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py core/tests/test_reference_integrity.py -k "lease_interest or lease_treatment or split_lease or net_interest" -v
```

---

### Task 5: Close G4 on the canonical Fast Retailing benchmark

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Modify: `scripts/audit_fast_retailing_benchmark.py` only if the existing output needs an explicit G4 treatment probe; do not change unrelated audit stages.
- Modify generated benchmark docs after measured verification:
  - `benchmark/fast_retailing/BASELINE.md`
  - `benchmark/fast_retailing/GAPS.md`
  - `RESULT.md`

**Interfaces:**
- Canonical Fast Retailing standardized input now legitimately contains `historical_lease`.
- Active component families/count remain the existing ones; this step changes expected values/formulas, not practice-surface breadth.

- [ ] **Step 1: Add canonical lease-interest source assertions**

Require the reconciled standardized payload to contain the exact five-period series from Task 2, while provenance still contains source file/page/hash for each observation.

Require:

```text
FY2025 lease interest = 8,464
FY2025 split BS diagnostic lease liability = 513,500
FY2025 Note 17 lease-liability total = 513,501
```

These are three distinct facts/contracts; none may overwrite another.

- [ ] **Step 2: Add default operating-treatment anchor assertions**

Compute the canonical anchor with no overrides. Independently derive the pre-adjustment reported net-interest series from the primary finance-cost / finance-income lines. For every period require:

```python
anchor.historical.net_interest[i] == pytest.approx(
    reported_net_interest[i] - lease_interest[i]
)
```

For periods with numeric ETR, require the corresponding after-tax/NOPAT relationship.

- [ ] **Step 3: Add all-financial lease override assertions**

Resolve both Fast Retailing lease source identities and override both to `Financial Liability`. Require:

```text
net interest returns to reported primary-statement net interest
lease diagnostic amount remains unchanged
Net Debt increases versus supplied operating treatment
NOA increases versus supplied operating treatment
NOPAT increases by after-tax lease interest versus supplied operating treatment (for numeric ETR periods)
Actual reported net income remains unchanged
```

Do not assert a G5 parent/NCI ROE policy here.

- [ ] **Step 4: Add canonical mixed-treatment rejection**

Override only one of the two lease rows to financial and require `InconsistentLeaseTreatmentError`. This proves the aggregate Note 17 interest amount is never arbitrarily allocated between current and non-current lease maturities.

- [ ] **Step 5: Add Fast Retailing workbook / Check assertions**

Require the default build and filled Check to continue passing with:

```text
lease_specs = 18
expected_specs = 312
blank Check total = 312
filled Check correct = 312
```

No new active component family is added by the disclosed lease-interest context row.

Also exercise the all-financial lease judgment selection through the existing Check-context path and require treatment-consistent formulas/expected values rather than merely testing Python math.

- [ ] **Step 6: Run focused canonical tests**

```bash
PYTHONPATH=. pytest \
  core/tests/test_filing_reconciler.py \
  core/tests/test_lease_liability.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Record the literal pass count; do not pre-fill it in docs.

- [ ] **Step 7: Run the staged Fast Retailing audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require Stages 1–7 to remain green. If a newly treatment-conditioned formula exposes an execution defect directly caused by this G4 implementation, fix only that defect. Do not begin G5–G7.

---

### Task 6: Regression, artifact, and documentation gate

**Files:**
- Modify: `benchmark/fast_retailing/GAPS.md`
- Modify: `benchmark/fast_retailing/BASELINE.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status line only after all final verification passes.

- [ ] **Step 1: Run the full historical suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the literal result.

- [ ] **Step 2: Verify source/provenance/conflict immutability**

```bash
git diff -- \
  benchmark/fast_retailing/source \
  benchmark/fast_retailing/extracted \
  benchmark/fast_retailing/reconciled/provenance.json \
  benchmark/fast_retailing/reconciled/conflicts.json
```

Expected: no output.

The only canonical reconciliation artifact permitted to change in this step is `benchmark/fast_retailing/reconciled/standardized.json`, and its only intended semantic addition is the model-only `historical_lease` field.

Re-check counts:

```text
primary-statement overlap conflicts = 3
supplemental conflicts = 3
```

- [ ] **Step 3: Verify unrelated workbook fixtures do not drift**

```bash
git diff -- \
  example/DEMO_HK_Trainer.xlsx \
  example/DEMO_HK_Answer_Key.xlsx \
  example/DEMO_HK_Standardized.json
```

Expected: no output. The demo lacks the new explicit historical lease-interest input and therefore must retain its pre-Step-9M.3B model behavior.

- [ ] **Step 4: Verify forecast/valuation isolation and family orders**

Run the existing historical exit-gate / scenario-isolation regressions. Require:

```text
normal historical build does not call scenario/forecast/valuation paths
active family orders remain 1..90
Fast Retailing expected_specs remains 312
```

- [ ] **Step 5: Update GAPS.md from measured evidence**

Mark G4 closed only if all treatment-source, Python, workbook, Check, and Fast Retailing tests pass. Document:

```text
complete reported lease-interest input contract
operating treatment excludes disclosed lease interest from financing net interest
financial treatment retains reported financing net interest
split mixed treatment fails closed because interest cannot be allocated safely
missing/incomplete/conflicting disclosure leaves historical_lease absent and preserves legacy behavior
no source mutation / no note-balance substitution
```

Keep G5–G7 open.

- [ ] **Step 6: Update BASELINE.md and RESULT.md with literal output**

Record, without guessing:

```text
focused test count
full test count
Stages 1–7 result
lease specs / expected specs
blank / filled Check counts
Fast Retailing historical lease-interest axis present: yes/no
operating-vs-financial treatment probe: pass/fail
mixed-treatment fail-closed probe: pass/fail
standardized artifact change limited to historical_lease: yes/no
source/provenance/conflicts unchanged: yes/no
G4 status
G5–G7 status
forecast/valuation isolation
```

- [ ] **Step 7: Final behavioral audit**

Run again after doc/status changes:

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
PYTHONPATH=. pytest core/tests/ -q
```

Do not claim completion from an earlier run.

- [ ] **Step 8: Mark Step 9M.3B complete and stop**

Only after fresh final verification, add a compact status line at the top of `IMPLEMENTATION.md` using actual counts/results.

Do not implement G5, G6, or G7. Return the implementation summary to the user so they can run `checkpoint`; ChatGPT should review that checkpoint and choose the next substantive historical gap from measured evidence.
