# RESULT.md — Step 9N Historical Exit-Gate Assessment

**Status:** Step 9 exit gate **FAIL** — regressions not green; exactly one next Step 9 implementation selected.

**Implementation base:** `60926d632efe7721bff1183521ef929a4dee2cdd`
**HEAD at assessment:** `7faa9c4f0d6504a0f91ba455e750681edde8c735`

Writable files touched: `docs/GOOGL_HISTORICAL_REFERENCE.md`, `RESULT.md` only.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).

---

## Six-row exit-criteria assessment

| # | Exit criterion (TARGET) | Disposition | Evidence |
|---|---|---|---|
| 1 | GOOGL historical reference audit has no unresolved high-value historical gap | **pass** | Gap matrix/queue refreshed in `docs/GOOGL_HISTORICAL_REFERENCE.md`. Remaining historical candidates are implemented or explicitly deferred with concrete source/curriculum reasons (not contract-absence alone). |
| 2 | Historically material modules supported by available source facts are implemented, tested, or explicitly deferred with a documented reason | **pass** (conditional on queue text) | G1–G7 + capex/ROU/GW/deferred-tax modules implemented. Remaining candidates explicitly disposed in reference queue (SBC/acquisition/segments absent; reinvestment/lease-payment/cash-tax/forensics/interpretation deferred with non-contract-only reasons). |
| 3 | Source-document → filing JSON → reconciliation → StandardizedFinancials → reference-model → Trainer/Answer-Key demonstrated on real-company data | **pass** | Fast Retailing path in `benchmark/fast_retailing/` + `core/tests/test_fast_retailing_benchmark.py` (26 passed); `BASELINE.md` stages 1–7 pass; `expected_specs=481`. |
| 4 | Optional historical modules fail closed when required evidence is missing or contradictory | **pass** | Module tests assert omit/gating for capex, deferred tax, lease ROU, goodwill, per-share, ownership, lease interest; DEMO omits FR-only modules; conflicts retained 3 overlap / 3 supplemental. |
| 5 | Historical schedules, practice surfaces, Check, provenance, workbook generation pass required regression and benchmark tests | **fail** | Full suite: **1 failed, 570 passed** (see verification). Failure: `test_historical_v1_active_catalog_namespace_is_frozen`. Fast Retailing benchmark assertions hold (481 / capex 10 / Check parity / 3+3 conflicts). `git diff --check` pass. |
| 6 | No known historical defect or missing module materially limits learner analysis of an unfamiliar non-financial company | **fail** | Stale historical-v1 catalog-freeze assertion leaves required `core/tests` red; cannot claim release readiness until green. Curriculum modules for FR-supported facts are otherwise usable per benchmark. |

**Gate decision:** Step 9 **not complete**. Do **not** advance to Step 10.

---

## Gap dispositions (Task 1)

| Candidate | Disposition | Reason |
|---|---|---|
| Structured interpretation prompts | **explicitly deferred** | Major-schedule structured diagnostics already exist (WC / profitability / ROE / EQ change attribution). TARGET prefers structured diagnostics over essays; further prompts on newer intensity modules are polish, not material blockers. |
| Capex reinvestment / D&A bridge | **explicitly deferred** | Capex + fixed-asset intensity already teach TARGET capex/D&A/asset-intensity. FR `depreciation_amortization` is aggregate D&A (includes lease/ROU amortization risk); a PPE reinvestment ratio without a maintenance/disposal split would overclaim. Bounded `ppe_capex` + `ppe_capex_to_revenue` remain the accepted surface. |
| SBC expense / dilution bridge | **explicitly deferred** | No CF SBC concept on Fast Retailing or ordinary DEMO. |
| Acquisition-cash / GW-impairment attribution | **explicitly deferred** | No business-acquisition CF; goodwill flat; `impairment_losses` not goodwill-tagged (prior 9M.4/9M.5 verdict preserved). |
| Lease-payment / discount-rate analysis | **explicitly deferred** | Liability + ROU balance modules cover lease intensity. FR has `repayments_of_lease_liabilities` / `payments_for_rou_assets`, but rates are absent; ROU cash payments are immaterial vs ROU stock; CF repayments largely duplicate liability amortization already diagnosed. |
| Richer tax-adjustment / cash-tax bridge | **explicitly deferred** | ETR + deferred-tax balance context cover historical tax diagnostics. Cash-tax vs book-tax bridge needs reconciling-item contract beyond supplied `income_taxes_paid`/`refunded` alone. |
| Segment economics | **explicitly deferred** | Not evidenced as structured GOOGL schedules; no FR segment input contract/facts. |
| Forensic screens (Beneish/Piotroski/Benford) | **explicitly deferred** | Curriculum: mechanical EQ diagnostics preferred; Benford needs XBRL populations (not-trainer-target). |

G1–G7 and capex acceptance preserved.

---

## Measured verification (Task 2)

### Commands

```text
python -m pytest core/tests -q
→ 1 failed, 570 passed in 60.22s

python -m pytest core/tests/test_fast_retailing_benchmark.py -q
→ 26 passed in 5.47s

git diff --check
→ pass (exit 0)
```

### Failure detail

- `core/tests/test_historical_v1_exit_gate.py::test_historical_v1_active_catalog_namespace_is_frozen`
- Asserts `sorted(orders) == list(range(1, 98))` but `ACTIVE_CATALOGS` includes `LEASE_ROU_COMPONENT_CATALOG` (orders 112–115) → **101** families; orders `[1..97, 112..115]`.
- Post–9M catalogs **not** in that freeze list: goodwill/intangibles (98–111), deferred tax (116–119), capex (120–121).
- **Gate blocker.** No code/test/fixture edits in this assessment step.

### Fast Retailing retained assertions

- `expected_specs=481`; `capex_specs=10`
- Blank Check `0/0/481`; filled Check `481/0/0` (via stage messages / builder counts in benchmark tests)
- Overlap conflicts **3** / supplemental conflicts **3**

### Coverage exercised in the 570 passing tests (failure isolated)

Real-company filing validate/reconcile + provenance; optional-module fail-closed gating; workbook generation; Trainer/Answer-Key parity; non-disclosing Check; cross-company robustness; forecast/valuation isolation (`test_normal_historical_build_never_executes_dormant_forecast` and related paths among the passing set).

### Limitations

- Full suite is red solely on the frozen-catalog assertion; product benchmark path is green.
- No workbook visual re-audit of GOOGL xlsx in this step (hash/inventory treated as still valid from prior audit tooling notes).

---

## Exactly one next implementation

**Name:** Repair historical-v1 active-catalog freeze for post–9M modules

**Why:** Criterion 5 fails; exit gate cannot pass with `core/tests` red. Highest-value defect before any Step 10 or further curriculum work.

**Files (expected):**
- `core/tests/test_historical_v1_exit_gate.py` (primary)
- Possibly `core/engine/component_catalog.py` only if order/id collisions must be documented—prefer test-only alignment

**Actions:**
1. Make `ACTIVE_CATALOGS` consistent with all active historical optional catalogs (lease ROU, goodwill/intangibles, deferred tax, capex) **or** restore a documented v1-only freeze that excludes post–v1 catalogs.
2. Update the frozen order/id assertions to the chosen contract (contiguous active historical orders through capex if expanding).
3. Keep deferred forecast/valuation specs disjoint from active ids/categories.

**Tests / acceptance:**
- `python -m pytest core/tests -q` → 0 failed
- `python -m pytest core/tests/test_fast_retailing_benchmark.py -q` → still 26 passed; 481 / 10 capex / 3+3 conflicts unchanged
- `git diff --check` pass
- No new analytical modules, forecasting, or source changes

**Plan changes required:** none to TARGET/IMPLEMENTATION content ownership; next plan should implement the freeze repair above, then re-run Step 9 exit assessment.
