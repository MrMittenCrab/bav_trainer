# Step 9M.3E — Verify and Document Retained Conflict Policy

**Base:** `10f5bbd67e71c5b341d261213f157fb8df0ec64a`

**Goal:** Close G7 through explicit precedence and provenance verification while retaining all reported disagreements.

### Task 1: Verify generic overlap provenance

**File:** `core/tests/test_filing_reconciler.py`

- [x] Extend existing restated-comparative and later-comparative regressions to verify selected values, selection reasons, and every superseded observation in both reconciliation and serialized audit payloads.
- [x] Assert retained filing year, source filename, SHA-256, page, presentation role, and reported value.
- [x] Repeat with reversed filing input order; require identical selections and audit payloads.
- [x] Verify standardization consumes selected statement values without changing reconciliation observations or conflicts.

### Task 2: Lock Fast Retailing conflict acceptance

**File:** `core/tests/test_fast_retailing_benchmark.py`

- [x] Assert all three primary conflicts: FY2022 basic EPS `2675.30 → 891.77`, diluted EPS `2671.29 → 890.43`, and FY2024 financing “Others, net” `85 → 63`.
- [x] Require `restated_comparative_precedence` for both EPS conflicts and `later_audited_presentation` for the cash-flow conflict, with both source observations preserved.
- [x] Assert all three supplemental disagreements remain source-bound after share-basis resolution; retain the existing comparable-share-axis and parent-attributable EPS assertions.
- [x] Require unchanged extracted facts and committed reconciled artifacts, with overlap/supplemental conflict counts `3/3`.

### Task 3: Record the accepted policy and verification

**Files:** `benchmark/fast_retailing/GAPS.md`, `benchmark/fast_retailing/PROVENANCE.md`, `RESULT.md`

- [x] Document G7 as closed by verified deterministic selection and retained disagreements; closure does not mean source values agree or conflict records disappear.
- [x] Document the selected EPS and cash-flow presentations and their existing precedence reasons. Do not infer a cause for the cash-flow difference.
- [x] Replace obsolete claims that `historical_shares` remains omitted with the validated split-adjusted model-axis contract; distinguish analytical adjustment from unchanged reported facts.
- [x] Run `PYTHONPATH=. pytest core/tests/test_filing_reconciler.py core/tests/test_share_basis.py core/tests/test_fast_retailing_benchmark.py -q` and `PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py`.
- [x] Require Stages 1–7 passing, `expected_specs=380`, blank Check `0 correct / 0 incorrect / 380 blank`, and filled Check `380 correct / 0 incorrect / 0 blank`.
- [x] Record actual results in `RESULT.md`; close G7 only after these checks pass.
