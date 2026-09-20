"""Copy Lululemon extracted filings and append store-KPI note facts.

Writes only to the destination directory. Source PDFs, committed extracted
JSON, and geographic/share observations are left unchanged.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXTRACTED = ROOT / "build" / "input" / "lululemon" / "extracted"
DEFAULT_FACTS = (
    ROOT
    / "core"
    / "tests"
    / "fixtures"
    / "operating_kpis"
    / "lululemon_company_operated_stores.json"
)
# Preserve the historical script API while sharing the generic staged handoff.
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from core.ingestion.note_handoff import (
    KPI_PREFIX, load_store_facts, augment_extracted_filings,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extracted", type=Path, default=DEFAULT_EXTRACTED)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--facts", type=Path, default=DEFAULT_FACTS)
    args = parser.parse_args()
    dest = args.dest.resolve()
    extracted = args.extracted.resolve()
    if dest == extracted:
        raise SystemExit("dest must be a temporary directory, not the extracted source")
    written = augment_extracted_filings(extracted, dest, args.facts)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
