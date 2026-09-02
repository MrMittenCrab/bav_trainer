"""Load runtime semantic component maps from workbooks and sidecars."""

from __future__ import annotations

from pathlib import Path

from ..engine.semantic_map import ResolvedComponent, SemanticMap


def component_map_path_for(workbook_path: Path) -> Path:
    """Sidecar path: foo.xlsx -> foo.component_map.json"""
    return workbook_path.with_suffix(".component_map.json")


def resolve_pair_paths(output_path: Path) -> tuple[Path, Path]:
    """Resolve Trainer and Answer Key paths from a requested build output.

    If the stem already ends with ``_Trainer``, keep it and derive ``_Answer_Key``.
    Otherwise append ``_Trainer`` / ``_Answer_Key`` to the stem.
    """
    output_path = Path(output_path)
    suffix = output_path.suffix or ".xlsx"
    stem = output_path.stem
    parent = output_path.parent
    if stem.endswith("_Trainer"):
        company = stem[: -len("_Trainer")]
    else:
        company = stem
    trainer_path = parent / f"{company}_Trainer{suffix}"
    answer_key_path = parent / f"{company}_Answer_Key{suffix}"
    return trainer_path, answer_key_path


def answer_key_path_for(training_path: Path) -> Path:
    """Infer matching Answer Key path from a Trainer workbook name."""
    _, answer_key_path = resolve_pair_paths(training_path)
    return answer_key_path


def reference_workbook_path(training_path: Path) -> Path:
    """Backward-compatible alias — Answer Key replaces the old reference workbook."""
    return answer_key_path_for(training_path)


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
