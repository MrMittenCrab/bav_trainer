# Step 9M.3D Repair — Complete Same-Period Share Validation

**Base:** `afa5e3331ad6104f976fc8d38160d3ec810eb8cd`

**Goal:** Require every eligible same-period share presentation to agree with the single audited split anchor before emitting a comparable share axis.

### Task 1: Add contradictory-presentation regressions

**File:** `core/tests/test_share_basis.py`

- [x] Extend the existing 2023-anchored 3-for-1 fixture: FY2022 diluted WAS is `100` in filing 2022 and `300` in filing 2023.
- [x] Parameterize additional FY2022 presentations: filing 2021 value `90`, filing 2024 value `310`, and filing 2024 value `900` must each return `None`; matching additional values `100` before and `300` after the anchor must preserve the existing axis and metadata.
- [x] Cover reported and valid derived diluted WAS, conflicting duplicate observations within a filing, and contradictory additional reported basic/dilutive components, including duplicates hidden behind a matching first observation.
- [x] Repeat cases with reordered observations; acceptance and rejection must be order-independent. Run `PYTHONPATH=. pytest core/tests/test_share_basis.py -q` and confirm the new contradiction cases fail before the repair.

### Task 2: Validate complete presentation groups

**File:** `core/ingestion/share_basis.py`

- [x] In `resolve_historical_share_basis()`, validate all eligible observations for each modeled period against the anchor filing-year boundary. Require one consistent pre-anchor value and one consistent post-anchor value wherever those groups exist; when both exist, require `post = pre × split_factor`.
- [x] Reject contradictions before selecting an axis value, including periods handled by `restated_was_by_period`. Preserve the existing audited EPS anchor, integer-factor, single-event, derived-observation eligibility, and EPS-rounding contracts.
- [x] Replace first-observation component checks in `_components_support_factor()` with validation of all available reported basic/dilutive presentations: same-side values must agree, and values on opposite sides must reconcile to the factor. Preserve valid zero/zero components and reject zero/nonzero contradictions.
- [x] Keep raw observations and conflicts immutable. Run `PYTHONPATH=. pytest core/tests/test_share_basis.py -q` and require all cases to pass.

### Task 3: Verify fail-closed integration and benchmark preservation

**Files:** `core/tests/test_filing_reconciler.py`, `core/tests/test_fast_retailing_benchmark.py`, `RESULT.md`

- [x] Add a standardization regression with a valid split anchor plus a contradictory additional presentation. Require `historical_shares=None`, otherwise intact standardized statements, and unchanged reconciliation observations/conflicts.
- [x] Retain Fast Retailing assertions for the FY2021–FY2025 financial-statement-unit axis: `306.871785`, `306.969624`, `307.138870`, `307.231804`, `307.247804`; adjustment factors remain `3, 1, 1, 1, 1`, with parent-attributable per-share earnings.
- [x] Run `PYTHONPATH=. pytest core/tests/test_share_basis.py core/tests/test_filing_reconciler.py core/tests/test_fast_retailing_benchmark.py -q`, then `PYTHONPATH=. pytest core/tests/ -q`, and `PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py`.
- [x] Require Stages 1–7 passing, `expected_specs=380`, blank Check `0 correct / 0 incorrect / 380 blank`, and filled Check `380 correct / 0 incorrect / 0 blank`.
- [x] Verify extracted facts and committed `reconciled/standardized.json`, `reconciled/provenance.json`, and `reconciled/conflicts.json` under `benchmark/fast_retailing/` remain unchanged; overlap/supplemental conflicts remain `3/3`, with G7 open.
- [x] Record actual test counts and audit results in `RESULT.md`; mark completed checkboxes only after verification.
