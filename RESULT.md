Status: Step 9M.3E complete — G7 closed by verified retained conflict policy

Implementation base:
- 10f5bbd67e71c5b341d261213f157fb8df0ec64a

Step 9M.3E status: complete

Final verification:
- focused suite: 93 passed
  (`test_filing_reconciler.py` + `test_share_basis.py` + `test_fast_retailing_benchmark.py`)
- Fast Retailing Stages 1–7: all pass
  - expected_specs=380
  - blank Check: 0 correct / 0 incorrect / 380 blank
  - filled Check: 380 correct / 0 incorrect / 0 blank
- extracted facts and committed reconciled artifacts unchanged: yes
  (`benchmark/fast_retailing/reconciled/standardized.json`,
   `provenance.json`, `conflicts.json`)
- statement overlap conflicts: 3
- supplemental conflicts: 3
- G7 closed (conflicts retained; selections locked)

Accepted conflict policy:
- FY2022 basic EPS selected 891.77 over 2675.30
  (`restated_comparative_precedence`)
- FY2022 diluted EPS selected 890.43 over 2671.29
  (`restated_comparative_precedence`)
- FY2024 financing “Others, net” selected 63 over 85
  (`later_audited_presentation`; no cause inferred)
- both observations retained for every conflict
- share-basis analytical axis unchanged; reported facts unchanged

TARGET.md: unchanged by Cursor
