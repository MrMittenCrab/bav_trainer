Status: Step 9M.1 complete — generic filing-JSON input + Fast Retailing migration

Implementation base:
- 3c3949f Step 9M.0 Fast Retailing benchmark baseline
- Target/spec: TARGET.md source-data architecture + filing-JSON design

Final verification (Task 8):
- focused input-pipeline tests: 30 passed
- full `core/tests/`: 346 passed
- Fast Retailing `validate-source`: 5/5 OK, 0 errors / 0 warnings
- `reconcile` twice into `/tmp/fr{1,2}`: no artifact diffs; `overlap_conflicts=3`
- engine audit: source fixture load + identity validation pass; stages 3–4 fail on G1–G7 as intended
- CLI: `{ingest, validate-source, reconcile, build, check, list}` (no `extract`)

Step 9M.1 evidence:
- five Fast Retailing extracted filings validated: yes
- reconciliation artifacts deterministic: yes (`standardized.json` / `provenance.json` / `conflicts.json`)
- generic pipeline reproduces accepted benchmark facts/conflicts: yes (3 overlap conflicts; FY2025 anchors)
- existing Step 9M.0 accounting gaps intentionally remain for 9M.2: yes (G1–G7)
- OpenAI API extraction not implemented: yes (no `extract` command)
- source hashes computed by BAV validation (not by extractor): yes
- CLI surface: {ingest, validate-source, reconcile, build, check, list}
- no production Fast Retailing-specific reconciliation path: yes
- no new historical formula families: yes (orders 1..90 unchanged)
- forecasting / valuation still deferred: yes
- TARGET.md unchanged by Cursor

Synthetic surfaces unchanged:
- active family orders 1..90
- base demo: 74 / 312
- normalization demo: 78 / 332
- shares only: 82 / 346
- shares + norm: 90 / 384
- services: 59 / 248
- retail: 78 / 331
- manufacturer: 74 / 311

Files added/updated (input pipeline + migration):
- `core/data/filing.py`
- `core/ingestion/filing_json.py`
- `core/ingestion/filing_validator.py`
- `core/ingestion/filing_reconciler.py`
- `core/ingestion/filing_standardizer.py`
- `core/ingestion/filing_cli.py`
- `core/__main__.py` (`validate-source`, `reconcile`)
- `core/tests/test_filing_json.py`
- `core/tests/test_filing_reconciler.py`
- `core/tests/test_filing_cli.py`
- `core/tests/test_fast_retailing_benchmark.py`
- `benchmark/fast_retailing/extracted/FY2021.json` … `FY2025.json`
- `benchmark/fast_retailing/reconciled/{standardized,provenance,conflicts}.json`
- `benchmark/fast_retailing/PROVENANCE.md` / `BASELINE.md`
- `scripts/audit_fast_retailing_benchmark.py`
- retired: `scripts/build_fast_retailing_benchmark.py`, `benchmark/fast_retailing/source_facts.json`

Next checkpoint:
- Step 9M.2 accounting-engine gap queue from `benchmark/fast_retailing/GAPS.md`

Unresolved on 9M.1 scope: none — G1–G7 remain intentionally open for 9M.2
