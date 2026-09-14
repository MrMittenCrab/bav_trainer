# Step 10A — One-Year Operating Forecast Foundation

**Base:** `4b0e7b0cc3d131db48e472f5089ab59b16cf39f4`

**Goal:** Compute one explicit base-case forecast year for revenue, NOPAT, and working capital from the verified historical model.

**Read-only:** `TARGET.md`, `IMPLEMENTATION.md`. Cursor must never modify either file.

**Writable files:** `core/model/operating_forecast.py` (new), `core/tests/test_operating_forecast.py` (new), `RESULT.md`.

### Task 1: Define the forecast contract

- Add frozen dataclasses for explicit assumptions and forecast results, following existing `core/model` conventions.
- Accept an existing `AnchorMetrics` and its canonical historical period axis; use the latest historical period as the opening anchor.
- Require next-year revenue growth, after-tax NOPAT margin, and closing NOWC/revenue assumptions; provide no inferred defaults.
- Keep assumptions separate from calculated outputs; record each assumption’s supplied/learner origin and non-empty explanation.
- Include historical/forecast period labels and latest historical Sales Growth, NOPAT Margin, and NOWC/revenue comparators, reusing existing diagnostics.
- Reject empty or mismatched axes/series, nonannual axes, missing assumptions, nonnumeric/nonfinite drivers, and nonpositive opening revenue. Preserve unavailable historical comparators as unavailable.

### Task 2: Implement the bounded calculation

- Compute forecast revenue = opening revenue × (1 + growth).
- Compute forecast NOPAT = forecast revenue × explicit NOPAT margin; apply no additional tax.
- Compute closing NOWC = forecast revenue × explicit NOWC/revenue.
- Compute change in NOWC = closing NOWC − latest historical NOWC; positive change represents operating investment.
- Reject growth below −100%; allow zero forecast revenue, negative margins, and negative NOWC intensity.
- Return opening balances, assumptions, comparators, and outputs without mutating historical inputs; reject nonfinite calculated outputs.
- Keep the callable independent of `ri_engine.py` and normal historical generation. Defer workbook activation, capex/D&A, separate tax and financing schedules, shares, valuation, and scenarios.

### Task 3: Verify and record

- Test independently calculated examples for growth, contraction, zero revenue, losses, negative NOWC, and investment/release signs.
- Test invalid inputs, unavailable comparators, period alignment, input immutability, and classification-conditioned opening NOWC.
- Exercise existing DEMO and Fast Retailing standardized fixtures through `canonical_fiscal_periods` and `compute_anchor`; use explicitly labeled illustrative forecast assumptions.
- Run `python -m pytest core/tests/test_operating_forecast.py core/tests/test_historical_v1_exit_gate.py core/tests/test_fast_retailing_benchmark.py -q`.
- Run `python -m pytest core/tests -q` and `git diff --check`; inspect the final changed-file list.
- Keep test-generated artifacts outside the final diff while preserving pre-existing user changes.
- Record completion, actual commands, measured results, revision, and remaining Step 10 scope in `RESULT.md`; distinguish fresh verification from prior recorded passes.

### Acceptance criteria

- One forecast year reconciles to the accepted historical anchor and explicit drivers.
- Historical comparators never silently become forecast assumptions.
- Invalid required inputs fail explicitly; supported negative economics remain valid.
- Required verification passes and historical workbook behavior remains unchanged.
- Only writable files change; Step 10 remains incomplete. No commit or push.
