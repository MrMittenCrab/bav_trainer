"""Explicit contract for the complete workbook supported by this checkout.

Registration is intentional: a Python analytical module alone is not a workbook
module. An eligible entry supplies preparation/specs and workbook writers. Input
package presence is checked before applicability or metric-level availability.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Callable

from .component_catalog import ComponentSpec, geographic_spec_identity

if TYPE_CHECKING:
    from openpyxl import Workbook
    from ..data.interface import StandardizedFinancials
    from .reference_model import ReferenceModelBuilder
    from .semantic_map import SemanticMap


@dataclass(frozen=True)
class RequiredInput:
    name: str
    supplied: Callable[[StandardizedFinancials], bool]


@dataclass(frozen=True)
class WorkbookWriter:
    """Shared sheet writers run once, after every module has prepared its specs."""

    id: str
    order: int
    write: Callable[[ReferenceModelBuilder, Workbook], None]


def _spec_key(spec: ComponentSpec) -> tuple:
    return spec.family_id, spec.period_index


@dataclass(frozen=True)
class BuildModule:
    id: str
    status: str
    workbook_capable: bool
    complete_analysis: bool
    prepare: Callable[[ReferenceModelBuilder, int], tuple[ComponentSpec, ...]] | None = None
    writers: tuple[WorkbookWriter, ...] = ()
    depends_on: tuple[str, ...] = ()
    required_inputs: tuple[RequiredInput, ...] = ()
    applicable: Callable[[ReferenceModelBuilder], bool] | None = None
    spec_key: Callable[[ComponentSpec], tuple] = _spec_key


def complete_build_modules(financials: StandardizedFinancials) -> tuple[BuildModule, ...]:
    """Snapshot and validate the registry; never select by available input alone."""
    selected = []
    seen = set()
    ready = set()
    for module in BUILD_MODULES:
        if module.id in seen:
            raise ValueError(f"Duplicate Build module: {module.id}")
        seen.add(module.id)
        if module.status not in {"complete", "incomplete", "deferred"}:
            raise ValueError(f"Unknown Build completion status: {module.id}: {module.status}")
        if not (module.status == "complete" and module.workbook_capable and module.complete_analysis):
            continue
        if not callable(module.prepare) or not module.writers:
            raise ValueError(f"Build module {module.id}: missing workbook/spec integration")
        for writer in module.writers:
            if not callable(writer.write):
                raise ValueError(f"Build module {module.id}: invalid workbook writer {writer.id}")
        for dependency in module.depends_on:
            if dependency not in ready:
                raise ValueError(f"Build module {module.id}: dependency {dependency} must be registered before it and eligible")
        for requirement in module.required_inputs:
            if not requirement.supplied(financials):
                raise ValueError(f"Build module {module.id}: missing required input: {requirement.name}")
        selected.append(module)
        ready.add(module.id)
    return tuple(selected)


def prepare_complete_build(builder: ReferenceModelBuilder) -> tuple[ComponentSpec, ...]:
    """Prepare in registry order and assign globally unique component order."""
    specs = []
    builder.module_specs = {}
    builder.workbook_writers = {}
    for module in builder.build_modules:
        if module.applicable is not None and not module.applicable(builder):
            continue
        for dependency in module.depends_on:
            if dependency not in builder.module_specs:
                raise ValueError(
                    f"Build module {module.id}: dependency {dependency} is not applicable"
                )
        assert module.prepare is not None
        prepared = tuple(module.prepare(builder, len(specs) + 1))
        # Source-unavailable filtering can leave holes in a family's local order.
        # Rebase after filtering, so the following module cannot overlap it.
        ordered = tuple(replace(spec, order=len(specs) + i + 1) for i, spec in enumerate(prepared))
        builder.module_specs[module.id] = ordered
        setattr(builder, f"{module.id}_specs", ordered)
        setattr(builder, f"_{module.id}_spec_index", {
            module.spec_key(s): s for s in ordered
        })
        specs.extend(ordered)
        for writer in module.writers:
            previous = builder.workbook_writers.setdefault(writer.id, writer)
            if previous != writer:
                raise ValueError(f"Conflicting Build workbook writer: {writer.id}")
    ids = [s.id for s in specs]
    keys = [s.semantic_key for s in specs]
    if len(set(ids)) != len(ids) or len(set(keys)) != len(keys):
        raise ValueError("Duplicate Build component identity")
    return tuple(specs)


def write_complete_build(builder: ReferenceModelBuilder, workbook: Workbook) -> None:
    # Stable sorting preserves registration order for equal writer priorities.
    for writer in sorted(builder.workbook_writers.values(), key=lambda w: w.order):
        writer.write(builder, workbook)


def verify_complete_build(expected_specs: tuple[ComponentSpec, ...], semantic_map: SemanticMap) -> None:
    """Reject missing, extra, reordered or substituted runtime components."""
    def identity(component):
        return (component.id, component.semantic_key, component.family_id,
                component.period_index, component.period_end, component.order,
                tuple(component.depends_on))

    expected = [identity(s) for s in expected_specs]
    actual = [identity(c) for c in semantic_map.all_ordered()]
    if actual != expected:
        missing = sorted({s[0] for s in expected} - {s[0] for s in actual})
        extra = sorted({s[0] for s in actual} - {s[0] for s in expected})
        raise ValueError(
            "Complete Build semantic component mismatch: "
            f"expected={len(expected)}, actual={len(actual)}, missing={missing}, extra={extra}; "
            "ordered identities must match the runtime contract"
        )


def _writer(method: str, order: int, *, when: str | None = None) -> WorkbookWriter:
    def write(builder, workbook):
        if when is None or getattr(builder, when):
            getattr(builder, method)(workbook)
    return WorkbookWriter(method, order, write)


SOURCE = _writer("_build_source_tabs", 0)
CONDENSED = _writer("_build_condensed", 1)
DUPONT = _writer("_build_dupont", 2)
JUDGMENT = _writer("_build_accounting_judgment", 3)
OWNERSHIP = _writer("_build_ownership_attribution", 4, when="ownership_attribution_series")
NORMALIZATION_JUDGMENT = _writer("_build_normalization_judgment", 5, when="normalization_cases")
NORMALIZATION = _writer("_build_earnings_normalization", 6, when="normalization_cases")
QUALITY = _writer("_build_earnings_quality", 7, when="quality_series")
WORKING_CAPITAL = _writer("_build_working_capital_analysis", 8, when="working_capital_series")
PER_SHARE = _writer("_build_per_share_analysis", 9, when="per_share_series")
GEOGRAPHIC = _writer("_build_geographic_segment", 10, when="geographic_series")
OPERATING_KPI = _writer("_build_store_count", 11, when="operating_kpi_series")


def _integrated(id: str, writers: tuple[WorkbookWriter, ...], *,
                depends_on: tuple[str, ...] = ("historical",),
                spec_key: Callable[[ComponentSpec], tuple] = _spec_key) -> BuildModule:
    def prepare(builder, start_order):
        return getattr(builder, f"_prepare_{id}")(start_order)
    return BuildModule(id, "complete", True, True, prepare, writers, depends_on,
                       spec_key=spec_key)


# This tuple is the canonical completion/integration declaration. Keep it in
# dependency order. Existing adapters retain their source-level applicability.
# New modules may provide callables directly, without editing the builder.
BUILD_MODULES = (
    _integrated("historical", (SOURCE, CONDENSED, DUPONT, JUDGMENT), depends_on=()),
    _integrated("normalization", (NORMALIZATION_JUDGMENT, NORMALIZATION)),
    _integrated("quality", (QUALITY,)),
    _integrated("working_capital", (WORKING_CAPITAL,)),
    _integrated("profitability_driver", (DUPONT,)),
    _integrated("profitability_change", (DUPONT,)),
    _integrated("roe_attribution", (DUPONT,)),
    _integrated("quality_change", (QUALITY,), depends_on=("quality",)),
    _integrated("per_share", (PER_SHARE,)),
    _integrated("per_share_attribution", (PER_SHARE,), depends_on=("per_share",)),
    _integrated("normalized_per_share", (PER_SHARE,), depends_on=("normalization", "per_share")),
    _integrated("fixed_asset", (DUPONT,)),
    _integrated("lease_liability", (DUPONT,)),
    _integrated("ownership_attribution", (OWNERSHIP,)),
    _integrated("goodwill_intangibles", (DUPONT,)),
    _integrated("lease_rou", (DUPONT,)),
    _integrated("deferred_tax", (DUPONT,)),
    _integrated("capex", (DUPONT,)),
    _integrated("lease_repayment", (DUPONT,)),
    _integrated("acquisition_cash", (DUPONT,)),
    _integrated("share_repurchase", (DUPONT,)),
    _integrated("cash_rollforward", (DUPONT,)),
    _integrated("reported_margin", (DUPONT,)),
    _integrated("inventory_analysis", (DUPONT,)),
    _integrated("geographic", (GEOGRAPHIC,), spec_key=lambda s: (
        s.family_id, s.period_index, geographic_spec_identity(s),
    )),
    _integrated("operating_kpi", (OPERATING_KPI,)),
    BuildModule("forecast", "deferred", True, True),
)
