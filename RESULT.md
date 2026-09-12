Status: Step 9A.3 complete — historical core source completeness hardening

Implementation base:
- 142a3718 Step 9.2

Historical formula surface (no normalization assumptions; demo CFO + total assets present):
- fiscal periods: 5
- formula families: 30
- formula practice cells: 141
- fresh Check: 0 / 0 / 141

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 34
- formula practice cells: 161
- fresh Check: 0 / 0 / 161

Historical core source completeness:
- historical core IS lines are required and period-complete
  (revenue, net_income, pretax_income, tax_expense, interest_expense, interest_income): yes
- missing period value is distinct from explicit numeric zero: yes
- supplied BS detail rows are period-complete: yes
- optional reported BS totals remain optional as whole lines, but complete if present: yes
- cash-flow checksum no longer treats missing component periods as zero: yes
- classification curly-apostrophe normalization aligned with line resolver: yes
- Step 9A quality #N/A semantics preserved: yes
- missing Net Income fails even when CFO absent / Earnings Quality omitted: yes
- missing BS detail fails even when reported totals absent: yes

Preservation:
- Step 8A/8B1/8B2 trusted-workbook behavior preserved
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- working-capital interpretation / forecasting / valuation not begun: yes

Files changed:
- Add: `core/model/source_values.py`
- Add: `core/tests/test_validators.py`
- Modify: `core/model/financial_math.py` — required core IS lines + required_period_series
- Modify: `core/model/earnings_quality.py` — shared required_period_value
- Modify: `core/model/classification.py` — BS detail/total completeness; curly apostrophes
- Modify: `core/data/validators.py` — CF checksum no missing-to-zero
- Modify: fixtures/tests for explicit zero interest lines and new regressions
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 195 passed
- focused suites (reference/classification/earnings_quality/trainer/line_resolver/line_identity/normalization/validators) green
- base build/check/list -> 141 / 30 / 0-0-141 blank
- norm build/check/list -> 161 / 34 / 0-0-161 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- working-capital / driver interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred
- DuPont historical ratios still use numeric-zero guards for zero denominators (not Step 9A quality `#N/A`)

Unresolved (out of this checkpoint's explicit scope; remaining missing-value fallbacks):
- `core/engine/reference_model.py` deferred-forecast path still uses `rev_item.values.get(...) or 1000.0` when deferred tabs are enabled
- `core/model/normalization.py` still uses `hist.effective_tax_rate[j] or 0.0` when reading ETR for tax-effecting adjustments
