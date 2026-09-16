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
REASON_NO_DISTINCT_PEER = "no_distinct_peer"
REASON_MISSING_DEFINITION = "missing_definition"
REASON_UNBOUND_DEFINITION = "unbound_definition"
REASON_MISSING_POPULATION = "missing_population"
REASON_MISSING_UNIT = "missing_unit"
REASON_MISSING_BASIS = "missing_basis"
REASON_MISSING_COMPARISON = "missing_comparison"
REASON_PERIOD_DATE = "period_date"
REASON_CALENDAR_WEEK = "calendar_week_adjustment"
REASON_CALENDAR_REPORTING = "calendar_reporting_basis"
REASON_PERIOD_MISMATCH = "period_mismatch"
REQUIRED_COMPARISON_REASONS = (
    REASON_MISSING_DEFINITION,
    REASON_UNBOUND_DEFINITION,
    REASON_MISSING_POPULATION,
    REASON_MISSING_UNIT,
    REASON_MISSING_BASIS,
    REASON_MISSING_COMPARISON,
    REASON_PERIOD_DATE,
    REASON_CALENDAR_WEEK,
    REASON_CALENDAR_REPORTING,
)
_PEER_REASON_PREFIX = "peer_"
PEER_COMPARISON_REASONS = tuple(
    f"{_PEER_REASON_PREFIX}{reason}" for reason in REQUIRED_COMPARISON_REASONS
)
_EVIDENCED_FIELDS = (
    ("definition_text", "definition_mismatch"),
    ("population", "population_mismatch"),
    ("unit", "unit_mismatch"),
    ("basis", "basis_mismatch"),
    ("comparison", "comparison_mismatch"),
    ("calendar_week_adjustment", "calendar_mismatch"),
    ("calendar_reporting_basis", "calendar_reporting_mismatch"),
    ("qualifiers_other", "qualifier_mismatch"),
)

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


def _qualifiers_other(qualifiers: Mapping[str, str]) -> str:
    remaining = {
        key: value for key, value in qualifiers.items() if key != "excludes_53rd_week"
    }
    if not remaining:
        return ""
    return json.dumps(remaining, sort_keys=True, separators=(",", ":"))


def text_present(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def peer_gap_reason(reason: str) -> str:
    return f"{_PEER_REASON_PREFIX}{reason}"


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
    if mapping.comparison and observation.comparison != mapping.comparison:
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


def required_comparison_reasons(evidence: Mapping[str, str]) -> tuple[str, ...]:
    reasons: list[str] = []
    if not text_present(evidence.get("definition_id", "")):
        reasons.append(REASON_MISSING_DEFINITION)
    elif not text_present(evidence.get("definition_text", "")):
        reasons.append(REASON_UNBOUND_DEFINITION)
    if not text_present(evidence.get("population", "")):
        reasons.append(REASON_MISSING_POPULATION)
    if not text_present(evidence.get("unit", "")):
        reasons.append(REASON_MISSING_UNIT)
    if not text_present(evidence.get("basis", "")):
        reasons.append(REASON_MISSING_BASIS)
    if not text_present(evidence.get("comparison", "")):
        reasons.append(REASON_MISSING_COMPARISON)
    if evidence.get("period_kind") != "date":
        reasons.append(REASON_PERIOD_DATE)
    if not text_present(evidence.get("calendar_week_adjustment", "")):
        reasons.append(REASON_CALENDAR_WEEK)
    if not text_present(evidence.get("calendar_reporting_basis", "")):
        reasons.append(REASON_CALENDAR_REPORTING)
    return tuple(reasons)


def evidenced_conflicts(
    self_ev: Mapping[str, str], peer_ev: Mapping[str, str]
) -> tuple[str, ...]:
    reasons: list[str] = []
    for key, reason in _EVIDENCED_FIELDS:
        left = self_ev.get(key, "")
        right = peer_ev.get(key, "")
        if text_present(left) and text_present(right) and left != right:
            reasons.append(reason)
    return tuple(reasons)


def evidenced_period_conflict(
    self_ev: Mapping[str, str], peer_ev: Mapping[str, str]
) -> tuple[str, ...]:
    left_kind = self_ev.get("period_kind", "")
    right_kind = peer_ev.get("period_kind", "")
    left_period = self_ev.get("period", "")
    right_period = peer_ev.get("period", "")
    if left_kind == "date" and right_kind == "date" and left_period != right_period:
        return (REASON_PERIOD_MISMATCH,)
    return ()


def pair_is_fully_evidenced_same_period(
    self_ev: Mapping[str, str], peer_ev: Mapping[str, str]
) -> bool:
    if required_comparison_reasons(self_ev) or required_comparison_reasons(peer_ev):
        return False
    if evidenced_conflicts(self_ev, peer_ev):
        return False
    if evidenced_period_conflict(self_ev, peer_ev):
        return False
    return (
        self_ev.get("period_kind") == "date"
        and peer_ev.get("period_kind") == "date"
        and self_ev.get("period") == peer_ev.get("period")
    )


def _required_comparison_reasons(evidence: Mapping[str, str]) -> tuple[str, ...]:
    return required_comparison_reasons(evidence)


def _evidenced_conflicts(
    self_ev: Mapping[str, str], peer_ev: Mapping[str, str]
) -> tuple[str, ...]:
    return evidenced_conflicts(self_ev, peer_ev)


def _has_required_gap(unresolved: Sequence[str]) -> bool:
    return any(reason in REQUIRED_COMPARISON_REASONS for reason in unresolved)


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
        if definition is not None:
            definition_text = definition.definition
            definition_label = definition.reported_label
            definition_document = observation.extraction_document
        qualifiers = _qualifier_map(observation)
        week_adjustment = _week_adjustment(qualifiers)
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
            "qualifiers_other": _qualifiers_other(qualifiers),
            "scope": json.dumps(dict(observation.scope), sort_keys=True, separators=(",", ":")),
            "definition_text": definition_text,
            "definition_id": observation.definition_id,
            "extraction_document": observation.extraction_document,
            "bound_source_file": observation.bound_source_file,
        }
        if status == STATUS_SUPPORTED:
            unresolved.extend(_required_comparison_reasons(evidence))
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
        own_locator = observation.locator
        peer_locators = tuple(
            locator
            for locator in peers.get(item["identity"], ())
            if locator != own_locator
        )
        if status == STATUS_OUTSIDE_SCOPE:
            comparability = COMPARABILITY_OUTSIDE_SCOPE
        elif status != STATUS_SUPPORTED:
            comparability = COMPARABILITY_UNRESOLVED
        else:
            distinct_peers = [
                peer
                for peer in classified
                if peer is not item
                and peer["status"] == STATUS_SUPPORTED
                and peer["identity"]
                and peer["identity"] == item["identity"]
            ]
            distinct_peers.sort(key=lambda peer: peer["observation"].locator)
            conflict_reasons: list[str] = []
            peer_gap_seen: set[str] = set()
            for peer in distinct_peers:
                for reason in _evidenced_conflicts(item["evidence"], peer["evidence"]):
                    if reason not in conflict_reasons:
                        conflict_reasons.append(reason)
                peer_gap_seen.update(
                    reason
                    for reason in peer["unresolved"]
                    if reason in REQUIRED_COMPARISON_REASONS
                )
            peer_gap_reasons = [
                peer_gap_reason(reason)
                for reason in REQUIRED_COMPARISON_REASONS
                if reason in peer_gap_seen
            ]
            for reason in conflict_reasons:
                if reason not in unresolved:
                    unresolved.append(reason)
            for reason in peer_gap_reasons:
                if reason not in unresolved:
                    unresolved.append(reason)
            if conflict_reasons:
                comparability = COMPARABILITY_NOT_COMPARABLE
            elif not distinct_peers:
                if REASON_NO_DISTINCT_PEER not in unresolved:
                    unresolved.append(REASON_NO_DISTINCT_PEER)
                comparability = COMPARABILITY_UNRESOLVED
            elif _has_required_gap(unresolved) or peer_gap_reasons:
                comparability = COMPARABILITY_UNRESOLVED
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
