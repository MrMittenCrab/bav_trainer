# RESULT.md — Step 9M.2.4.1.1.1.26 Source-supported reported operating-margin bridge

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.26 — Source-supported reported operating-margin bridge  
**Work:** `ed66f1fcc3b149d4b4edac8d03efee9e`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `f29c94829a2bde0dd42ee013841a3ccfab5e46463f295e86e2dd83836c8bc318` (7903).  
No commit / push / sync / checkpoint / branch change. No source/provenance edits, note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed.

Files required beyond the listed production trio, to satisfy the shared resolver and semantic practice identities: `core/model/reported_margin.py`, `core/model/line_resolver.py` (explicit-concept `gross_profit` and `operating_profit`/`operating_income` aliases), `core/engine/component_catalog.py` (families 139–144 with independent gating), `core/model/historical_expected.py`, `core/engine/reference_model.py`, `core/trainer/checker.py`, `scripts/build_lululemon_release.py` (`EXPECTED_SPECS` 354), `scripts/audit_fast_retailing_benchmark.py` (`EXPECTED_PRACTICE_TOTAL` 548). Plan not rewritten.

---

## Task 1 — Source-gated reported operating-margin practice

Registered unique explicit IS `gross_profit` and `operating_profit` / `operating_income`, using existing revenue resolution. Stored concepts and original-row links are unchanged. Competing aliases, label-only profit inputs, and wrong-statement substitutes do not resolve.

Added practice families `gross_margin = gross_profit / revenue`, `reported_operating_margin = operating_profit / revenue`, and `net_operating_expense_burden = (gross_profit − operating_profit) / revenue` for every period; adjacent-period families `gross_margin_change`, `net_operating_expense_burden_change`, and `reconstructed_operating_margin_change = gross_margin_change − burden change`. Each family gates on its own unique dependencies; absent or ambiguous sources omit only dependent families. Missing required-period values fail closed. Reported zeros remain valid. Zero revenue yields `#N/A` with downstream propagation. Opening-period change cells are not practice. Answer-Key Notes explain percentage-point changes, that gross profit minus operating profit includes net intervening operating items (not necessarily SG&A), that a positive burden change reduces operating margin, and that reported operating margin is distinct from BAV NOPAT margin; no price, mix, cost, or normalized-earnings inference.

---

## Task 2 — Independent arithmetic and release regeneration

Independent Python from unchanged reconciled facts (not workbook cache):

| Issuer | Latest gross / operating margin | Reconstructed OM changes (adjacent) |
|---|---|---|
| Lululemon | `0.566005440167168` / `0.19910786662583538` (56.6005% / 19.9108%) | `0.057920226048566836 / 0.01494307232648473 / -0.0375437372557203` |
| Fast Retailing | `0.5378141524034866` / `0.16593398870002668` (53.7814% / 16.5934%) | `0.012466122688521208 / 0.008540125906455864 / 0.023633404320481333 / 0.004551750720958148` |

Stored identities unchanged. Lululemon: `gross_profit` / `Gross profit`; `operating_income` / `Income from operations`; `revenue` / `Net revenue`. Fast Retailing: `gross_profit` / `Gross profit`; `operating_profit` / `Operating profit`; `revenue` / `Revenue`. Answer-Key source links after export/reload include Lululemon `='Income Statement'!B14` (gross profit). FY2026 gross-margin formula `=IF(E115=0,NA(),E116/E115)` expected `0.566005440167168`; reconstructed `=E121-E122`. Fast Retailing FY2025 gross-margin `=IF(F104=0,NA(),F105/F104)` expected `0.5378141524034866`; reconstructed `=F110-F111`. Opening-period reconstructed cells are empty. Reconstructed changes equal adjacent reported-operating-margin differences within `1e-12`.

Practice surface:

- Lululemon: preserved **333** identities + **21** reported-margin-bridge exercises → **354**
- Fast Retailing: preserved **521** identities + **27** reported-margin-bridge exercises → **548**

Repeated temporary builds matched persisted semantic maps (keys, formulas, expected values). Disposable Check: Lululemon blank `(0,0,354,354)`, filled `(354,0,0,354)`; Fast Retailing blank `(0,0,548,548)`, filled `(548,0,0,548)`. Incorrect injection did not disclose formulas or hints. Trainers: 354/548 blank yellow cells without Notes. Answer Keys: matching formulas with Notes. Exactly two user-facing workbooks per issuer. Unavailable displays **74 / 74** (Lululemon) and **0 / 0** (Fast Retailing). Availability sidecars unchanged `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` and `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89`.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| `PYTHONPATH=. python -m pytest core/tests/test_reported_margin.py core/tests/test_line_resolver.py::test_reported_margin_explicit_aliases_and_label_only_rejection core/tests/test_line_resolver.py::test_reported_margin_competing_aliases_are_ambiguous core/tests/test_line_resolver.py::test_reported_margin_explicit_concept_outranks_label core/tests/test_historical_v1_exit_gate.py::test_historical_v1_active_catalog_namespace_is_frozen -q --tb=short` | 0 | **13 passed** in 0.52s |
| `PYTHONPATH=. python -m pytest` reported-margin, cash-rollforward, share-repurchase, acquisition, capex, lease-repayment, source-availability, catalog freeze, trainer, reference-integrity, line-resolver, both benchmarks `-q --tb=line` (after release rebuild) | 0 | included in full suite |
| `PYTHONPATH=. python -m pytest core/tests -q --tb=line` | 0 | **1226 passed** in 99.17s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced (repeat-build map identical) |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |
| `PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py --require-check-counts --verify-release-pair` | 0 | expected_specs=548; blank `(0,0,548,548)`; filled `(548,0,0,548)` |

### Final release inventory (SHA-256 / bytes, recomputed after verification)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `8faa78f837f1a1faacdf5873c1f94c92245fdda09eff86ccc60b540ddf7d513f` | 32561 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `a094d80aca0a69124e75ea0e8ffbafd12c5559c4482cadafeda309bdbb5716c8` | 99512 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `0377ca1aae55362bfd24ab70d19de7d02a20b546189954443300d8ca89355408` | 404705 |
| `release/lululemon/Lululemon_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `release/lululemon/rowmap.json` | `4f79ebfc6d01876e8a242bbef161442fc432f6953888e9e1e7c5f7e91cf42a73` | 74477 |
| `release/lululemon/README.md` | `472639b372beee0d8411e4d3d387339bb035cdef9d39f91e7678e956e3717b85` | 1550 |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `5cebfb377be596a5ab2834bc41efd004aac00e4c464072d36433aaf981c0bb07` | 38254 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `839fd6c07683e4bd5fc1b5eb4420a1a91047037999ae08af4289010efee17de9` | 134036 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `5b0017d5dd63a16bc7b11777621e3336d22f6136755eabc17308a6e0e8ec42b1` | 605265 |
| `release/fast_retailing/FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |
| `release/fast_retailing/rowmap.json` | `2495ddd63bad27c692db603bd119db0971cbeb38f75a767cb6d8fb97faa2f1fc` | 89625 |
| `release/fast_retailing/README.md` | `e80a4f9448e245b3a8c2093924fa74d578274ad4f3d4efdf3570e7bad746a824` | 1417 |
| `release/fast_retailing/supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `release/fast_retailing/supporting/provenance.json` | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` | 875119 |
| `release/fast_retailing/supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 |

Supporting standardized/provenance/conflicts remain SHA-256-identical to `benchmark/{issuer}/reconciled/`. Source PDFs were not modified.

---

## Task 3 — Recorded disposition and pending obligations

Reported-margin disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md` now records source-gated `REPORTED MARGIN BRIDGE CONTEXT` when unique explicit IS `gross_profit` and/or `operating_profit`/`operating_income` resolve with revenue (Lululemon and Fast Retailing). DEMO omits. Notes keep reported operating margin distinct from BAV NOPAT margin; intervening items are not treated as SG&A; price/mix/cost and normalized-earnings causes are not inferred.

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

**Resumed** wrappers (passing pytest summaries; `PIPESTATUS[0]` unset under zsh): 76 passed in 5.56s; 543 passed in 13.12s; 132 passed in 29.97s; 1099 passed in 92.08s; wrapper **exit 1**. Historical test evidence is separate from this child's 1226-passed run.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward exercises; explicit-concept precedence; ambiguity rejection; original-row links; 74 Lululemon / 0 Fast Retailing unavailable displays; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending; E11 NonReq UNVERIFIED; G6–G9 and remaining TARGET Step 9 exit gates unchanged. No blanket DONE. No prospective ID reservation.

No plan rewrite.
