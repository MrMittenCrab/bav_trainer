Status: Step 9M.3D Repair complete — same-period share presentations must agree with the audited split anchor

Implementation base:
- afa5e3331ad6104f976fc8d38160d3ec810eb8cd

Step 9M.3D Repair status: complete

Final verification:
- focused suite: 92 passed
  (`test_share_basis.py` + `test_filing_reconciler.py` + `test_fast_retailing_benchmark.py`)
- full core tests: 525 passed
- Fast Retailing Stages 1–7: all pass
  - expected_specs=380
  - blank Check: 0 correct / 0 incorrect / 380 blank
  - filled Check: 380 correct / 0 incorrect / 0 blank
- extracted facts and committed reconciled artifacts unchanged: yes
  (`benchmark/fast_retailing/reconciled/standardized.json`,
   `provenance.json`, `conflicts.json`)
- statement overlap conflicts: 3
- supplemental conflicts: 3
- G7 remains open

Share-basis repair:
- every eligible same-period presentation must agree within the pre-anchor
  and post-anchor groups; when both exist, `post = pre × split_factor`
- component checks validate all reported basic/dilutive presentations
  (order-independent); zero/zero allowed; zero/nonzero rejected
- contradictory additional presentations fail closed (`historical_shares=None`)
  without mutating reconciliation observations/conflicts
- Fast Retailing axis preserved:
  306.871785, 306.969624, 307.138870, 307.231804, 307.247804
  adjustment factors 3, 1, 1, 1, 1; parent-attributable per-share earnings

TARGET.md: unchanged by Cursor
