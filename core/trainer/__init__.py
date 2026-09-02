"""Trainer subpackage."""

from .checker import CheckResult, check_component, check_dependencies
from .hints import HintResult, reveal_answer, show_hint
from .semantic_io import answer_key_path_for, load_semantic_map, resolve_pair_paths
from .workbook import TrainingWorkbookGenerator, build_training_workbook

__all__ = [
    "CheckResult",
    "HintResult",
    "TrainingWorkbookGenerator",
    "answer_key_path_for",
    "build_training_workbook",
    "check_component",
    "check_dependencies",
    "load_semantic_map",
    "resolve_pair_paths",
    "reveal_answer",
    "show_hint",
]
