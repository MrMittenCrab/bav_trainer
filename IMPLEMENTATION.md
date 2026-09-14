# Step 9M.2.4.1.1.1 — Restore Isolation References and Historical Totals Accounting

**Base:** `4035dbf2d87e7bd731b3679c05ca8c2e04879d83`
**Status:** PROBLEMS — UNRESOLVED; repair of the same step.
**Parents:** Steps 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 remain UNRESOLVED until every original acceptance criterion passes.
**Scope:** Repair evidence references, historical totals accounting, and dependent completion claims in `RESULT.md`.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`; only `RESULT.md` may change in the authoritative workspace.
- No production/test changes, generated refreshes, baseline updates, commits, or pushes. Preserve source PDFs, extracted JSON, standardized facts, provenance, conflicts, and release/demo workbooks.
- Preserve classification metadata, source identity, concept/override precedence, ambiguity errors, required-value semantics, subtotal/detail boundaries, and non-balance-sheet completeness.
- Any necessary execution requires permitted independent disposable copies with authoritative files protected throughout, including failure paths; no writable links or generated copy-back. Access restrictions remain blockers.
- No invented facts, measurements, zeros, carry-forward, balancing plugs, issuer-specific rules, benchmark overrides, tolerance inflation, suppressed errors, G4–G7, forecasting, valuation, or unrelated repair.

## Task 1 — Restore deleted isolation evidence references

- Compare `4035dbf2^:RESULT.md` with `4035dbf2:RESULT.md`; restore deleted log/manifest references without deleting the restored criterion-specific evidence.
- Retain the full isolation base and restore its `manifests/isolation_setup.json`, `auth_before_*.json`, `auth_after_*.json`, `suite_runs.json`, and `logs/focused.log`, `fr.log`, `full.log` references; expand individual filenames where recoverable.
- Map references to verified revision `590c73a4eba8ee2901687f8f2d03e63aacc865bd`, execution roots, exact commands, exits, suite counts, authoritative hash boundaries, and isolated artifact changes.
- Distinguish references recovered from committed records from files inspected now. Preserve unavailable paths and source revisions, explicitly mark inaccessible verification UNVERIFIED, and propagate missing support to dependent claims.
- Preserve source-input hashes, both reconciliation output hashes and committed comparisons for all three artifacts, and separate subprocess-failure, comparison-failure, mutation-detection, and drift-detection outcomes.

## Task 2 — Supply historical resolved totals or explicit missing-evidence accounting

- Inspect directly relevant records at `cdf0c9f`, `c50912c`, `17114fc`, `8c0098c`, and `470aa435^`; record four-period resolved asset, liability, and equity totals for each historical stage where supported.
- For each unavailable stage/period/total, enter UNVERIFIED with the precise missing evidence or exception; “totals existed” and current totals do not satisfy historical accounting.
- Keep historical measurements, later-code diagnostics, overlays, and isolated repaired measurements distinct. Gate-absent equity-detail measurements and unavailable post-exception aggregates remain UNVERIFIED.
- Retain causal included/excluded rows and amounts, all four reconciliation gaps, actual detail counts, and unchanged tolerance formulas/envelopes: pre-repair A/L 11/10 with 6.0/5.5 and implied 11.0; repaired A/L/E-detail 11/11/4 with 6.0/6.0/2.5 and implied 11.5.
- Preserve existing NCIT provenance itemization, synthetic before/after assertions, sparse/zero/export-reload evidence, safeguards, and individual pretax/ETR outcomes.

## Task 3 — Correct dependent claims and verify the evidence-only repair

- Withdraw unsupported COMPLETE and blanket “fully restored/preserved” statements in the header, restoration summary, ledger, and closure note.
- Reassess A2, A4, E4, E8–E10, E12–E13, and every other dependent claim against restored references and historical totals; split obligations with differing evidence and use FAIL for demonstrated failures or UNVERIFIED for missing proof.
- Retain original criterion wording and source revisions from `aa6adc1`, `a370a02`, `2e88322`, `88ce931`, `a62893f`, `0f1d2c3`, and `b5a33cd`; complete accounting does not satisfy missing technical evidence.
- Verify each deleted reference is restored or explicitly accounted for, every required historical total has evidence or UNVERIFIED accounting, summaries agree with the ledger, and the authoritative diff changes only `RESULT.md`.
- Reuse traceable measurements without relabeling them fresh; rerun only missing verification when protected isolation is permitted. Record commands, outcomes, and access blockers in `RESULT.md`.

## Original acceptance retained

- All four Lululemon periods pass `check_reformulation_integrity` within unchanged tolerance rules; the recorded liability and corresponding equity discrepancies are explained and repaired.
- Required tests pass, genuine inconsistencies still fail closed, and source facts and committed artifacts remain unchanged.
- Unsupported sparse equity omissions fail closed before usable reformulation results; balanced assets and liabilities alone cannot authorize missing equity detail.
- Independent asset, liability, and signed equity-detail gates retain separate implied-equity reconciliation; missing keys/totals, contradictory evidence, equal omissions, and excessive gaps fail closed.
- Sparse absence remains distinct from reported zero through standardization, export/reload, and reformulation; selected, superseded, and outside-axis observations remain preserved without invented facts.
- Historical causal evidence includes resolved totals, counts, gaps, and envelopes; synthetic before/after, sparse-position/zero/complete-row, latest-available identity, contra-equity, subtotal/override, non-balance-sheet omission, empty unclassified-detail, and G1/G2/G3 obligations retain criterion-specific proof.
- NCIT remains 28555 / 15864 / reported 0 / `None`; Common stock remains 611 / 606 / 581 / 557.
- All 12 parity cases and workbook mutation controls pass; required suites, deterministic comparisons, and failure-path immutability pass with authoritative artifacts protected throughout execution.
- Every original obligation retains its original wording and supported PASS or explicit FAIL/UNVERIFIED accounting. Complete accounting does not establish technical completion; workbook generation success is not an original parent acceptance requirement.

**Next step:** On unresolved evidence or failure, **Step 9M.2.4.1.1.1 — Restore Isolation References and Historical Totals Accounting**. Only after original acceptance passes, return to Plan for closure assessment. Preserve the exact `interest_expense` exception separately from synthetic parity and unavailable full-company parity. First unused child for genuinely new bounded work: **9M.2.4.1.1.1.8**. Step 9 remains incomplete.
