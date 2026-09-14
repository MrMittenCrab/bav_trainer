# Step 9M.2 — Repair Failure-Path Artifact Immutability Verification

**Base:** `9bb3880dc75fbca5ff9c8f0b14585bb405818bd2`
**Status:** PROBLEMS
**Goal:** Verify committed reconciliation bytes even when reconciliation or comparison fails.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit changes to `core/tests/test_lululemon_benchmark.py` and `RESULT.md`.
- Preserve committed artifacts, baseline hashes, source inputs, production behavior, and existing benchmark assertions.
- Keep generated artifacts and workbooks in temporary directories; never refresh or restore expected fixtures inside tests.

## Task 1 — Guarantee verification on failure

- In `test_generic_reconcile_is_deterministic`, snapshot all three committed artifacts before either reconciliation run.
- Put both subprocess runs, stdout assertions, inter-run comparisons, and committed-baseline comparisons inside `try`.
- Move the committed-byte reread and equality assertion into `finally`.
- Preserve the original exception when committed bytes are unchanged; report immutability failures with affected artifact names.

## Task 2 — Cover the guarded failure paths

- Exercise the same guarded execution path used by the benchmark, using monkeypatching and temporary expected artifacts.
- Inject subprocess failure at each reconciliation pass and comparison failure at both inter-run and committed-baseline comparisons.
- Assert each failure propagates and the final reread verifies all three artifacts.
- Using temporary expected copies only, simulate artifact mutation before an injected failure; parameterize across `ARTIFACT_NAMES` and require the final guard to detect and identify the mutation without restoring it.
- Retain the existing parameterized drift regression. New regressions must fail if final verification is moved back after the guarded block.

## Task 3 — Verify and record

Run:

- `PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py -q`
- `PYTHONPATH=. pytest core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py -q`
- `PYTHONPATH=. pytest core/tests -q`

Capture SHA-256 hashes of `benchmark/lululemon/reconciled/{standardized,provenance,conflicts}.json` before and after verification; inspect repository changes.

Update `RESULT.md` with the repair, measured command results, failure-path coverage, before/after hashes, and remaining failures. Supersede the previous PASS assessment.

## Acceptance and next step

- Final committed-byte verification runs after success, subprocess failure, and comparison failure.
- Unchanged artifacts preserve the original failure; temporary artifact mutations are detected without rewriting evidence.
- Both successful reconciliation runs still match each other and all three committed artifacts byte-for-byte.
- Required checks pass and committed artifact hashes remain unchanged.
- On failure, retain **Step 9M.2 — Repair Failure-Path Artifact Immutability Verification**.
- On PASS, propose **Step 9M.2.1 — Generic Gift-Card / Deferred-Revenue Liability Classification (G1)**; Step 9 remains incomplete.
