"""Cache-preserving practice-cell fill updates via OOXML package edits.

openpyxl workbook saves do not reliably retain formula cached ``<v>`` values.
Check therefore recolors cells by rewriting only style references in the XLSX
ZIP, leaving formula text and cached results intact.
"""

from __future__ import annotations

import os
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

SSML = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OD_RELS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

REQUIRED_FILLS = ("FFFF00", "C8E6C9", "FFC7CE")


@dataclass(frozen=True)
class CellFillUpdate:
    sheet: str
    cell: str
    rgb: str


def _norm_rgb(raw: str | None) -> str:
    if not raw:
        return ""
    s = str(raw).upper().lstrip("#")
    if len(s) == 8:
        s = s[2:]
    return s[-6:] if len(s) >= 6 else s


def _sheet_path_map(zf: zipfile.ZipFile) -> dict[str, str]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    sheets_el = wb.find(f"{{{SSML}}}sheets")
    if sheets_el is None:
        raise FileNotFoundError("workbook.xml missing <sheets>")

    rid_to_target: dict[str, str] = {}
    for rel in rels:
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target", "")
        if rid and target:
            rid_to_target[rid] = target

    mapping: dict[str, str] = {}
    for sheet in sheets_el:
        name = sheet.attrib.get("name")
        rid = sheet.attrib.get(f"{{{OD_RELS}}}id")
        if not name or not rid:
            continue
        target = rid_to_target.get(rid)
        if not target:
            raise FileNotFoundError(f"Missing relationship for sheet {name!r}")
        target = target.lstrip("/")
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        mapping[name] = target
    return mapping


def _ensure_solid_fills(styles_root: ET.Element) -> dict[str, int]:
    fills_el = styles_root.find(f"{{{SSML}}}fills")
    if fills_el is None:
        fills_el = ET.SubElement(styles_root, f"{{{SSML}}}fills")

    rgb_to_id: dict[str, int] = {}
    fills = list(fills_el)
    for idx, fill in enumerate(fills):
        pattern = fill.find(f"{{{SSML}}}patternFill")
        if pattern is None or pattern.attrib.get("patternType") != "solid":
            continue
        fg = pattern.find(f"{{{SSML}}}fgColor")
        if fg is None:
            continue
        rgb = _norm_rgb(fg.attrib.get("rgb") or fg.attrib.get("indexed"))
        if rgb and rgb not in rgb_to_id:
            rgb_to_id[rgb] = idx

    for rgb in REQUIRED_FILLS:
        if rgb in rgb_to_id:
            continue
        fill = ET.SubElement(fills_el, f"{{{SSML}}}fill")
        pattern = ET.SubElement(fill, f"{{{SSML}}}patternFill")
        pattern.set("patternType", "solid")
        fg = ET.SubElement(pattern, f"{{{SSML}}}fgColor")
        fg.set("rgb", f"00{rgb}")
        rgb_to_id[rgb] = len(list(fills_el)) - 1

    fills_el.set("count", str(len(list(fills_el))))
    return rgb_to_id


def _clone_xf_with_fill(src_xf: ET.Element, fill_id: int) -> ET.Element:
    xf = deepcopy(src_xf)
    xf.set("fillId", str(fill_id))
    xf.set("applyFill", "1")
    return xf


def _ensure_cell_xf(
    styles_root: ET.Element,
    original_style_idx: int,
    fill_id: int,
    style_cache: dict[tuple[int, int], int],
) -> int:
    key = (original_style_idx, fill_id)
    if key in style_cache:
        return style_cache[key]

    cell_xfs = styles_root.find(f"{{{SSML}}}cellXfs")
    if cell_xfs is None:
        raise FileNotFoundError("styles.xml missing <cellXfs>")
    xfs = list(cell_xfs)
    if original_style_idx < 0 or original_style_idx >= len(xfs):
        raise ValueError(f"Invalid style index {original_style_idx}")

    # Reuse an existing xf that already matches the desired fill and same base attrs.
    src = xfs[original_style_idx]
    for idx, xf in enumerate(xfs):
        if int(xf.attrib.get("fillId", "0")) != fill_id:
            continue
        # Same non-fill identity as the source style.
        same = True
        for attr in ("numFmtId", "fontId", "borderId", "xfId", "quotePrefix", "pivotButton"):
            if xf.attrib.get(attr, src.attrib.get(attr, "0")) != src.attrib.get(attr, "0"):
                same = False
                break
        if not same:
            continue
        # Compare child elements loosely by serialized form excluding fill-only attrs already checked
        src_children = [
            ET.tostring(c, encoding="unicode")
            for c in list(src)
            if not c.tag.endswith("}fill")
        ]
        xf_children = [
            ET.tostring(c, encoding="unicode")
            for c in list(xf)
            if not c.tag.endswith("}fill")
        ]
        if src_children == xf_children and (
            int(xf.attrib.get("fillId", "0")) == fill_id
        ):
            # Also require alignment/protection children match source if present
            style_cache[key] = idx
            return idx

    new_xf = _clone_xf_with_fill(src, fill_id)
    cell_xfs.append(new_xf)
    new_idx = len(list(cell_xfs)) - 1
    cell_xfs.set("count", str(new_idx + 1))
    style_cache[key] = new_idx
    return new_idx


def _update_sheet_cells(
    sheet_root: ET.Element,
    updates_for_sheet: list[CellFillUpdate],
    styles_root: ET.Element,
    rgb_to_fill_id: dict[str, int],
    style_cache: dict[tuple[int, int], int],
) -> None:
    by_addr = {u.cell.upper(): u for u in updates_for_sheet}
    found: set[str] = set()
    for cell_el in sheet_root.iter(f"{{{SSML}}}c"):
        addr = (cell_el.attrib.get("r") or "").upper()
        if addr not in by_addr:
            continue
        update = by_addr[addr]
        rgb = _norm_rgb(update.rgb)
        if rgb not in rgb_to_fill_id:
            raise ValueError(f"Unsupported fill RGB {update.rgb!r}")
        original_style = int(cell_el.attrib.get("s", "0"))
        fill_id = rgb_to_fill_id[rgb]
        new_style = _ensure_cell_xf(styles_root, original_style, fill_id, style_cache)
        cell_el.set("s", str(new_style))
        found.add(addr)

    missing = sorted(set(by_addr) - found)
    if missing:
        raise FileNotFoundError(
            f"Practice cell(s) not found on sheet {updates_for_sheet[0].sheet!r}: "
            + ", ".join(missing)
        )


def apply_fill_updates(workbook_path: Path, updates: list[CellFillUpdate]) -> None:
    """Apply solid RGB fills to named cells without rewriting formula caches."""
    workbook_path = Path(workbook_path)
    if not updates:
        return

    ET.register_namespace("", SSML)
    ET.register_namespace("r", OD_RELS)

    with zipfile.ZipFile(workbook_path, "r") as zf:
        sheet_map = _sheet_path_map(zf)
        styles_xml = zf.read("xl/styles.xml")
        member_data = {info.filename: zf.read(info.filename) for info in zf.infolist()}

    styles_root = ET.fromstring(styles_xml)
    rgb_to_fill_id = _ensure_solid_fills(styles_root)
    style_cache: dict[tuple[int, int], int] = {}

    by_sheet: dict[str, list[CellFillUpdate]] = {}
    for upd in updates:
        by_sheet.setdefault(upd.sheet, []).append(upd)

    for sheet_name, sheet_updates in by_sheet.items():
        sheet_path = sheet_map.get(sheet_name)
        if not sheet_path:
            raise FileNotFoundError(f"Sheet not found in workbook: {sheet_name!r}")
        if sheet_path not in member_data:
            raise FileNotFoundError(f"Missing worksheet part: {sheet_path}")
        sheet_root = ET.fromstring(member_data[sheet_path])
        _update_sheet_cells(
            sheet_root, sheet_updates, styles_root, rgb_to_fill_id, style_cache
        )
        member_data[sheet_path] = ET.tostring(
            sheet_root, encoding="utf-8", xml_declaration=True
        )

    member_data["xl/styles.xml"] = ET.tostring(
        styles_root, encoding="utf-8", xml_declaration=True
    )

    fd, tmp_name = tempfile.mkstemp(
        suffix=".xlsx",
        prefix=workbook_path.stem + "_fills_",
        dir=str(workbook_path.parent),
    )
    os.close(fd)
    tmp_path = Path(tmp_name)
    try:
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zf_out:
            for name, data in member_data.items():
                zf_out.writestr(name, data)
        os.replace(tmp_path, workbook_path)
    except Exception:
        tmp_path.unlink(missing_ok=True)
        raise
