# RESULT.md — Step 9M.2.4.1.1.1.27 Source-supported inventory growth and intensity bridge

**Status:** COMPLETE (this child; parents remain UNRESOLVED)  
**Step:** 9M.2.4.1.1.1.27 — Source-supported inventory growth and intensity bridge  
**Work:** `b57b3f6199f54daa98b20563fb784b55`  
**Parents:** Steps 9M.2.4.1.1.1, 9M.2.4.1.1, 9M.2.4.1, and 9M.2.4 — remain **UNRESOLVED**  
**INPUT_STATUS:** PENDING  
`TARGET.md` / `IMPLEMENTATION.md`: read-only (unchanged). TARGET SHA-256 `3274be515f8ccf579a4b495bd820a4d14c87328b4d63f95123d0d4a6042407e2` (21552). IMPLEMENTATION SHA-256 `9e5b136df938399cc96283da18b09baa4ae780747b4ea9081bbc8efd7211660f` (7908).  
No commit / push / sync / checkpoint / branch change. No source/provenance edits, note extraction, forecasting, or valuation. Spreadsheet recalculation was **not** performed.

Files required beyond the listed production trio, to satisfy the shared resolver and semantic practice identities: `core/model/inventory_analysis.py`, `core/model/line_resolver.py` (explicit-concept `inventories`), `core/engine/component_catalog.py` (families 145–149 with independent gating), `core/model/historical_expected.py`, `core/engine/reference_model.py`, `core/trainer/checker.py`, `scripts/build_lululemon_release.py` (`EXPECTED_SPECS` 370), `scripts/audit_fast_retailing_benchmark.py` (`EXPECTED_PRACTICE_TOTAL` 569). Plan not rewritten.

---

## Task 1 — Source-gated inventory growth and intensity practice

Registered unique explicit BS `inventories`, using existing revenue resolution. Stored concepts and original-row links are unchanged. Duplicate inventory concepts, label-only inventory, and wrong-statement substitutes do not resolve.

Added practice family `inventory_intensity = inventory / revenue` for every period, plus adjacent-period families `inventory_change`; `inventory_revenue_scale_effect = I_(t−1) × (revenue_t − revenue_(t−1))`; `inventory_intensity_effect = revenue_t × (I_t − I_(t−1))`; and `reconstructed_inventory_change` as the sum of both effects. Inventory change gates on unique inventory alone; intensity and attribution additionally require unique revenue. Absent or ambiguous sources omit only dependent families. Missing required-period values fail closed. Reported zeros remain valid. Zero revenue yields `#N/A` with dependency propagation; direct inventory change remains available. Opening-period change cells are not practice. Answer-Key Notes explain ending inventory relative to annual revenue, the prior-intensity / current-revenue attribution convention, and signed effects. The bridge is an arithmetic decomposition, not inventory days or turnover, and not proof of cash movement, deterioration, seasonality, markdowns, or management causes.

---

## Task 2 — Independent arithmetic and release regeneration

Independent Python from unchanged reconciled facts (not workbook cache):

| Issuer | Latest intensity | Latest inventory change | Latest revenue-scale / intensity effects |
|---|---|---|---|
| Lululemon | `0.15318510979410227` (`1700753 / 11102600`) | `258672` | `70070.30142954475 / 188601.69857045508` |
| Fast Retailing | `0.15025794440234327` (`510958 / 3400539`) | `36498` | `45354.74985791775 / -8856.749857917737` |

Stored identities unchanged. Lululemon: `inventories` / `Inventories`; `revenue` / `Net revenue`. Fast Retailing: `inventories` / `Inventories`; `revenue` / `Revenue`. Answer-Key source links after export/reload include Lululemon `='Balance Sheet'!B9` (inventories). FY2026 intensity formula `=IF(E127=0,NA(),E126/E127)` expected `0.15318510979410227`; reconstructed `=E130+E131`. Fast Retailing FY2025 intensity `=IF(F116=0,NA(),F115/F116)` expected `0.15025794440234327`; reconstructed `=F119+F120`. Opening-period change/attribution cells are empty. Reconstructed changes equal adjacent inventory changes within `1e-8` on both benchmarks.

Practice surface:

- Lululemon: preserved **354** identities + **16** inventory exercises → **370**
- Fast Retailing: preserved **548** identities + **21** inventory exercises → **569**

Repeated temporary builds matched persisted semantic maps (keys, formulas, expected values). Disposable Check: Lululemon blank `(0,0,370,370)`, filled `(370,0,0,370)`; Fast Retailing blank `(0,0,569,569)`, filled `(569,0,0,569)`. Incorrect injection did not disclose formulas or hints. Trainers: 370/569 blank yellow cells without Notes. Answer Keys: matching formulas with Notes. Exactly two user-facing workbooks per issuer. Unavailable displays **74 / 74** (Lululemon) and **0 / 0** (Fast Retailing). Availability sidecars unchanged `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` and `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89`.

### Measured commands (this run)

| Command | Exit | Result |
|---|---:|---|
| `PYTHONPATH=. python -m pytest core/tests/test_inventory_analysis.py core/tests/test_line_resolver.py::test_inventories_explicit_concept_and_label_only_rejection core/tests/test_line_resolver.py::test_inventories_competing_concepts_are_ambiguous core/tests/test_line_resolver.py::test_inventories_explicit_concept_outranks_label core/tests/test_historical_v1_exit_gate.py::test_historical_v1_active_catalog_namespace_is_frozen core/tests/test_lululemon_benchmark.py::test_source_supported_inventory_analysis_four_period_diagnostics core/tests/test_fast_retailing_benchmark.py::test_fast_retailing_inventory_analysis_five_period_diagnostics -q --tb=short` | 0 | **15 passed** in 1.09s |
| `PYTHONPATH=. python -m pytest` inventory, reported-margin, cash-rollforward, share-repurchase, acquisition, capex, lease-repayment, source-availability, catalog freeze, trainer, reference-integrity, line-resolver, both benchmarks (after release rebuild) | 0 | included in full suite |
| `PYTHONPATH=. python -m pytest core/tests -q --tb=line` | 0 | **1240 passed** in 101.74s |
| `python scripts/build_lululemon_release.py` | 0 | staged, verified, replaced (repeat-build map identical) |
| `python scripts/build_fast_retailing_release.py` | 0 | staged, verified, replaced |
| `PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py --require-check-counts --verify-release-pair` | 0 | expected_specs=569; blank `(0,0,569,569)`; filled `(569,0,0,569)` |

### Final release inventory (SHA-256 / bytes, recomputed after verification)

| Path | SHA-256 | Bytes |
|---|---|---:|
| `release/lululemon/Lululemon_Trainer.xlsx` | `f606fe0a942757f6018a091e070dc4fa15fb8e3bd7b466e7cb9b90881b57f940` | 33007 |
| `release/lululemon/Lululemon_Answer_Key.xlsx` | `e86e93f012fc9a35208a7cd4cab12398dc2c502ad4082a4315bd365abec29475` | 102760 |
| `release/lululemon/Lululemon_Answer_Key.component_map.json` | `dca321846c0e29f61eb5c865b69f95626398db2e4b280d57905f3c4026411ec2` | 425282 |
| `release/lululemon/Lululemon_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/lululemon/availability.json` | `13bda24586ef1b55d45351031e796e70378dc62405ebdcdf4e7f310a54abe1c3` | 12422 |
| `release/lululemon/rowmap.json` | `87aec509b7cf3472c3436453c781131b3ee49e8bce5a11d6ea66690fdf5d13b3` | 77041 |
| `release/lululemon/README.md` | `472639b372beee0d8411e4d3d387339bb035cdef9d39f91e7678e956e3717b85` | 1550 |
| `release/lululemon/supporting/standardized.json` | `29852347d78387be6fd9224246ab337b15a5176218cd01b2c20a0c8c3c00b361` | 22548 |
| `release/lululemon/supporting/provenance.json` | `a31f7b05cddc16a61df91cdc8578bb69713069651af21160ff662ea562433075` | 699401 |
| `release/lululemon/supporting/conflicts.json` | `d8a33012f6ea73126ac4e2ece3613e7011c11cb2b581745d8c3563e3c2e978e0` | 4718 |
| `release/fast_retailing/FastRetailing_Trainer.xlsx` | `be67f035a670ef7a4e382e0fbc3be30a564b76f2f229880558fc570b2c21ea5a` | 38714 |
| `release/fast_retailing/FastRetailing_Answer_Key.xlsx` | `4a9e7ea63fecbe92c45b22d6339a62f6bda28930488f0be45f07b993a3aa8f39` | 137950 |
| `release/fast_retailing/FastRetailing_Answer_Key.component_map.json` | `0fff910a9fc446af35409dff54290df8d8c5d1b476a0f6fadb1a85b2ecd61ac3` | 632310 |
| `release/fast_retailing/FastRetailing_Answer_Key.assumptions.json` | `73fbb33f222a978828042ebde1fbbc3cd285c40efda6be5217c2cfbae1fda21a` | 69 |
| `release/fast_retailing/availability.json` | `52bc2257c5b491b901d4a6f905338473cb9f1e9f4cfca61ce51d5e4718096c89` | 1920 |
| `release/fast_retailing/rowmap.json` | `c9020ec49b410ea941ef06138b4ce991a2a2dac5a16f15d86692f74a766f28a8` | 92895 |
| `release/fast_retailing/README.md` | `e80a4f9448e245b3a8c2093924fa74d578274ad4f3d4efdf3570e7bad746a824` | 1417 |
| `release/fast_retailing/supporting/standardized.json` | `5a1d445c8f5013ef4045fb7f9725c6c234d4f814b04cad95856df4e5e2ff92e1` | 30952 |
| `release/fast_retailing/supporting/provenance.json` | `26d9a170881f10b466405339c7f38fa06241c011acd3aab74be650dfc0d0777d` | 875119 |
| `release/fast_retailing/supporting/conflicts.json` | `12b910485985df8390634a7fa5361132bf674b5df403858afb03c9a8c56c44a5` | 7321 |

Supporting standardized/provenance/conflicts remain SHA-256-identical to `benchmark/{issuer}/reconciled/`. Source PDFs were not modified.

---

## Task 3 — Recorded disposition and pending obligations

Inventory disposition in `docs/GOOGL_HISTORICAL_REFERENCE.md` now records source-gated `INVENTORY GROWTH AND INTENSITY CONTEXT` when unique explicit BS `inventories` resolves (Lululemon and Fast Retailing). Intensity and attribution additionally require unique revenue. DEMO omits (no explicit inventory concept). Notes keep the bridge as an arithmetic prior-intensity / current-revenue decomposition; it is not inventory days or turnover and does not prove cash movement, deterioration, seasonality, markdowns, or management causes.

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

**Resumed** wrappers (passing pytest summaries; `PIPESTATUS[0]` unset under zsh): 76 passed in 5.56s; 543 passed in 13.12s; 132 passed in 29.97s; 1099 passed in 92.08s; wrapper **exit 1**. Historical test evidence is separate from this child's 1240-passed run.

---

## Retained acceptance (not reopened)

G5 aliases; prior lease/deferred-tax/capex/SBC/acquisition/repurchase/cash-roll-forward/reported-margin exercises; explicit-concept precedence; ambiguity rejection; original-row links; 74 Lululemon / 0 Fast Retailing unavailable displays; availability `absent_line` with no 4% substitute; capex `638657 / 651865 / 689232 / 680802`; repurchase residuals `-116195 / 1085647 / -207544 / -256674`; NCIT `28555 / 15864 / reported 0 / None`; Common stock `611 / 606 / 581 / 557`. Frozen requests `20260914-193338-000000004` and `20260915-042248-000000005` remain PENDING. A2-ED/B7-MID documentary UNVERIFIED; A5/B8/E10 pending; E11 NonReq UNVERIFIED; G6–G9 and remaining TARGET Step 9 exit gates unchanged. No blanket DONE. No prospective ID reservation.

No plan rewrite.
