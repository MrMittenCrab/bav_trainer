# RESULT.md — Step 9M.2.4.1.1.1.22 Historical stock-based compensation and operating cash diagnostics

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.22 — Historical stock-based compensation and operating cash diagnostics  
**Work:** `f3295bfc32d045ed81798dae1f18b030`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552).  
No commit / push / sync / checkpoint / branch change. No source/provenance edits, note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed.

Files required beyond the listed production trio, to satisfy the shared resolver and semantic practice identities: `core/model/line_resolver.py` (explicit-concept-only `stock_based_compensation`), `core/engine/component_catalog.py` (families 126–128 and `include_sbc` gating), `scripts/build_lululemon_release.py` (`EXPECTED_SPECS` 293). Plan not rewritten.

---

## Task 1 — Source-gated SBC diagnostic

Registered unique explicit cash-flow concept `stock_based_compensation` on the shared resolver (no label aliases). Settlement proceeds, withholding payments, and repurchases do not resolve. Original source row, values, and signs are retained; the reported SBC link stays populated.

Added practice families `sbc_to_revenue = SBC / revenue`, `sbc_to_operating_cash_flow = SBC / reported CFO`, and `operating_cash_flow_less_sbc = reported CFO − SBC` (label **Reported CFO less SBC add-back**). Absent or ambiguous SBC omits only this extension. Unambiguous CFO and explicit required-period values are required; reported zeros, signed values, and `#N/A` undefined-ratio semantics are preserved. Answer-Key Notes state this mechanical diagnostic does not restate reported CFO, estimate cash compensation or dilution, establish free cash flow, or quantify tax effects.

---

## Task 2 — Independent arithmetic and release regeneration

Independent Python from unchanged reconciled facts (not workbook cache):

| Issuer | Period axis | SBC | Reported CFO | CFO − SBC | SBC/Revenue | SBC/CFO |
|---|---|---|---|---|---|---|
| Lululemon | 2023-01-29 / 2024-01-28 / 2025-02-02 / 2026-02-01 | `78075 / 93560 / 90011 / 62203` | `966463 / 2296164 / 2272713 / 1602477` | `888388 / 2202604 / 2182702 / 1540274` | `78075/8110518`, `93560/9619278`, `90011/10588126`, `62203/11102600` | `78075/966463`, `93560/2296164`, `90011/2272713`, `62203/1602477` |
| Fast Retailing | 2021-08-31 … 2025-08-31 | no explicit CF `stock_based_compensation` | n/a | omitted | omitted | omitted |

Stored Lululemon identities unchanged: SBC concept `stock_based_compensation` / label `Stock-based compensation expense`; CFO `net_cash_from_operating_activities` / `Net cash provided by operating activities`. Answer-Key source link after export/reload: `='Cash Flow Statement'!B35`. CFO-less-SBC formula `=B5-B22` (reported CFO minus reported SBC). Ratio formulas use `NA()` zero-denominator guards on the stated reported denominators.

Practice surface:

- Lululemon: preserved **281** identities + **12** SBC exercises → **293**
- Fast Retailing: preserved **501** identities; **0** SBC exercises

Repeated temporary builds matched persisted semantic maps (keys, formulas, expected values). Disposable Check: Lululemon blank `(0,0,293,293)`, filled `(293,0,0,293)`; Fast Retailing blank `(0,0,501,501)`, filled `(501,0,0,501)`. Incorrect injection did not disclose formulas or hints. Trainers: 293/501 blank yellow cells without Notes. Answer Keys: matching formulas with Notes. Exactly two user-facing workbooks per issuer. Unavailable displays **74 / 74** (Lululemon) and **0 / 0** (Fast Retailing). Availability sidecars unchanged `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` and `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89`. Fast Retailing component map SHA-256 unchanged `3bdc4a68ccb5ff7d30ca1da87bd36a21c51a31f845058590bd5aef70ba1a2374`.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| `PYTHONPATH=. python -m pytest core/tests/test_earnings_quality.py core/tests/test_earnings_quality_change.py core/tests/test_historical_v1_exit_gate.py core/tests/test_lululemon_benchmark.py::test_source_supported_sbc_four_period_diagnostics -q --tb=short` | 0 | **36 passed** in 5.68s |
| `PYTHONPATH=. python -m pytest` capex, earnings-quality, source-availability, trainer, reference-integrity, both benchmarks, lease-repayment, catalog freeze `-q --tb=line` | 0 | **383 passed** in 59.40s |
| `PYTHONPATH=. python -m pytest core/tests -q --tb=line` | 0 | **1164 passed** in 94.66s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |

### Final release inventory (SHA-256 / bytes, recomputed after verification)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `3227f4ff124f4e9a34c791529cd60dda1a097758b29050b20104eaed715d8423` | 30732 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `d9873b976b4c2110b557fc5963328d762136b00876efa67738493d072a8c4b2e` | 87318 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `d1f32b20cee891deb8b65bed7ab574c40318fe5b7b8df87f18ccfb44aa5888fa` | 318659 |
| `release/lululemon/Lululemon_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `release/lululemon/rowmap.json` | `dd807b2cebd3895148b9fc71c546146d25e375916f9b48d9d95e8b48d44299a9` | 64484 |
| `release/lululemon/README.md` | `472639b372beee0d8411e4d3d387339bb035cdef9d39f91e7678e956e3717b85` | 1550 |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `5d4da6cbf7867c225831334a241e8b97dd842053662a617865c754b85418f894` | 37003 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `c48c138c734c30e8d773e399ce76dc85b4c604a7d718c8fb14068536b862e343` | 125337 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `3bdc4a68ccb5ff7d30ca1da87bd36a21c51a31f845058590bd5aef70ba1a2374` | 544689 |
| `release/fast_retailing/FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |
| `release/fast_retailing/rowmap.json` | `9b47c3076abfdecc8184c0ad6632d38007ed682038ae31487371d908c4e57594` | 82160 |
| `release/fast_retailing/README.md` | `e80a4f9448e245b3a8c2093924fa74d578274ad4f3d4efdf3570e7bad746a824` | 1417 |
| `release/fast_retailing/supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `release/fast_retailing/supporting/provenance.json` | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` | 875119 |
| `release/fast_retailing/supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 |

Supporting standardized/provenance/conflicts remain SHA-256-identical to `benchmark/{issuer}/reconciled/`. Source PDFs were not modified.

---

## Task 3 — Corrected historical capex timing (not this child's test runs)

Inspected `.git/autocycle/reviewed-recovery-20260915-120942/evidence.json` SHA-256 `616253f85ebfbb2155f3de0374f8de75d9f2c9656599a12bf2cbc2bb4c9997fb` (4217). Snapshot-limited authorization remains the five production/test files listed there. Original edit ownership, historical batch, and recovery work/attempt `b0ebb338d08f4e09a674d1ad1ee3da21` / `cc3fdf471a9c44c28fa7e8fed1d9e4fa` are retained. Publication recovery does not establish parent acceptance. No NEW_EVIDENCE.

Hash-bound logs:

- original `cursor-20260915-033742-18263.log` SHA-256 `d1ebe9291a24a508dc4e1361955c5e6817ead1f776b0bee26082aeca574348e8`
- resumed `cursor-20260915-034910-19408.log` SHA-256 `57cfd40f1d7c266af8116a6d1cae450f645959746b4eb68744771973dd24a60c`

**Original** isolation subprocess (explicit `exit=0`; pytest duration vs wrapper elapsed kept distinct):

| Suite | Pytest | Wrapper elapsed | Exit |
|---|---|---|---:|
| focused 76 passed | 6.34s | 6.63s | 0 |
| parent 543 passed | 14.51s | 14.81s | 0 |
| Fast Retailing 132 passed | 30.51s | 30.77s | 0 |
| full 1099 passed | 95.38s | 95.66s | 0 |

**Resumed** wrappers (passing pytest summaries; `PIPESTATUS[0]` unset under zsh): 76 passed in 5.56s; 543 passed in 13.12s; 132 passed in 29.97s; 1099 passed in 92.08s; wrapper **exit 1**. Historical test evidence is separate from this child's 1164-passed run.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex exercises; explicit-concept precedence; ambiguity rejection; original-row links; 74 Lululemon / 0 Fast Retailing unavailable displays; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; cash-after-capex `327806 / 1644299 / 1583481 / 921675`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending; E11 NonReq UNVERIFIED; G6–G9 and remaining TARGET Step 9 exit gates unchanged. No blanket DONE. No prospective ID reservation.

No plan rewrite.
