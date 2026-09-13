Status: Step 9M.3B complete — treatment-conditioned lease interest (G4 closed)

Implementation base:
- 3f12963 Step 9M.3A split lease-liability aggregation

Step 9M.3B status: complete

Final verification:
- focused tests: 115 passed
  (`test_filing_reconciler.py` + `test_lease_liability.py` +
   `test_reference_integrity.py` + `test_fast_retailing_benchmark.py`)
- full core tests: 459 passed
- forecast/valuation isolation: pass
- family orders: 1..90 unchanged
- provenance/conflicts/source/extracted unchanged: yes
- standardized.json change: historical_lease model field only
- statement overlap conflicts: 3
- supplemental conflicts: 3

Lease interest contract:
- Fast Retailing historical_lease series:
  2021–2025 = 4847 / 4757 / 5187 / 6507 / 8464
- FY2025 Note 17 lease interest provenance: 8464 (source-bound reported)
- FY2025 BS diagnostic lease liability: 513500
- FY2025 Note 17 lease-liability total: 513501
- default operating: net interest = reported − lease interest
- all-financial override: net interest returns to reported; NOA/Net Debt/NOPAT rise
- mixed split treatment: InconsistentLeaseTreatmentError / Excel NA()
- lease specs: 18; expected specs: 312
- blank/filled Check: 312 / 312

Fast Retailing Stages 1–7: all pass
G1/G1B/G2/G2B/G2C/G3/G4 closed; G5–G7 remain open
TARGET.md: unchanged by Cursor

Next checkpoint:
- G5 NCI attribution and/or G6 share-basis / per-share work
