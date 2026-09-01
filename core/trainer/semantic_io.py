"""Load runtime semantic component maps from workbooks and sidecars."""

from __future__ import annotations

from pathlib import Path

from ..engine.semantic_map import ResolvedComponent, SemanticMap


def component_map_path_for(workbook_path: Path) -> Path:
    """Sidecar path: foo.xlsx -> foo.component_map.json"""
    return workbook_path.with_suffix(".component_map.json")


def reference_workbook_path(training_path: Path) -> Path:
    """Infer reference workbook path from a training workbook name."""
    stem = training_path.stem
    if stem.endswith("_Trainer"):
        return training_path.with_name(stem + "_reference.xlsx")
    return training_path.with_name(stem + "_reference.xlsx")


def load_semantic_map(workbook_path: Path) -> SemanticMap:
    """Load component map from sidecar or embedded _ComponentMap sheet."""
    sidecar = component_map_path_for(workbook_path)
    if sidecar.exists():
        return SemanticMap.load_json(sidecar)
    return SemanticMap.from_workbook(workbook_path)


def get_component(workbook_path: Path, component_id: str) -> ResolvedComponent:
    return load_semantic_map(workbook_path).get(component_id)


def parse_cell_ref(cell_ref: str) -> tuple[int, int]:
    from openpyxl.utils import column_index_from_string

    col = "".join(c for c in cell_ref if c.isalpha())
    row = int("".join(c for c in cell_ref if c.isdigit()))
    return row, column_index_from_string(col)
