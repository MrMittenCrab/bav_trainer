# RESULT.md — Step 9M.2.4.1.1.1.49 Operating KPIs: revenue/comparable-sales growth relationship

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.49 — Operating KPIs — Consolidated revenue growth and reported comparable-sales relationship  
**Work:** `95663457369f47879e945e6f24a8800c`  
**Plan:** `2617c4e1442a4cb8bf1abe91b1e42914`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `d0f50d6f508c851679927102ca290a3ba4d297eeab8f801d9064543d631af081` (10890).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, or Step 9 acceptance.

Edits this child: `core/model/operating_kpi_relationships.py`, `core/tests/test_operating_kpi_relationships.py`, `core/tests/test_operating_kpi_analysis.py`, `core/tests/test_management_kpi_analysis.py`, and `RESULT.md`. Existing store, management, and revenue/store relationship APIs were not redesigned.

No required plan change.

`.git/autocycle/latest-implementation` currently references `HEAD: 1df2e1600fe81c2eda10608669ac9a46162e60d2` and log `cursor-20260917-121725-31232.log` and was not rewritten. That pointer is a historical controller artifact, not this increment's acceptance. Working-tree HEAD is `747b1eed1298a1f400bc504094564f3d605211d3`.

`operating_kpi_revenue_comparable_sales_relationship_applicable` / `compute_operating_kpi_revenue_comparable_sales_relationship` require validated global reported `comparable_sales_growth` observations with percent units and year-over-year comparison. Absent, null, store-only, sales-per-square-foot-only, regional, and constant-currency payloads have no comparable-sales relationship module. Deferred supplied observations still produce no management analytics, no revenue/store relationship, and no comparable-sales relationship.

---

## Task 1 — Add the bounded comparable-sales relationship

A dedicated relationship applicability function and computation API sit in `core/model/operating_kpi_relationships.py`. Eligible observations are global, reported-basis, percent-unit, year-over-year `comparable_sales_growth` rows. Series are keyed by full management identity and are never selected, merged, or averaged. Regional and constant-currency observations remain outside this increment.

Reported consolidated revenue is resolved from income-statement lines with existing explicit-concept precedence and ambiguity rejection. Currency and monetary-scale metadata are retained. Adjacent consolidated revenue growth is `(current - prior) / prior`. The current reported comparable-sales percentage is reused directly. The descriptive difference is `100 * revenue_growth - current_reported_comparable_sales_percent`. Growth of a growth rate and adjacent percentage-point change are not used.

Revenue growth is labeled statement-derived, comparable-sales growth reported, and the difference analyst-derived in percentage points. The scope note states that consolidated revenue and the comparable-sales population have distinct scopes, that disclosed calendar differences are retained and not normalized, and that the difference is not new-store contribution, revenue attribution, organic growth, productivity, or causal evidence.

Opening revenue growth and differences are `None`; available reported KPI values remain visible. A current reported comparable-sales observation does not require a prior KPI observation. Revenue growth requires immediately adjacent canonical revenue inputs. Missing required inputs produce `SOURCE_UNAVAILABLE` with explicit reasons. Zero prior revenue produces `#N/A`. Missing-input unavailability takes precedence in the difference. Reported zeros and declines are preserved. Gaps are not compressed, substituted, annualized, or calendar-adjusted. Existing semantic-discontinuity gates are unchanged. Malformed contracts, interim-only histories, and noncanonical requested axes raise without mutation.

---

## Task 2 — Verify arithmetic, eligibility and ordinary handoff

Independent fixtures cover positive, negative, and zero values; percent-versus-fraction conversion of revenue growth (`×100`) while reusing the reported percentage directly; monetary-scale invariance; singleton and sparse histories; missing current/prior revenue; missing current KPI; zero revenue denominator; and mixed unavailable/undefined cases. A missing prior KPI does not suppress an otherwise valid current comparison.

Eligible management-only and mixed histories activate the API; store-only, SPSF-only, regional, constant-currency, and empty-geography store-only comparable-sales histories do not. Multiple full identities remain isolated. Definition, calendar, and qualifier fields are retained. Explicit revenue-concept precedence, ambiguous revenue rejection, malformed contracts, shuffled observations, axis rejection, determinism, and input immutability were asserted.

Filing reconciliation → standardization → analytics and standardized JSON export/reload → analytics were exercised with existing revenue statements and temporary documentary-selection fixtures. Fixture-added selected occurrences (`2` / `7` on P2023/P2024; sparse `2` / `4` on P2023/P2025) are identified separately from supplied source facts. Numeric outputs compared within `1e-12`. Mixed store-plus-selected-management fixtures keep both-family management analytics, store counts `574/655/711/767/811`, changes `None/81/56/56/44`, and the accepted revenue/store relationship unchanged. Supplied deferred documents activate neither management analytics nor either relationship.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent mixed-directory load of supplied extracted inputs (admit `2022-01-30`):

- 4 statement filings (FY2022–FY2025) + 4 management documents vs annual-only 4+0
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- 107 market-table store observations
- 3 nonhistorical targets
- status `admitted_unreconciled`; model-facing canonical selection `deferred`
- assessments: **135** items; **28** supported, **107** outside_scope, **0** unsupported_variant
- comparability: comparable **0**, not_comparable **22**, unresolved **6**, outside_scope **107**
- reconciliation: pair_count **24**; agreeing_duplicate **0**; conflicting_candidate **0**; incompatible **24**; unresolved pairs **0**; singleton **6**; unsupported_variant **0**; outside_scope **107**
- supplied presentation/assurance/revision: `revision_links` **[]**; counts recognized/unresolved/incompatible **0/0/0**
- group selections: **28** identity-period groups, all `deferred`; selected **0**; superseded **0**
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed and annual-only `historical_operating_kpis is None`; management analytics absent (`MissingLineError: management KPI sources not available`); revenue/store relationship absent; comparable-sales relationship absent (`MissingLineError: operating KPI revenue/comparable-sales relationship sources not available`)
- extracted JSON bytes immutable after the exercise

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Separate revenue/comparable-sales relationship API keyed by full identity; eligible global reported percent YoY only; percentage-point difference `100 * revenue_growth - current_reported_comparable_sales_percent`; missing prior KPI does not suppress a current comparison; percent-versus-fraction conversion of revenue growth; missing/undefined precedence; interim-only and axis rejection; ordinary-path handoff → analytics → export/reload with temporary documentary-selection fixtures; deferred supplied exclusion; mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets, 107 market-table; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; mixed `historical_operating_kpis is None`, management analytics absent, store relationship absent, and comparable-sales relationship absent; focused KPI/analytics pytest **1207 passed**; required listed files **2158 collected**, all passed / **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, store relationship and selected comparable-sales differences within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication; malformed management-text rejection on object/default/`strict=False`/`strict=True` reload |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Prior revenue/store-relationship child focused **1193** / required **2144**; both-family-analytics child focused **1179** / required **2130**; selected-history-handoff child focused **1160** / required **2111**; fail-closed-reload child focused **1125** / required **2076**; premature-completion child focused **126** / required **1077**; revision-selection child focused **370** / required **1049**; older 352/1031, 309/988, 232/911, 175/854 and 117/796 remain historical |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

`.git/autocycle/latest-implementation` currently points at `1df2e1600fe81c2eda10608669ac9a46162e60d2` / `cursor-20260917-121725-31232.log` and was **not** rewritten. Working-tree HEAD is `747b1eed1298a1f400bc504094564f3d605211d3`. Any remaining controller refresh belongs to the existing controller mechanism; prospective IDs are not certified here.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_relationships.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_operating_kpi_management_history.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py -q --tb=short` | 0 | **1207 passed** in **4.33s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **2158 passed** in **187.50s**, **0 failed**. Listed required files collect **2158**. |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory copies; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical / 107 market-table; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; std/conflicts/statement-provenance match; mixed and annual-only `historical_operating_kpis is None`; management analytics, store relationship, and comparable-sales relationship absent; extracted JSON unchanged |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/operating_kpi_relationships.py` | `fe28f208d0e27749ddfb9f70b9dbd85508465af13e05f90fa6ebdcbde0423f1f` | 22207 |
| `core/tests/test_operating_kpi_relationships.py` | `f09b444709f6f23b4815df57ecbe73c69fd0c6c1b79aa63e45c8a5049f0c9d1c` | 68144 |
| `core/tests/test_operating_kpi_analysis.py` | `d933250227b87f598e43cb68deb115278e79336d5f6946321d743fe41f2cd128` | 22934 |
| `core/tests/test_management_kpi_analysis.py` | `c9b07b5d7c140c383786593edab4de2ecf10adc8bc751effe9e09ce9deb22fa1` | 29343 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated global reported comparable-sales histories now expose a descriptive revenue/comparable-sales comparison; additional revenue relationships remain unfinished.

---

## Remaining scope

This child compares consolidated revenue growth with reported global comparable-sales growth. Other supported revenue relationships, geography/margin/inventory/working-capital/capex relationships, and ordinary BAV/Trainer/Answer-Key/Check integration remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41`, `.42`, `.43`, `.44`, `.45`, `.46`, `.47` and `.48` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store relationship remains unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected global reported comparable-sales observations that pass those gates now produce the revenue/comparable-sales comparison; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
