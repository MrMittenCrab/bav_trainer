"""Lululemon Drivers research publication from validated BAV outputs."""
from __future__ import annotations

import hashlib
import json
import re
import warnings
from datetime import date
from pathlib import Path

import pytest
from matplotlib import ft2font
from PIL import Image

from core.current_build import prepare_company_input, resolve_company
from core.ingestion.management_kpi_enrichment import inspect_source_pdf
from core.research.drivers import (
    _label_for,
    assemble_drivers_view,
    expected_sections,
    publish_drivers,
    render_drivers_markdown,
)
from core.research.publish import publish_company_research, verify_research_artifacts
from core.research.style import (
    CJK_FACE,
    FIGURE_DPI,
    FIGURE_SIZE,
    LABEL_PT,
    LATIN_FACE,
    MIN_WORD_GAP_EM,
    PT,
    TITLE_PT,
    _ink_gap_px,
    apply_research_style,
    finish_figure,
    new_figure,
    resolve_required_fonts,
    spaced,
)
from core.tests.test_lululemon_benchmark import REVENUE_ANCHORS
from core.tests.test_management_kpi_admission import EXTRACTED, SOURCE
from core.tests.test_operating_kpi_facts import INDEPENDENT_STORE_TOTALS

ROOT = Path(__file__).resolve().parents[2]
FIFTY_THREE_WEEK_END = date(2025, 2, 2)
DISPLAYED_FY2024_END = date(2024, 1, 28)
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
    assert "build/output/lululemon/Lululemon_BAV.xlsx" in text
    assert "build/output/lululemon/research/*.md" in text
    assert "build/output/lululemon/figures/" in text
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
    latest_i = view.periods.index(latest)
    assert view.labels[latest_i] == "FY2025"
    assert view.labels[view.periods.index(FIFTY_THREE_WEEK_END)] == "FY2024"
    gm = view.gross_margin_change[latest_i]
    burden = view.net_operating_expense_burden_change[latest_i]
    om = view.operating_margin_change[latest_i]
    assert gm is not None and burden is not None and om is not None
    assert abs(om - (gm - burden)) < 1e-12
    assert "operating-margin change was -3.75 pp" in text
    assert "gross-margin change (-2.62 pp)" in text
    assert "net-operating-expense-burden change (+1.13 pp)" in text
    assert "approximately $275 million" in text
    assert "Form 10-K pp. 28–29" in text or "Form 10-K pp. 28-29" in text
    assert "Management explanations of the latest operating-margin movement are unavailable." not in text
    assert "SG&A / revenue" in text
    assert "Impairment / revenue" in text
    assert "company-wide revenue per store" in text.lower()
    assert "not store productivity" in text.lower()
    assert "unestablished" in text.lower()
    assert "Residuals are computed from the validated reconstructions." in text
    assert "Direction" in text and "Disclosure" in text
    assert "geographic revenue reconstruction" in text.lower()
    assert "footprint and intensity identity" in text.lower()
    assert view.sga_ratio[-1] == pytest.approx(4066556.0 / 11102600.0)
    assert view.impairment[1] == 407913.0
    assert view.operating_margin_residual[-1] == 0.0
    assert view.geo_residual is not None
    assert all(value == 0.0 for value in view.geo_residual)
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


def test_drivers_calendar_limitation_reconciles_53_week_year(tmp_path):
    extract = json.loads(
        (EXTRACTED / "LULU_FY2024_management_kpis.json").read_text(encoding="utf-8")
    )
    assert extract["report"]["fiscal_year"] == 2024
    assert extract["report"]["fiscal_year_end"] == FIFTY_THREE_WEEK_END.isoformat()
    assert "53 weeks" in extract["report"]["reporting_basis"]
    fy2024_definition = next(
        item["definition"]
        for item in extract["kpi_definitions"]
        if item["metric_id"] == "comparable_sales_growth"
    )
    assert "53rd week is excluded from comparable sales" in fy2024_definition
    fy2025 = json.loads(
        (EXTRACTED / "LULU_FY2025_management_kpis.json").read_text(encoding="utf-8")
    )
    fy2025_definition = next(
        item["definition"]
        for item in fy2025["kpi_definitions"]
        if item["metric_id"] == "comparable_sales_growth"
    )
    assert "shifted by one week" in fy2025_definition
    inspection = inspect_source_pdf(SOURCE / "LULU_FY2024_Annual_Report.pdf")
    assert 2024 in inspection.fifty_three_week_years
    assert 2023 in inspection.fifty_two_week_years
    company = resolve_company("Lululemon")
    fin = prepare_company_input(company, tmp_path / "input")
    assert _label_for(fin, FIFTY_THREE_WEEK_END) == "FY2024"
    assert _label_for(fin, DISPLAYED_FY2024_END) == "FY2023"
    adjustments = {
        (item.period, item.calendar_week_adjustment)
        for item in fin.historical_operating_kpis.management_observations
        if item.family == "comparable_sales_growth"
        and item.geography == "global"
        and item.basis == "reported"
        and item.population == "company_operated_stores_and_ecommerce"
    }
    assert (FIFTY_THREE_WEEK_END, "excluded") in adjustments
    assert (DISPLAYED_FY2024_END, "included") in adjustments
    view = assemble_drivers_view(fin, company.name)
    assert view.fifty_three_week_period == FIFTY_THREE_WEEK_END
    assert view.labels[view.periods.index(FIFTY_THREE_WEEK_END)] == "FY2024"
    assert view.labels[view.periods.index(DISPLAYED_FY2024_END)] == "FY2023"
    assert view.issuer_fiscal_name == "fiscal 2024"
    text = render_drivers_markdown(view)
    assert "| FY2023 | 28 January 2024 |" in text
    assert "| FY2024 | 2 February 2025 |" in text
    week_sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=\.)\s+", text)
        if "53-week" in sentence
    ]
    assert len(week_sentences) == 1
    assert week_sentences[0].startswith("FY2024, the year ended 2 February 2025, is a 53-week year")
    assert "FY2025 is a 53-week" not in text
    assert "FY2023 is a 53-week" not in text
    assert "exclude or realign that extra week" in text
    publish_drivers(fin, tmp_path / "out", display_name=company.name)
    published = (tmp_path / "out" / "research" / "Lululemon_Drivers.md").read_text(
        encoding="utf-8"
    )
    assert published == text


def _font_has(path: Path, codepoint: int) -> bool:
    return codepoint in ft2font.FT2Font(str(path)).get_charmap()


def _interior_ink_gaps(path: Path, y0: int, y1: int, *, min_gap: int = 2) -> list[int]:
    image = Image.open(path).convert("L")
    strip = image.crop((0, y0, image.size[0], y1))
    cols = [
        any(strip.getpixel((x, row)) < 200 for row in range(strip.size[1]))
        for x in range(strip.size[0])
    ]
    gaps: list[int] = []
    index = 0
    width = len(cols)
    while index < width:
        if cols[index]:
            index += 1
            continue
        end = index
        while end < width and not cols[end]:
            end += 1
        if index > 0 and end < width and end - index >= min_gap:
            gaps.append(end - index)
        index = end
    return gaps


def test_figure_word_spacing_uses_required_fonts_and_visible_gaps(tmp_path):
    fonts = resolve_required_fonts()
    assert fonts.latin_name == LATIN_FACE
    assert fonts.cjk_name == CJK_FACE
    assert fonts.latin_path.name == "Aptos.ttf"
    assert fonts.cjk_path.name == "Deng.ttf"
    assert _font_has(fonts.latin_path, 0x20)
    assert _font_has(fonts.cjk_path, 0x20)
    assert not _font_has(fonts.latin_path, 0x2002)
    assert not _font_has(fonts.cjk_path, 0x2002)

    style = apply_research_style(accent=None)
    assert style.fonts.latin_path == fonts.latin_path
    assert style.fonts.cjk_path == fonts.cjk_path
    assert set(style.word_space) == {" "}
    assert "\u2002" not in style.word_space
    assert len(style.word_space) > 1
    assert spaced("Revenue growth") == f"Revenue{style.word_space}growth"
    assert "\u2002" not in spaced("Revenue growth")

    min_title = TITLE_PT * FIGURE_DPI * PT * MIN_WORD_GAP_EM
    min_note = LABEL_PT * FIGURE_DPI * PT * MIN_WORD_GAP_EM
    assert _ink_gap_px("Revenue growth", pt=TITLE_PT) < min_title
    assert _ink_gap_px(spaced("Revenue growth"), pt=TITLE_PT) >= min_title
    assert _ink_gap_px(spaced("store-count growth"), pt=LABEL_PT) >= min_note

    title = "Revenue growth, store-count growth, and reported comparable sales"
    source = (
        "Source: Lululemon BAV income statement and company-operated store counts.\n"
        "Comparable sales use the reported global definition of each year."
    )
    fig, ax = new_figure(style)
    ax.bar([0, 1], [10, 20], color=style.series_color(0), label="Consolidated revenue growth")
    ax.set_xticks([0, 1], ["FY2025\n2 Feb 2025", "FY2024\n28 Jan 2024"])
    ax.set_ylabel("Percentage-point contribution")
    ax.legend(loc="upper right")
    path = tmp_path / "spacing.png"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        finish_figure(fig, ax, style, title, source, path)
    missing = [
        str(item.message)
        for item in caught
        if "missing from font" in str(item.message) or "Glyph" in str(item.message)
    ]
    assert missing == []
    assert path.is_file() and path.stat().st_size > 0

    image = Image.open(path)
    assert image.size == (
        int(FIGURE_SIZE[0] * FIGURE_DPI),
        int(FIGURE_SIZE[1] * FIGURE_DPI),
    )
    title_gaps = _interior_ink_gaps(path, 90, 125)
    note_line_one = _interior_ink_gaps(path, 626, 644)
    note_line_two = _interior_ink_gaps(path, 652, 672)
    assert max(title_gaps) >= min_title, (title_gaps, min_title)
    assert max(note_line_one) >= min_note, (note_line_one, min_note)
    assert max(note_line_two) >= min_note, (note_line_two, min_note)
    assert sum(gap >= min_title for gap in title_gaps) >= 3
    assert sum(gap >= min_note for gap in note_line_one) >= 3
