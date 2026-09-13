# Step 9M.5 — Goodwill & Intangible-Asset Diagnostics

**Base:** `f68db107064326fc50a9241d192d322f02fd62b5`

**Goal:** Add source-gated historical balance, change, and intensity diagnostics with optional intangible-payment ratios.

### Task 1: Enable explicit concept resolution

**Files:** `core/model/line_resolver.py`, `core/tests/test_line_resolver.py`

- [x] Register `goodwill`, `intangible_assets`, and `payments_for_intangible_assets` using existing normalized explicit-concept matching, without label or pattern fallback.
- [x] Preserve missing/required and ambiguity exceptions, existing concept behavior, and unknown-concept rejection.
- [x] Test unique, missing, duplicate, and label-only inputs for all three concepts.

### Task 2: Implement gated historical calculations

**Files:** new `core/model/goodwill_intangibles.py`, new `core/tests/test_goodwill_intangibles.py`

- [x] Resolve BS balances and optional CF payments through the shared resolver; treat ambiguous concepts as unavailable independently.
- [x] Omit the module unless at least one BS concept resolves; emit only available balance families and omit unavailable payment families.
- [x] Read supplied period values using existing strict source-value helpers; never substitute zero for missing facts.
- [x] For each available balance, calculate change, growth, average balance, and average balance/revenue. Leave first-period derived values blank; use existing `NA()` conventions for zero denominators.
- [x] Include `goodwill_and_intangibles` only when both BS concepts resolve.
- [x] Present intangible payments as `−reported payments` consistently across periods, plus payments/revenue; never apply absolute value.
- [x] Test partial availability, duplicates, missing periods, zero denominators, flat balances, and mixed payment signs.

### Task 3: Integrate the historical practice surface

**Files:** `core/engine/reference_model.py`, `core/engine/component_catalog.py`, `core/model/historical_expected.py`, `core/trainer/checker.py`

- [x] Add one optional ALT DuPont block using existing semantic family IDs, period expansion, dependency mapping, and registration conventions.
- [x] Keep linked source balances and signed CF facts populated; register derived calculations as practice cells.
- [x] Wire the same availability contract and calculations into Excel formulas, Python expected values, and workbook-wide Check.
- [x] Produce blank yellow Trainer practice cells without Notes and matching Answer-Key formulas with concise Notes.
- [x] Notes explain average-balance intensity and payment signs; state that flat goodwill does not establish absence of impairment and intangible payments are not business acquisitions.

### Task 4: Validate integration and update evidence

**Files:** `core/tests/test_trainer.py`, `core/tests/test_fast_retailing_benchmark.py`, `scripts/audit_fast_retailing_benchmark.py`, `benchmark/fast_retailing/BASELINE.md`, `docs/GOOGL_HISTORICAL_REFERENCE.md`

- [x] Test omitted and partially available surfaces, semantic mapping, formula/value agreement, pair parity, and blank/correct/incorrect non-disclosing Check results.
- [x] Validate Fast Retailing against supplied balances and payments; derive updated practice counts from the registered families and retain explicit regression assertions.
- [x] Run the benchmark audit and update its baseline and capability documentation from measured results.

### Validation and acceptance

- [x] Resolver, module, Trainer, reference-integrity, historical-v1 exit-gate, and Fast Retailing benchmark tests pass; `git diff --check` passes.
- [x] Label-only DEMO retains existing practice counts; Fast Retailing activates the supported families and passes blank/filled Check.
- [x] Benchmark G1–G7 remain closed; provenance and overlap/supplemental conflicts remain unchanged at 3/3.
- [x] No acquisition or impairment attribution, forecasting, valuation, or TARGET progression is introduced.
