"""BAV engine — semantic component catalog and reference model builder."""

from .component_catalog import COMPONENT_CATALOG, ComponentSpec, catalog_by_id
from .reference_model import ReferenceModelBuilder
from .semantic_map import ResolvedComponent, SemanticMap

__all__ = [
    "COMPONENT_CATALOG",
    "ComponentSpec",
    "ReferenceModelBuilder",
    "ResolvedComponent",
    "SemanticMap",
    "catalog_by_id",
]
