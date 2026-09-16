# RESULT.md — Step 9M.2.4.1.1.1.36 Operating KPIs: reported-label provenance validation

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.36 — Operating KPIs: reported-label provenance validation  
**Work:** `0a6a4585ec404220aa91d71fc7439eb6`  
**Plan:** `fc6cf3a69853493a8a54b0550e0a98d8`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged vs this child's start). TARGET SHA-256 `ab70dd8859ba352a2387b95c55477cbc31944288c60478023d5937cf0662e91c` (23864). IMPLEMENTATION SHA-256 `49538fd17a2fd2b203b34929c06c177022f121c5468012a0c71d403b51e9ee36` (8823).  
No commit / push / sync / checkpoint / branch change. No release rewrite, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent, Operating KPIs product, or Step 9 acceptance.

Edits this child: `core/data/historical_operating_kpis.py`, `core/tests/test_operating_kpi_facts.py`, `core/tests/test_filing_json.py`, `core/tests/test_filing_reconciler.py`, `RESULT.md`.

---

## Correction of prior unsupported missing-provenance claim

The previous child listed “missing provenance” among rejected contracts. Review reproduction showed that removing **both** `source.label` and `source.note` from an otherwise valid serialized store observation still passed production filing validation. That acceptance claim was **unsupported** and is not reused.

This child requires a string `source.label` with non-whitespace text in `validate_operating_kpi_fact`. A populated `source.note` does not substitute. The shared function is already the production filing-validation and reconciliation boundary; superseded observations are validated before selection. Labels are not synthesized from metric identity.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Reported-label rejection at `validate_operating_kpi_fact`; omitted / empty / whitespace-only labels fail with and without note context; review reproduction removing both fields fails production validation; reconciliation rejects invalid filings without mutation; shared revalidation after a previously valid report; CLI rejection leaves inputs/outputs unchanged; valid labels and supplied notes retained in audit selection; model payload still omits source evidence; temporary augmented filings still select `574/655/711/767/811` with unit `stores`, labels `Total company-operated stores`, retained notes, and geo **56**; required pytest **572 passed** in **158.45s**; checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` **50/50 MATCH** |
| Retained via passing required tests this child | Rendered-page store totals `574` / `655` / `711` / `767` / `811` (not re-transcribed from PDFs this child); five-period admit `2022-01-30`; geo **74** / preserved **486** / practice **560**; unavailable **101**; **15** margin formulas; selected Americas `7928156`; superseded `7928256` only in audit evidence; Fast Retailing **577**; pale-yellow rejection; frozen compatibility authentication |
| Not claimed | Excel engine recalculation; workbook/Check/KPI analytics; parent or Step 9 completion; G6–G9 remainder |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Augmented filings and reconciliations used `TemporaryDirectory` only. Committed extracted JSON, PDFs, reconciled artifacts, releases, and examples were not rewritten.

---

## Task 1 — Enforce reported-label provenance

`require_reported_label` rejects non-string / blank / whitespace-only `source.label` with `operating-KPI {identity} missing reported label`. Filing validation maps that to `invalid_operating_kpi`. Note text is not inspected as a substitute. Selected audit payloads copy the supplied label and note; model-facing `historical_operating_kpis` still contains only metric/population/period/value/unit.

Non-KPI supplemental facts remain label-optional. Lease/share facts without labels still validate.

---

## Task 2 — Measured rejection at production boundaries

Object-level and serialized mutations: omitted, empty (`""`), and whitespace-only (`" \t "`) labels, each with populated note `Company-Operated Stores` and with note omitted.

| Case | Filing validation | Reconciliation | Inputs / output |
|---|---|---|---|
| 3×2 object-level missing/blank labels | `ValueError: missing reported label` via `select_operating_kpi_facts` | n/a (shared validator) | original good fact unchanged |
| 3×2 serialized mutations reloaded from temporary FY2025 JSON | `invalid_operating_kpi` / `missing reported label`; `report.ok` is false | `cannot reconcile filings with validation errors` | augmented JSON bytes unchanged; no reconciled dir |
| Review reproduction: remove both `label` and `note` from an otherwise valid serialized store observation | same failure | same rejection | source JSON unchanged |
| Previously valid report + subsequently blank-label KPI fact | original `report.ok` | shared `validate_operating_kpi_fact` raises `missing reported label` | original filing unchanged |
| CLI `reconcile` on temporary augmented dir after removing both fields from FY2025 store facts | `invalid_operating_kpi` / `missing reported label` / `wrote no artifacts`; exit ≠ 0 | no artifacts | dest JSON bytes unchanged; output empty |

Positive controls: valid label without note is accepted (`source_note` omitted from provenance); supplied notes survive selection; legacy absent/null KPI payloads still omit `historical_operating_kpis`; unrelated lease facts without labels still validate.

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

Geographic selected facts remain **56**; Americas revenue `7928156`. Model KPI JSON contains neither `source_label` nor `source_note`. Unit `ones` remains independently accepted on the synthetic path.

| Command | Exit | Result |
|---|---:|---|
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_operating_kpi_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py core/tests/test_historical_segment.py core/tests/test_geographic_segment_facts.py core/tests/test_geographic_segment_analysis.py core/tests/test_geographic_segment_workbook.py core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py core/tests/test_normalization.py core/tests/test_historical_v1_exit_gate.py -q` | 0 | **572 passed** in **158.45s** |
| Independent temporary augment → JSON reload → validate/reconcile/standardize/reload (forward and reversed) | 0 | Selected `574/655/711/767/811` `stores`; labels and notes retained in audit; geo **56**; Americas `7928156` |
| Protected artifacts vs checkpoints `3f6f5dde023847e3347a4c830d822614a28c81a9` and `20d93331bd3c1b3cccd72a3bf5c805453789e189` | 0 | **50/50 MATCH** (working-tree git blob SHA-1 via `hash-object`) |

Edited files this child:

| Path | SHA-256 | Bytes |
|---|---|---:|
| `core/data/historical_operating_kpis.py` | `fb711fabcdf5d02edf85733ed00b09fb0d81798b852dd03e40fcd4c88507dce6` | 5905 |
| `core/tests/test_operating_kpi_facts.py` | `10555313cd9116bf81609ddcf8edfc4d1ff8743dc0ff85454d95c07187b5f512` | 32841 |
| `core/tests/test_filing_json.py` | `82b7b26c598ee4f35a05d322f8c4a843030c66cfcddaf4c561c03b83c14b1764` | 21318 |
| `core/tests/test_filing_reconciler.py` | `452ab4583f83ca124db3f4e2e1c5991d6bcf78ee91c2df5c7eebf7f858de90ae` | 73958 |

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
