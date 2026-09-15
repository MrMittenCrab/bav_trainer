# RESULT.md — Step 9M.2.4.1.1.1.31 Lululemon segment-disclosure readiness assessment

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.31 — Lululemon segment-disclosure readiness assessment  
**Work:** `dee5e0e04a9745e5bfc0423677563a4d`  
**Plan:** `1f524c22a0db4369a587dda04f0b206c`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `ee7afcf5b0f4b07e2ceda8f42e756da277b96af594b8a3e1e1fca948df6cc0f3` (6966).  
No commit / push / sync / checkpoint / branch change. No note extraction, canonical regeneration, production-code edits, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent or Step 9 acceptance. G7 remains **OPEN**.

**Advisory correction (preceding RESULT 9M.2.4.1.1.1.30):** the measured Lululemon Trainer SHA-256 is `4e06ce78957a291857d9db074113f071021d057234ff0f7376afafbce4b76904` (34670), not the previously recorded `2e23f3b6d6fdba9b5f101d983a29f0854c9406474c92305ee06ca452e45afa6e`. Comparative admission remains accepted. Answer Key / map / availability / reconciled hashes below match the five-period canonical set already accepted.

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | PDF SHA-256 vs JSON `source_sha256`; independent inspection of cited PDF pages (native extract FY2022/FY2023; Identity-H Calibri subset decode FY2024/FY2025); `note_facts` counts; supplemental-fact / reconciler / standardizer contract inspection; before/after protected-artifact hashes |
| Not rerun | `pytest core/tests` 1253; production `build` / `reconcile`; workbook Check / spreadsheet recalculation |

---

## Task 1 — Documentary segment coverage

### Sources inspected

| Filing | Path | SHA-256 | Bytes | JSON `period_end` | PDF pages |
|---|---|---|---:|---|---:|
| FY2022 AR | `benchmark/lululemon/source/LULU_FY2022_Annual_Report.pdf` | `b344d1e7a710259fa06f88773dee0b3827334820ce2b881fe6b95ca2ae275e4e` | 4913067 | 2023-01-29 | 92 |
| FY2023 AR | `benchmark/lululemon/source/LULU_FY2023_Annual_Report.pdf` | `cd47ea251d608d06a3e58b5d782f2d41d5a231a994d2f7993267a430cb13c0f1` | 5848446 | 2024-01-28 | 96 |
| FY2024 AR | `benchmark/lululemon/source/LULU_FY2024_Annual_Report.pdf` | `9268fd530db162babdd1ec4363cf388ebce57125d83b7e097aba6f98ba0ca7ec` | 5953217 | 2025-02-02 | 92 |
| FY2025 AR | `benchmark/lululemon/source/LULU_FY2025_Annual_Report.pdf` | `82e00f900cc912a7d79596409594156b7779c3a193783ea8fecf87bc013c71cc` | 6590658 | 2026-02-01 | 92 |

JSON `source_sha256` on all four extracted filings matches the PDF hashes. Units on all four filings: **USD thousands**. Company fiscal years end on the Sunday closest to 31 January; fiscal 2024 (ended 2025-02-02) is a **53-week** year.

Extracted filing JSONs (`benchmark/lululemon/extracted/LULU_FY2022.json` … `LULU_FY2025.json`): `note_facts: []` on all four; `share_facts` populated (6 per filing). Reconciled provenance `note_facts: []`. `standardized.json` `historical_lease` is `null`. Canonical axis: `2022-01-30, 2023-01-29, 2024-01-28, 2025-02-02, 2026-02-01`.

### Reportable-segment definition change (Q4 2023)

FY2023 Note 23 (PDF p84 / printed **78**): during Q4 2023 the CODM shifted from selling **channel** to **regional market**. As of 2024-01-28 the Company reports three segments: **Americas**, **China Mainland**, and **Rest of World** (APAC + EMEA combined). Capital expenditures and assets by segment are **not** reported because they are not reviewed by the CODM. Prior periods in that note were **restated** to the new segments.

FY2022 Note 22 (PDF p78 / printed **74**) is the last original channel-era reportable presentation: **company-operated stores**, **direct to consumer**, remainder in **Other** (outlets, wholesale, license/supply, recommerce, temporary locations, lululemon Studio).

Channel, country, product-category, and store-KPI tables are **not** the reportable-segment P&L:

| Surface | What it is | Not to treat as |
|---|---|---|
| Topic 280 segmented information | Reportable segments + reconciling items to consolidated income from operations | — |
| Net revenue by geography (US / Canada / PRC / other) | ASC 280 entity-wide geographic disaggregation | Reportable segments. **China Mainland ≠ PRC** (PRC includes HK SAR, Taiwan, Macau SAR) |
| Net revenue by channel (stores / e-commerce / other) | Post-reorganization **disaggregation only** | Reportable-segment profit (no channel IFOP after FY2022 original) |
| Women's / men's / other product | Category disaggregation | Segments |
| Store counts, sales per square foot | MD&A / business-description KPIs | Segment economics |
| Long-lived assets by country | Entity-wide geographic assets (PPE + ROU) | Segment assets (explicitly not CODM-reviewed) |

Mexico (FY2025 Note 3, PDF p63 / printed **57**): before the 10 Sep 2024 Mexico acquisition, wholesale to the Mexico licensee was disclosed inside **Canada**. After acquisition, Mexico is a country line inside Americas. **Americas totals remain the reportable-segment revenue**; do not treat Canada/Mexico country lines as segments.

### Representative anchors (USD thousands)

**A. Channel-era reportable segments — FY2022 Note 22, PDF p78 / printed 74** (original, not restated to geography)

| Period end | Company-operated stores rev / IFOP | Direct to consumer rev / IFOP | Other rev / IFOP | Consolidated revenue / IFOP |
|---|---|---|---|---|
| 2023-01-29 (2022) | 3,648,127 / 991,067 | 3,699,791 / 1,562,538 | 762,600 / 107,083 | 8,110,518 / 1,328,408 |
| 2022-01-30 (2021) | 2,821,497 / 727,735 | 2,777,944 / 1,216,496 | 657,176 / 77,283 | 6,256,617 / 1,333,355 |

Same note also discloses channel **capex** and **D&A**. Those channel capex/D&A series **stop** after this presentation.

**B. Geographic reportable segments — later-audited**

FY2023 Note 23 restatement (PDF p84 / printed 78), including the only geographic presentation of **2022-01-30**:

| Period end | Americas rev / IFOP | China Mainland rev / IFOP | Rest of World rev / IFOP | Consolidated revenue |
|---|---|---|---|---|
| 2024-01-28 (2023) | 7,631,647 / 2,937,184 | 963,760 / 337,316 | 1,023,871 / 201,832 | 9,619,278 |
| 2023-01-29 (2022) | 6,817,454 / 2,503,740 | 576,503 / 196,865 | 716,561 / 103,204 | 8,110,518 |
| 2022-01-30 (2021) | 5,299,906 / 1,867,016 | 434,261 / 167,318 | 522,450 / 67,674 | 6,256,617 |

FY2025 Note 24 (PDF p79–81 / printed **73–75**), later-audited 2023–2025 with ASU 2023-07 significant expenses:

| Period end | Americas rev / IFOP | China Mainland rev / IFOP | Rest of World rev / IFOP | Consolidated revenue / IFOP |
|---|---|---|---|---|
| 2026-02-01 (2025) | 7,847,044 / 2,560,658 | 1,754,799 / 701,123 | 1,500,757 / 345,901 | 11,102,600 / 2,210,615 |
| 2025-02-02 (2024) | 7,928,156 / 3,015,557 | 1,361,337 / 509,859 | 1,298,633 / 314,946 | 10,588,126 / 2,505,697 |
| 2024-01-28 (2023) | 7,631,647 / 2,937,184 | 963,760 / 337,316 | 1,023,871 / 201,832 | 9,619,278 / 2,132,676 |

FY2024 Note 23 (PDF p79–80 / printed **73–74**) restates **2023-01-29** with the same geographic revenue/IFOP as FY2023 and adds product costs, other cost of sales, and SG&A by segment (ASU 2023-07 adopted in 2024; FY2024 p63 / printed 57). FY2025 does **not** repeat 2023-01-29. FY2024/FY2025 do **not** repeat 2022-01-30.

Reconciliation check (FY2025 current): Americas+China Mainland+ROW IFOP 3,607,682 − corporate 1,397,067 = consolidated IFOP 2,210,615. Segment revenue sums to consolidated with corporate revenue **0**.

**C. China Mainland vs PRC (do not substitute)**

FY2022 Note 23 geography (PDF p79 / printed 75) PRC 2022 = 681,633. FY2023 Note 24 (PDF p85 / printed 79) splits 2022 as China Mainland 576,503 + HK/TW/Macau 105,130 = 681,633.

**D. Channel disaggregation after reorganization (revenue only)**

FY2025 Note 3 (PDF p63 / printed 57): company-operated stores / e-commerce / other channels 5,049,744 / 4,918,697 / 1,134,159 (2026-02-01); 5,007,872 / 4,570,446 / 1,009,808 (2025-02-02); 4,410,956 / 4,311,110 / 897,212 (2024-01-28). No channel IFOP in this table.

**E. Store KPIs (G7 remainder — not this module)**

FY2022 Note 1 (PDF p55): 655 / 574 / 521 company-operated stores at 2023-01-29 / 2022-01-30 / 2021-01-31. FY2023 business description (PDF p11 / printed 5): sales per square foot 1,609 / 1,580 / 1,443 for 2023 / 2022 / 2021; store counts by market. Lease maturity detail remains unextracted. Not used below.

### Five-period coverage matrix (geographic reportable segments)

| Axis date | Revenue | Segment IFOP | Product costs / other COS / SG&A | Segment D&A | Segment assets | Segment capex | IFOP reconciling items | Later-audited source |
|---|---|---|---|---|---|---|---|---|
| 2022-01-30 | yes | yes | **no** | yes | **no** (not CODM-reviewed) | **no** | yes | FY2023 Note 23 restatement only |
| 2023-01-29 | yes | yes | yes (FY2024 ASU restatement) | yes | **no** | **no** | yes | FY2024 Note 23 (later than FY2023 for this date) |
| 2024-01-28 | yes | yes | yes | yes | **no** | **no** | yes | FY2025 Note 24 |
| 2025-02-02 | yes | yes | yes | yes | **no** | **no** | yes | FY2025 Note 24 |
| 2026-02-01 | yes | yes | yes | yes | **no** | **no** | yes | FY2025 Note 24 current |

Missing / noncomparable (not inferred):

- Segment **assets** and post-reorganization **capex**: filings state they are not reviewed by the CODM.
- Channel **IFOP** after the FY2022 original note: not restated; do not carry FY2022 channel profit onto later years.
- 2022-01-30 **significant expenses** (product costs / other COS / SG&A): not in the FY2023 restatement; FY2024/FY2025 do not include that year.
- 2021-01-31: still **no selected BS**; outside the admitted axis (G6). No segment module may invent that year.
- 53-week FY2024: annual **reported** amounts are disclosed; week-adjusted annual segment totals are **not** disclosed. Do not infer them. YoY involving 2025-02-02 is mixed 53/52-week.
- Do not infer segment costs from consolidated COGS/SG&A minus something else.

---

## Task 2 — Smallest supported analytical handoff

### What the existing contract can preserve

`SupplementalFact` (`core/data/filing.py`): `fact_type`, `period`, `value`, `status` (`reported`|`derived`), `source` (`page`, `statement`, `note`, `label`), optional `derivation`. No `presentation_role`, no segment identity, no definition-vintage, no unit override.

Parser (`core/ingestion/filing_json.py`) accepts any nonempty `fact_type` string. Validator requires a positive source page. Reconciler keeps **all** note observations and flags `cross_filing_supplemental_disagreement` when the same `(kind, fact_type, period)` disagrees; it does **not** apply `later_audited_presentation` selection used for statement rows. Provenance serializes `note_facts` without promoting them onto `StandardizedFinancials` statement lines (`test_note_facts_not_promoted`). The only `note_facts` consumer in standardization is complete-axis `lease_interest_expense` → `historical_lease`. There is **no** segment type, payload, or production module in `core/`.

Therefore namespaced `fact_type`s (e.g. `segment_geo_net_revenue_americas`) could be *parsed* today, but they cannot become model-facing schedules without a new optional standardizer payload analogous to `historical_lease`, and they cannot encode restatement role or segment identity as first-class fields.

### Proposed smallest useful module (not implemented this step)

**Name:** geographic reportable-segment contribution P&L (Americas / China Mainland / Rest of World).

**Supported facts (USD thousands, `status=reported`, later-audited where overlapping):**

- `segment_geo_net_revenue_{americas,china_mainland,rest_of_world}` for all five axis dates.
- `segment_geo_income_from_operations_{americas,china_mainland,rest_of_world}` for all five axis dates.
- Explicit unallocated / corporate reconciling items that the notes already use to bridge segment IFOP to consolidated IFOP (corporate expense total; plus period-specific disclosed items such as Studio obsolescence, impairment/restructuring, amortization of intangibles, acquisition-related, gain on disposal — only when the cited note shows them).
- Source links: FY2025 Note 24 PDF p79–81 / printed 73–75 for 2024-01-28…2026-02-01; FY2024 Note 23 PDF p79–80 / printed 73–74 for 2023-01-29 (and its ASU expense lines if a later child adds them); FY2023 Note 23 PDF p84 / printed 78 for 2022-01-30 only.
- Reconciliation checks: Σ segment revenue = consolidated IS revenue; Σ segment IFOP + disclosed reconciling items = consolidated IS income from operations. Fail closed on mismatch, missing segment, mixed channel/geo fact_types, or empty `note_facts`.

**Gates (fail closed / Source unavailable — do not infer):**

- Segment assets, segment capex.
- Channel IFOP / channel capex as if they were current reportable segments.
- 2022-01-30 product costs / other COS / SG&A by segment.
- PRC geography as a substitute for China Mainland.
- 2021-01-31.
- Week-adjusted 53-week amounts.
- Any cost allocation not printed in the segment note.

**Optional later submodule (not this smallest module):** ASU 2023-07 significant expenses and segment D&A for 2023-01-29…2026-02-01 only, gated unavailable at 2022-01-30.

**Learner surface (proposal only; no new exercise counts this step):**

- Populated: extracted segment source facts and existing consolidated IS totals.
- Practice (blank yellow, no Trainer Notes): segment revenue share; segment operating margin (IFOP / segment revenue); reconciling bridge that sums to consolidated IFOP.
- Answer Key: formula + concise Note that segments are geographic (ROW = APAC+EMEA combined), corporate is unallocated, channel tables are not this schedule, China Mainland ≠ PRC, FY2024 had 53 weeks, and Q4 2023 restated the framework.
- Check: existing workbook-wide non-disclosing Check once identities exist.

**Contract / extraction dependencies (concrete, not waived):**

1. G7: all four filing JSONs still have empty `note_facts` — no executable module until extraction (forbidden in this child).
2. `SupplementalFact` lacks segment identity and `presentation_role`; supplemental conflicts are not later-audited-selected.
3. No `HistoricalSegmentData` (or equivalent) path from `note_facts` into `StandardizedFinancials`.
4. Plan must add those contract fields or an explicit namespaced-fact_type convention plus a fail-closed standardizer payload before implementation. This RESULT does not rewrite the plan.

Store KPIs and lease maturity remain G7-pending and outside this handoff.

---

## Task 3 — Disposition

**Source readiness:** the four supplied annual reports **do** support a bounded historical geographic segment-economics module for **revenue, segmented income from operations, and explicit IFOP reconciling items** on the admitted five-period axis, with 2022-01-30 sourced only from the FY2023 restatement. They do **not** support segment assets, post-reorganization segment capex, five-period channel profit, or 2022-01-30 significant-expense lines.

**Unresolved dependencies:** G7 empty `note_facts`; missing first-class segment identity / presentation_role / later-audited supplemental selection; no standardizer segment payload. Remaining G7 store KPIs and lease maturity. G6 2021-01-31 BS. G8 deferral. G9 standalone interest. TARGET Step 9 exit gates.

**Remaining G7 scope (not closed):** extraction of note facts; store KPIs; lease maturity detail.

No production artifacts were modified. No prospective ID reserved. No parent or Step 9 acceptance.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| SHA-256 of four source PDFs | 0 | match JSON `source_sha256` and BASELINE.md |
| JSON `note_facts` length on four extracted filings | 0 | **0 / 0 / 0 / 0** |
| Independent FY2022 Note 22 / FY2023 Note 23 native text extract | 0 | channel vs geographic reorganization; anchors above |
| Independent FY2024 Note 23 / FY2025 Note 24 Calibri-subset decode | 0 | geographic P&L + ASU expenses; printed 73–75 |
| Inspect `SupplementalFact`, reconciler supplemental grouping, `test_note_facts_not_promoted`, `historical_lease` | 0 | contract gaps as Task 2 |
| Protected-artifact SHA-256 before RESULT write | 0 | table below |
| `pytest core/tests` | — | **not rerun** (prior 1253 retained, not this child's proof) |

### Protected-artifact hashes (unchanged this child)

**Lululemon (five-period canonical, including Trainer advisory correction):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `4e06ce78957a291857d9db074113f071021d057234ff0f7376afafbce4b76904` | 34670 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` | 119554 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `cc584a7bca130e0d52472a7b186bca00954e6eb98d2194418eb3e1c973c1e09f` | 561320 |
| `release/lululemon/availability.json` | `12e3b90aa640b76839e91f388b494644d686dfd705910a0d5541b2e28fbcd8a0` | 15691 |
| `benchmark/lululemon/reconciled/standardized.json` | `a3568c29e883c8ba57af23da7b4286641a3c5f929af311e2e9593c5f63ea2287` | 25011 |
| `benchmark/lululemon/reconciled/provenance.json` | `6799371215e02c888b3a5f687637b38dba4840bd1548cb1860a253f7a699cb12` | 699438 |
| `benchmark/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

**Fast Retailing (byte-identical, 577 identities, 0 unavailable displays):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `8a3f4f0c0e8bebb84317ead5a2e1c29679e8b70cdf58c211fe50ccbab04f5a23` | 644387 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |

Extracted JSON hashes (unchanged; empty `note_facts` preserved): FY2022 `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` (60110); FY2023 `745876dbac871a45b0bd9857c921529bf786f178cfc304af6c0fb12a12373b2e` (60225); FY2024 `a0bc4ccef0974b1ae08e5aa0c4601989476061e98afedd0f860655d0d75dc372` (60984); FY2025 `3887f0d452d9c8887133e25e5a9bad018918de66f0e50419afafab3f072892dd` (58912).

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 note facts remain open; G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

### Plan-facing correction (advisory; plan not rewritten)

Next implementation of a Lululemon segment module requires Plan to specify: (1) G7 extraction of geographic segment note facts with provenance; (2) either first-class segment identity + `presentation_role` on `SupplementalFact`, or a namespaced `fact_type` convention plus later-audited supplemental selection; (3) an optional fail-closed standardizer payload that does not promote segments onto IS/BS lines. This child does not implement those changes.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
