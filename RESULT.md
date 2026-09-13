Status: Step 9M.3A complete — split lease-liability aggregation contract (G3 closed)

Implementation base:
- d491126 Step 9M.2D reporting-unit rounding envelope

Step 9M.3A status: complete

Final verification:
- focused tests: 88 passed
  (`test_lease_liability.py` + `test_reference_integrity.py` + `test_fast_retailing_benchmark.py`)
- full core tests: 445 passed
- forecast/valuation isolation: pass
- family orders: 1..90 unchanged
- Fast Retailing standardized/provenance/conflicts source artifacts unchanged: yes
- statement overlap conflicts: 3
- supplemental conflicts: 3

Lease source contract:
- Fast Retailing lease source mode: split
- FY2025 computed BS lease total: 513500 (= 126830 + 386670)
- FY2025 reported Note 17 total: 513501 (independent; not substituted)
- lease specs: 18
- full expected specs: 312
- blank Check: correct=0 incorrect=0 blank=312 total=312
- filled Check: correct=312 total=312

Fast Retailing Stages 1–7: all pass
G1/G1B/G2/G2B/G2C/G3 closed; G4–G7 remain open
TARGET.md: unchanged by Cursor

Next checkpoint:
- G4 lease-interest income-side consistency and/or G5 NCI attribution
  (select from measured remaining substantive gaps)
