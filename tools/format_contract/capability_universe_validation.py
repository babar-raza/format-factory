"""Fail-closed semantic validation for FF6 capability enrichments."""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping, Sequence

from .capability_universe_runtime import UniverseError

CLASSIFICATIONS = (
    "STABLE_REQUIRED",
    "OPTIONAL_ADAPTER_REQUIRED",
    "PREVIEW_ISOLATED",
    "EXCLUDED_WITH_AUTHORITY",
)
SAL_ID = re.compile(r"^SAL-([A-Z0-9]+)-[A-Z0-9_-]+$")
REQUIRED_ENRICHMENT_FIELDS = (
    "capability_id",
    "stable_name",
    "classification",
    "developer_use_cases",
    "spec_profiles",
    "authority_fact_ids",
    "public_symbols",
    "source_symbols",
    "model_invariants",
    "preservation_contract",
    "error_contract",
    "security_contract",
    "resource_limits",
    "performance_budget",
    "dependency_policy",
    "positive_tests",
    "negative_tests",
    "property_tests",
    "roundtrip_tests",
    "fixtures",
    "independent_oracles",
    "documentation_examples",
    "compatibility_status",
    "proof_node_ids",
    "invalidation_inputs",
    "taskcard_ids",
    "release_state",
)
DERIVED_FIELDS = {"format_id", "normative_obligation_ids"}
LEGACY_CLASSIFICATIONS = {
    "stable": "STABLE_REQUIRED",
    "optional_adapter": "OPTIONAL_ADAPTER_REQUIRED",
    "preview": "PREVIEW_ISOLATED",
    "excluded": "EXCLUDED_WITH_AUTHORITY",
}


def iter_ids(value: Any) -> Iterable[str]:
    """Yield policy and research identities from nested YAML data."""

    if isinstance(value, dict):
        for key in ("id", "finding_id"):
            identity = value.get(key)
            if isinstance(identity, str):
                yield identity
        for child in value.values():
            yield from iter_ids(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_ids(child)


def _require_nonempty(record: Mapping[str, Any], field: str, capability_id: str) -> None:
    if field not in record:
        raise UniverseError(f"{capability_id}: missing required field {field}")
    if record[field] in (None, "", [], {}):
        raise UniverseError(
            f"{capability_id}: empty {field}; use PLANNED for future references"
        )


def validate_enrichment(
    format_id: str,
    records: Sequence[dict[str, Any]],
    contract_capabilities: Mapping[str, dict[str, Any]],
    facts: Mapping[str, dict[str, Any]],
    policy_ids: set[str],
    classification_locks: Mapping[str, str],
) -> dict[str, dict[str, Any]]:
    """Validate exact identity, provenance, classification, and exclusion scope."""

    by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        capability_id = str(record.get("capability_id", ""))
        for field in REQUIRED_ENRICHMENT_FIELDS:
            _require_nonempty(record, field, capability_id or "<unknown>")
        if capability_id in by_id:
            raise UniverseError(f"duplicate capability ID: {capability_id}")
        classification = str(record["classification"])
        if classification not in CLASSIFICATIONS:
            raise UniverseError(
                f"{capability_id}: invalid classification {classification}"
            )
        locked = classification_locks.get(capability_id)
        if locked is not None and classification != locked:
            raise UniverseError(
                f"{capability_id}: classification lock requires {locked}, got {classification}"
            )
        if classification == "EXCLUDED_WITH_AUTHORITY":
            exclusion = record.get("exclusion")
            if (
                not isinstance(exclusion, dict)
                or not exclusion.get("authority_basis")
                or not exclusion.get("user_disposition")
            ):
                raise UniverseError(
                    f"{capability_id}: exclusion requires authority_basis and user_disposition"
                )
        for fact_id in record["authority_fact_ids"]:
            fact_id = str(fact_id)
            match = SAL_ID.match(fact_id)
            if match:
                if match.group(1).lower() != format_id:
                    raise UniverseError(
                        f"{capability_id}: foreign fact {fact_id} for {format_id}"
                    )
                if fact_id not in facts:
                    raise UniverseError(f"{capability_id}: dangling fact {fact_id}")
            elif fact_id not in policy_ids:
                raise UniverseError(
                    f"{capability_id}: dangling policy/research reference {fact_id}"
                )
        expected_provenance = {
            str(item)
            for item in contract_capabilities[capability_id].get("provenance", [])
        }
        actual_provenance = {str(item) for item in record["authority_fact_ids"]}
        if actual_provenance != expected_provenance:
            raise UniverseError(
                f"{capability_id}: authority references differ from canonical contract"
            )
        by_id[capability_id] = record
    expected = set(contract_capabilities)
    actual = set(by_id)
    if expected != actual:
        raise UniverseError(
            "capability identity mismatch: "
            f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}"
        )
    return by_id
