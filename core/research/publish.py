"""Publish research artifacts into a company build directory when Drivers applies."""
from __future__ import annotations

from pathlib import Path

from ..data.interface import StandardizedFinancials
from ..model.revenue_driver import revenue_driver_applicable
from .drivers import (
    FIGURE_NAMES,
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
    if headings != list(expected_sections(company)):
        raise ValueError(f"Drivers sections were {headings}")
    for name in placeholder_filenames(company):
        path = research / name
        if not path.is_file() or path.stat().st_size != 0:
            raise ValueError(f"placeholder must be a zero-byte file: {path}")
    for name in FIGURE_NAMES:
        path = figures / name
        if not path.is_file() or path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"missing PNG figure: {path}")
        if f"../figures/drivers/{name}" not in text:
            raise ValueError(f"Drivers missing relative link to {name}")


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
