# RESULT.md — Step 9M.2.4.1.1.1.32 Lululemon geographic segment-fact extraction and supplemental reconciliation

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.32 — Lululemon geographic segment-fact extraction and supplemental reconciliation  
**Work:** `24a805ab41064b6aa5a8b6ad474edf88`  
**Plan:** `377527f6ed624e0288dcd56eb982456a`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `6b5f9a7ee96b5cacc58c3d2f3ead227c8fa29f8d91c8b87c104c3db60ffdf8ba` (8865).  
No commit / push / sync / checkpoint / branch change. No workbook generation, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent or Step 9 acceptance. G7 remains **OPEN** (store KPIs and lease maturity still unextracted).

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | PDF page inspection (FY2023 native p84; FY2024/FY2025 Calibri CID decode p79–81); extracted `note_facts` counts; temporary `python -m core reconcile`; independent five-period arithmetic; focused filing tests; `pytest core/tests` **1267 passed** |
| Not claimed | Historical 1253-test count (superseded by this fresh 1267); production canonical rewrite; workbook Check / spreadsheet recalculation |

Tolerance for note-control and IS cross-checks: **`GEO_BRIDGE_TOLERANCE = 0`** (USD thousands integers).

---

## Task 1 — Namespaced identities and extracted facts

Namespace prefix: `segment.geo.q4_2023.` (Q4-2023 geographic reportable-segment definition). Allowed local identities:

| Identity | Role |
|---|---|
| `net_revenue.{americas,china_mainland,rest_of_world}` | Reportable-segment revenue |
| `net_revenue.segment_total` | Three-segment control (column presentations) |
| `net_revenue.consolidated` | Note consolidated revenue control |
| `income_from_operations.{americas,china_mainland,rest_of_world}` | Reportable-segment IFOP |
| `income_from_operations.segment_total` | Three-segment IFOP control (not a bridge addend with the three segments) |
| `income_from_operations.corporate_unallocated` | ASU column corporate IFOP, **reported signed** (negative) |
| `income_from_operations.consolidated` | Note consolidated IFOP control |
| `ifop_reconciling.general_corporate_expenses` | Itemized expense line, reported positive |
| `ifop_reconciling.studio_obsolescence_provision` | Itemized expense line, reported positive |
| `ifop_reconciling.impairment_and_restructuring` | Itemized expense line, reported positive (labels vary; one identity) |
| `ifop_reconciling.amortization_of_intangible_assets` | Itemized expense line, reported positive |
| `ifop_reconciling.acquisition_related_expenses` | Itemized expense line, reported positive |
| `ifop_reconciling.gain_on_disposal_of_assets` | Itemized line, reported signed (FY2023 2023-01-29: `-10180`) |

Units: USD thousands, `status=reported`. Omitted dashes are absent (not inferred zeros). Channel/product/D&A/significant-expense/asset/capex/KPI/lease lines were not extracted. China Mainland is not PRC. No 2021-01-31 facts. No week-adjusted amounts.

**Bridge operations**

- Revenue: `americas + china_mainland + rest_of_world = consolidated`. Corporate revenue omitted (dash) stays absent.
- Itemized IFOP (FY2023 note): `segment_total − Σ reported reconciling-line values = consolidated`. Subtracting a parenthetical gain (`-10180`) increases IFOP.
- Corporate-column IFOP (FY2024/FY2025 notes): `segment_total + corporate_unallocated = consolidated`. Itemized components inside the corporate column are **not** also selected (double-count fail-closed).

`SupplementalFact.presentation_role` is optional; geographic facts set it. Empty-note / lease / share payloads omit it.

### Fact counts (extracted `note_facts`)

| Filing | `note_facts` | SHA-256 | Bytes |
|---|---:|---|---:|
| FY2022 | **0** (unchanged) | `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` | 60110 |
| FY2023 | **39** | `fcaa9abb417c4f96eb5496c5fc3f1b683b13c17a498c400de869e81880788c05` | 73971 |
| FY2024 | **33** | `0ddc2893afa892d2e1684a38fdc3a3275bb82ace5d4a237c785ad1246d327c4f` | 72244 |
| FY2025 | **33** | `fc4ffe8e7ce7f919c815ff4eecdb171d7f75f528a925cbced5814044d8363a10` | 70176 |

Non-note filing content (company/filing/statements/share_facts) is semantically identical to HEAD for all four JSONs. FY2023–FY2025 edits are `note_facts` only. Source PDFs, FY2022 JSON, canonical reconciled artifacts, releases, and Fast Retailing bytes were not rewritten.

Source anchors: FY2023 Note 23 PDF p84 / printed 78; FY2024 Note 23 PDF p79–80 / printed 73–74; FY2025 Note 24 PDF p80–81 / printed 74–75 (Note 24 title begins on p79 / printed 73).

---

## Task 2 — Deterministic supplemental selection

Selection applies **only** to `segment.geo.q4_2023.*`. Lease, share, and other supplemental facts keep existing disagreement-flagging without geographic selection. Segment observations stay in `note_facts` and are not promoted onto IS/BS lines.

Per period, later `filing_year` wins among complete snapshots of one presentation family. Equal-priority contradictions fail closed (no input-order tie-break). All original observations remain in provenance `note_facts`. Selected identities serialize separately as `selected_geographic_segment_facts` (omitted when empty so Fast Retailing provenance stays byte-identical).

### Selected-source matrix (temporary reconcile)

| Period | Filing year | Source file | Family | Reason | PDF page |
|---|---:|---|---|---|---:|
| 2022-01-30 | 2023 | `LULU_FY2023_Annual_Report.pdf` | itemized_reconciling | sole_source_observation | 84 |
| 2023-01-29 | 2024 | `LULU_FY2024_Annual_Report.pdf` | corporate_column | later_audited_presentation | 80 |
| 2024-01-28 | 2025 | `LULU_FY2025_Annual_Report.pdf` | corporate_column | later_audited_presentation | 81 |
| 2025-02-02 | 2025 | `LULU_FY2025_Annual_Report.pdf` | corporate_column | later_audited_presentation | 80 |
| 2026-02-01 | 2025 | `LULU_FY2025_Annual_Report.pdf` | corporate_column | sole_source_observation | 80 |

Matches the plan’s later-audited map. Live provenance retained FY2023 losers for 2024-01-28 while selecting FY2025. `supplemental_conflict_count` remains **0** (overlapping values agree).

Rejected / fail-closed cases (tests): missing segment; mixed `segment.channel.*`; unknown identity / missing `presentation_role`; corporate double counting; revenue/IFOP bridge mismatch; equal-priority same-year contradiction; IS control disagreement. Failure raises before returning a selection (CLI writes nothing).

Optional standardizer segment payload, analytical schedules, and learner exercises were **not** implemented.

---

## Task 3 — Verification

### Independent five-period bridges (USD thousands)

| Period | Revenue Σ segs = cons | IFOP bridge | IS cross-check |
|---|---|---|---|
| 2022-01-30 | 5299906+434261+522450=**6256617** | 2102008−718477−8782−41394=**1333355** | match |
| 2023-01-29 | 6817454+576503+716561=**8110518** | 2803809+(−1475401)=**1328408** | match |
| 2024-01-28 | 7631647+963760+1023871=**9619278** | 3476332+(−1343656)=**2132676** | match |
| 2025-02-02 | 7928156+1361337+1298633=**10588126** | 3840362+(−1334665)=**2505697** | match |
| 2026-02-01 | 7847044+1754799+1500757=**11102600** | **3607682 − 1397067 = 2210615** | match |

### Measured commands

| Command | Exit | Result |
|---|---:|---|
| Independent FY2023 p84 extract; FY2024/FY2025 Calibri CID decode | 0 | anchors above |
| `python -m core reconcile` extracted → **temporary** dir `--admit-period 2022-01-30` | 0 | `overlap_conflicts=3`; `note_facts=105`; selected=56 |
| Temporary standardized.json / conflicts.json vs committed | 0 | **byte-identical** |
| Statement-only provenance (note_facts/selected stripped) vs committed | 0 | **equal** |
| `pytest core/tests/test_geographic_segment_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py` | 0 | **88 passed** |
| `pytest core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py` | 0 | **171 passed** |
| `pytest core/tests` | 0 | **1267 passed** in 104.65s (fresh; historical 1253 not this proof) |
| Protected-artifact SHA-256 after work | 0 | table below; canonical reconciled **unchanged** |

Live temporary provenance SHA-256 `a6abebc8e20fbb0cd26505becefdaca0155ae3fe5e6d2e693d371d98d5c8c10c` (786190) — not a committed artifact.

### Protected-artifact hashes (unchanged this child)

**Lululemon (five-period canonical):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `4e06ce78957a291857d9db074113f071021d057234ff0f7376afafbce4b76904` | 34670 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `ecb1a4120e8a50ca132ab62bca0cc214968bd2770b0e94560c75740d5662570f` | 119554 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `cc584a7bca130e0d52472a7b186bca00954e6eb98d2194418eb3e1c973c1e09f` | 561320 |
| `release/lululemon/availability.json` | `12e3b90aa640b76839e91f388b494644d686dfd705910a0d5541b2e28fbcd8a0` | 15691 |
| `benchmark/lululemon/reconciled/standardized.json` | `a3568c29e883c8ba57af23da7b4286641a3c5f929af311e2e9593c5f63ea2287` | 25011 |
| `benchmark/lululemon/reconciled/provenance.json` | `6799371215e02c888b3a5f687637b38dba4840bd1548cb1860a253f7a699cb12` | 699438 |
| `benchmark/lululemon/reconciled/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |

**Fast Retailing (byte-identical releases, 577 identities, 0 unavailable displays):**

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `546390001c69b2d05e7f16f730bacfed79a62817ea718e97bef079b4a6d014bd` | 38951 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `f01241947745e4c5db4ceff9b445af3811f41eb5e2247a8c82c372de28bdec27` | 139634 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `8a3f4f0c0e8bebb84317ead5a2e1c29679e8b70cdf58c211fe50ccbab04f5a23` | 644387 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` retained. Hash-bound logs `cursor-20260915-033742-18263.log` / `cursor-20260915-034910-19408.log` retained, not re-executed. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING.

---

## Remaining dependency and G7 scope

Exact remaining standardizer/module dependency: there is still **no** `HistoricalSegmentData` (or equivalent) path from selected geographic `note_facts` into `StandardizedFinancials`. Learner schedules/Check identities are not yet generated. Remaining G7: store KPIs; lease maturity detail. Channel-era FY2022 Note 22 was intentionally not extracted.

No plan rewrite. No parent or Step 9 completion claim.

---

## Retained acceptance (not reopened)

Canonical Lululemon five-period history; **486** identities/expectations; **101** unavailable displays; accepted **110** additions; Fast Retailing **577** / **0** unavailable. G1/G2/G3, G5 aliases, accepted historical modules, explicit-concept precedence, ambiguity rejection, strict values, deterministic mapping, original-row provenance. Independent asset/liability/signed-equity gates, sparse omissions, contradiction rejection, empty-detail and subtotal/override controls, contra-equity, historical causal evidence, twelve pretax/ETR cases, mutation controls, failure immutability. Partial-period interest closure, opening-only CoD `0.374`, undefined ratios, pretax resolution, distinct tax expense; no invented interest, inferred zeros, cash-interest substitution, unavailable-history 4% substitute, lease repayment inference, or deferred-tax expense/recoverability claims. Capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Parent temporary-build acceptance: success or exactly `MissingLineError: Required concept 'interest_expense' not found in statement lines`.

A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending Plan closure; E11 NonReq UNVERIFIED. G6 missing 2021-01-31 BS; G7 remainder (store KPIs, lease maturity); G8 deferral; G9 standalone interest completeness; TARGET Step 9 exit gates. No blanket DONE.

Parents 9M.2.4.1.1.1 / 9M.2.4.1.1 / 9M.2.4.1 / 9M.2.4 remain UNRESOLVED.
