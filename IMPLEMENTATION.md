# Step 9M.2.4.1.1.1.37 — Operating KPIs: historical company-operated store analysis

AUTOCYCLE_PLAN: {"baseline": "At df96d3670deceacb218fbde7e6aaafbff432879d, validated company-operated store histories reload deterministically as 574/655/711/767/811; provenance and malformed-label controls passed Review, but no operating-KPI analytical series exists.", "finding_key": "operating-kpi-store-history-missing-analytical-series", "inputs": [], "kind": "work", "objective": "Establish source-supported historical store-count analytics", "plan_id": "88639dae567748c4971027f20b81df83", "step_id": "9M.2.4.1.1.1.37", "success": "An optional analytical module consumes validated StandardizedFinancials store histories and returns deterministic period-end counts, adjacent-period net changes and growth, with explicit missing-source and zero-denominator behavior and unchanged protected artifacts.", "verification": "Independently reconstruct serialized source-grounded filings in both orders, reconcile and reload standardized inputs, compare analytical outputs with direct count arithmetic, exercise sparse/zero/invalid-input controls, inspect regression evidence and compare all 50 protected artifacts with both required checkpoints.", "work_id": "7608d8dab10c49959e9d24407e3cc040"}

## Scope and constraints

- Implement one historical analytical dependency under TARGET’s focus gate. Workbook practice, Check integration and additional KPI extraction remain subsequent work.
- Permitted edits: new `core/model/operating_kpi.py`, new `core/tests/test_operating_kpi_analysis.py`, narrowly necessary reusable test helpers in `core/tests/test_operating_kpi_facts.py`, and `RESULT.md`.
- Reuse the accepted contract, fixture and temporary preparation helper. Preserve source PDFs, extracted JSON, canonical reconciled artifacts, Fast Retailing data, releases and committed examples.
- All 50 protected artifacts must match `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189`; augmented filings and generated artifacts use temporary destinations.
- Cursor must never modify `TARGET.md` or `IMPLEMENTATION.md`. No commits, pushes, publication, forecasting or valuation; execution remains subject to available permissions.

## Task 1 — Add the optional analytical series

- Follow `core/model/geographic_segment.py` conventions: expose applicability and computation entry points, consume only `StandardizedFinancials.historical_operating_kpis`, and validate supplied contracts before calculation.
- Return canonical fiscal dates, explicit metric/population/unit identity, period-end company-operated counts, net count change `current - previous`, and growth `(current - previous) / previous`.
- Use `canonical_fiscal_periods` and existing ratio sentinels. Absent/null payloads make the module unavailable; explicit computation without sources raises `MissingLineError`. Malformed supplied payloads raise validation errors.
- Opening-period change/growth is `None`. Later comparisons require both immediately adjacent model-period observations; missing observations produce `SOURCE_UNAVAILABLE` without compressing gaps. Zero denominators produce `UNDEFINED_RATIO`; actual zero counts and negative net changes remain valid.
- Treat accepted `stores`/`ones` as count units independent of monetary scale. Label changes as net count changes, not gross openings; derive no closures, same-store sales, revenue-per-store, geographic allocation or operating causality.

## Task 2 — Verify arithmetic and source-to-analysis continuity

- Reuse accepted source-grounded temporary filing preparation; load serialized inputs, validate, reconcile, standardize and JSON-reload in forward and reversed filing orders before invoking the analytical module.
- Independently assert counts `574/655/711/767/811`, net changes `81/56/56/44`, and growth `81/574`, `56/655`, `56/711`, `44/767` within `1e-12`; opening comparisons remain absent.
- Test shuffled observations, monetary-scale independence, both accepted count units, absent/null payloads, single-period and sparse histories, zero denominators, zero current counts and declining counts.
- Exercise direct in-memory malformed values, identities, units, duplicate keys and off-axis periods; retain canonical-axis rejection and prove success/failure do not mutate inputs. Preserve all 56 geographic facts and separate audit provenance.
- Require analytical outputs after standardized reload to equal pre-reload outputs and outputs from reversed filing order; no company-specific selection or hard-coded benchmark arithmetic.

## Task 3 — Run regressions and record evidence

- Run `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest` for the new analytical tests and existing operating-KPI facts, filing JSON/reconciler/CLI, historical segment, geographic facts/analysis/workbook, Lululemon/Fast Retailing benchmarks, normalization and historical-v1 exit-gate tests.
- Independently compare protected hashes against both checkpoints. Record commands, measured outcomes, arithmetic, availability behavior, input immutability and hash comparisons in `RESULT.md`.
- Distinguish fresh evidence from retained PDF/provenance inspection; record unavailable checks explicitly. Claim no spreadsheet recalculation, workbook integration or broader Operating KPIs completion.

## Acceptance and retained commitments

- Source-grounded store histories produce the specified deterministic analytics; malformed inputs fail closed, missing evidence stays unavailable, and monetary scale never changes store counts.
- Preserve accepted provenance validation, deterministic precedence, conflicts/superseded observations, sparse histories and unique metric/population/period keys. Keep temporary admission of `2022-01-30` without inventing `2021-01-31` balance-sheet data; source evidence remains outside model-facing payloads.
- Preserve geographic acceptance: 56 facts, 74 additions, 486 prior identities, 560 practice counterparts, 101 unavailable displays, 15 margin formulas, selected Americas revenue `7928156`, audit-only superseded `7928256`, signed bridges and availability/semantic/source controls.
- Preserve two user-facing workbooks, blank yellow/no-Notes Trainer practice, formula/Notes white-or-no-fill Answer Key without yellow, non-disclosing Check, minimal typography, visual parity, pale-yellow rejection, authenticated frozen compatibility and Fast Retailing 577-cell coverage.
- Preserve accepted 110 additions, G1/G2/G3/G5 aliases, reformulation/provenance/ambiguity gates, historical causal evidence, twelve pretax/ETR cases, sparse/zero-denominator behavior, partial interest closure and opening-only CoD `0.374`; invent no interest, zeros, lease repayments or deferred-tax interpretations.
- Preserve capex `638657 / 651865 / 689232 / 680802`, repurchase residuals `-116195 / 1085647 / -207544 / -256674`, NCIT `28555 / 15864 / 0 / None`, Common stock `611 / 606 / 581 / 557`, cash/inventory differences and liability/equity discrepancy explanations.
- Parent temporary-build acceptance remains success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`; canonical generation succeeds. This exception does not satisfy analytical acceptance.
- Pending requests `20260914-193338-000000004` and `20260915-042248-000000005` retain their normal five-stage commitments; parent acceptance and publication remain unfinished.
- Preserve `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json`, five snapshot-matched edit identities, historical batch, recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa`, and hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log`; do not repeat completed recovery actions.
- Parents `9M.2.4.1.1.1`, `9M.2.4.1.1`, `9M.2.4.1`, `9M.2.4` remain unresolved; retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED.
- Remaining scope: KPI workbook/Check and other source-supported KPIs; Normalization Judgment + Earnings Normalization; G6 opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication and TARGET Step 9 exit gates. Defer independent M&A Net Debt, Complete NOPAT/RNOA and forecasting under the analytical focus gate.
