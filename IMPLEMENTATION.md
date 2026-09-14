# Step 9M.2.2 — Normalize PPE Topic Detection and Reject Punctuation Movements (G2)

**Base:** `ab19f79ba93ce5eca0b59a92644ec0ece2d06476`
**Status:** PROBLEMS — repair G2 before advancing.
**Goal:** Reject PPE movements consistently across punctuation variants through the public classifier.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/model/classification.py`, `core/tests/test_classification.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`, and `RESULT.md`.
- Preserve source facts, committed reconciliation artifacts, baseline hashes, and failure-path immutability guards. Generate verification artifacts only in temporary directories.
- No issuer-specific rules, source relabeling, benchmark overrides, G3–G7 implementation, or forecasting/valuation work.

## Task 1 — Normalize PPE topic detection consistently

- Apply `_ppe_label_key` consistently to label topic detection and its phrase vocabulary, including comma, Oxford-comma, ampersand, and whitespace variants.
- Keep topic recognition distinct from whole-label balance recognition; do not broaden balance matching to substrings.
- Ensure `_is_ppe_movement` rejects normalized PPE topics before concept classification and legacy asset fallbacks, while explicit overrides retain precedence.
- Preserve exact PPE balance concepts, neutral-label concept recognition, supported `net` balances, payable/liability classification, and unrelated behavior.

## Task 2 — Add public-path punctuation regressions

- Through `classify_balance_sheet_line`, assert `Property plant & equipment additions` and `Property, plant, and equipment disposals` raise `UnclassifiedBalanceSheetLineError`.
- Parameterize both reported labels with empty, unrelated, and both exact PPE balance concepts so concept recognition cannot mask label-topic failures.
- Cover normalized topic variants with leading/trailing singular/plural movement markers, including additions, disposals, payments, sales, and changes.
- Add matching punctuation balance controls that remain `Operating Long-Term Asset`; retain payable, movement-concept, no-judgment, and explicit-override coverage.
- Extend resolver near-match regressions with both reported labels without explicit balance identity; preserve canonical/alias priority, ambiguity, and stored concepts.

## Task 3 — Verify and record measured completion

- Confirm unchanged Lululemon PPE resolves to its original item/index with all four values intact and `fixed_asset_applicable` true.
- Preserve exactly `{Common stock}` as the unclassified set and `Common stock` as the temporary build probe’s first exception.
- Retain G1 coverage, fixed-asset calculations, deterministic reconciliation, and artifact immutability guards.
- Run:
  - `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_fixed_asset.py core/tests/test_lululemon_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`
  - `PYTHONPATH=. pytest core/tests -q`
- Update `RESULT.md` to supersede the prior G2 PASS with the punctuation repair, measured command results, artifact hashes before/after, remaining blockers, and final diff scope. Record failures or execution restrictions explicitly.

## Acceptance and next step

- Both reported movements and their punctuation variants fail closed through the public classifier, including legacy fallback paths.
- Valid PPE balances, payable/liability categories, override precedence, resolver identity, and the exact Lululemon G3 blocker remain intact.
- Required checks pass and committed artifacts remain unchanged; incomplete verification does not establish PASS.
- On failure, retain **Step 9M.2.2 — Normalize PPE Topic Detection and Reject Punctuation Movements (G2)**.
- On PASS, propose **Step 9M.2.3 — Generic Common-Stock Equity Classification (G3)**; Step 9 remains incomplete.
