# Step 9L.1 — Lease-Liability Diagnostics + Judgment-Selector Hardening

**Status: COMPLETE** — `identity:` judgment selectors; aggregate lease-liability families 87–90 on ALT DuPont; surfaces 74/312, 78/332, 82/346, 90/384; manufacturer 74/311; GOOGL provenance repaired; no ROU/capex. See `RESULT.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md` first, then `docs/GOOGL_HISTORICAL_REFERENCE.md`, then this plan in full. The accepted implementation base is commit `e81a04837176562c721f3b04f81e21a1bb381a0f` (`Step 9K.1`, fixed-asset diagnostics complete). Implement only Step 9L.1 below using red/green TDD. This remains **Step 9 historical convergence**. Do not begin forecasting, valuation, scenarios, or forward-model activation. Do not commit or push; the user owns the checkpoint commit.

**Goal:** Harden guided classification so duplicate concepts can be addressed row-by-row, then add a conservative historical lease-liability diagnostic layer that teaches lease-balance intensity and change without inventing ROU assets, lease payments, discount rates, or lease accounting schedules that are not explicitly supplied.

**Architecture:** First add an exact `identity:` selector for system-generated judgment cases while retaining user-facing `concept:` and `label:` assumption selectors. Then add an optional `LeaseLiabilitySeries` driven only by one uniquely resolvable aggregate lease-liability source line plus existing Revenue. If a company reports split current/non-current lease-liability rows rather than one aggregate balance, keep the judgment cases but omit the new diagnostic module in this checkpoint instead of silently summing lines. Append four semantic families, orders `87..90`, to `ALT DuPont` so the historical model stays integrated.

**Tech Stack:** Python, dataclasses, pytest, openpyxl, existing `LineIdentity`, `resolve_line`, `required_period_value`, `ratio_or_na`, `ReferenceModelBuilder`, component catalogs, `historical_expected`, `check_workbook`, trusted-workbook validation, and the existing Accounting Judgment flow.

**Spec:** `TARGET.md` sections `Historical accounting competence to cover`, `Interpretation is part of the product`, `Reference workbook for historical convergence`, and `Step 9 roadmap before forecasting`; plus the lease Priority A item in `docs/GOOGL_HISTORICAL_REFERENCE.md`.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- `example/GOOGL_Demo_Integrated_Financials.xlsx` remains read-only.
- Remain in Step 9. Forecasting, valuation, scenarios, guidance/consensus, and investment conclusions remain deferred.
- Preserve Step 9I.1 fresh-workbook style: Aptos Narrow 11, white/yellow only, no decorative borders; Check green/red remains functional feedback only.
- Preserve Trainer / Answer Key / Check separation and trusted-cell validation.
- Preserve non-financial-company scope.
- Preserve source signs. No `ABS()` or `IFERROR(...,0)` in practice formulas.
- Do not infer an ROU asset from a lease liability.
- Do not infer lease payments, interest accretion, discount rate, maturity profile, or lease expense.
- Do not build a lease amortization schedule.
- Do not aggregate split current/non-current lease-liability rows in this checkpoint.
- A unique aggregate lease-liability line is sufficient for diagnostics; split rows remain judgment-only until an explicit aggregation contract exists.
- Missing optional module inputs omit the module. A uniquely resolved line with a missing modeled-period value fails closed through `MissingHistoricalValueError`.
- Do not add a new visible worksheet; integrate on `ALT DuPont`.
- Cursor must not commit, push, reset, rebase, merge, or delete branches.

---

### Task 1: Repair GOOGL-reference provenance before adding another module

**Files:**
- Modify: `docs/GOOGL_HISTORICAL_REFERENCE.md`
- Modify: `core/tests/test_reference_workbook_audit.py`

**Interfaces:**
- Produces a reference document where the `GOOGL evidence` column contains only evidence actually observed in the GOOGL workbook.

- [ ] **Step 1: Write regression assertions for the fixed-asset row**

Require the document to retain actual GOOGL evidence equivalent to:

```text
BS Property and equipment
CF depreciation
CF Purchases of property and equipment
```

and require the Trainer column, not the GOOGL column, to mention the Step 9K.1 `FIXED-ASSET INTENSITY CONTEXT` implementation.

Also assert that the document does not permanently present the old canonical Answer-Key SHA as if it were still current after canonical workbooks are regenerated.

- [ ] **Step 2: Run the focused audit test red**

```bash
PYTHONPATH=. pytest core/tests/test_reference_workbook_audit.py -v
```

- [ ] **Step 3: Correct the document**

Remove the stale persistent line:

```text
Canonical Answer Key SHA-256: ...
```

Keep the immutable GOOGL reference hash.

Restore the fixed-asset `GOOGL evidence` cell to the actual source evidence observed in GOOGL. Keep the Step 9K.1 implementation description under `Current Trainer` / `Training adaptation`.

Do not alter the Priority A ordering except where later tasks in this plan explicitly update the lease row.

- [ ] **Step 4: Run the focused test green**

```bash
PYTHONPATH=. pytest core/tests/test_reference_workbook_audit.py -v
```

---

### Task 2: Add exact `identity:` selectors for generated classification judgments

**Files:**
- Modify: `core/model/classification.py`
- Modify: `core/model/judgment.py`
- Test: `core/tests/test_classification.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Extends classification-override selectors with `identity:<LineIdentity.key()>`.
- Existing `concept:` and `label:` selectors remain supported for assumptions/backward compatibility.
- System-generated `JudgmentCase.override_selector` becomes exact-row identity.

- [ ] **Step 1: Write a duplicate-concept lease regression**

Create two BS lines with distinct labels but the same concept:

```python
LineItem(
    label="Current lease liabilities",
    concept="lease_liability",
    ...,
)
LineItem(
    label="Non-current lease liabilities",
    concept="lease_liability",
    ...,
)
```

Prove `validate_statement_identities()` accepts them because their full identities differ.

Then require `classification_judgment_cases()` to produce two distinct selectors beginning with `identity:`.

- [ ] **Step 2: Prove the existing selector is currently ambiguous**

Add a regression showing that one broad manual selector:

```text
concept:lease_liability
```

still raises `AmbiguousClassificationOverrideError` when it matches both rows.

This behavior must remain; do not silently choose one row.

- [ ] **Step 3: Implement `identity:` parsing**

Extend `_parse_override_selector()` so it returns one of:

```text
identity
concept
label
```

For `identity:` preserve the exact identity payload after trimming outer whitespace. Do not case-normalize concept IDs inside the serialized identity beyond what `line_identity()` already does.

- [ ] **Step 4: Implement exact identity resolution**

In `resolve_classification_overrides()`:

```python
if kind == "identity":
    matches = [
        item
        for item in detail_items
        if line_identity(item).key() == value
    ]
```

Require exactly one match when present.

- zero matches: preserve existing stale-override semantics and ignore;
- more than one match: raise `AmbiguousClassificationOverrideError` because duplicate full identities should never be silently accepted.

- [ ] **Step 5: Make generated judgment cases use identity selectors**

Replace concept-first generation in `classification_judgment_cases()` with:

```python
override_selector = f"identity:{identity}"
```

for every generated case.

Do not change `case.line_identity`.

- [ ] **Step 6: Add Check-context regression**

Build a workbook containing the two split lease-liability rows. Select different treatments for the two judgment cases and prove Check can recompute the historical model without concept-selector ambiguity.

- [ ] **Step 7: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
```

---

### Task 3: Define the conservative aggregate lease-liability resolver contract

**Files:**
- Modify: `core/model/line_resolver.py`
- Modify: `core/tests/test_line_resolver.py`

**Interfaces:**
- Adds canonical concept `lease_liability` to `resolve_line()` for diagnostic source resolution.

- [ ] **Step 1: Add exact aggregate label aliases only**

Support:

```text
lease liability
lease liabilities
operating lease liability
operating lease liabilities
```

Do **not** add aliases for:

```text
current lease liabilities
non-current lease liabilities
short-term lease liabilities
long-term lease liabilities
```

because those are partial balances and this checkpoint has no aggregation contract.

- [ ] **Step 2: Add explicit-concept tests**

One line with:

```python
concept="lease_liability"
```

must resolve regardless of display label.

Two rows sharing that concept must raise `AmbiguousLineError` for canonical diagnostic resolution.

- [ ] **Step 3: Run resolver tests**

```bash
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
```

---

### Task 4: Add the lease-liability historical series

**Files:**
- Create: `core/model/lease_liability.py`
- Create: `core/tests/test_lease_liability.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class LeaseLiabilityAvailability:
    lease_liability: bool
    ambiguous: bool

@dataclass(frozen=True)
class LeaseLiabilitySeries:
    lease_liability: tuple[float, ...]
    lease_liability_to_revenue: tuple[float | str, ...]
    lease_liability_change: tuple[float | None, ...]
    lease_liability_growth: tuple[float | str | None, ...]


def lease_liability_availability(
    financials: StandardizedFinancials,
) -> LeaseLiabilityAvailability:
    ...


def lease_liability_applicable(
    financials: StandardizedFinancials,
) -> bool:
    ...


def compute_lease_liability_series(
    financials: StandardizedFinancials,
    periods: list[date],
    anchor: AnchorMetrics,
) -> LeaseLiabilitySeries:
    ...
```

- [ ] **Step 1: Write ordinary two-period math test**

For lease balances `100, 120` and revenue `1000, 1100` require:

```text
lease_liability = 100, 120
lease_liability_to_revenue = 10.0%, 10.909...%
lease_liability_change = None, 20
lease_liability_growth = None, 20.0%
```

- [ ] **Step 2: Write zero-denominator semantics**

Require:

```text
Revenue = 0 -> Lease Liability / Revenue = #N/A
Prior Lease Liability = 0 -> growth = #N/A
Current Lease Liability = 0 with nonzero prior -> growth = -100%
```

Preserve negative source values if supplied; do not wrap in `ABS()`.

- [ ] **Step 3: Write missing-period failure test**

If the unique aggregate source line exists but one modeled period is missing, `compute_lease_liability_series()` must raise `MissingHistoricalValueError`.

- [ ] **Step 4: Write ambiguity gating test**

For two split rows sharing `concept="lease_liability"`:

```text
lease_liability_availability(...).ambiguous == True
lease_liability_applicable(...) == False
```

Do not sum them.

- [ ] **Step 5: Implement minimal model**

Use `required_period_value()` and `ratio_or_na()` only. Revenue comes from `anchor.historical.revenue` and its axis length must equal `periods`.

- [ ] **Step 6: Run model tests green**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py -v
```

---

### Task 5: Add four semantic families, orders 87–90

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/model/historical_expected.py`
- Test: `core/tests/test_lease_liability.py`

**Interfaces:**

Add exactly:

```text
87 lease_liability_source_link
88 lease_liability_to_revenue
89 lease_liability_change
90 lease_liability_growth
```

Expected 5-period concrete-cell counts:

```text
source link: 5
ratio:       5
change:      4
growth:      4
Total:      18
```

- [ ] **Step 1: Define catalog metadata**

All families use:

```text
category = lease_liability
tab_template = ALT DuPont
```

Comparable-period scope applies to change and growth only.

Hints must explicitly say:

- the source balance is reported lease liability;
- classification treatment is a separate judgment;
- balance growth is not rent growth, lease cash payments, commitments, or ROU-asset growth;
- zero prior balance makes percentage growth undefined.

- [ ] **Step 2: Add expansion function**

Follow the existing fixed-asset expansion pattern, including duplicate/chronology rejection.

- [ ] **Step 3: Add expected-series mapping**

Add:

```python
lease_liability_expected_series(...)
```

and route the four family IDs through `expected_value_for_component()`.

- [ ] **Step 4: Run focused tests**

```bash
PYTHONPATH=. pytest core/tests/test_lease_liability.py -v
```

---

### Task 6: Integrate lease context into `ALT DuPont` and Formula Check

**Files:**
- Modify: `core/engine/reference_model.py`
- Modify: `core/trainer/checker.py`
- Modify: `core/trainer/workbook.py`
- Test: `core/tests/test_lease_liability.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- No new visible worksheet.
- Section appears only when `lease_liability_applicable(financials)` is true.

- [ ] **Step 1: Add builder initialization**

Compute `LeaseLiabilitySeries` after existing optional historical modules and allocate orders after fixed-asset specs.

Append lease specs to `expected_specs` and maintain a dedicated spec index.

- [ ] **Step 2: Append the section to ALT DuPont**

If fixed-asset context exists, start after its check row. Otherwise start after the existing ROE-attribution check row.

Use these visible labels:

```text
LEASE LIABILITY CONTEXT
Lease Liability
Lease Liability / Revenue
Change in Lease Liability
Lease Liability Growth
```

Do not add a decorative check row unless it validates a genuine accounting identity. These four diagnostics do not need a synthetic self-check identity.

- [ ] **Step 3: Use transparent formulas**

Source link:

```excel
='Balance Sheet'!<source cell>
```

Ratio:

```excel
=IF(<Revenue>=0,NA(),<Lease Liability>/<Revenue>)
```

Change:

```excel
=<Current Lease Liability>-<Prior Lease Liability>
```

Growth:

```excel
=IF(<Prior Lease Liability>=0,NA(),<Current>/<Prior>-1)
```

Use exact cell references generated by the builder; do not hard-code coordinates.

- [ ] **Step 4: Add Formula Check recomputation**

When any of the four lease family IDs are present in the SemanticMap, reconstruct `LeaseLiabilitySeries` from trusted source payload and pass it through `expected_value_for_component()`.

- [ ] **Step 5: Register catalog metadata in Trainer grouping**

Add lease families to `group_components_by_family()` family metadata so the Trainer index shows them in orders 87–90.

- [ ] **Step 6: Add trusted-tamper regression**

Tamper with a non-practice generated lease-context cell and require Check to raise before recoloring any practice cell.

- [ ] **Step 7: Prove classification choice does not mutate raw lease diagnostics**

For the aggregate lease demo:

1. record lease ratio expected value under reference operating-liability treatment;
2. switch Accounting Judgment to `Financial Liability`;
3. prove downstream NOA / Net Debt changes;
4. prove `lease_liability_to_revenue` stays numerically unchanged because it is based on the reported raw lease balance and Revenue.

This distinction is pedagogically important: classification affects reformulation, not the reported lease balance itself.

---

### Task 7: Prove split lease rows remain usable for judgment without unsafe aggregation

**Files:**
- Modify: `core/tests/test_classification.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_cross_company_robustness.py`

- [ ] **Step 1: Build a split-liability synthetic case**

Supply:

```text
Current lease liabilities      concept=lease_liability
Non-current lease liabilities  concept=lease_liability
```

with nonzero values across periods.

- [ ] **Step 2: Require two independent Accounting Judgment rows**

Both must have distinct `identity:` selectors and accept separate treatments.

- [ ] **Step 3: Require lease diagnostics to be omitted**

No family `87..90` should appear because canonical aggregate resolution is ambiguous.

- [ ] **Step 4: Require Check to succeed**

Fill all practice formulas, select independent treatments, and require no selector ambiguity or false trusted-state failure.

- [ ] **Step 5: Preserve existing manufacturer judgment regression**

The current aggregate manufacturer lease case remains valid. Extend it to prove the raw lease-liability ratio does not change when classification switches to Financial Liability.

---

### Task 8: Update canonical surfaces and regenerate committed demo workbooks

**Files:**
- Regenerate: `example/DEMO_HK_Trainer.xlsx`
- Regenerate: `example/DEMO_HK_Answer_Key.xlsx`
- Modify relevant surface-count tests
- Do not modify: `example/DEMO_HK_Standardized.json`
- Do not modify: `example/DEMO_HK_Assumptions.json`

The canonical demo contains one aggregate `Operating lease liabilities` line, so the lease module should activate.

Expected counts after adding four families / 18 concrete cells:

```text
base demo:               74 families / 312 cells
normalization demo:      78 / 332
shares only:             82 / 346
shares + normalization:  90 / 384
```

Cross-company expectations:

```text
services:      59 / 248   (unchanged; no lease)
retail:        78 / 331   (unchanged; no lease)
manufacturer:  74 / 311   (+4 families / +18 cells; aggregate lease present)
```

Full-feature active family namespace must become exactly:

```text
1..90
```

- [ ] **Step 1: Update expected counts in tests first**

Run affected tests and confirm they fail before production changes are complete.

- [ ] **Step 2: Regenerate through the public build path**

```bash
PYTHONPATH=. python -m core build \
  example/DEMO_HK_Standardized.json \
  -a example/DEMO_HK_Assumptions.json \
  -o example/DEMO_HK_Trainer.xlsx
```

- [ ] **Step 3: Verify fresh Check counts**

Normalization canonical Trainer:

```text
0 correct
0 incorrect
332 blank
```

- [ ] **Step 4: Preserve Step 9I.1 visual contract**

Fresh visible workbook surface remains Aptos Narrow 11, white/yellow, no decorative borders.

---

### Task 9: Update documentation only after the implementation is verified

**Files:**
- Modify: `README.md`
- Modify: `docs/GOOGL_HISTORICAL_REFERENCE.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only after all tests pass
- Modify: `skills/bav-trainer/SKILL.md` only if current capability claims would otherwise be false
- Do not modify: `TARGET.md`

- [ ] **Step 1: Update README current capability list**

Add one concise implemented capability:

```text
optional lease-liability intensity and trend diagnostics when one aggregate historical lease-liability line is supplied
```

Do not advertise split-liability aggregation, ROU modeling, or lease amortization.

- [ ] **Step 2: Update the GOOGL gap matrix**

Lease row becomes `implemented-differently` for aggregate-liability diagnostics + guided classification.

State clearly that:

```text
ROU-asset diagnostics are not implemented
split current/non-current aggregation is not implemented
lease payment / discount-rate analysis is not implemented
```

After Step 9L.1, the next Priority A item should be **goodwill / acquired intangibles / acquisition-cash diagnostics** unless new evidence from tests changes the dependency order.

- [ ] **Step 3: Record review fixes in RESULT.md**

Record:

```text
GOOGL provenance drift fixed
stale Answer-Key hash removed from persistent reference doc
identity: judgment selectors added
split duplicate-concept lease case verified
lease module orders 87–90
aggregate-vs-split gating verified
actual surface counts
actual full pytest count
no attached CI status
forecasting / valuation still deferred
TARGET.md unchanged
```

---

### Task 10: Final verification

Run:

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -v
PYTHONPATH=. pytest core/tests/test_line_resolver.py -v
PYTHONPATH=. pytest core/tests/test_lease_liability.py -v
PYTHONPATH=. pytest core/tests/test_reference_workbook_audit.py -v
PYTHONPATH=. pytest core/tests/test_reference_integrity.py -v
PYTHONPATH=. pytest core/tests/test_cross_company_robustness.py -v
PYTHONPATH=. pytest core/tests/test_historical_v1_exit_gate.py -v
PYTHONPATH=. pytest core/tests/test_trainer.py -v
PYTHONPATH=. pytest core/tests/ -q
```

Do not prestate the final test count. Record the actual count.

Verify CLI remains exactly:

```text
ingest
build
check
list
```

Verify deferred sheets remain hidden:

```text
Model_Bear
Model_Base
Model_Bull
Scenario_Summary
```

Verify no normal build executes forecast/valuation code.

---

## Definition of Done

Step 9L.1 is complete only when:

1. Step 9K.1 fixed-asset behavior remains correct.
2. The GOOGL reference document again separates actual GOOGL evidence from Trainer-created features.
3. The stale canonical Answer-Key hash is removed from persistent reference documentation.
4. Generated Accounting Judgment cases use exact `identity:` selectors.
5. Existing manual `concept:` and `label:` overrides remain backward compatible.
6. Two different rows sharing one concept can be judged independently without override ambiguity.
7. One unique aggregate lease-liability line activates four families, orders 87–90.
8. Split current/non-current lease rows do not get silently aggregated; lease diagnostics are omitted while judgment remains usable.
9. Lease diagnostics preserve source signs and proper `#N/A` semantics.
10. Changing lease classification changes reformulated NOA / Net Debt but does not change raw lease-liability intensity/trend diagnostics.
11. Canonical demo counts are 74/312, 78/332, 82/346, and 90/384 as applicable.
12. Cross-company counts are services 59/248, retail 78/331, manufacturer 74/311.
13. Full-feature family namespace is exactly 1..90.
14. Minimal visual style and workbook-wide Check remain intact.
15. Full tests pass; actual count is recorded.
16. Forecasting and valuation remain deferred.
17. `TARGET.md` remains unchanged by Cursor.
18. Cursor performs no Git operations.
