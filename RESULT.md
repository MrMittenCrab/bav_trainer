# RESULT.md — Step 9N.1 Lease-Payment Exit-Gate Evidence Repair

**Status:** Step 9 exit gate **FAIL** — unresolved source-supported lease-repayment gap + catalog-freeze regression; exactly one next Step 9 implementation selected.

**Implementation base:** `f4172600c5348c9b5baf442ac00ffced1f47fcc8`
**HEAD at repair:** `52049942e85aecf0d5ac2cee3c382a4689f99fd2`

Writable files touched: `docs/GOOGL_HISTORICAL_REFERENCE.md`, `RESULT.md` only.
`TARGET.md` / `IMPLEMENTATION.md`: unchanged (read-only).
No code, tests, fixtures, or baselines modified.

---

## Prior assessment error (corrected)

Step 9N deferred “lease-payment / discount-rate analysis” on the claim that CF `repayments_of_lease_liabilities` “largely duplicate liability amortization already diagnosed,” and bundled missing rates / ROU-payment immateriality into that deferral.

**Unsupported:**
- Liability **balance change / growth** is not amortization and is not repayment cash.
- Measured Δ lease liability ≠ −repayments in any FY2022–FY2025 period (new leases / remeasurements / other roll-forward items intervene).
- Missing discount rates do **not** block analysis of reported repayment cash flows.
- ROU acquisition-payment materiality does **not** dismiss repayment diagnostics.

---

## Task 1 — Supplied facts and module coverage

### Units / periods

- Currency: **JPY**; unit scale: **JPY in Millions** (`standardized.json` `units`; provenance `unit_scale=millions`).
- Periods: FY2021–FY2025 (`2021-08-31` … `2025-08-31`).
- Sign: CF outflows stored **negative as reported** (no abs()/sign inference).

### `repayments_of_lease_liabilities` (CF)

| FY | Value (JPY mn) | |repay|/Revenue | |repay|/Lease liability |
|---|---:|---:|---:|
| 2021 | −148,248 | 6.95% | 32.18% |
| 2022 | −136,889 | 5.95% | 28.48% |
| 2023 | −140,646 | 5.08% | 30.20% |
| 2024 | −146,403 | 4.72% | 30.62% |
| 2025 | −140,483 | 4.13% | 27.36% |

- Average |repay|/Revenue ≈ **5.37%**; average |repay|/LL ≈ **29.8%** → **material**.
- Provenance: `status=selected`, `selection_rule=agreeing_observations`; CFS p.5 (e.g. FY2025 current: `Fastretailing_CFS2025.pdf` pdf_page 5; earlier years agree across current/comparative filings).
- Extracted rows: `benchmark/fast_retailing/extracted/FY*.json` — label “Repayments of lease liabilities”, `suggested_concept=repayments_of_lease_liabilities`, source statement Consolidated Statement of Cash Flows p.5.

### `payments_for_rou_assets` (CF) — assessed separately

| FY | Value (JPY mn) | |pay|/ROU assets | |pay|/Revenue |
|---|---:|---:|---:|
| 2021 | −846 | 0.22% | 0.04% |
| 2022 | −796 | 0.20% | 0.03% |
| 2023 | −1,851 | 0.48% | 0.07% |
| 2024 | −2,015 | 0.48% | 0.06% |
| 2025 | −15,924 | 3.34% | 0.47% |

- Mostly immaterial vs ROU stock/revenue; FY2025 spike still ≪ repayments. Does **not** justify deferring repayment analysis.

### Context balances (for materiality / non-equivalence)

- Split LL (current+non-current): 460,657 → 513,500; ROU: 390,537 → 477,111; Revenue: 2,132,992 → 3,400,539.
- ΔLL vs −repay (FY2022–FY2025): ΔLL + repay = −116,821 / −155,722 / −133,990 / −105,045 → balance change **does not** measure repayments.

### Rates / interest

- `historical_lease.lease_interest_expense` present (4,847 … 8,464).
- **No** discount-rate / IBR concepts in standardized facts.

### Implemented coverage (verified in code/catalogs/tests)

| Surface | Present? | Evidence |
|---|---|---|
| Liability balances (aggregate or split sum) | **yes** | `lease_liability.py`; families 87–90 |
| Liability / revenue intensity, change, growth | **yes** | catalog `lease_liability_*` |
| Treatment-conditioned lease interest | **yes** | 9M.3B path in `lease_liability.py` + tests |
| ROU balance context (change/growth/avg/to-revenue) | **yes** | `lease_rou.py`; families 112–115 |
| CF repayment diagnostics | **absent** | modules explicitly “Do not invent lease payments”; no repayment concepts in catalogs/tests |
| ROU amortization diagnostics | **absent** | same |
| Discount-rate analysis | **absent** | no rate inputs; correctly out of scope until supplied |
| Complete lease roll-forward | **absent** | would need more than CF repayments + Δ balances |

`core/tests/test_lease_liability.py` / `test_lease_rou.py`: no repayment/amortization/payment assertions.

---

## Corrected gap dispositions

| Candidate | Disposition | Reason |
|---|---|---|
| Structured interpretation prompts | **explicitly deferred** | Major-schedule structured diagnostics already exist; TARGET prefers structured diagnostics over essays. |
| Capex reinvestment / D&A bridge | **explicitly deferred** | Bounded `ppe_capex` + `ppe_capex_to_revenue` accepted; aggregate D&A / no maintenance-disposal split. |
| SBC expense / dilution bridge | **explicitly deferred** | No CF SBC on Fast Retailing or ordinary DEMO. |
| Acquisition-cash / GW-impairment attribution | **explicitly deferred** | No business-acquisition CF; goodwill flat; impairment not GW-tagged. |
| **Lease repayment diagnostics** | **unresolved source-supported gap** | Material CF `repayments_of_lease_liabilities` supplied and selected; liability/ROU **balance** modules do not analyze repayment cash; ΔLL ≠ repayments. |
| Lease discount-rate analysis | **explicitly deferred** | Rates/IBR absent; separate from repayment cash analysis. |
| Complete lease roll-forward | **explicitly deferred** | Needs additions/remeasurements/etc. beyond reported repayments; not required to teach repayment cash intensity. |
| ROU acquisition-payment diagnostics | **explicitly deferred** | Separate CF line; mostly immaterial vs ROU/revenue (FY2021–FY2024 ≪1% of ROU; FY2025 3.3% ROU / 0.47% revenue). |
| Richer tax-adjustment / cash-tax bridge | **explicitly deferred** | ETR + deferred-tax balance context; cash-tax bridge needs reconciling items beyond paid/refunded alone. |
| Segment economics | **explicitly deferred** | No FR segment input contract/facts; not structured in GOOGL reference. |
| Forensic screens (Beneish/Piotroski/Benford) | **explicitly deferred** | Mechanical EQ preferred; Benford not-trainer-target. |

G1–G7 and capex acceptance preserved.

---

## Six-row exit-criteria reassessment

| # | Exit criterion (TARGET) | Disposition | Evidence |
|---|---|---|---|
| 1 | GOOGL historical reference audit has no unresolved high-value historical gap | **fail** | Material Fast Retailing lease-repayment CF facts lack any Trainer repayment diagnostic; prior “duplicate amortization” deferral withdrawn. See gap matrix/queue in `docs/GOOGL_HISTORICAL_REFERENCE.md`. |
| 2 | Historically material modules supported by available source facts are implemented, tested, or explicitly deferred with a documented reason | **fail** | Repayment analysis is source-supported and material, neither implemented/tested nor validly deferred. Discount-rate / full roll-forward / ROU-acquisition-payment remain separately deferred with documented reasons. |
| 3 | Source-document → filing JSON → reconciliation → StandardizedFinancials → reference-model → Trainer/Answer-Key demonstrated on real-company data | **pass** *(prior measurement; not rerun)* | Fast Retailing path + `test_fast_retailing_benchmark.py` (26 passed); `BASELINE.md` stages 1–7; `expected_specs=481` — recorded in Step 9N. |
| 4 | Optional historical modules fail closed when required evidence is missing or contradictory | **pass** *(prior measurement; not rerun)* | Module omit/gating tests; DEMO omits FR-only modules; conflicts 3+3 — Step 9N. |
| 5 | Historical schedules, practice surfaces, Check, provenance, workbook generation pass required regression and benchmark tests | **fail** *(prior measurement; not rerun)* | Step 9N: full suite **1 failed, 570 passed** — `test_historical_v1_active_catalog_namespace_is_frozen`. FR benchmark assertions held. |
| 6 | No known historical defect or missing module materially limits learner analysis of an unfamiliar non-financial company | **fail** | (a) Catalog-freeze regression keeps `core/tests` red. (b) Missing repayment diagnostics leave a material financing cash-conversion / lease-cash topic untaught despite supplied CF facts. |

**Gate decision:** Step 9 **not complete**. Do **not** advance to Step 10.

---

## Measured verification (Task 3)

### Commands run this step

```text
python -m pytest core/tests/test_lease_liability.py core/tests/test_lease_rou.py -q
→ 34 passed in 2.44s

git diff --check
→ pass (exit 0)

git diff --name-only
→ RESULT.md
→ docs/GOOGL_HISTORICAL_REFERENCE.md
```

### Prior measurements (Step 9N — not rerun)

```text
python -m pytest core/tests -q
→ 1 failed, 570 passed in 60.22s

python -m pytest core/tests/test_fast_retailing_benchmark.py -q
→ 26 passed in 5.47s
```

Failure detail (unchanged prior record): `test_historical_v1_active_catalog_namespace_is_frozen` — asserts `range(1, 98)` but `ACTIVE_CATALOGS` includes lease ROU 112–115; goodwill/deferred-tax/capex catalogs omitted from freeze list.

### Limitations

- Documentation/evidence repair only; no repayment module implemented.
- Full suite and FR benchmark not re-executed in 9N.1; criterion 3–5 product measurements cited as prior.
- Discount rates remain unavailable; full lease roll-forward still unsupported as a complete schedule.

---

## Unresolved blockers (visible)

1. **Catalog-freeze regression** — criterion 5 red.
2. **Lease repayment diagnostics gap** — criteria 1, 2, 6 (curriculum).

## Exactly one next implementation

**Name:** Repair historical-v1 active-catalog freeze for post–9M modules

**Why:** Criterion 5 fails with `core/tests` red; highest-priority release regression before curriculum module work. Lease-repayment gap remains an explicit unresolved blocker for the subsequent exit reassessment after the freeze is green.

**Files (expected):**
- `core/tests/test_historical_v1_exit_gate.py` (primary)
- Possibly `core/engine/component_catalog.py` only if order/id collisions must be documented—prefer test-only alignment

**Actions:**
1. Make `ACTIVE_CATALOGS` consistent with all active historical optional catalogs (lease ROU, goodwill/intangibles, deferred tax, capex) **or** restore a documented v1-only freeze that excludes post–v1 catalogs.
2. Update frozen order/id assertions to the chosen contract.
3. Keep deferred forecast/valuation specs disjoint from active ids/categories.

**Tests / acceptance:**
- `python -m pytest core/tests -q` → 0 failed
- `python -m pytest core/tests/test_fast_retailing_benchmark.py -q` → still 26 passed; 481 / 10 capex / 3+3 conflicts unchanged
- `git diff --check` pass
- No new analytical modules in that repair step (repayment module is a later Step 9 item after freeze repair)

**Plan changes required:** none to TARGET/IMPLEMENTATION ownership; after freeze repair, plan should schedule source-supported **lease repayment diagnostics** (distinct from discount-rate / full roll-forward) before claiming criteria 1/2/6.
