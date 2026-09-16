# RESULT.md — Step 9M.2.4.1.1.1.36 Operating KPIs: reject serialized non-string provenance labels

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.36 — Operating KPIs: reject serialized non-string provenance labels  
**Work:** `0a6a4585ec404220aa91d71fc7439eb6`  
**Plan:** `f88e276677ac468fb5d6ef063a35d003`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `cb9293a890d71eb71dd3d138a17a30532f5a0688da7fb9b245a7ce2daac6806b` (8932).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/data/historical_operating_kpis.py`, `core/ingestion/filing_json.py`, `core/tests/test_operating_kpi_facts.py`, `core/tests/test_filing_json.py`, `core/tests/test_filing_reconciler.py`, `core/tests/test_filing_cli.py`, `RESULT.md`.

---

## Correction of prior incomplete string-label acceptance claim

The previous child claimed string-label acceptance after rejecting omitted / empty / whitespace-only labels. That claim was **incomplete**. Production `_parse_source` still did `str(payload.get("label") or "")`, so serialized non-string KPI labels (`123`, `true`, nonempty objects/arrays) became accepted provenance strings and passed filing validation and reconciliation.

This child rejects non-string operating-KPI `source.label` values at supplemental JSON parsing, before `_parse_source` can stringify them, using `is_operating_kpi_fact_type` and `reject_non_string_reported_label`. `None` / omitted / empty / whitespace-only labels remain object-level validation defects. Populated notes still cannot substitute.

Parser rejection is distinct from validation-report rejection: `load_extracted_filing` raises `ValueError` (`missing reported label`) and creates no accepted filing; omitted/null/blank labels still load and fail as `invalid_operating_kpi`.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Pre-coercion parser rejection of serialized KPI labels `123`, `1.5`, `0`, `true`, `false`, nonempty/empty objects and nonempty/empty arrays, with and without notes, on `note_facts` and `share_facts`; in-memory non-string labels fail shared validation including superseded observations after a previously valid report; CLI parse path prints `error:` without `invalid_operating_kpi` or `wrote no artifacts`; blank/null/omitted labels still fail as validation-report `invalid_operating_kpi`; non-KPI numeric labels still coerce (`123`, statement `99`); temporary augmented filings still select `574/655/711/767/811` with unit `stores`, labels `Total company-operated stores`, retained notes, and geo **56**; required pytest **678 passed** in **163.94s**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH** |
| Retained via passing required tests this child | Rendered-page store totals `574` / `655` / `711` / `767` / `811` (not re-transcribed from PDFs this child); five-period admit `2022-01-30`; geo **74** / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; selected Americas `7928156`; superseded `7928256` only in audit evidence; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Not claimed | Excel engine recalculation; workbook/Check/KPI analytics; parent or Step 9 completion; G6–G9 remainder |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Augmented filings and reconciliations used `TemporaryDirectory` only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Task 1 — Reject non-string labels before coercion

`reject_non_string_reported_label` leaves `None` and strings to object-level `require_reported_label`. `_parse_supplemental` applies the guard on KPI `source.label` before `_parse_source`. Errors identify the KPI reported-label defect (`operating-KPI {identity} missing reported label`). Notes are not inspected as a substitute.

Non-KPI supplemental facts and statement-row sources keep existing coercion. Selected audit payloads still copy supplied string labels and notes; model-facing `historical_operating_kpis` still contains only metric/population/period/value/unit.

---

## Task 2 — Measured parser vs validation-report rejection

Serialized non-string labels: `123`, `1.5`, `0`, `true`, `false`, `{"x": 1}`, `{}`, `[1]`, `[]`, each with populated note `Company-Operated Stores` and with note omitted.

| Case | Production load | Validation / reconcile | Inputs / output |
|---|---|---|---|
| 9×2 serialized KPI mutations (note_facts and share_facts) | `ValueError: missing reported label` from `load_extracted_filing`; no `ExtractedFiling`; not `invalid_operating_kpi` | never reached | mutated JSON bytes unchanged; no reconciled dir |
| 9×2 object-level non-string labels | n/a (in-memory) | `select_operating_kpi_facts` / `validate_operating_kpi_fact` raise `missing reported label` | original good fact unchanged |
| Previously valid report + superseded PRIOR_PRESENTATION fact with non-string label | original `report.ok` | shared reconcile revalidation raises `missing reported label` | original filing unchanged |
| CLI `reconcile` / `validate-source` on serialized `123` | `error: ... missing reported label`; exit ≠ 0 | no validation-report path (`invalid_operating_kpi` absent; `wrote no artifacts` absent) | dest JSON bytes unchanged; output empty |
| Omitted / null / empty / whitespace labels (retained) | load succeeds | `invalid_operating_kpi` / `missing reported label`; reconcile `cannot reconcile filings with validation errors` | source JSON unchanged |
| Review reproduction: remove both `label` and `note` | load succeeds | same validation-report failure | source JSON unchanged |
| Non-KPI `lease_interest_expense` label `123` and statement-row label `99` | load succeeds; coerced to `"123"` / `"99"` | `report.ok` | labels remain coerced strings |

Positive controls: valid label/note text preserved exactly; valid label without note accepted; legacy absent/null KPI payloads still omit `historical_operating_kpis`; unrelated lease facts without labels still validate.

---

## Task 3 — Retained handoff and verification commands

Temporary source-grounded augmented filings, both filing orders, after validate / reconcile / standardize / standardized JSON reload:

| Period | Selected count | Unit | Label | Note |
|---|---:|---|---|---|
| 2022-01-30 | 574 | stores | Total company-operated stores | Company-Operated Stores |
| 2023-01-29 | 655 | stores | Total company-operated stores | Number of company-operated stores by market |
| 2024-01-28 | 711 | stores | Total company-operated stores | Number of company-operated stores by market |
| 2025-02-02 | 767 | stores | Total company-operated stores | Number of company-operated stores by market |
| 2026-02-01 | 811 | stores | Total company-operated stores | Number of company-operated stores by market |

Geographic selected facts remain **56**; Americas revenue `7928156`. Model KPI JSON contains neither `source_label` nor `source_note`. Unit `ones` remains independently accepted on the synthetic path. Independent parser probe of FY2025 serialized label `123` raised `ValueError` before validation; blank labels still produced `invalid_operating_kpi`. Committed extracted JSON unchanged.

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **678 passed** in **163.94s** |
| Independent temporary augment → JSON reload → validate/reconcile/standardize/reload (forward and reversed) | 0 | Selected `574/655/711/767/811` `stores`; labels and notes retained in audit; geo **56**; Americas `7928156` |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object`) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/data/historical_operating_kpis.py` | `7fffe018162cb65a5f4b5e6cfd31aa06fbf0639e68693ff3dca0dad74ea1c198` | 6230 |
| `core/ingestion/filing_json.py` | `dc0266f8fb441d0eb1cb28d1bcb9ad9a05b86522432dc1e8be45e5d59ec2aff0` | 12518 |
| `core/tests/test_operating_kpi_facts.py` | `0a95bcffbdf69782bbc69aad4ea97e6dafc051ad4d5365158e71e96f0016191c` | 37644 |
| `core/tests/test_filing_json.py` | `dec03d23dfa9ba896f1ad6bd22f07ef42675b8c0e2f55eb5256c8ff235dc0bbc` | 24027 |
| `core/tests/test_filing_reconciler.py` | `dbfc192bbbd90d213dcda7487dc09e6185bce6ec14b38c01e7678b2ee7420f91` | 76804 |
| `core/tests/test_filing_cli.py` | `265101ad7bd514ba33660fdbdd4641b6b565ca3abde681aa97d702323c3d74ca` | 7811 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining scope

KPI analytics/workbook/Check; other source-supported KPIs; Normalization Judgment + Earnings Normalization; G6 missing opening BS; G7 lease maturity/remaining notes; G8 deferral; G9 standalone interest completeness; segment assets/capex/significant expenses/D&A; benchmark publication; TARGET Step 9 exit gates. Analytical focus gate retained. Independent M&A Net Debt, Complete NOPAT/RNOA, and forecasting remain deferred.

No plan rewrite.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; geographic additions **74** reported separately; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Selected Americas revenue `7928156` remains stable under prior-presentation mutation; superseded `7928256` remains exclusively in audit evidence. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`. This child's tests do not close parent acceptance.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
