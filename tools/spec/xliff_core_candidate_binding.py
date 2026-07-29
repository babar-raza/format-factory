"""Content binding and semantic classes for XLIFF Core authority candidates.

This module is deliberately independent of the XLIFF census compiler.  It
provides pure, deterministic primitives that the compiler and its standalone
validator can share without duplicating hash or classification rules.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


class CandidateBindingError(ValueError):
    """Raised when candidate identity or content binding is malformed."""


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_PROSE_LOCATION = re.compile(
    r"^(?:prose|prose-nonmodal)/.+/(para|listitem)\[[1-9][0-9]*\]$"
)
_NORMATIVE_MODAL = re.compile(
    r"\b(?:must(?:\s+not)?|shall(?:\s+not)?|should(?:\s+not)?|"
    r"required|recommended|may|optional)\b",
    re.IGNORECASE,
)

_XSD_SIMPLE_CLASSES = {
    "all": "XSD_ORDER_ALL",
    "any": "XSD_WILDCARD_ELEMENT",
    "anyAttribute": "XSD_WILDCARD_ATTRIBUTE",
    "choice": "XSD_ORDER_CHOICE",
    "enumeration": "XSD_FACET_ENUMERATION",
    "extension": "XSD_TYPE_EXTENSION",
    "field": "XSD_IDENTITY_FIELD",
    "fractionDigits": "XSD_FACET_FRACTION_DIGITS",
    "group": "XSD_GROUP_DECLARATION_OR_REFERENCE",
    "import": "XSD_SCHEMA_IMPORT",
    "key": "XSD_IDENTITY_KEY",
    "keyref": "XSD_IDENTITY_KEYREF",
    "length": "XSD_FACET_LENGTH",
    "list": "XSD_TYPE_LIST",
    "maxExclusive": "XSD_FACET_MAX_EXCLUSIVE",
    "maxInclusive": "XSD_FACET_MAX_INCLUSIVE",
    "maxLength": "XSD_FACET_MAX_LENGTH",
    "minExclusive": "XSD_FACET_MIN_EXCLUSIVE",
    "minInclusive": "XSD_FACET_MIN_INCLUSIVE",
    "minLength": "XSD_FACET_MIN_LENGTH",
    "pattern": "XSD_FACET_PATTERN",
    "restriction": "XSD_TYPE_RESTRICTION",
    "selector": "XSD_IDENTITY_SELECTOR",
    "sequence": "XSD_ORDER_SEQUENCE",
    "totalDigits": "XSD_FACET_TOTAL_DIGITS",
    "union": "XSD_TYPE_UNION",
    "unique": "XSD_IDENTITY_UNIQUE",
    "whiteSpace": "XSD_FACET_WHITE_SPACE",
}
XSD_CANDIDATE_KINDS = frozenset(
    {*_XSD_SIMPLE_CLASSES, "attribute", "complexType", "element", "simpleType"}
)

CORE_CANDIDATE_CLASSES = frozenset(
    {
        "PROSE_MODAL_PARAGRAPH",
        "PROSE_MODAL_LIST_ITEM",
        "PROSE_NON_MODAL_PARAGRAPH",
        "PROSE_NON_MODAL_LIST_ITEM",
        "SCHEMATRON_ASSERT",
        "SCHEMATRON_REPORT",
        "XSD_ATTRIBUTE_DECLARATION",
        "XSD_ATTRIBUTE_DECLARATION_CARDINALITY",
        "XSD_COMPLEX_TYPE_ANONYMOUS",
        "XSD_COMPLEX_TYPE_DECLARATION",
        "XSD_ELEMENT_DECLARATION",
        "XSD_ELEMENT_PARTICLE",
        "XSD_ELEMENT_PARTICLE_CARDINALITY",
        "XSD_SIMPLE_TYPE_ANONYMOUS",
        "XSD_SIMPLE_TYPE_DECLARATION",
        *_XSD_SIMPLE_CLASSES.values(),
    }
)

_BASE_OCCURRENCE_FIELDS = frozenset(
    {
        "profile",
        "source_id",
        "source_sha256",
        "member",
        "member_sha256",
        "location",
        "candidate_class",
        "normalized_requirement",
    }
)
_BOUND_OCCURRENCE_FIELDS = _BASE_OCCURRENCE_FIELDS | {
    "requirement_sha256",
    "occurrence_sha256",
}
_CANDIDATE_CONTENT_FIELDS = (
    "candidate_id",
    "source_kind",
    "candidate_class",
    "semantic_location",
    "profile_relation",
    "stable_profiles",
    "occurrences",
)


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _required_string(value: Mapping[str, object], field: str) -> str:
    raw = value.get(field)
    if not isinstance(raw, str) or not raw:
        raise CandidateBindingError(f"{field} must be a non-empty string")
    return raw


def _xsd_payload(normalized_requirement: str) -> tuple[str, Mapping[str, Any]]:
    try:
        payload = json.loads(normalized_requirement)
    except json.JSONDecodeError as exc:
        raise CandidateBindingError("XSD candidate requirement is not JSON") from exc
    if not isinstance(payload, Mapping):
        raise CandidateBindingError("XSD candidate requirement must be an object")
    kind = payload.get("kind")
    attributes = payload.get("attributes")
    if not isinstance(kind, str) or not isinstance(attributes, Mapping):
        raise CandidateBindingError(
            "XSD candidate requirement lacks kind or attributes"
        )
    return kind, attributes


def classify_candidate(
    *,
    source_kind: str,
    semantic_location: str,
    normalized_requirement: str,
) -> str:
    """Return the deterministic semantic class for one candidate occurrence."""

    if not semantic_location or not normalized_requirement:
        raise CandidateBindingError("candidate location and requirement are required")
    if source_kind in {"NORMATIVE_PROSE", "NON_MODAL_PROSE"}:
        match = _PROSE_LOCATION.fullmatch(semantic_location)
        if match is None:
            raise CandidateBindingError("invalid Core prose candidate location")
        is_modal = bool(_NORMATIVE_MODAL.search(normalized_requirement))
        if source_kind == "NORMATIVE_PROSE" and not is_modal:
            raise CandidateBindingError("normative prose candidate lacks a modal")
        if source_kind == "NON_MODAL_PROSE" and is_modal:
            raise CandidateBindingError("non-modal prose candidate contains a modal")
        block = "PARAGRAPH" if match.group(1) == "para" else "LIST_ITEM"
        prefix = "PROSE_MODAL" if is_modal else "PROSE_NON_MODAL"
        return f"{prefix}_{block}"

    if source_kind == "CORE_SCHEMATRON":
        kind = (
            "assert"
            if re.search(r"/assert\[[1-9][0-9]*\]$", semantic_location)
            else (
                "report"
                if re.search(r"/report\[[1-9][0-9]*\]$", semantic_location)
                else ""
            )
        )
        try:
            payload = json.loads(normalized_requirement)
        except json.JSONDecodeError as exc:
            raise CandidateBindingError(
                "Schematron candidate requirement is not JSON"
            ) from exc
        if not isinstance(payload, Mapping) or payload.get("kind") != kind:
            raise CandidateBindingError(
                "Schematron class contradicts candidate content"
            )
        if kind == "assert":
            return "SCHEMATRON_ASSERT"
        if kind == "report":
            return "SCHEMATRON_REPORT"
        raise CandidateBindingError("invalid Schematron candidate location")

    if source_kind != "CORE_XSD" or not semantic_location.startswith("xsd/"):
        raise CandidateBindingError(f"unsupported candidate source kind: {source_kind}")

    kind, attributes = _xsd_payload(normalized_requirement)
    segments = semantic_location.removeprefix("xsd/").split("/")
    location_kind = segments[-1].split(":", 1)[0]
    if kind != location_kind:
        raise CandidateBindingError("XSD class contradicts candidate location")
    if kind == "element":
        if len(segments) == 1:
            return "XSD_ELEMENT_DECLARATION"
        if "minOccurs" in attributes or "maxOccurs" in attributes:
            return "XSD_ELEMENT_PARTICLE_CARDINALITY"
        return "XSD_ELEMENT_PARTICLE"
    if kind == "attribute":
        return (
            "XSD_ATTRIBUTE_DECLARATION_CARDINALITY"
            if "use" in attributes
            else "XSD_ATTRIBUTE_DECLARATION"
        )
    if kind in {"complexType", "simpleType"}:
        prefix = "XSD_COMPLEX_TYPE" if kind == "complexType" else "XSD_SIMPLE_TYPE"
        return (
            f"{prefix}_DECLARATION"
            if len(segments) == 1 and isinstance(attributes.get("name"), str)
            else f"{prefix}_ANONYMOUS"
        )
    candidate_class = _XSD_SIMPLE_CLASSES.get(kind)
    if candidate_class is None:
        raise CandidateBindingError(f"unsupported XSD candidate kind: {kind}")
    return candidate_class


def bind_occurrence(occurrence: Mapping[str, object]) -> dict[str, str]:
    """Validate base fields and add requirement and occurrence digests."""

    if set(occurrence) != _BASE_OCCURRENCE_FIELDS:
        raise CandidateBindingError("invalid occurrence binding fields")
    result = {
        field: _required_string(occurrence, field)
        for field in sorted(_BASE_OCCURRENCE_FIELDS)
    }
    if result["profile"] not in {"xliff_2.0", "xliff_2.1"}:
        raise CandidateBindingError("invalid occurrence profile")
    for field in ("source_sha256", "member_sha256"):
        if _SHA256.fullmatch(result[field]) is None:
            raise CandidateBindingError(f"{field} is not a SHA-256 digest")
    expected_class = classify_candidate(
        source_kind=(
            "NORMATIVE_PROSE"
            if result["candidate_class"].startswith("PROSE_MODAL_")
            else (
                "NON_MODAL_PROSE"
                if result["candidate_class"].startswith("PROSE_NON_MODAL_")
                else (
                    "CORE_SCHEMATRON"
                    if result["candidate_class"].startswith("SCHEMATRON_")
                    else "CORE_XSD"
                )
            )
        ),
        semantic_location=result["location"],
        normalized_requirement=result["normalized_requirement"],
    )
    if result["candidate_class"] != expected_class:
        raise CandidateBindingError("candidate class contradicts occurrence content")
    result["requirement_sha256"] = hashlib.sha256(
        result["normalized_requirement"].encode("utf-8")
    ).hexdigest()
    result["occurrence_sha256"] = _canonical_sha256(result)
    return result


def validate_bound_occurrence(occurrence: Mapping[str, object]) -> None:
    """Fail closed unless all occurrence fields and digests are coherent."""

    if set(occurrence) != _BOUND_OCCURRENCE_FIELDS:
        raise CandidateBindingError("invalid bound occurrence fields")
    base = {field: occurrence[field] for field in _BASE_OCCURRENCE_FIELDS}
    expected = bind_occurrence(base)
    if dict(occurrence) != expected:
        raise CandidateBindingError("occurrence binding digest mismatch")


def _mapping_rows(
    value: Sequence[Mapping[str, object]] | object,
    *,
    label: str,
) -> list[Mapping[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise CandidateBindingError(f"{label} must be a sequence")
    rows: list[Mapping[str, object]] = []
    for row in value:
        if not isinstance(row, Mapping):
            raise CandidateBindingError(f"{label} row must be a mapping")
        rows.append(row)
    return rows


def validate_occurrence_authority(
    occurrence: Mapping[str, object],
    *,
    authority_inputs: Sequence[Mapping[str, object]] | object,
    authority_member_inputs: Sequence[Mapping[str, object]] | object,
) -> None:
    """Bind an internally coherent occurrence to independent authority inputs."""

    validate_bound_occurrence(occurrence)
    profile = _required_string(occurrence, "profile")
    source_id = _required_string(occurrence, "source_id")
    source_sha256 = _required_string(occurrence, "source_sha256")
    member = _required_string(occurrence, "member")
    member_sha256 = _required_string(occurrence, "member_sha256")

    source_matches = [
        row
        for row in _mapping_rows(authority_inputs, label="authority inputs")
        if row.get("authority_class") == "XLIFF_STANDARD_PACKAGE"
        and row.get("profile") == profile
        and row.get("source_id") == source_id
    ]
    if len(source_matches) != 1:
        raise CandidateBindingError(
            "occurrence authority source is missing or ambiguous"
        )
    if source_matches[0].get("source_sha256") != source_sha256:
        raise CandidateBindingError("occurrence authority source digest mismatch")

    member_matches = [
        row
        for row in _mapping_rows(
            authority_member_inputs,
            label="authority member inputs",
        )
        if row.get("profile") == profile
        and row.get("source_id") == source_id
        and row.get("member") == member
    ]
    if len(member_matches) != 1:
        raise CandidateBindingError(
            "occurrence authority member is missing or ambiguous"
        )
    expected_member = member_matches[0]
    if (
        expected_member.get("source_sha256") != source_sha256
        or expected_member.get("member_sha256") != member_sha256
    ):
        raise CandidateBindingError("occurrence authority member digest mismatch")


def candidate_content_sha256(candidate: Mapping[str, object]) -> str:
    """Hash stable identity, semantic class, profile relation, and occurrences."""

    missing = [
        field for field in _CANDIDATE_CONTENT_FIELDS if field not in candidate
    ]
    if missing:
        raise CandidateBindingError(f"candidate content fields missing: {missing}")
    occurrences = candidate["occurrences"]
    if not isinstance(occurrences, Sequence) or isinstance(
        occurrences, (str, bytes)
    ) or not occurrences:
        raise CandidateBindingError("candidate occurrences must be a sequence")
    source_kind = _required_string(candidate, "source_kind")
    candidate_class = _required_string(candidate, "candidate_class")
    semantic_location = _required_string(candidate, "semantic_location")
    for occurrence in occurrences:
        if not isinstance(occurrence, Mapping):
            raise CandidateBindingError("candidate occurrence must be a mapping")
        validate_bound_occurrence(occurrence)
        if occurrence["candidate_class"] != candidate_class:
            raise CandidateBindingError("candidate and occurrence classes differ")
        if occurrence["location"] != semantic_location:
            raise CandidateBindingError("candidate and occurrence locations differ")
        expected_class = classify_candidate(
            source_kind=source_kind,
            semantic_location=semantic_location,
            normalized_requirement=_required_string(
                occurrence,
                "normalized_requirement",
            ),
        )
        if expected_class != candidate_class:
            raise CandidateBindingError(
                "candidate class contradicts source kind or content"
            )
    payload = {
        field: candidate[field] for field in _CANDIDATE_CONTENT_FIELDS
    }
    return _canonical_sha256(payload)
