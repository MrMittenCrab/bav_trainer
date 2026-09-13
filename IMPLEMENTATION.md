# Step 9M.6 — Lease ROU-Asset Intensity & Trends

**Base:** `8003cc1089135b005bde209197a09a3944453d67`

**Goal:** Add source-gated historical right-of-use asset diagnostics to ALT DuPont and workbook-wide Check.

### Task 1: Define ROU resolution and calculations

**Files:** `core/model/line_resolver.py`, new `core/model/lease_rou.py`

- [x] Resolve BS `right_of_use_assets` by unique exact concept only; omit the module for absent, label-only, or ambiguous matches.
- [x] Require reported values for every historical period through `required_period_value`; incomplete resolved history raises the existing missing-value error.
- [x] Compute change, growth, average ROU assets, and average ROU assets/revenue. Use existing chronological-period and undefined-ratio conventions.
- [x] Keep applicability independent of lease-liability availability and classification treatment.

### Task 2: Integrate workbook practice and Check

**Files:** `core/engine/component_catalog.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, `core/trainer/checker.py`

- [x] Add `LEASE ROU-ASSET CONTEXT` to ALT DuPont with populated source-linked balances.
- [x] Register four semantic practice families: `rou_assets_change`, `rou_assets_growth`, `average_rou_assets`, and `rou_assets_to_revenue`; intensity uses average ROU assets/current revenue.
- [x] Leave all four first-period diagnostics genuinely blank in both workbooks and outside practice; register later periods only.
- [x] Connect expected series to Check. Preserve blank yellow Trainer practice cells without Notes and matching Answer-Key formulas with concise Notes.
- [x] Explain intensity as balance context; exclude lease-payment, discount-rate, amortization, and liability-reconciliation calculations.

### Task 3: Verify synthetic and real-company behavior

**Files:** new `core/tests/test_lease_rou.py`, `core/tests/test_fast_retailing_benchmark.py`, `scripts/audit_fast_retailing_benchmark.py`, `benchmark/fast_retailing/BASELINE.md`, `docs/GOOGL_HISTORICAL_REFERENCE.md`

- [x] Cover unique, absent, label-only, duplicate, and incomplete ROU inputs; zero prior balance, zero revenue, and one-period history.
- [x] Assert numerical calculations, semantic mapping after source-row reordering, first-period `.value is None`, populated balances, formula/Note parity, and blank/correct/incorrect non-disclosing Check behavior.
- [x] Verify activation without lease liabilities and omission without changing existing DEMO practice counts.
- [x] Verify Fast Retailing FY2025 ROU assets equal supplied `477111`; five-year history adds 16 practice cells, taking `expected_specs` from 438 to 454.
- [x] Add ROU availability/count reporting, refresh benchmark assertions and measured baseline, and mark this bounded gap implemented in the reference audit.

### Validation and acceptance

- [x] Run `python -m pytest core/tests/test_lease_rou.py core/tests/test_lease_liability.py core/tests/test_goodwill_intangibles.py core/tests/test_fast_retailing_benchmark.py core/tests/test_reference_workbook_audit.py core/tests/test_cross_company_robustness.py`.
- [x] Run `git diff --check`.
- [x] Fast Retailing blank Check reports `0/0/454`; filled Check reports `454/0/0`; existing goodwill/intangibles and lease-liability counts remain unchanged.
