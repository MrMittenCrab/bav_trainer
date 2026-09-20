"""Load runtime semantic component maps from workbooks and sidecars."""

from __future__ import annotations

from pathlib import Path

from ..engine.semantic_map import ResolvedComponent, SemanticMap

_BAV_TRAINER_SUFFIX = "_BAV_Trainer"
_ANSWER_KEY_SUFFIX = "_Answer_Key"
_BAV_SUFFIX = "_BAV"
_TRAINER_SUFFIX = "_Trainer"


def supporting_dir(workbook_path: Path) -> Path:
    return Path(workbook_path).parent / "supporting"


def sidecar_paths(workbook_path: Path) -> tuple[Path, Path, Path]:
    """Return component_map, assumptions, and rowmap paths for a workbook."""
    workbook_path = Path(workbook_path)
    supporting = supporting_dir(workbook_path)
    supporting_map = supporting / "component_map.json"
    if supporting_map.is_file() or (supporting / "assumptions.json").is_file() or (
        supporting / "rowmap.json"
    ).is_file():
        return (
            supporting_map,
            supporting / "assumptions.json",
            supporting / "rowmap.json",
        )
    return (
        workbook_path.with_suffix(".component_map.json"),
        workbook_path.with_suffix(".assumptions.json"),
        workbook_path.parent / "rowmap.json",
    )


def component_map_path_for(workbook_path: Path) -> Path:
    """Sidecar path: supporting/component_map.json or foo.component_map.json."""
    return sidecar_paths(workbook_path)[0]


def company_stem_from_output(stem: str) -> str:
    """Strip product suffixes from a requested build stem."""
    for suffix in (
        _BAV_TRAINER_SUFFIX,
        _ANSWER_KEY_SUFFIX,
        _BAV_SUFFIX,
        _TRAINER_SUFFIX,
    ):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def resolve_pair_paths(output_path: Path) -> tuple[Path, Path]:
    """Resolve Trainer and BAV paths from a requested build output.

    Returns ``(trainer_path, bav_path)``. Ordinary and explicit builds use
    ``<Company>_BAV.xlsx`` and ``<Company>_BAV_Trainer.xlsx``.
    """
    output_path = Path(output_path)
    suffix = output_path.suffix or ".xlsx"
    company = company_stem_from_output(output_path.stem)
    parent = output_path.parent
    trainer_path = parent / f"{company}{_BAV_TRAINER_SUFFIX}{suffix}"
    bav_path = parent / f"{company}{_BAV_SUFFIX}{suffix}"
    return trainer_path, bav_path


def bav_path_for(training_path: Path) -> Path:
    """Infer matching BAV, falling back to a committed legacy Answer Key."""
    training_path = Path(training_path)
    _, bav_path = resolve_pair_paths(training_path)
    if bav_path.exists():
        return bav_path
    company = company_stem_from_output(training_path.stem)
    legacy = training_path.parent / f"{company}{_ANSWER_KEY_SUFFIX}{training_path.suffix or '.xlsx'}"
    if legacy.exists():
        return legacy
    return bav_path


def answer_key_path_for(training_path: Path) -> Path:
    """Backward-compatible alias — the BAV replaces the former Answer Key."""
    return bav_path_for(training_path)


def reference_workbook_path(training_path: Path) -> Path:
    """Backward-compatible alias for the matching professional BAV."""
    return bav_path_for(training_path)


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
