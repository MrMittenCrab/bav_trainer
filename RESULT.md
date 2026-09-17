# RESULT.md — Step 9M.2.4.1.1.1.44 Operating KPIs: explicit-revision canonical selection

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.44 — Operating KPIs — Explicit-revision canonical selection  
**Work:** `b15c586a94d94f5b8bc4f011456ed5db`  
**Plan:** `d45934e03cf44d908e7925a16e0f270b`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `72ead326d8625e950c3b7e5af1c5bf2dfe18887a10bf26a91c0e272839902cc7` (10810).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, model-facing canonical history, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi_reconciliation.py`, `core/tests/test_management_kpi_reconciliation.py`, `core/tests/test_management_kpi_admission.py`, `core/tests/test_filing_cli.py`, and `RESULT.md`. Production change is `_link_involves` only; `core/ingestion/management_kpi.py` was not edited.

No required plan change.

Prior documentary-revision work `78a0392fcae9437dbd35dc0cc7266a58` remains accepted. A previous child of this same step/work recorded selection without candidate-locator involvement and claimed COMPLETE under plan `dd96bab19d534edda15694d1b549b55f` with focused **352** / required **1031**; those counts are retained historical measurements, not this child's fresh results. That completion claim is not this increment's acceptance. `.git/autocycle/latest-implementation` currently references `HEAD: e6c74654bd79864691b4e883a5aab6409f899680` and log `cursor-20260917-104553-10519.log` and was not rewritten. The earlier pointer wording (`3f5f4b0a...` / `cursor-20260917-103006-7400.log`) is stale and is not restated as current.

`_link_involves` now treats a revision link as involving a group when its reviser, uniquely bound revised locator, or `candidate_locators` intersect the group's locators, including when `revised` is null. The existing unresolved/incompatible assertion gate then applies to every such link, including an incoming assertion from another group. Candidate intersection does not create unique binding, an intra-group revision, or precedence (`_link_is_intra` still requires a uniquely bound revised member). Unrelated candidate sets outside the group do not block an otherwise eligible pair. Model-facing `canonical_selection` remains `deferred`; observations stay `admitted_unreconciled` and excluded from `StandardizedFinancials`. Supplied mixed inputs still select nothing.

---

## Task 1 — Repair candidate-locator involvement

`_link_involves` now returns true when:

- the reviser locator is in the group; or
- a uniquely bound `revised` locator is in the group; or
- `candidate_locators` intersects the group, including `revised is None`.

Incoming unresolved/incompatible assertions that name a group member only among ambiguous candidates therefore defer that complete two-occurrence group: `status=deferred`, `selected`/`superseded` null, and reasons include `unresolved` plus `ambiguous_target`. The recognized intra-group directed revision remains serialized and does not become a candidate-bound winner. Unrelated assertions whose candidates lie entirely outside the group leave selection unchanged.

---

## Task 2 — Ordinary admission and CLI

Temporary fixtures for both families build an otherwise eligible two-occurrence group (audited reviser, uniquely bound evidenced revision, exactly two supported members) and add an incoming assertion from a later-period same-family group with `revised=null`, `ambiguous_target`, and candidate locators including the superseded or the reviser. The tested group stays deferred; values, printed sources, definitions, locators, and revision/assurance evidence survive; the extra candidate is `unsupported_variant` and is not a third group member. Removing the incoming assertion, or placing every candidate outside the group, restores selection. Renamed/reordered inputs and reversed pair orientation preserve documentary direction and deferred unresolved reasons. CLI `validate-source` / `reconcile` serialize the same deferred group, unresolved incoming link, and candidate locators. Existing positive-selection and rejection coverage is retained.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

New regressions against the reviewed (pre-repair) `_link_involves` behavior: **14 failed**, **4 passed** in **2.03s**. The four passes are the intended controls (remove incoming assertion; candidates entirely outside the eligible group). After repair the same 18 tests passed in **2.51s**.

Independent mixed-directory load of supplied extracted inputs:

- 4 statement filings (FY2022–FY2025) + 4 management documents
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- 107 market-table store observations
- 3 nonhistorical targets
- status `admitted_unreconciled`; model-facing canonical selection `deferred`
- assessments: **135** items covering every reported observation; **28** supported, **107** outside_scope, **0** unsupported_variant
- comparability: comparable **0**, not_comparable **22**, unresolved **6**, outside_scope **107**
- reconciliation: pair_count **24**; agreeing_duplicate **0**; conflicting_candidate **0**; incompatible **24**; unresolved pairs **0**; singleton **6**; unsupported_variant **0**; outside_scope **107**
- supplied presentation/assurance/revision: all observations unknown; `revision_links` **[]**; counts recognized/unresolved/incompatible **0/0/0**
- group selections: **28** identity-period groups, all `deferred`; selected **0**; superseded **0**
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile` against temporary mixed and annual-only copies (admit `2022-01-30`): mixed writes `management_kpi_admission.json` with 135 assessment items, supported_count **28**, pair_count **24**, comparability 0/22/6/107, zero revision links, and zero selected/superseded group members; annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`. Mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Pre-repair new regressions **14 failed / 4 passed**; post-repair **18 passed**; mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation pairs **24** all `incompatible`, agreeing/conflicting **0/0**, singletons **6**, outside-scope coverage **107**; supplied presentation/assurance/revision remain unknown; `revision_links` empty; identity-period group selections **28** all deferred, selected/superseded **0/0**; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; CLI mixed admission includes group_selections and annual-only omits the artifact; focused pytest **370 passed**; required suite **1049 passed**, **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Prior same-step child plan `dd96bab19d534edda15694d1b549b55f` focused **352** / required **1031**; work `78a0392fcae9437dbd35dc0cc7266a58` focused **309** / required **988**; older 232/911, 175/854 and 117/796 remain historical |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; model-facing management-history handoff; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

`.git/autocycle/latest-implementation` SHA-256 `bcf4cc195afd6c3b0654b641fdb9b0cd73bf3343c62a8711fa1fe217b3fd6bef` (183) currently points at `e6c74654bd79864691b4e883a5aab6409f899680` / `cursor-20260917-104553-10519.log` and was **not** manually rewritten. Any remaining controller refresh belongs to the existing controller mechanism; prospective IDs are not certified here.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py::test_incoming_ambiguous_candidate_defers_otherwise_eligible_group core/tests/test_management_kpi_reconciliation.py::test_removing_incoming_ambiguous_assertion_selects core/tests/test_management_kpi_reconciliation.py::test_unrelated_ambiguous_candidates_do_not_block_selection core/tests/test_management_kpi_reconciliation.py::test_incoming_ambiguous_candidate_is_permutation_invariant core/tests/test_management_kpi_reconciliation.py::test_cli_serializes_incoming_ambiguous_candidate_deferral core/tests/test_management_kpi_admission.py::test_ordinary_admission_incoming_ambiguous_candidate_defers core/tests/test_filing_cli.py::test_cli_serializes_incoming_ambiguous_candidate_deferral -q --tb=line` (before `_link_involves` repair) | 1 | **14 failed**, **4 passed** in **2.03s** (controls only) |
| same selector after repair | 0 | **18 passed** in **2.51s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_filing_cli.py -q --tb=short` | 0 | **370 passed** in **16.81s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py core/tests/test_management_kpi_identity.py -q` | 0 | **1049 passed** in **180.36s** |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory annual copy; mixed from supplied extracted dir; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; group_selections 28 deferred, selected/superseded 0/0; std/conflicts/statement-provenance match; extracted JSON unchanged |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`; mixed writes `management_kpi_admission.json` (reported 135, assessments 135/supported 28, comparability 0/22/6/107, pair_count 24, revision_links 0, selected/superseded 0/0, 28 deferred groups); annual-only omits that artifact; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi_reconciliation.py` | `06a0278cfd7d07d0e78b496d3cf09e68ee703eb38d3fca87144fc8978b53bb1f` | 39935 |
| `core/tests/test_management_kpi_reconciliation.py` | `9127c8a4e3c3487f012d70b1fc5e812c6936284fc1c493fe5bfa1dc7145aec64` | 127876 |
| `core/tests/test_management_kpi_admission.py` | `a183265255bc3cdd7799f365b2971497f485b50884feb4cdd5c6c7bb0a397283` | 62441 |
| `core/tests/test_filing_cli.py` | `e924621a8705bc6d037b47c7edc47738159aae1c0651ba996eba2c9e9fd5c869` | 15797 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Five snapshot-matched production/test identities retained from `edit_replay_counts`: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`. Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Admitted observations remain audit-only and excluded from `StandardizedFinancials`. Model-facing canonical history remains deferred.

---

## Remaining scope

Beyond this increment remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Then extend validated `StandardizedFinancials` histories/round trips, Operating KPI analytics and supported revenue/geography/margin/inventory/working-capital/capex relationships, followed by ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and definition/calendar discontinuities; distinguish reported/statement-derived/analyst-derived measures; infer no causality. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41`, `.42` and `.43` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
