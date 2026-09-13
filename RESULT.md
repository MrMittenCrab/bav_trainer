Status: Step 9M.3C complete — parent/NCI attribution and parent ROE (G5 closed)

Implementation base:
- 9f3c4b0 Step 9M.3B treatment-conditioned lease interest

Step 9M.3C status: complete

Final verification:
- focused tests: 110 passed
  (`test_ownership_attribution.py` + `test_line_resolver.py` + `test_per_share.py` +
   `test_per_share_attribution.py` + `test_reference_integrity.py` +
   `test_fast_retailing_benchmark.py`)
- full core tests: 470 passed
- forecast/valuation isolation: pass
- family orders: 1..97 (ownership 91..97); prior 1..90 unchanged in meaning
- lease-treatment regressions: pass
- source/extracted/provenance/conflicts unchanged: yes
- standardized.json unchanged (attribution already on statement rows)
- statement overlap conflicts: 3
- supplemental conflicts: 3

Ownership attribution:
- ownership_specs: 34
- expected_specs: 346
- FY2025 profit bridge gap: -1; equity bridge gap: -1 (within 1.5 envelope)
- Parent ROE: separate shareholder diagnostic (not consolidated DuPont ROE)
- Per-share numerator: parent-attributable when ownership complete; FR per-share
  still omitted until G6 (`historical_shares=null`)

Fast Retailing Stages 1–7: all pass
  blank Check 346; filled Check 346
G1/G1B/G2/G2B/G2C/G3/G4/G5 closed; G6–G7 remain open
TARGET.md: unchanged by Cursor

Next checkpoint:
- G6 audited split-adjusted share basis / per-share activation
