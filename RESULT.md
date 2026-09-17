# RESULT.md — Step 9M.2.4.1.1.1.58 Geographic Analysis: operating-profit amount-change bridge (residual-sign repair)

**Status:** BLOCKED (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.58 — Geographic Analysis — Operating-profit amount-change bridge  
**Work:** `06c5cb92775a41e1a9b7515d0268b9e4`  
**Plan:** `380cb2b9d389456aa23682a3ae608445`  
**Finding:** `geographic-operating-profit-amount-change-bridge`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted mix/within work `3bc0356f73fb4e289eec1c23db6e6ff4` remains complete and is not reopened.  
Prior child RESULT under plan `48754410c77148c185ba39c27336ab87` claimed COMPLETE; that completion is superseded by this repair.  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `87b1bdec4654e9045f9f9f0b44ace5b988f80a1ff8143b444dee4da7e3d1b2ef` (10132).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance.

No interrupted working-tree edits were present. `core/trainer/checker.py`, `core/engine/reference_model.py`, `core/model/historical_expected.py`, and `core/tests/test_operating_kpi_workbook.py` required no edits (catalog-driven family IDs and retained counts).

## Required plan change

No required plan change. Completing original accepted-nonzero-reconciliation coverage would need Plan to change admission/validation; this repair must not.

## Blocker

Original accepted-nonzero-reconciliation coverage remains an explicit unresolved acceptance requirement. Exact source reconciliation (`SEGMENT_BRIDGE_TOLERANCE = 0.0`) rejects nonzero reconstructed-versus-reported differences on the production path, so admitted historical snapshots cannot expose genuine nonzero `D_t` or nonzero amount-change residuals. Arithmetic-only synthetic helper coverage (`+11.0` / `-7.0`) and production-path rejection checks cannot satisfy that requirement or justify COMPLETE.

---

## Task 1 — Residual-sign contract

Accepted difference field remains `D_t = reconstructed operating profit_t − reported consolidated operating profit_t` (reconstructed-minus-reported). Prior RESULT’s parenthetical “reported-minus-reconstructed” description is corrected.

Retained residual `R_t = Δreported consolidated profit − ΣΔsegment profit − Δaggregate signed reconcilers`. Required identity is `R_t = −(D_t − D_previous)`, not `+ΔD`. The contradictory positive adjacent-difference equality from the previous plan is superseded only for that equality; the bridge formula and other acceptance requirements are retained.

Answer-Key Notes, catalog hints, independent expectations, and tests now state reconstructed-minus-reported `D` and `R = −ΔD`. Current-minus-immediately-prior monetary changes, aggregate ADD/SUBTRACT treatment across both presentation families, opening `None`, uncompressed gaps, and dependent-only `SOURCE_UNAVAILABLE` are unchanged. Zero revenue does not suppress available amount changes.

---

## Task 2 — Signed coverage without weakening admission

Production helper `_operating_profit_amount_bridge` is the arithmetic boundary used by `compute_geographic_segment_series`. Independently calculated synthetic cases, not admitted snapshots:

| Case | Expected residual | Independent `R` | Independent `−ΔD` | `D_t` | `D_prior` |
|---|---:|---:|---:|---:|---:|
| Positive residual | `11.0` | `11.0` | `11.0` | `-6.0` | `5.0` |
| Negative residual | `-7.0` | `-7.0` | `-7.0` | `7.0` | `0.0` |

Assertions use exact equality (no tolerance that accepts zero). Tests fail if the residual is zeroed or negated. Segment and reconciling amounts move in both cases; values are not cancellation artifacts.

Production-path rejection: mutating consolidated IFOP by `+11.0` (corporate) or `-7.0` (itemized) while keeping IS aligned raises `geographic IFOP bridge mismatch`; inputs are unchanged after the raise; `SEGMENT_BRIDGE_TOLERANCE` remains `0.0`. Validation was not patched.

Misleading nominal nonzero-fixture claim replaced: family-transition fixture and admitted Lululemon export/reload control now assert actual differences and residuals `0.0`. `_assert_series_matches` requires numeric `ifop_diff == 0.0` and numeric amount-change residual `0.0` on valid reconciling fixtures.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Supplied-filing reconciliation → standardization → export/reload → ordinary geographic workbook fixture remains five canonical periods with **56** selected geographic sources. Amount-change identities remain **24** (3 segment amount changes + aggregate reconciling change + consolidated change + residual on each of 4 adjacent pairs). Geographic practice total **200** (`74 + 20 + 54 + 28 + 24`). Ordinary components **686** (`486 + 200`). Independent recomputation of all 24 additions from accepted snapshots, including residual = `ΔP − ΣΔsegment − Δreconciling` and residual = `−ΔD` with `D` = reconstructed − reported, at maximum absolute error **0.0**:

| Quantity | Value |
|---|---|
| Americas operating-profit amount change FY2023 | `636724.0` |
| China Mainland amount change FY2023 | `29547.0` |
| Rest of World amount change FY2023 | `35530.0` |
| Aggregate reconciling amount change FY2023 | `-706748.0` |
| Consolidated operating-profit amount change FY2023 | `-4947.0` |
| Amount-change residual FY2023 | `0.0` |
| Americas operating-profit amount change FY2024 | `433444.0` |
| China Mainland amount change FY2024 | `140451.0` |
| Rest of World amount change FY2024 | `98628.0` |
| Aggregate reconciling amount change FY2024 | `131745.0` |
| Consolidated operating-profit amount change FY2024 | `804268.0` |
| Amount-change residual FY2024 | `0.0` (`804268 − (433444 + 140451 + 98628) − 131745`) |
| Americas operating-profit amount change FY2025 | `78373.0` |
| China Mainland amount change FY2025 | `172543.0` |
| Rest of World amount change FY2025 | `113114.0` |
| Aggregate reconciling amount change FY2025 | `8991.0` |
| Consolidated operating-profit amount change FY2025 | `373021.0` |
| Amount-change residual FY2025 | `0.0` |
| Americas operating-profit amount change FY2026 | `-454899.0` |
| China Mainland amount change FY2026 | `191264.0` |
| Rest of World amount change FY2026 | `30955.0` |
| Aggregate reconciling amount change FY2026 | `-62402.0` |
| Consolidated operating-profit amount change FY2026 | `-295082.0` |
| Amount-change residual FY2026 | `0.0` (`-295082 − (-454899 + 191264 + 30955) − (-62402)`) |
| Accepted `D_t` (reconstructed − reported), all five periods | `0.0` |
| Maximum bridge / `−ΔD` identity error | `0.0` |
| Opening FY2022 amount changes / residual | `None` |

These admitted residuals being `0.0` is the actual measured result, not a nominal nonzero claim.

Workbook Check on the admitted Lululemon geographic pair remains **686** (`486 + 74 + 20 + 54 + 28 + 24`). Blank then formula-filled correct; authenticated source/formula tamper still rejects without disclosure. Store fixture **702** (`486 + 200 + 8 + 8`). Mixed selected 2/4 Check **704**. Selected-document compsales Check **696**. Fast Retailing **577**. Geo sources/practice **56/200**. Preserved **486**. Unavailable **101**. Segment-margin formulas **15**.

Relocated cross-sheet/nonadjacent geographic operating-profit sources produce amount-change formulas from mapped current/prior ifop cells, and reconciling amount-change formulas from mapped signed monetary contributions, rather than adjacent columns or rounded margins. Notes distinguish monetary changes from margin attribution and make no normalization, organic-growth, causal, or BAV NOPAT claims.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Residual-sign contract `D` = reconstructed − reported and `R = −ΔD`; Answer-Key/catalog Notes; synthetic helper residuals `+11.0` / `-7.0`; production IFOP-mismatch rejection with immutable inputs; admitted/reload actual `D` and residuals `0.0`; all 24 additions recomputed, identity error **0.0**; geographic analysis+workbook **23 passed**; focused required suite **1502 passed**; complete `core/tests` **3237 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Zero current/prior revenue does not suppress available profit amount changes; unaffected mix/within remain `UNDEFINED_RATIO` where required; losses, zeros, negative changes, and signed reconcilers; family transition uses aggregate signed sums; relocated amount-change formulas follow mapped ifop sources and signed contributions; tamper still authenticated; store fixture **702**; mixed selected 2/4 Check **704**; selected-document compsales Check **696**; Fast Retailing **577**; geo **56/200**; preserved **486**; unavailable **101** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 segment-margin formulas; signed item-level bridges; revenue-growth contributions; operating-margin contribution bridge; mix/within midpoint decomposition |
| Arithmetic-only, not admitted | Synthetic nonzero residuals `+11.0` / `-7.0` at `_operating_profit_amount_bridge` |
| Not claimed | Excel engine recalculation; admitted nonzero `D` or residual; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py -q --tb=short` | 0 | **23 passed** in **5.15s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1502 passed** in **43.28s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3237 passed**, **0 failed** in **272.02s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/geographic_segment.py` | `c769dc2f0f7a78f6897aa0f2fe0d526ff4dcd560fc7936977a0982364cc49a5c` | 34093 |
| `core/engine/component_catalog.py` | `a15f14696283bc36e6edf347662d643e12c2ad161f4abec9912c7c6ca375d7b6` | 288049 |
| `core/tests/test_geographic_segment_analysis.py` | `f413ac8b61e731d7d542289f908150fefc7739db71c125d495f88603140bb615` | 58177 |
| `core/tests/test_geographic_segment_workbook.py` | `a3d606a1812282da7a3281ef38998c94b3f7a8766cb96e5bdd2cba0cbad4db55` | 104818 |
| `RESULT.md` | (this file) | |

Unchanged this repair: `core/engine/reference_model.py` SHA-256 `be1f434c85085c065ceb06c86f491cce4fd98dcc04a4e870c2dd1f9af32842c1` (413366); `core/model/historical_expected.py` SHA-256 `429ec3f8b63ba60c0fc0f3a0df1f0feba0faeb4ecac0d913c0701f9ace1326ee` (68447); `core/tests/test_operating_kpi_workbook.py` SHA-256 `a97ea7738c68bf6c11bcc152038cbc2cd950f8bffb59209b1aef83eef162d15b` (159571).

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Eligible geographic snapshots continue to expose identity-specific adjacent operating-profit amount changes, aggregate reconciling amount change, consolidated amount change, and a signed residual. Admitted residuals remain actually `0.0`.

Working-tree HEAD is `6ac7e062822c7d902c43d236413bc6034a4f55f2`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Remaining scope

This child repairs the geographic operating-profit amount-change residual-sign contract on the accepted Geographic Analysis Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.57` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic baseline **74**, prior increment’s **20** revenue-growth contribution identities, prior increment’s **54** margin-bridge identities, and prior increment’s **28** mix/within identities reported separately from this increment’s **24** amount-change identities (**200** combined); Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales and revenue/SPSF relationship identities remain when eligible. Management-history adjacent-change and SPSF practice remain when eligible selections exist, reported separately from the previous **678**-cell store fixture, which is now **702** with this increment’s geographic amount-change identities. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, revenue/SPSF, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
