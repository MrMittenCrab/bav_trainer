# Step 9M.7 — Deferred-Tax Balance Diagnostics

**Base:** `cb17c496a82413b40a9d51208a115b9f0e33013d`

**Goal:** Add source-gated deferred-tax balance diagnostics using Fast Retailing’s supplied DTA/DTL history.

### Task 1: Define the source contract and calculations — DONE

**Files:** `core/model/deferred_tax.py` (new), `core/model/line_resolver.py`

- Resolve BS `deferred_tax_assets` and `deferred_tax_liabilities` by unique exact concept only.
- Require both sources; missing or ambiguous sources omit the entire module. Missing modeled-period values raise `MissingHistoricalValueError`; never substitute zero.
- Compute signed net deferred-tax asset position as DTA − DTL for every period.
- Compute period changes in DTA, DTL, and net position; first-period changes are `None`.
- Preserve reported signs. Do not infer deferred-tax expense, cash-tax effects, recoverability, or legal offset eligibility.

### Task 2: Integrate workbook practice and Check — DONE

**Files:** `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/checker.py`

- Follow existing optional-module conventions with `deferred_tax` semantic keys and specs.
- Add `DEFERRED-TAX BALANCE CONTEXT` on ALT DuPont with populated DTA/DTL source links and four practice families: net position and the three changes.
- Label net position as analytical DTA less DTL; Notes must distinguish balance movements from tax expense or cash taxes.
- Register semantic formulas, expected values, and workbook-wide Check coverage.
- Keep first-period change cells genuinely empty in both workbooks; preserve Trainer/Answer-Key parity, yellow practice cells, and Answer-Key-only formulas and Notes.

### Task 3: Verify calculations, gating, and workbook behavior — DONE

**Files:** `core/tests/test_deferred_tax.py` (new), `core/tests/test_fast_retailing_benchmark.py`, `scripts/audit_fast_retailing_benchmark.py`

- Cover absent, partial, duplicate, label-only, missing-period, and explicit-zero sources; signed net liabilities; source-row reordering; and first-period blanks.
- Verify source balances remain populated and Check handles blank/correct/incorrect responses without disclosing answers.
- Verify FY2025 DTA `40889`, DTL `22539`, net position `18350`, and net-position change `17814`.
- Verify Fast Retailing adds 17 practice cells: `deferred_tax_specs=17`, `expected_specs=471`; blank Check `0/0/471`, filled Check `471/0/0`.
- Verify existing DEMO counts and other module counts remain unchanged.
- Run `python -m pytest core/tests/test_deferred_tax.py core/tests/test_fast_retailing_benchmark.py core/tests/test_lease_rou.py core/tests/test_goodwill_intangibles.py core/tests/test_reference_workbook_audit.py core/tests/test_cross_company_robustness.py`.

### Task 4: Record coverage and acceptance — DONE

**Files:** `docs/GOOGL_HISTORICAL_REFERENCE.md`, `benchmark/fast_retailing/BASELINE.md`, `IMPLEMENTATION.md`

- Update deferred-tax coverage and record measured benchmark results.
- Replace the unsupported SBC next-candidate entry with the remaining source-supported capex candidate; retain evidence-based deferrals.
- Record tested SHA, pass/fail/skip counts, and blockers; run `git diff --check`.

### Acceptance criteria

- Deferred-tax practice activates only under the defined source contract and passes calculation, workbook, and Check tests.
- Required tests pass without skipped workbook verification; benchmark counts match measured results.
- Source facts, retained conflicts, and existing accounting treatments remain unchanged.
- Forecasting and valuation remain deferred while source-supported Step 9 gaps remain.

### Verification (measured)

- **Tested working tree on HEAD:** `4838e0fc982fcc70f2ce5ac7fb31929c84b98770` (uncommitted Step 9M.7 implementation)
- **Required pytest:** `67 passed, 0 failed, 0 skipped`
- **Fast Retailing audit:** all stages pass; `deferred_tax_specs=17`, `expected_specs=471`; blank Check `0/0/471`; filled Check `471/0/0`
- **FY2025 anchors:** DTA `40889`, DTL `22539`, net `18350`, net-change `17814`
- **`git diff --check`:** clean
- **Blockers:** none
- **Next candidate:** Capex / reinvestment bridge (`payments_for_ppe`); SBC remains deferred (no Fast Retailing / DEMO SBC line)
