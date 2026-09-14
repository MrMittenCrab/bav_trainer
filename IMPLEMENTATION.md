# Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity

**Base:** `7358db04098fce5014abe23a74806be14c0ef986`
**Previous step:** Step 9M.2.3 — PASS
**Goal:** Repair the measured liability-detail reconciliation gaps while preserving reported source facts and strict integrity checks.

## Constraints

- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`.
- Limit production changes to the demonstrated defect in `core/model/classification.py` or `core/model/line_resolver.py`; add regressions in their existing tests and `core/tests/test_lululemon_benchmark.py`.
- Record completion and measured verification in `RESULT.md`.
- Preserve source PDFs, extracted JSON, stored labels/concepts/values, reconciliation artifacts, baseline hashes, and failure-path immutability guards.
- Generate verification artifacts only in temporary directories.
- No issuer-specific rules, benchmark overrides, balancing plugs, tolerance inflation, suppressed integrity errors, G4–G7 implementation, or forecasting/valuation work.

## Task 1 — Diagnose the reconciliation gaps

- Reproduce the recorded liability-detail gaps at 2023-01-29 (approximately −28,555) and 2024-01-28 (approximately −15,864); measure all four periods.
- Trace each balance-sheet row through subtotal detection, classification, and aggregation; identify the resolved reported totals.
- Reconcile included and excluded liability amounts to reported totals and explain the corresponding equity gaps using exact row identities and values.
- Consult relevant committed provenance and extracted filing observations as needed. If evidence establishes an upstream source defect, record it and retain this step as incomplete rather than altering source facts.

## Task 2 — Repair and add regressions

- Apply the smallest generic correction supported by the diagnosis, preserving classification metadata, explicit override precedence, and source identity.
- Add a synthetic regression reproducing the demonstrated defect; show failure before the repair and success afterward.
- Cover neighboring asset/liability/equity cases and subtotal-versus-detail boundaries implicated by the repair.
- Preserve rejection of genuine omissions and contradictory inputs, including equal asset/liability omissions and gaps exceeding existing rounding envelopes.
- Replace the obsolete expected liability-gap blocker assertion with direct four-period reformulation integrity assertions; retain the empty unclassified-detail set and G1/G2/G3 controls.
- Keep artifact immutability coverage exercised through a deterministic failure path even if the original build blocker disappears.

## Task 3 — Verify and record

- Run `PYTHONPATH=. pytest core/tests/test_classification.py core/tests/test_line_resolver.py core/tests/test_reference_integrity.py core/tests/test_lululemon_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -q`.
- Run `PYTHONPATH=. pytest core/tests -q`.
- Rerun the Lululemon build in a temporary directory; record successful workbook generation or the exact next exception without repairing an unrelated blocker.
- Record exact before/after asset-detail, liability-detail, and equity gaps for every period, applicable rounding envelopes, causal rows, regression results, test counts, artifact hashes before/after, and final diff scope in `RESULT.md`.
- Confirm Common stock values remain 611 / 606 / 581 / 557 and existing gift-card/PPE assertions pass. Record any execution restrictions; incomplete verification does not establish PASS.

## Acceptance and next step

- All four Lululemon periods pass `check_reformulation_integrity` within unchanged tolerance rules; the recorded liability and corresponding equity discrepancies are explained and repaired.
- Required tests pass, genuine inconsistencies still fail closed, and source facts and committed artifacts remain unchanged.
- On failure, retain **Step 9M.2.4 — Lululemon Liability-Detail Reformulation Integrity**.
- On PASS with no further build blocker, propose **Step 9M.2.5 — Generic Capex Concept Identity (G4)**; otherwise use Step 9M.2.5 for the measured next build blocker and defer G4. Step 9 remains incomplete.
