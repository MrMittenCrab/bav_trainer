Status: Step 9A.5 complete — historical tax and normalization undefined-state hardening

Implementation base:
- 8c7dcb9 Step 9.3 (Step 9A.4 complete)

Historical formula surface (no normalization assumptions):
- fiscal periods: 5
- formula families: 30
- formula practice cells: 141
- fresh Check: 0 / 0 / 141

Step 9A illustrative demo (with DEMO_HK_Assumptions.json):
- fiscal periods: 5
- formula families: 34
- formula practice cells: 161
- fresh Check: 0 / 0 / 161

Tax / normalization undefined-state semantics:
- zero Pretax Income -> Effective Tax Rate `#N/A` / Excel `NA()`: yes
- zero Net Interest short-circuit (NIAT remains 0 when ETR undefined): yes
- nonzero Net Interest + undefined ETR -> NIAT / NOPAT `#N/A`: yes
- undefined NOPAT propagates into NOPAT Margin / RNOA via `ratio_or_na`: yes
- Actual ROE remains independent of NOPAT / ETR when its own inputs are valid: yes
- normalization candidate period completeness (omit / None -> MissingHistoricalValueError): yes
- all-zero candidate still suppressed after completeness check: yes
- zero pretax normalization adjustment short-circuit (after-tax remains 0 when ETR undefined): yes
- nonzero pretax normalization adjustment + undefined ETR -> after-tax / normalized NI / NOPAT `#N/A`: yes
- Formula Check exact/equivalent `#N/A` accepted; fabricated `0.0` rejected: yes
- Step 9A.4 DuPont `#N/A` behavior preserved: yes
- Step 9A.3 source-completeness behavior preserved: yes
- Step 9A earnings-quality `#N/A` behavior preserved: yes

Preservation:
- CLI remains {ingest,build,check,list}
- forecast/scenario engine not called on normal build
- TARGET.md unchanged: yes
- working-capital interpretation / forecasting / valuation not begun: yes

Files changed:
- Modify: `core/model/ratio_values.py` — numerator/denominator `#N/A` propagation
- Modify: `core/model/financial_math.py` — ETR / NIAT / NOPAT undefined-state rules
- Modify: `core/model/normalization.py` — candidate period completeness + tax-effect rules
- Modify: `core/engine/reference_model.py` — Condensed `NA()` / NIAT `ISNA` + normalization after-tax bridge
- Modify: `core/engine/component_catalog.py` — ETR / NIAT / NOPAT Notes
- Modify: `core/tests/test_reference_integrity.py` — ETR / NIAT / NOPAT / Check regressions
- Modify: `core/tests/test_normalization.py` — completeness + undefined-ETR normalization regressions
- Modify: `RESULT.md`
- Modify: `IMPLEMENTATION.md` status only

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/ -q` -> 202 passed
- base build/check/list -> 141 / 30 / 0-0-141 blank
- norm build/check/list -> 161 / 34 / 0-0-161 blank
- CLI -> `{ingest,build,check,list}` only

Known deferred limitations:
- dormant deferred-forecast defaults/fallbacks remain (e.g. revenue `or 1000.0` path)
- working-capital / driver interpretation remains deferred
- quality scoring / forecasting / valuation remain deferred

Unresolved: none on the active historical tax / normalization surface addressed by this checkpoint
