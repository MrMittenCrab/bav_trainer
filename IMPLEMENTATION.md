# Step 9M.2A — Real-Company Build Unblockers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **For Cursor:** Read `TARGET.md`, then `docs/superpowers/specs/2026-09-13-step-9m2a-real-company-build-unblockers-design.md`, then `benchmark/fast_retailing/GAPS.md`, then this plan in full. The accepted code base is `a707408d109037f11e3677d67f29b157cf6fa026` (`Step 9M.1.1`); the approved design is commit `37c0b843fd4ab9e432b5e9cfd923f42fd0471903`. Implement only Step 9M.2A using red/green TDD. Do not begin G3–G7 fixes, PDF/AI extraction, forecasting, valuation, scenarios, or investment conclusions. Do not commit, push, reset, rebase, merge, clean, or delete branches; the user owns checkpoint commits.

**Goal:** Close Fast Retailing G1 and G2 only: accept audited one-unit balance-sheet rounding residuals without plugs, and route clearly identified generic financial-instrument rows into the existing Accounting Judgment workflow instead of hard-failing classification.

**Architecture:** Keep source/reconciliation inputs immutable. G1 is a validator policy change: one reporting-unit balance-sheet residual is acceptable, anything larger still fails. G2 is a narrow concept-driven classification extension: explicit current/non-current financial asset/liability concepts receive a financial default plus a side-appropriate operating alternative through the existing judgment registry. Then rerun the real-company audit and stop at the next genuine blocker.

**Tech Stack:** Python, pytest, existing `StandardizedFinancials`, arithmetic validators/reconciler, balance-sheet classifier, judgment registry, `ReferenceModelBuilder`, Fast Retailing benchmark audit.

**Spec:** `docs/superpowers/specs/2026-09-13-step-9m2a-real-company-build-unblockers-design.md`

## Global Constraints

- `TARGET.md` is read-only for Cursor.
- Preserve the Step 9M.1.1 filing-JSON schema, source binding, provenance, and conflict semantics.
- Preserve all Fast Retailing reported/reconciled source values; do not change `benchmark/fast_retailing/reconciled/standardized.json` to make the engine pass.
- Do not add balancing plugs or mutate reported assets, liabilities, or equity.
- Accept only an absolute balance-sheet identity residual of at most **1.0 reporting unit**; values strictly above `1.0` fail.
- Keep the classifier fail-closed for vague unsupported lines.
- Generic financial-instrument recognition must require explicit standardized concept evidence for financial nature plus asset/liability side plus current/non-current status.
- Do not classify merely because a label contains the word `financial`.
- Preserve more-specific existing treatments for cash, borrowings/debt, leases, deferred tax, short-term investments, equity-method investments, pensions, and other already-supported categories.
- New generic financial-instrument decisions must be `ambiguous=True` and must enter the existing Accounting Judgment mechanism.
- Preserve the three Fast Retailing primary-statement overlap conflicts and three supplemental conflicts.
- Preserve existing lease behavior (G3/G4), NCI behavior (G5), share/per-share gating (G6), and reconciliation precedence (G7).
- No company-specific `6288.HK` / Fast Retailing branch in production code.
- No new forecast/valuation activation.
- No new active historical formula family solely because G1/G2 are unblocked; Accounting Judgment rows may increase only through the existing judgment-case mechanism.
- Cursor stops after implementation/tests and reports results; the user runs `checkpoint`.

---

### Task 1: Make one-unit balance-sheet rounding an explicit accepted tolerance (G1)

**Files:**
- Modify: `core/data/validators.py`
- Test: `core/tests/test_classification.py`
- Read only unless a test proves otherwise: `core/ingestion/reconciler.py`

**Interfaces:**
- Add `BALANCE_SHEET_TOLERANCE = 1.0` in `core/data/validators.py`.
- Change the validator signature to:

```python
def validate_balance_sheet(
    data: StandardizedFinancials,
    *,
    tolerance: float = BALANCE_SHEET_TOLERANCE,
) -> dict[date, bool]:
    ...
```

- `reconcile_financials(data)` continues to call `validate_balance_sheet(data)` and therefore inherits the default tolerance without a new reconciler API.

- [ ] **Step 1: Add a focused fixture for balance-sheet identity residuals**

In `core/tests/test_classification.py`, add a helper using the existing `P1`, `P2`, `_li()`, and `_periods()` helpers:

```python
def _balance_sheet_identity_fin(residual: float) -> StandardizedFinancials:
    assets = 100.0
    liabilities = 60.0
    equity = 40.0 - residual
    return StandardizedFinancials(
        ticker="ROUND",
        company_name="Rounding Co",
        currency="HKD",
        units="HKD in Millions",
        jurisdiction="HK",
        periods=_periods(),
        income_statement=[],
        balance_sheet=[
            _li("Total assets", assets, assets),
            _li("Total liabilities", liabilities, liabilities),
            _li("Total equity", equity, equity),
        ],
        cash_flow=[],
    )
```

Take a value snapshot before validation so the test can prove validation does not mutate source numbers.

- [ ] **Step 2: Add the four required tolerance cases**

Import `validate_balance_sheet` and add:

```python
@pytest.mark.parametrize(
    ("residual", "expected"),
    [
        (0.0, True),
        (0.5, True),
        (1.0, True),
        (1.01, False),
    ],
)
def test_balance_sheet_rounding_tolerance(residual, expected):
    fin = _balance_sheet_identity_fin(residual)
    before = [dict(item.values) for item in fin.balance_sheet]
    result = validate_balance_sheet(fin)
    assert set(result.values()) == {expected}
    assert [dict(item.values) for item in fin.balance_sheet] == before
```

- [ ] **Step 3: Add reconciler warning semantics**

Require the accepted one-unit residual to produce a passing balance-sheet checksum and no generic balance-sheet warning, while `1.01` still fails and warns:

```python
def test_reconciliation_accepts_one_unit_but_rejects_larger_residual():
    accepted = reconcile_financials(_balance_sheet_identity_fin(1.0))
    assert accepted.checksums["balance_sheet"] is True
    assert "Balance sheet does not balance for one or more periods" not in accepted.warnings

    rejected = reconcile_financials(_balance_sheet_identity_fin(1.01))
    assert rejected.checksums["balance_sheet"] is False
    assert "Balance sheet does not balance for one or more periods" in rejected.warnings
```

- [ ] **Step 4: Run the G1 tests red**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "balance_sheet_rounding_tolerance or reconciliation_accepts_one_unit" -v
```

Expected before implementation: the `1.0` residual case fails because the current checksum threshold is `0.5`.

- [ ] **Step 5: Implement the explicit tolerance**

In `core/data/validators.py`, add:

```python
BALANCE_SHEET_TOLERANCE = 1.0
```

and change the identity test from the hard-coded `0.5` to:

```python
elif abs(float(a) - (float(l) + float(e))) > tolerance:
    ok = False
```

Do not round, plug, rewrite, or normalize any values.

- [ ] **Step 6: Run the G1 tests green**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "balance_sheet_rounding_tolerance or reconciliation_accepts_one_unit" -v
```

Expected: all selected tests pass.

---

### Task 2: Recognize only explicit generic financial-instrument concepts (G2 classifier)

**Files:**
- Modify: `core/model/classification.py`
- Test: `core/tests/test_classification.py`

**Interfaces:**
- Preserve `classify_balance_sheet_line(item, *, override=None) -> ClassificationDecision`.
- Add no new public classification API.
- Introduce four exact judgment codes:

```text
financial_asset_current_financial_vs_operating
financial_asset_noncurrent_financial_vs_operating
financial_liability_current_financial_vs_operating
financial_liability_noncurrent_financial_vs_operating
```

- [ ] **Step 1: Add parameterized G2 classification tests**

Add the following exact cases to `core/tests/test_classification.py`:

```python
@pytest.mark.parametrize(
    ("label", "concept", "category", "code"),
    [
        (
            "Other financial assets",
            "other_financial_assets_current",
            "Financial Asset",
            "financial_asset_current_financial_vs_operating",
        ),
        (
            "Financial assets",
            "financial_assets_noncurrent",
            "Financial Asset",
            "financial_asset_noncurrent_financial_vs_operating",
        ),
        (
            "Derivative financial assets",
            "derivative_financial_assets_current",
            "Financial Asset",
            "financial_asset_current_financial_vs_operating",
        ),
        (
            "Derivative financial assets",
            "derivative_financial_assets_noncurrent",
            "Financial Asset",
            "financial_asset_noncurrent_financial_vs_operating",
        ),
        (
            "Other financial liabilities",
            "other_financial_liabilities_current",
            "Financial Liability",
            "financial_liability_current_financial_vs_operating",
        ),
        (
            "Financial liabilities",
            "financial_liabilities_noncurrent",
            "Financial Liability",
            "financial_liability_noncurrent_financial_vs_operating",
        ),
        (
            "Derivative financial liabilities",
            "derivative_financial_liabilities_current",
            "Financial Liability",
            "financial_liability_current_financial_vs_operating",
        ),
        (
            "Derivative financial liabilities",
            "derivative_financial_liabilities_noncurrent",
            "Financial Liability",
            "financial_liability_noncurrent_financial_vs_operating",
        ),
    ],
)
def test_generic_financial_concepts_become_guided_judgments(
    label, concept, category, code
):
    decision = classify_balance_sheet_line(
        LineItem(label=label, concept=concept, values={P1: 10, P2: 12})
    )
    assert decision.category == category
    assert decision.ambiguous is True
    assert decision.judgment_code == code
    assert decision.reason
```

- [ ] **Step 2: Add fail-closed and specificity regressions**

Require a generic label without usable concept evidence to remain unsupported:

```python
def test_generic_financial_label_without_side_concept_still_fails_closed():
    with pytest.raises(UnclassifiedBalanceSheetLineError):
        classify_balance_sheet_line(
            LineItem(
                label="Other financial assets",
                concept="",
                values={P1: 10, P2: 12},
            )
        )
```

Also require more-specific existing label behavior not to be displaced by a broad generic concept fallback:

```python
def test_generic_financial_concept_does_not_override_specific_existing_rules():
    cash = classify_balance_sheet_line(
        LineItem(
            label="Cash and cash equivalents",
            concept="financial_assets_current",
            values={P1: 10, P2: 12},
        )
    )
    assert cash.category == "Financial Asset"
    assert cash.ambiguous is False

    debt = classify_balance_sheet_line(
        LineItem(
            label="Bank borrowings",
            concept="financial_liabilities_noncurrent",
            values={P1: 10, P2: 12},
        )
    )
    assert debt.category == "Financial Liability"
    assert debt.ambiguous is False

    short_term_investment = classify_balance_sheet_line(
        LineItem(
            label="Short-term investments",
            concept="financial_assets_current",
            values={P1: 10, P2: 12},
        )
    )
    assert short_term_investment.judgment_code == (
        "short_term_investment_financial_vs_operating"
    )
```

- [ ] **Step 3: Run the G2 classifier tests red**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "generic_financial" -v
```

Expected before implementation: the eight explicit generic financial rows raise `UnclassifiedBalanceSheetLineError` or do not carry the required judgment codes.

- [ ] **Step 4: Implement a narrow concept-driven fallback**

At the end of `_classify_by_concept(item)`, after the existing strong concept rules and before `return None`, add a small private helper or equivalent inline logic with this behavior:

```python
def _generic_financial_concept_decision(
    item: LineItem,
) -> ClassificationDecision | None:
    c = _concept_token(item.concept or "")
    low = _norm(item.label)

    # Concept is authoritative for nature/side/currentness; label is only a gate
    # that this is genuinely a generic financial/derivative presentation row.
    if "financial" not in c:
        return None
    if not _match_any(
        low,
        (
            "financial asset",
            "financial liab",
            "derivative financial",
        ),
    ):
        return None

    if "noncurrent" in c:
        horizon = "noncurrent"
    elif "current" in c:
        horizon = "current"
    else:
        return None

    if "asset" in c and "liab" not in c:
        code = (
            "financial_asset_noncurrent_financial_vs_operating"
            if horizon == "noncurrent"
            else "financial_asset_current_financial_vs_operating"
        )
        return ClassificationDecision(
            "Financial Asset",
            ambiguous=True,
            reason=(
                "Generic financial-asset concept — financial vs operating "
                "purpose/hedging judgment"
            ),
            judgment_code=code,
        )

    if "liab" in c:
        code = (
            "financial_liability_noncurrent_financial_vs_operating"
            if horizon == "noncurrent"
            else "financial_liability_current_financial_vs_operating"
        )
        return ClassificationDecision(
            "Financial Liability",
            ambiguous=True,
            reason=(
                "Generic financial-liability concept — financial vs operating "
                "purpose/hedging judgment"
            ),
            judgment_code=code,
        )

    return None
```

Then have `_classify_by_concept()` return this fallback only after the existing more-specific concept rules.

The `noncurrent` check must occur before `current`, because the normalized token `noncurrent` contains the substring `current`.

Do not add any ticker/company checks. Do not broaden label-only classification.

- [ ] **Step 5: Run the G2 classifier tests green**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "generic_financial" -v
```

Expected: all selected tests pass, including the fail-closed and specificity cases.

---

### Task 3: Register side-aware Accounting Judgment templates and prove case generation

**Files:**
- Modify: `core/model/judgment.py`
- Test: `core/tests/test_classification.py`
- Test: `core/tests/test_reference_integrity.py`

**Interfaces:**
- Keep `ClassificationJudgmentTemplate`, `JudgmentCase`, and `classification_judgment_cases()` unchanged.
- Add four entries to `CLASSIFICATION_JUDGMENT_TEMPLATES` keyed by the four judgment codes from Task 2.

- [ ] **Step 1: Add the four exact registry templates**

The templates must use these exact option pairs:

```python
"financial_asset_current_financial_vs_operating": ClassificationJudgmentTemplate(
    topic="Current financial asset: financial vs operating",
    options=("Financial Asset", "Operating Working Capital Asset"),
    model_rationale=(
        "The reference model treats a generically disclosed current financial "
        "instrument as a financial asset absent evidence that it is integral to "
        "normal operations or an operating hedge."
    ),
    consequence_prompt=CONSEQUENCE_PROMPT,
    model_consequence=(
        "Financial-asset treatment lowers Net Debt; operating-WC treatment raises "
        "NOWC/NOA by the same balance. Implied equity is unchanged by the "
        "classification switch alone."
    ),
),
"financial_asset_noncurrent_financial_vs_operating": ClassificationJudgmentTemplate(
    topic="Non-current financial asset: financial vs operating",
    options=("Financial Asset", "Operating Long-Term Asset"),
    model_rationale=(
        "The reference model treats a generically disclosed non-current financial "
        "instrument as a financial asset absent evidence that it is strategically "
        "or operationally required."
    ),
    consequence_prompt=CONSEQUENCE_PROMPT,
    model_consequence=(
        "Financial-asset treatment lowers Net Debt; operating-LT treatment raises "
        "NOLA/NOA by the same balance. Implied equity is unchanged by the "
        "classification switch alone."
    ),
),
"financial_liability_current_financial_vs_operating": ClassificationJudgmentTemplate(
    topic="Current financial liability: financial vs operating",
    options=("Financial Liability", "Operating Working Capital Liability"),
    model_rationale=(
        "The reference model treats a generically disclosed current financial "
        "instrument as a financial liability absent evidence that it is an "
        "operating payable or operating hedge."
    ),
    consequence_prompt=CONSEQUENCE_PROMPT,
    model_consequence=(
        "Financial-liability treatment raises Net Debt; operating-WC-liability "
        "treatment lowers NOWC/NOA by the same balance. Implied equity is unchanged "
        "by the classification switch alone."
    ),
),
"financial_liability_noncurrent_financial_vs_operating": ClassificationJudgmentTemplate(
    topic="Non-current financial liability: financial vs operating",
    options=("Financial Liability", "Operating Long-Term Liability"),
    model_rationale=(
        "The reference model treats a generically disclosed non-current financial "
        "instrument as a financial liability absent evidence that it is an "
        "operating long-term obligation or operating hedge."
    ),
    consequence_prompt=CONSEQUENCE_PROMPT,
    model_consequence=(
        "Financial-liability treatment raises Net Debt; operating-LT-liability "
        "treatment lowers NOLA/NOA by the same balance. Implied equity is unchanged "
        "by the classification switch alone."
    ),
),
```

The first option must exactly equal the classifier's default category.

- [ ] **Step 2: Add a four-case synthetic judgment fixture**

In `core/tests/test_classification.py`, create a two-period `StandardizedFinancials` with these non-zero detail rows:

```text
Other financial assets / other_financial_assets_current             10, 11
Financial assets / financial_assets_noncurrent                      20, 21
Other financial liabilities / other_financial_liabilities_current    5,  6
Financial liabilities / financial_liabilities_noncurrent              7,  8
Share capital and reserves / retained_earnings                       18, 18
```

This gives assets `30/32`, liabilities `12/14`, and equity `18/18` without requiring reported total rows. Use `FinancialPeriod` objects for `P1/P2`; income statement and cash flow may be empty because this test exercises reformulation/judgment generation directly.

- [ ] **Step 3: Add judgment-case assertions**

Import `classification_judgment_cases` and require four cases. For each expected label, require:

```text
supplied_treatment = financial default
alternatives = exactly one side-appropriate operating category
override_selector starts with "identity:"
line_identity equals the identity suffix used by override_selector
model_rationale is non-empty
model_consequence is non-empty
```

Also apply one case's alternative via:

```python
reform_alt = reformulate_balance_sheet(
    fin,
    [P1, P2],
    overrides={case.override_selector: case.alternatives[0]},
)
```

and require:

- the selected detail decision changes to the alternative category;
- the underlying `LineItem.values` remain byte-for-byte/numerically unchanged;
- `implied_equity` is unchanged versus the reference classification;
- NOA and/or Net Debt move in the direction described by the template.

- [ ] **Step 4: Run the judgment tests red**

```bash
PYTHONPATH=. pytest core/tests/test_classification.py -k "generic_financial or judgment_case" -v
```

Expected before Task 3 implementation: `classification_judgment_cases()` raises for unsupported new judgment codes or cannot produce the required cases.

- [ ] **Step 5: Implement the registry entries**

Add only the four templates above to `CLASSIFICATION_JUDGMENT_TEMPLATES`. Do not add a new judgment engine or a second registry.

- [ ] **Step 6: Add a builder-level integration regression**

In `core/tests/test_reference_integrity.py`, create a minimal two-period `StandardizedFinancials` containing:

- the four generic financial-instrument rows from the synthetic fixture;
- one balancing equity row;
- required income-statement concepts for `revenue`, `net_income`, `pretax_income`, `tax_expense`, `interest_expense`, and `interest_income`;
- no optional cash-flow rows unless needed by the existing builder.

Instantiate:

```python
builder = ReferenceModelBuilder(fin)
```

and require that `builder.judgment_cases` contains the four expected supplied treatments/alternatives. This proves the existing Accounting Judgment workflow receives the cases; do not create a parallel workbook mechanism.

- [ ] **Step 7: Run Task 3 green**

```bash
PYTHONPATH=. pytest \
  core/tests/test_classification.py \
  core/tests/test_reference_integrity.py \
  -k "generic_financial or judgment_case" -v
```

Expected: all selected tests pass.

---

### Task 4: Prove Fast Retailing G1/G2 are unblocked and measure the next blocker

**Files:**
- Test: `core/tests/test_fast_retailing_benchmark.py`
- Modify: `scripts/audit_fast_retailing_benchmark.py`
- Generated by audit: `benchmark/fast_retailing/BASELINE.md`
- Read only: `benchmark/fast_retailing/reconciled/standardized.json`
- Read only: `benchmark/fast_retailing/reconciled/conflicts.json`

**Interfaces:**
- `run_audit()` remains the benchmark stage runner.
- Stage names remain:

```text
1_source_fixture_load
2_identity_validation
3_reconciliation
4_reference_model_builder
5_workbook_generation
6_blank_check
7_filled_check
```

- [ ] **Step 1: Add the Fast Retailing G1 acceptance assertion**

In `core/tests/test_fast_retailing_benchmark.py`, load `reconciled/standardized.json` through `standardized_from_payload()`, call `reconcile_financials(fin)`, and require:

```python
assert report.checksums["balance_sheet"] is True
assert "Balance sheet does not balance for one or more periods" not in report.warnings
```

Do not change the standardized fixture to make this pass.

- [ ] **Step 2: Add the Fast Retailing G2 row assertions**

For each Fast Retailing balance-sheet row whose concept is one of:

```text
other_financial_assets_current
financial_assets_noncurrent
derivative_financial_assets_current
derivative_financial_assets_noncurrent
other_financial_liabilities_current
financial_liabilities_noncurrent
derivative_financial_liabilities_current
derivative_financial_liabilities_noncurrent
```

require `classify_balance_sheet_line(item)` to return the financial default, `ambiguous=True`, and the correct side-aware judgment code from Task 2.

This test is the direct proof that the known G2 rows no longer hard-fail even if a later unrelated row becomes the next blocker.

- [ ] **Step 3: Add an audit-stage regression**

Call `run_audit()` and build:

```python
stages = {stage.stage: stage for stage in result["stages"]}
```

Require:

```python
assert stages["1_source_fixture_load"].status == "pass"
assert stages["2_identity_validation"].status == "pass"
assert stages["3_reconciliation"].status == "pass"
```

For Stage 4, do **not** pre-assume the whole builder now succeeds. Instead require that any Stage-4 `UnclassifiedBalanceSheetLineError` message no longer names any of the known G2 financial-instrument rows above. If Stage 4 passes, allow later stages to reveal the next blocker.

- [ ] **Step 4: Run the Fast Retailing acceptance tests**

```bash
PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v
```

Expected after Tasks 1–3: G1 assertions pass and G2-specific hard failures disappear. A newly exposed unrelated failure is acceptable only if recorded in the next steps.

- [ ] **Step 5: Run the real stage audit and capture the exact next blocker**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Read the entire stage output, not only the first line. Record exactly:

```text
first failing stage
exception type
full first-failure message
whether Stage 4 passed
whether workbook generation/check stages were reached
```

Do not fix the newly exposed failure in this checkpoint unless it is demonstrably still G1 or one of the eight explicit G2 financial-instrument concepts.

- [ ] **Step 6: Remove stale audit-version wording**

`scripts/audit_fast_retailing_benchmark.py` currently describes the audited accounting engine using the old Step 9L.1 commit constant. Replace that stale claim with phase wording that does not pretend to know the user's future checkpoint SHA, for example:

```text
- Accounting engine phase: Step 9M.2A (G1/G2 implementation on accepted Step 9M.1.1 base)
```

Update the generated baseline heading to:

```text
# Fast Retailing Benchmark Baseline (Step 9M.2A)
```

Do not add Git subprocess/version discovery solely for documentation.

- [ ] **Step 7: Re-run the audit after metadata cleanup**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Expected: same stage behavior and same measured next blocker as Step 5; only benchmark metadata wording changes.

---

### Task 5: Close G1/G2 documentation, run full regression, and stop

**Files:**
- Modify: `benchmark/fast_retailing/GAPS.md`
- Modify/generated: `benchmark/fast_retailing/BASELINE.md`
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status/checkmarks only after verification

**Interfaces:**
- Do not change `TARGET.md`.
- Do not change the filing-JSON design/spec in this task.

- [ ] **Step 1: Update the gap queue from measured evidence**

In `benchmark/fast_retailing/GAPS.md`:

- mark **G1 closed in Step 9M.2A** and state that `<= 1.0` reporting-unit residuals are accepted without plugs while `> 1.0` still fails;
- mark **G2 closed in Step 9M.2A** and state that explicit generic financial-instrument concepts now produce guided side-aware classification judgments while vague rows still fail closed;
- leave G3–G7 open unless the new audit proves that a listed item was already non-blocking by existing behavior;
- add a short **Post-9M.2A first remaining blocker** subsection containing the exact stage/exception/message observed in Task 4, or state that no blocker remained if all stages passed;
- do not implement or speculate a fix for that next blocker here.

- [ ] **Step 2: Update RESULT.md with actual evidence only**

Record the final observed values, including:

```text
Step 9M.2A scope: G1 + G2 only
G1 one-unit BS tolerance: pass
G2 generic financial rows: guided judgment, no hard stop
Fast Retailing Stage 3: <actual status>
Fast Retailing Stage 4: <actual status>
next blocker: <exact measured stage/type/message, or none>
statement overlap conflicts: 3
supplemental conflicts: 3
Fast Retailing standardized source payload changed: no
forecast/valuation activation: no
focused tests: <actual count>
full core tests: <actual count>
```

Replace the angle-bracket descriptions with the actual command output before marking the step complete; do not guess counts.

- [ ] **Step 3: Run the focused Step 9M.2A suite**

```bash
PYTHONPATH=. pytest \
  core/tests/test_classification.py \
  core/tests/test_reference_integrity.py \
  core/tests/test_fast_retailing_benchmark.py \
  -q
```

Expected: all pass. Record the actual pass count.

- [ ] **Step 4: Run the full historical regression suite**

```bash
PYTHONPATH=. pytest core/tests/ -q
```

Expected: all pass. Record the actual pass count.

- [ ] **Step 5: Verify source/reconciliation artifacts did not drift**

Run:

```bash
git diff -- benchmark/fast_retailing/reconciled/standardized.json
git diff -- benchmark/fast_retailing/reconciled/conflicts.json
```

Expected:

- no diff for `standardized.json`;
- no diff for `conflicts.json` unless the only change is benchmark formatting produced by code explicitly in scope (normally there should be no change at all because G1/G2 are downstream engine changes).

Then verify conflict counts from the committed artifact:

```bash
python - <<'PY'
import json
from pathlib import Path
p = json.loads(Path("benchmark/fast_retailing/reconciled/conflicts.json").read_text())
print("overlap", p["overlap_conflict_count"])
print("supplemental", p["supplemental_conflict_count"])
PY
```

Require:

```text
overlap 3
supplemental 3
```

- [ ] **Step 6: Verify unrelated workbook/source artifacts remain untouched**

```bash
git diff -- example/DEMO_HK_Trainer.xlsx
git diff -- benchmark/fast_retailing/extracted benchmark/fast_retailing/source
```

Expected: no output.

- [ ] **Step 7: Re-run the Fast Retailing audit as the final behavioral gate**

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Require:

```text
Stage 1 pass
Stage 2 pass
Stage 3 pass
known G2 financial-instrument rows no longer block Stage 4
```

If a later failure remains, it must exactly match the one recorded in `GAPS.md` / `RESULT.md`. Do not fix it in this checkpoint.

- [ ] **Step 8: Verify forecast/valuation isolation remains intact**

The full suite must still include the existing regression that normal historical builds do not call `run_scenario`. Also run the focused test explicitly:

```bash
PYTHONPATH=. pytest \
  core/tests/test_reference_integrity.py::test_normal_v1_build_does_not_call_run_scenario \
  -v
```

Expected: PASS.

- [ ] **Step 9: Mark Step 9M.2A complete only with fresh evidence**

At the top of `IMPLEMENTATION.md`, add a concise status line containing the actual focused/full test counts, Fast Retailing Stage 3/4 outcome, next measured blocker, unchanged conflict counts, unchanged standardized payload, and forecast/valuation isolation result.

Check every completed step `[x]` only after its command/test has actually run successfully.

- [ ] **Step 10: Stop**

Do not begin G3/G4 lease work, G5 NCI work, G6 share-basis work, G7 reconciliation changes, extraction automation, forecasting, valuation, or scenarios.

Return the implementation/test/audit summary to the user so they can inspect it and run `checkpoint` themselves.
