# RESULT.md — Step 9M.2.4.1.1.1.50 Operating KPIs: store-count learner schedule and Check

**Status:** COMPLETE (this work child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.50 — Operating KPIs — Store-count learner schedule and Check integration  
**Work:** `a486cad27960408bb13d183bbf863bba`  
**Plan:** `d499604b75584d43a9feeb5f52aea75d`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
Instruction `20260916-075534-000000006` is incorporated as retained extraction/source-binding evidence (eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151`; mixed vs annual-only canonical standardized/conflicts/statement-provenance match). That identifier is not a status token and recovery was not re-executed.  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `7393a2d346a2f2a30ae2b8624a893648247d0ef5d1fd29f3eab29aba9baa6eb3` (9975).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed; Check used formula-string match and injected cached-value probes.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/data/standardized_io.py`, `core/engine/reference_model.py`, `core/tests/test_operating_kpi_workbook.py`, `core/tests/test_build_cli.py`, and `RESULT.md`. README and CLI usage repairs from the prior increment were preserved and not rewritten. Existing store analytics, management, and revenue-relationship APIs were not redesigned.

No required plan change.

Working-tree HEAD is `4fc035b980b6dd0fe9470e313b588b9c53d62a89`. `.git/autocycle/latest-implementation` was not rewritten.

This increment repairs the two blocking defects: (1) `metadata.jurisdiction` fallback is now validated against the canonical jurisdiction **string** contract before required-field exemption or `str()` coercion; (2) generated Trainer/Answer-Key pairs were built with physically moved count-source cells, saved, reloaded, and inspected independently of default coordinates and resolver-only strings.

Prior RESULT claims of complete strict rejection of non-string fallback jurisdiction and of generated-layout workbook verification are withdrawn. Those claims outran the then-measured evidence: object/list/numeric/boolean `metadata.jurisdiction` fallbacks were still coercible, and layout coverage was a resolver-string unit test rather than ordinary workbook generation.

---

## Task 1 — Validate fallback jurisdiction before construction

`standardized_from_payload(..., strict=True)` still admits the supported top-level `metadata` object and copies it. When top-level `jurisdiction` is missing or `""`, `metadata.jurisdiction` is used as fallback only after a `type is str` check. Object, list, numeric, and boolean fallback values now raise `standardized.metadata.jurisdiction must be str` without mutating the payload and without workbook output (CLI). Missing, null, and empty fallback values remain a required-field miss (`missing field(s): jurisdiction`). Explicit non-empty top-level `jurisdiction` keeps precedence. Malformed top-level values (`1`, `None`) still fail `standardized.jurisdiction must be str` even when metadata holds a valid string.

Protected DEMO fixture (`example/DEMO_HK_Standardized.json`) still strict-loads with `jurisdiction == "HK"` from metadata, identity-bearing `restructuring_expense` concept surviving export/reload. Copied metadata is a new dict. CLI `test_cli_assumptions_propagate` and `test_cli_build_reports_both_paths` still pass. Protected DEMO JSON was not edited.

---

## Task 2 — Verify generated workbooks under changed source placement

`ReferenceModelBuilder._store_count_source_placement` is a narrow test seam. Default layout still writes sources on count row 10 at consecutive period columns. The generated-workbook test monkeypatches that hook, then runs the source-bound Lululemon store fixture through reconciliation, standardization, export/reload, `build_training_workbook`, save, and copy-reload.

Moved source cells (nonadjacent columns, mixed rows): `B32`/`E40`/`H32`/`K40`/`N32` for the five admitted periods. Default `B10`–`F10` stay empty. Serialized sidecar JSON, embedded `_ComponentMap`, populated worksheet cells, and Answer-Key formulas all reference the moved cells. Current/prior dependency identities remain `(current_source, prior_source)`. Net-change formulas are `={current}-{prior}` (direction preserved); growth uses `IF(prior=0,NA(),(current-prior)/prior)`. Adjacent-column construction (`current_col-1` at the current row) and stale default coordinates are absent from those formulas. Independent cell arithmetic matches `81/56/56/44`.

Altered-layout Trainer practice cells are blank bright yellow without Notes. Answer-Key counterparts contain the linked formulas, nonempty Notes, and ordinary white/no-fill. Source cells stay populated, non-yellow, and excluded from Check totals. Workbook-wide Check: blank `568/568/0/0`; filled-correct `568/0/0/568` inverted as total/correct/incorrect/blank `568/568/0/0`; one injected wrong growth cached value yields incorrect `1` without disclosing `=999` or the answer formula. Tampering a moved source cell raises authenticated `Trusted workbook cell was modified: Store Count Analysis`. Default-layout coverage remains in `test_source_grounded_reload_workbook_and_check` (mapped cells equal `B10`–`F10`). Spreadsheet engine recalculation was not performed.

---

## Task 3 — Run regressions and correct evidence

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only (via required tests). Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Strict fallback jurisdiction string contract (object/list/numeric/boolean rejected; missing/null/empty stay required; DEMO `HK`; top-level precedence; malformed top-level rejected; no payload mutation; CLI writes no workbook on bad fallback); generated-workbook moved-source placement through ordinary `build_training_workbook` + save/reload; sidecar/embedded mapping inspection; independent cell arithmetic; Check blank/correct/incorrect + moved-source tamper; focused **217 passed**; complete `core/tests` **3202 passed / 0 failed / 3202 collected**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Augmented five-period admit `2022-01-30` keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, store practice additions **8**, store sources **5**, geo **56/74**, preserved **486**, total practice **568**, unavailable **101**, Americas `7928156`; Fast Retailing **577**; pale-yellow/frozen tests remain in the complete suite; mixed deferred documents 135/9/107/0 selections; management/revenue-relationship APIs unchanged |
| Retained, not re-measured independently | Superseded `7928256` only in audit evidence; 15 margin formulas; signed bridges |
| Historical, not this child | Prior comparable-sales child focused **1207** / required **2158**; revenue/store-relationship child focused **1193** / required **2144**; both-family-analytics child focused **1179** / required **2130**; selected-history-handoff child focused **1160** / required **2111**; previous increment of this step focused **199** / complete **3184** before the two blocking-defect repairs |
| Not claimed | Excel engine recalculation; management or revenue-relationship workbook/Check surfaces; later-audited precedence; larger-group selection; parent or Step 9 completion; G6–G9 remainder |

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_build_cli.py -q --tb=short` | 0 | **55 passed** in **8.60s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_workbook.py core/tests/test_geographic_segment_workbook.py core/tests/test_build_contract.py core/tests/test_build_cli.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_relationships.py core/tests/test_operating_kpi_facts.py core/tests/test_learner_ready_presentation.py::test_root_readme_is_practical_trainer_guide core/tests/test_trainer.py::test_cli_build_reports_both_paths core/tests/test_reference_integrity.py::test_cli_assumptions_propagate -q --tb=short` | 0 | **217 passed** in **21.08s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests -q --tb=line` | 0 | **3202 passed**, **0 failed**, **3202 collected** in **260.51s** |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints) |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/data/standardized_io.py` | `546857707bc424809f89d256b4e7924d80a923fb7e9856377bbcd630109686cf` | 24544 |
| `core/engine/reference_model.py` | `483c3e51550fea072b96cb9aa5e91917e26d707a0c81fcdfe29a4ec39455bd75` | 301701 |
| `core/tests/test_operating_kpi_workbook.py` | `cefe0d13dfe663c32fac34b8f16a88bc033c4240f0d93def39bf41ebe8523425` | 58573 |
| `core/tests/test_build_cli.py` | `5429dfc12eeb7dcc60c241c2039f4d82115bf8a1740b7bb6e24fe4e1297a54e0` | 10030 |

Unedited permitted files this child: `core/engine/component_catalog.py` SHA-256 `2b8ae30120593039e84dabd1737e28402e62aca3bc55fa8717dddc8ef8f7da8f` (196976); `core/trainer/workbook.py` SHA-256 `620d85eb758e1586b888fb46bef17590e2a99d74bac6d78456d2d1277089c5c5` (16573); `core/trainer/checker.py` SHA-256 `fe1d594328bcb23618905533777c62808debf52ce4e64a0bb4c007b7f274114e` (19801); `core/engine/build_contract.py` SHA-256 `f9be68daac881e0efa4ab37b96dfdb55a48a0b4d1b0d9e367271fc5423797cc1` (9508); `core/model/historical_expected.py` SHA-256 `7a870f579cd57c68df2c60260e683875c2b2d88ef018d8d3ff3a2dae154f8df8` (55793); `core/trainer/check_context.py` SHA-256 `73b4d18ede31136225e19f61d7016921d841a30f222090764c1c2e4a976dc767` (26518); `core/__main__.py` SHA-256 `a6864ea42c6b978bf2ccea2a4fcb10c76518502c8adc2d779672af50747a9e6a` (16007); `README.md` SHA-256 `1870364e272d23389521b508c1dda3cfa8088ee6b92aff90caf2a2c3fa2745a1` (4975).

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` is retained historical recovery evidence and was not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining selection restrictions: larger-than-two groups, general later-audited precedence, and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there and no supplied occurrence is selected or superseded. Validated store-count histories expose a learner schedule with semantic source mapping, including generated-workbook formulas that follow moved source cells; management and revenue-relationship workbook integration remain unfinished.

---

## Remaining scope

This child integrates company-operated period-end store counts into the historical Trainer/Answer-Key/Check path with semantic source identities and generated-layout proof. Management-KPI learner schedules, revenue-relationship workbook integration, other supported revenue relationships, and geography/margin/inventory/working-capital/capex relationships remain unfinished product scope. Preserve missing values and semantic discontinuities; distinguish reported, statement-derived and analyst-derived measures; infer no causality.

Beyond those remain additional supported identities, evidenced later-audited precedence, and larger-group selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41`, `.42`, `.43`, `.44`, `.45`, `.46`, `.47`, `.48` and `.49` are not reopened. This child does not certify parent acceptance, publication, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. This increment adds **8** store-count practice identities and **5** non-practice source identities on source-bound store fixtures only. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Store counts `574/655/711/767/811`, changes `None/81/56/56/44`. The accepted revenue/store and revenue/comparable-sales relationship APIs remain unchanged. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

Accepted two-occurrence selection remains: unique evidenced compatible uncontradicted documentary direction, nonmissing occurrence-specifically audited reviser, retained superseded evidence, complete-group membership and ambiguous incoming-candidate blocking. Singletons/larger groups, unknown assurance and unresolved assertions remain deferred; infer no chronology or transitive precedence. Selected store-count observations that pass those gates now produce the learner schedule; deferred observations do not.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
