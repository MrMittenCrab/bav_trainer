# Step 9M.2.4.1.1.1.30 — Lululemon supported comparative-period admission

AUTOCYCLE_PLAN: {"baseline": "At 1d399566dd24c8bc1f3e3044d0c69f6287f38a65, verified assessment establishes 2022-01-30 IS/BS/CF eligibility and excludes 2021-01-31 for missing BS. Disposable five-period generation produced 486 exercises, adding 110 with no removed identities or changed existing expectations; canonical releases remain 376/577.", "finding_key": "lululemon-comparative-history-excluded-from-canonical-period-axis", "inputs": [], "kind": "work", "objective": "Admit supported Lululemon comparative history into the canonical axis", "plan_id": "772fcbfc00aa47b88aed4ee9c07503dc", "step_id": "9M.2.4.1.1.1.30", "success": "Explicit validated comparative admission adds only 2022-01-30 to canonical Lululemon history, preserves documentary provenance and missing-data behavior, and produces a matched 486-exercise release retaining all 376 accepted identities and expectations; Fast Retailing remains unchanged at 577.", "verification": "Read RESULT; inspect admission policy and independently reproduce validation, reconciliation, standardization and disposable generation. Verify five dates, exclusion of 2021-01-31, provenance and omission records, the 110-identity addition with zero existing expectation changes, exported formulas/Notes and non-disclosing Check outcomes; compare canonical artifacts and unchanged Fast Retailing hashes against recorded evidence.", "work_id": "1df615c8e50b4b20932cb59593e7dd84"}

INPUT_STATUS: PENDING
Parents 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1 and 9M.2.4 remain UNRESOLVED.
The controller assigns authoritative step and work identities.

## Scope

- One bounded G6 implementation: explicit comparative admission, canonical Lululemon regeneration and regression verification.
- Modify only necessary ingestion code, its CLI wiring, `scripts/build_lululemon_release.py`, directly affected tests, generated `benchmark/lululemon/reconciled/` and `release/lululemon/` artifacts, G6 in `benchmark/lululemon/GAPS.md`, and `RESULT.md`.
- This scope supersedes the completed assessment's production/generated-artifact freeze only for the listed changes; it does not broaden historical recovery authorization.
- Cursor must not modify `TARGET.md` or `IMPLEMENTATION.md`. Preserve source PDFs/extracted JSON and Fast Retailing artifacts. No note extraction, commits, pushes, forecasting or valuation.

## Task 1 — Implement explicit comparative admission

- Add a generic explicit comparative-date admission option to reconciliation and the reproducible ingestion entry point; preserve filing-year-end selection by default and avoid issuer-specific branches.
- Admit requested dates only from validated selected documentary IS/BS/CF coverage; reject missing-statement and unsupported-date requests before writing outputs. Retain existing downstream completeness, contradiction and accounting gates.
- Enable `2022-01-30` for the Lululemon canonical build. Reject `2021-01-31`: CF beginning cash does not establish BS coverage.
- Preserve deterministic precedence, conflicts, superseded observations, original-row links, source hashes/pages, reported signs, units and diluted-share scaling. Make admitted/excluded dates auditable without discarding outside-axis observations.
- Preserve sparse BS semantics and incomplete IS/CF omission; document missing comparative AR cash-flow coverage without zero filling.

## Task 2 — Regenerate and verify the canonical release

- Capture the checkpoint's 376 accepted semantic identities/expectations and artifact hashes before regeneration; retain a reproducible comparison to that baseline.
- Regenerate Lululemon reconciliation, standardized data, provenance/conflicts, supporting copies, availability, semantic map and the existing Trainer/Answer-Key pair through production paths. Update the release script's count and generated documentation coherently.
- Require the axis `2022-01-30, 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01`; verify 486 exercises, exactly 110 additions, zero removals and zero changed existing expected values despite coordinate shifts.
- Independently verify new-period source values and added opening/comparable calculations. Confirm 486 blank yellow Trainer cells without Notes and 486 matching Answer-Key formulas with nonempty Notes, visual parity and populated source facts.
- Check disposable copies: 486 blank; 486 correct after valid filling; one incorrect plus 485 blank after injection. Check must disclose no answers or hints. Verify 101 unavailable displays per Lululemon workbook, replacing the four-period 74; Fast Retailing remains 0.

## Task 3 — Regression evidence and disposition

- Test unchanged default reconciliation, explicit admission, missing-statement rejection, deterministic precedence/provenance, incomplete AR omission, round-trip identity and failure immutability; use generic fixtures plus the supplied Lululemon benchmark.
- Run relevant ingestion, Lululemon/Fast Retailing benchmark, historical model, workbook and Check regressions. Preserve four-period regression coverage instead of replacing accepted assertions with counts alone.
- Record commands, exits, identity/value differences, provenance checks and before/after hashes in `RESULT.md`; distinguish formula-text Check from actual spreadsheet recalculation and state whether recalculation occurred.
- Update G6 with measured delivery and the continuing 2021-01-31 BS dependency. Verify Fast Retailing's 577 identities/expectations and release hashes remain unchanged; do not declare parent or Step 9 acceptance.

## Original unresolved acceptance retained

- Preserve G5 aliases and accepted lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward/margin/inventory exercises; explicit-concept precedence, ambiguity rejection, strict values and deterministic mapping.
- Preserve partial-period interest dependency closure, opening-only CoD `0.374`, undefined ratios, no unavailable-history 4% substitute, pretax resolution and distinct tax expense.
- Preserve prior-period capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, cash/inventory reconciliation differences, reformulation tolerances and liability/equity discrepancy explanations.
- Preserve independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, comparative provenance, prior-period NCIT `28555 / 15864 / reported 0 / None` and Common stock `611 / 606 / 581 / 557`.
- Retain G1/G2/G3, empty-detail, subtotal/override, contra-equity, sparse-position, historical causal evidence, all twelve pretax/ETR cases, mutation controls and failure immutability.
- Retain parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; this step requires successful gated generation.
- No invented interest, inferred zeros, cash-interest substitution, lease repayment inference or deferred-tax expense/recoverability claims.
- Carry requests `20260914-193338-000000004` and `20260915-042248-000000005` through the normal five stages; remaining benchmark-improvement and parent-acceptance obligations stay pending without restarting completed publication recovery.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, its five snapshot-matched edit identities, historical batch and work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`.
- Retain hash-bound logs `cursor-20260915-033742-18263.log` and `cursor-20260915-034910-19408.log`; distinguish original successful subprocess exits, resumed wrapper failures and fresh implementation evidence.
- Carry A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending closure; E11 NonReq UNVERIFIED; G7 note facts, G8 deferral, G9 standalone interest completeness and remaining TARGET Step 9 exit gates. No blanket DONE or prospective ID reservation.
