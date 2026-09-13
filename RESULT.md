Status: Step 9M.3D complete — split-adjusted share basis and per-share activation (G6 closed)

Implementation base:
- f15a01a Step 9M.3C

Step 9M.3D status: complete

Final verification:
- focused G6 suite: 131 passed
  (`test_share_basis.py` + `test_filing_reconciler.py` + `test_per_share.py` +
   `test_per_share_attribution.py` + `test_reference_integrity.py` +
   `test_fast_retailing_benchmark.py`)
- full core tests: 492 passed
- forecast/valuation isolation: pass
- lease-treatment regressions: pass
- ownership-attribution regressions: pass
- family orders unchanged (G6 activates existing per-share families)
- source/extracted/provenance/conflicts unchanged: yes
- standardized.json: historical_shares null → split-adjusted comparable axis only
- statement overlap conflicts: 3
- supplemental conflicts: 3

Share basis / per-share:
- basis: split_adjusted; split_factor: 3 (audited FY2022 restatement anchor)
- FY2021 analytically ×3; FY2022 later audited restated WAS selected
- scale_basis: financial_statement_units
  (306.871785 … 307.247804)
- per_share_specs: 18; per_share_attribution_specs: 16
- ownership_specs: 34; lease_specs: 18
- expected_specs: 380
- FY2025 diluted EPS ≈ 1409.32 (parent-attributable 433009 / 307.247804)
- raw extracted share facts preserved; G7 conflicts unchanged

Fast Retailing Stages 1–7: all pass
  blank Check 380; filled Check 380
G1/G1B/G2/G2B/G2C/G3/G4/G5/G6 closed; G7 remains open
TARGET.md: unchanged by Cursor

Next checkpoint:
- G7 restatement / overlap conflict policy (presentation or code — TBD)
