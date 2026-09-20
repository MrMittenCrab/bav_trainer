"""Lululemon Drivers research publication from validated BAV outputs."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from core.current_build import prepare_company_input, resolve_company
from core.research.drivers import assemble_drivers_view, expected_sections, publish_drivers
from core.research.publish import publish_company_research, verify_research_artifacts
from core.research.style import apply_research_style, resolve_required_fonts
from core.tests.test_lululemon_benchmark import REVENUE_ANCHORS
from core.tests.test_operating_kpi_facts import INDEPENDENT_STORE_TOTALS

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN_PROSE = (
    "admitted",
    "fail-closed",
    "fail closed",
    "source unavailable",
    "standardizedfinancials",
    "hypothesis",
    "verdict",
    "audit-only",
    "audit only",
    "supported_descriptively",
    "segment_bridge",
    "provenance",
    "trainer",
    "answer key",
)


def test_style_specification_and_fonts():
    text = (ROOT / "STYLE.md").read_text(encoding="utf-8")
    assert "Aptos Regular" in text
    assert "DengXian Regular" in text
    assert "14" in text and "10" in text
    assert "11" in text and "9" in text
    assert "8 pt" in text or "8pt" in text
    assert "16 pt" in text or "16pt" in text
    assert "1.25" in text
    fonts = resolve_required_fonts()
    assert fonts.latin_name
    assert fonts.cjk_name
    assert fonts.latin_path.is_file()
    assert fonts.cjk_path.is_file()
    style = apply_research_style(accent=None)
    assert style.accent is None
    assert style.series_color(0, highlight=True) == style.series_color(0)


def test_readme_documents_architecture_without_copying_style():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "build/lululemon/Lululemon_BAV.xlsx" in text
    assert "build/lululemon/research/*.md" in text
    assert "build/lululemon/figures/" in text
    assert "Drivers → Forecast → Valuation → Overview" in text
    assert "STYLE.md" in text
    assert "Aptos Regular" not in text
    assert "DengXian Regular" not in text


def test_lululemon_drivers_from_validated_outputs(tmp_path):
    company = resolve_company("Lululemon")
    fin = prepare_company_input(company, tmp_path / "input")
    view = publish_drivers(fin, tmp_path / "out", display_name=company.name)
    verify_research_artifacts(tmp_path / "out", company.name)
    text = (tmp_path / "out" / "research" / "Lululemon_Drivers.md").read_text(
        encoding="utf-8"
    )
    headings = [line for line in text.splitlines() if line.startswith("#")]
    assert headings == list(expected_sections(company.name))
    lowered = text.lower()
    for term in FORBIDDEN_PROSE:
        assert term not in lowered, term
    assert "forecast" not in lowered
    assert "valuation" not in lowered
    assert "acquisition" not in lowered
    assert "synerg" not in lowered
    conclusions = re.findall(r"^(\d+)\. ", text, flags=re.M)
    assert 3 <= len(conclusions) <= 5
    for period, revenue in REVENUE_ANCHORS.items():
        assert view.revenue[view.periods.index(period)] == revenue
    for period, stores in INDEPENDENT_STORE_TOTALS.items():
        assert view.stores[view.periods.index(period)] == stores
    latest = view.periods[-1]
    latest_i = view.periods.index(latest)
    assert abs(view.revenue_growth[latest_i] - 0.04858971266492295) < 1e-12
    assert abs(view.store_growth[latest_i] - 0.05736636245110821) < 1e-12
    assert abs(view.geo_contributions[latest_i]["americas"] + 0.7660656852780181) < 1e-12
    assert abs(view.geo_contributions[latest_i]["china_mainland"] - 3.716068358083385) < 1e-12
    assert abs(view.geo_contributions[latest_i]["rest_of_world"] - 1.9089685936869283) < 1e-12
    for index, period in enumerate(view.periods):
        if view.consolidated_revenue_growth[index] is None:
            continue
        total = sum(view.geo_contributions[index].values())
        assert abs(total - view.consolidated_revenue_growth[index] * 100) < 1e-9
    assert "−0.766 pp" in text or "-0.766 pp" in text
    assert "5.74%" in text and "4.86%" in text
    assembled = assemble_drivers_view(fin, company.name)
    assert assembled.revenue == view.revenue
    assert assembled.operating_margin == view.operating_margin


def test_accent_disabled_and_enabled_remain_complete(tmp_path):
    company = resolve_company("Lululemon")
    fin = prepare_company_input(company, tmp_path / "input")
    publish_drivers(fin, tmp_path / "plain", display_name=company.name, accent=None)
    publish_drivers(fin, tmp_path / "accent", display_name=company.name, accent="#1F4E79")
    verify_research_artifacts(tmp_path / "plain", company.name)
    verify_research_artifacts(tmp_path / "accent", company.name)
    plain = {
        name: hashlib.sha256(
            (tmp_path / "plain" / "figures" / "drivers" / name).read_bytes()
        ).hexdigest()
        for name in ("growth.png", "geography.png", "margin.png")
    }
    styled = {
        name: hashlib.sha256(
            (tmp_path / "accent" / "figures" / "drivers" / name).read_bytes()
        ).hexdigest()
        for name in ("growth.png", "geography.png", "margin.png")
    }
    assert plain == styled


def test_fast_retailing_does_not_publish_drivers(tmp_path):
    company = resolve_company("FastRetailing")
    fin = prepare_company_input(company, tmp_path / "input")
    publish_company_research(company.name, fin, tmp_path / "out")
    assert not (tmp_path / "out" / "research").exists()
