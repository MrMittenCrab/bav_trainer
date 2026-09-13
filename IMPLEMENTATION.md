# Step 9M.5 — Repair First-Period Goodwill & Intangibles Blanks

**Base:** `5510c1e290dc4c1c55191181fa1f93da47a2036c`

**Goal:** Leave first-period balance-derived diagnostics blank in both Trainer and Answer Key.

### Task 1: Correct workbook population

**File:** `core/engine/reference_model.py`

- [x] In `_populate_balance_block`, remove first-period `na` writes for change, growth, average balance, and average balance/revenue; retain the first-period `continue`.
- [x] Apply this to `goodwill`, `intangible_assets`, and `goodwill_and_intangibles`.
- [x] Preserve populated balance cells, payment calculations, later-period formulas, and existing zero-denominator `NA()` behavior.

### Task 2: Add workbook regression coverage

**File:** `core/tests/test_goodwill_intangibles.py`

- [x] Use `_tiny` and `build_training_workbook` to cover both balances available, goodwill only, and intangibles only.
- [x] Reload both generated workbooks with `data_only=False`; assert first-period change, growth, average, and intensity cells for every available balance block have `.value is None`.
- [x] Locate diagnostic rows through existing labels or semantic mappings, without fixed worksheet row numbers.
- [x] Assert these first-period cells are excluded from the semantic practice surface, balance cells remain populated, and later-period diagnostics retain Answer-Key formulas and blank Trainer cells.

### Validation and acceptance

- [x] Run `python -m pytest core/tests/test_goodwill_intangibles.py core/tests/test_fast_retailing_benchmark.py`.
- [x] Run `git diff --check`.
- [x] The new workbook regression fails before the repair and passes afterward.
- [x] Existing practice-count and blank/filled/incorrect Check assertions pass unchanged.
