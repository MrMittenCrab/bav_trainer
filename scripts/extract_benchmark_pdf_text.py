"""Regenerate Fast Retailing PDF text extracts for benchmark transcription.

Benchmark-only helper. Not a Trainer runtime dependency.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "benchmark" / "fast_retailing" / "source"
OUT = ROOT / "benchmark" / "fast_retailing" / "_extract"


def extract_year(year: int, *, max_pages: int = 30) -> Path:
    pdf = SOURCE / f"Fastretailing_CFS{year}.pdf"
    reader = PdfReader(str(pdf))
    parts: list[str] = []
    limit = min(max_pages, len(reader.pages))
    for i in range(limit):
        text = reader.pages[i].extract_text() or ""
        parts.append(f"\n\n===== PAGE {i + 1} =====\n{text}")
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"CFS{year}_p1-{limit}.txt"
    out.write_text("".join(parts), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, action="append")
    parser.add_argument("--max-pages", type=int, default=30)
    args = parser.parse_args()
    years = args.year or list(range(2021, 2026))
    for year in years:
        path = extract_year(year, max_pages=args.max_pages)
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
