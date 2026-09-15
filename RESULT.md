# RESULT.md — Step 9M.2.4.1.1.1.23 Source-supported acquisition cash and historical cash-use diagnostics

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.23 — Source-supported acquisition cash and historical cash-use diagnostics  
**Work:** `1ab2dedee174455eab63872e9a7fb818`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `46dafd50c47ff2df372054293cbc46d6594a817294df7a63965c8391293c5921` (7619).  
No commit / push / sync / checkpoint / branch change. No source/provenance edits, note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed.

Files required beyond the listed production trio, to satisfy the shared resolver and semantic practice identities: `core/model/line_resolver.py` (explicit-concept-only `acquisition_net_of_cash_acquired`), `core/engine/component_catalog.py` (families 129–131 and residual gating), `core/model/historical_expected.py`, `core/engine/reference_model.py`, `core/trainer/checker.py`, `scripts/build_lululemon_release.py` (`EXPECTED_SPECS` 305). Plan not rewritten.

---

## Task 1 — Source-gated acquisition-cash practice

Registered unique explicit cash-flow concept `acquisition_net_of_cash_acquired` on the shared resolver (no label aliases). Goodwill changes, intangible purchases, securities purchases, and ROU payments do not resolve. Original source row, values, and signs are retained; the reported acquisition link stays populated (`='Cash Flow Statement'!B12`).

Added practice families `acquisition_cash_outflow = −reported acquisition cash`, `acquisition_cash_to_revenue = outflow / revenue`, and `cash_after_ppe_capex_and_acquisitions = reported CFO − ppe_capex − outflow`. First two families gate independently of goodwill/intangible balances and capex. The residual additionally requires unique CFO and PP&E-capex sources and reuses their established −reported contracts. Absent or ambiguous sources omit only dependent families. Reported zeros, signed inflows, and `#N/A` undefined-ratio semantics are preserved. Answer-Key Notes state net-of-acquired-cash reporting and that the residual is a mechanical cash-use diagnostic, not comprehensive free cash flow, acquisition profitability, purchase-price allocation, or a goodwill roll-forward.

---

## Task 2 — Independent arithmetic and release regeneration

Independent Python from unchanged reconciled facts (not workbook cache):

| Issuer | Period axis | Reported acquisition | Outflow (−reported) | Revenue | Residual CFO − PP&E capex − outflow |
|---|---|---|---|---|---|
| Lululemon | 2023-01-29 / 2024-01-28 / 2025-02-02 / 2026-02-01 | `0 / 0 / -154146 / 0` | `0 / 0 / 154146 / 0` | `8110518 / 9619278 / 10588126 / 11102600` | `327806 / 1644299 / 1429335 / 921675` |
| Fast Retailing | 2021-08-31 … 2025-08-31 | no explicit CF `acquisition_net_of_cash_acquired` (ROU `payments_for_rou_assets` present, unused) | omitted | n/a | omitted |

Stored Lululemon identities unchanged: acquisition concept `acquisition_net_of_cash_acquired` / label `Acquisition, net of cash acquired`; CFO `net_cash_from_operating_activities` / `Net cash provided by operating activities`; capex stored concept `capital_expenditures` / `Purchase of property and equipment`. Answer-Key source link after export/reload: `='Cash Flow Statement'!B12`. Residual formula `=D81-D77-D87` (reported CFO minus PP&E capex minus acquisition outflow) with expected `1429335` in FY2025. Ratio formulas use `NA()` zero-denominator guards on reported revenue.

Practice surface:

- Lululemon: preserved **293** identities + **12** acquisition-cash exercises → **305**
- Fast Retailing: preserved **501** identities; **0** acquisition-cash exercises

Repeated temporary builds matched persisted semantic maps (keys, formulas, expected values). Disposable Check: Lululemon blank `(0,0,305,305)`, filled `(305,0,0,305)`; Fast Retailing blank `(0,0,501,501)`, filled `(501,0,0,501)`. Incorrect injection did not disclose formulas or hints. Trainers: 305/501 blank yellow cells without Notes. Answer Keys: matching formulas with Notes. Exactly two user-facing workbooks per issuer. Unavailable displays **74 / 74** (Lululemon) and **0 / 0** (Fast Retailing). Availability sidecars unchanged `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` and `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89`. Fast Retailing component map SHA-256 unchanged `3bdc4a68ccb5ff7d30ca1da87bd36a21c51a31f845058590bd5aef70ba1a2374`.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| `PYTHONPATH=. python -m pytest core/tests/test_acquisition_cash.py core/tests/test_historical_v1_exit_gate.py::test_historical_v1_active_catalog_namespace_is_frozen -q --tb=short` | 0 | **14 passed** in 0.69s |
| `PYTHONPATH=. python -m pytest` acquisition, capex, earnings-quality, source-availability, both benchmarks, lease-repayment, catalog freeze, trainer, reference-integrity, line-resolver `-q --tb=line` | 0 | **446 passed** in 59.77s |
| `PYTHONPATH=. python -m pytest core/tests -q --tb=line` | 0 | **1180 passed** in 94.56s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced (repeat-build map identical) |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |

### Final release inventory (SHA-256 / bytes, recomputed after verification)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `5893c0b3580c9b670db02d2012cbf03a128d3f7ef0ceb52aec44ecf7e736cf50` | 31077 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `f66367f56638211ac2c486109c6157849fffdd7a1472355cfb66e2372f33a0a2` | 89599 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `d0106d2a8f270c833eff43bf7bf37226f15037063d073ef90c79a2a2cc939807` | 337179 |
| `release/lululemon/Lululemon_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `release/lululemon/rowmap.json` | `5b118f64c0dceccfb90abebc4053f3921c57cd4c355fd4d2090c25284982e417` | 66432 |
| `release/lululemon/README.md` | `472639b372beee0d8411e4d3d387339bb035cdef9d39f91e7678e956e3717b85` | 1550 |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `28e37cbb8b45acc94b9cdfff9ffc137a47fe0c38e7af7680abcc1234265680b9` | 37006 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `cb13d396165fa9e989e8cf8dd05119583541015fb71300bc1f168afa5efa569a` | 125340 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `3bdc4a68ccb5ff7d30ca1da87bd36a21c51a31f845058590bd5aef70ba1a2374` | 544689 |
| `release/fast_retailing/FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |
| `release/fast_retailing/rowmap.json` | `9b47c3076abfdecc8184c0ad6632d38007ed682038ae31487371d908c4e57594` | 82160 |
| `release/fast_retailing/README.md` | `e80a4f9448e245b3a8c2093924fa74d578274ad4f3d4efdf3570e7bad746a824` | 1417 |
| `release/fast_retailing/supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `release/fast_retailing/supporting/provenance.json` | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` | 875119 |
| `release/fast_retailing/supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 |

Supporting standardized/provenance/conflicts remain SHA-256-identical to `benchmark/{issuer}/reconciled/`. Source PDFs were not modified. Fast Retailing XLSX bytes differ from the prior child only after rebuild (semantic map unchanged).

---

## Task 3 — Recorded disposition and pending obligations

Acquisition-source disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md` now distinguishes Lululemon’s unique explicit CF `acquisition_net_of_cash_acquired` (taught) from Fast Retailing / DEMO (absent; ROU-acquisition payments are not a substitute). Unsupported impairment / purchase-price-allocation deferrals are preserved.

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Snapshot-limited authorization remains the five production/test files listed there. Original edit ownership, historical batch, and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` are retained. Publication recovery does not establish parent acceptance. No NEW_EVIDENCE claimed for those recovered logs.

Hash-bound logs (retained, not re-executed as this child’s proof):

- original `cursor-20260915-033742-18263.log` SHA-256 `d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`
- resumed `cursor-20260915-034910-19408.log` SHA-256 `57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`

**Original** isolation subprocess (explicit `exit=0`; pytest duration vs wrapper elapsed kept distinct):

| Suite | Pytest | Wrapper elapsed | Exit |
|---|---|---|---:|
| focused 76 passed | 6.34s | 6.63s | 0 |
| parent 543 passed | 14.51s | 14.81s | 0 |
| Fast Retailing 132 passed | 30.51s | 30.77s | 0 |
| full 1099 passed | 95.38s | 95.66s | 0 |

**Resumed** wrappers (passing pytest summaries; `PIPESTATUS[0]` unset under zsh): 76 passed in 5.56s; 543 passed in 13.12s; 132 passed in 29.97s; 1099 passed in 92.08s; wrapper **exit 1**. Historical test evidence is separate from this child's 1180-passed run.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex/SBC exercises; explicit-concept precedence; ambiguity rejection; original-row links; 74 Lululemon / 0 Fast Retailing unavailable displays; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; cash-after-capex `327806 / 1644299 / 1583481 / 921675`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending; E11 NonReq UNVERIFIED; G6–G9 and remaining TARGET Step 9 exit gates unchanged. No blanket DONE. No prospective ID reservation.

No plan rewrite.
