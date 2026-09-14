# Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)

**Base:** `f718ef4d90a8c6a0ab22766c8b2b9ba73be3634a`
**Previous step:** Step 9M.2.1 — PASS per supplied review.
**Goal:** Classify generic property-and-equipment balances and resolve their PPE identity without changing source facts.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/model/line_resolver.py`, `core/tests/test_classification.py`, `core/tests/test_line_resolver.py`, `core/tests/test_fixed_asset.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`.
- Preserve source inputs, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, G3–G7 implementation, or forecasting/valuation work.

## Task 1 — Classify property-and-equipment balances

- Recognize `Property and equipment, net` and bounded generic property-and-equipment balance wording as `Operating Long-Term Asset`, without a new judgment case.
- Support exact PPE balance concepts `property_plant_equipment` and `property_plant_and_equipment`.
- Preserve explicit override precedence and existing PP&E classification behavior.
- Prevent the new matching from admitting purchases, proceeds, depreciation, impairment, or other PPE movement rows as PPE balances; retain unrelated liability and asset treatment.
- Add public-classifier regressions for the reported row, label-only and concept-only recognition, wording variants, misleading movement labels/concepts, and override precedence.

## Task 2 — Resolve canonical PPE identity

- In `line_resolver.py`, recognize `property_plant_and_equipment` as an explicit alias of canonical `property_plant_equipment`; leave stored `LineItem.concept` unchanged.
- Treat canonical and alias concepts at the same explicit-concept priority, ahead of label matches; multiple matching rows must raise `AmbiguousLineError`.
- Add exact normalized net-balance label aliases, including `property and equipment net` and `property plant and equipment net`.
- Test alias-only recognition with a neutral label, label-only recognition, concept precedence, duplicate canonical/alias ambiguity, and rejection of movement-label near matches.
- Verify fixed-asset availability and independently calculated PPE averages, turnover, and intensity using synthetic source values. Preserve first-period blanks and missing/ambiguous-source behavior.

## Task 3 — Verify benchmark progression and record completion

- On unchanged Lululemon standardized input, assert the PPE row classifies and resolves to the original item/index with all four period values intact; `fixed_asset_applicable` becomes true.
- Update benchmark expectations to exactly `{Common stock}` as the unclassified set and `Common stock` as the temporary build probe’s first exception.
- Retain G1 gift-card coverage, deterministic reconciliation, committed hashes, failure-path immutability, and no-issuer-branch guards.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Record completion, measured results, artifact hashes before/after verification, remaining blockers, and final diff scope in `RESULT.md`.
- Distinguish the supplied prior review’s 177 passing tests and seven reproduced base failures from the excluded mismatched log. Record new failures or execution restrictions explicitly; do not reuse unsupported full-suite claims.

## Acceptance and next step

- Generic PPE classification and canonical resolution succeed without source mutation, unsafe new matches, or silent ambiguity.
- Lululemon fixed-asset availability is restored; the build advances to the exact G3 `Common stock` blocker.
- Required checks pass and committed artifacts remain unchanged; any verification restriction is explicitly recorded.
- On failure, retain **Step 9M.2.2 — Generic Property-and-Equipment Classification and PPE Identity (G2)**.
- On PASS, propose **Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)**; Step 9 remains incomplete.
