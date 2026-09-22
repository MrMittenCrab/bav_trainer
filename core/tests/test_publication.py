"""Word/PDF publication from canonical research, without rebuilding analysis."""
from __future__ import annotations

from io import BytesIO
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
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


def _word_payload(data: bytes) -> dict:
    from docx import Document

    document = Document(BytesIO(data))
    text = [paragraph.text for paragraph in document.paragraphs]
    tables = [
        [[cell.text for cell in row.cells] for row in table.rows]
        for table in document.tables
    ]
    sections = [
        (
            int(section.page_width),
            int(section.page_height),
            str(section.orientation),
        )
        for section in document.sections
    ]
    with zipfile.ZipFile(BytesIO(data)) as archive:
        media = {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name.startswith("word/media/")
        }
        core = (
            archive.read("docProps/core.xml")
            if "docProps/core.xml" in archive.namelist()
            else b""
        )
    return {
        "text": text,
        "tables": tables,
        "sections": sections,
        "media": media,
        "core": hashlib.sha256(core).hexdigest(),
    }


def _pdf_payload(data: bytes) -> dict:
    import fitz

    doc = fitz.open(stream=data, filetype="pdf")
    try:
        text = [page.get_text() for page in doc]
        images = []
        for page in doc:
            for xref, *_rest in page.get_images():
                images.append(hashlib.sha256(doc.extract_image(xref)["image"]).hexdigest())
        meta = {
            key: doc.metadata.get(key)
            for key in ("creationDate", "modDate", "producer", "creator")
        }
        return {"text": text, "images": images, "pages": doc.page_count, "meta": meta}
    finally:
        doc.close()


def _content_equal(first_word: bytes, first_pdf: bytes, second_word: bytes, second_pdf: bytes) -> bool:
    word_a, word_b = _word_payload(first_word), _word_payload(second_word)
    pdf_a, pdf_b = _pdf_payload(first_pdf), _pdf_payload(second_pdf)
    return (
        word_a["text"] == word_b["text"]
        and word_a["tables"] == word_b["tables"]
        and word_a["sections"] == word_b["sections"]
        and word_a["media"] == word_b["media"]
        and pdf_a["text"] == pdf_b["text"]
        and pdf_a["images"] == pdf_b["images"]
        and pdf_a["pages"] == pdf_b["pages"]
    )


def _metadata_diff(first_word: bytes, first_pdf: bytes, second_word: bytes, second_pdf: bytes) -> dict:
    return {
        "word_core": _word_payload(first_word)["core"] != _word_payload(second_word)["core"],
        "pdf_meta": _pdf_payload(first_pdf)["meta"] != _pdf_payload(second_pdf)["meta"],
        "word_sha": hashlib.sha256(first_word).hexdigest() != hashlib.sha256(second_word).hexdigest(),
        "pdf_sha": hashlib.sha256(first_pdf).hexdigest() != hashlib.sha256(second_pdf).hexdigest(),
    }


def _publish_cli_hiding(module: str, output_root: Path, company: str = "Lululemon"):
    script = f"""
import sys
from pathlib import Path

class _Block:
    def find_spec(self, name, path=None, target=None):
        root = {module!r}
        if name == root or name.startswith(root + "."):
            raise ImportError(root)
        return None

sys.meta_path.insert(0, _Block())
from core import current_build
current_build.OUTPUT_ROOT = Path({str(output_root)!r})
from core.__main__ import main
raise SystemExit(main(["publish", {company!r}]))
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ROOT), env["PYTHONPATH"]] if env.get("PYTHONPATH") else [str(ROOT)]
    )
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


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


def test_valid_document_references_are_preserved(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    note = company.output / "research" / "source-note.md"
    note.write_text("# Source note\n\nItem 7 locator retained.\n", encoding="utf-8")
    drivers = company.output / "research" / "Lululemon_Drivers.md"
    text = drivers.read_text(encoding="utf-8")
    drivers.write_text(
        text.replace(
            "## Context\n",
            "## Context\n\nSee the [source note](source-note.md#source-note) and [Context](#context).\n",
        ),
        encoding="utf-8",
    )
    published = publish_resolved_company(company)
    from docx import Document
    import fitz

    word_text = "\n".join(p.text for p in Document(published.word).paragraphs)
    assert "source note (source-note.md)" in word_text
    assert "Context" in word_text
    doc = fitz.open(published.pdf)
    try:
        pdf_text = "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()
    assert "source note (source-note.md)" in pdf_text
    assert "Context" in pdf_text


def test_missing_local_document_reference_fails(tmp_path, monkeypatch, capsys):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    drivers = company.output / "research" / "Lululemon_Drivers.md"
    text = drivers.read_text(encoding="utf-8")
    drivers.write_text(
        text.replace("## Context\n", "## Context\n\nSee [missing note](missing-note.md).\n"),
        encoding="utf-8",
    )
    prior = {
        path: path.read_bytes()
        for path in company.output.rglob("*")
        if path.is_file() and path.suffix in {".docx", ".pdf"}
    }
    assert main(["publish", "Lululemon"]) != 0
    err = capsys.readouterr().err
    assert "missing-note.md" in err
    assert str(drivers) in err or "Lululemon_Drivers.md" in err
    assert "broken document reference" in err
    assert not list(company.output.glob("*.docx"))
    for path, data in prior.items():
        assert path.read_bytes() == data


def test_invalid_document_anchor_fails(tmp_path, monkeypatch, capsys):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    drivers = company.output / "research" / "Lululemon_Drivers.md"
    text = drivers.read_text(encoding="utf-8")
    drivers.write_text(
        text.replace("## Context\n", "## Context\n\nSee [missing heading](#no-such-heading).\n"),
        encoding="utf-8",
    )
    assert main(["publish", "Lululemon"]) != 0
    err = capsys.readouterr().err
    assert "no-such-heading" in err
    assert "Lululemon_Drivers.md" in err
    assert "invalid anchor" in err
    assert not list(company.output.glob("*.docx"))


def test_invalid_anchor_on_local_markdown_fails(tmp_path, monkeypatch, capsys):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    (company.output / "research" / "source-note.md").write_text(
        "# Source note\n\nPresent.\n", encoding="utf-8"
    )
    drivers = company.output / "research" / "Lululemon_Drivers.md"
    text = drivers.read_text(encoding="utf-8")
    drivers.write_text(
        text.replace(
            "## Context\n",
            "## Context\n\nSee [bad target](source-note.md#absent-section).\n",
        ),
        encoding="utf-8",
    )
    assert main(["publish", "Lululemon"]) != 0
    err = capsys.readouterr().err
    assert "source-note.md#absent-section" in err
    assert "invalid anchor" in err
    assert "Lululemon_Drivers.md" in err
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


def test_repeat_comparison_detects_content_difference(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    first = publish_resolved_company(company)
    first_word = first.word.read_bytes()
    first_pdf = first.pdf.read_bytes()
    drivers = company.output / "research" / "Lululemon_Drivers.md"
    drivers.write_text(
        drivers.read_text(encoding="utf-8").replace(
            "## Context\n",
            "## Context\n\nDeliberate publication difference for comparison.\n",
        ),
        encoding="utf-8",
    )
    second = publish_resolved_company(company)
    second_word = second.word.read_bytes()
    second_pdf = second.pdf.read_bytes()
    assert not _content_equal(first_word, first_pdf, second_word, second_pdf)
    assert "Deliberate publication difference for comparison" in "\n".join(
        _word_payload(second_word)["text"]
    )


def test_repeat_publish_equivalent_content(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    first = publish_resolved_company(company)
    first_word = first.word.read_bytes()
    first_pdf = first.pdf.read_bytes()
    second = publish_resolved_company(company)
    second_word = second.word.read_bytes()
    second_pdf = second.pdf.read_bytes()
    assert _content_equal(first_word, first_pdf, second_word, second_pdf)
    metadata = _metadata_diff(first_word, first_pdf, second_word, second_pdf)
    assert set(metadata) == {"word_core", "pdf_meta", "word_sha", "pdf_sha"}


def test_missing_python_docx_reaches_cli(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    assert main(["publish", "Lululemon"]) == 0
    word = company.output / "Lululemon_BAV.docx"
    pdf = company.output / "Lululemon_BAV.pdf"
    prior = {word: word.read_bytes(), pdf: pdf.read_bytes()}
    result = _publish_cli_hiding("docx", tmp_path)
    assert result.returncode != 0
    err = result.stderr
    assert "python-docx" in err
    assert "pip install -r requirements-trainer.txt" in err
    assert "README" in err
    assert word.read_bytes() == prior[word]
    assert pdf.read_bytes() == prior[pdf]


def test_missing_reportlab_reaches_cli(tmp_path, monkeypatch):
    company = _company(tmp_path, monkeypatch)
    _copy_research(company.output)
    assert main(["publish", "Lululemon"]) == 0
    word = company.output / "Lululemon_BAV.docx"
    pdf = company.output / "Lululemon_BAV.pdf"
    prior = {word: word.read_bytes(), pdf: pdf.read_bytes()}
    result = _publish_cli_hiding("reportlab", tmp_path)
    assert result.returncode != 0
    err = result.stderr
    assert "reportlab" in err
    assert "pip install -r requirements-trainer.txt" in err
    assert "README" in err
    assert word.read_bytes() == prior[word]
    assert pdf.read_bytes() == prior[pdf]


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
