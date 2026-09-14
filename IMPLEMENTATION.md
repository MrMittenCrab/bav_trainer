# Step 9M.1.1 — Filing-JSON Hardening Acceptance and Closure

**Base:** `af02e2e575ab95e5ecd6b2047d395b4002098a07`
**Incoming review:** PROBLEMS
**Goal:** Reconcile Step 9M.1.1 acceptance evidence, repair only remaining hardening defects, record closure, and stop.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`; Cursor must never modify either.
**Writable:** `RESULT.md`; only demonstrated hardening repairs in `core/ingestion/filing_{json,validator,reconciler,standardizer}.py`, corresponding `core/tests/test_filing_*.py`, `core/tests/test_fast_retailing_benchmark.py`, and `scripts/audit_fast_retailing_benchmark.py`.

### Task 1: Reconcile the detailed acceptance scope

- Read the Step 9M.1.1 plan at `d3b808b:IMPLEMENTATION.md`, completion record at `a707408:RESULT.md`, and current implementation/tests.
- In `RESULT.md`, map each original acceptance requirement to current code, named tests, measured evidence, and any remaining defect.
- Cover strict required metadata and exact dates; portable source-root containment before source access; complete bound-source registry; source-bound supplemental provenance; deterministic supplemental conflicts; and fail-closed share promotion.
- Reconcile the original synthetic-workbook drift requirement using historical blob evidence and subsequent intentional changes. Do not restore obsolete workbook bytes or undo accepted later functionality.
- Treat historical family counts, share omission, and G1–G7 status as historical evidence; verify current behavior without reverting subsequent accepted work.
- Preserve the existing formatting-verification evidence as separately identified prior work; it does not establish filing-JSON hardening closure.

### Task 2: Repair only demonstrated hardening defects

- Add focused failing regressions for uncovered acceptance failures, then make the smallest necessary fixes. If all hardening behavior passes, change only the completion record.
- Verify all bound filings remain represented, including filings whose statement observations lose precedence and supplemental-only contributors.
- Verify supplemental observations retain filing year, filename, computed SHA-256, page-level evidence, and derivations; disagreements remain explicit and cannot select shares by input order.
- Preserve current explicit share-basis policies, statement precedence, documentary values, and model-only `StandardizedFinancials`.
- Keep source inputs, committed generated artifacts, workbook surfaces, accounting features, and forecasting behavior unchanged.

### Task 3: Measure acceptance and record closure

- Run `python -m pytest core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_fast_retailing_benchmark.py -q`.
- Reconcile `benchmark/fast_retailing/extracted` against `benchmark/fast_retailing/source` into two fresh temporary directories using `python -m core reconcile`; compare all three output artifacts for deterministic equality.
- Measure source-registry completeness, computed source hashes, statement/supplemental conflict counts, and current share-promotion evidence; explain discrepancies from historical records.
- Compare generated artifacts with current committed counterparts; investigate differences without overwriting them to obtain a pass.
- Run `python -m pytest core/tests -q`, `python -m core --help`, and `git diff --check`.
- Verify tests leave committed workbooks and benchmark artifacts unchanged.
- Record revision, exact commands, measured outcomes, acceptance mapping, artifact comparisons, changed files, and unresolved issues in `RESULT.md`.

### Acceptance and stop

- Every Step 9M.1.1 requirement has explicit evidence or a documented unresolved defect; generic Step 9 formatting completion is not substituted.
- Required verification passes, and no remaining hardening defect is known.
- Use review status `PASS`, `PROBLEMS`, or `BLOCKED`; successful closure is `PASS`, with completion `DONE` and next step `None`.
- If unresolved, retain Step 9M.1.1 and enumerate only its remaining work.
- Stop after closure. Do not plan or begin Step 9M.2 or any new stage; do not commit or push.
