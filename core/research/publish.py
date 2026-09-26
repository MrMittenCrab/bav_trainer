"""Publish research artifacts into a company build directory when Drivers applies."""
from __future__ import annotations

from pathlib import Path

from ..data.interface import StandardizedFinancials
from ..model.revenue_driver import revenue_driver_applicable
from .drivers import (
    APPENDIX_HEADING,
    OBSOLETE_SECTIONS,
    WORKPAPER_FIELDS,
    drivers_filename,
    expected_sections,
    placeholder_filenames,
    publish_drivers,
)


def verify_research_artifacts(output: Path, company: str) -> None:
    research = output / "research"
    figures = output / "figures" / "drivers"
    drivers = research / drivers_filename(company)
    if not drivers.is_file():
        raise ValueError(f"missing {drivers}")
    text = drivers.read_text(encoding="utf-8")
    headings = [line for line in text.splitlines() if line.startswith("#")]
    expected = list(expected_sections(company))
    if not headings or headings[0] != expected[0]:
        raise ValueError(f"Drivers title was {headings[:1]}")
    if APPENDIX_HEADING not in headings:
        raise ValueError("Drivers missing Appendix heading")
    appendix_at = headings.index(APPENDIX_HEADING)
    if any(item in OBSOLETE_SECTIONS for item in headings):
        raise ValueError(f"Drivers retained obsolete sections: {headings}")
    if any(item.startswith("###") for item in headings[: appendix_at + 1]):
        raise ValueError("Drivers main body contains nested headings")
    if headings[1:appendix_at]:
        raise ValueError(f"Drivers main-body headings were {headings[1:appendix_at]}")
    main_body = text.split(APPENDIX_HEADING, 1)[0]
    for field in WORKPAPER_FIELDS:
        if f"\n## {field}" in main_body or f"\n### {field}" in main_body:
            raise ValueError(f"Drivers main body exposes workpaper field {field}")
    for name in placeholder_filenames(company):
        path = research / name
        if not path.is_file() or path.stat().st_size != 0:
            raise ValueError(f"placeholder must be a zero-byte file: {path}")
    referenced = []
    for line in text.splitlines():
        if "](../figures/drivers/" not in line:
            continue
        name = line.split("../figures/drivers/", 1)[1].split(")", 1)[0]
        referenced.append(name)
    if not referenced:
        raise ValueError("Drivers has no figure references")
    for name in referenced:
        path = figures / name
        if not path.is_file() or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"missing PNG figure: {path}")
    if figures.is_dir():
        extras = sorted(
            path.name
            for path in figures.iterdir()
            if path.suffix.lower() == ".png" and path.name not in referenced
        )
        if extras:
            raise ValueError(f"unreferenced Drivers figures: {extras}")


def publish_company_research(
    company: str,
    financials: StandardizedFinancials,
    output: Path,
    *,
    accent: str | None = None,
) -> None:
    if not revenue_driver_applicable(financials):
        return
    publish_drivers(financials, output, display_name=company, accent=accent)
    verify_research_artifacts(output, company)
