# Step 9 — Persistent Fast Retailing Release Pair

**Base:** `1547e262e68229e93b51d5fe0dbb8f4b6db04cce`
**Incoming review:** PROBLEMS
**Goal:** Generate and verify persistent, human-reviewable Fast Retailing historical Trainer and Answer Key through the production pipeline before resuming normal Step 9 work.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`; Cursor must never modify either file.
**Writable files:** `scripts/build_fast_retailing_release.py` (new), `scripts/audit_fast_retailing_benchmark.py`, `core/tests/test_fast_retailing_benchmark.py`, `release/fast_retailing/` (new), `RESULT.md`.

### Task 1: Add the reproducible release build

- Add `python scripts/build_fast_retailing_release.py`, resolving paths relative to the repository.
- Validate the existing source-manifest hashes and FY2021–FY2025 extracted filings against `benchmark/fast_retailing/source/`.
- Use the existing production reconciliation, standardization, reference-model, and workbook-generation entry points; do not copy temporary benchmark workbooks or duplicate financial calculations.
- Persist `FastRetailing_Trainer.xlsx` and `FastRetailing_Answer_Key.xlsx` under `release/fast_retailing/`, with any sidecars required by normal Check.
- Preserve generated standardized data, provenance, and conflicts in a supporting subdirectory; retain existing source facts and benchmark fixtures unchanged.
- Add a concise release README documenting dependencies, build command, workbook paths, and normal Check usage.
- Fail with a nonzero exit on validation, generation, or verification failure. Keep forecasting and valuation dormant.

### Task 2: Verify the actual release pair

- Extend the existing benchmark audit to accept explicit release workbook paths and generated standardized input while preserving its default test interface.
- Reuse benchmark checks against the persisted pair; do not regenerate substitute workbooks during release verification.
- Require all audit stages to pass and assert Check counts explicitly: pristine Trainer `(correct, incorrect, blank, total) = (0, 0, 491, 491)`; answer-filled copy `(491, 0, 0, 491)`.
- Perform all mutating Check and answer-fill operations on temporary copies with required sidecars; leave release workbooks pristine.
- Verify matching semantic practice cells, populated historical source facts, blank yellow Trainer cells without Notes, Answer Key formulas with non-empty Notes, and visible structural parity.
- Preserve existing benchmark expectations for company identity, FY2021–FY2025 periods, historical anchors, share basis, optional modules, and retained conflicts.
- Add regression coverage for explicit-pair verification, missing or mismatched artifacts, failed counts, and unchanged release files after verification.

### Task 3: Build, verify, and record

- Run the release build and verify the persistent pair.
- Repeat the build and compare workbook content, semantic maps, and audit payloads for reproducibility; exclude only documented packaging timestamps.
- Run `python -m pytest core/tests/test_fast_retailing_benchmark.py core/tests/test_historical_v1_exit_gate.py -q`.
- Run `python -m pytest core/tests -q` and `git diff --check`.
- Inspect the final changed-file list; exclude incidental test-generated changes while preserving pre-existing user changes.
- Record revision, exact commands, measured results, artifact paths and SHA-256 hashes, reproducibility comparison, and review status in `RESULT.md`.
- Use only PASS, PROBLEMS, or BLOCKED for review status. Carry any unfinished release requirement forward explicitly; keep further forecasting work deferred.

### Acceptance criteria

- Exactly two user-facing release workbooks persist under `release/fast_retailing/` and are reproducible from checked-in source-grounded inputs.
- Existing Fast Retailing benchmark checks verify that persisted pair successfully.
- Release Trainer remains pristine and the matching Answer Key remains usable for human review.
- Required checks pass; only writable files change. No commit or push.
