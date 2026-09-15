# RESULT.md — Step 9M.2.4.1.1.1.25 Source-supported historical cash roll-forward practice

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.25 — Source-supported historical cash roll-forward practice  
**Work:** `70a2e6c171194e8697b32a1e29757e77`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `b84c5c9bca03f9772fbe33fc6861e47cf07fff09d4387b54ce56f1ed7edabc88` (7506).  
No commit / push / sync / checkpoint / branch change. No source/provenance edits, note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed.

Files required beyond the listed production trio, to satisfy the shared resolver and semantic practice identities: `core/model/line_resolver.py` (explicit-concept aliases for operating/investing/financing totals, FX, opening/closing cash, and reported cash change), `core/engine/component_catalog.py` (families 135–138 with independent gating), `core/model/historical_expected.py`, `core/engine/reference_model.py`, `core/trainer/checker.py`, `scripts/build_lululemon_release.py` (`EXPECTED_SPECS` 333), `scripts/audit_fast_retailing_benchmark.py` (`EXPECTED_PRACTICE_TOTAL` 521). Plan not rewritten.

---

## Task 1 — Source-gated cash roll-forward practice

Registered unique explicit CF concepts for operating, investing and financing totals, FX, opening cash, closing cash, and reported cash change. Stored-concept aliases cover both benchmarks without changing stored rows: `net_cash_from_operating_activities` / `operating_cash_flow`, `net_cash_from_investing_activities` / `investing_cash_flow`, `net_cash_from_financing_activities` / `financing_cash_flow`, `effect_of_fx_on_cash` / `effect_of_exchange_rate_on_cash`, `change_in_cash` / `net_change_in_cash`, plus `cash_beginning` and `cash_ending`. Competing aliases, label-only inputs, and wrong-statement substitutes (including BS cash and `cash_generated_from_operations`) do not resolve.

Added practice families `cash_movement_from_flows = CFO + CFI + CFF + FX`, `cash_movement_difference = cash_movement_from_flows − reported_cash_change`, `cash_ending_from_flows = cash_beginning + cash_movement_from_flows`, and `cash_ending_difference = cash_ending_from_flows − reported_cash_ending`. Each family gates on its own unique dependencies; absent or ambiguous sources omit only dependent families. Missing required-period values fail closed. Reported zeros and signed flows are preserved. Original-row source links stay populated. Answer-Key Notes explain signed flows, FX, and calculated-minus-reported differences in statement units; nonzero gaps remain visible with no balancing plug, cause claim, BS-cash substitute, or debt-funding inference.

---

## Task 2 — Independent arithmetic and release regeneration

Independent Python from unchanged reconciled facts (not workbook cache):

| Issuer | Period axis | Movement from flows (CFO+CFI+CFF+FX) | Movement − reported change | Ending from flows − reported ending |
|---|---|---|---|---|
| Lululemon | 2023-01-29 / 2024-01-28 / 2025-02-02 / 2026-02-01 | `-105004 / 1089104 / -259635 / -177134` | `0 / 0 / 0 / 0` | `0 / 0 / 0 / 0` |
| Fast Retailing | 2021-08-31 … 2025-08-31 | `84204 / 180556 / -455013 / 290280 / -300321` | `0 / 0 / -2 / 1 / -1` | `-1 / 0 / -1 / 0 / 0` |

Stored identities unchanged. Lululemon: operating `net_cash_from_operating_activities` / `Net cash provided by operating activities`; investing `net_cash_from_investing_activities`; financing `net_cash_from_financing_activities`; FX `effect_of_fx_on_cash`; change `change_in_cash`; opening/closing `cash_beginning` / `cash_ending`. Fast Retailing: `operating_cash_flow` / `investing_cash_flow` / `financing_cash_flow` / `effect_of_exchange_rate_on_cash` / `net_change_in_cash` / `cash_beginning` / `cash_ending`. Answer-Key source links after export/reload include Lululemon `='Cash Flow Statement'!B27` (operating), `B13` (investing), `B7` (financing), `B39` (FX), `B40` (change), `B37` (beginning), `B38` (ending). FY2026 movement formula `=E102+E103+E104+E105` expected `-177134`; difference `=E106-E107` expected `0`. Fast Retailing FY2025 movement `=F91+F92+F93+F94` expected `-300321`; movement difference `=F95-F96` expected `-1`.

Practice surface:

- Lululemon: preserved **317** identities + **16** cash-roll-forward exercises → **333**
- Fast Retailing: preserved **501** identities + **20** cash-roll-forward exercises → **521**

Repeated temporary builds matched persisted semantic maps (keys, formulas, expected values). Disposable Check: Lululemon blank `(0,0,333,333)`, filled `(333,0,0,333)`; Fast Retailing blank `(0,0,521,521)`, filled `(521,0,0,521)`. Incorrect injection did not disclose formulas or hints. Trainers: 333/521 blank yellow cells without Notes. Answer Keys: matching formulas with Notes. Exactly two user-facing workbooks per issuer. Unavailable displays **74 / 74** (Lululemon) and **0 / 0** (Fast Retailing). Availability sidecars unchanged `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` and `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89`.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| `PYTHONPATH=. python -m pytest core/tests/test_cash_rollforward.py core/tests/test_historical_v1_exit_gate.py::test_historical_v1_active_catalog_namespace_is_frozen core/tests/test_line_resolver.py::test_cash_rollforward_explicit_aliases_and_label_only_rejection core/tests/test_line_resolver.py::test_cash_rollforward_competing_aliases_are_ambiguous core/tests/test_line_resolver.py::test_cash_rollforward_explicit_concept_outranks_label -q --tb=short` | 0 | **15 passed** in 0.58s |
| `PYTHONPATH=. python -m pytest` cash-rollforward, share-repurchase, acquisition, capex, earnings-quality, source-availability, both benchmarks, lease-repayment, catalog freeze, trainer, reference-integrity, line-resolver `-q --tb=line` | 0 | **470 passed** in 61.69s |
| `PYTHONPATH=. python -m pytest core/tests -q --tb=line` | 0 | **1212 passed** in 97.46s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced (repeat-build map identical) |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |

### Final release inventory (SHA-256 / bytes, recomputed after verification)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `600c26e5c3a198916a7294906ec5c8cc4b2a4de0f8a22f2c0eb950ab795dfb43` | 31989 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `b0541be1f852df1dc90eaf6bf77e4af334700d714f3a6db2ca1c77eb49d39f6c` | 95308 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `4792338286adc88a4f196b5f9f7ae8df7a17273dd052773c0bbc4c5a6dd8ddd2` | 378218 |
| `release/lululemon/Lululemon_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `release/lululemon/rowmap.json` | `358fa361887ff0952e76a6396fbc243c744e27d73b5bd990bd6f7904f3f71c22` | 71113 |
| `release/lululemon/README.md` | `472639b372beee0d8411e4d3d387339bb035cdef9d39f91e7678e956e3717b85` | 1550 |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `b029c149967d087a8cf79350d9e47d749cd373bd6caea7fc0b6a2ea5ae279278` | 37656 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `5c924e3a51097dd589c30e0a7383d5e0dc7b1467f74bfec816df48b99e8ebb5c` | 129020 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `095129bad292d551bf7699f4539a00c29e4c5bee05eee086f4c97e59bb32c92c` | 571120 |
| `release/fast_retailing/FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |
| `release/fast_retailing/rowmap.json` | `d0bf4a3abc58035f0be93f9f61252f4dd28bdc1086cd283e031e746bd76a16b4` | 85421 |
| `release/fast_retailing/README.md` | `e80a4f9448e245b3a8c2093924fa74d578274ad4f3d4efdf3570e7bad746a824` | 1417 |
| `release/fast_retailing/supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `release/fast_retailing/supporting/provenance.json` | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` | 875119 |
| `release/fast_retailing/supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 |

Supporting standardized/provenance/conflicts remain SHA-256-identical to `benchmark/{issuer}/reconciled/`. Source PDFs were not modified.

---

## Task 3 — Recorded disposition and pending obligations

Cash-reconciliation disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md` now records source-gated `CASH ROLL-FORWARD CONTEXT` when unique explicit CF operating, investing, financing and FX totals resolve (Lululemon and Fast Retailing). DEMO omits. Calculated-minus-reported gaps stay visible; balancing plugs, cause claims, BS-cash substitution, and debt-funding inference remain excluded.

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Snapshot-limited authorization remains the five production/test files listed there. Original edit ownership, historical batch, and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` are retained. Publication recovery does not establish parent acceptance. No NEW_EVIDENCE claimed for those recovered logs.

Hash-bound logs (retained, not re-executed as this child's proof):

- original `cursor-20260915-033742-18263.log` SHA-256 `d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`
- resumed `cursor-20260915-034910-19408.log` SHA-256 `57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`

**Original** isolation subprocess (explicit `exit=0`; pytest duration vs wrapper elapsed kept distinct):

| Suite | Pytest | Wrapper elapsed | Exit |
|---|---|---|---:|
| focused 76 passed | 6.34s | 6.63s | 0 |
| parent 543 passed | 14.51s | 14.81s | 0 |
| Fast Retailing 132 passed | 30.51s | 30.77s | 0 |
| full 1099 passed | 95.38s | 95.66s | 0 |

**Resumed** wrappers (passing pytest summaries; `PIPESTATUS[0]` unset under zsh): 76 passed in 5.56s; 543 passed in 13.12s; 132 passed in 29.97s; 1099 passed in 92.08s; wrapper **exit 1**. Historical test evidence is separate from this child's 1212-passed run.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex/SBC/acquisition/repurchase exercises; explicit-concept precedence; ambiguity rejection; original-row links; 74 Lululemon / 0 Fast Retailing unavailable displays; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending; E11 NonReq UNVERIFIED; G6–G9 and remaining TARGET Step 9 exit gates unchanged. No blanket DONE. No prospective ID reservation.

No plan rewrite.
