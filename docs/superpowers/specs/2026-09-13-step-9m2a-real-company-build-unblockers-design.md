# Step 9M.2A Real-Company Build Unblockers Design

## Purpose

Move the Fast Retailing real-company benchmark past the first two generic accounting-engine blockers without broadening scope into leases, NCI, per-share reconstruction, forecasting, valuation, or company-specific patches.

Step 9M.2A closes only:

- **G1** — published balance-sheet totals that differ by one presentation unit because of audited rounding;
- **G2** — generic financial-instrument balance-sheet rows that currently hard-stop classification before the Accounting Judgment workflow can be built.

The step ends by re-running the Fast Retailing stage audit and recording the next genuine blocker after G1/G2.

## Accepted implementation base

Use commit `260268b6361d89ccb9fd3d13ddbc0ef5ee633fed` (`Step 9M.1.1`) on `checkpoint/20260913-183303` as the accepted base.

Step 9M.1.1 already established the source-grounded filing JSON boundary, deterministic source binding/reconciliation, source-bound supplemental provenance, explicit supplemental conflicts, strict portable source paths, and no silent share overwrite. Step 9M.2A must not reopen that input architecture.

## Scope

### In scope

1. A documented balance-sheet rounding tolerance that accepts an absolute residual of at most one reporting unit.
2. Continued rejection of material balance-sheet imbalances.
3. No balancing plug, source mutation, or silent adjustment to reported totals.
4. Conservative concept-based recognition of generic financial-instrument rows when the standardized concept explicitly identifies both financial nature and balance-sheet side/currentness.
5. Guided Accounting Judgment cases for recognized generic financial assets/liabilities and derivatives, so the learner can choose financial versus operating treatment.
6. Fast Retailing audit progression beyond the present G1/G2 stops.
7. Regression coverage proving synthetic surfaces and unrelated historical modules remain unchanged.

### Out of scope

- G3 split lease-liability aggregation;
- G4 lease-interest/NOPAT consistency;
- G5 NCI/parent attribution modeling;
- G6 historical diluted-share reconstruction across the stock split;
- changing G7 filing reconciliation precedence/conflict behavior;
- automatic PDF/AI extraction;
- forecasting, scenarios, valuation, or investment conclusions;
- company-specific `if ticker == 6288.HK` logic;
- automatic classification of vague balance-sheet rows whose concept does not provide enough side/nature evidence.

## Design principles

### 1. G1 is tolerance, not repair

Fast Retailing publishes FY2023/FY2024 statement totals with:

```text
abs(Total Assets - (Total Liabilities + Total Equity)) = 1
```

The current standardized balance-sheet checksum uses a `0.5` tolerance, while the downstream reformulation integrity check already uses a default tolerance of `1.0`. This makes the audit fail at reconciliation before reaching the accounting model even though the downstream engine already treats a one-unit residual as tolerable.

Step 9M.2A should align the standardized balance-sheet checksum with an explicit **one reporting-unit tolerance**:

```text
residual <= 1.0  -> checksum passes
residual > 1.0   -> checksum fails
```

This is an arithmetic acceptance policy only. It must not:

- modify assets, liabilities, or equity;
- create an `Other`/plug line;
- redistribute the residual across detail rows;
- alter the source filing JSON or reconciled standardized payload.

The original residual remains observable from reported totals.

### 2. G2 should become a guided judgment, not an auto-classification shortcut

The classifier currently raises `UnclassifiedBalanceSheetLineError` for rows it cannot safely classify. That fail-closed default remains correct for genuinely vague rows.

However, Fast Retailing's standardized concepts distinguish rows such as:

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

Those concepts provide two strong signals:

1. **nature:** financial asset or financial liability;
2. **side/currentness:** current asset, non-current asset, current liability, or non-current liability.

The model may therefore use a financial default while marking the decision ambiguous and exposing an operating alternative through the existing Accounting Judgment workflow.

The default/alternative pairs are:

| Concept side | Supplied reference treatment | Alternative |
|---|---|---|
| current financial asset | Financial Asset | Operating Working Capital Asset |
| non-current financial asset | Financial Asset | Operating Long-Term Asset |
| current financial liability | Financial Liability | Operating Working Capital Liability |
| non-current financial liability | Financial Liability | Operating Long-Term Liability |

This applies equally to derivative and non-derivative generic financial-instrument concepts when the concept token explicitly contains the required asset/liability + current/noncurrent signal.

A label alone such as `Other financial assets` is not sufficient if its concept is absent or does not encode the side. Such a row should continue to fail closed or require an explicit override.

### 3. Accounting Judgment remains the user-facing ambiguity mechanism

Add explicit judgment templates rather than silently making the classification final. Use four side-aware judgment codes so each case has a correct operating alternative:

```text
financial_asset_current_financial_vs_operating
financial_asset_noncurrent_financial_vs_operating
financial_liability_current_financial_vs_operating
financial_liability_noncurrent_financial_vs_operating
```

Each generated case should:

- use the existing exact `identity:` override selector;
- show the supplied financial treatment;
- show one operating alternative appropriate to currentness/side;
- explain that classification depends on economic purpose/hedging relationship rather than the word `financial` alone;
- state the mechanical consequence for NOWC/NOLA/NOA versus Net Debt;
- remain ungraded as a reasoning choice, consistent with the existing judgment workflow.

Derivative rows do not receive special automatic economic treatment beyond this. A derivative can be operating when tied to operating hedges or financial when used for financing/investment purposes; the reference default is financial absent stronger operating evidence.

### 4. No broad generic fallback

Do not add logic equivalent to:

```python
if "financial" in label:
    return Financial Asset / Financial Liability
```

Do not classify based on presentation order.

Do not infer current/non-current from values or neighboring rows.

Recognition must come from the standardized concept token. If the concept does not clearly identify both the financial nature and the relevant side/currentness, preserve the existing hard failure/override requirement.

## Component changes

### `core/data/validators.py`

Make balance-sheet identity tolerance explicit and reusable within the validator. The default must be `1.0` reporting unit. Tests must cover `0`, `0.5`, `1.0`, and a value strictly above `1.0`.

No source values are rewritten.

### `core/ingestion/reconciler.py`

No reconciliation architecture change is needed. `reconcile_financials()` should simply inherit the revised balance-sheet checksum semantics through `validate_balance_sheet()`.

Warnings remain reserved for checksum failure. A residual within the accepted tolerance should not produce a generic "does not balance" warning.

### `core/model/classification.py`

Extend `_classify_by_concept()` with narrowly defined, side-aware generic financial-instrument patterns.

Recognition should cover at least the Fast Retailing concept families above while remaining company-agnostic. The implementation should prefer explicit token tests over label heuristics.

Return `ClassificationDecision` with:

- category = financial default;
- `ambiguous=True`;
- a clear reason;
- one of the four new judgment codes.

Do not change behavior for concepts that are already classified more specifically, such as cash, lease liabilities, deferred tax, equity-method investments, or explicit borrowings.

### `core/model/judgment.py`

Add four `ClassificationJudgmentTemplate` entries matching the new judgment codes and category pairs.

The first option must exactly equal the classifier's supplied category because `classification_judgment_cases()` validates this invariant.

### Tests

Primary files:

```text
core/tests/test_classification.py
core/tests/test_reference_integrity.py
core/tests/test_fast_retailing_benchmark.py
```

Use additional existing judgment tests if that is where judgment-template behavior is already concentrated; do not create a parallel test architecture solely for this step.

## Required behavior tests

### G1 rounding tests

Require:

```text
residual 0.0  -> pass
residual 0.5  -> pass
residual 1.0  -> pass
residual 1.01 -> fail
```

Also require that the validator leaves all source values unchanged.

Fast Retailing FY2023/FY2024 balance-sheet checksum must pass without changing `benchmark/fast_retailing/reconciled/standardized.json`.

### G2 classification tests

For explicit concepts, require the following supplied decisions:

```text
other_financial_assets_current          -> Financial Asset, ambiguous
financial_assets_noncurrent             -> Financial Asset, ambiguous
derivative_financial_assets_current     -> Financial Asset, ambiguous
derivative_financial_assets_noncurrent  -> Financial Asset, ambiguous
other_financial_liabilities_current     -> Financial Liability, ambiguous
financial_liabilities_noncurrent        -> Financial Liability, ambiguous
derivative_financial_liabilities_current    -> Financial Liability, ambiguous
derivative_financial_liabilities_noncurrent -> Financial Liability, ambiguous
```

Each must carry the correct side-aware judgment code.

Require fail-closed behavior for a vague row such as:

```text
label = "Other financial assets"
concept = ""
```

unless an explicit classification override is supplied.

### Judgment-case tests

For at least one case of each of the four side-aware judgment codes, require:

- exact identity selector;
- supplied treatment = financial default;
- correct operating alternative;
- non-empty rationale/consequence text;
- override switches the reformulation category without changing reported equity/source values.

## Fast Retailing acceptance gate

Re-run:

```bash
PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py
```

Required Step 9M.2A result:

1. source fixture load passes;
2. identity validation passes;
3. financial reconciliation passes G1 without a plug;
4. `ReferenceModelBuilder` no longer fails on the G2 generic financial-instrument rows;
5. the audit continues until it reaches the next genuine blocker or completes later stages;
6. record that next blocker exactly; do not repair it unless it is still within G1/G2 scope.

If the next failure is a G3–G6 issue, stop and record it for the next planned checkpoint.

The benchmark's three statement overlap conflicts and three supplemental conflicts remain source/reconciliation evidence and must not be altered merely to make the engine greener.

## Regression constraints

Step 9M.2A must preserve:

- filing JSON schema and Step 9M.1.1 provenance semantics;
- Fast Retailing `standardized.json` source values;
- three statement overlap conflicts;
- three supplemental conflicts unless source evidence itself changes (which is out of scope);
- existing lease behavior;
- existing NCI behavior;
- existing per-share gating;
- existing forecast/valuation dormancy;
- Trainer/Answer Key learning mechanics;
- no company-specific code path;
- no new active historical formula family solely because G1/G2 were unblocked, except any Accounting Judgment rows generated by the existing judgment mechanism.

## Documentation updates

After implementation and fresh verification:

- update `benchmark/fast_retailing/GAPS.md` to mark G1 and G2 closed by Step 9M.2A and preserve G3–G7 status accurately;
- update `benchmark/fast_retailing/BASELINE.md` with the new stage results and first remaining blocker;
- update `RESULT.md` with actual focused/full test counts and audit outcome;
- mark `IMPLEMENTATION.md` complete only after all required verification commands pass.

Do not change `TARGET.md` for this checkpoint; the product intent already covers accounting judgment, consistency checks, and real-company validation.

## Definition of done

Step 9M.2A is complete only when all of the following are demonstrated by fresh tests/audit output:

1. one reporting-unit published BS residual is accepted without altering source values;
2. residuals greater than one unit still fail;
3. generic financial-instrument concepts with explicit side/currentness produce guided classification judgments rather than hard failures;
4. vague unsupported concepts still fail closed;
5. Fast Retailing Stage 3 passes;
6. Fast Retailing Stage 4 is no longer blocked by G2 rows;
7. the next actual benchmark blocker is recorded, not speculatively fixed;
8. G3–G7 remain outside this checkpoint except for documentation of the newly exposed failure;
9. full historical regression tests pass;
10. forecasting/valuation remain inactive.
