Status: Step 9M.0 complete — Fast Retailing real-company historical benchmark baseline

Implementation base:
- 26f22b7 Step 9L.1 complete
- 19c8aad Fast Retailing CFS PDF sources
- 56a9d00 Plan Step 9M.0

Step 9L.1 review accepted / findings measured:
- identity: judgment selectors remain accepted
- split-lease diagnostic omission confirmed on Fast Retailing primary BS
- lease interest income-side inconsistency recorded as Gap G4 (not fixed)

Benchmark evidence:
- five source hashes verified: yes
- five-period source_facts.json with page provenance: yes
- latest-audited-presentation precedence applied: yes
- overlap conflicts/restatements recorded: 3
- FY2025 independent anchors passed: yes
- engine audit stage results: load pass; identity pass; reconciliation fail (1-unit BS); builder fail (Other financial assets); workbook/Check skipped
- applicable modules (pre-fix): earnings_quality yes; fixed_asset yes; lease_liability omitted (ambiguous split); per_share omitted; normalization omitted
- gaps classified in GAPS.md: 7 open (+ 1 closed transcription fix)
- no production Fast Retailing-specific branches: yes
- no committed Fast Retailing Trainer/Answer Key: yes
- no new historical formula families: yes
- forecasting / valuation still deferred: yes
- GOOGL workbook hash unchanged:
  81faf2882d0df07ecf5def45695431c1935b4f7a94c1e017367596a063063896
- TARGET.md unchanged by Cursor:
  88f69fb47d8464084d504b6e65be9742d5e4924ca78a2c3412156293b3fa2015

Synthetic surfaces unchanged (Step 9L.1):
- active family orders 1..90
- base demo: 74 / 312
- normalization demo: 78 / 332
- shares only: 82 / 346
- shares + norm: 90 / 384
- services: 59 / 248
- retail: 78 / 331
- manufacturer: 74 / 311
- CLI: {ingest, build, check, list}

Files added/updated (benchmark + tests/scripts only):
- `benchmark/fast_retailing/source_manifest.json`
- `benchmark/fast_retailing/source_facts.json`
- `benchmark/fast_retailing/FastRetailing_Standardized.json`
- `benchmark/fast_retailing/provenance.json`
- `benchmark/fast_retailing/PROVENANCE.md`
- `benchmark/fast_retailing/BASELINE.md`
- `benchmark/fast_retailing/GAPS.md`
- `scripts/build_fast_retailing_benchmark.py`
- `scripts/audit_fast_retailing_benchmark.py`
- `scripts/extract_benchmark_pdf_text.py`
- `scripts/build_fast_retailing_source_facts.py` (if present)
- `requirements-benchmark.txt`
- `core/tests/test_fast_retailing_benchmark.py`
- `RESULT.md` / `IMPLEMENTATION.md` status

Tests (fresh, local verification — no attached GitHub CI):
- `PYTHONPATH=. pytest core/tests/test_fast_retailing_benchmark.py -v` -> 5 passed
- `PYTHONPATH=. pytest core/tests/ -q` -> 321 passed
- `PYTHONPATH=. python scripts/audit_fast_retailing_benchmark.py` -> BASELINE written

Next checkpoint:
- Step 9M.1 must be planned from `benchmark/fast_retailing/GAPS.md` only

Unresolved on 9M.0 measurement scope: none — production gaps intentionally open for 9M.1
