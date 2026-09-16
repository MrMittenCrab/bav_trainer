"""Semantic identity and comparability for supported management KPIs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

FAMILY_COMPARABLE_SALES_GROWTH = "comparable_sales_growth"
FAMILY_SALES_PER_SQUARE_FOOT = "sales_per_square_foot"
SUPPORTED_FAMILIES = (
    FAMILY_COMPARABLE_SALES_GROWTH,
    FAMILY_SALES_PER_SQUARE_FOOT,
)

STATUS_SUPPORTED = "supported"
STATUS_OUTSIDE_SCOPE = "outside_scope"
STATUS_UNSUPPORTED_VARIANT = "unsupported_variant"

COMPARABILITY_COMPARABLE = "comparable"
COMPARABILITY_NOT_COMPARABLE = "not_comparable"
COMPARABILITY_UNRESOLVED = "unresolved"
COMPARABILITY_OUTSIDE_SCOPE = "outside_scope"

POP_STORES_AND_ECOMMERCE = "company_operated_stores_and_ecommerce"
POP_STORES_AND_DTC = "company_operated_stores_and_direct_to_consumer"
POP_COMPANY_OPERATED_STORES = "company_operated_stores"

_GEOGRAPHY_ALIASES = {
    "global": "global",
    "americas": "americas",
    "china mainland": "china_mainland",
    "china_mainland": "china_mainland",
    "rest of world": "rest_of_world",
    "rest_of_world": "rest_of_world",
}

_IDENTITY_FIELD_ORDER = (
    "family",
    "entity_ticker",
    "entity_company",
    "geography",
    "population",
    "unit",
    "basis",
    "comparison",
)


@dataclass(frozen=True)
class MetricMapping:
    family: str
    unit: str
    basis: str
    comparison: str
    geography: str
    population: str
    channel: str = ""


def _compsales(
    *,
    basis: str,
    geography: str,
    population: str = POP_STORES_AND_ECOMMERCE,
    channel: str = "",
) -> MetricMapping:
    return MetricMapping(
        family=FAMILY_COMPARABLE_SALES_GROWTH,
        unit="percent",
        basis=basis,
        comparison="year_over_year",
        geography=geography,
        population=population,
        channel=channel,
    )


# Explicit metric-id mappings. Lookup is by id, never by declaration order.
SUPPORTED_METRIC_MAPPINGS: dict[str, MetricMapping] = {
    "comparable_sales_growth": _compsales(basis="reported", geography="global"),
    "comparable_sales_growth_constant_dollar": _compsales(
        basis="constant_dollar", geography="global"
    ),
    "americas_comparable_sales_growth": _compsales(
        basis="reported", geography="americas"
    ),
    "americas_comparable_sales_growth_constant_dollar": _compsales(
        basis="constant_dollar", geography="americas"
    ),
    "china_mainland_comparable_sales_growth": _compsales(
        basis="reported", geography="china_mainland"
    ),
    "china_mainland_comparable_sales_growth_constant_dollar": _compsales(
        basis="constant_dollar", geography="china_mainland"
    ),
    "rest_of_world_comparable_sales_growth": _compsales(
        basis="reported", geography="rest_of_world"
    ),
    "rest_of_world_comparable_sales_growth_constant_dollar": _compsales(
        basis="constant_dollar", geography="rest_of_world"
    ),
    "total_comparable_sales_growth": _compsales(
        basis="reported",
        geography="global",
        population=POP_STORES_AND_DTC,
    ),
    "total_comparable_sales_growth_constant_dollar": _compsales(
        basis="constant_dollar",
        geography="global",
        population=POP_STORES_AND_DTC,
    ),
    "comparable_store_sales_growth": _compsales(
        basis="reported",
        geography="",
        population=POP_COMPANY_OPERATED_STORES,
        channel="company_operated_stores",
    ),
    "comparable_store_sales_growth_constant_dollar": _compsales(
        basis="constant_dollar",
        geography="",
        population=POP_COMPANY_OPERATED_STORES,
        channel="company_operated_stores",
    ),
    "sales_per_square_foot": MetricMapping(
        family=FAMILY_SALES_PER_SQUARE_FOOT,
        unit="USD_per_square_foot",
        basis="reported",
        comparison="",
        geography="",
        population=POP_COMPANY_OPERATED_STORES,
        channel="company_operated_stores",
    ),
}


def encode_metric_identity(fields: Mapping[str, str]) -> str:
    """Delimiter-safe identity; independent of mapping or dict insertion order."""
    canonical = {key: str(fields.get(key, "")) for key in _IDENTITY_FIELD_ORDER}
    extra = sorted(key for key in fields if key not in canonical)
    if extra:
        raise ValueError(f"unsupported metric-identity fields: {extra}")
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _looks_like_supported_family(metric_id: str) -> str:
    if "sales_per_square_foot" in metric_id:
        return FAMILY_SALES_PER_SQUARE_FOOT
    if "comparable_sales" in metric_id or "comparable_store_sales" in metric_id:
        return FAMILY_COMPARABLE_SALES_GROWTH
    return ""


def _normalize_geography(value: str) -> str | None:
    if not value:
        return ""
    collapsed = " ".join(value.strip().lower().split())
    if collapsed not in _GEOGRAPHY_ALIASES:
        return None
    return _GEOGRAPHY_ALIASES[collapsed]


def _qualifier_map(observation: Any) -> dict[str, str]:
    return {key: value for key, value in observation.qualifiers}


def _canonical_qualifiers(observation: Any) -> str:
    return json.dumps(_qualifier_map(observation), sort_keys=True, separators=(",", ":"))


def _week_adjustment(qualifiers: Mapping[str, str]) -> str:
    raw = qualifiers.get("excludes_53rd_week")
    if raw == "true":
        return "excluded"
    if raw == "false":
        return "included"
    return ""


@dataclass(frozen=True)
class ManagementIdentityAssessment:
    locator: str
    occurrence_identity: str
    status: str
    family: str
    metric_identity: str
    metric_identity_fields: tuple[tuple[str, str], ...]
    comparability: str
    definition_id: str
    definition_document: str
    definition_text: str
    definition_label: str
    evidence: tuple[tuple[str, str], ...]
    unresolved_reasons: tuple[str, ...]
    peer_locators: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "locator": self.locator,
            "occurrence_identity": self.occurrence_identity,
            "status": self.status,
            "family": self.family,
            "metric_identity": self.metric_identity,
            "metric_identity_fields": dict(self.metric_identity_fields),
            "comparability": self.comparability,
            "definition": {
                "definition_id": self.definition_id,
                "extraction_document": self.definition_document,
                "reported_label": self.definition_label,
                "text": self.definition_text,
            },
            "evidence": dict(self.evidence),
            "unresolved_reasons": list(self.unresolved_reasons),
            "peer_locators": list(self.peer_locators),
        }


def _document_index(documents: Sequence[Any]) -> dict[str, Any]:
    index: dict[str, Any] = {}
    for bound in documents:
        document = bound.document if hasattr(bound, "document") else bound
        index[document.extraction_document] = document
    return index


def _definition_index(documents: Sequence[Any]) -> dict[tuple[str, str], Any]:
    index: dict[tuple[str, str], Any] = {}
    for bound in documents:
        document = bound.document if hasattr(bound, "document") else bound
        for definition in document.definitions:
            index[(document.extraction_document, definition.definition_id)] = definition
    return index


def _classify_metric(
    observation: Any,
    *,
    ticker: str,
    company: str,
) -> tuple[str, str, dict[str, str], tuple[str, ...]]:
    metric_id = observation.metric_id
    mapping = SUPPORTED_METRIC_MAPPINGS.get(metric_id)
    if mapping is None:
        family = _looks_like_supported_family(metric_id)
        if family:
            return (
                STATUS_UNSUPPORTED_VARIANT,
                family,
                {},
                ("unknown_variant",),
            )
        return (STATUS_OUTSIDE_SCOPE, "", {}, ("outside_supported_families",))

    reasons: list[str] = []
    if observation.unit != mapping.unit:
        reasons.append("contradictory_unit")
    if observation.basis != mapping.basis:
        reasons.append("contradictory_basis")
    if observation.comparison != mapping.comparison:
        reasons.append("contradictory_comparison")

    scope = dict(observation.scope)
    allowed = set()
    geography = ""
    if mapping.geography:
        allowed.add("geography")
        raw_geo = scope.get("geography", "")
        if not raw_geo:
            reasons.append("missing_geography")
        else:
            normalized = _normalize_geography(raw_geo)
            if normalized is None:
                reasons.append("unknown_geography")
            elif normalized != mapping.geography:
                reasons.append("contradictory_geography")
            else:
                geography = normalized
    if mapping.channel:
        allowed.add("channel")
        raw_channel = scope.get("channel", "")
        if not raw_channel:
            reasons.append("missing_channel")
        elif raw_channel != mapping.channel:
            reasons.append("contradictory_channel")
    extra = sorted(key for key in scope if key not in allowed)
    if extra:
        reasons.append("unexpected_scope")

    if reasons:
        return (
            STATUS_UNSUPPORTED_VARIANT,
            mapping.family,
            {},
            tuple(reasons),
        )

    fields = {
        "family": mapping.family,
        "entity_ticker": ticker,
        "entity_company": company,
        "geography": geography,
        "population": mapping.population,
        "unit": mapping.unit,
        "basis": mapping.basis,
        "comparison": mapping.comparison,
    }
    return (STATUS_SUPPORTED, mapping.family, fields, ())


def _conflict_reason(self_ev: Mapping[str, str], peer_ev: Mapping[str, str]) -> str:
    if self_ev["definition_text"] != peer_ev["definition_text"]:
        return "definition_mismatch"
    if self_ev["population"] != peer_ev["population"]:
        return "population_mismatch"
    if self_ev["calendar_reporting_basis"] != peer_ev["calendar_reporting_basis"]:
        return "calendar_mismatch"
    if self_ev["calendar_week_adjustment"] != peer_ev["calendar_week_adjustment"]:
        return "calendar_mismatch"
    if self_ev["qualifiers"] != peer_ev["qualifiers"]:
        return "qualifier_mismatch"
    if self_ev["period_kind"] != peer_ev["period_kind"]:
        return "period_kind_mismatch"
    return ""


def assess_reported_observations(
    observations: Sequence[Any],
    documents: Sequence[Any],
) -> tuple[ManagementIdentityAssessment, ...]:
    """Assess every reported observation; other kinds are ignored."""
    docs = _document_index(documents)
    definitions = _definition_index(documents)
    reported = [item for item in observations if item.kind == "reported_kpi"]
    classified: list[dict[str, Any]] = []
    for observation in reported:
        document = docs.get(observation.extraction_document)
        ticker = getattr(document, "ticker", "") if document is not None else ""
        company = getattr(document, "company", "") if document is not None else ""
        reporting_basis = (
            getattr(document, "reporting_basis", "") if document is not None else ""
        )
        status, family, fields, reasons = _classify_metric(
            observation, ticker=ticker, company=company
        )
        definition = definitions.get(
            (observation.extraction_document, observation.definition_id)
        )
        unresolved = list(reasons)
        definition_text = ""
        definition_label = ""
        definition_document = ""
        if status == STATUS_SUPPORTED:
            if not observation.definition_id:
                unresolved.append("missing_definition")
            elif definition is None:
                unresolved.append("unbound_definition")
            else:
                definition_text = definition.definition
                definition_label = definition.reported_label
                definition_document = observation.extraction_document
            if observation.period_kind == "fiscal_year_label":
                unresolved.append("period_date")
        qualifiers = _qualifier_map(observation)
        week_adjustment = _week_adjustment(qualifiers)
        if status == STATUS_SUPPORTED and not week_adjustment:
            unresolved.append("calendar_week_adjustment")
        identity = encode_metric_identity(fields) if fields else ""
        evidence = {
            "entity_ticker": ticker,
            "entity_company": company,
            "geography": fields.get("geography", ""),
            "population": fields.get("population", ""),
            "unit": observation.unit,
            "basis": observation.basis,
            "comparison": observation.comparison,
            "period": observation.period,
            "period_kind": observation.period_kind,
            "calendar_reporting_basis": reporting_basis,
            "calendar_week_adjustment": week_adjustment,
            "qualifiers": _canonical_qualifiers(observation),
            "scope": json.dumps(dict(observation.scope), sort_keys=True, separators=(",", ":")),
            "definition_text": definition_text,
            "definition_id": observation.definition_id,
            "extraction_document": observation.extraction_document,
            "bound_source_file": observation.bound_source_file,
        }
        classified.append(
            {
                "observation": observation,
                "status": status,
                "family": family,
                "fields": fields,
                "identity": identity,
                "unresolved": unresolved,
                "definition_text": definition_text,
                "definition_label": definition_label,
                "definition_document": definition_document,
                "evidence": evidence,
                "filing_year": observation.filing_year,
            }
        )

    peers: dict[str, list[str]] = {}
    for item in classified:
        if item["status"] != STATUS_SUPPORTED or not item["identity"]:
            continue
        peers.setdefault(item["identity"], []).append(item["observation"].locator)
    for locators in peers.values():
        locators.sort()

    ordered_assessments: list[tuple[int, str, str, ManagementIdentityAssessment]] = []
    for item in classified:
        observation = item["observation"]
        status = item["status"]
        unresolved = list(item["unresolved"])
        peer_locators = tuple(peers.get(item["identity"], ()))
        if status == STATUS_OUTSIDE_SCOPE:
            comparability = COMPARABILITY_OUTSIDE_SCOPE
        elif status != STATUS_SUPPORTED:
            comparability = COMPARABILITY_UNRESOLVED
        elif "missing_definition" in unresolved or "unbound_definition" in unresolved:
            comparability = COMPARABILITY_UNRESOLVED
        else:
            conflict = ""
            for peer in classified:
                if peer is item:
                    continue
                if peer["identity"] != item["identity"] or not item["identity"]:
                    continue
                conflict = _conflict_reason(item["evidence"], peer["evidence"])
                if conflict:
                    break
            if conflict:
                if conflict not in unresolved:
                    unresolved.append(conflict)
                comparability = COMPARABILITY_NOT_COMPARABLE
            else:
                comparability = COMPARABILITY_COMPARABLE
        ordered_assessments.append(
            (
                item["filing_year"],
                observation.identity,
                observation.locator,
                ManagementIdentityAssessment(
                    locator=observation.locator,
                    occurrence_identity=observation.identity,
                    status=status,
                    family=item["family"],
                    metric_identity=item["identity"],
                    metric_identity_fields=tuple(sorted(item["fields"].items())),
                    comparability=comparability,
                    definition_id=observation.definition_id,
                    definition_document=item["definition_document"],
                    definition_text=item["definition_text"],
                    definition_label=item["definition_label"],
                    evidence=tuple(sorted(item["evidence"].items())),
                    unresolved_reasons=tuple(unresolved),
                    peer_locators=peer_locators,
                ),
            )
        )
    ordered_assessments.sort(key=lambda item: (item[0], item[1], item[2]))
    return tuple(item[3] for item in ordered_assessments)


def assessments_payload(
    assessments: Iterable[ManagementIdentityAssessment],
) -> dict[str, Any]:
    items = list(assessments)
    supported = [item for item in items if item.status == STATUS_SUPPORTED]
    variants = [item for item in items if item.status == STATUS_UNSUPPORTED_VARIANT]
    outside = [item for item in items if item.status == STATUS_OUTSIDE_SCOPE]
    comparability_counts = {
        COMPARABILITY_COMPARABLE: 0,
        COMPARABILITY_NOT_COMPARABLE: 0,
        COMPARABILITY_UNRESOLVED: 0,
        COMPARABILITY_OUTSIDE_SCOPE: 0,
    }
    for item in items:
        comparability_counts[item.comparability] = (
            comparability_counts.get(item.comparability, 0) + 1
        )
    return {
        "supported_families": list(SUPPORTED_FAMILIES),
        "reported_observation_count": len(items),
        "supported_count": len(supported),
        "unsupported_variant_count": len(variants),
        "outside_scope_count": len(outside),
        "comparability_counts": comparability_counts,
        "canonical_selection": "deferred",
        "items": [item.to_payload() for item in items],
    }
