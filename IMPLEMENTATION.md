# Step 9M.3D — Split-Adjusted Historical Share Basis and Per-Share Activation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted implementation base is commit `f15a01ac4733a9290c238f621a993e722f524032` (`Step 9M.3C`). Implement only Step 9M.3D using red/green TDD. Do not begin G7 conflict-policy redesign, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Close G6 by constructing a complete, source-grounded, split-adjusted diluted weighted-average share axis for Fast Retailing and companies with the same audited-restatement pattern, then activate the existing diluted per-share and earnings/share-count attribution modules on that comparable basis.

**Architecture:** Preserve all raw extracted share facts and conflicts. Add one deterministic share-basis resolver upstream of `HistoricalShareData`: accept reported diluted-WAS facts directly, or validated derived diluted-WAS facts whose derivation is exactly `basic_weighted_average_shares + dilutive_shares`. When the same historical period is later restated after a stock split, infer one integer split factor only from source-grounded overlapping share observations that are anchored by an audited `RESTATED_COMPARATIVE` diluted-EPS selection; use that factor to analytically restate earlier periods that have no later restated share presentation. The model payload stores the resulting comparable share axis in financial-statement units and explicitly records which periods were adjusted. Existing per-share math then consumes that axis with the Step 9M.3C parent-attributable earnings numerator. G7 conflicts remain recorded and unchanged.

**Tech Stack:** Python dataclasses, pytest, existing filing reconciler/standardizer, `HistoricalShareData`, `StandardizedFinancials` JSON IO, existing per-share/per-share-attribution engine, `ReferenceModelBuilder`, semantic map / Check workflow, Fast Retailing benchmark audit.

**Spec:** `TARGET.md` no-invented-input, source-grounding, historical-share-count, dilution, per-share, optional-module, and auditability requirements plus G6 in `benchmark/fast_retailing/GAPS.md`.

## Why this is the next step

Step 9M.3C closes G5 and leaves Fast Retailing Stages 1–7 passing with `expected_specs=346`. G6 is now the only missing input contract preventing the already-built per-share curriculum from activating.

The documentary evidence is sufficient to establish a comparable basis without silently rewriting source facts:

```text
FY2022 filing diluted WAS (derived from reported basic + dilutive): 102,323,208
FY2023 filing FY2022 comparative diluted WAS:                   306,969,624
ratio:                                                           3.0x

FY2022 diluted EPS as originally presented:                    2,671.29
FY2023 filing FY2022 diluted EPS, RESTATED_COMPARATIVE:          890.43
inverse ratio:                                                    3.0x
```

The same FY2022 basic and dilutive share components are also exactly tripled in the later filing. That gives a source-grounded split-restatement anchor. For FY2021, there is no later audited comparative share row, so the model may not call an adjusted FY2021 share count “reported”; it may, however, apply the established 3-for-1 factor as an explicit analytical restatement for comparability. The raw FY2021 reported share facts remain untouched in provenance.

The intended Fast Retailing comparable diluted-WAS axis in actual shares is:

```text
FY2021  306,871,785   = 102,290,595 × 3  (analytically split-adjusted)
FY2022  306,969,624   = later audited restated comparative
FY2023  307,138,870   = reported/derived on post-split basis
FY2024  307,231,804   = reported/derived on post-split basis
FY2025  307,247,804   = reported/derived on post-split basis
```

Because Fast Retailing statements are in JPY millions, `HistoricalShareData` must expose these as `306.871785`, `306.969624`, `307.138870`, `307.231804`, `307.247804` with `scale_basis="financial_statement_units"`; otherwise JPY-million earnings divided by raw shares would be dimensionally wrong.

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve all source PDFs, source hashes, extracted filing JSON, and raw supplemental share facts.
- Preserve all existing statement and supplemental conflicts; do not delete or overwrite G7 evidence to obtain a clean share axis.
- Preserve overlap conflict count `3` and supplemental conflict count `3` unless a test proves the existing artifacts themselves are wrong; this step is not allowed to change conflict policy.
- Do not add a Fast Retailing ticker/name branch to production code.
- Do not infer a split merely because adjacent yearly share counts differ.
- A split factor may be inferred only from two audited presentations of the **same historical period**, with an explicit `RESTATED_COMPARATIVE` diluted-EPS selection anchoring the later presentation.
- The inferred factor must be a positive integer greater than `1` and must reconcile the overlapping diluted-WAS observations; supporting basic/dilutive components must not contradict it.
- Only one split/restatement event is supported in Step 9M.3D. Multiple distinct factors/events must fail closed rather than being chained speculatively.
- Earlier periods adjusted by the factor are analytical comparable-basis values, not newly reported source facts.
- Accept a derived diluted-WAS observation only when its derivation is exactly `basic_weighted_average_shares + dilutive_shares` and the same filing/period contains reported component facts that sum to it.
- `HistoricalShareData` emitted by filing standardization must use `scale_basis="financial_statement_units"`.
- Step 9M.3C ownership logic remains authoritative: per-share earnings use parent-attributable profit when complete ownership attribution exists.
- Consolidated BAV reformulation, leases, ownership attribution, formula family meanings, and forecast isolation remain unchanged.
- Existing per-share family IDs remain stable. Do not create a second per-share module.
- Cursor stops after implementation/tests/documentation and returns control for user `checkpoint`.

---

### Task 1: Build a deterministic share-basis resolver

**Files:**
- Create: `core/ingestion/share_basis.py`
- Create: `core/tests/test_share_basis.py`
- Read: `core/data/filing.py`
- Read: `core/ingestion/filing_reconciler.py`

**Interfaces:**

Add one immutable result type and one resolver:

```python
@dataclass(frozen=True)
class HistoricalShareBasisResolution:
    diluted_weighted_average_actual_shares: dict[date, float]
    applied_adjustment_factors: dict[date, float]
    basis: str  # "reported" | "split_adjusted"
    restatement_anchor_period: date | None
    restatement_filing_year: int | None
    split_factor: float | None


def resolve_historical_share_basis(
    reconciled: ReconciledCompanyData,
) -> HistoricalShareBasisResolution | None:
    ...
```

Do not expose source file paths through this model-facing result; audit artifacts already preserve observations.

- [ ] **Step 1: Add a no-split reported-axis test**

Construct a synthetic `ReconciledCompanyData` with a complete period axis where each period has one `diluted_weighted_average_shares` observation with `status="reported"`. Require:

```python
result = resolve_historical_share_basis(reconciled)
assert result is not None
assert result.basis == "reported"
assert result.split_factor is None
assert result.applied_adjustment_factors == {p1: 1.0, p2: 1.0}
assert result.diluted_weighted_average_actual_shares == {p1: 100.0, p2: 110.0}
```

- [ ] **Step 2: Add valid derived-WAS validation**

For one filing/period supply:

```text
basic_weighted_average_shares = 100 (reported)
dilutive_shares               =   5 (reported)
diluted_weighted_average_shares = 105 (derived)
derivation = "basic_weighted_average_shares + dilutive_shares"
```

Require the resolver to accept `105`. Then parameterize failures for:

```text
wrong derivation string
missing basic component
missing dilutive component
component status != reported
derived total != basic + dilutive
```

Each unsupported case must return `None` for a required complete axis rather than inventing a correction.

- [ ] **Step 3: Add one valid audited-restatement anchor test**

Use three model periods. For period 2 supply two audited share presentations:

```text
filing 2022: diluted WAS = 100
filing 2023: diluted WAS = 300
```

Also add the canonical income-statement `diluted_eps` reconciliation conflict for period 2:

```text
old current-period EPS = 30.00
selected later EPS     = 10.00
selected.presentation_role = RESTATED_COMPARATIVE
selected.filing_year = 2023
```

For period 1, only a pre-restatement diluted WAS of `90` exists. For period 3, a post-restatement WAS of `330` exists. Require:

```python
result.basis == "split_adjusted"
result.split_factor == 3.0
result.restatement_anchor_period == p2
result.restatement_filing_year == 2023
result.diluted_weighted_average_actual_shares == {
    p1: 270.0,
    p2: 300.0,
    p3: 330.0,
}
result.applied_adjustment_factors == {p1: 3.0, p2: 1.0, p3: 1.0}
```

- [ ] **Step 4: Add fail-closed restatement tests**

Require `None` for each unsupported contract:

```text
same-period share disagreement but no RESTATED_COMPARATIVE EPS evidence
share ratio 2.7 rather than an integer factor
later EPS does not approximately invert the share factor
basic/dilutive component evidence contradicts the diluted-WAS factor
more than one distinct split factor across the model axis
restatement evidence exists but one modeled period has no usable share observation
later selected share observation does not come from the restatement filing or later
```

For the EPS inverse-factor check, use a rounding-aware comparison suitable for two-decimal EPS presentation; do not demand bitwise equality. Keep the tolerance local and documented.

- [ ] **Step 5: Run Task 1 red**

```bash
PYTHONPATH=. pytest core/tests/test_share_basis.py -v
```

Expected before implementation: import/behavior failures because the resolver does not exist.

- [ ] **Step 6: Implement the minimal resolver**

Implementation order:

```text
1. collect eligible diluted-WAS observations by filing_year + period
2. validate every derived observation against reported basic + dilutive components
3. identify same-period diluted-WAS disagreements
4. require the matching diluted-EPS ReconciledValue to select RESTATED_COMPARATIVE
5. infer one integer factor from the old/new same-period diluted-WAS values
6. corroborate with basic/dilutive components when non-zero
7. corroborate with inverse diluted-EPS ratio within presentation-rounding tolerance
8. choose the later/restated share presentation for the anchor period
9. multiply only earlier periods lacking a post-restatement presentation
10. require one complete positive model-period axis
```

Do not mutate `reconciled.share_facts`, `reconciled.values`, or conflicts.

- [ ] **Step 7: Run Task 1 green**

```bash
PYTHONPATH=. pytest core/tests/test_share_basis.py -v
```

---

### Task 2: Emit an explicit comparable share basis in StandardizedFinancials

**Files:**
- Modify: `core/data/interface.py`
- Modify: `core/data/standardized_io.py`
- Modify: `core/ingestion/filing_standardizer.py`
- Modify: `core/tests/test_filing_reconciler.py`
- Modify or create focused standardized-IO tests following existing repository placement

**Interfaces:**

Extend `HistoricalShareData` backwards-compatibly:

```python
@dataclass
class HistoricalShareData:
    scale_basis: str = ""
    diluted_weighted_average: dict[date, float | None] = field(default_factory=dict)
    basis: str = "reported"
    adjustment_factors: dict[date, float] = field(default_factory=dict)
```

Older payloads without `basis` / `adjustment_factors` must deserialize with the defaults above.

- [ ] **Step 1: Add JSON round-trip tests**

Require the new fields to survive:

```text
StandardizedFinancials -> standardized_to_payload -> standardized_from_payload
```

Also load a legacy payload containing only `scale_basis` + `diluted_weighted_average` and require `basis="reported"`, empty `adjustment_factors`.

- [ ] **Step 2: Add unit-scale conversion tests**

Parameterize filing unit scales:

```text
ones      -> divisor 1
thousands -> divisor 1_000
millions  -> divisor 1_000_000
billions  -> divisor 1_000_000_000
```

Given `307_247_804` actual shares and `unit_scale="millions"`, require standardized diluted WAS `307.247804` and:

```python
shares.scale_basis == "financial_statement_units"
```

This is a dimensional contract, not display formatting.

- [ ] **Step 3: Replace the current `_historical_shares()` selection logic**

`filing_standardizer.py` currently requires `status="reported"` diluted-WAS facts and therefore rejects the Fast Retailing axis even though the extraction already contains explicitly derived diluted WAS. Replace that behavior with `resolve_historical_share_basis(reconciled)`.

If resolution returns `None`, keep `historical_shares=None` exactly as today.

If it returns a basis, emit:

```python
HistoricalShareData(
    scale_basis="financial_statement_units",
    diluted_weighted_average={
        period: actual_shares / unit_scale_divisor
        for period, actual_shares in resolution.diluted_weighted_average_actual_shares.items()
    },
    basis=resolution.basis,
    adjustment_factors=resolution.applied_adjustment_factors,
)
```

Do not put source paths or page numbers into `StandardizedFinancials`.

- [ ] **Step 4: Prove unsupported share data remains optional**

Add regressions that incomplete/unresolved share facts still produce `historical_shares=None` while the rest of `StandardizedFinancials` is emitted normally. G6 must not make share data mandatory for companies without a reliable basis.

- [ ] **Step 5: Run Task 2 tests**

```bash
PYTHONPATH=. pytest \
  core/tests/test_share_basis.py \
  core/tests/test_filing_reconciler.py \
  -k "share or historical_shares or standardized" \
  -v
```

Then run the repository's existing standardized-IO round-trip tests containing `HistoricalShareData`.

---

### Task 3: Make the learner-facing per-share surface semantically honest on an adjusted basis

**Files:**
- Modify: `core/engine/component_catalog.py`
- Modify: `core/engine/reference_model.py`
- Modify: `core/model/per_share.py` only if required for basis validation/message clarity; do not change its existing parent-earnings numerator contract
- Modify: `core/tests/test_per_share.py`
- Modify: `core/tests/test_per_share_attribution.py`
- Modify: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Keep existing family IDs `reported_diluted_eps`, `nopat_per_diluted_share`, `diluted_eps_change`, `diluted_share_count_change` and existing attribution IDs stable.
- Keep Step 9M.3C `PerShareSeries.earnings_numerator` behavior unchanged.

- [ ] **Step 1: Add split-adjusted per-share math regression**

Use parent-attributable earnings in financial-statement units and a `HistoricalShareData` object with `basis="split_adjusted"`, `scale_basis="financial_statement_units"`. Require exact computation from the adjusted share axis and require share-count change to use adjusted values, not raw pre-split counts.

- [ ] **Step 2: Preserve whole-owned / already-comparable behavior**

Existing fixtures with `basis="reported"` and `scale_basis="financial_statement_units"` must produce unchanged numbers.

- [ ] **Step 3: Correct learner-facing terminology**

The current family title/hint says “Reported Diluted EPS” even when the earliest period can be analytically split-adjusted. Keep the stable internal family ID but change visible title/hints to the equivalent of:

```text
Diluted EPS (Comparable Basis)
Earnings numerator / diluted weighted-average shares on the supplied comparable share basis.
When the supplied basis is split-adjusted, this is an analytical comparable figure and may differ from the originally printed pre-split EPS.
```

Likewise, change attribution display text that says “Reported Net Income” to “Per-Share Earnings Numerator” (or equivalent), because Step 9M.3C may use parent-attributable profit. Keep internal IDs stable.

- [ ] **Step 4: Expose the share basis without adding a practice answer**

On `Per Share Analysis`, keep supplied share counts populated. Add a small non-practice basis label such as:

```text
Share Basis: Split-adjusted comparable basis
```

when `historical_shares.basis == "split_adjusted"`; use `Reported basis` otherwise. Do not make this a yellow cell and do not create a new semantic practice family.

- [ ] **Step 5: Prove module/spec counts**

For five periods, existing per-share families contribute:

```text
Per-share level/change specs: 18
Per-share attribution specs:  16
Total newly active specs:      34
```

With the Fast Retailing Step 9M.3C base of `346`, G6 activation should therefore produce `380` active specs if no unrelated optional module becomes active. Add an assertion against the catalog arithmetic; if the measured count differs, inspect rather than changing `380` blindly.

- [ ] **Step 6: Run Task 3 tests**

```bash
PYTHONPATH=. pytest \
  core/tests/test_per_share.py \
  core/tests/test_per_share_attribution.py \
  core/tests/test_reference_integrity.py \
  -v
```

---

### Task 4: Prove Fast Retailing uses the source-grounded 3-for-1 comparable basis

**Files:**
- Modify: `core/tests/test_fast_retailing_benchmark.py`
- Modify only the model output generated from unchanged extracted facts: `benchmark/fast_retailing/reconciled/standardized.json`
- Read only: `benchmark/fast_retailing/extracted/*.json`
- Read only: `benchmark/fast_retailing/reconciled/provenance.json`
- Read only: `benchmark/fast_retailing/reconciled/conflicts.json`

**Interfaces:**
- Use the normal filing validation/reconciliation/standardization path; do not hand-edit `standardized.json` values.

- [ ] **Step 1: Add documentary anchor assertions**

Require the benchmark evidence already committed:

```text
FY2022 diluted WAS, 2022 filing = 102323208
FY2022 diluted WAS, 2023 filing = 306969624
ratio = 3
FY2022 selected diluted EPS = 890.43
selected EPS presentation role = RESTATED_COMPARATIVE
prior diluted EPS = 2671.29
```

Also require the later FY2022 reported basic and dilutive components to be exactly 3× the earlier components where both are non-zero.

- [ ] **Step 2: Assert the five-year resolved actual-share axis**

Require:

```python
{
    date(2021, 8, 31): 306_871_785.0,
    date(2022, 8, 31): 306_969_624.0,
    date(2023, 8, 31): 307_138_870.0,
    date(2024, 8, 31): 307_231_804.0,
    date(2025, 8, 31): 307_247_804.0,
}
```

Require basis metadata:

```text
basis = split_adjusted
split_factor = 3
FY2021 applied adjustment factor = 3
FY2022–FY2025 applied factor = 1
```

- [ ] **Step 3: Assert standardized financial-statement-unit values**

After normal standardization require:

```text
scale_basis = financial_statement_units
FY2021 306.871785
FY2022 306.969624
FY2023 307.138870
FY2024 307.231804
FY2025 307.247804
```

The only intentional `standardized.json` change in this checkpoint should be `historical_shares: null -> populated comparable-basis object` (plus its new basis metadata). Income statement, balance sheet, cash flow, historical lease, and all source-grounded statement values must remain unchanged.

- [ ] **Step 4: Assert per-share economics against ownership-safe numerators**

Fast Retailing per-share computation must use Step 9M.3C parent-attributable profit. Require FY2022–FY2025 computed diluted EPS to agree with the later audited/restated EPS presentation within the existing numerical tolerance. For FY2021, require the computed comparable EPS to equal the originally reported pre-split EPS divided by `3` within two-decimal presentation rounding; do not relabel that analytically adjusted value as a newly reported source fact.

Require FY2025 approximately:

```text
433009 / 307.247804 ≈ 1409.32
```

- [ ] **Step 5: Assert module activation and Check totals**

Require:

```text
per_share applicable = True
per_share_specs = 18
per_share_attribution_specs = 16
ownership_specs = 34
lease_specs = 18
expected_specs = 380
```

Run workbook generation and require:

```text
blank Check:  correct=0 incorrect=0 blank=380 total=380
filled Check: correct=380 incorrect=0 blank=0 total=380
```

- [ ] **Step 6: Prove G7 evidence is untouched**

Require:

```text
primary-statement overlap conflicts = 3
supplemental conflicts = 3
FY2022 EPS conflict still records both original and restated observations
FY2022 basic-WAS conflict still records both observations
FY2022 dilutive-share conflict still records both observations
```

G6 may consume those observations as evidence; it must not erase or “resolve away” the conflict artifact.

- [ ] **Step 7: Regenerate standardized output through production code**

Use the same validated extraction → reconciliation → `standardize_reconciled()` path already used by the benchmark tests/scripts. Do not edit JSON by hand. Then inspect the diff and require the narrow `historical_shares` change described above.

- [ ] **Step 8: Run Fast Retailing acceptance tests**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

---

### Task 5: Full regression, audit, documentation, and stop

**Files:**
- Modify after measured verification: `benchmark/fast_retailing/GAPS.md`
- Modify after measured verification: `benchmark/fast_retailing/BASELINE.md`
- Modify after measured verification: `RESULT.md`
- Modify status/check boxes in `IMPLEMENTATION.md` only after fresh verification

- [ ] **Step 1: Run the focused G6 suite**

```bash
PYTHONPATH=. pytest \
  core/tests/test_share_basis.py \
  core/tests/test_filing_reconciler.py \
  core/tests/test_per_share.py \
  core/tests/test_per_share_attribution.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -v
```

Record the literal pass count; do not pre-fill it.

- [ ] **Step 2: Run the full historical suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Record the literal pass count.

- [ ] **Step 3: Run the staged benchmark audit**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require Stages 1–7 all pass. Record literal Stage-4 module/spec counts and Stage-6/7 Check totals. Expected catalog arithmetic is `380`, but measured output is authoritative.

- [ ] **Step 4: Verify source and audit artifacts did not drift**

```bash
git diff -- \
  benchmark/fast_retailing/source/ \
  benchmark/fast_retailing/extracted/ \
  benchmark/fast_retailing/reconciled/provenance.json \
  benchmark/fast_retailing/reconciled/conflicts.json
```

Expected: no output.

Then inspect:

```bash
git diff -- benchmark/fast_retailing/reconciled/standardized.json
```

Require only the intended `historical_shares` comparable-basis activation.

- [ ] **Step 5: Verify prior accounting behavior and forecast isolation**

Run the existing Step 9M.3B lease-treatment regressions, Step 9M.3C ownership-attribution regressions, and normal-build scenario/forecast isolation regression. Family IDs/orders remain unchanged; G6 activates existing per-share families rather than adding new family orders.

- [ ] **Step 6: Update measured documentation**

If the acceptance criteria pass, update:

```text
G6 -> CLOSED in Step 9M.3D
G7 -> remains OPEN
```

Document explicitly:

```text
raw extracted share facts preserved
one 3-for-1 factor inferred from an audited same-period restatement anchor
FY2021 comparable share count analytically adjusted, not falsely labeled reported
FY2022 later audited restated share presentation selected
historical_shares emitted in financial-statement units
per-share numerator remains parent-attributable under G5
G7 conflicts preserved unchanged
```

Update `BASELINE.md` with actual per-share applicability, spec counts, Check totals, and the five-year comparable share axis. Update `RESULT.md` with literal test/audit evidence.

- [ ] **Step 7: Mark complete only after fresh evidence, then stop**

At the top of `IMPLEMENTATION.md`, record actual focused/full test counts and actual benchmark stage/count results. Mark checkboxes complete only for steps actually run.

Do not begin G7 in this checkpoint. Return the implementation/test summary to the user so they can run `checkpoint`; ChatGPT will then review whether G7 requires a code change, an audit/presentation improvement, or should remain an intentionally preserved conflict state.
