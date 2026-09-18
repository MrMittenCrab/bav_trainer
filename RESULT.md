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

