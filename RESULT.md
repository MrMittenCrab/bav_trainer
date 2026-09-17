# RESULT.md — Step 9M.2.4.1.1.1.43 Operating KPIs: documentary revision links

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.43 — Operating KPIs — Documentary revision links  
**Work:** `78a0392fcae9437dbd35dc0cc7266a58`  
**Plan:** `6946a937743b49c899466d46729a413b`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** `20260916-075534-000000006`  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `bf84aa15c3adaafa6654a94deb22d1ebd64b8344b4c87f716bf79ef66993264e` (9788).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, workbook/Check, canonical history selection, or Step 9 acceptance.

Edits this child: `core/ingestion/management_kpi.py`, `core/ingestion/management_kpi_reconciliation.py`, `core/tests/test_management_kpi_admission.py`, `core/tests/test_management_kpi_reconciliation.py`, `core/tests/test_management_kpi_identity.py`, `core/tests/test_filing_cli.py`, and `RESULT.md`.

No required plan change.

Prior work `5184ff82785d42a89f051ce144ee4290` (Step 9M.2.4.1.1.1.42 presentation relationships) is accepted by Review. Preserved relationship logs record **232** focused and **911** required passes; those counts are historical and are not this child's fresh results. `.git/autocycle/latest-implementation` remains stale (`HEAD: cd3a131359857e4268a2640b8757fa4fceae9ab8`, log `cursor-20260916-204023-91441.log`) and was not rewritten.

Ordinary admission now validates optional occurrence-bound revision assertions on the two supported families. Reconciliation serializes separate directed revision diagnostics. Supplied mixed inputs remain unknown on presentation, assurance, and revision; comparable **0**, not-comparable **22**, unresolved **6**, outside-scope **107**; 24 incompatible pairs; zero revision links. Canonical selection remains deferred.

---

## Task 1 — Revision assertion contract

Supported `reported_kpis` entries may optionally supply a nested `revision` object:

```text
revision: {
  revises: {
    metric_id, period, source_file, page_reference,   # required
    definition_id, unit, basis, comparison, section   # optional; if nonblank must match
  },
  evidence: string,
  source: { section, page_reference, source_file?, physical_page_mapping? }
}
```

`revises.source_file` is the **target occurrence's bound PDF**, not an extraction JSON filename. `page_reference` plus documentary identity (`metric_id` + `period` + bound PDF) is the occurrence discriminator. Values, input order, and filenames alone do not identify a target. Unexpected fields, including `value`, fail closed.

The assertion source must bind to the **revising** observation's source document. A non-empty `revises` object requires nonblank documentary evidence and that bound source. Absent, null, empty, or whitespace-only evidence leaves revision unresolved. Malformed types, unbound `source_file`, asserted physical-page mapping, contradictory top-level `revises`, self-referential unique names, and revision targets on unsupported observations fail through ordinary parse/admission.

Missing targets emit `revision_target_missing`; two or more matches emit `revision_target_ambiguous`. Neither diagnostic selects a target. Repeated same-document copies that share a discriminator remain ambiguous.

---

## Task 2 — Directed revision diagnostics

Reconciliation serializes a separate `revision_links` array. Each link retains reviser and revised occurrence references (locator + occurrence identity), named target fields, evidence, and printed source. A link is **recognized** only when documentary binding succeeds and existing same-period definition/scope/basis/unit/calendar gates pass. Missing required comparison evidence is unresolved; evidenced dimension conflicts are incompatible. Missing values do not create or block a link.

Restated/prior roles, assurance, equal values, filing dates, and filenames do not invent revision links. Reciprocal assertions add `reciprocal_revision` and cyclic assertions add `cyclic_revision` without choosing precedence, winners, or superseded observations. Transitive links are not inferred; peers do not inherit evidence.

Presentation 15-combination table, pair membership, value outcomes, and occurrence presentation/assurance evidence are unchanged. Observations remain `admitted_unreconciled` and excluded from `StandardizedFinancials`. Canonical selection stays deferred.

---

## Task 3 — Measured verification

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Mixed reconciliations used `TemporaryDirectory` copies only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

Independent mixed-directory load of supplied extracted inputs:

- 4 statement filings (FY2022–FY2025) + 4 management documents
- 135 reported observations (`29/36/37/33`)
- 9 definitions
- 107 market-table store observations
- 3 nonhistorical targets
- status `admitted_unreconciled`; canonical selection `deferred`
- assessments: **135** items covering every reported observation; **28** supported, **107** outside_scope, **0** unsupported_variant
- comparability: comparable **0**, not_comparable **22**, unresolved **6**, outside_scope **107**
- reconciliation: pair_count **24**; agreeing_duplicate **0**; conflicting_candidate **0**; incompatible **24**; unresolved pairs **0**; singleton **6**; unsupported_variant **0**; outside_scope **107**
- supplied presentation/assurance/revision: all observations unknown; `revision_links` **[]**; counts recognized/unresolved/incompatible **0/0/0**
- annual-only vs mixed: canonical standardized (optional handoffs stripped), conflicts, and statement provenance match
- mixed `historical_operating_kpis is None`; annual-only admission artifact absent (`None`)
- extracted JSON bytes immutable after the exercise

CLI `validate-source` / `reconcile` against temporary mixed and annual-only copies (admit `2022-01-30`): mixed writes `management_kpi_admission.json` with 135 assessment items, supported_count **28**, pair_count **24**, comparability 0/22/6/107, and zero revision links; annual-only writes only `standardized.json` / `provenance.json` / `conflicts.json`. Mixed validate-source: `validated 4 filing(s)` and `management-kpi documents: 4`, exit 0.

Temporary fixtures exercised both families with explicit valid links, absent evidence, malformed/unbound/self-referential assertions, missing/ambiguous targets, JSON-filename targets, restated/prior non-inference, agreeing/conflicting/missing values, definition/calendar/period/qualifier gates, three-peer non-transitivity, reciprocal and cyclic diagnostics, renamed/reordered inputs, and CLI serialization. Revision direction remained documentary.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Mixed directory 4+4; 135 reported (`29/36/37/33`), 9 definitions, 3 nonhistorical targets; assessments 135/28/107/0; comparability **0/22/6/107**; reconciliation pairs **24** all `incompatible`, agreeing/conflicting **0/0**, singletons **6**, outside-scope coverage **107**; supplied presentation/assurance/revision remain unknown; `revision_links` empty; annual-only vs mixed canonical standardized/conflicts/statement-provenance match; CLI mixed admission includes revision_links array and annual-only omits the artifact; focused pytest **273 passed**; required suite **952 passed**, **0 failed**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH**; eight extracted JSON blob SHA-1 values unchanged vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` |
| Fresh via required suite this child | Mixed + temporary store prep keeps counts `574/655/711/767/811`, changes `None/81/56/56/44`, growth within `1e-12`, geo **56**, Americas `7928156`; five-period admit `2022-01-30`; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Retained, not re-measured independently | Geo **74** additions / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; superseded `7928256` only in audit evidence |
| Historical, not this child | Work `5184ff82785d42a89f051ce144ee4290` focused **232** / required **911** from `cursor-20260916-205703-94911.log` (SHA-256 `5be712cea1d31c8696e171b05a9b4f011b54ea46f1549dfbe16297426629cc70`) and Review `review-20260917-100524-1937.log` (SHA-256 `8d2a110f379b5bdcb941a18c95e55cd0db3c831f8245ac91c4bfaddbe519393c`); older 175/854 and 117/796 remain historical |
| Not claimed | Excel engine recalculation; workbook/Check/KPI learner surface; canonical management-history selection; later-audited precedence; parent or Step 9 completion; G6–G9 remainder |

No freshly encountered required-suite failures.

`.git/autocycle/latest-implementation` SHA-256 `25ad07bd9a3f7f39ee52a6486a93456c6606efebfb2431d604ac8a3c48e98bd5` (183) still points at `cd3a131359857e4268a2640b8757fa4fceae9ab8` / `cursor-20260916-204023-91441.log` and was **not** manually rewritten. Controller refresh remains pending.

---

## Commands

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_identity.py core/tests/test_management_kpi_admission.py core/tests/test_filing_cli.py -q --tb=short` | 0 | **273 passed** in **7.92s** |
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_management_kpi_reconciliation.py core/tests/test_management_kpi_admission.py core/tests/test_operating_kpi_analysis.py core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py core/tests/test_management_kpi_identity.py -q` | 0 | **952 passed** in **175.24s** |
| Independent mixed vs annual-only Python load/reconcile (TemporaryDirectory annual copy; mixed from supplied extracted dir; admit `2022-01-30`) | 0 | 4+4 documents; 135 / 9 / 3 nonhistorical; assessments 135 (28 supported / 107 outside / 0 variant); comparability **0/22/6/107**; reconciliation **24/0/0/24/0/6/0/107**; revision_links empty 0/0/0; std/conflicts/statement-provenance match; extracted JSON unchanged |
| Independent CLI `validate-source` + `reconcile --admit-period 2022-01-30` on TemporaryDirectory mixed and annual-only copies | 0 | mixed validate-source: 4 filings + 4 management-kpi documents; mixed writes `management_kpi_admission.json` (reported 135, assessments 135/supported 28, comparability 0/22/6/107, pair_count 24, revision_links 0); annual-only omits that artifact; extracted JSON immutable |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object` vs `rev-parse <commit>:<path>`; example/release/benchmark `xlsx`/`json`/`pdf` plus release `README.md` present at those checkpoints). Four management-KPI JSONs are extra vs those checkpoints and are checked separately below. |
| Eight extracted JSON vs `5e3ef5cfdbfebcf5871dd7e75fad81654d669151` blob SHA-1 | 0 | eight files **UNCHANGED** (4 annual + 4 management-KPI) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/ingestion/management_kpi.py` | `3657a02fd9847214be875c22379557bbd2e1b1ff2cbfcb63b4f7ac3d760e75ea` | 63954 |
| `core/ingestion/management_kpi_reconciliation.py` | `4f8cd4fcbeab065a19de54f03381d4c81c2076a59b85e53f123b4cab4bb6a2d9` | 27547 |
| `core/tests/test_management_kpi_admission.py` | `06f6bf6a57ac000c192979291041a3ea1bd5c5885cc5ad3d7d0a80d16189fbed` | 54424 |
| `core/tests/test_management_kpi_reconciliation.py` | `957be1f40f9c1ede326d41f9ea534b3f7976ef95214efa7df7ccf2e1c2136d5a` | 84134 |
| `core/tests/test_management_kpi_identity.py` | `31e2f75cbd4585d0cf1e6b404600b8ab50549d38c2132138d193e5240e583456` | 54085 |
| `core/tests/test_filing_cli.py` | `515718c957da0e2d0e3495e0c314d54ff7656ae802fbe94980b9cebfc48cee7c` | 13687 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Five snapshot-matched production/test identities retained from `edit_replay_counts`: `core/model/capex.py`, `core/model/line_resolver.py`, `core/tests/test_capex.py`, `core/tests/test_line_resolver.py`, `core/tests/test_lululemon_benchmark.py`. Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

Remaining admission restrictions: later-audited precedence and physical-page mapping stay unresolved; supplied documents still lack presentation/assurance/revision evidence, so those dimensions remain unknown there. Admitted observations remain audit-only and excluded from `StandardizedFinancials`. Canonical value selection is still deferred.

---

## Remaining scope

Beyond this increment remain additional supported identities, evidenced later-audited precedence, superseded observations and canonical selection; unavailable assurance/presentation/revision evidence in supplied documents remains unresolved. Then extend validated `StandardizedFinancials` histories/round trips, Operating KPI analytics and supported revenue/geography/margin/inventory/working-capital/capex relationships, followed by ordinary BAV/Trainer/Answer-Key/Check integration. Preserve missing values and definition/calendar discontinuities; distinguish reported/statement-derived/analyst-derived measures; infer no causality. Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED. Completed admission, `.37`, `.39`, `.40`, `.41` and `.42` are not reopened. This child does not certify parent acceptance, publication, workbook integration, or Step 9 completion.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.
