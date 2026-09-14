# Step 9M.2.2 — Repair PPE Balance Boundaries and Liability Preservation (G2)

**Base:** `ba110d4283616b3f336292d0cad35befe60569a8`
**Status:** PROBLEMS — repair G2 before advancing.
**Goal:** Recognize PPE balances without reclassifying payables or admitting PPE movements.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`.
- Preserve source facts, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, G3–G7 implementation, or forecasting/valuation work.

## Task 1 — Bound PPE classification and close fallback escapes

- Replace PPE phrase-substring matching with normalized whole-label balance matching; retain supported punctuation, plant wording, and leading/trailing `net` variants.
- Preserve exact balance concepts `property_plant_equipment` and `property_plant_and_equipment`, neutral-label concept recognition, and explicit override precedence.
- Prevent PPE label recognition inside `_classify_by_concept` or label fallbacks from preempting existing payable/liability classification.
- Reject PPE movement variants regardless of marker position, including trailing additions, disposals, payments, sales, and changes, with singular/plural forms.
- Ensure movement rejection cannot fall through to legacy plant/PPE asset matching. Preserve legitimate PPE balances and unrelated classification behavior.

## Task 2 — Add public-path regressions

- Assert `Accounts payable for property and equipment` and `Property and equipment payable` remain `Operating Working Capital Liability`, with empty, unrelated, and applicable payable concepts.
- Assert `Property and equipment additions` and equivalent trailing movement variants raise `UnclassifiedBalanceSheetLineError`; cover generic and plant wording.
- Cover movement labels with empty, unrelated, and exact PPE balance concepts, plus balance labels carrying movement concepts.
- Replace the regression that expects `Purchases of property, plant and equipment` to classify as an asset with fail-closed expectations.
- Retain positive balance, concept-only, no-judgment, and override tests; verify explicit overrides still win for rejected movements.
- Extend resolver near-match tests for the reported movement variants with no explicit balance identity; preserve canonical/alias priority, ambiguity, and stored concepts.

## Task 3 — Verify G2 and record measured completion

- Confirm unchanged Lululemon PPE resolves to its original item/index with all four values intact and `fixed_asset_applicable` true.
- Preserve exactly `{Common stock}` as the unclassified set and `Common stock` as the temporary build probe’s first exception.
- Retain G1 coverage, fixed-asset calculations, deterministic reconciliation, and artifact immutability guards.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Update `RESULT.md` to supersede the unsupported G2 closure with repaired behavior, measured command results, artifact hashes before/after, remaining blockers, and final diff scope. Record failures or execution restrictions explicitly.

## Acceptance and next step

- PPE balance matching preserves payable/liability categories and rejects movement variants through the public classifier, including legacy fallback paths.
- Valid PPE classification, resolver identity, fixed-asset behavior, and the exact Lululemon G3 blocker remain intact.
- Required checks pass and committed artifacts remain unchanged; incomplete verification does not establish PASS.
- On failure, retain **Step 9M.2.2 — Repair PPE Balance Boundaries and Liability Preservation (G2)**.
- On PASS, propose **Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)**; Step 9 remains incomplete.
