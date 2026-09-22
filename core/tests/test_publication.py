"""Word/PDF publication from canonical research, without rebuilding analysis."""
from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import zipfile

import pytest

from core.__main__ import main
from core.research.document import (
    publication_filenames,
    publish_company_documents,
    publish_resolved_company,
)
from core.research.drivers import FIGURE_NAMES, placeholder_filenames
from core.research.style import LATIN_FACE

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "build" / "output" / "lululemon"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _copy_research(dest: Path) -> Path:
    dest.mkdir(parents=True)
    shutil.copytree(CANONICAL / "research", dest / "research")
    shutil.copytree(CANONICAL / "figures", dest / "figures")
    return dest


def _company(tmp_path: Path, monkeypatch, name: str = "Lululemon"):
    from core import current_build
    monkeypatch.setattr(current_build, "OUTPUT_ROOT", tmp_path)
    return current_build.resolve_company(name)


def test_publish_help_is_bav_first():
    from core.__main__ import main as cli
    import io
    from contextlib import redirect_stdout
    buf = io.StringIO()
    with pytest.raises(SystemExit) as raised:
        with redirect_stdout(buf):
            cli(["publish", "--help"])
    assert raised.value.code == 0
    text = buf.getvalue()
    assert "BAV" in text
    assert "canonical Drivers research" in text
    assert "Answer Key" not in text


def test_fast_retailing_has_no_publishable_research(capsys):
    before = {
        path: path.read_bytes()
        for path in (ROOT / "build" / "output" / "fast_retailing").rglob("*")
        if path.is_file()
    }
    assert main(["publish", "FastRetailing"]) != 0
    err = capsys.readouterr().err
    assert "No publishable canonical research" in err
    assert "FastRetailing" in err
    assert "legacy" in err.casefold()
    after = {
        path: path.read_bytes()
        for path in (ROOT / "build" / "output" / "fast_retailing").rglob("*")
        if path.is_file()
    }
    assert after == before
    word, pdf = publication_filenames("FastRetailing")
    assert not (ROOT / "build" / "output" / "fast_retailing" / word).exists()
    assert not (ROOT / "build" / "output" / "fast_retailing" / pdf).exists()


def test_missing_markdown_fails_without_inventing(tmp_path, monkeypatch, capsys):
    company = _company(tmp_path, monkeypatch)
    company.output.mkdir(parents=True)
    assert main(["publish", "Lululemon"]) != 0
    err = capsys.readouterr().err
    assert "No publishable canonical research" in err
    assert not list(company.output.glob("*.docx"))
    assert not list(company.output.glob("*.pdf"))
    assert not (company.output / "research").exists()


def test_missing_figure_fails(tmp_path, monkeypatch, capsys):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    (company.output / "figures" / "drivers" / "growth.png").unlink()
    assert main(["publish", "LULU"]) != 0
    err = capsys.readouterr().err
    assert "growth.png" in err
    assert not list(company.output.glob("*.docx"))


def test_broken_reference_fails(tmp_path, monkeypatch, capsys):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    drivers = company.output / "research" / "Lululemon_Drivers.md"
    text = drivers.read_text(encoding="utf-8")
    drivers.write_text(text.replace("growth.png", "missing.png"), encoding="utf-8")
    assert main(["publish", "lululemon"]) != 0
    err = capsys.readouterr().err
    assert "missing.png" in err or "broken" in err.casefold() or "missing" in err.casefold()
    assert not list(company.output.glob("*.docx"))


def test_missing_font_fails(tmp_path, monkeypatch, capsys):
    from core.research import document
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    monkeypatch.setattr(
        document,
        "resolve_required_fonts",
        lambda: (_ for _ in ()).throw(ValueError("required fonts unavailable: Aptos Regular")),
    )
    assert main(["publish", "Lululemon"]) != 0
    assert "required fonts unavailable" in capsys.readouterr().err
    assert not list(company.output.glob("*.docx"))


def test_missing_pandoc_fails(tmp_path, monkeypatch, capsys):
    from core.research import document
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    monkeypatch.setattr(document.shutil, "which", lambda name: None)
    assert main(["publish", "Lululemon"]) != 0
    assert "pandoc" in capsys.readouterr().err
    assert not list(company.output.glob("*.docx"))


def test_converter_failure_preserves_prior_publication(tmp_path, monkeypatch, capsys):
    from core.research import document
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    assert main(["publish", "Lululemon"]) == 0
    word = company.output / "Lululemon_BAV.docx"
    pdf = company.output / "Lululemon_BAV.pdf"
    prior = {word: word.read_bytes(), pdf: pdf.read_bytes()}
    monkeypatch.setattr(
        document,
        "_render_pdf",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("forced converter failure")),
    )
    assert main(["publish", "Lululemon"]) != 0
    assert "publication conversion failed" in capsys.readouterr().err
    assert word.read_bytes() == prior[word]
    assert pdf.read_bytes() == prior[pdf]


def test_publish_does_not_require_trainer_or_mutate_inputs(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    workbook = company.output / "Lululemon_BAV.xlsx"
    workbook.write_bytes(b"workbook-bytes")
    trainer = company.output / "Lululemon_BAV_Trainer.xlsx"
    before = {
        path: path.read_bytes()
        for path in company.output.rglob("*")
        if path.is_file()
    }
    assert main(["publish", "Lululemon"]) == 0
    assert not trainer.exists()
    assert workbook.read_bytes() == b"workbook-bytes"
    for name in placeholder_filenames(company.name):
        path = company.output / "research" / name
        assert path.is_file() and path.stat().st_size == 0
    for name in FIGURE_NAMES:
        path = company.output / "figures" / "drivers" / name
        assert path.read_bytes() == before[path]
    drivers = company.output / "research" / "Lululemon_Drivers.md"
    assert drivers.read_bytes() == before[drivers]


def test_repeat_publish_equivalent_content(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    first = publish_resolved_company(company)
    second = publish_resolved_company(company)
    import fitz
    from docx import Document

    def word_payload(path: Path):
        document = Document(path)
        text = [p.text for p in document.paragraphs]
        tables = [
            [[cell.text for cell in row.cells] for row in table.rows]
            for table in document.tables
        ]
        with zipfile.ZipFile(path) as archive:
            media = {
                name: hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist()
                if name.startswith("word/media/")
            }
        return text, tables, media

    def pdf_payload(path: Path):
        doc = fitz.open(path)
        try:
            text = [page.get_text() for page in doc]
            images = []
            for page in doc:
                for xref, *_rest in page.get_images():
                    images.append(hashlib.sha256(doc.extract_image(xref)["image"]).hexdigest())
            return text, images, doc.page_count
        finally:
            doc.close()

    assert word_payload(first.word) == word_payload(second.word)
    assert pdf_payload(first.pdf) == pdf_payload(second.pdf)


def test_lululemon_publication_preserves_analysis(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    published = publish_resolved_company(company)
    from docx import Document
    import fitz

    document = Document(published.word)
    word_text = "\n".join(p.text for p in document.paragraphs)
    table_text = "\n".join(
        cell.text for table in document.tables for row in table.rows for cell in row.cells
    )
    combined = word_text + "\n" + table_text
    required = (
        "Lululemon — Drivers",
        "Context",
        "Growth",
        "Geography",
        "Margin",
        "Conclusions",
        "Limits",
        "Lululemon BAV",
        "Δgross margin",
        "−Δ(SG&A/revenue)",
        "Revenue = stores × company-wide revenue per store",
        "FY2024",
        "2 February 2025",
        "Form 10-K pp. 28–29",
        "footprint and intensity identity",
        "component operating-margin identity",
    )
    for item in required:
        assert item in combined, item
    assert "Forecast" not in [p.text for p in document.paragraphs if p.text.startswith("Forecast")]
    assert "Valuation" not in word_text
    assert "# Overview" not in word_text
    doc = fitz.open(published.pdf)
    try:
        pdf_text = "\n".join(page.get_text() for page in doc)
        fonts = {font[3] or font[4] for page in doc for font in page.get_fonts()}
        images = sum(len(page.get_images()) for page in doc)
        assert doc.page_count >= 3
    finally:
        doc.close()
    for item in required:
        assert item in pdf_text, item
    assert images >= 3
    assert any(LATIN_FACE.casefold() in str(name).casefold() for name in fonts)
    with zipfile.ZipFile(published.word) as archive:
        assert sum(1 for name in archive.namelist() if name.startswith("word/media/")) >= 3


def test_publish_writes_only_under_canonical_output(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    published = publish_company_documents("LULU")
    assert published.word.parent == company.output
    assert published.pdf.parent == company.output
    assert published.word.name == "Lululemon_BAV.docx"
    assert published.pdf.name == "Lululemon_BAV.pdf"
    assert company.output == tmp_path / "lululemon"
