"""BAV engine — semantic component catalog and reference model builder."""

from .component_catalog import (
    COMPONENT_CATALOG,
    ComponentFamily,
    ComponentSpec,
    catalog_by_id,
    expand_historical_specs,
)
from .reference_model import ReferenceModelBuilder
from .semantic_map import ResolvedComponent, SemanticMap

__all__ = [
    "COMPONENT_CATALOG",
    "ComponentFamily",
    "ComponentSpec",
    "ReferenceModelBuilder",
    "ResolvedComponent",
    "SemanticMap",
    "catalog_by_id",
    "expand_historical_specs",
]
