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

---

# Current assessment — authorized REVISED_APPROACH (plan `81af8967a78c45748b92c7f57314ef4c`)

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Work:** `06c5cb92775a41e1a9b7515d0268b9e4` (retained)  
**Step:** 9M.2.4.1.1.1.58  
**Input:** `20260918-115651-000000007`  
Working-tree HEAD `548e9b3f6fe4d31c431e58367a4d07cba04937a2`. No commit / push / sync / checkpoint / branch change. No code edits this child. A partial RESULT append was present from interruption; it was inspected, preserved in structure, and completed only after fresh verification. Spreadsheet-engine recalculation was **not** performed; Check used formula-string match and injected cached-value probes. This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance. Input incorporation is not itself acceptance.

`TARGET.md` SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864), unchanged. Current `IMPLEMENTATION.md` SHA-256 `101349067fcda9df04eb90ec608d6a61c59b8147e1daa0d665090317d1bb9753` (11872). Both treated as read-only.

## Authorized correction (supersedes obsolete blocker only)

Review-authorized `REVISED_APPROACH` supersedes **only** the machine-generated admitted-nonzero reconstructed-versus-reported coverage that the residual-sign repair recorded as its blocker. That earlier **Blocker** paragraph is obsolete for this child and is **not** a remaining acceptance requirement.

Replacement obligations, all measured this child:

1. Exact-reconciliation admitted controls: source validation, supplied-filing reconciliation, standardization, export/reload, and ordinary Trainer/Answer-Key/Check builds assert actual `D_t = 0.0` and amount-change residuals `0.0` (opening `None`), not nominal nonzero claims.
2. Production rejects positive (`+11.0`, corporate: `50.0 != 61.0`) and negative (`−7.0`, itemized: `55.0 != 48.0`) inconsistent reconstructed-versus-reported differences; inputs unchanged after the raise; `SEGMENT_BRIDGE_TOLERANCE` remains `0.0`; validation was not patched.
3. Independently calculated synthetic residuals at `_operating_profit_amount_bridge`: `+11.0` (`D_t=-6.0`, `D_prior=5.0`) and `−7.0` (`D_t=7.0`, `D_prior=0.0`), with bridge equation and `R = −ΔD`; exact equality; rejects zeroed/negated residuals. Synthetic arithmetic coverage only, never admitted historical evidence.

Every other retained acceptance requirement is unchanged, including `D_t` = reconstructed − reported, `R_t = −(D_t − D_previous)`, current-minus-immediately-prior monetary changes, aggregate ADD/SUBTRACT across both families, opening `None`, uncompressed gaps, dependent-only `SOURCE_UNAVAILABLE`, and zero revenue not suppressing available amount changes.

## Required plan change

No required plan change. The authorized correction is already in `IMPLEMENTATION.md`. Historical observations, executions, and the prior BLOCKED status above are preserved as written.

## Code this child

No remaining defects versus the corrected criteria. Implementation hashes match the residual-sign repair (authenticated, not edited):

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/geographic_segment.py` | `c769dc2f0f7a78f6897aa0f2fe0d526ff4dcd560fc7936977a0982364cc49a5c` | 34093 |
| `core/engine/component_catalog.py` | `a15f14696283bc36e6edf347662d643e12c2ad161f4abec9912c7c6ca375d7b6` | 288049 |
| `core/engine/reference_model.py` | `be1f434c85085c065ceb06c86f491cce4fd98dcc04a4e870c2dd1f9af32842c1` | 413366 |
| `core/model/historical_expected.py` | `429ec3f8b63ba60c0fc0f3a0df1f0feba0faeb4ecac0d913c0701f9ace1326ee` | 68447 |
| `core/trainer/checker.py` | `aec15dfb7ce6ee356a5e6b718ffdeda9fd63dcabe11740b87ab6a7797a27938d` | 22993 |
| `core/tests/test_geographic_segment_analysis.py` | `f413ac8b61e731d7d542289f908150fefc7739db71c125d495f88603140bb615` | 58177 |
| `core/tests/test_geographic_segment_workbook.py` | `a3d606a1812282da7a3281ef38998c94b3f7a8766cb96e5bdd2cba0cbad4db55` | 104818 |
| `core/tests/test_operating_kpi_workbook.py` | `a97ea7738c68bf6c11bcc152038cbc2cd950f8bffb59209b1aef83eef162d15b` | 159571 |

Edited this child: `RESULT.md` only (this append).

## Fresh measured verification (this child)

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent recomputation of all **24** supplied-fixture amount-change additions (3 segment + aggregate reconciling + consolidated + residual, four adjacent pairs) from admitted Lululemon snapshots: maximum bridge error **0.0**, maximum `R + ΔD` identity error **0.0**. Admitted `D_t` all five periods **0.0**. Opening FY2022 amount changes / residual `None`. Geographic sources **56**. Practice **200** (`74+20+54+28+24`). Ordinary components **686** (`486+200`). Other fixture totals measured separately: store Check **702** (`486+200+8+8`); mixed selected 2/4 Check **704** (`702+2`); selected-document compsales Check **696**; Fast Retailing **577**; unavailable **101**; segment-margin formulas **15**.

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py -q --tb=short` | 0 | **23 passed** in **5.89s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1502 passed** in **47.51s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3237 passed**, **0 failed** in **278.50s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

## Fresh vs retained vs synthetic (this child)

| Kind | This child |
|---|---|
| Fresh | Authorized supersession of admitted-nonzero coverage; exact-reconciliation admitted `D`/`R` actually `0.0`; independent 24-addition recomputation identity error **0.0**; geographic **23 passed**; focused required suite **1502 passed**; complete `core/tests` **3237 passed / 0 failed**; checkpoints **50/50 MATCH**; eight extractions unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; implementation hashes authenticated unchanged |
| Retained executions, re-authenticated by the fresh suite above | Residual-sign contract `D` reconstructed-minus-reported and `R = −ΔD`; production IFOP-mismatch rejection with immutable inputs; synthetic helper residuals `+11.0` / `−7.0`; zero current/prior revenue does not suppress amount changes; relocated formulas follow mapped ifop sources and signed contributions; tamper still authenticated without disclosure; store **702**; mixed **704**; compsales **696**; Fast Retailing **577**; geo **56/200**; preserved **486**; unavailable **101** |
| Arithmetic-only, not admitted | Synthetic nonzero residuals `+11.0` / `-7.0` at `_operating_profit_amount_bridge` |
| Not claimed | Excel engine recalculation; admitted nonzero `D` or residual; parent or Step 9 completion; G6–G9 remainder |

## Genuine remaining blockers

None for this bounded child after the authorized correction. Unfinished commitments listed above (parents `9M.2.4.1.1.1` / `9M.2.4.1.1` / `9M.2.4.1` / `9M.2.4`, requests `20260914-193338-000000004` and `20260915-042248-000000005`, A2-ED/B7-MID, A5/B8/E10/E11, G6–G9, Normalization Judgment + Earnings Normalization, analytical focus remainder, TARGET Step 9 exit) remain unresolved and are outside this correction. No prospective IDs reserved. Continue normal stages.

---

# RESULT.md — Step 9M.2.4.1.1.1.59 Geographic Analysis: revenue and margin effects on operating-profit change

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.59 — Geographic Analysis — Revenue and margin effects on operating-profit change  
**Work:** `15a91bfc2d584a6cba58be599a3a5dac`  
**Plan:** `6aecb627029742259eedc16863828d76`  
**Finding:** `geographic-operating-profit-revenue-margin-effects`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted amount-change work `06c5cb92775a41e1a9b7515d0268b9e4` and the authorized residual-sign correction remain complete and are not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `de2fd12f6ecf45ab94e7e10d7cf4954b36e5a99b77eef000e1c2df52c64ad178` (10392).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance.

No interrupted working-tree edits were present at start. `core/trainer/checker.py` required no edits.

## Required plan change

No required plan change.

## Task 1 — Monetary revenue and margin effects

For each segment and immediately adjacent canonical pair, with revenue `V`, operating profit `P` and decimal reported margin `m = P / V`:

- revenue effect `(V_t − V_p) × (m_t + m_p) / 2`
- margin effect `(m_t − m_p) × (V_t + V_p) / 2`

Unrounded values; existing currency/scale; no percentage-point multiplier; no new historical inputs. The two effects sum to existing `ΔP` within scale-appropriate floating-point tolerance. Opening effects are `None`. Missing current/prior snapshots yield dependent-only `SOURCE_UNAVAILABLE` without compressing gaps. Zero segment revenue at either endpoint yields `UNDEFINED_RATIO` for that segment’s effects; existing amount changes remain available; unaffected segments remain available. Both presentation families, signed reconcilers, losses, and zero profits are preserved.

## Task 2 — Ordinary learning surface

Two semantic practice families keyed by segment and period: `geographic_operating_profit_revenue_effect` and `geographic_operating_profit_margin_effect`. Expected-value dispatch, mapped formulas from relocated revenue sources and existing margin practices, and ordinary geographic schedule rows. Reuses existing revenue, margin, and amount-change dependencies. No new source rows and no duplicate residual practices. Unavailable results remain non-practice displays. Answer-Key Notes explain the midpoint arithmetic allocation in monetary units and its reconciliation to operating-profit amount change, without volume/price, organic-growth, causal, normalization, or BAV NOPAT claims. Trainer practice cells are blank bright yellow without answers/formulas/Notes; Answer Key linked formulas with concise Notes and no yellow anywhere.

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Supplied-filing reconciliation → standardization → export/reload → ordinary geographic workbook fixture remains five canonical periods with **56** selected geographic sources. Geographic practice total **224** (`74 + 20 + 54 + 28 + 24 + 24`). Ordinary components **710** (`486 + 224`). The 24 additions are two effects × three segments × four adjacent pairs, reported separately from the existing 24 amount-change identities. Independent recomputation of all 24 new supplied-fixture effects from accepted revenues and profits, with segment identity `rev + mgn = ΔP` and consolidated identity `Δreported = Σrevenue effects + Σmargin effects + Δsigned reconcilers + existing amount-change residual`, at maximum absolute error **2.3283064365386963e-10**:

| Quantity | Value |
|---|---|
| Americas revenue / margin effect FY2023 | `545959.002747382` / `90764.99725261805` (sum `636724.0`) |
| China Mainland revenue / margin effect FY2023 | `51688.96103173528` / `-22141.961031735274` (sum `29547.0`) |
| Rest of World revenue / margin effect FY2023 | `26550.388987212256` / `8979.611012787747` (sum `35530.0`) |
| FY2023 `ΔP_cons` identity | `-4947.0 = 636724 + 29547 + 35530 + (-706748) + 0` |
| Americas revenue / margin effect FY2024 | `306186.7863742937` / `127257.21362570612` (sum `433444.0`) |
| China Mainland revenue / margin effect FY2024 | `133890.48894788924` / `6560.511052110715` (sum `140451.0`) |
| Rest of World revenue / margin effect FY2024 | `52419.89691015994` / `46208.10308984005` (sum `98628.0`) |
| FY2024 `ΔP_cons` identity | `804268.0 = 433444 + 140451 + 98628 + 131745 + 0` |
| Americas revenue / margin effect FY2025 | `113448.70301290436` / `-35075.7030129042` (sum `78373.0`) |
| China Mainland revenue / margin effect FY2025 | `144027.86003765048` / `28515.13996234952` (sum `172543.0`) |
| Rest of World revenue / margin effect FY2025 | `60399.22281338311` / `52714.7771866169` (sum `113114.0`) |
| FY2025 `ΔP_cons` identity | `373021.0 = 78373 + 172543 + 113114 + 8991 + 0` |
| Americas revenue / margin effect FY2026 | `-28660.187206984265` / `-426238.8127930156` (sum `-454899.0`) |
| China Mainland revenue / margin effect FY2026 | `152284.38636578634` / `38979.6136342137` (sum `191264.0`) |
| Rest of World revenue / margin effect FY2026 | `47802.88417423252` / `-16847.884174232506` (sum `30955.0`) |
| FY2026 `ΔP_cons` identity | `-295082.0 = -454899 + 191264 + 30955 + (-62402) + 0` |
| Accepted `D_t` (reconstructed − reported), all five periods | `0.0` |
| Admitted amount-change residual `R` | opening `None`; four adjacent pairs `0.0` |
| Maximum segment / consolidated identity error | `2.3283064365386963e-10` |
| Opening FY2022 revenue / margin effects | `None` |

Admitted residuals remaining `0.0` is the actual measured result, not a nominal nonzero claim. `D = reconstructed − reported` and existing residual `R = −ΔD` are preserved. Synthetic arithmetic is not historical evidence.

Workbook Check on the admitted Lululemon geographic pair is **710** (`486 + 224`). Blank then formula-filled correct; authenticated source/formula tamper still rejects without disclosure. Store fixture **726** (`486 + 224 + 8 + 8`). Mixed selected 2/4 Check **728**. Selected-document compsales Check **720**. Fast Retailing **577**. Geo sources/practice **56/224**. Preserved **486**. Unavailable **101**. Segment-margin formulas **15**.

Relocated cross-sheet/nonadjacent geographic revenue sources produce revenue/margin-effect formulas from mapped current/prior revenue cells and existing margin practices, rather than adjacent columns or a percentage-point multiplier. Notes explain midpoint monetary allocation and reconciliation to operating-profit amount change; they make no volume/price, organic-growth, causal, normalization, or BAV NOPAT claims.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Midpoint revenue/margin effects; all 24 additions independently recomputed, max identity error **2.3283064365386963e-10**; geo **56/224**; ordinary **710**; store **726**; mixed **728**; compsales **720**; Fast Retailing **577**; geographic analysis+workbook **24 passed**; focused required suite **1503 passed**; complete `core/tests` **3238 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Opening effects `None`; sparse missing snapshots `SOURCE_UNAVAILABLE` without gap compression; zero current/prior segment revenue `UNDEFINED_RATIO` for that segment’s effects while amount changes remain available; unaffected segments remain available; pure revenue, pure margin, simultaneous, offsetting, and unchanged-profit cases; relocated formulas follow mapped revenue sources and margin practices; tamper still authenticated; preserved **486**; unavailable **101**; segment-margin formulas **15** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 segment-margin formulas; signed item-level bridges; revenue-growth contributions; operating-margin contribution bridge; mix/within midpoint decomposition; amount-change residual-sign contract |
| Arithmetic-only, not admitted | Synthetic helper coverage at `_operating_profit_amount_bridge` (`+11.0` / `-7.0`) retained from the prior child; not used as historical evidence here |
| Not claimed | Excel engine recalculation; admitted nonzero `D` or residual; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py -q --tb=short` | 0 | **24 passed** in **5.51s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1503 passed** in **44.06s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3238 passed**, **0 failed** in **273.57s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/geographic_segment.py` | `ff5dbc9e24671df112ee202544b4f1a016d193fbc2a84868b4511aa2ff32e487` | 38735 |
| `core/engine/component_catalog.py` | `db2c4ce734273641eea595b573215c3797124a981ffb0abed059677f71938c2a` | 294019 |
| `core/engine/reference_model.py` | `4f629ca74293afdfd62732682f9e2ed7a9ec96398e7f9980baa9edf97fd52ad4` | 418131 |
| `core/model/historical_expected.py` | `9dd28473d772258772c52f456daabcb33b26b473aae4abaea1a37a577f9f51a8` | 68828 |
| `core/tests/test_geographic_segment_analysis.py` | `de03a2534fbcf71f9393139881df8a36018030a9cd9e27c49d59a4deb6caaaa0` | 67851 |
| `core/tests/test_geographic_segment_workbook.py` | `1d8849f58624e060260a3b366baf52a88e8349ceaf4e69f1afc9b31af4efbf92` | 117156 |
| `core/tests/test_operating_kpi_workbook.py` | `9368bd2b11d0708db85aef298edf9111c57d9ed6138f3d288bb413bddb03d86b` | 159644 |
| `RESULT.md` | (this file) | |

Unchanged this child: `core/trainer/checker.py` SHA-256 `aec15dfb7ce6ee356a5e6b718ffdeda9fd63dcabe11740b87ab6a7797a27938d` (22993).

Working-tree HEAD is `ff5a5cfdd00f33f3e39ba8494da5faaae024be52`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Remaining scope

This child adds geographic operating-profit revenue and margin effects on the accepted Geographic Analysis Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.58` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic baseline **74**, prior **20** revenue-growth contribution identities, prior **54** margin-bridge identities, prior **28** mix/within identities, prior **24** amount-change identities, and this increment’s **24** revenue/margin-effect identities reported separately (**224** combined); Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales and revenue/SPSF relationship identities remain when eligible. Management-history adjacent-change and SPSF practice remain when eligible selections exist, reported separately from the previous **702**-cell store fixture, which is now **726** with this increment’s geographic revenue/margin-effect identities. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, revenue/SPSF, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence.

Exact admitted reconciliation, production rejection of inconsistent reconstructed-versus-reported differences, and separately labelled synthetic signed residual coverage from `20260918-115651-000000007` remain in force. `SEGMENT_BRIDGE_TOLERANCE = 0.0`. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

---

# RESULT.md — Step 9M.2.4.1.1.1.60 Geographic Analysis: incremental reported operating margins

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.60 — Geographic Analysis — Incremental reported operating margins  
**Work:** `ca3865b066c045a5b2a85ef3e0a4947a`  
**Plan:** `89995ebe24c1453a9cad80347a5a00a1`  
**Finding:** `geographic-incremental-reported-operating-margins`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted revenue/margin-effect work `15a91bfc2d584a6cba58be599a3a5dac` and the authorized residual-sign correction remain complete and are not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `c10b5402ade4e55f3e0318a6ce53f4675a790e1793994cea537f443122bc621f` (10681).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance.

No interrupted working-tree edits were present at start. `core/trainer/checker.py` required no edits.

## Required plan change

No required plan change.

## Task 1 — Incremental reported operating margins

For each segment and reported consolidated total on immediately adjacent canonical periods, incremental reported operating margin is `(P_t − P_p) / (V_t − V_p)` from unrounded accepted operating profit and revenue. Opening results are `None`. Missing current/prior snapshots yield dependent-only `SOURCE_UNAVAILABLE` without compressing gaps. Exactly zero revenue change is `UNDEFINED_RATIO`, including unchanged profit; zero and ordinary operating margin are not substituted. Signed declines, losses, zero profits, and zero endpoint revenue are preserved when Δrevenue is nonzero. Ratios are not clamped. Consolidated ratios use reported consolidated profit and revenue, including existing signed reconcilers, and are not the sum or average of segment incremental margins.

## Task 2 — Ordinary learning surface

Two semantic practice families: `geographic_operating_profit_incremental_margin` (segment, identity+period) and `geographic_consolidated_operating_profit_incremental_margin` (period). Formulas reuse populated revenue sources and existing amount-change practices: `IF((V_t−V_p)=0,NA(),ΔP/(V_t−V_p))`. Ratios store as decimals and display as percentages. Answer-Key Notes define change in reported operating profit per unit of revenue change, distinguish reported operating margin, explain signed declines and small-denominator sensitivity, identify consolidated reconciling effects, and deny marginal cost, operating leverage, organic growth, normalization, and BAV NOPAT. Trainer practices are blank bright yellow without answers/formulas/Notes; Answer Key linked formulas with concise Notes and no yellow anywhere.

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Supplied-filing reconciliation → standardization → export/reload → ordinary geographic workbook fixture remains five canonical periods with **56** selected geographic sources. All 16 supplied-fixture denominators are nonzero, so the 16 additions are numeric practices (0 undefined displays). Geographic practice total **240** (`74 + 20 + 54 + 28 + 24 + 24 + 16`). Ordinary components **726** (`486 + 240`). Independent recomputation of three segment ratios and one consolidated ratio on each of four adjacent pairs, verifying `incremental margin × Δrevenue = Δoperating profit` wherever defined, at maximum absolute error **3.637978807091713e-12**:

| Quantity | Value |
|---|---|
| Americas incremental FY2023 | `0.4195742078669011` (`636724 / 1517548`) |
| China Mainland incremental FY2023 | `0.2077234572067322` (`29547 / 142242`) |
| Rest of World incremental FY2023 | `0.18303960105300576` (`35530 / 194111`) |
| Consolidated incremental FY2023 | `-0.0026684272784792715` (`-4947 / 1853901`) |
| Americas incremental FY2024 | `0.5323602634756133` (`433444 / 814193`) |
| China Mainland incremental FY2024 | `0.3626816300286373` (`140451 / 387257`) |
| Rest of World incremental FY2024 | `0.3209397676613192` (`98628 / 307310`) |
| Consolidated incremental FY2024 | `0.5330655637742252` (`804268 / 1508760`) |
| Americas incremental FY2025 | `0.2643191269067718` (`78373 / 296509`) |
| China Mainland incremental FY2025 | `0.43398637245112265` (`172543 / 397577`) |
| Rest of World incremental FY2025 | `0.41167992662740843` (`113114 / 274762`) |
| Consolidated incremental FY2025 | `0.38501498687100555` (`373021 / 968848`) |
| Americas incremental FY2026 | `5.608282374987671` (`-454899 / -81112`; not clamped) |
| China Mainland incremental FY2026 | `0.48610539264274566` (`191264 / 393462`) |
| Rest of World incremental FY2026 | `0.15314856226870635` (`30955 / 202124`) |
| Consolidated incremental FY2026 | `-0.5735605686584745` (`-295082 / 514474`) |
| Numeric additions / undefined displays | **16** / **0** |
| Accepted `D_t` (reconstructed − reported), all five periods | `0.0` |
| Admitted amount-change residual `R` | opening `None`; four adjacent pairs `0.0` |
| Maximum `incremental × ΔV = ΔP` identity error | `3.637978807091713e-12` |
| Opening FY2022 incremental margins | `None` |

Admitted residuals remaining `0.0` is the actual measured result, not a nominal nonzero claim. `D = reconstructed − reported` and existing residual `R = −ΔD` are preserved. Consolidated incremental is not the sum or average of segment incrementals. Synthetic arithmetic is not historical evidence.

Workbook Check on the admitted Lululemon geographic pair is **726** (`486 + 240`). Blank then formula-filled correct; authenticated source/formula tamper still rejects without disclosure. Store fixture **742** (`486 + 240 + 8 + 8`). Mixed selected 2/4 Check **744**. Selected-document compsales Check **736**. Fast Retailing **577**. Geo sources/practice **56/240**. Preserved **486**. Unavailable **101**. Segment-margin formulas **15**.

Relocated cross-sheet/nonadjacent geographic revenue sources produce incremental-margin formulas from mapped amount-change practices and mapped current/prior revenue cells, including the zero-denominator `NA()` guard, rather than adjacent columns or reported operating margin. Notes distinguish this change ratio from reported operating margin; they make no marginal-cost, operating-leverage, organic-growth, causal, normalization, or BAV NOPAT claims.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Incremental reported operating margins; all 16 additions independently recomputed, max identity error **3.637978807091713e-12**; geo **56/240**; ordinary **726**; store **742**; mixed **744**; compsales **736**; Fast Retailing **577**; geographic analysis+workbook **25 passed**; focused required suite **1504 passed**; complete `core/tests` **3239 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Opening incrementals `None`; sparse missing snapshots `SOURCE_UNAVAILABLE` without gap compression; zero revenue change `UNDEFINED_RATIO` including unchanged profit; rising/declining/offsetting revenues; losses; zero endpoint revenue with nonzero ΔV; unclamped ratios above 100%; relocated formulas follow mapped amount-change practices and revenue sources with `NA()` guards; tamper still authenticated; preserved **486**; unavailable **101**; segment-margin formulas **15** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 segment-margin formulas; signed item-level bridges; revenue-growth contributions; operating-margin contribution bridge; mix/within midpoint decomposition; amount-change residual-sign contract; revenue/margin effects |
| Arithmetic-only, not admitted | Synthetic helper coverage at `_operating_profit_amount_bridge` (`+11.0` / `-7.0`) retained from a prior child; not used as historical evidence here |
| Not claimed | Excel engine recalculation; admitted nonzero `D` or residual; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py -q --tb=short` | 0 | **25 passed** in **5.38s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1504 passed** in **45.03s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3239 passed**, **0 failed** in **272.14s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/geographic_segment.py` | `6425e454012f0595d921d1faa8bd62e56a22e1dd32cdac3478fe7ae2829e7229` | 41859 |
| `core/engine/component_catalog.py` | `1472467a6a9a7973cc4116debdc84e372027ee8d9fd77d5a8a18902e7331015a` | 299059 |
| `core/engine/reference_model.py` | `68962fbf8f9226d6535cd82f0b6fc089e2cbc3c677c596a1a07335a47d4619c4` | 422536 |
| `core/model/historical_expected.py` | `6c9d5268bd2987e5b6d004ce3c3ee99f7cf1912e080c91c39f61d965df7795ca` | 69265 |
| `core/tests/test_geographic_segment_analysis.py` | `4abd2e697b99e754e0292a03eafc3ba5829cd1531f14766c2e3c95b77264f1ab` | 79543 |
| `core/tests/test_geographic_segment_workbook.py` | `3849a8437658db20e2b00f7bca7bf5166edcfd076ad77b4aef3079b72fb3bbbb` | 128901 |
| `core/tests/test_operating_kpi_workbook.py` | `eeceefb2f048d9233f787919e32221b70073a24b8b8af7aa3d957f3c377a276c` | 159727 |
| `RESULT.md` | (this file) | |

Unchanged this child: `core/trainer/checker.py` SHA-256 `aec15dfb7ce6ee356a5e6b718ffdeda9fd63dcabe11740b87ab6a7797a27938d` (22993).

Working-tree HEAD is `c16a16b24568360240dca780faaa2439ba3527cb`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Remaining scope

This child adds geographic incremental reported operating margins on the accepted Geographic Analysis Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.59` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic baseline **74**, prior **20** revenue-growth contribution identities, prior **54** margin-bridge identities, prior **28** mix/within identities, prior **24** amount-change identities, prior **24** revenue/margin-effect identities, and this increment’s **16** incremental-margin identities reported separately (**240** combined); Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales and revenue/SPSF relationship identities remain when eligible. Management-history adjacent-change and SPSF practice remain when eligible selections exist, reported separately from the previous **726**-cell store fixture, which is now **742** with this increment’s geographic incremental-margin identities. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, revenue/SPSF, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence.

Exact admitted reconciliation, production rejection of inconsistent reconstructed-versus-reported differences, and separately labelled synthetic signed residual coverage from `20260918-115651-000000007` remain in force. `SEGMENT_BRIDGE_TOLERANCE = 0.0`. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

---

# RESULT.md — Step 9M.2.4.1.1.1.61 Geographic Analysis: reported operating-profit growth contributions

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.61 — Geographic Analysis — Reported operating-profit growth contributions  
**Work:** `963f02c4fa8d499d9609bb963ce98d99`  
**Plan:** `6f4622e2cd6d4609bea300cfd584e297`  
**Finding:** `geographic-reported-operating-profit-growth-contributions`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted incremental-margin work `ca3865b066c045a5b2a85ef3e0a4947a` and the authorized residual-sign correction remain complete and are not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `778dccc6babed0a419473296a997a92cdc24ff3a0c50b4c1c266e7cbd7fff58d` (10565).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance.

No interrupted working-tree edits were present at start. `core/trainer/checker.py` required no edits.

## Required plan change

No required plan change.

## Task 1 — Reported operating-profit growth bridge

On immediately adjacent canonical periods, reuse accepted segment profit changes `ΔP_s`, aggregate signed reconciling change `ΔB`, consolidated profit change `ΔP`, and prior reported consolidated profit `P_p`. Consolidated growth `g = ΔP/P_p` is a decimal. Segment contributions `c_s = 100×ΔP_s/P_p`, reconciling contribution `b = 100×ΔB/P_p`, and residual `r = 100×g−Σc_s−b` are percentage points. The residual is computed, never hard-coded zero, and equals `100×R/P_p = −100×ΔD/P_p` when defined, with `D` reconstructed-minus-reported and `R` the accepted amount-change residual. Opening results are `None`. Missing required adjacent inputs yield dependent-only `SOURCE_UNAVAILABLE` without compressing gaps. Exactly zero prior consolidated profit is `UNDEFINED_RATIO`, including unchanged profit. Signed negative prior profits, losses, zero current profit, and declines are preserved without absolute denominators. Zero segment profit or revenue does not suppress a bridge with available inputs and nonzero `P_p`. Aggregate signed reconcilers are compared across presentation transitions; unlike item identities are not matched.

## Task 2 — Ordinary learning surface

Four semantic families: `geographic_operating_profit_growth_contribution` (segment, identity+period), `geographic_reconciling_operating_profit_growth_contribution` (period), `geographic_consolidated_operating_profit_growth` (period), and `geographic_operating_profit_growth_contribution_residual` (period). Formulas reuse mapped amount-change practices and prior consolidated operating-profit sources: `IF(P_p=0,NA(),100*ΔP_s/P_p)`, `IF(P_p=0,NA(),ΔP/P_p)`, and `100×g−Σc_s−b`. Consolidated growth displays as a percentage; contributions and residual display as percentage points. Answer-Key Notes explain the common prior consolidated-profit denominator, signed-base interpretation, and reconciliation, and state that contributions are not each segment's own growth rate. Notes distinguish reported operating-profit growth from revenue growth, margin change, incremental margin, organic growth, causal attribution, normalized earnings, and BAV NOPAT. Trainer practices are blank bright yellow without answers/formulas/Notes; Answer Key linked formulas with concise Notes and no yellow anywhere. Unavailable results remain non-practice displays.

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Supplied-filing reconciliation → standardization → export/reload → ordinary geographic workbook fixture remains five canonical periods with **56** selected geographic sources. All 24 supplied-fixture denominators are nonzero, so the 24 additions are numeric practices (0 undefined displays). Geographic practice total **264** (`74 + 20 + 54 + 28 + 24 + 24 + 16 + 24`). Ordinary components **750** (`486 + 264`). Independent recomputation of three segment contributions, one reconciling contribution, consolidated growth, and residual on each of four adjacent pairs, verifying `r = 100×g − Σc_s − b` and `r = 100×R/P_p` wherever defined, at maximum absolute error **7.105427357601002e-15**:

| Quantity | Value |
|---|---|
| Prior consolidated operating profit FY2022 (`P_p` for FY2023) | `1333355.0` |
| Americas / China Mainland / Rest of World contribution FY2023 | `47.753524005234915` / `2.21598899017891` / `2.664706698516149` |
| Reconciling contribution FY2023 | `-53.0052386648717` |
| Consolidated operating-profit growth FY2023 | `-0.003710189709417222` (`-4947 / 1333355`) |
| Growth residual FY2023 | `7.105427357601002e-15` (`100×g − Σc − b`; `100×R/P_p = 0.0`) |
| Prior consolidated operating profit FY2023 (`P_p` for FY2024) | `1328408.0` |
| Americas / China Mainland / Rest of World contribution FY2024 | `32.62883090134959` / `10.572881223238644` / `7.424526199781995` |
| Reconciling contribution FY2024 | `9.917510282985347` |
| Consolidated operating-profit growth FY2024 | `0.6054374860735557` (`804268 / 1328408`) |
| Growth residual FY2024 | `0.0` |
| Prior consolidated operating profit FY2024 (`P_p` for FY2025) | `2132676.0` |
| Americas / China Mainland / Rest of World contribution FY2025 | `3.6748666932998733` / `8.0904459936718` / `5.303852999705534` |
| Reconciling contribution FY2025 | `0.42158302526966124` |
| Consolidated operating-profit growth FY2025 | `0.17490748711946869` (`373021 / 2132676`) |
| Growth residual FY2025 | `-2.831068712794149e-15` (`100×R/P_p = 0.0`) |
| Prior consolidated operating profit FY2025 (`P_p` for FY2026) | `2505697.0` |
| Americas / China Mainland / Rest of World contribution FY2026 | `-18.154589321853358` / `7.6331655423620655` / `1.235384805106124` |
| Reconciling contribution FY2026 | `-2.490404865392743` |
| Consolidated operating-profit growth FY2026 | `-0.11776443839777914` (`-295082 / 2505697`) |
| Growth residual FY2026 | `-2.6645352591003757e-15` (`100×R/P_p = 0.0`) |
| Numeric additions / undefined displays | **24** / **0** |
| Accepted `D_t` (reconstructed − reported), all five periods | `0.0` |
| Admitted amount-change residual `R` | opening `None`; four adjacent pairs `0.0` |
| Maximum contribution-sum / scaled-residual identity error | `7.105427357601002e-15` |
| Opening FY2022 growth contributions / residual | `None` |

Admitted residuals remaining `0.0` is the actual measured amount-change result, not a nominal nonzero claim. Growth residuals are computed, not forced to zero; the tiny nonzero values are floating-point reconstruction of `100×g − Σc − b` against exact `R = 0.0`. `D = reconstructed − reported` and existing residual `R = −ΔD` are preserved. Contributions are not each segment's own growth rate. Synthetic arithmetic is not historical evidence.

Workbook Check on the admitted Lululemon geographic pair is **750** (`486 + 264`). Blank then formula-filled correct; authenticated source/formula tamper still rejects without disclosure. Store fixture **766** (`486 + 264 + 8 + 8`). Mixed selected 2/4 Check **768**. Selected-document compsales Check **760**. Fast Retailing **577**. Geo sources/practice **56/264**. Preserved **486**. Unavailable **101**. Segment-margin formulas **15**.

Relocated cross-sheet/nonadjacent geographic operating-profit sources produce growth-contribution formulas from mapped amount-change practices and mapped prior consolidated operating-profit cells, including the zero-denominator `NA()` guard, rather than adjacent columns or each segment's own growth rate. Notes explain the common prior consolidated-profit denominator and signed-base interpretation; they make no revenue-growth, margin-change, incremental-margin, organic-growth, causal, normalization, or BAV NOPAT claims.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Reported operating-profit growth contributions; all 24 additions independently recomputed, max identity error **7.105427357601002e-15**; geo **56/264**; ordinary **750**; store **766**; mixed **768**; compsales **760**; Fast Retailing **577**; geographic analysis+workbook **26 passed**; focused required suite **1505 passed**; complete `core/tests` **3240 passed / 0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Opening growth contributions `None`; sparse missing snapshots `SOURCE_UNAVAILABLE` without gap compression; zero prior consolidated profit `UNDEFINED_RATIO` including unchanged profit; signed negative prior profits and loss-to-profit; offsetting segment changes; zero segment profit/revenue does not suppress a nonzero-`P_p` bridge; family-transition aggregate signed reconcilers; relocated formulas follow mapped amount-change practices and prior consolidated profit sources with `NA()` guards; tamper still authenticated; preserved **486**; unavailable **101**; segment-margin formulas **15** |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 segment-margin formulas; signed item-level bridges; revenue-growth contributions; operating-margin contribution bridge; mix/within midpoint decomposition; amount-change residual-sign contract; revenue/margin effects; incremental reported operating margins |
| Arithmetic-only, not admitted | Synthetic helper coverage at `_operating_profit_amount_bridge` (`+11.0` / `-7.0`) retained from a prior child; not used as historical evidence here |
| Not claimed | Excel engine recalculation; admitted nonzero `D` or amount-change residual; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py -q --tb=short` | 0 | **26 passed** in **5.70s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1505 passed** in **45.30s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3240 passed**, **0 failed** in **275.74s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/model/geographic_segment.py` | `a4f797861800bec89c8caea74dff4c7b1ad856f1380d9ee0cf3861e023a61da7` | 47439 |
| `core/engine/component_catalog.py` | `d7013e80c8b7f5a4ac8e057cd1fcb5ac6bd4f3f38d7734dc39c636b100def957` | 310115 |
| `core/engine/reference_model.py` | `b6baa84f83834a4050d82005ebc03211bf7ce373983b46e944fb152ee323b5d5` | 431289 |
| `core/model/historical_expected.py` | `34bf15a402b9251ff812ff4cddcb3094cabc0e6d03df2a9f4012e12a5e8ff1c8` | 70126 |
| `core/tests/test_geographic_segment_analysis.py` | `0c46196f7de0b23140870f45b970dd1b19ca6700459e187ffdc50083e5b98a6a` | 91593 |
| `core/tests/test_geographic_segment_workbook.py` | `7080cf4db3db9bbb87266e694cf792e5cacb38833360eb2cb5a7b2b7693e0e6a` | 146760 |
| `core/tests/test_operating_kpi_workbook.py` | `4e12ceb3e74c6611366ad45b178c5495dd3baabaa5ec26c52e82ca0da02116ed` | 159800 |
| `RESULT.md` | (this file) | |

Unchanged this child: `core/trainer/checker.py` SHA-256 `aec15dfb7ce6ee356a5e6b718ffdeda9fd63dcabe11740b87ab6a7797a27938d` (22993).

Working-tree HEAD is `04b70bf4ddd97290be510e390405014931b500d6`. `.git/autocycle/latest-implementation` was not rewritten.

---

## Remaining scope

This child adds geographic reported operating-profit growth contributions on the accepted Geographic Analysis Trainer/Answer-Key/Check path. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.60` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic baseline **74**, prior **20** revenue-growth contribution identities, prior **54** margin-bridge identities, prior **28** mix/within identities, prior **24** amount-change identities, prior **24** revenue/margin-effect identities, prior **16** incremental-margin identities, and this increment’s **24** operating-profit growth-contribution identities reported separately (**264** combined); Fast Retailing **577** / **0** unavailable. Prior increments added **8** store-count practice identities, **5** non-practice count sources, **8** revenue/store practice identities and **5** non-practice revenue sources on source-bound store fixtures only. Comparable-sales and revenue/SPSF relationship identities remain when eligible. Management-history adjacent-change and SPSF practice remain when eligible selections exist, reported separately from the previous **742**-cell store fixture, which is now **766** with this increment’s geographic operating-profit growth-contribution identities. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store, revenue/comparable-sales, revenue/SPSF, and management-KPI series APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence.

Exact admitted reconciliation, production rejection of inconsistent reconstructed-versus-reported differences, and separately labelled synthetic signed residual coverage from `20260918-115651-000000007` remain in force. `SEGMENT_BRIDGE_TOLERANCE = 0.0`. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

---

# RESULT.md — Step 9M.2.4.1.1.1.62 Geographic Analysis: spreadsheet-engine verification

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.62 — Geographic Analysis — Spreadsheet-engine verification  
**Work:** `473bb39bc59a48cc973fd616064d012a`  
**Plan:** `4cd09ded7301403e8e34bb12d01812db`  
**Finding:** `geographic-spreadsheet-recalculation-acceptance`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted growth-contribution work `963f02c4fa8d499d9609bb963ce98d99` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `77344eca10c4aca76241a41f9475e85665c32d1360a2bb5b89d59fee14f2f0aa` (9656).  
No commit / push / sync / checkpoint / branch change. No production-code repair, release rewrite, forecasting, or valuation.  
This child does **not** declare parent, Geographic Analysis product, or Step 9 acceptance.

No interrupted production-tree edits were present. Temporary verification artifacts live only under `/tmp/bav_geo_excel_verify_9M2411162/`. Edited this child: `RESULT.md` only.

## Required plan change

No required plan change.

## Task 1 — Ordinary pair and Excel engine

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used in-memory copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Supplied-filing path: validate four Lululemon annual extracts → `reconcile_filings(..., admit_periods=(2022-01-30,))` → `standardize_reconciled` → JSON export/reload → ordinary `build_training_workbook`. Geographic sources **56**. Geographic practices **264**. Ordinary components **750** (`486 + 264`). Unavailable displays **101**. Segment-margin formulas **15**. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

Exactly one matching pair was generated in temporary storage:

| Copy | Path | SHA-256 | Bytes |
|---|---|---|---:|
| Pristine / inspect Trainer | `/tmp/bav_geo_excel_verify_9M2411162/{pristine,inspect}/LULU_GEO_Trainer.xlsx` | `6b6803dda0a50fc5fa33ffb80a1e293f37a2e445e8ae2541376a8c64028ec9c4` | 40987 |
| Pristine / inspect Answer Key | `/tmp/bav_geo_excel_verify_9M2411162/{pristine,inspect}/LULU_GEO_Answer_Key.xlsx` | `9d51808ba9afe1990448974fe368f9c3668b54db8f8a3d2fca313d49db937be1` | 184644 |

Inspect copies were never opened by Excel; inspect Answer Key SHA-256 remained unchanged after recalculation of the internal copy.

Microsoft Excel **16.113** (`/Applications/Microsoft Excel.app/Contents/MacOS/Microsoft Excel`). Working command: `osascript` `tell application "Microsoft Excel"` → `open POSIX file` → `calculate` → `calculate full` → `save workbook 1` → `close workbook 1 saving no`. Excel workbook count was **0** before and after each session. An HFS `open workbook workbook file name` probe failed with AppleScript parameter error (−50) and is **not** the accepted engine path.

Internal Answer Key recalculation (exit **0**, `calculate full=ok`, 5.55s):

| | SHA-256 |
|---|---|
| Before | `9d51808ba9afe1990448974fe368f9c3668b54db8f8a3d2fca313d49db937be1` |
| After | `29dcdfe658ce3186140a53b9ccade19d4d81dbb7ff24cf2c5dae597929fee152` |

`data_only=True` reopen of the recalculated Answer Key yielded numeric caches. Formula-bearing originals still retain all **264** geographic formulas and the sampled Americas FY2026 source `7847044`. Recalculated Answer Key also retains those **264** formulas after save.

## Task 2 — Arithmetic, presentation, Check

Independent expectations from accepted unrounded snapshot facts (`_independent_from_snapshots`) compared with Excel caches for all **264** geographic practices. Compared **264**, none-caches **0**, mismatches **0**. Maximum absolute error **8.881784197001252e-15** (family `geographic_operating_margin_contribution_change_residual`). Growth-contribution family max error **3.552713678800501e-15** (24 numeric practices). Signed identities: `D = reconstructed − reported` is **0.0** in all five periods; amount-change residual `R = −ΔD` is opening `None` then **0.0**; computed growth residual `100×g−Σc_s−b` equals `100×R/P_p` within the same floating-point residuals recorded in `.61` (not hard-coded zero).

Workbook-wide Check on internal Trainer copies after Excel recalculation:

| State | total / blank / correct / incorrect |
|---|---|
| Blank | **750 / 750 / 0 / 0** |
| Formulas from semantic map, Excel-recalculated | **750 / 0 / 750 / 0** |
| One geographic formula set to `=999`, Excel-recalculated (cache **999**) | **750 / 0 / 749 / 1** |

Check `repr` did not contain `=999` or `NOPAT`. Source tamper of `Geographic Segment Analysis!F10` raised `Trusted workbook cell was modified` (authentication rejection). A legitimate learner formula edit `=1+1` (Excel cache **2**) yielded **749/1** without that authentication error.

Presentation on inspect copies: Trainer **264** geographic practice cells blank bright yellow without answers/Notes; Answer Key **264** formulas with concise Notes and no yellow; visible structure/style contract held (Aptos Narrow 11, non-bold black, ordinary white, no decorative borders/fills). Sources remain populated.

Synthetic (labelled separately):

- Relocated chain: Americas revenue-growth contribution `=IF(H31=0,NA(),100*('Income Statement'!L28-H28)/H31)` (cross-sheet + nonadjacent `H28`; default adjacent ref absent). Excel cache **30.0** matches independent **30.0**. Filled relocated Check **153/153**.
- Zero prior consolidated profit: series and Excel caches `gpc`/`gcs`/`gpr` all `#N/A`; formula `=IF(B41=0,NA(),C84/B41)`; workbook XML contains `#N/A`.

## Task 3 — Coverage, artifacts, remaining acceptance

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py -q --tb=line` | 0 | **52 passed** in **5.96s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_geographic_segment_facts.py core/tests/test_historical_segment.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_cli_assumptions_propagate core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components -q --tb=line` | 0 | **1505 passed** in **47.06s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Complete `core/tests` **3240 passed / 0 failed** remains **historical** from `.61` and was not rerun this child.

Inspectable engine evidence: `/tmp/bav_geo_excel_verify_9M2411162/evidence.json` plus workbook copies under `pristine/`, `inspect/`, `verify/`, and `synthetic/`. No prospective IDs reserved.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Actual Excel 16.113 open/calculate/save/close on temporary ordinary pair; 264 geographic Excel caches vs independent facts, max abs error **8.881784197001252e-15**; Check 750 blank / 750 correct / 749+1 incorrect after Excel; source-authentication vs learner-formula distinction; formula retention on inspect and recalculated Answer Key; geo analysis+workbook+facts **52 passed**; focused required suite **1505 passed**; checkpoints **50/50 MATCH**; eight extractions unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Synthetic, labelled separately | Relocated cross-sheet/nonadjacent contribution cache **30.0**; zero-prior-profit Excel `#N/A` |
| Retained via required suite, not independently re-counted | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; stores `574/655/711/767/811`; geo **56/264**; preserved **486**; unavailable **101**; segment-margin formulas **15** |
| Historical, not rerun | Complete `core/tests` **3240 passed** from `.61` |
| Not claimed | Parent or Step 9 completion; G6–G9 remainder; admitted nonzero `D` or amount-change residual |

---

## Remaining scope

This child verifies geographic schedules through actual spreadsheet recalculation on a temporary ordinary source-bound pair. Broader parent acceptance remains unresolved. Other supported revenue relationships and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.61` are not reopened. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

Working-tree HEAD is `5ed036ae95e3abf4bb7844d33dbc3ee4cb23e61c`. `.git/autocycle/latest-implementation` was not rewritten.

---

# RESULT.md — Step 9M.2.4.1.1.1.63 Operating KPIs: store-count and revenue spreadsheet verification

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.63 — Operating KPIs — Store-count and revenue spreadsheet verification  
**Work:** `15b9c21afd82464d81fd33d8ae418764`  
**Plan:** `f52ea10ef3c94f59b38d31090dfb6bb8`  
**Finding:** `operating-kpi-store-revenue-spreadsheet-acceptance`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted geographic spreadsheet work `473bb39bc59a48cc973fd616064d012a` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `6493db74a45b46f16a441ee7ccd1c14f3d41849f957802bbdf77ed49b1dbb4c9` (9868).  
No commit / push / sync / checkpoint / branch change. No production-code repair, release rewrite, forecasting, or valuation.  
This child does **not** declare parent, Geographic Analysis product, Operating KPIs product, or Step 9 acceptance.

No interrupted production-tree edits were present. Temporary verification artifacts live only under `/tmp/bav_kpi_excel_verify_9M2411163/`. Edited this child: `RESULT.md` only.

## Required plan change

No required plan change.

## Task 1 — Ordinary pair and Excel engine

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used temporary copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Fixture augmentation was explicit and temporary: `scripts/prepare_lululemon_operating_kpi_filings.py` copied the four annual extracts into `/tmp/bav_kpi_excel_verify_9M2411163/prep/augmented/` and appended committed `core/tests/fixtures/operating_kpis/lululemon_company_operated_stores.json`. No observations were manufactured. Deferred management evidence was not promoted.

Supplied-filing path: validate four augmented Lululemon annual extracts → `reconcile_filings(..., admit_periods=(2022-01-30,))` → `standardize_reconciled` → JSON export/reload → ordinary `build_training_workbook`. Store sources **5**. Store practices **8**. Revenue sources **5**. Revenue/store practices **8**. Geographic sources **56**. Geographic practices **264**. Check components **766** (`486 + 264 + 8 + 8`). Unavailable displays **101**. `SEGMENT_BRIDGE_TOLERANCE = 0.0`. Expected-spec count including non-Check KPI sources **776**.

Five accepted store counts traced to selected extraction evidence:

| Period | Count | Filing year | Role | Reason | Page | Note |
|---|---:|---:|---|---|---:|---|
| 2022-01-30 | `574` | 2022 | comparative | sole_source_observation | 7 | Company-Operated Stores |
| 2023-01-29 | `655` | 2023 | comparative | later_audited_presentation | 11 | Number of company-operated stores by market |
| 2024-01-28 | `711` | 2024 | comparative | later_audited_presentation | 11 | Number of company-operated stores by market |
| 2025-02-02 | `767` | 2025 | comparative | later_audited_presentation | 11 | Number of company-operated stores by market |
| 2026-02-01 | `811` | 2025 | current_period | sole_source_observation | 11 | Number of company-operated stores by market |

Five accepted revenues traced to standardized `income_statement` `concept=revenue` after the same reconcile/standardize/export-reload path: `6256617 / 8110518 / 9619278 / 10588126 / 11102600`.

Exactly one matching pair was generated in temporary storage:

| Copy | Path | SHA-256 | Bytes |
|---|---|---|---:|
| Pristine / inspect Trainer | `/tmp/bav_kpi_excel_verify_9M2411163/{pristine,inspect}/LULU_KPI_Trainer.xlsx` | `cbd782db348faa24c74e746eb79712b134ac613592ec7572917f0fa6c9f41613` | 42665 |
| Pristine / inspect Answer Key | `/tmp/bav_kpi_excel_verify_9M2411163/{pristine,inspect}/LULU_KPI_Answer_Key.xlsx` | `c377e56e77d22c40488086c4b704a146d49811c371c1d9baa32a9a5888042652` | 192176 |

Inspect copies were never opened by Excel; inspect hashes remained unchanged after recalculation of internal copies.

Microsoft Excel **16.113** (`/Applications/Microsoft Excel.app/Contents/MacOS/Microsoft Excel`). Working command: `osascript` `tell application "Microsoft Excel"` → `open POSIX file` → `calculate` → `calculate full` → `save` named temp workbook → `close` named temp workbook `saving no`. One unrelated workbook, `build/output/Lululemon_Live_Answer_Key.xlsx` (`Lululemon_Live_Answer_Key.xlsx`), was already open. It was not saved or closed. Disk SHA-256 remained `5651119d2e6fb3a153b4fc4ff11106580592f9f16dbc03d6d843429e4e99f280` (184642) before and after every session. Temp workbooks were addressed by filename so workbook 1 was never assumed.

Internal Answer Key recalculation (exit **0**, `calculate full=ok`, 5.64s):

| | SHA-256 |
|---|---|
| Before | `c377e56e77d22c40488086c4b704a146d49811c371c1d9baa32a9a5888042652` |
| After | `1642ba2a8bac157aee4d084991bf95740124c87008a3978e022099827ea3170b` |

`data_only=True` reopen of the recalculated Answer Key yielded numeric caches. Inspect and recalculated Answer Key still retain all **16** operating-KPI formulas and populated sources `811` / `11102600`.

## Task 2 — Arithmetic, presentation, Check

Independent expectations from accepted unrounded counts `574/655/711/767/811` and revenues `6256617/8110518/9619278/10588126/11102600`. Changes `None/81/56/56/44`. Growth `(current−prior)/prior`. Difference `100×(revenue growth−store-count growth)`. Opening growth remains unavailable. Compared **16**, none-caches **0**, mismatches **0**. Maximum absolute error **0.0** in every family. The difference is an analyst-derived percentage-point gap, not store productivity or causal revenue attribution.

| Family / period | Independent | Excel cache | Abs error |
|---|---:|---:|---:|
| Store change FY2023–FY2026 | `81 / 56 / 56 / 44` | same | `0.0` |
| Store growth FY2023 | `0.14111498257839722` (`81/574`) | same | `0.0` |
| Store growth FY2024 | `0.08549618320610687` (`56/655`) | same | `0.0` |
| Store growth FY2025 | `0.07876230661040788` (`56/711`) | same | `0.0` |
| Store growth FY2026 | `0.05736636245110821` (`44/767`) | same | `0.0` |
| Revenue growth FY2023 | `0.29631045020016406` | same | `0.0` |
| Revenue growth FY2024 | `0.18602510961691965` | same | `0.0` |
| Revenue growth FY2025 | `0.10071940950245954` | same | `0.0` |
| Revenue growth FY2026 | `0.04858971266492295` | same | `0.0` |
| Difference FY2023 | `15.519546762176684` | same | `0.0` |
| Difference FY2024 | `10.052892641081277` | same | `0.0` |
| Difference FY2025 | `2.195710289205166` | same | `0.0` |
| Difference FY2026 | `-0.877664978618526` | same | `0.0` |
| Opening FY2022 change/growth/difference | `None` | not practiced | — |

Workbook-wide Check on internal Trainer copies after Excel recalculation:

| State | total / blank / correct / incorrect |
|---|---|
| Blank, Excel-recalculated | **766 / 766 / 0 / 0** |
| Formulas from semantic map, Excel-recalculated | **766 / 0 / 766 / 0** |
| One operating-KPI formula set to `=999`, Excel-recalculated (cache **999**) | **766 / 0 / 765 / 1** |

Check `repr` did not contain `=999` or `NOPAT`. Source tamper of `Store Count Analysis!F10` raised `Trusted workbook cell was modified` (authentication rejection). A legitimate learner formula edit `=1+1` (Excel cache **2**) yielded **765/1** without that authentication error.

Presentation on inspect copies: Trainer **16** store/revenue practice cells blank bright yellow without answers/Notes; Answer Key **16** formulas with concise Notes and no yellow; visible structure/style contract held (Aptos Narrow 11, non-bold black, ordinary white, no decorative borders/fills). Ten populated sources remain populated. Geographic baseline **750** is preserved inside the **766**-component Check surface.

Synthetic (labelled separately):

- Relocated chain: revenue growth `=IF('Income Statement'!C28=0,NA(),('Income Statement'!F36-'Income Statement'!C28)/'Income Statement'!C28)` (cross-sheet + nonadjacent). Excel cache **0.1** matches independent **0.1**. Store growth `=IF(B32=0,NA(),(E40-B32)/B32)` from nonadjacent `E40`/`B32`; Excel cache **0.07876230661040788**. Filled relocated Check **75/75**.
- Zero prior store count and revenue: series and Excel caches store-growth / revenue-growth / difference all `#N/A`; formulas `=IF(B10=0,NA(),(C10-B10)/B10)` and `=IF(B20=0,NA(),(C20-B20)/B20)`; workbook XML contains `#N/A`.
- Sparse/missing gates retained without Excel: gap current/prior missing snapshots remain `SOURCE_UNAVAILABLE` without compression.

## Task 3 — Coverage, artifacts, remaining acceptance

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_kpi_excel_verify_9M2411163/verify_kpi_excel.py` | 0 | Excel 16.113 open/calculate/save/close on temporary pair; 16/16 KPI caches match; Check 766 blank / 766 correct / 765+1 incorrect; live workbook undisturbed |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide -q --tb=line` | 0 | **1263 passed** in **36.90s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Complete `core/tests` **3240 passed / 0 failed** remains **historical** from `.61` and was not rerun this child. Geographic Excel **264/750** remains **historical** from `.62`.

Inspectable engine evidence: `/tmp/bav_kpi_excel_verify_9M2411163/evidence.json` plus workbook copies under `pristine/`, `inspect/`, `verify/`, and `synthetic/`. No prospective IDs reserved.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Actual Excel 16.113 open/calculate/save/close on one temporary ordinary store/revenue pair; 16 operating-KPI Excel caches vs independent accepted-source facts, max abs error **0.0**; Check 766 blank / 766 correct / 765+1 incorrect after Excel; source-authentication vs learner-formula distinction; formula retention on inspect and recalculated Answer Key; operating-KPI + affected Check/build suite **1263 passed**; checkpoints **50/50 MATCH**; eight extractions unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Synthetic, labelled separately | Relocated cross-sheet/nonadjacent revenue-growth cache **0.1** and store-growth **0.07876230661040788**; zero-prior Excel `#N/A`; filled relocated Check **75/75** |
| Retained via required suite, not independently re-counted | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; geo **56/264**; preserved **486**; unavailable **101**; segment-margin formulas **15** |
| Historical, not rerun | Complete `core/tests` **3240 passed** from `.61`; geographic Excel 264-practice verification from `.62` |
| Not claimed | Parent or Step 9 completion; other operating-KPI families; G6–G9 remainder; admitted nonzero geographic `D` or amount-change residual |

---

## Remaining scope

This child verifies source-bound store-count and revenue/store practices through actual spreadsheet recalculation on a temporary ordinary pair. Other operating-KPI families and broader parent acceptance remain unresolved.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.62` are not reopened. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

Working-tree HEAD is `7fc46f315e6ce05c57557ba18ed29b601643f738`. `.git/autocycle/latest-implementation` was not rewritten.

---

# RESULT.md — Step 9M.2.4.1.1.1.64 Operating KPIs: comparable-sales and SPSF spreadsheet verification

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.64 — Operating KPIs — Comparable-sales and SPSF spreadsheet verification  
**Work:** `8710acb0f36d43d5a04a14c1d26d8630`  
**Plan:** `d49f97d0f4724b93a0f808c1d8349392`  
**Finding:** `operating-kpi-comparable-sales-spsf-spreadsheet-verification`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted store/revenue spreadsheet work `15b9c21afd82464d81fd33d8ae418764` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `4060320b82692644d4748743b63360e9bda553c1aeec1d5287c832d56b90b00d` (9760).  
No commit / push / sync / checkpoint / branch change. No production-code repair, release rewrite, forecasting, or valuation.  
This child does **not** declare parent, Geographic Analysis product, Operating KPIs product, or Step 9 acceptance.

No interrupted production-tree edits were present. Temporary verification artifacts live only under `/tmp/bav_kpi_excel_verify_9M2411164/`. Edited this child: `RESULT.md` only.

## Required plan change

No required plan change.

## Task 1 — Evidence boundaries and one test-augmented pair

Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used temporary copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

Unaugmented mixed vs annual-only path (reproduce `test_supplied_deferred_documents_do_not_activate_schedule`): both `historical_operating_kpis` are `None`; mixed/annual standardized, statement-provenance, and conflict payloads match; extracted bytes unchanged. Management admission remains closed:

| Quantity | Measured |
|---|---|
| Reported observations | **135** (`29/36/37/33`) |
| Definitions | **9** |
| Market-table observations | **107** |
| Excluded targets | **3** |
| Comparability `comparable/not_comparable/unresolved/outside_scope` | **0/22/6/107** |
| Pairs / incompatible / singletons | **24 / 24 / 6** |
| Selections | **0** |
| Revision links | **[]** |

Missing real-source comparable-sales/SPSF evidence: unaugmented supplied management documents admit zero selections, so those schedules stay closed. Deferred observations were not promoted.

Explicit temporary test augmentation of copies of the four management extracts (`_write_selected_global_compsales` / `_write_selected_spsf`) is **synthetic**. Selected right-hand values `2/7` (compsales, FY2023/FY2024) and `1410/1430` (SPSF) with definition/week/reporting-basis and attached revision/audited-evidence relationships are test-helper inputs, not supplied filing evidence. Temporary leaf diffs vs unaugmented copies: FY2022 **23**, FY2023 **14**, FY2024 **10**, FY2025 **14**. Committed extracts unchanged.

Validate → `reconcile_filings(..., admit_periods=(2022-01-30,))` → `standardize_reconciled` → JSON export/reload → ordinary `build_training_workbook` on that synthetic pair. Store-count schedule remains inactive (`operating_kpi_applicable` is False). Geographic sources **56**. Check components **760** (`486 + 264 + 4 + 2 + 1 + 3`). Ten practices above the 750-component baseline: four revenue-growth, two revenue/comparable-sales differences, one comparable-sales change, three SPSF. Sources: two comparable-sales, two SPSF, five populated revenues.

Exactly one matching pair was generated in temporary storage. Inspect copies were never opened by Excel; inspect hashes remained unchanged after recalculation of internal copies.

| Copy | Path | SHA-256 | Bytes |
|---|---|---|---:|
| Pristine / inspect Trainer | `/tmp/bav_kpi_excel_verify_9M2411164/{pristine,inspect}/COMP_SELECTED_Trainer.xlsx` | `33d26746ea4d44bb72f89c7ac633c604adba14d922ee26abc80818999b39b34c` | 45422 |
| Pristine / inspect Answer Key | `/tmp/bav_kpi_excel_verify_9M2411164/{pristine,inspect}/COMP_SELECTED_Answer_Key.xlsx` | `a3d12e7c8d1753c02b2dab47b04c04c6e18b4d64fa8ae223e9ab7619721c101e` | 196820 |

Microsoft Excel **16.113** (`/Applications/Microsoft Excel.app/Contents/MacOS/Microsoft Excel`). Working command: `osascript` `tell application "Microsoft Excel"` → `open POSIX file` → `calculate` → `calculate full` → `save` named temp workbook → `close` named temp workbook `saving no`. No Excel workbooks were open at start or end. Disk SHA-256 of `build/output/Lululemon_Live_Answer_Key.xlsx` remained `58ac9054d87ff8f71f70e6cda8be759fef6a6a4373d28edf5aa964f56263b89a` (214508) before and after every session. Temp workbooks were addressed by filename.

Internal Answer Key recalculation (exit **0**, `calculate full=ok`, 5.56s):

| | SHA-256 |
|---|---|
| Before | `a3d12e7c8d1753c02b2dab47b04c04c6e18b4d64fa8ae223e9ab7619721c101e` |
| After | `9d061e91867e49d9eaa763547629996bacc74e3dcca7bce8854b84ffdd7ebc71` |

`data_only=True` reopen of the recalculated Answer Key yielded numeric caches. Inspect and recalculated Answer Key still retain all **10** new-family formulas and populated sources `7` / `1430`. Management-history nondisclosure held after Trainer reserialize.

## Task 2 — Arithmetic, presentation, Check

Independent expectations from augmented input records `compsales 2/7`, `SPSF 1410/1430`, and accepted unrounded revenues `6256617 / 8110518 / 9619278 / 10588126 / 11102600`. Not from model `expected_value` or workbook formulas. Opening FY2022 growth remains unavailable. Percent-versus-fraction scaling: comparable-sales inputs are percent (`2` means 2%); revenue and SPSF growth are fractions. Compared **10**, none-caches **0**, mismatches **0**. Maximum absolute error **0.0** in every family. Differences are analyst-derived percentage-point gaps, not store productivity or causal attribution.

| Family / period | Independent | Excel cache | Abs error |
|---|---:|---:|---:|
| Revenue growth FY2023 | `0.29631045020016406` | same | `0.0` |
| Revenue growth FY2024 | `0.18602510961691965` | same | `0.0` |
| Revenue growth FY2025 | `0.10071940950245954` | same | `0.0` |
| Revenue growth FY2026 | `0.04858971266492295` | same | `0.0` |
| Compsales inputs FY2023/FY2024 | `2 / 7` | populated sources | — |
| Compsales change FY2024 | `5` (`7−2`) | same | `0.0` |
| Difference FY2023 `100×g−2` | `27.631045020016405` | same | `0.0` |
| Difference FY2024 `100×g−7` | `11.602510961691966` | same | `0.0` |
| SPSF inputs FY2023/FY2024 | `1410 / 1430` | populated sources | — |
| SPSF change FY2024 | `20` | same | `0.0` |
| SPSF growth FY2024 | `0.014184397163120567` (`20/1410`) | same | `0.0` |
| SPSF difference FY2024 `100×(g−spsf growth)` | `17.184071245379908` | same | `0.0` |
| Opening FY2022 growth/difference | `None` | not practiced | — |

Workbook-wide Check on internal Trainer copies after Excel recalculation:

| State | total / blank / correct / incorrect |
|---|---|
| Blank, Excel-recalculated | **760 / 760 / 0 / 0** |
| Formulas from semantic map, Excel-recalculated | **760 / 0 / 760 / 0** |
| One new-family SPSF-growth formula set to `=999`, Excel-recalculated (cache **999**) | **760 / 0 / 759 / 1** |

Check `repr` did not contain `=999`, `NOPAT`, or `=100*`. Source tamper of `Comparable Sales Analysis!D28` raised `Trusted workbook cell was modified` (authentication rejection). A legitimate learner formula edit `=1+1` (Excel cache **2**) yielded **759/1** without that authentication error.

Presentation on inspect copies: Trainer **10** new-family practice cells blank bright yellow without answers/Notes; Answer Key **10** formulas with concise Notes and no yellow; visible structure/style contract held (Aptos Narrow 11, non-bold black, ordinary white, no decorative borders/fills). Nine populated sources remain populated. Scope notes retain distinct population/definition/calendar comparability and noncausal wording. Geographic baseline **750** is preserved inside the **760**-component Check surface. This pair's unavailable displays measured **199**; retained ordinary store-fixture **101** is not this pair's count.

Synthetic (labelled separately):

- Relocated chain: compsales change `='Income Statement'!G52-'Income Statement'!D44`; SPSF change `='Income Statement'!G54-'Income Statement'!D46`; SPSF growth `=IF('Income Statement'!D46=0,NA(),('Income Statement'!G54-'Income Statement'!D46)/'Income Statement'!D46)` (cross-sheet + nonadjacent; default adjacent ref absent). Excel caches **5 / 20 / 0.014184397163120567** match independent **5 / 20 / 20/1410**. Filled relocated Check **77/77**.
- Zero prior SPSF and revenue: series and Excel caches SPSF-growth / revenue-growth `#N/A`; formulas `=IF(B28=0,NA(),(C28-B28)/B28)` and `=IF(B9=0,NA(),(C9-B9)/B9)`; workbook XML contains `#N/A`.
- Sparse/incompatible gates retained without Excel: missing adjacent compsales remains `SOURCE_UNAVAILABLE` without compression; definition mismatch blocks adjacent change.

## Task 3 — Coverage, artifacts, remaining acceptance

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_kpi_excel_verify_9M2411164/verify_compsales_excel.py` | 0 through Excel Check; sparse-gate assertion later corrected | Excel 16.113 open/calculate/save/close on temporary pair; 10/10 new-family caches match; Check 760 blank / 760 correct / 759+1 incorrect; live workbook undisturbed |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_kpi_excel_verify_9M2411164/finish_remaining.py` | 0 | Relocated caches reused from existing Excel artifacts; sparse/incompatible gates; protected/extract hashes; required tests |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide -q --tb=line` | 0 | **1419 passed** in **40.21s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Complete `core/tests` **3240 passed / 0 failed** remains **historical** from `.61` and was not rerun this child. Geographic Excel **264/750** remains **historical** from `.62`. Store/revenue Excel **16/766** remains **historical** from `.63`.

Inspectable engine evidence: `/tmp/bav_kpi_excel_verify_9M2411164/evidence.json` plus workbook copies under `pristine/`, `inspect/`, `verify/`, and `synthetic/`. No prospective IDs reserved. Real-source comparable-sales/SPSF acceptance remains unresolved.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Actual Excel 16.113 open/calculate/save/close on one temporary explicitly test-augmented compsales/SPSF pair; 10 new-family Excel caches vs independent augmented inputs and unrounded revenues, max abs error **0.0**; Check 760 blank / 760 correct / 759+1 incorrect after Excel; source-authentication vs learner-formula distinction; formula retention on inspect and recalculated Answer Key; unaugmented admission **0** selections; operating-KPI + management admission/history + affected Check/build suite **1419 passed**; checkpoints **50/50 MATCH**; eight extractions unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Synthetic, labelled separately | Test-augmented selected compsales `2/7` and SPSF `1410/1430` with helper revision/evidence attachments; relocated cross-sheet/nonadjacent caches **5 / 20 / 20/1410**; zero-prior Excel `#N/A`; filled relocated Check **77/77** |
| Retained via required suite, not independently re-counted | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; stores `574/655/711/767/811`; geo **56/264**; preserved **486**; ordinary-fixture unavailable **101**; segment-margin formulas **15** |
| Historical, not rerun | Complete `core/tests` **3240 passed** from `.61`; geographic Excel 264-practice verification from `.62`; store/revenue Excel 16-practice verification from `.63` |
| Not claimed | Parent or Step 9 completion; real-source compsales/SPSF acceptance; G6–G9 remainder; admitted nonzero geographic `D` or amount-change residual |

---

## Remaining scope

This child verifies comparable-sales and SPSF spreadsheet behavior on one explicitly test-augmented temporary pair. Unaugmented source admission remains closed. Broader parent acceptance remains unresolved.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.63` are not reopened. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

Working-tree HEAD is `122c025fb3d49d65471803eb66e39ec922f3013b`. `.git/autocycle/latest-implementation` was not rewritten.

---

# RESULT.md — Step 9M.2.4.1.1.1.64 Operating KPIs: current-generation comparable-sales and SPSF verification

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.64 — Operating KPIs — Current-generation comparable-sales and SPSF verification  
**Work:** `8710acb0f36d43d5a04a14c1d26d8630`  
**Plan:** `f3ecd047a8834b4e96bba84c004a9d5c`  
**Finding:** `operating-kpi-comparable-sales-spsf-spreadsheet-verification`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted store/revenue spreadsheet work `15b9c21afd82464d81fd33d8ae418764` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `b73c5fc6cac05789b0a2be2765c09bb83cde376019e08a60f74a37467f7227b4` (11559).  
No commit / push / sync / checkpoint / branch change. No production-code repair, release rewrite, forecasting, or valuation.  
This child does **not** declare parent, Geographic Analysis product, Operating KPIs product, or Step 9 acceptance.

Prior RESULT under plan `d49f97d0f4724b93a0f808c1d8349392` claimed COMPLETE at HEAD `122c025`. That **current-generation completion claim is superseded**. Retained `/tmp/bav_kpi_excel_verify_9M2411164/` arithmetic and synthetic dependency evidence remains authentic baseline evidence only.

No interrupted production-tree edits were present. Fresh current-generation artifacts live only under `/tmp/bav_kpi_excel_verify_9M2411164_cg/` and redirected company output `/tmp/bav_cg_company_ze2d_snv/`. Edited this child: `RESULT.md` only. Generating SHA `7329dafa1f82f424242db49348a0217eaa54cb51`. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

## Required plan change

No required plan change.

## Task 1 — Reconcile retained evidence, fd0f311…HEAD, and one fresh pair

Retained `.64` pristine/inspect hashes still match the superseded RESULT table:

| Copy | SHA-256 | Bytes |
|---|---|---:|
| Retained Trainer | `33d26746ea4d44bb72f89c7ac633c604adba14d922ee26abc80818999b39b34c` | 45422 |
| Retained Answer Key | `a3d12e7c8d1753c02b2dab47b04c04c6e18b4d64fa8ae223e9ab7619721c101e` | 196820 |

Retained Check **760/760/0/0**, **760/0/760/0**, **760/0/759/1**; cache max abs error **0.0**; unaugmented selections **0**. Relocated formulas `='Income Statement'!G52-'Income Statement'!D44` / `G54-D46` / `IF(D46=0,NA(),(G54-D46)/D46)` and zero-prior `=IF(B28=0,NA(),(C28-B28)/B28)` / `=IF(B9=0,NA(),(C9-B9)/B9)` were re-authenticated against current generation (byte-identical formulas; Excel rerun on fresh workbooks).

`fd0f311..HEAD` scoped to the listed build files: commits `71e78a5` then `7329daf`. Names: `core/trainer/workbook.py` (Build Status + `current_snapshot`), `core/build_status.py` (new), `core/current_build.py` (new), `core/engine/build_contract.py` (`current_ready` / snapshot selection), `core/engine/reference_model.py` (forwards snapshot), `core/__main__.py` (company CLI), `core/project_companies.json`, `core/ingestion/note_handoff.py`, `core/tests/test_current_build.py`, `core/tests/test_learner_ready_presentation.py`, `docs/build-contract.md`, `README.md`. These affect presentation (Build Status) and the company current-snapshot path; they do not authorize additional implementation. Prior pair hashes differ because ordinary finalization now inserts Build Status.

Unaugmented mixed vs annual-only (temporary copies): both `historical_operating_kpis` are `None`; standardized / statement-provenance / conflict parity held; extracted bytes unchanged. Management admission remains closed: observations **135** (`29/36/37/33`), definitions **9**, market-table **107**, excluded targets **3**, comparability `0/22/6/107`, pairs/incompatible/singletons `24/24/6`, selections **0**, revision links `[]`. Missing real-source comparable-sales/SPSF evidence is unchanged; deferred observations were not promoted.

Explicit temporary test augmentation (`_write_selected_global_compsales` / `_write_selected_spsf`) is **synthetic**. Selected rights `2/7` and `1410/1430`. Temporary leaf diffs vs unaugmented copies: FY2022 **23**, FY2023 **14**, FY2024 **10**, FY2025 **14**. Committed extracts unchanged.

Validate → `reconcile_filings(..., admit_periods=(2022-01-30,))` → `standardize_reconciled` → JSON export/reload → ordinary `build_training_workbook` (no `current_snapshot`) on that synthetic pair. Store-count schedule inactive (`operating_kpi_applicable` is False). Geographic sources **56**. Check components **760**. Ten practices: four revenue-growth, two revenue/comparable-sales differences, one comparable-sales change, three SPSF. Sources: two comparable-sales, two SPSF, five populated revenues.

| Copy | Path | SHA-256 | Bytes |
|---|---|---|---:|
| Fresh pristine / inspect Trainer | `/tmp/bav_kpi_excel_verify_9M2411164_cg/{pristine,inspect}/COMP_SELECTED_Trainer.xlsx` | `cf69ebd5dc8d0aa26612bd47f7d7d5a88f25e11e35a22f2e7ae328e2fde57a75` | 47375 |
| Fresh pristine / inspect Answer Key | `/tmp/bav_kpi_excel_verify_9M2411164_cg/{pristine,inspect}/COMP_SELECTED_Answer_Key.xlsx` | `75172a59b44de061114b753866e4e2666da79ee9a0b5d73c08be583527865192` | 198784 |

Inspect copies were never opened by Excel; inspect hashes unchanged after recalculation of internal copies.

## Task 2 — Current-generation Excel and learner acceptance

Microsoft Excel **16.113** (`/Applications/Microsoft Excel.app/Contents/MacOS/Microsoft Excel`). Working command: `osascript` `tell application "Microsoft Excel"` → `open POSIX file` → `calculate` → `calculate full` → `save` named temp workbook → `close` named temp workbook `saving no`. An already-open unrelated workbook named `Lululemon_Answer_Key.xlsx` remained open; it was not targeted. Release sentinel `/Users/lizhiguo/Documents/Developer/bav_trainer/release/lululemon/Lululemon_Answer_Key.xlsx` SHA-256 `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` (119554) was unchanged before and after every session. All eight temp recalculations exit **0**, `calculate full=ok`, hash_changed **True**, unrelated-workbook set unchanged.

Internal Answer Key recalculation (6.04s):

| | SHA-256 |
|---|---|
| Before | `75172a59b44de061114b753866e4e2666da79ee9a0b5d73c08be583527865192` |
| After | `b637cead3a6f11705d2fe516c75d471424da56f5732a4349b33e7e20a4e31fd4` |

`data_only=True` reopen yielded numeric caches. Inspect and recalculated Answer Key retain all **10** new-family formulas and populated sources `7` / `1430`. Management-history nondisclosure held after Trainer reserialize.

Independent expectations from augmented records `compsales 2/7`, `SPSF 1410/1430`, and accepted unrounded revenues `6256617 / 8110518 / 9619278 / 10588126 / 11102600`. Not from model `expected_value`. Opening FY2022 growth remains unavailable. Percent-versus-fraction scaling: comparable-sales inputs are percent (`2` means 2%); revenue and SPSF growth are fractions. Compared **10**, none-caches **0**, mismatches **0**. Maximum absolute error **0.0** in every family. Tolerances: adjacent changes exact `0.0`; SPSF growth `max(component, OPERATING_KPI_RATIO_TOLERANCE)`; remaining relationship families `max(component, OPERATING_KPI_RELATIONSHIP_TOLERANCE)`.

| Family / period | Independent | Excel cache | Abs error |
|---|---:|---:|---:|
| Revenue growth FY2023 | `0.29631045020016406` | same | `0.0` |
| Revenue growth FY2024 | `0.18602510961691965` | same | `0.0` |
| Revenue growth FY2025 | `0.10071940950245954` | same | `0.0` |
| Revenue growth FY2026 | `0.04858971266492295` | same | `0.0` |
| Compsales inputs FY2023/FY2024 | `2 / 7` | populated sources | — |
| Compsales change FY2024 | `5` (`7−2`) | same | `0.0` |
| Difference FY2023 `100×g−2` | `27.631045020016405` | same | `0.0` |
| Difference FY2024 `100×g−7` | `11.602510961691966` | same | `0.0` |
| SPSF inputs FY2023/FY2024 | `1410 / 1430` | populated sources | — |
| SPSF change FY2024 | `20` | same | `0.0` |
| SPSF growth FY2024 | `0.014184397163120567` (`20/1410`) | same | `0.0` |
| SPSF difference FY2024 `100×(g−spsf growth)` | `17.184071245379908` | same | `0.0` |
| Opening FY2022 growth/difference | `None` | not practiced | — |

Workbook-wide Check on internal Trainer copies after Excel recalculation:

| State | total / blank / correct / incorrect |
|---|---|
| Blank, Excel-recalculated | **760 / 760 / 0 / 0** |
| Formulas from semantic map, Excel-recalculated | **760 / 0 / 760 / 0** |
| One new-family SPSF-growth formula set to `=999`, Excel-recalculated (cache **999**) | **760 / 0 / 759 / 1** |

Check `repr` did not contain `=999`, `NOPAT`, or `=100*`. Source tamper of `Comparable Sales Analysis!D28` raised `Trusted workbook cell was modified` (authentication rejection). A legitimate learner formula edit `=1+1` (Excel cache **2**) yielded **759/1** without that authentication error.

Presentation on inspect copies: every visible sheet checked. Trainer **10** new-family practice cells blank bright yellow without answers/Notes; matching Answer-Key formulas with concise Notes and no yellow anywhere; Aptos Narrow 11, non-bold black, ordinary white, no decorative borders/fills. Nine populated sources remain populated. Scope notes retain population/definition/calendar comparability and noncausal wording. Geographic baseline **750** is preserved inside the **760**-component Check surface. This pair's unavailable displays measured **199**; retained ordinary store-fixture **101** is not this pair's count.

Build Status is sheet index **1** on both workbooks, adds **0** practice components, and is absent from the semantic map tabs. Trainer `Trainer!G1` = `Current Progress` → `#'Build Status'!A1`. Header states availability does not establish parent or release acceptance. On this **test-augmented** pair: Comparable Sales Analysis **Active / available** (2 mapped cells), Sales per Square Foot Analysis **Active / available** (2), Store-count history **Source unavailable / not admitted** (0), Revenue per store ratio **Implementation / family not active** (0). No revenue-per-store productivity claim and no real-source comparable-sales/SPSF acceptance claim.

Synthetic, labelled separately; formulas equivalent to retained baseline; Excel rerun on current-generation workbooks:

- Relocated chain: compsales change `='Income Statement'!G52-'Income Statement'!D44`; SPSF change `='Income Statement'!G54-'Income Statement'!D46`; SPSF growth `=IF('Income Statement'!D46=0,NA(),('Income Statement'!G54-'Income Statement'!D46)/'Income Statement'!D46`. Excel caches **5 / 20 / 0.014184397163120567**. Filled relocated Check **77/77**.
- Zero prior SPSF and revenue: series and Excel caches SPSF-growth / revenue-growth `#N/A`; formulas `=IF(B28=0,NA(),(C28-B28)/B28)` and `=IF(B9=0,NA(),(C9-B9)/B9`; workbook XML contains `#N/A`.
- Sparse/incompatible gates retained without Excel: missing adjacent compsales remains `SOURCE_UNAVAILABLE` without compression; definition mismatch blocks adjacent change.

## Task 3 — Current-generation build contracts

Company path exercised with `current_build.OUTPUT_ROOT` redirected to `/tmp/bav_cg_company_ze2d_snv`. Canonical `build/output/` was not a destination.

Isolated Lululemon `python -m core build Lululemon` exit **0** (0.74s). Admit period `2022-01-30`. Vetted store-fact note handoff wrote `supporting/extracted/` and `supporting/supplemental_facts.json`. Artifacts: matching Trainer/Answer Key, sidecars `component_map` / `assumptions` / `rowmap` / `build_status.json`, `supporting/{standardized,provenance,conflicts,management_kpi_admission}.json`. Embedded vs sidecar semantic parity **True**. Blank Check **766 / 766 / 0 / 0**. Admission selected_count **0**, revision links `[]`. Families include store-count and geographic growth contribution; no `comparable_sales` or `square_foot` families. Build Status: Comparable Sales / SPSF **Source unavailable / not admitted** (0 cells); Store-count history **Active / available** (5); Revenue per store ratio **inactive**. Trainer SHA-256 `e10d7cda7b89e6b59c4dfbc6d1f2f341c8931634660ecc546155744408eb32ba`; Answer Key `1c4f27fe99f51fed34e01af194ff3eae6eae2422221a8e5b5e11c0b80a9b6d09`. Answer Key has no yellow. Forecast trap was not called.

Default `complete_build_modules` and `current_snapshot=True` both selected the same 26 integrated historical modules including `operating_kpi` and excluding deferred `forecast` (110 families on committed unaugmented standardized.json, which has no compsales/SPSF and no store-count package). `current_snapshot=True` did not execute forecasting.

Staged-verification, source-validation, and directory-exchange failures each exit **1** with the previous generation byte-identical. Replacement republish exit **0** and left only `Lululemon/` under the temp root. Matching legacy `Lululemon_Live_Trainer.xlsx` removed after success; unrelated `Other_Trainer.xlsx` preserved. Symlink current-directory guard exit **1** (`Current build directory must not be a symlink`). Explicit JSON `-o` into `benchmark/` exit **1** (`protected build destination`).

Isolated Fast Retailing current-snapshot build exit **0** into the same temp root (not repo publication). Parent temporary-build acceptance is **success**.

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_kpi_excel_verify_9M2411164_cg/verify_compsales_excel.py` | 0 | Excel 16.113 on one temporary explicitly test-augmented pair; 10/10 caches match independent expectations, max abs error **0.0**; Check 760 blank / 760 correct / 759+1 incorrect; Build Status present; unaugmented admission **0** selections |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_kpi_excel_verify_9M2411164_cg/verify_current_contracts.py` | 0 | Retained hashes authenticated; fd0f311…HEAD recorded; redirected company path; failure/symlink/legacy guards; Fast Retailing temp success |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_current_build.py core/tests/test_operating_kpi_workbook.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_operating_kpi_management_history.py core/tests/test_management_kpi_analysis.py core/tests/test_management_kpi_history.py core/tests/test_management_kpi_admission.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers core/tests/test_reference_integrity.py::test_historical_expected_covers_catalog_and_matches_reference_components core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide -q --tb=line` | 0 | **1432 passed** in **50.86s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | eight files **UNCHANGED** |

Complete `core/tests` **3240 passed / 0 failed** remains **historical** from `.61` and was not rerun this child. Geographic Excel **264/750** remains **historical** from `.62`. Store/revenue Excel **16/766** remains **historical** from `.63`.

Inspectable engine evidence: `/tmp/bav_kpi_excel_verify_9M2411164_cg/evidence.json`, `/tmp/bav_kpi_excel_verify_9M2411164_cg/contracts_evidence.json`, retained `/tmp/bav_kpi_excel_verify_9M2411164/evidence.json`. No prospective IDs reserved. Real-source comparable-sales/SPSF acceptance remains unresolved.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Current-generation ordinary pair plus Excel 16.113 on one temporary explicitly test-augmented compsales/SPSF pair; Build Status; 10 new-family Excel caches vs independent augmented inputs and unrounded revenues, max abs error **0.0**; Check 760 blank / 760 correct / 759+1 incorrect after Excel; redirected Lululemon current-snapshot company path Check **766/766/0/0** with unaugmented management selections **0**; Fast Retailing temporary-build success; failure/symlink/legacy guards; operating-KPI + management + current-build + Check/build suite **1432 passed**; checkpoints **50/50 MATCH**; eight extractions unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Synthetic, labelled separately | Test-augmented selected compsales `2/7` and SPSF `1410/1430`; relocated cross-sheet/nonadjacent caches **5 / 20 / 20/1410**; zero-prior Excel `#N/A`; filled relocated Check **77/77** |
| Retained baseline, re-authenticated | Prior `.64` pair hashes and Check 760-state arithmetic; relocated/zero-prior formulas equivalent under current generation |
| Retained via required suite, not independently re-counted | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; stores `574/655/711/767/811`; geo **56/264**; preserved **486**; ordinary-fixture unavailable **101**; segment-margin formulas **15** |
| Historical, not rerun | Complete `core/tests` **3240 passed** from `.61`; geographic Excel 264-practice verification from `.62`; store/revenue Excel 16-practice verification from `.63` |
| Not claimed | Parent or Step 9 completion; real-source compsales/SPSF acceptance; G6–G9 remainder; admitted nonzero geographic `D` or amount-change residual |

---

## Remaining scope

This child verifies current-generation comparable-sales and SPSF spreadsheet behavior on one explicitly test-augmented temporary pair, plus redirected company-path contracts. Unaugmented source admission remains closed. Broader parent acceptance remains unresolved.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.63` are not reopened. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

Working-tree HEAD is `7329dafa1f82f424242db49348a0217eaa54cb51`. `.git/autocycle/latest-implementation` was not rewritten.

---

# RESULT.md — Step 9M.2.4.1.1.1.65 Normalization Judgment and Earnings Normalization: Excel treatment verification

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.65 — Normalization Judgment and Earnings Normalization — Excel treatment verification  
**Work:** `e2b825657b944d36beafca6c36cf91ff`  
**Plan:** `ec73aa03a1a64313aa7ac918768c7c72`  
**Finding:** `normalization-treatment-conditioned-spreadsheet-verification`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted comparable-sales/SPSF spreadsheet work `8710acb0f36d43d5a04a14c1d26d8630` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `2136e7d9342a377afe579ae12863e675f127b301adc21ccc3714a3c1d8dd26eb` (9594).  
No commit / push / sync / checkpoint / branch change. No production-code repair, release rewrite, forecasting, or valuation.  
This child does **not** declare parent, Geographic Analysis product, Operating KPIs product, Normalization product, or Step 9 acceptance.

No interrupted production-tree edits were present. Fresh artifacts live only under `/tmp/bav_norm_excel_verify_9M2411165/`. Edited this child: `RESULT.md` only. Generating SHA `95753da3e5e59d4800c71a96846b754449496bd4`. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.

## Required plan change

No required plan change.

## Task 1 — Generate and authenticate the illustrative normalization pair

Ordinary `_build_norm_pair` on `example/DEMO_HK_Standardized.json` + `example/DEMO_HK_Assumptions.json` (0.17s). DEMO facts and the restructuring judgment are **illustrative**. Explicit candidate `concept:restructuring_expense`; scope `operating_pretax_effective_tax`; reference `Non-recurring`; signed source values `0 / 0 / -200 / 0 / 0`. Reference rationale distinguishes the supplied illustrative event from analyst treatment. 332-component / 78-family contract held (20 normalization practices; no extra mapped dependents on this pair — no share history).

| Copy | Path | SHA-256 | Bytes |
|---|---|---|---:|
| Fresh pristine / inspect Trainer | `/tmp/bav_norm_excel_verify_9M2411165/{pristine,inspect}/DEMO_HK_Trainer.xlsx` | `c1dc88093ed5dd1051dc1be1cb0c62ea4770fad189fb461effb0dee72e8c3db4` | 28496 |
| Fresh pristine / inspect Answer Key | `/tmp/bav_norm_excel_verify_9M2411165/{pristine,inspect}/DEMO_HK_Answer_Key.xlsx` | `debe244e05fb40192559f6d631a12825df915cb21954d5ff133a195d77eb468e` | 85799 |

Inspect copies were never opened by Excel; inspect hashes unchanged after every recalculation of internal copies.

Independent oracle from signed candidate values and reported IS inputs (not model `expected_value`). Pretax add-back = `−signed`; ETR = `−tax / pretax`; after-tax = pretax × `(1 − ETR)` when pretax ≠ 0, else 0; NOPAT = NI + net interest × `(1 − ETR)` with net interest = `−(finance costs + finance income)`; normalized NOPAT/NI = reported + after-tax. FY2023 Non-recurring pretax add-back **200**; Recurring adjustment **0**. Tax convention is the illustrative reported effective-tax assumption, not evidence of actual deductibility.

| Period | Signed | ETR | NR pretax | NR after-tax | NR NOPAT | NR NI | Recurring pretax / after / NOPAT / NI |
|---|---:|---:|---:|---:|---:|---:|---|
| FY2021 | `0` | `565/3325` | `0` | `0` | `2822.2556390977443` | `2760` | same unadjusted |
| FY2022 | `0` | `612/3600` | `0` | `0` | `3054.4` | `2988` | same unadjusted |
| FY2023 | `-200` | `672/3955` | `200` | `166.01769911504425` | `3519.575221238938` | `3449.0176991150443` | `0 / 0 / 3353.5575221238937 / 3283` |
| FY2024 | `0` | `746/4390` | `0` | `0` | `3718.7061503416858` | `3644` | same unadjusted |
| FY2025 | `0` | `833/4905` | `0` | `0` | `4150.866462793068` | `4072` | same unadjusted |

Declared cache tolerances: each component's catalog `tolerance` (default `0.01`); measured max abs error **0.0**.

## Task 2 — Excel treatment changes and learner behavior

Microsoft Excel **16.113** (`/Applications/Microsoft Excel.app/Contents/MacOS/Microsoft Excel`). Working command: `osascript` `tell application "Microsoft Excel"` → `open POSIX file` → `calculate` → `calculate full` → `save` named temp workbook → `close` named temp workbook `saving no`. An already-open unrelated workbook named `Lululemon_Answer_Key.xlsx` remained open; it was not targeted. Release sentinel `/Users/lizhiguo/Documents/Developer/bav_trainer/release/lululemon/Lululemon_Answer_Key.xlsx` SHA-256 `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` (119554) was unchanged before and after every session. All **10** temp recalculations exit **0**, `calculate full=ok`, hash_changed **True**, unrelated-workbook set unchanged.

Internal Answer Key recalculation (6.65s):

| | SHA-256 |
|---|---|
| Before | `debe244e05fb40192559f6d631a12825df915cb21954d5ff133a195d77eb468e` |
| After | `d84ee3557dfb4439462298f4339e16ba0b54120e750ae91836b58060f993283a` |

`data_only=True` reopen: **20/20** mapped normalization caches match independent Non-recurring expectations, max abs error **0.0**. Blank-F and explicit `Non-recurring` Trainer variants reproduce the same 20 caches after Excel. `Recurring` removes the FY2023 adjustment (Excel pretax cache **0**) and restores unadjusted NOPAT `3353.5575221238937` / NI `3283`.

Workbook-wide Check after Excel recalculation:

| State | total / blank / correct / incorrect |
|---|---|
| Blank, Excel-recalculated | **332 / 332 / 0 / 0** |
| Formulas filled, F blank (reference), Excel-recalculated | **332 / 0 / 332 / 0** |
| Explicit `Non-recurring`, Excel-recalculated | **332 / 0 / 332 / 0** |
| `Recurring`, Excel-recalculated | **332 / 0 / 332 / 0** |
| Recurring + FY2023 pretax `=200` (former Non-recurring answer) at `Earnings Normalization!E9`, Excel cache **200** | **332 / 0 / 331 / 1** |

CLI Check on the stale workbook: `Checked 332 practice cells: 331 correct, 1 incorrect, 0 blank.` Exit **1** (incorrect > 0). Output contained no formulas, Notes, or rationale/consequence text. Legitimate learner formula `=1+1` (Excel cache **2**) yielded **331/1** without authentication error. Invalid treatment `Not A Treatment` raised `Invalid treatment`. Income Statement source tamper raised `Trusted workbook cell was modified: Income Statement!B7`. Trusted Earnings Normalization ETR formula tamper raised `Trusted workbook cell was modified: Earnings Normalization!C10`.

Presentation on inspect copies: every visible sheet checked. Trainer **332** practice cells blank bright yellow without Notes; guided response cells F5/G5/H5 on Accounting Judgment and Normalization Judgment blank yellow without Notes; matching Answer-Key formulas with concise Notes and no yellow anywhere; Aptos Narrow 11, non-bold black, ordinary white, no decorative borders/fills. Candidate label `Restructuring expense`; supplied reference `Non-recurring`; scope `operating_pretax_effective_tax`. Notes use the ETR convention and contain no deductibility claim.

Build Status is sheet index **1**, adds **0** practice components, absent from the semantic map tabs. Trainer `Trainer!G1` = `Current Progress` → `#'Build Status'!A1`. Header: availability does not establish parent or release acceptance. No real-source or parent-acceptance claim.

Synthetic undefined-ETR fixture reproduced under `/tmp/bav_norm_excel_verify_9M2411165/etr/` (PBT=0, tax=0, FY2025 signed candidate `-100`). Excel after-tax and normalized NI caches **`#N/A`**, not zero; pretax caches `0` / `100`; formula contains `ISNA(`. Filled Check **79/0/79/0**. Replacing the undefined after-tax practice with `=0` (Excel cache **0**) yielded **79/0/78/1**. Absent candidates omit both normalization sheets and keep **312** components. Label-only automatic normalization did not fire. Ambiguous `label:Special charge` and missing candidate history fail closed.

## Task 3 — Reproducible acceptance evidence

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_norm_excel_verify_9M2411165/verify_normalization_excel.py` | 0 | Excel 16.113 on temporary illustrative DEMO pair; 20/20 normalization caches match independent expectations, max abs error **0.0**; Check 332 blank / 332 correct / 331+1 incorrect; undefined-ETR Excel `#N/A`; protected **50/50**; extracts **8/8** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_normalization.py core/tests/test_normalized_per_share.py core/tests/test_reference_integrity.py core/tests/test_learner_ready_presentation.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_trainer.py::test_check_scans_all_practice_cells_and_colors_three_states core/tests/test_trainer.py::test_cli_check_output_does_not_disclose_answers -q --tb=line` | 0 | **172 passed** in **30.28s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | eight files **UNCHANGED** |

Complete `core/tests` **3240 passed / 0 failed** remains **historical** from `.61` and was not rerun this child. Geographic Excel **264/750** remains **historical** from `.62`. Store/revenue Excel **16/766** remains **historical** from `.63`. Compsales/SPSF Excel **760** remains **historical** from `.64`.

Inspectable engine evidence: `/tmp/bav_norm_excel_verify_9M2411165/evidence.json` plus workbook copies under `pristine/`, `inspect/`, `verify/`, and `etr/`. No prospective IDs reserved. Real-company normalization acceptance remains unresolved.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Current-generation illustrative DEMO pair plus Excel 16.113 treatment-conditioned recalculation; independent signed-source bridge including FY2023 NR pretax **200** / Recurring **0**; 20/20 Excel caches vs independent expectations, max abs error **0.0**; Check 332 blank / 332 correct / 331+1 incorrect after Excel; undefined-ETR Excel `#N/A` not zero; invalid/tamper fail-closed; absent-candidate omission **312**; required normalization + per-share + reference-integrity + presentation + Check/build suite **172 passed**; checkpoints **50/50 MATCH**; eight extractions unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Synthetic / illustrative, labelled separately | DEMO restructuring candidate; undefined-ETR two-period fixture; ambiguous-selector and missing-history fail-closed probes |
| Retained via required suite, not independently re-counted | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; stores `574/655/711/767/811`; geo **56/264**; preserved **486**; ordinary-fixture unavailable **101**; segment-margin formulas **15** |
| Historical, not rerun | Complete `core/tests` **3240 passed** from `.61`; geographic Excel from `.62`; store/revenue Excel from `.63`; compsales/SPSF Excel from `.64` |
| Not claimed | Parent or Step 9 completion; real-company normalization acceptance; G6–G9 remainder; admitted nonzero geographic `D` or amount-change residual |

---

## Remaining scope

This child verifies treatment-conditioned earnings normalization in Excel on one illustrative DEMO pair, plus a synthetic undefined-ETR fixture. Real-company normalization evidence and unresolved parent acceptance remain open.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.64` are not reopened. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment. No prospective IDs reserved.

Working-tree HEAD is `95753da3e5e59d4800c71a96846b754449496bd4`. `.git/autocycle/latest-implementation` was not rewritten.

---

# RESULT.md — Step 9M.2.4.1.1.1.66 Real-company normalization: source-to-selector qualification

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.66 — Real-company normalization: source-to-selector qualification  
**Work:** `9a9bf001dea84a868ef326d8ef5126ea`  
**Plan:** `512736ff019643588afc95abb61cab90`  
**Finding:** `real-company-normalization-source-to-selector-gap`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted illustrative normalization Excel work `e2b825657b944d36beafca6c36cf91ff` remains complete and is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed. Instruction `20260918-115651-000000007` remains retained. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `b4eee40d6cdae0715b988038238347b8faa4aa60685dbdf597f86d17fd3f0d3b` (8800).  
No commit / push / sync / checkpoint / branch change. No production-code repair, extraction rerun, source amendment, live artifact replacement, publication, forecasting, or valuation. Edited this child: `RESULT.md` only. Diagnostic scripts and intermediates live only under `/tmp/bav_norm_qualify_9M2411166/`.  
Generating SHA `2396e03329c119ff3091a9b41b97d8c4312a8638`. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.  
This child does **not** declare parent, Geographic Analysis product, Operating KPIs product, Normalization product, real-company workbook, or Step 9 acceptance.

Interrupted `/tmp/bav_norm_qualify_9M2411166/` work and this RESULT section were inspected and preserved, then re-executed. Prior `/tmp/lulu_pdf_extract` text was not reused as evidence. FY2022/FY2023 statement pages are plain PyMuPDF text. FY2024/FY2025 statement/note pages are Calibri Identity-H; the temp reproducer now decodes 2-byte CIDs from content-stream hex strings (FY2024) and PDF literal octal strings (FY2025). Empirical CID map: digits `0x0E–0x17` → `0–9`; `0x0A` → comma; `0x36–0x4F` → `A–Z`; nil glyphs `0x52` (FY2025) and `0x53` (FY2024) → `—`. Plain-text pages are not CID-decoded.

## Required plan change

Any later admission, identity alignment, sparse-IS policy change, candidate insertion, signed-value convention, or tax-effect treatment needs Plan. This qualification does not revise `IMPLEMENTATION.md`.

## Task 1 — Five-period qualification ledger

Currency **USD**, unit scale **thousands**, as bound on all four filings. Statement amounts below are income-statement face amounts. Cash-flow operating add-backs equal the IS amounts on every overlapping period. Geographic reconciling items are a third presentation of the same charge, not a second P&L hit. Labels were **not** combined solely because they share `suggested_concept = impairment_and_restructuring`.

| Period | Document / SHA-256 | Physical PDF page (JSON `source.page`) | Printed page | Statement / section | Exact IS label | Reported amount (USD thousands) | Role | Zero vs missing |
|---|---|---:|---:|---|---|---:|---|---|
| `2022-01-30` | `LULU_FY2022_Annual_Report.pdf` `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 50 | 46 | Consolidated Statements of Operations / blank section | Impairment of goodwill and other assets | `0` (face `—`) | comparative | explicit nil |
| `2022-01-30` | `LULU_FY2023_Annual_Report.pdf` `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 56 | 50 | same statement | Impairment of goodwill and other assets, restructuring costs | `0` (face `—`) | comparative | explicit nil |
| `2023-01-29` | FY2022 p50 / printed 46 | 50 | 46 | same statement | Impairment of goodwill and other assets | `407913` | current_period | nonzero |
| `2023-01-29` | FY2023 p56 / printed 50 | 56 | 50 | same statement | Impairment of goodwill and other assets, restructuring costs | `407913` | comparative | nonzero |
| `2023-01-29` | FY2024 p51 / printed 45 (decoded Identity-H) | 51 | 45 | same statement | Impairment of goodwill and other assets, restructuring costs | `407913` | comparative | nonzero |
| `2024-01-28` | FY2023 p56 / printed 50 | 56 | 50 | same statement | Impairment of goodwill and other assets, restructuring costs | `74501` | current_period | nonzero |
| `2024-01-28` | FY2024 p51 / printed 45 | 51 | 45 | same statement | Impairment of goodwill and other assets, restructuring costs | `74501` | comparative | nonzero |
| `2024-01-28` | FY2025 p51 / printed 45 (decoded Identity-H) | 51 | 45 | same statement | Impairment of assets and restructuring costs | `74501` | comparative | nonzero |
| `2025-02-02` | FY2024 p51 / printed 45 | 51 | 45 | same statement | Impairment of goodwill and other assets, restructuring costs | `0` (face `—`) | current_period | explicit nil |
| `2025-02-02` | FY2025 p51 / printed 45 | 51 | 45 | same statement | Impairment of assets and restructuring costs | `0` (face `—`) | comparative | explicit nil |
| `2026-02-01` | `LULU_FY2025_Annual_Report.pdf` `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 51 | 45 | same statement | Impairment of assets and restructuring costs | `0` (face `—`) | current_period | explicit nil |

Overlapping-period IS values **agree** across filings; labels do **not**. Cash-flow add-backs (FY2022 p53/printed 49; FY2023 p59/printed 53; FY2024 p54/printed 48; FY2025 p53/printed 47) match IS amounts and use the same three labels. No impairment numeric conflict appears in `conflicts.json` (`overlap_conflict_count` remains **3**, all unrelated WC restatements).

Geographic / note reconciling (distinct from IS/CF):

- FY2023 JSON `note_facts` only: `segment.geo.q4_2023.ifop_reconciling.impairment_and_restructuring` = `407913` @ `2023-01-29` (restated_comparative) and `74501` @ `2024-01-28` (current_period), Note 23 Segmented Information, physical page 84 / printed 78.
- Later PDFs still print a corporate reconciling line (FY2024 physical 79–80; FY2025 physical 81), but those observations are **not** in FY2024/FY2025 extracted `note_facts`. Not treated as IS candidates.

`2021-01-31` appears as FY2022 comparative IS/CF explicit nil (`—` / JSON `0`) and remains outside the five-period axis (`excluded_comparative_periods`: `2021-01-31`). It was not invented and is not a ledger amount.

### Notes: composition and recurrence (facts only; no treatment inferred)

FY2022 Note (physical 65 / printed 61) and FY2023 Note 8 (physical 71–72 / printed 65–66), restated in FY2024 Note 9 (physical 66 / printed 60) and FY2025 recap (physical 67 / printed 61):

| Fiscal label in notes | IS aggregate | Composition inside the IS line | Related charges **not** in the IS line |
|---|---:|---|---|
| 2022 (period `2023-01-29`) | `407913` | goodwill `362492` + intangibles `40585` + PP&E `4836` | Studio COGS obsolescence `62928`; total pre-tax `470841`; disclosed tax effect `(28171)` |
| 2023 (period `2024-01-28`) | `74501` | asset impairments `44186` (intangibles `16951` + cloud implementation `16074` + PP&E `11161`; goodwill `0`) + restructuring `30315` | Studio COGS obsolescence `23709`; total pre-tax `98210`; disclosed tax effect `(26085)` |
| 2024 (period `2025-02-02`) | `0` / face `—` | note table current column `—` | not a missing row |
| 2025 (period `2026-02-01`) | `0` / face `—` | IS/CF dashes; no new current-year composition table | not a missing row |

Recurrence, deductibility, and documentary precedence are **UNRESOLVED**. Notes disclose discrete tax effects of the charges and MD&A non-GAAP exclusions; those are not a BAV treatment.

### Proposed signed analytical amount

**UNRESOLVED.** Extracted IS values are face-positive expenses (or explicit `0` for dashes). DEMO `operating_pretax_effective_tax` math is `pretax_adj += -reported` and therefore expects an expense-as-negative source. Using `+407913` / `+74501` as-is would reverse the add-back. Negating them is a convention choice, not evidenced by the filings. This child does not choose.

## Task 2 — Source-to-selector gap (ordinary path)

Validate-source on `build/input/lululemon/extracted` with `--source-root build/input/lululemon/source`: **4 filings, 0 errors, 0 warnings**; bound PDF SHA-256 match BASELINE. Input PDFs/JSON are byte-identical to `benchmark/lululemon/source` and `benchmark/lululemon/extracted`.

Ordinary `python -m core reconcile` (no input mutation) into `/tmp/bav_norm_qualify_9M2411166/`:

| Run | Periods | `standardized.json` SHA-256 | Impairment IS/CF lines emitted |
|---|---|---|---|
| Default filing year-ends | `2023-01-29` … `2026-02-01` | `b9d8354cbeb04edad2aba1df332ef46d49a61c2c8d9eea35cf209d4491bf1cfa` | **none** |
| `--admit-period 2022-01-30` | five ledger periods | `6c9aad59b04a5995742c68e08f1a704953796fc9fad97a036b08aeeab59051e5` | **none** |
| `build/input/lululemon-live/standardized.json` | same five | **byte-identical** to admit run | **none** |

Live `provenance.json` SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951` (786300) is byte-identical to the admit run. Live extra `management_kpi_admission.json` is outside this statement handoff. Conflicts SHA-256 `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` unchanged.

**Rule, not data loss.** `source_row_identity` = `statement|section|label|concept`. Three IS identities and three CF identities, all `suggested_concept=impairment_and_restructuring`, none covering the full model axis. `filing_standardizer._line_values_for_axis` keeps incomplete axes only for `balance_sheet`. Non-BS incomplete rows are **deliberately omitted** as `omitted_incomplete_axis` while selected observations remain in provenance. Admit-run omitted identities:

- `income_statement||impairment of goodwill and other assets|impairment_and_restructuring` — `2022-01-30`, `2023-01-29`
- `income_statement||impairment of goodwill and other assets, restructuring costs|impairment_and_restructuring` — `2022-01-30` … `2025-02-02`
- `income_statement||impairment of assets and restructuring costs|impairment_and_restructuring` — `2024-01-28` … `2026-02-01`
- matching three cash-flow identities

Default (four-period) omission is the same split (FY2022-only identity then covers only `2023-01-29` on that axis). Combining labels by concept was not performed.

Current company assumptions: `release/lululemon/Lululemon_Answer_Key.assumptions.json` SHA-256 `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` has `normalizationCandidates: []`. `core/project_companies.json` has no candidates. `current_build.build_company(assumptions=None)` setdefaults that list to `[]`.

Selector resolution against **unmodified** ordinary admit output and live `StandardizedFinancials` (no candidate inserted, no derived-input patch):

| Selector | Result |
|---|---|
| `concept:impairment_and_restructuring` | `ValueError`: matched no income-statement line |
| `concept:restructuring_expense` | same |
| `label:` each of the three exact IS labels | same |
| `normalization_cases(..., {"normalizationCandidates": []})` | **0** cases |
| explicit probe candidate with those concept selectors | same `ValueError` (fail-closed before history/nonzero checks) |

Complete-history requirement: even if a line were present, `required_period_series` needs a value on every modeled period. The omitted identities are incomplete by construction.

### `operating_pretax_effective_tax` vs this aggregate

**Source facts (not a treatment):** the IS line is one operating-expense aggregate; CF add-back and (where extracted) geographic corporate reconciling reprint the same amounts; Studio COGS obsolescence is a **separate** line. Using the IS aggregate alone would not double-count CF or geo.

**Proposed analyst reference treatment:** UNRESOLVED (recurring vs non-recurring; whether to keep the mixed impairment+restructuring aggregate vs split it; whether related COGS charges belong).

**Effective-tax convention:** the supported scope applies reported operating ETR to a pretax add-back. Notes disclose **different** item-specific tax effects (`(28171)` / `(26085)`). Whether ETR can represent this aggregate without mismatching those disclosed tax effects is **UNRESOLVED**. Deductibility is not inferred.

## Task 3 — Smallest evidenced next decision

**Boundary:** standardization identity completeness (`source_row_identity` + `_line_values_for_axis` omitting non-BS incomplete axes).  
**Expected behavior if Plan later admits a candidate:** one complete-history **income-statement** line with statement-specific identity, explicit signed convention, and an explicit `normalizationCandidates` entry. Observations must remain auditable; changing labels must not be silently merged by concept.  
**This diagnosis does not repair the handoff.**

Inspectable evidence: `/tmp/bav_norm_qualify_9M2411166/evidence.json` SHA-256 `fb9a13378756600a0087e6a6785ed38ad06a587b8d76182cf6c41d1c129f6960` (162968); `extracted_observations.json`; `ordinary_reconcile/` and `ordinary_reconcile_admit_2022/`; `pdf_pages/` plus Identity-H decoded FY2024/FY2025 statement pages. Reproducer: `/tmp/bav_norm_qualify_9M2411166/qualify_source_to_selector.py` SHA-256 `3d7a02f7027db5a18da4dd7701fada9d6dd4c66592b5f0b54aefa6bf9c41f8d2`. Statement-row PDF checks **24/24** label and amount (including Identity-H `74,501` / `407,913` / `—`). Identity-H printed-page auto-resolver remains unresolved when another 1–3 digit token exists; the decoded footer last line is still **45** (FY2024/FY2025 IS p51) and **48** / **47** (FY2024 CF p54 / FY2025 CF p53).

## Measured verification

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m core validate-source build/input/lululemon/extracted --source-root build/input/lululemon/source` | 0 | **4 filings, 0 error(s), 0 warning(s)**; PDF SHA-256 bound |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m core reconcile build/input/lululemon/extracted --source-root build/input/lululemon/source -o /tmp/bav_norm_qualify_9M2411166/ordinary_reconcile` | 0 | `overlap_conflicts=3`; no IS/CF impairment line; standardized SHA-256 `b9d8354cbeb04edad2aba1df332ef46d49a61c2c8d9eea35cf209d4491bf1cfa` |
| same + `--admit-period 2022-01-30` → `ordinary_reconcile_admit_2022` | 0 | `overlap_conflicts=3`; standardized SHA-256 `6c9aad59b04a5995742c68e08f1a704953796fc9fad97a036b08aeeab59051e5` **byte-identical** to live; provenance SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951`; 6 impairment identities `omitted_incomplete_axis` |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_norm_qualify_9M2411166/qualify_source_to_selector.py` | 0 | ledger + Identity-H CID decode + selector fail-closed; statement PDF checks **24/24**; elapsed **2.859s** |
| Protected artifacts vs `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | **8/8 UNCHANGED** |

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Five-period IS/CF/geo ledger vs PDFs+JSON; overlapping values agree and labels do not; ordinary validate/reconcile/standardize into temp; live standardized/provenance byte-match admit run; 6 `omitted_incomplete_axis` identities; selector probes fail-closed on unmodified output; empty company `normalizationCandidates`; note composition and disclosed tax effects; Identity-H CID decode of FY2024/FY2025 face amounts `74,501` / `407,913` / `—` (CID `0x53`/`0x52`); statement PDF checks **24/24**; checkpoints **50/50**; extracts **8/8** |
| Unresolved by design | signed analytical convention; recurring/non-recurring treatment; deductibility; whether ETR matches note tax effects; later-filing geographic note_facts not extracted; broader physical-page mapping beyond cited pages |
| Retained, not re-measured independently | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; stores `574/655/711/767/811`; geo **56/264**; preserved **486**; ordinary-fixture unavailable **101**; segment-margin formulas **15**; complete `core/tests` **3240** from `.61`; Excel verifications from `.62`–`.65` |
| Not claimed | Real-company normalization workbook; candidate admission; implementation repair; treatment-conditioned Excel; normalized per-share; parent or Step 9 completion |

## Remaining scope

Source qualification of the Lululemon impairment/restructuring history and the ordinary-path omission is complete for this child. Candidate admission, any handoff repair, treatment-dependent Excel verification, and normalized per-share acceptance remain open.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.65` are not reopened. G6–G9, segment remainder, benchmark publication, independent M&A Net Debt, Complete NOPAT/RNOA, forecasting and valuation remain deferred. No prospective IDs reserved.

Working-tree HEAD is `2396e03329c119ff3091a9b41b97d8c4312a8638`. `.git/autocycle/latest-implementation` was not rewritten.

---

# RESULT.md — Step 9M.2.4.1.1.1.66 Real-company normalization: conditional signed source-qualification proposal

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.66 — Real-company normalization: source-to-selector qualification  
**Work:** `9a9bf001dea84a868ef326d8ef5126ea` (continued; missing signed proposal repaired)  
**Plan:** `18db9dda6e634091bde2f4d2adb0e798`  
**Finding:** `real-company-normalization-source-to-selector-gap`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted illustrative normalization Excel work `e2b825657b944d36beafca6c36cf91ff` remains complete and is not reopened. Geographic/KPI Excel verification is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed. Instruction `20260918-115651-000000007` remains retained. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `58e4bdc0981f350f68b7b3af6eb39275aeee0202dd03fe33d3e1fc9fad98e7bd` (9476).  
No commit / push / sync / checkpoint / branch change. No production-code repair, candidate admission, extraction rerun, source amendment, live artifact replacement, publication, forecasting, or valuation. Edited this child: `RESULT.md` only. Diagnostic scripts and intermediates live only under `/tmp/bav_norm_qualify_9M2411166/`.  
Generating SHA `601698100d57ce29053478a3018c8860474728df`. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.  
This child does **not** declare parent, Geographic Analysis product, Operating KPIs product, Normalization product, real-company workbook, or Step 9 acceptance.

Prior RESULT under plan `512736ff019643588afc95abb61cab90` remains as written for the ordinary-path diagnosis. Its blanket “signed analytical convention UNRESOLVED” and any implication that the signed proposal was complete are **superseded only for that missing proposal**. Interrupted `/tmp/bav_norm_qualify_9M2411166/` evidence was inspected and preserved; `evidence.json` and `qualify_source_to_selector.py` were not overwritten.

## Required plan change

No required plan change. Later admission, identity alignment, sparse-IS policy, candidate insertion, implemented source-sign conversion, or tax-effect treatment still need Plan. This child does not revise `IMPLEMENTATION.md`.

## Correction of prior signed-convention statement

The prior child correctly recorded face-positive extracted amounts and the ordinary omission/rejection trace. It left engine representation unsigned. This child records an explicit **conditional engine-representation proposal**, not a filing claim and not an implemented conversion:

- face amounts remain `0 / 407913 / 74501 / 0 / 0`;
- proposed signed analytical amounts equal **negative reported face expense**;
- adoption, identity merge, documentary precedence, and accounting treatment remain unresolved.

## Task 1 — Conditional signed qualification ledger

Currency **USD**, unit scale **thousands**. Face amounts are the existing source-checked IS observations. Proposed signed amounts use the engine’s expense-negative convention: `proposed_signed = -face_reported`. Labels were **not** combined by `suggested_concept`. This history does not establish documentary precedence or supply missing observations.

| Period | Face (USD thousands) | Proposed signed analytical (USD thousands) | Linked existing IS evidence | Zero vs missing |
|---|---:|---:|---|---|
| `2022-01-30` | `0` | `0` | FY2022 p50/printed 46 label `Impairment of goodwill and other assets` (comparative explicit nil); FY2023 p56/printed 50 label `Impairment of goodwill and other assets, restructuring costs` (comparative explicit nil) | explicit nil |
| `2023-01-29` | `407913` | `-407913` | FY2022 current; FY2023 comparative; FY2024 comparative (decoded Identity-H); values agree, labels do not | nonzero |
| `2024-01-28` | `74501` | `-74501` | FY2023 current; FY2024 comparative; FY2025 comparative (decoded Identity-H); values agree, labels do not | nonzero |
| `2025-02-02` | `0` | `0` | FY2024 current explicit nil; FY2025 comparative explicit nil | explicit nil |
| `2026-02-01` | `0` | `0` | FY2025 current explicit nil | explicit nil |

Document hashes, printed/physical pages, exact labels, statement identities, presentation roles, overlapping observations, and explicit-zero evidence remain those already recorded in the prior ledger and authenticated `evidence.json`. Cash-flow add-backs continue to equal the IS face amounts on every overlapping period and are **not** a second P&L hit. Geographic reconciling reprints (where extracted) are a third presentation. `2021-01-31` remains outside the five-period axis.

## Task 2 — Sign arithmetic separated from accounting judgments

Cited `core/model/normalization.py` `compute_normalization_series` (SHA-256 `5b6e99870716ede72416e774c646355890e4911cf681b143538db25933bd252f`, 11826 bytes): `pretax_adj += -float(reported)`. Recurring treatment skips the candidate (`continue`). Scope remains `operating_pretax_effective_tax`.

Using the **conditional signed series** as hypothetical `reported` (not admitted; ordinary standardized still has no IS candidate):

| Treatment | Pretax adjustment series |
|---|---|
| Hypothetical Non-recurring | `0 / +407913 / +74501 / 0 / 0` |
| Hypothetical Recurring | `0 / 0 / 0 / 0 / 0` |

Independent check: if face-positive amounts were fed to the same `pretax_adj += -reported` line, Non-recurring pretax would reverse to `0 / -407913 / -74501 / 0 / 0`. That reversal is why the signed proposal exists; it is not a filing claim.

`operating_pretax_effective_tax` applies reported operating ETR only when pretax adjustment is nonzero and ETR is numeric: after-tax = `pretax_adj * (1.0 - ETR)`. If pretax adjustment is `0.0`, after-tax is `0.0` without an ETR. If ETR is `UNDEFINED_RATIO` (`#N/A`), after-tax is `UNDEFINED_RATIO`. This child **did not invent tax rates and did not calculate after-tax amounts** for the nonzero periods. Disclosed note tax effects `(28171)` and `(26085)` cover broader charge totals (including Studio COGS) and do **not** establish tax effects for this IS aggregate alone.

Unresolved (not prerequisites for documenting the conditional proposal):

- recurring vs non-recurring treatment;
- aggregate vs components;
- related COGS inclusion;
- deductibility;
- suitability of operating ETR for this IS aggregate.

Count the IS aggregate **once**: CF add-backs and geographic reconciling observations are alternate presentations; Studio COGS charges remain excluded from this proposal.

Diagnosed boundary **preserved, not repaired**: three IS and three CF identities remain `omitted_incomplete_axis`; ordinary live/admit standardized still emit **no** IS impairment line; selectors still fail closed. The conditional proposal does not admit a candidate or convert source signs.

Omitted identities (admit-run provenance, unchanged):

- `income_statement||impairment of goodwill and other assets|impairment_and_restructuring`
- `income_statement||impairment of goodwill and other assets, restructuring costs|impairment_and_restructuring`
- `income_statement||impairment of assets and restructuring costs|impairment_and_restructuring`
- matching three cash-flow identities

## Task 3 — Reviewable verification

Retained ordinary-path evidence authenticated, not regenerated. Missing signed-arithmetic evidence written only under `/tmp/bav_norm_qualify_9M2411166/`. Hypothetical arithmetic kept separate from actual selector results.

| Artifact | SHA-256 | Bytes | Role |
|---|---|---:|---|
| `/tmp/bav_norm_qualify_9M2411166/evidence.json` | `fb9a13378756600a0087e6a6785ed38ad06a587b8d76182cf6c41d1c129f6960` | 162968 | retained ordinary-path ledger; **authenticated match** |
| `/tmp/bav_norm_qualify_9M2411166/qualify_source_to_selector.py` | `3d7a02f7027db5a18da4dd7701fada9d6dd4c66592b5f0b54aefa6bf9c41f8d2` | 41666 | retained reproducer; **authenticated match** |
| `/tmp/bav_norm_qualify_9M2411166/signed_arithmetic_check.py` | `cab57b5d973477ebe8d069096cc1fd314fa9faf74b2b938b74af1961bd5eaa43` | 22103 | new read-only arithmetic checker |
| `/tmp/bav_norm_qualify_9M2411166/signed_arithmetic_check.json` | `a870a856e1959e370dca979d11e85c665f9ce76dc03d1420de5407daac608699` | 33492 | new measured arithmetic + hash evidence |

Live `build/input/lululemon-live/standardized.json` SHA-256 `6c9aad59b04a5995742c68e08f1a704953796fc9fad97a036b08aeeab59051e5` **byte-identical** to retained admit-run standardized. Live provenance SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951` byte-identical to admit-run. Conflicts SHA-256 `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0`. Default four-period standardized SHA-256 `b9d8354cbeb04edad2aba1df332ef46d49a61c2c8d9eea35cf209d4491bf1cfa`. Ordinary output still has **0** IS impairment lines.

Fresh selector probes against unmodified live and admit `StandardizedFinancials` (no candidate inserted): all five selectors `ValueError` matched no income-statement line; empty `normalizationCandidates` → **0** cases; explicit probe candidates fail closed before history/nonzero checks.

## Measured verification

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_norm_qualify_9M2411166/signed_arithmetic_check.py` | 0 | face `0/407913/74501/0/0`; signed `0/-407913/-74501/0/0`; Non-recurring pretax `0/+407913/+74501/0/0`; Recurring pretax all `0`; retained evidence/reproducer hashes match; live=admit standardized; selectors fail-closed; elapsed **1.486s** |
| Protected artifacts vs `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (fresh this child) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | **8/8 UNCHANGED** (fresh this child) |

Prior child commands (retained, not re-executed): validate-source 4/0/0; ordinary reconcile default and `--admit-period 2022-01-30`; `qualify_source_to_selector.py` statement PDF checks **24/24**. Those outputs remain byte-identical to the hashes above.

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Conditional signed series `0 / -407913 / -74501 / 0 / 0`; transformation `proposed_signed = -face`; hypothetical Non-recurring pretax `0 / +407913 / +74501 / 0 / 0` and Recurring zeros via `pretax_adj += -reported`; no after-tax amounts calculated; correction of prior blanket signed-convention UNRESOLVED; authenticated retained evidence/reproducer hashes; fresh selector fail-closed on live/admit; checkpoints **50/50**; extracts **8/8** |
| Retained, re-authenticated | Five-period IS/CF/geo ledger vs PDFs+JSON; overlapping values agree and labels do not; ordinary validate/reconcile/standardize into temp; live standardized/provenance byte-match admit run; 6 `omitted_incomplete_axis` identities; empty company `normalizationCandidates`; note composition and disclosed tax effects; Identity-H CID decode; statement PDF checks **24/24** |
| Unresolved by design | adoption of the signed convention into source conversion; recurring/non-recurring treatment; aggregate vs components; related COGS; deductibility; whether ETR matches note tax effects; later-filing geographic `note_facts` not extracted; broader physical-page mapping beyond cited pages |
| Retained, not re-measured independently | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; stores `574/655/711/767/811`, changes `None/81/56/56/44`; five revenue sources / eight revenue-store practices; geo **56/264**; preserved **486**; ordinary-fixture unavailable **101**; segment-margin formulas **15**; complete `core/tests` **3240** from `.61`; Excel verifications from `.62`–`.65`; management 135 observations (`29/36/37/33`), nine definitions, 107 market observations, three excluded targets, assessments `0/22/6/107`, 24 incompatible pairs, six singletons, zero selections/revision links; 110 accepted additions; G1/G2/G3/G5 aliases; twelve pretax/ETR cases; opening-only CoD `0.374`; selected Americas `7928156`; audit-only `7928256`; capex `638657/651865/689232/680802`; repurchase residuals `-116195/1085647/-207544/-256674`; NCIT `28555/15864/0/None`; Common stock `611/606/581/557` |
| Not claimed | Real-company normalization workbook; candidate admission; implementation repair; treatment-conditioned Excel; normalized per-share; parent or Step 9 completion |

## Remaining scope

The conditional signed qualification proposal is complete for this child. Candidate admission, any handoff repair, treatment-dependent Excel verification, normalized per-share acceptance, and real-company workbook acceptance remain open. Both workflow commitments remain unfinished.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.65`, and the prior source-to-selector diagnosis are not reopened. G6 opening BS, G7 lease maturity/notes, G8 deferral, G9 standalone interest completeness, segment assets/capex/significant expenses/D&A, benchmark publication, independent M&A Net Debt, Complete NOPAT/RNOA, forecasting and valuation remain deferred. Retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED. Parent temporary-build acceptance remains: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. No prospective IDs reserved.

Working-tree HEAD is `601698100d57ce29053478a3018c8860474728df`. `.git/autocycle/latest-implementation` was not rewritten.

---

# RESULT.md — Step 9M.2.4.1.1.1.67 Real-company normalization: bounded candidate-admission contract

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.67 — Real-company normalization: bounded candidate-admission contract  
**Work:** `d0a2655be7ea4eda91ec1e807a440265`  
**Plan:** `73e8e14b79ca4ee6b3375730e334b95b`  
**Finding:** `real-company-normalization-source-to-selector-gap`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Accepted source qualification `9a9bf001dea84a868ef326d8ef5126ea` / Step `9M.2.4.1.1.1.66` is not reopened. Accepted illustrative normalization Excel work `e2b825657b944d36beafca6c36cf91ff` is not reopened. Geographic/KPI Excel verification is not reopened.  
Instruction `20260916-075534-000000006` is retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`). Recovery was not re-executed. Instruction `20260918-115651-000000007` remains retained. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain unfinished beyond this increment.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `7576af968d341d70387f98fb958a91e1b8fc62152eff8e8d3dd1f1e5c250fdf2` (9959).  
No commit / push / sync / checkpoint / branch change. No production-code repair, live candidate activation, extraction rerun, source amendment, live artifact replacement, publication, forecasting, or valuation. Edited this child: `RESULT.md` only. Diagnostic scripts and intermediates live only under `/tmp/bav_norm_admit_9M2411167/`. Retained qualification evidence under `/tmp/bav_norm_qualify_9M2411166/` was authenticated and not overwritten.  
Generating SHA `7c0906c68189f183fbe8352ede6cb924a9abb2d5`. Interpreter `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. `SEGMENT_BRIDGE_TOLERANCE = 0.0`.  
This child does **not** declare parent, Geographic Analysis product, Operating KPIs product, Normalization product, real-company workbook, or Step 9 acceptance.

No prior `/tmp/bav_norm_admit_9M2411167/` work existed. Interrupted qualification artifacts were inspected and preserved.

## Required plan change

No required plan change. Production admission, documentary-identity merge, `normalizationCandidates` activation, implemented source-sign conversion, and tax-effect treatment still need Plan. This child does not revise `IMPLEMENTATION.md`.

## Task 1 — Explicit admission contract

Inspected, not modified: `core/ingestion/filing_validator.py` (`source_row_identity` = `statement|section|label|concept`, SHA-256 `9c2051171592cb7e230f8ee62c1b645fc014ce28b029747d839c186439e59a00`), `core/ingestion/filing_reconciler.py` (documentary grouping, SHA-256 `deb6d89750bc763868800a6923179d59d4a2d0bf18cd218f778d3b73e9fdc85d`), `core/ingestion/filing_standardizer.py` (`_line_values_for_axis` omits incomplete non-BS axes, SHA-256 `4209f4f3d7ae6bc34d2828f9d204a86342893e370158862a38d177b2d33ec97a`), `core/model/normalization.py` (unique IS selectors + `pretax_adj += -float(reported)`, SHA-256 `5b6e99870716ede72416e774c646355890e4911cf681b143538db25933bd252f`), `core/data/standardized_io.py` (`LineItem.concept` survives export/reload, SHA-256 `546857707bc424809f89d256b4e7924d80a923fb7e9856377bbcd630109686cf`).

**Smallest proposed integration boundary (not created):** a new opt-in layer `core/ingestion/normalization_candidate_admission.py` after documentary standardization. It would consume qualified IS observations and a **copy** of `StandardizedFinancials`, emit a separate analytical `LineItem`, and leave `_line_values_for_axis` / `source_row_identity` unchanged. `normalizationCandidates` activation remains a separate company-assumption contract.

Documentary IS members (closed set; not merged by concept):

- `income_statement||impairment of goodwill and other assets|impairment_and_restructuring`
- `income_statement||impairment of goodwill and other assets, restructuring costs|impairment_and_restructuring`
- `income_statement||impairment of assets and restructuring costs|impairment_and_restructuring`

CF add-backs and `segment.geo.q4_2023.ifop_reconciling.impairment_and_restructuring` are audit evidence only. Studio COGS / components are excluded. `2021-01-31` remains outside the five-period axis (2 retained comparative observations; not invented).

Analytical identity (distinct from documentary identities):

- label `Impairment and restructuring costs (provisional analytical aggregate)`
- concept `analytical_is_impairment_restructuring_aggregate`
- unique selector `concept:analytical_is_impairment_restructuring_aggregate`
- line identity after reload `concept=analytical_is_impairment_restructuring_aggregate|label=impairment and restructuring costs (provisional analytical aggregate)`

Sign conversion is once-only: `analytical_amount = -reported_face_expense`. Face amounts remain `0/407913/74501/0/0`.

**Mapping status: provisional.** Matching `suggested_concept` and agreeing overlapping values are recorded as source-supported scope rationale, not authorization. Equivalence of the three IS labels is **UNRESOLVED**. The grouping is **not** an accepted source fact. Production activation is **blocked**.

Gates: complete-axis; USD/thousands; bound source SHA-256; unique overlapping IS value; closed authorized membership; no CF/geo membership; no Studio COGS; no aggregate+component double count; no duplicate observation use; missing remains missing; sign conversion applied exactly once. No inferred chronology, transitive precedence, or zero filling.

Factual eligibility is separate from `normalizationCandidates` activation, which still requires explicit treatment, rationale, consequence note, and supported scope.

## Task 2 — Isolated prototype

Prototype constructed the five-period series from qualified `extracted_observations.json`, not a hand-entered line, then inserted one analytical `LineItem` into a copy of ordinary `--admit-period 2022-01-30` standardized data (16 → 17 IS lines). Ordinary live/default/admit files were not written.

| Period | Face | Analytical | IS obs | Explicit nil | Physical pages | Printed pages from retained lookup |
|---|---:|---:|---:|---|---|---|
| `2022-01-30` | `0` | `0` | 2 | yes | 50, 56 | 46, 50 |
| `2023-01-29` | `407913` | `-407913` | 3 | no | 50, 51, 56 | 46, 50; FY2024 p51 unresolved |
| `2024-01-28` | `74501` | `-74501` | 3 | no | 51, 56 | 50; FY2024/FY2025 p51 unresolved |
| `2025-02-02` | `0` | `0` | 2 | yes | 51 | FY2024/FY2025 p51 unresolved |
| `2026-02-01` | `0` | `0` | 1 | yes | 51 | FY2025 p51 unresolved |

FY2024/FY2025 Identity-H printed-page auto-resolver remains unresolved in retained `pdf_page_checks`; this child did not invent printed `45`. Physical page 51 and bound PDF hashes remain inspectable.

Export/reload of isolated financials resolved **exactly one** IS candidate via `concept:analytical_is_impairment_restructuring_aggregate`. Documentary selectors `concept:impairment_and_restructuring`, `concept:restructuring_expense`, and the three exact labels still match no isolated line.

Existing `normalization_cases` / `compute_normalization_series` were exercised separately with **hypothetical** Recurring and Non-recurring assumptions (labeled not adopted). Pretax: Recurring `0/0/0/0/0`; Non-recurring `0/+407913/+74501/0/0`. After-tax used `UNDEFINED_RATIO` (`#N/A`) on nonzero pretax periods; no tax rate was invented; note effects `(28171)` / `(26085)` were not attributed to this aggregate. Empty `normalizationCandidates` still yields **0** cases on live, ordinary admit, and isolated copies. Company assumptions remain `[]`.

Negative probes **11/11** rejected as specified:

| Probe | Reason |
|---|---|
| missing period evidence | `missing_period_evidence` (`2022-01-30`) |
| altered source binding | `altered_or_unbound_source_hash` |
| conflicting overlaps | `conflicting_overlapping_observations` (`407913` vs `999999`) |
| unauthorized identity | `unauthorized_identity_membership` |
| CF substitution | `cash_flow_substitution_forbidden` |
| Studio COGS | `studio_cogs_excluded` |
| aggregate+component | `aggregate_and_component_double_count` |
| absent sign conversion | `absent_sign_conversion` |
| repeated sign conversion | `repeated_sign_conversion` |
| duplicate observation use | `observation_used_more_than_once` |
| ambiguous selector | existing selector `ValueError` matched 2 lines |

## Task 3 — Reviewable evidence and implementation boundary

| Artifact | SHA-256 | Bytes | Role |
|---|---|---:|---|
| `/tmp/bav_norm_qualify_9M2411166/evidence.json` | `fb9a13378756600a0087e6a6785ed38ad06a587b8d76182cf6c41d1c129f6960` | 162968 | retained ordinary-path ledger; **authenticated match** |
| `/tmp/bav_norm_qualify_9M2411166/qualify_source_to_selector.py` | `3d7a02f7027db5a18da4dd7701fada9d6dd4c66592b5f0b54aefa6bf9c41f8d2` | 41666 | retained reproducer; **authenticated match** |
| `/tmp/bav_norm_qualify_9M2411166/signed_arithmetic_check.py` | `cab57b5d973477ebe8d069096cc1fd314fa9faf74b2b938b74af1961bd5eaa43` | 22103 | retained signed proposal; **authenticated match** |
| `/tmp/bav_norm_qualify_9M2411166/signed_arithmetic_check.json` | `a870a856e1959e370dca979d11e85c665f9ce76dc03d1420de5407daac608699` | 33492 | retained arithmetic; **authenticated match** |
| `/tmp/bav_norm_qualify_9M2411166/extracted_observations.json` | `d74a6f1588a0b1397eaa79dd24c02e3454c46643e7e3b18105a46adbc9129880` | 22010 | qualified observations used for construction |
| `/tmp/bav_norm_admit_9M2411167/admit_candidate_contract.py` | `db884002cc088bb631944e2804f693509b7e0019f53befccf82b34e15d775621` | 57367 | isolated prototype |
| `/tmp/bav_norm_admit_9M2411167/admit_candidate_contract.json` | `1c1a897cf96abf411a9d42f0aef91fd491262ada9e4c6d6f6593a8bef870b1ff` | 59654 | measured contract + probes |
| `/tmp/bav_norm_admit_9M2411167/isolated_standardized.json` | `8f9e4adaf0dfba00fdead7e05b7860ce96dd990e65a67dd2136da578ae4159bd` | 29925 | isolated export/reload payload |

Ordinary live standardized SHA-256 `6c9aad59b04a5995742c68e08f1a704953796fc9fad97a036b08aeeab59051e5` **byte-identical** to retained admit-run. Live provenance SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951` byte-identical to admit-run. Conflicts SHA-256 `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0`. Default four-period standardized SHA-256 `b9d8354cbeb04edad2aba1df332ef46d49a61c2c8d9eea35cf209d4491bf1cfa`. Ordinary outputs still have **0** IS impairment lines; all five documentary selectors still `ValueError`.

Three IS and three CF identities remain `omitted_incomplete_axis`. Handoff was not repaired.

Unresolved adoption decisions (technical feasibility ≠ authorization): label equivalence of the three IS identities; recurring vs non-recurring; aggregate vs components; related COGS; deductibility; operating-ETR suitability; later-audited documentary precedence; production `normalizationCandidates` activation; omitted-incomplete-axis handoff repair.

## Measured verification

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python /tmp/bav_norm_admit_9M2411167/admit_candidate_contract.py` | 0 | face `0/407913/74501/0/0`; analytical `0/-407913/-74501/0/0`; unique selector 1 match after export/reload; hypothetical Non-recurring pretax `0/+407913/+74501/0/0`; Recurring pretax all `0`; after-tax `#N/A` on nonzero pretax; negatives **11/11**; ordinary selectors fail-closed; production activation **blocked**; elapsed **1.241s** |
| Protected artifacts vs `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` path blobs | 0 | **8/8 UNCHANGED** |

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Explicit admission contract; isolated evidence-bound construction; unique analytical selector after export/reload; hypothetical Recurring/Non-recurring pretax via existing normalization code; 11 fail-closed negative probes; ordinary live/default/admit hashes and selector rejection unchanged; checkpoints **50/50**; extracts **8/8** |
| Retained, re-authenticated | Five-period IS/CF/geo ledger vs PDFs+JSON; overlapping values agree and labels do not; ordinary validate/reconcile/standardize into temp; live standardized/provenance byte-match admit run; 6 `omitted_incomplete_axis` identities; empty company `normalizationCandidates`; note composition and disclosed tax effects; Identity-H CID decode; statement PDF checks **24/24**; conditional signed arithmetic hashes |
| Unresolved by design | label equivalence / grouping authorization; production candidate activation; implemented source-sign conversion; recurring/non-recurring treatment; aggregate vs components; related COGS; deductibility; whether ETR matches note tax effects; later-filing geographic `note_facts` not extracted; broader physical-page mapping; FY2024/FY2025 printed-page auto-resolver |
| Retained, not re-measured independently | Store/mixed/compsales totals `766/768/760`; Fast Retailing **577**; stores `574/655/711/767/811`, changes `None/81/56/56/44`; five revenue sources / eight revenue-store practices; geo **56/264**; preserved **486**; ordinary-fixture unavailable **101**; segment-margin formulas **15**; complete `core/tests` **3240** from `.61`; Excel verifications from `.62`–`.65`; management 135 observations (`29/36/37/33`), nine definitions, 107 market observations, three excluded targets, assessments `0/22/6/107`, 24 incompatible pairs, six singletons, zero selections/revision links; 110 accepted additions; G1/G2/G3/G5 aliases; twelve pretax/ETR cases; opening-only CoD `0.374`; selected Americas `7928156`; audit-only `7928256`; capex `638657/651865/689232/680802`; repurchase residuals `-116195/1085647/-207544/-256674`; NCIT `28555/15864/0/None`; Common stock `611/606/581/557` |
| Not claimed | Real-company normalization workbook; production candidate admission; implementation repair; accepted source-fact grouping; treatment-conditioned Excel; normalized per-share; parent or Step 9 completion |

## Remaining scope

The bounded candidate-admission contract and isolated proof are complete for this child. Production handoff repair, candidate activation, treatment-dependent Excel verification, normalized per-share acceptance, and real-company workbook acceptance remain open. Both workflow commitments remain unfinished.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37` through `.66`, and the prior source-to-selector diagnosis are not reopened. G6–G9, segment assets/capex/significant expenses/D&A, benchmark publication, independent M&A Net Debt, Complete NOPAT/RNOA, forecasting and valuation remain deferred. Retain A2-ED/B7-MID documentary UNVERIFIED, A5/B8/E10 pending Plan closure and E11 NonReq UNVERIFIED. Parent temporary-build acceptance remains: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. No prospective IDs reserved.

Working-tree HEAD is `7c0906c68189f183fbe8352ede6cb924a9abb2d5`. `.git/autocycle/latest-implementation` was not rewritten.

