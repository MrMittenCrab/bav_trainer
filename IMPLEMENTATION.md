**Status:** Step 9M.3C complete — G5 parent/NCI attribution + parent ROE; FR Stages 1–7 pass with expected_specs=346. Stopped for user checkpoint.

# Step 9M.3C — Parent / NCI Attribution and Parent ROE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `9f3c4b0f35b50fd885e68849fe12ec71b5899a0e` (`Step 9M.3B`). Implement only Step 9M.3C using red/green TDD. Do not begin G6 share-basis restatement, G7 conflict-policy changes, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Close G5 by making parent-attributable profit, parent equity, and NCI explicit historical analytical inputs; add a source-grounded parent-ROE attribution schedule; and ensure any future diluted-EPS calculation uses parent-attributable earnings rather than consolidated profit when NCI is present.

**Architecture:** Do not add another ingestion payload when the required facts already exist as standardized statement rows. Extend the canonical line resolver for four explicit attribution concepts, then add one optional `OwnershipAttributionSeries` computed only when the full parent/NCI profit-and-equity set is present. Keep the consolidated BAV reformulation and decomposed ROE unchanged: those remain enterprise/consolidated diagnostics. Add a separate parent/NCI schedule so the workbook does not pretend parent ROE is identical to consolidated decomposed ROE. Finally, harden the existing per-share engine so its earnings numerator is parent-attributable profit when a complete ownership-attribution set exists, while preserving total-net-income behavior for companies with no NCI evidence.

**Tech Stack:** Python, pytest, existing `StandardizedFinancials`, canonical line resolver, `AnchorMetrics`, `ReferenceModelBuilder`, semantic component map, per-share diagnostics, Fast Retailing benchmark audit.

**Spec:** `TARGET.md` minority/NCI, ROE, per-share, source-grounding, optional-module, and no-invented-input requirements plus G5 in `benchmark/fast_retailing/GAPS.md`.

## Why this is the next step

Step 9M.3B closes G4 and leaves Fast Retailing Stages 1–7 passing with 312 active historical components. The remaining substantive gaps are G5–G7. G5 should precede G6 because the current per-share engine still uses consolidated `net_income` as its numerator, but Fast Retailing explicitly reports profit attributable to owners and NCI. Building the share-basis fix first would preserve the wrong shareholder numerator.

Fast Retailing already supplies the required five-year statement concepts:

```text
profit_attributable_to_owners
profit_attributable_to_nci
equity_attributable_to_owners
noncontrolling_interests
```

FY2025 evidence:

```text
Total profit                     459,153
Profit attributable to owners    433,009
Profit attributable to NCI        26,143
owners + NCI                     459,152   (1-unit presentation difference)

Total equity                   2,327,501
Equity attributable to owners  2,273,115
NCI equity                        54,385
owners + NCI                   2,327,500   (1-unit presentation difference)
```

These differences are compatible with independently rounded presentation. Do not plug either bridge.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve all Step 9M.3B lease treatment behavior and tests.
- Preserve source/extracted/provenance/conflict artifacts; no source mutation or invented attribution values.
- Do not derive parent profit as `total - NCI` when the parent line is missing; require the reported parent line for the optional attribution module.
- Do not derive NCI profit/equity from differences when reported components are missing.
- Do not replace consolidated BAV `NOA`, `Net Debt`, `NOPAT`, `RNOA`, `Spread`, `FLEV`, or decomposed ROE with parent-only quantities in this checkpoint.
- Parent ROE is a separate shareholder-attribution diagnostic: current parent profit divided by average reported parent equity.
- Parent/NCI presentation bridge tolerances must reflect reporting-unit rounding only: for two displayed components against one displayed total, accept absolute gap `<= 1.5` reporting units; larger discrepancies fail closed.
- A company with no parent/NCI attribution lines keeps all existing behavior and should not receive the new optional module.
- A partial/ambiguous ownership presentation must not silently fall back to a parent-specific analysis.
- Do not activate Fast Retailing per-share analysis yet; G6 remains responsible for its split-adjusted comparable share axis.
- Forecast/valuation isolation remains mandatory.

---

### Task 1: Add canonical ownership-attribution resolution and integrity math

**Files:**
- Modify: `core/model/line_resolver.py`
- Create: `core/model/ownership_attribution.py`
- Create: `core/tests/test_ownership_attribution.py`
- Modify: `core/tests/test_line_resolver.py`

**Interfaces:**
- Extend `resolve_line()` to recognize these canonical concepts:
  - `profit_attributable_to_owners`
  - `profit_attributable_to_nci`
  - `equity_attributable_to_owners`
  - `noncontrolling_interests`
- New module API:

```python
@dataclass(frozen=True)
class OwnershipAttributionAvailability:
    available: bool
    partial: bool
    ambiguous: bool

@dataclass(frozen=True)
class OwnershipAttributionSeries:
    parent_profit: tuple[float, ...]
    nci_profit: tuple[float, ...]
    profit_attribution_gap: tuple[float, ...]
    parent_equity: tuple[float, ...]
    nci_equity: tuple[float, ...]
    equity_attribution_gap: tuple[float, ...]
    parent_roe: tuple[float | str | None, ...]

class OwnershipAttributionIntegrityError(ValueError): ...

ownership_attribution_availability(financials) -> OwnershipAttributionAvailability
compute_ownership_attribution_series(financials, periods) -> OwnershipAttributionSeries
```

- [x] **Step 1: Write resolver tests for all four exact concepts**

Require exact `LineItem.concept` resolution first. Add narrow exact-label aliases only for conventional parent/NCI labels such as `Owners of the Parent`, `Profit attributable to owners of the Parent`, `Non-controlling interests`, and `Equity attributable to owners of the Parent`. Do not use broad `owner`, `minority`, or `interest` substring matching.

- [x] **Step 2: Write availability tests**

Cover:

```text
no attribution lines                  -> available=False, partial=False
all four unique lines                 -> available=True
one/more lines missing                -> available=False, partial=True
duplicate same-priority parent/NCI row -> available=False, ambiguous=True
```

- [x] **Step 3: Write the core series and rounding-bound tests**

Use a two-period fixture with complete reported total profit/equity and all four attribution lines. Require:

```python
series.profit_attribution_gap[i] == pytest.approx(
    series.parent_profit[i] + series.nci_profit[i] - total_profit[i]
)
series.equity_attribution_gap[i] == pytest.approx(
    series.parent_equity[i] + series.nci_equity[i] - total_equity[i]
)
series.parent_roe[0] is None
series.parent_roe[1] == pytest.approx(
    series.parent_profit[1] / ((series.parent_equity[0] + series.parent_equity[1]) / 2)
)
```

Accept bridge gaps exactly at `1.5`; reject `> 1.5` with `OwnershipAttributionIntegrityError`.

- [x] **Step 4: Run Task 1 red**

```bash
PYTHONPATH=. pytest \
  core/tests/test_line_resolver.py \
  core/tests/test_ownership_attribution.py \
  -v
```

- [x] **Step 5: Implement the minimal resolver/module**

Use `required_period_value()` / `required_period_series()` for full-axis completeness. Do not derive a missing component from the bridge. Keep the 1.5 reporting-unit tolerance local and explicit (`0.5 * (2 + 1)`).

- [x] **Step 6: Run Task 1 green**

Run the same command; require all selected tests pass.

---

### Task 2: Add the optional Ownership Attribution learning schedule

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/model/historical_expected.py`
- Modify: `core/tests/test_reference_integrity.py`
- Modify: `core/tests/test_ownership_attribution.py`

**Interfaces:**
- Add `OWNERSHIP_ATTRIBUTION_COMPONENT_CATALOG` with family orders `91..97`:

```text
91 parent_profit_source_link      all periods
92 nci_profit_source_link         all periods
93 profit_attribution_gap         all periods
94 parent_equity_source_link      all periods
95 nci_equity_source_link         all periods
96 equity_attribution_gap         all periods
97 parent_roe                     comparable periods
```

- Add `expand_ownership_attribution_specs(periods, start_order=...)`.
- `ReferenceModelBuilder` exposes:

```python
self.ownership_attribution_series
self.ownership_attribution_specs
```

- [x] **Step 1: Write catalog-expansion tests**

For five periods require `6 * 5 + 1 * 4 = 34` concrete ownership specs and family orders exactly `91..97`.

- [x] **Step 2: Write builder applicability tests**

Complete attribution fixture -> module/specs present. No attribution evidence -> `ownership_attribution_series is None` and specs empty. Partial/ambiguous presentation -> module omitted; the existing historical model still builds, because this remains an optional module.

- [x] **Step 3: Write workbook-formula tests**

Add one visible `Ownership Attribution` sheet. Formula contract:

```text
Parent Profit            -> exact Income Statement parent-profit source row
NCI Profit               -> exact Income Statement NCI-profit source row
Total Profit             -> existing Net Income source row (display context; non-practice)
Profit Attribution Gap   -> Parent Profit + NCI Profit - Total Profit
Parent Equity            -> exact Balance Sheet parent-equity source row
NCI Equity               -> exact Balance Sheet NCI-equity source row
Total Equity             -> exact reported Total Equity source row (display context; non-practice)
Equity Attribution Gap   -> Parent Equity + NCI Equity - Total Equity
Parent ROE               -> Parent Profit / average current+prior Parent Equity
```

The first Parent ROE period is display-only `N/A`/blank, not a comparable practice cell.

- [x] **Step 4: Register semantic expected values and Check behavior**

The 34 new components must use the same Python `OwnershipAttributionSeries` values as workbook formulas. Trainer cells are blank yellow; Answer Key formulas/Notes are populated; Check grades all 34.

- [x] **Step 5: Run Task 2 tests**

```bash
PYTHONPATH=. pytest \
  core/tests/test_ownership_attribution.py \
  core/tests/test_reference_integrity.py \
  -k "ownership or parent_roe or nci" \
  -v
```

---

### Task 3: Make the existing per-share earnings numerator ownership-safe

**Files:**
- Modify: `core/model/per_share.py`
- Modify: `core/model/per_share_attribution.py`
- Modify: `core/tests/test_per_share.py`
- Modify: `core/tests/test_per_share_attribution.py`
- Reuse: `core/model/ownership_attribution.py`

**Interfaces:**
- Add to `PerShareSeries`:

```python
earnings_numerator: tuple[float, ...]
```

- Add helper in `ownership_attribution.py`:

```python
per_share_earnings_numerator(financials, periods, fallback_total_profit) -> tuple[float, ...]
```

Contract:

```text
complete ownership attribution -> reported parent_profit
no ownership/NCI evidence       -> existing consolidated net_income behavior
partial/ambiguous evidence      -> fail closed if per-share computation is requested
```

- [x] **Step 1: Add whole-owned regression**

Existing share-enabled fixtures with no ownership evidence must produce exactly the same EPS as before.

- [x] **Step 2: Add NCI fixture with shares**

With total profit `110`, parent profit `100`, NCI profit `10`, and diluted shares `10`, require reported diluted EPS = `10.0`, not `11.0`.

- [x] **Step 3: Update per-share attribution to use the same numerator**

`compute_per_share_attribution_series()` must use `per_share.earnings_numerator`, not `anchor.historical.net_income`, so the level and change bridge cannot disagree.

- [x] **Step 4: Add partial-attribution fail-closed test**

If NCI/parent attribution evidence is present but incomplete and historical shares are supplied, `compute_per_share_series()` must raise a specific ownership-attribution error rather than silently using consolidated profit.

- [x] **Step 5: Run Task 3 tests**

```bash
PYTHONPATH=. pytest \
  core/tests/test_per_share.py \
  core/tests/test_per_share_attribution.py \
  core/tests/test_ownership_attribution.py \
  -v
```

Do not activate Fast Retailing per-share in this task; `historical_shares` remains null until G6 supplies a defensible comparable axis.

---

### Task 4: Prove the Fast Retailing G5 contract on real statements

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Read only: `benchmark/fast_retailing/reconciled/standardized.json`
- Read only: `benchmark/fast_retailing/reconciled/provenance.json`
- Modify after measured verification: `benchmark/fast_retailing/GAPS.md`
- Modify after measured verification: `benchmark/fast_retailing/BASELINE.md`
- Modify after measured verification: `RESULT.md`

- [x] **Step 1: Assert all four five-year attribution concepts exist**

Locate by concept, not row position. Require complete 2021–2025 values for parent profit, NCI profit, parent equity, and NCI equity.

- [x] **Step 2: Assert FY2025 literal facts and bridges**

Require:

```text
Total profit                     459153
Parent profit                    433009
NCI profit                        26143
profit bridge gap                    -1

Total equity                    2327501
Parent equity                   2273115
NCI equity                        54385
equity bridge gap                    -1
```

Both gaps must be accepted without mutation because they are inside the 1.5-unit reporting envelope.

- [x] **Step 3: Assert parent ROE is separate from consolidated DuPont ROE**

Require the ownership schedule to compute parent ROE from reported parent profit/equity. Do not require equality to `anchor.dupont["ROE (decomposed)"]`; add a regression explicitly preventing production code from replacing consolidated NOA/Net Debt/NOPAT with parent-only quantities.

- [x] **Step 4: Assert module count**

Step 9M.3B has `expected_specs=312`. With complete Fast Retailing ownership attribution, Step 9M.3C should add 34 specs:

```text
ownership_attribution_specs = 34
expected_specs = 346
```

If the measured catalog count differs, stop and inspect the family inventory rather than changing the expected number blindly.

- [x] **Step 5: Run the benchmark acceptance test**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

---

### Task 5: Run the full real-company audit and regression gates

**Files:**
- Test only except measured documentation/status updates.

- [x] **Step 1: Run the focused Step 9M.3C suite**

```bash
PYTHONPATH=. pytest \
  core/tests/test_ownership_attribution.py \
  core/tests/test_line_resolver.py \
  core/tests/test_per_share.py \
  core/tests/test_per_share_attribution.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Record the literal pass count.

- [x] **Step 2: Run the full historical regression suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the literal pass count.

- [x] **Step 3: Run the staged Fast Retailing audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require Stages 1–7 to pass. Expected if the measured component count matches Task 4:

```text
Stage 4 expected_specs=346
blank Check:  correct=0 incorrect=0 blank=346 total=346
filled Check: correct=346 incorrect=0 blank=0 total=346
```

- [x] **Step 4: Verify source/provenance/conflict artifacts did not drift**

```bash
git diff -- \
  benchmark/fast_retailing/source \
  benchmark/fast_retailing/extracted \
  benchmark/fast_retailing/reconciled/provenance.json \
  benchmark/fast_retailing/reconciled/conflicts.json
```

Expected: no output. Preserve overlap conflicts = 3 and supplemental conflicts = 3.

`standardized.json` should not need a schema change for G5 because the four attribution concepts already exist as statement rows.

- [x] **Step 5: Verify forecast/valuation isolation and existing lease behavior**

Run the existing normal-build scenario/forecast isolation regression plus Step 9M.3B lease-treatment tests. Family orders below the new ownership range remain unchanged; new ownership family orders are exactly `91..97`.

- [x] **Step 6: Update documentation from literal evidence**

If all acceptance criteria pass:

```text
G5 -> CLOSED in Step 9M.3C
G6/G7 -> remain open
```

Document that parent ROE is a separate shareholder-attribution diagnostic and that consolidated BAV DuPont remains unchanged. Document that the per-share engine is now ownership-safe but Fast Retailing per-share remains omitted until G6 establishes a comparable post-split share axis.

- [x] **Step 7: Mark Step 9M.3C complete only after fresh evidence, then stop**

At the top of `IMPLEMENTATION.md` and in `RESULT.md`, record actual focused/full test counts, ownership spec count, Fast Retailing Stage 1–7 state, and Check totals. Do not begin G6 in the same checkpoint.

## Stop condition

After Step 9M.3C, stop. The next review should decide G6 (audited split-adjusted share basis and per-share activation) using the newly correct parent-attributable earnings numerator. G7 restatement/conflict policy remains separate.
