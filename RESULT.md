# RESULT.md — Step 9M.2.4.1.1.1.32 Lululemon geographic segment-fact extraction and supplemental reconciliation

**Status:** COMPLETE (this child repair; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.32 — Lululemon geographic segment-fact extraction and supplemental reconciliation  
**Work:** `24a805ab41064b6aa5a8b6ad474edf88`  
**Plan:** `54dbb892521c44bc90dffd4ecded2eb0`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** empty (`inputs: []`)  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `2cbe6f32332f0c550bd246e27a897afda62fe4c3dd44c6eed4393e31a106b9f3` (9224).  
No commit / push / sync / checkpoint / branch change. No workbook generation, forecasting, or valuation. Spreadsheet recalculation was **not** performed.  
This child does **not** declare parent or Step 9 acceptance. G7 remains **OPEN** (store KPIs and lease maturity still unextracted).

---

## Fresh vs retained evidence

| Kind | This child |
|---|---|
| Fresh | Role-eligibility repair; in-memory FY2025 `prior_presentation` mutation; focused filing tests **101 passed**; Lululemon/Fast Retailing benchmarks **171 passed**; `pytest core/tests` **1280 passed**; temporary `python -m core reconcile`; independent five-period arithmetic; checkpoint `b17e8460fd5baa272ceaa4d86886fe50c9515279` protected hashes and non-note JSON comparison |
| Retained | JSON `note_facts` extraction (no re-extraction); PDF SHA-256 identity with checkpoint; prior page inspection (FY2023 native p84 / printed 78; FY2024 Note 23 p79–80 / printed 73–74; FY2025 Note 24 title p79 / printed 73, facts p80–81 / printed 74–75) |
| Not claimed | Historical focused **88** / suite **1267** counts as this proof; production canonical rewrite; workbook Check / spreadsheet recalculation; CID re-decode |

Interpreter: `/Users/lizhiguo/Documents/Developer/.venv/bin/python` **3.14.0**. Tolerance: **`GEO_BRIDGE_TOLERANCE = 0`**.

---

## Task 1 — Presentation eligibility and precedence (repair)

Geographic selection now evaluates **complete period/source presentations** before ranking.

- Mixed `presentation_role` values inside one `(period, filing_year, source_file)` fail closed (`mixed presentation roles`).
- Eligible roles: `current_period`, `comparative`, `restated_comparative`.
- `prior_presentation` observations stay in provenance `note_facts` and are excluded from comparable selection.
- Incomplete eligible presentations fail closed. Incomplete prior presentations are not assembled as comparable snapshots.
- A period with geographic facts but **no eligible complete presentation** fails closed.
- Rank matches the filing contract: restated comparative above current/comparative; current and comparative equal; later `filing_year` within that rank. Unresolved equal-priority candidates fail closed (no input-order tie-break).
- Serialized `presentation_basis` is the **selected** role. Reasons:
  - `restated_comparative_precedence` when restated wins over other eligible roles;
  - `excluded_newer_prior_presentation` when a newer prior presentation is excluded;
  - `sole_source_observation` when one eligible presentation remains;
  - `later_audited_presentation` when later year wins among equal-rank eligible presentations.
- Namespace, duplicate, bridge, IS-control, unit-scale, and failure-immutability checks are unchanged. Geographic selection remains separate from statement rows, lease, and share facts.

---

## Selected-source matrix (temporary reconcile, unmutated filings)

| Period | Filing year | Source file | Family | Role | Reason | PDF page |
|---|---:|---|---|---|---|---:|
| 2022-01-30 | 2023 | `LULU_FY2023_Annual_Report.pdf` | itemized_reconciling | restated_comparative | sole_source_observation | 84 |
| 2023-01-29 | 2024 | `LULU_FY2024_Annual_Report.pdf` | corporate_column | restated_comparative | later_audited_presentation | 80 |
| 2024-01-28 | 2025 | `LULU_FY2025_Annual_Report.pdf` | corporate_column | restated_comparative | restated_comparative_precedence | 81 |
| 2025-02-02 | 2025 | `LULU_FY2025_Annual_Report.pdf` | corporate_column | restated_comparative | restated_comparative_precedence | 80 |
| 2026-02-01 | 2025 | `LULU_FY2025_Annual_Report.pdf` | corporate_column | current_period | sole_source_observation | 80 |

Source years: FY2023 for `2022-01-30`; FY2024 for `2023-01-29`; FY2025 for `2024-01-28`, `2025-02-02`, `2026-02-01`. Counts: **105** `note_facts`, **56** selections, `supplemental_conflict_count=0`.

### Blocking mutation (in-memory; extracted JSON not rewritten)

FY2025 facts for `2025-02-02` marked `prior_presentation`; Americas revenue `+100` → `7928256`; Rest of World `−100`. Consolidated note controls still balance. Selection keeps FY2024 Americas **`7928156`** (`current_period`, reason `excluded_newer_prior_presentation`) and retains superseded `7928256` in provenance. Reverse filing order unchanged. Committed `LULU_FY2025.json` bytes identical after the test.

### Rejection cases (tests)

Prior-only period; mixed roles; incomplete eligible not rescued by complete prior; equal-priority current vs comparative same year; reverse order; missing segment; mixed `segment.channel.*`; unknown identity; missing role; corporate double counting; revenue/IFOP/IS mismatch; incompatible `unit_scale`; invalid page / non-finite value. Failures raise before returning a selection. CLI prior-only case: input JSON unchanged and output directory empty.

---

## Fact counts (extracted `note_facts`, unchanged this repair)

| Filing | `note_facts` | SHA-256 | Bytes |
|---|---:|---|---:|
| FY2022 | **0** | `706cd75845133425b1821b9ff989ef1131005bdfb2321a76b1a6e91f710a6f18` | 60110 |
| FY2023 | **39** | `fcaa9abb417c4f96eb5496c5fc3f1b683b13c17a498c400de869e81880788c05` | 73971 |
| FY2024 | **33** | `0ddc2893afa892d2e1684a38fdc3a3275bb82ace5d4a237c785ad1246d327c4f` | 72244 |
| FY2025 | **33** | `fc4ffe8e7ce7f919c815ff4eecdb171d7f75f528a925cbced5814044d8363a10` | 70176 |

Non-note filing content equals checkpoint `b17e8460fd5baa272ceaa4d86886fe50c9515279` for all four JSONs. Source PDFs SHA-256 match that checkpoint. Canonical reconciled artifacts and Fast Retailing releases were not rewritten.

JSON pages: FY2023 Note 23 p84; FY2024 Note 23 p79–80; FY2025 Note 24 p80–81 (title on p79 per retained inspection). Labels include Americas, China Mainland, Rest of World. China Mainland is not PRC. No 2021-01-31 facts.

---

## Task 3 — Verification

### Independent five-period bridges (USD thousands, tolerance 0)

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
| `/Users/lizhiguo/Documents/Developer/.venv/bin/python -m pytest core/tests/test_geographic_segment_facts.py core/tests/test_filing_json.py core/tests/test_filing_reconciler.py core/tests/test_filing_cli.py -q` | 0 | **101 passed** in 1.49s (fresh; historical 88 not this proof) |
| `... pytest core/tests/test_lululemon_benchmark.py core/tests/test_fast_retailing_benchmark.py -q` | 0 | **171 passed** in 38.85s |
| `... pytest core/tests -q` | 0 | **1280 passed** in 105.22s (fresh; historical 1267 not this proof) |
| `python -m core reconcile` extracted → **temporary** dir `--admit-period 2022-01-30` | 0 | `overlap_conflicts=3`; `note_facts=105`; selected=56 |
| Temporary standardized.json / conflicts.json vs committed | 0 | **equal** |
| Statement-only provenance vs committed | 0 | **equal** |
| Protected artifacts + extracted JSON SHA-256 vs `b17e8460fd5baa272ceaa4d86886fe50c9515279` | 0 | **match** (table below) |

Temporary provenance SHA-256 `5067c1d04aa93c18062fe7eb90558a86394283b7d9fe45899761f71cfb615951` (786300) — not a committed artifact. Size/hash differ from the prior later-year-only serialization because selected roles/reasons are now truthful.

### Protected-artifact hashes vs checkpoint `b17e8460fd5baa272ceaa4d86886fe50c9515279`

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
