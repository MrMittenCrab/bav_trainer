# Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)

**Base:** `a86b9368095880bc3ad018d8d55b5ad3b41514fe`
**Previous step:** Step 9M.2.2 — PASS.
**Goal:** Classify ordinary common-stock balances safely as Equity and remove the remaining Lululemon classification blocker.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`.
- Preserve source facts, stored concepts, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, G4–G7 implementation, or forecasting/valuation work.

## Task 1 — Add guarded common-stock classification

- Recognize exact normalized `common_stock` balance concepts and whole-label `Common stock` balances as `Equity`, without ambiguity or a required judgment.
- Follow existing concept/label normalization conventions; do not use unrestricted `commonstock` substring matching.
- Prevent redeemable or mandatorily redeemable stock, preferred stock, stock investments, and issuance/repurchase/payment movements from entering the new ordinary-equity rule.
- Check contradictory labels and concepts before accepting common-stock identity; retain supported liability/investment behavior and fail closed for unsupported rows.
- Preserve explicit override precedence and existing equity-component, G1, and G2 behavior.

## Task 2 — Add public-classifier regressions

- Cover exact-concept recognition with a neutral label, whole-label recognition with empty/unrelated concepts, and case/whitespace variants.
- Assert valid balances return `Equity` with `ambiguous=False`.
- Cover excluded concepts paired with `Common stock` and excluded labels paired with exact `common_stock`, so either recognition route cannot bypass exclusions.
- Include redeemable stock, mandatory redemption, preferred stock, common-stock investments, issuance proceeds, and repurchase/payment movements.
- Retain liability, equity-method investment, existing equity-component, and explicit-override controls.

## Task 3 — Re-measure the benchmark and record completion

- Assert unchanged Lululemon `Common stock` / `common_stock` classifies as Equity with its original four-period values and identity intact.
- Replace the expected `{Common stock}` unclassified set with an empty set; retain gift-card, PPE, fixed-asset, reconciliation, and artifact-immutability assertions.
- Run the temporary-directory build probe past classification. Assert the measured next exception precisely, or assert successful workbook-pair creation if no exception occurs; do not repair downstream gaps.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Record G3 completion, measured command results, build outcome, artifact hashes before/after, remaining blockers, and final diff scope in `RESULT.md`. Record failures or execution restrictions explicitly.

## Acceptance and next step

- Ordinary common-stock balances classify deterministically as Equity; excluded instruments and movements cannot bypass guards.
- Lululemon has no unclassified balance-sheet detail rows, and the build probe advances beyond G3.
- Required checks pass; source facts and committed artifacts remain unchanged. Incomplete verification does not establish PASS.
- On failure, retain **Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)**.
- On PASS, propose **Step 9M.2.4 — Generic Capex Concept Identity (G4)** unless the measured build exposes a higher-priority blocker; record that blocker for the next bounded plan. Step 9 remains incomplete.
