"""Digest-bound specification extraction for the SAL ingestion pipeline.

The first supported extractor is the XLIFF 2.x profile-surface compiler. It
reads pinned authority archives without extracting them to disk. Additional
format extractors must preserve the same fail-closed digest and output rules.
"""

# generated_by: codex

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any, Iterable, Mapping, NamedTuple, Sequence
import xml.etree.ElementTree as ET
import zipfile

import yaml

try:
    from tools.spec import xliff_core_candidate_binding as _candidate_binding
except ModuleNotFoundError:
    # Direct script execution places tools/spec, rather than the repository
    # root, on sys.path.  The sibling import preserves the CLI entry point.
    import xliff_core_candidate_binding as _candidate_binding  # type: ignore[no-redef,import-not-found]

try:
    from tools.spec import (
        xliff_core_candidate_adjudication as _candidate_adjudication,
    )
except ModuleNotFoundError:
    _candidate_adjudication = importlib.import_module(
        "xliff_core_candidate_adjudication"
    )


_CORE_CANDIDATE_CLASSES = _candidate_binding.CORE_CANDIDATE_CLASSES
CandidateBindingError = _candidate_binding.CandidateBindingError
bind_occurrence = _candidate_binding.bind_occurrence
candidate_content_sha256 = _candidate_binding.candidate_content_sha256
classify_candidate = _candidate_binding.classify_candidate
validate_occurrence_authority = _candidate_binding.validate_occurrence_authority


_XSD_NS = "http://www.w3.org/2001/XMLSchema"
_SCH_NS = "http://purl.oclc.org/dsdl/schematron"
_NVDL_NS = "http://purl.oclc.org/dsdl/nvdl/ns/structure/1.0"
_CORE_NAMESPACE = "urn:oasis:names:tc:xliff:document:2.0"
_MAX_ARCHIVE_MEMBERS = 256
_MAX_MEMBER_BYTES = 16 * 1024 * 1024
_MAX_ARCHIVE_UNCOMPRESSED_BYTES = 64 * 1024 * 1024
_MAX_COMPRESSION_RATIO = 250
_MAX_INTERNAL_ENTITIES = 64
_MAX_ENTITY_VALUE_BYTES = 4096
_XML_ID = "{http://www.w3.org/XML/1998/namespace}id"
_ENTITY_DECLARATION = re.compile(
    br"""<!ENTITY\s+([A-Za-z_:][A-Za-z0-9_.:-]*)\s+
    (?:"([^"]*)"|'([^']*)')\s*>""",
    re.IGNORECASE | re.VERBOSE,
)
_ENTITY_REFERENCE = re.compile(br"&([A-Za-z_:][A-Za-z0-9_.:-]*);")
_XML_COMMENT = re.compile(br"<!--.*?-->", re.DOTALL)
_PREDEFINED_ENTITIES = frozenset(
    {b"amp", b"apos", b"gt", b"lt", b"quot"}
)


class ExtractionError(RuntimeError):
    """Raised when authority input cannot be verified or safely interpreted."""


class MatrixDriftError(ExtractionError):
    """Raised when check mode observes output that differs from canonical bytes."""


class ProfileSource(NamedTuple):
    """One digest-pinned XLIFF profile authority package."""

    profile: str
    source_id: str
    package_path: Path
    expected_sha256: str
    prose_member: str


class PolicySource(NamedTuple):
    """One Git-tracked production-policy authority."""

    source_id: str
    path: Path


_PROFILE_MODULES: dict[str, dict[str, dict[str, Any]]] = {
    "xliff_2.0": {
        "translation_candidates": {
            "section_id": "candidates",
            "schema_vocabularies": ["matches"],
            "schema_members": ["schemas/modules/matches.xsd"],
        },
        "glossary": {
            "section_id": "glossary-module",
            "schema_vocabularies": ["glossary"],
            "schema_members": ["schemas/modules/glossary.xsd"],
        },
        "format_style": {
            "section_id": "fs-mod",
            "schema_vocabularies": ["fs"],
            "schema_members": ["schemas/modules/fs.xsd"],
        },
        "metadata": {
            "section_id": "metadata_module",
            "schema_vocabularies": ["metadata"],
            "schema_members": ["schemas/modules/metadata.xsd"],
        },
        "resource_data": {
            "section_id": "resourceData_module",
            "schema_vocabularies": ["resource_data"],
            "schema_members": ["schemas/modules/resource_data.xsd"],
        },
        "change_tracking": {
            "section_id": "changeTracking_module",
            "schema_vocabularies": ["change_tracking"],
            "schema_members": ["schemas/modules/change_tracking.xsd"],
        },
        "size_restriction": {
            "section_id": "size_restriction_module",
            "schema_vocabularies": ["size_restriction"],
            "schema_members": ["schemas/modules/size_restriction.xsd"],
        },
        "validation": {
            "section_id": "validation_module",
            "schema_vocabularies": ["validation"],
            "schema_members": ["schemas/modules/validation.xsd"],
        },
    },
    "xliff_2.1": {
        "translation_candidates": {
            "section_id": "candidates",
            "schema_vocabularies": ["matches"],
            "schema_members": ["schemas/matches.xsd"],
            "validation_members": ["schemas/matches.sch"],
        },
        "glossary": {
            "section_id": "glossary-module",
            "schema_vocabularies": ["glossary"],
            "schema_members": ["schemas/glossary.xsd"],
            "validation_members": ["schemas/glossary.sch"],
        },
        "format_style": {
            "section_id": "fs-mod",
            "schema_vocabularies": ["fs"],
            "schema_members": ["schemas/fs.xsd"],
            "validation_members": ["schemas/fs.sch"],
        },
        "metadata": {
            "section_id": "metadata_module",
            "schema_vocabularies": ["metadata"],
            "schema_members": ["schemas/metadata.xsd"],
            "validation_members": ["schemas/metadata.sch"],
        },
        "resource_data": {
            "section_id": "resourceData_module",
            "schema_vocabularies": ["resource_data"],
            "schema_members": ["schemas/resource_data.xsd"],
            "validation_members": ["schemas/resource_data.sch"],
        },
        "size_restriction": {
            "section_id": "size_restriction_module",
            "schema_vocabularies": ["size_restriction"],
            "schema_members": ["schemas/size_restriction.xsd"],
            "validation_members": ["schemas/size_restriction.sch"],
        },
        "validation": {
            "section_id": "validation_module",
            "schema_vocabularies": ["validation"],
            "schema_members": ["schemas/validation.xsd"],
            "validation_members": ["schemas/validation.sch"],
        },
        "its": {
            "section_id": "ITS-module",
            "schema_vocabularies": ["its", "itsm"],
            "schema_members": ["schemas/its.xsd", "schemas/itsm.xsd"],
            "validation_members": ["schemas/its.sch"],
        },
    },
}

_MODULE_LABELS = {
    "translation_candidates": "Translation Candidates / Matches",
    "glossary": "Glossary",
    "format_style": "Format Style",
    "metadata": "Metadata",
    "resource_data": "Resource Data",
    "change_tracking": "Change Tracking",
    "size_restriction": "Size and Length Restriction",
    "validation": "Validation",
    "its": "ITS",
}

_COMMON_CORE_REQUIREMENTS = (
    (
        "XLF-DELTA-CORE-001",
        "core",
        "Treat XLIFF Core as the stable document vocabulary shared by the supported 2.x profiles.",
    ),
    (
        "XLF-DELTA-CORE-002",
        "xliff",
        "Model the XLIFF document root, files, and language declarations as typed Core structures.",
    ),
    (
        "XLF-DELTA-CORE-003",
        "skeleton",
        "Represent internal and external skeleton references without losing their source relationships.",
    ),
    (
        "XLF-DELTA-CORE-004",
        "inlineCodes",
        "Preserve inline code identity, references, pairing, ordering, nesting, and original-data links.",
    ),
    (
        "XLF-DELTA-CORE-005",
        "segmentation",
        "Represent segmentation and re-segmentation controls as semantic Core behavior.",
    ),
    (
        "XLF-DELTA-CORE-006",
        "state",
        "Represent translation state and sub-state values without collapsing their processing meaning.",
    ),
    (
        "XLF-DELTA-CORE-007",
        "extensions",
        "Preserve permitted foreign namespaces while keeping extension support distinct from Core support.",
    ),
)

_XLIFF_CORE_CATEGORIES = frozenset(
    {
        "document_structure",
        "hierarchy_cardinality",
        "identifiers_references_inheritance",
        "language_direction_whitespace",
        "inline_code_semantics",
        "segmentation",
        "state",
        "source_target_correspondence",
        "agent_processing",
        "extension_preservation",
        "xml_security_resource_limits",
        "semantic_roundtrip_canonical_output",
    }
)
_CORE_REQUIREMENT_CLASSES = frozenset(
    {
        "CARDINALITY_CONSTRAINT",
        "PRESERVATION_REQUIREMENT",
        "PROCESSING_REQUIREMENT",
        "SEMANTIC_CONSTRAINT",
        "STRUCTURAL_CONSTRAINT",
    }
)
_CORE_NORMATIVE_LEVELS = frozenset({"MUST", "SHOULD", "MAY"})
_CORE_OBLIGATION_BASES = frozenset(
    {"XLIFF_SPECIFICATION", "PRODUCTION_POLICY"}
)
_CORE_OBLIGATION_ID = re.compile(
    r"^SAL-XLIFF-CORE-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{3}$"
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalized_text(value: str) -> str:
    return " ".join(value.split())


def _safe_member_name(name: str) -> bool:
    pure = PurePosixPath(name)
    parts = pure.parts
    return (
        bool(name)
        and bool(parts)
        and "\\" not in name
        and not pure.is_absolute()
        and ".." not in parts
        and ":" not in parts[0]
    )


def _read_authority_archive(source: ProfileSource) -> dict[str, bytes]:
    path = Path(source.package_path)
    if not path.is_file():
        raise ExtractionError(f"authority package missing: {path}")
    package = path.read_bytes()
    observed = _sha256(package)
    if observed != source.expected_sha256:
        raise ExtractionError(
            f"{source.source_id} digest mismatch: "
            f"expected {source.expected_sha256}, observed {observed}"
        )
    if not zipfile.is_zipfile(path):
        raise ExtractionError(f"{source.source_id} is not a ZIP authority package")

    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        if len(infos) > _MAX_ARCHIVE_MEMBERS:
            raise ExtractionError(
                f"{source.source_id} has {len(infos)} members; "
                f"limit is {_MAX_ARCHIVE_MEMBERS}"
            )
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or len(names) != len(
            {name.casefold() for name in names}
        ):
            raise ExtractionError(f"{source.source_id} contains duplicate member names")
        total = 0
        members: dict[str, bytes] = {}
        for info in infos:
            if not _safe_member_name(info.filename):
                raise ExtractionError(
                    f"{source.source_id} has unsafe member path: {info.filename}"
                )
            if info.is_dir():
                continue
            if info.file_size > _MAX_MEMBER_BYTES:
                raise ExtractionError(
                    f"{source.source_id}:{info.filename} exceeds the member limit"
                )
            total += info.file_size
            if total > _MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                raise ExtractionError(
                    f"{source.source_id} exceeds the uncompressed archive limit"
                )
            compressed = max(info.compress_size, 1)
            if info.file_size / compressed > _MAX_COMPRESSION_RATIO:
                raise ExtractionError(
                    f"{source.source_id}:{info.filename} exceeds compression ratio"
                )
            data = archive.read(info)
            if len(data) != info.file_size:
                raise ExtractionError(
                    f"{source.source_id}:{info.filename} was truncated"
                )
            members[info.filename] = data
    return members


def _doctype_span(data: bytes, *, location: str) -> tuple[int, int] | None:
    start = data.upper().find(b"<!DOCTYPE")
    if start < 0:
        return None
    quote: int | None = None
    subset_depth = 0
    for index in range(start, len(data)):
        byte = data[index]
        if quote is not None:
            if byte == quote:
                quote = None
            continue
        if byte in (ord('"'), ord("'")):
            quote = byte
        elif byte == ord("["):
            subset_depth += 1
        elif byte == ord("]") and subset_depth:
            subset_depth -= 1
        elif byte == ord(">") and subset_depth == 0:
            return start, index + 1
    raise ExtractionError(f"{location} contains an unterminated DOCTYPE")


def _safe_internal_entities(subset: bytes, *, location: str) -> dict[bytes, bytes]:
    clean = _XML_COMMENT.sub(b"", subset)
    declarations: dict[bytes, bytes] = {}
    cursor = 0
    for match in _ENTITY_DECLARATION.finditer(clean):
        if clean[cursor : match.start()].strip():
            raise ExtractionError(
                f"{location} contains an unsupported DTD declaration"
            )
        name = match.group(1)
        if name in declarations:
            raise ExtractionError(f"{location} contains duplicate entity {name!r}")
        value = match.group(2) if match.group(2) is not None else match.group(3)
        assert value is not None
        if len(value) > _MAX_ENTITY_VALUE_BYTES:
            raise ExtractionError(f"{location} entity {name!r} exceeds the limit")
        declarations[name] = value
        cursor = match.end()
    if clean[cursor:].strip():
        raise ExtractionError(f"{location} contains an unsupported DTD declaration")
    if len(declarations) > _MAX_INTERNAL_ENTITIES:
        raise ExtractionError(f"{location} has too many internal entities")

    resolved: dict[bytes, bytes] = {}

    def resolve(name: bytes, stack: tuple[bytes, ...]) -> bytes:
        if name in resolved:
            return resolved[name]
        if name in stack or len(stack) >= 8:
            raise ExtractionError(f"{location} contains recursive entity expansion")
        value = declarations[name]

        def replace(reference: re.Match[bytes]) -> bytes:
            referenced_name = reference.group(1)
            if referenced_name in _PREDEFINED_ENTITIES:
                return reference.group(0)
            if referenced_name not in declarations:
                raise ExtractionError(
                    f"{location} references undeclared entity {referenced_name!r}"
                )
            return resolve(referenced_name, (*stack, name))

        expanded = _ENTITY_REFERENCE.sub(replace, value)
        if len(expanded) > _MAX_ENTITY_VALUE_BYTES:
            raise ExtractionError(f"{location} entity {name!r} exceeds the limit")
        if b"<" in expanded or b">" in expanded:
            raise ExtractionError(
                f"{location} entity {name!r} contains prohibited markup"
            )
        resolved[name] = expanded
        return expanded

    for name in declarations:
        resolve(name, ())
    return resolved


def _prepare_xml(
    data: bytes,
    *,
    location: str,
    allow_doctype: bool,
    allow_internal_entities: bool,
) -> bytes:
    span = _doctype_span(data, location=location)
    if span is None:
        if b"<!ENTITY" in data.upper():
            raise ExtractionError(
                f"{location} contains a prohibited entity declaration"
            )
        return data
    if not allow_doctype:
        raise ExtractionError(f"{location} contains a prohibited DOCTYPE declaration")

    start, end = span
    declaration = data[start:end]
    entities: dict[bytes, bytes] = {}
    subset_start = declaration.find(b"[")
    if subset_start >= 0:
        subset_end = declaration.rfind(b"]")
        if subset_end < subset_start:
            raise ExtractionError(f"{location} contains an invalid DTD subset")
        if not allow_internal_entities:
            raise ExtractionError(
                f"{location} contains a prohibited internal DTD subset"
            )
        entities = _safe_internal_entities(
            declaration[subset_start + 1 : subset_end],
            location=location,
        )

    without_doctype = _XML_COMMENT.sub(b"", data[:start] + data[end:])

    def replace(reference: re.Match[bytes]) -> bytes:
        name = reference.group(1)
        if name in _PREDEFINED_ENTITIES:
            return reference.group(0)
        if name not in entities:
            raise ExtractionError(f"{location} references undeclared entity {name!r}")
        return entities[name]

    prepared = _ENTITY_REFERENCE.sub(replace, without_doctype)
    if len(prepared) > _MAX_MEMBER_BYTES:
        raise ExtractionError(f"{location} exceeds the post-expansion XML limit")
    return prepared


def _parse_xml(
    data: bytes,
    *,
    location: str,
    allow_doctype: bool = False,
    allow_internal_entities: bool = False,
) -> ET.Element:
    prepared = _prepare_xml(
        data,
        location=location,
        allow_doctype=allow_doctype,
        allow_internal_entities=allow_internal_entities,
    )
    try:
        return ET.fromstring(prepared)
    except ET.ParseError as exc:
        raise ExtractionError(f"invalid XML in {location}: {exc}") from exc


def _section_inventory(
    data: bytes,
    *,
    source_id: str,
    source_sha256: str,
    member: str,
) -> list[dict[str, Any]]:
    root = _parse_xml(
        data,
        location=f"{source_id}:{member}",
        allow_doctype=True,
    )
    rows: list[dict[str, Any]] = []

    def walk(node: ET.Element, parents: list[str]) -> None:
        for child in node:
            if child.tag == "section":
                title = next(
                    (
                        _normalized_text("".join(title_node.itertext()))
                        for title_node in child
                        if title_node.tag == "title"
                    ),
                    "",
                )
                title_path = [*parents, title]
                section_id = child.attrib.get("id") or child.attrib.get(_XML_ID)
                text = _normalized_text("".join(child.itertext()))
                location_id = section_id or "title:" + " > ".join(title_path)
                rows.append(
                    {
                        "location_id": location_id,
                        "section_id": section_id,
                        "title_path": " > ".join(title_path),
                        "text_sha256": _sha256(text.encode("utf-8")),
                        "paragraph_count": sum(1 for item in child if item.tag == "para"),
                        "source_id": source_id,
                        "source_sha256": source_sha256,
                        "member": member,
                        "member_sha256": _sha256(data),
                    }
                )
                walk(child, title_path)
            else:
                walk(child, parents)

    walk(root, [])
    if not rows:
        raise ExtractionError(f"{source_id}:{member} has no DocBook sections")
    return rows


def _schema_inventory(data: bytes, *, location: str) -> dict[str, Any]:
    root = _parse_xml(data, location=location)
    if root.tag != f"{{{_XSD_NS}}}schema":
        raise ExtractionError(f"{location} is not an XML Schema document")
    kinds = ("element", "attribute", "complexType", "simpleType", "group")
    counts: dict[str, int] = {}
    named: list[str] = []
    for kind in kinds:
        nodes = list(root.iter(f"{{{_XSD_NS}}}{kind}"))
        counts[kind] = len(nodes)
        named.extend(
            f"{kind}:{node.attrib['name']}"
            for node in nodes
            if node.attrib.get("name")
        )
    return {
        "target_namespace": root.attrib.get("targetNamespace"),
        "component_counts": counts,
        "named_components_sha256": _sha256(
            json.dumps(sorted(named), separators=(",", ":")).encode("utf-8")
        ),
    }


def _schematron_inventory(data: bytes, *, location: str) -> dict[str, Any]:
    root = _parse_xml(
        data,
        location=location,
        allow_doctype=True,
        allow_internal_entities=True,
    )
    asserts = list(root.iter(f"{{{_SCH_NS}}}assert"))
    reports = list(root.iter(f"{{{_SCH_NS}}}report"))
    tests = sorted(
        [
            f"assert:{item.attrib.get('test', '')}:{_normalized_text(''.join(item.itertext()))}"
            for item in asserts
        ]
        + [
            f"report:{item.attrib.get('test', '')}:{_normalized_text(''.join(item.itertext()))}"
            for item in reports
        ]
    )
    return {
        "assert_count": len(asserts),
        "report_count": len(reports),
        "rules_sha256": _sha256(
            json.dumps(tests, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )
        ),
    }


def _profile_inventory(
    source: ProfileSource,
    members: Mapping[str, bytes],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if source.prose_member not in members:
        raise ExtractionError(
            f"{source.source_id} lacks prose member {source.prose_member}"
        )
    prose = members[source.prose_member]
    sections = _section_inventory(
        prose,
        source_id=source.source_id,
        source_sha256=source.expected_sha256,
        member=source.prose_member,
    )
    sections_by_id = {
        str(row["section_id"]): row for row in sections if row["section_id"]
    }
    core_member = "schemas/xliff_core_2.0.xsd"
    if core_member not in members:
        raise ExtractionError(f"{source.source_id} lacks {core_member}")
    core_schema = _schema_inventory(
        members[core_member], location=f"{source.source_id}:{core_member}"
    )
    if core_schema["target_namespace"] != _CORE_NAMESPACE:
        raise ExtractionError(
            f"{source.source_id} core namespace is "
            f"{core_schema['target_namespace']!r}"
        )

    modules: dict[str, Any] = {}
    for module_name, declaration in _PROFILE_MODULES[source.profile].items():
        section_id = str(declaration["section_id"])
        if section_id not in sections_by_id:
            raise ExtractionError(
                f"{source.source_id} lacks module section {section_id}"
            )
        schema_members = list(declaration["schema_members"])
        validation_members = list(declaration.get("validation_members", []))
        for member in [*schema_members, *validation_members]:
            if member not in members:
                raise ExtractionError(f"{source.source_id} lacks {member}")
        modules[module_name] = {
            "status": "NORMATIVE_MODULE",
            "section_id": section_id,
            "section_title": sections_by_id[section_id]["title_path"],
            "schema_vocabularies": list(declaration["schema_vocabularies"]),
            "schema_members": [
                {
                    "path": member,
                    "sha256": _sha256(members[member]),
                    "inventory": _schema_inventory(
                        members[member],
                        location=f"{source.source_id}:{member}",
                    ),
                }
                for member in schema_members
            ],
            "validation_members": [
                {
                    "path": member,
                    "sha256": _sha256(members[member]),
                    "inventory": _schematron_inventory(
                        members[member],
                        location=f"{source.source_id}:{member}",
                    ),
                }
                for member in validation_members
            ],
        }

    informative_extensions: list[str] = []
    if source.profile == "xliff_2.1":
        informative_member = (
            "schemas/informativeCopiesOf3rdPartySchemas/extensions/"
            "change_tracking.xsd"
        )
        if informative_member not in members:
            raise ExtractionError(
                f"{source.source_id} lacks informative Change Tracking schema"
            )
        informative_extensions.append("change_tracking")

    validation_layers: list[dict[str, Any]] = [
        {
            "kind": "XSD",
            "member": core_member,
            "sha256": _sha256(members[core_member]),
        }
    ]
    core_schematron = "schemas/xliff_core_2.1.sch"
    if core_schematron in members:
        validation_layers.append(
            {
                "kind": "SCHEMATRON",
                "member": core_schematron,
                "sha256": _sha256(members[core_schematron]),
                "inventory": _schematron_inventory(
                    members[core_schematron],
                    location=f"{source.source_id}:{core_schematron}",
                ),
            }
        )
    nvdl = "schemas/xliff_2_advanced_validation.nvdl"
    if nvdl in members:
        nvdl_root = _parse_xml(members[nvdl], location=f"{source.source_id}:{nvdl}")
        if nvdl_root.tag != f"{{{_NVDL_NS}}}rules":
            raise ExtractionError(f"{source.source_id}:{nvdl} is not NVDL rules")
        validation_layers.append(
            {
                "kind": "NVDL",
                "member": nvdl,
                "sha256": _sha256(members[nvdl]),
                "start_mode": nvdl_root.attrib.get("startMode"),
            }
        )

    profile = {
        "source_id": source.source_id,
        "source_sha256": source.expected_sha256,
        "prose_member": source.prose_member,
        "prose_member_sha256": _sha256(prose),
        "section_count": len(sections),
        "core_schema": {
            "member": core_member,
            "sha256": _sha256(members[core_member]),
            "inventory": core_schema,
        },
        "module_count": len(modules),
        "module_schema_vocabulary_count": sum(
            len(module["schema_vocabularies"]) for module in modules.values()
        ),
        "modules": modules,
        "informative_extensions": informative_extensions,
        "validation_layers": validation_layers,
    }
    return profile, sections


def _section_delta(
    by_profile: Mapping[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    indexed = {
        profile: {row["location_id"]: row for row in rows}
        for profile, rows in by_profile.items()
    }
    rows: list[dict[str, Any]] = []
    for location_id in sorted(set(indexed["xliff_2.0"]) | set(indexed["xliff_2.1"])):
        row20 = indexed["xliff_2.0"].get(location_id)
        row21 = indexed["xliff_2.1"].get(location_id)
        if row20 is None:
            delta_class = "ADDED_IN_2.1"
        elif row21 is None:
            delta_class = "REMOVED_IN_2.1"
        elif (
            row20["text_sha256"] == row21["text_sha256"]
            and row20["title_path"] == row21["title_path"]
        ):
            delta_class = "UNCHANGED"
        else:
            delta_class = "CHANGED_IN_2.1"
        exemplar = row21 or row20
        assert exemplar is not None
        rows.append(
            {
                "location_id": location_id,
                "section_id": exemplar["section_id"],
                "title_path": exemplar["title_path"],
                "delta_class": delta_class,
                "xliff_2.0": row20,
                "xliff_2.1": row21,
            }
        )
    return rows


def _requirement_matrix(
    seeds: Iterable[Mapping[str, Any]],
    sources: Mapping[str, ProfileSource],
    members: Mapping[str, Mapping[str, bytes]],
    sections: Mapping[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    section_indexes = {
        profile: {
            str(row["section_id"]): row
            for row in profile_sections
            if row["section_id"]
        }
        for profile, profile_sections in sections.items()
    }
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    required = {
        "matrix_id",
        "primary_profile",
        "member",
        "normalized_requirement",
        "affected_profiles",
        "owner",
        "requirement_class",
        "confidence",
        "interpretation_note",
    }
    for raw in seeds:
        missing = sorted(required - set(raw))
        if missing:
            raise ExtractionError(f"matrix seed missing fields: {missing}")
        matrix_id = str(raw["matrix_id"])
        if matrix_id in seen:
            raise ExtractionError(f"duplicate matrix_id: {matrix_id}")
        seen.add(matrix_id)
        primary_profile = str(raw["primary_profile"])
        if primary_profile not in sources:
            raise ExtractionError(f"{matrix_id} has unknown profile {primary_profile}")
        member = str(raw["member"])
        if member not in members[primary_profile]:
            raise ExtractionError(f"{matrix_id} has missing member {member}")
        section_id = raw.get("section_id")
        if section_id and str(section_id) not in section_indexes[primary_profile]:
            raise ExtractionError(
                f"{matrix_id} has missing section {section_id} "
                f"in {primary_profile}"
            )
        normalized_requirement = _normalized_text(
            str(raw["normalized_requirement"])
        )
        if len(normalized_requirement) < 25:
            raise ExtractionError(f"{matrix_id} requirement is too short")
        affected_profiles = sorted(set(map(str, raw["affected_profiles"])))
        if not affected_profiles or not set(affected_profiles) <= set(sources):
            raise ExtractionError(f"{matrix_id} has invalid affected_profiles")
        source = sources[primary_profile]
        primary_member = members[primary_profile][member]
        row: dict[str, Any] = {
            "matrix_id": matrix_id,
            "authority_source_id": source.source_id,
            "source_sha256": source.expected_sha256,
            "member": member,
            "member_sha256": _sha256(primary_member),
            "section_id": str(section_id) if section_id else None,
            "schema_location": raw.get("schema_location"),
            "normalized_requirement": normalized_requirement,
            "affected_profiles": affected_profiles,
            "owner": str(raw["owner"]),
            "requirement_class": str(raw["requirement_class"]),
            "confidence": str(raw["confidence"]),
            "interpretation_note": str(raw["interpretation_note"]),
            "corroborating_authorities": [],
        }
        for profile in raw.get("corroborating_profiles", []):
            profile = str(profile)
            if profile not in sources:
                raise ExtractionError(
                    f"{matrix_id} has unknown corroborating profile {profile}"
                )
            other_member = sources[profile].prose_member
            other_section = (
                section_indexes[profile].get(str(section_id)) if section_id else None
            )
            if section_id and other_section is None:
                raise ExtractionError(
                    f"{matrix_id} lacks corroborating section {section_id} "
                    f"in {profile}"
                )
            row["corroborating_authorities"].append(
                {
                    "profile": profile,
                    "source_id": sources[profile].source_id,
                    "source_sha256": sources[profile].expected_sha256,
                    "member": other_member,
                    "member_sha256": _sha256(members[profile][other_member]),
                    "section_id": str(section_id) if section_id else None,
                }
            )
        rows.append(row)
    return sorted(rows, key=lambda item: item["matrix_id"])


def _prose_paragraph_index(
    data: bytes,
    *,
    location: str,
) -> dict[str, list[str]]:
    """Index normalized paragraph text under each source section identifier."""

    root = _parse_xml(
        data,
        location=location,
        allow_doctype=True,
        allow_internal_entities=True,
    )
    by_section: dict[str, list[str]] = {}
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] not in {"section", "appendix"}:
            continue
        section_id = element.attrib.get("id") or element.attrib.get(_XML_ID)
        if not section_id:
            continue
        if section_id in by_section:
            raise ExtractionError(f"{location} has duplicate section id {section_id}")
        paragraphs = [
            _normalized_text("".join(descendant.itertext()))
            for descendant in element.iter()
            if descendant.tag.rsplit("}", 1)[-1] in {"para", "simpara"}
        ]
        by_section[section_id] = [text for text in paragraphs if text]
    return by_section


def _default_core_policy_sources() -> list[PolicySource]:
    """Return the Git-tracked policies that define production-only duties."""

    repository_root = Path(__file__).resolve().parents[2]
    return [
        PolicySource(
            source_id="POLICY-SHARED-LIBRARY-CONTRACT",
            path=repository_root
            / "shared"
            / "format-contracts"
            / "policy"
            / "shared-library-contract.yaml",
        ),
        PolicySource(
            source_id="POLICY-XML-LOCALIZATION-FAMILY",
            path=repository_root
            / "shared"
            / "format-contracts"
            / "policy"
            / "family-packs"
            / "xml_localization.yaml",
        ),
    ]


def _policy_rule_index(source: PolicySource) -> tuple[str, dict[str, str]]:
    """Load one policy and return its digest plus unique ``id``/``text`` rules."""

    try:
        data = source.path.read_bytes()
    except OSError as exc:
        raise ExtractionError(
            f"{source.source_id} policy source is unreadable: {source.path}"
        ) from exc
    try:
        document = yaml.safe_load(data)
    except yaml.YAMLError as exc:
        raise ExtractionError(
            f"{source.source_id} policy source is invalid YAML"
        ) from exc
    rules: dict[str, str] = {}

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            rule_id = value.get("id")
            rule_text = value.get("text")
            if rule_id is not None and rule_text is not None:
                normalized_id = str(rule_id)
                normalized_text = _normalized_text(str(rule_text))
                if normalized_id in rules:
                    raise ExtractionError(
                        f"{source.source_id} has duplicate policy rule "
                        f"{normalized_id}"
                    )
                if not normalized_text:
                    raise ExtractionError(
                        f"{source.source_id}:{normalized_id} has empty text"
                    )
                rules[normalized_id] = normalized_text
            for child in value.values():
                visit(child)
        elif isinstance(value, Sequence) and not isinstance(
            value, (str, bytes)
        ):
            for child in value:
                visit(child)

    visit(document)
    if not rules:
        raise ExtractionError(f"{source.source_id} contains no policy rules")
    return _sha256(data), rules


def _core_obligation_rows(
    seeds: Iterable[Mapping[str, Any]],
    sources: Mapping[str, ProfileSource],
    archives: Mapping[str, Mapping[str, bytes]],
    *,
    batch_id: str,
    policy_sources: Sequence[PolicySource] = (),
) -> list[dict[str, Any]]:
    """Validate and bind curated Core rules to exact authority paragraphs."""

    paragraph_indexes = {
        profile: _prose_paragraph_index(
            archives[profile][source.prose_member],
            location=f"{source.source_id}:{source.prose_member}",
        )
        for profile, source in sources.items()
    }
    policy_indexes: dict[str, tuple[PolicySource, str, dict[str, str]]] = {}
    for source in policy_sources:
        if source.source_id in policy_indexes:
            raise ExtractionError(
                f"duplicate Core policy source_id: {source.source_id}"
            )
        digest, rules = _policy_rule_index(source)
        policy_indexes[source.source_id] = (source, digest, rules)
    required = {
        "obligation_id",
        "obligation_basis",
        "introduced_in_batch",
        "stable_profiles",
        "owner",
        "category",
        "normalized_rule",
        "requirement_class",
        "normative_level",
        "authority_locations",
        "evidence_requirements",
        "interpretation_note",
    }
    optional = {"adjudication_candidate_ids"}
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    stable_profile_set = set(sources)
    for raw in seeds:
        missing = sorted(required - set(raw))
        if missing:
            raise ExtractionError(f"Core obligation seed missing fields: {missing}")
        unsupported = sorted(set(raw) - required - optional)
        if unsupported:
            raise ExtractionError(
                "unsupported Core obligation seed fields: "
                f"{unsupported}"
            )

        obligation_id = str(raw["obligation_id"])
        if not _CORE_OBLIGATION_ID.fullmatch(obligation_id):
            raise ExtractionError(
                f"invalid Core obligation_id: {obligation_id}"
            )
        if obligation_id in seen:
            raise ExtractionError(f"duplicate Core obligation_id: {obligation_id}")
        seen.add(obligation_id)

        introduced_in_batch = str(raw["introduced_in_batch"])
        if not re.fullmatch(r"XLF-04-BATCH-[0-9]{3}", introduced_in_batch):
            raise ExtractionError(
                f"{obligation_id} has invalid introduced_in_batch"
            )
        requested_sequence = int(batch_id.rsplit("-", 1)[-1])
        introduced_sequence = int(introduced_in_batch.rsplit("-", 1)[-1])
        if introduced_sequence > requested_sequence:
            raise ExtractionError(
                f"{obligation_id} was introduced after requested batch "
                f"{batch_id}: {introduced_in_batch}"
            )

        stable_profiles = sorted(set(map(str, raw["stable_profiles"])))
        if (
            not stable_profiles
            or len(stable_profiles) != len(raw["stable_profiles"])
            or not set(stable_profiles) <= stable_profile_set
        ):
            raise ExtractionError(
                f"{obligation_id} has invalid stable_profiles"
            )

        owner = str(raw["owner"])
        if not owner.startswith("core:") or len(owner) <= len("core:"):
            raise ExtractionError(f"{obligation_id} has invalid Core owner")
        category = str(raw["category"])
        if category not in _XLIFF_CORE_CATEGORIES:
            raise ExtractionError(f"{obligation_id} has unknown Core category")
        requirement_class = str(raw["requirement_class"])
        if requirement_class not in _CORE_REQUIREMENT_CLASSES:
            raise ExtractionError(
                f"{obligation_id} has unknown requirement_class"
            )
        normative_level = str(raw["normative_level"])
        if normative_level not in _CORE_NORMATIVE_LEVELS:
            raise ExtractionError(f"{obligation_id} has invalid normative_level")
        obligation_basis = str(raw["obligation_basis"])
        if obligation_basis not in _CORE_OBLIGATION_BASES:
            raise ExtractionError(f"{obligation_id} has invalid obligation_basis")

        normalized_rule = _normalized_text(str(raw["normalized_rule"]))
        if len(normalized_rule) < 25:
            raise ExtractionError(f"{obligation_id} rule is too short")
        interpretation_note = _normalized_text(
            str(raw["interpretation_note"])
        )
        if len(interpretation_note) < 15:
            raise ExtractionError(
                f"{obligation_id} interpretation_note is too short"
            )
        adjudication_candidate_ids = sorted(
            set(map(str, raw.get("adjudication_candidate_ids", [])))
        )
        if (
            len(adjudication_candidate_ids)
            != len(raw.get("adjudication_candidate_ids", []))
            or any(
                not candidate_id.startswith("XLF-CAND-CORE-")
                for candidate_id in adjudication_candidate_ids
            )
        ):
            raise ExtractionError(
                f"{obligation_id} has invalid adjudication candidate IDs"
            )

        evidence = raw["evidence_requirements"]
        if not isinstance(evidence, Mapping):
            raise ExtractionError(
                f"{obligation_id} evidence_requirements must be a mapping"
            )
        positive = [
            _normalized_text(str(value))
            for value in evidence.get("positive", [])
            if _normalized_text(str(value))
        ]
        rejection = [
            _normalized_text(str(value))
            for value in evidence.get("rejection", [])
            if _normalized_text(str(value))
        ]
        if not positive or not rejection:
            raise ExtractionError(
                f"{obligation_id} requires positive and rejection evidence"
            )

        locations = raw["authority_locations"]
        if not isinstance(locations, Sequence) or isinstance(
            locations, (str, bytes)
        ):
            raise ExtractionError(
                f"{obligation_id} authority_locations must be a sequence"
            )
        bound_locations: list[dict[str, Any]] = []
        location_profiles: list[str] = []
        policy_location_count = 0
        for raw_location in locations:
            if not isinstance(raw_location, Mapping):
                raise ExtractionError(
                    f"{obligation_id} authority location must be a mapping"
                )
            location_kind = str(raw_location.get("location_kind", ""))
            if location_kind == "policy_rule":
                authority_source_id = str(
                    raw_location.get("authority_source_id", "")
                )
                policy = policy_indexes.get(authority_source_id)
                if policy is None:
                    raise ExtractionError(
                        f"{obligation_id} has unknown policy source "
                        f"{authority_source_id}"
                    )
                policy_source, source_sha256, rules = policy
                rule_id = str(raw_location.get("rule_id", ""))
                source_text = rules.get(rule_id)
                if source_text is None:
                    raise ExtractionError(
                        f"{obligation_id} has missing policy rule "
                        f"{authority_source_id}:{rule_id}"
                    )
                bound_locations.append(
                    {
                        "authority_source_id": authority_source_id,
                        "source_sha256": source_sha256,
                        "location_kind": "policy_rule",
                        "path": policy_source.path.resolve().relative_to(
                            Path(__file__).resolve().parents[2]
                        ).as_posix(),
                        "rule_id": rule_id,
                        "source_text_sha256": _sha256(
                            source_text.encode("utf-8")
                        ),
                    }
                )
                policy_location_count += 1
                continue
            if location_kind != "prose_paragraph":
                raise ExtractionError(
                    f"{obligation_id} has unsupported authority location kind"
                )
            profile = str(raw_location.get("profile", ""))
            if profile not in sources:
                raise ExtractionError(
                    f"{obligation_id} has unknown authority profile {profile}"
                )
            profile_source = sources[profile]
            member = str(raw_location.get("member", ""))
            if (
                member != profile_source.prose_member
                or member not in archives[profile]
            ):
                raise ExtractionError(
                    f"{obligation_id} has invalid prose member for {profile}"
                )
            section_id = str(raw_location.get("section_id", ""))
            paragraphs = paragraph_indexes[profile].get(section_id)
            if paragraphs is None:
                raise ExtractionError(
                    f"{obligation_id} has missing section {section_id} "
                    f"in {profile}"
                )
            source_anchor = _normalized_text(
                str(raw_location.get("source_anchor", ""))
            )
            if len(source_anchor) < 10:
                raise ExtractionError(
                    f"{obligation_id} source anchor is too short"
                )
            paragraph_index = raw_location.get("paragraph_index")
            if paragraph_index is None:
                matches = [
                    index
                    for index, paragraph in enumerate(paragraphs)
                    if source_anchor in paragraph
                ]
                if len(matches) != 1:
                    raise ExtractionError(
                        f"{obligation_id} source anchor must resolve exactly "
                        f"once in {profile}:{section_id}; matches={len(matches)}"
                    )
                paragraph_index = matches[0]
            if (
                not isinstance(paragraph_index, int)
                or isinstance(paragraph_index, bool)
                or paragraph_index < 0
                or paragraph_index >= len(paragraphs)
            ):
                raise ExtractionError(
                    f"{obligation_id} has invalid paragraph_index "
                    f"for {profile}:{section_id}"
                )
            source_text = paragraphs[paragraph_index]
            if source_anchor not in source_text:
                raise ExtractionError(
                    f"{obligation_id} source anchor is absent from "
                    f"{profile}:{section_id}:{paragraph_index}"
                )
            member_bytes = archives[profile][member]
            bound_locations.append(
                {
                    "profile": profile,
                    "authority_source_id": profile_source.source_id,
                    "source_sha256": profile_source.expected_sha256,
                    "location_kind": "prose_paragraph",
                    "member": member,
                    "member_sha256": _sha256(member_bytes),
                    "section_id": section_id,
                    "paragraph_index": paragraph_index,
                    "source_anchor": source_anchor,
                    "source_text_sha256": _sha256(source_text.encode("utf-8")),
                }
            )
            location_profiles.append(profile)
        if obligation_basis == "XLIFF_SPECIFICATION":
            if policy_location_count:
                raise ExtractionError(
                    f"{obligation_id} specification obligation cannot use "
                    "production-policy authority"
                )
            if (
                len(set(location_profiles)) != len(location_profiles)
                or sorted(location_profiles) != stable_profiles
            ):
                raise ExtractionError(
                    f"{obligation_id} authority profiles must exactly match "
                    "stable_profiles"
                )
        elif location_profiles or not policy_location_count:
            raise ExtractionError(
                f"{obligation_id} production-policy obligation must use only "
                "policy-rule authority"
            )

        row = {
                "obligation_id": obligation_id,
                "obligation_basis": obligation_basis,
                "conformance_effect": (
                    "STANDARD_CONFORMANCE"
                    if obligation_basis == "XLIFF_SPECIFICATION"
                    else "PRODUCTION_PROFILE_ONLY"
                ),
                "introduced_in_batch": introduced_in_batch,
                "stable_profiles": stable_profiles,
                "owner": owner,
                "category": category,
                "normalized_rule": normalized_rule,
                "requirement_class": requirement_class,
                "normative_level": normative_level,
                "authority_locations": sorted(
                    bound_locations,
                    key=lambda item: (
                        str(item.get("profile", "")),
                        str(item["authority_source_id"]),
                        str(item.get("rule_id", "")),
                    ),
                ),
                "evidence_requirements": {
                    "positive": positive,
                    "rejection": rejection,
                },
                "interpretation_note": interpretation_note,
                "verification_status": "SOURCE_BOUND_UNVERIFIED",
            }
        if adjudication_candidate_ids:
            row["adjudication_candidate_ids"] = (
                adjudication_candidate_ids
            )
        rows.append(row)
    return sorted(rows, key=lambda item: item["obligation_id"])


_EXPECTED_CORE_IDS_BY_CATEGORY: dict[str, tuple[str, ...]] = {
    "document_structure": (
        "SAL-XLIFF-CORE-DOCUMENT-ROOT-001",
        "SAL-XLIFF-CORE-DOCUMENT-VERSION-001",
        "SAL-XLIFF-CORE-DOCUMENT-NAMESPACE-001",
        "SAL-XLIFF-CORE-DOCUMENT-SOURCE-LANGUAGE-001",
        "SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001",
        "SAL-XLIFF-CORE-DOCUMENT-FILE-MINIMUM-001",
        "SAL-XLIFF-CORE-DOCUMENT-FILE-ORDER-001",
    ),
    "hierarchy_cardinality": (
        "SAL-XLIFF-CORE-HIERARCHY-UNIT-001",
        "SAL-XLIFF-CORE-HIERARCHY-FILE-CHILDREN-001",
        "SAL-XLIFF-CORE-HIERARCHY-GROUP-CHILDREN-001",
        "SAL-XLIFF-CORE-HIERARCHY-UNIT-CHILDREN-001",
        "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001",
        "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001",
        "SAL-XLIFF-CORE-HIERARCHY-NOTES-001",
        "SAL-XLIFF-CORE-HIERARCHY-ORIGINAL-DATA-001",
        "SAL-XLIFF-CORE-HIERARCHY-SKELETON-001",
        "SAL-XLIFF-CORE-HIERARCHY-EXTENSION-POINTS-001",
        "SAL-XLIFF-CORE-HIERARCHY-ORDER-001",
    ),
    "identifiers_references_inheritance": (
        "SAL-XLIFF-CORE-ID-FILE-UNIQUE-001",
        "SAL-XLIFF-CORE-ID-GROUP-UNIQUE-001",
        "SAL-XLIFF-CORE-ID-UNIT-UNIQUE-001",
        "SAL-XLIFF-CORE-ID-SEGMENT-UNIQUE-001",
        "SAL-XLIFF-CORE-ID-DATA-UNIQUE-001",
        "SAL-XLIFF-CORE-ID-NOTE-UNIQUE-001",
        "SAL-XLIFF-CORE-REFERENCE-DATAREF-001",
        "SAL-XLIFF-CORE-REFERENCE-FRAGMENT-INHERIT-001",
        "SAL-XLIFF-CORE-REFERENCE-COPYOF-001",
        "SAL-XLIFF-CORE-REFERENCE-STARTREF-001",
        "SAL-XLIFF-CORE-REFERENCE-SKELETON-HREF-001",
        "SAL-XLIFF-CORE-INHERIT-TRANSLATE-001",
    ),
    "language_direction_whitespace": (
        "SAL-XLIFF-CORE-LANGUAGE-SOURCE-001",
        "SAL-XLIFF-CORE-LANGUAGE-TARGET-001",
        "SAL-XLIFF-CORE-LANGUAGE-ROOT-SOURCE-001",
        "SAL-XLIFF-CORE-LANGUAGE-ROOT-TARGET-001",
        "SAL-XLIFF-CORE-DIRECTION-SOURCE-001",
        "SAL-XLIFF-CORE-DIRECTION-TARGET-001",
        "SAL-XLIFF-CORE-WHITESPACE-INHERIT-001",
        "SAL-XLIFF-CORE-WHITESPACE-PRESERVE-001",
    ),
    "inline_code_semantics": (
        "SAL-XLIFF-CORE-INLINE-SPANNING-001",
        "SAL-XLIFF-CORE-INLINE-PH-001",
        "SAL-XLIFF-CORE-INLINE-PC-001",
        "SAL-XLIFF-CORE-INLINE-SC-001",
        "SAL-XLIFF-CORE-INLINE-EC-001",
        "SAL-XLIFF-CORE-INLINE-MRK-001",
        "SAL-XLIFF-CORE-INLINE-SM-001",
        "SAL-XLIFF-CORE-INLINE-EM-001",
        "SAL-XLIFF-CORE-INLINE-PAIRING-001",
        "SAL-XLIFF-CORE-INLINE-NESTING-001",
        "SAL-XLIFF-CORE-INLINE-ISOLATION-001",
        "SAL-XLIFF-CORE-INLINE-ORDER-001",
        "SAL-XLIFF-CORE-INLINE-DATAREF-001",
        "SAL-XLIFF-CORE-INLINE-COPYOF-001",
        "SAL-XLIFF-CORE-INLINE-STARTREF-001",
        "SAL-XLIFF-CORE-INLINE-CANCOPY-001",
        "SAL-XLIFF-CORE-INLINE-CANDELETE-001",
        "SAL-XLIFF-CORE-INLINE-CANREORDER-001",
        "SAL-XLIFF-CORE-INLINE-OVERLAP-001",
        "SAL-XLIFF-CORE-INLINE-ORIGINAL-DATA-001",
    ),
    "segmentation": (
        "SAL-XLIFF-CORE-SEGMENT-SPLIT-001",
        "SAL-XLIFF-CORE-SEGMENT-CANRESEGMENT-INHERIT-001",
        "SAL-XLIFF-CORE-SEGMENT-JOIN-001",
        "SAL-XLIFF-CORE-SEGMENT-SPLIT-MAPPING-001",
        "SAL-XLIFF-CORE-SEGMENT-TARGET-ORDER-001",
        "SAL-XLIFF-CORE-SEGMENT-INLINE-INTEGRITY-001",
        "SAL-XLIFF-CORE-SEGMENT-WHITESPACE-001",
    ),
    "state": (
        "SAL-XLIFF-CORE-STATE-SUBSTATE-001",
        "SAL-XLIFF-CORE-STATE-VALUE-001",
        "SAL-XLIFF-CORE-STATE-SUBSTATE-VALUE-001",
        "SAL-XLIFF-CORE-STATE-TARGET-PRESENCE-001",
        "SAL-XLIFF-CORE-STATE-TRANSITION-001",
    ),
    "source_target_correspondence": (
        "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001",
        "SAL-XLIFF-CORE-TARGET-LANGUAGE-001",
        "SAL-XLIFF-CORE-TARGET-ORDER-001",
        "SAL-XLIFF-CORE-SOURCE-TARGET-STRUCTURE-001",
        "SAL-XLIFF-CORE-SOURCE-TARGET-INLINE-001",
        "SAL-XLIFF-CORE-SOURCE-REQUIRED-001",
        "SAL-XLIFF-CORE-TARGET-PRESENCE-001",
        "SAL-XLIFF-CORE-TARGET-ORDER-CONFLICT-001",
    ),
    "agent_processing": (
        "SAL-XLIFF-CORE-AGENT-INLINE-001",
        "SAL-XLIFF-CORE-AGENT-EXTRACTOR-001",
        "SAL-XLIFF-CORE-AGENT-WRITER-001",
        "SAL-XLIFF-CORE-AGENT-MODIFIER-001",
        "SAL-XLIFF-CORE-AGENT-MERGER-001",
        "SAL-XLIFF-CORE-AGENT-VALIDATOR-001",
        "SAL-XLIFF-CORE-AGENT-LOSS-REPORT-001",
    ),
    "extension_preservation": (
        "SAL-XLIFF-CORE-EXTENSION-PRESERVE-001",
        "SAL-XLIFF-CORE-EXTENSION-NAMESPACE-001",
        "SAL-XLIFF-CORE-EXTENSION-CORE-CONFLICT-001",
        "SAL-XLIFF-CORE-EXTENSION-MERGER-RELIANCE-001",
        "SAL-XLIFF-CORE-EXTENSION-UNKNOWN-PRESERVE-001",
        "SAL-XLIFF-CORE-EXTENSION-DOWNGRADE-LOSS-001",
    ),
    "xml_security_resource_limits": (
        "SAL-XLIFF-CORE-SECURITY-URI-RISK-001",
        "SAL-XLIFF-CORE-SECURITY-EXTERNAL-RESOLUTION-001",
        "SAL-XLIFF-CORE-SECURITY-RESOURCE-LIMITS-001",
        "SAL-XLIFF-CORE-SECURITY-XML-ENTITY-001",
        "SAL-XLIFF-CORE-SECURITY-NESTING-LIMIT-001",
        "SAL-XLIFF-CORE-SECURITY-ELEMENT-LIMIT-001",
        "SAL-XLIFF-CORE-SECURITY-TEXT-LIMIT-001",
        "SAL-XLIFF-CORE-SECURITY-PATH-TRAVERSAL-001",
    ),
    "semantic_roundtrip_canonical_output": (
        "SAL-XLIFF-CORE-ROUNDTRIP-STRUCTURE-001",
        "SAL-XLIFF-CORE-ROUNDTRIP-SEMANTIC-001",
        "SAL-XLIFF-CORE-WRITE-DETERMINISTIC-001",
        "SAL-XLIFF-CORE-WRITE-LOSSLESS-NORMALIZED-001",
        "SAL-XLIFF-CORE-WRITE-SCHEMA-ORDER-001",
        "SAL-XLIFF-CORE-WRITE-NAMESPACE-PREFIX-001",
    ),
}

_PRODUCTION_POLICY_EXPECTED_IDS = frozenset(
    {
        "SAL-XLIFF-CORE-AGENT-LOSS-REPORT-001",
        "SAL-XLIFF-CORE-EXTENSION-DOWNGRADE-LOSS-001",
        "SAL-XLIFF-CORE-ROUNDTRIP-SEMANTIC-001",
        "SAL-XLIFF-CORE-SECURITY-ELEMENT-LIMIT-001",
        "SAL-XLIFF-CORE-SECURITY-EXTERNAL-RESOLUTION-001",
        "SAL-XLIFF-CORE-SECURITY-NESTING-LIMIT-001",
        "SAL-XLIFF-CORE-SECURITY-PATH-TRAVERSAL-001",
        "SAL-XLIFF-CORE-SECURITY-RESOURCE-LIMITS-001",
        "SAL-XLIFF-CORE-SECURITY-TEXT-LIMIT-001",
        "SAL-XLIFF-CORE-SECURITY-XML-ENTITY-001",
        "SAL-XLIFF-CORE-WRITE-DETERMINISTIC-001",
        "SAL-XLIFF-CORE-WRITE-LOSSLESS-NORMALIZED-001",
        "SAL-XLIFF-CORE-WRITE-NAMESPACE-PREFIX-001",
    }
)


def _default_core_obligation_expectations() -> list[dict[str, Any]]:
    """Return the explicit, still-open XLIFF Core work denominator."""

    rows: list[dict[str, Any]] = []
    for category, obligation_ids in _EXPECTED_CORE_IDS_BY_CATEGORY.items():
        for obligation_id in obligation_ids:
            rows.append(
                {
                    "obligation_id": obligation_id,
                    "category": category,
                    "stable_profiles": (
                        ["xliff_2.1"]
                        if obligation_id
                        in {
                            "SAL-XLIFF-CORE-INLINE-PAIRING-001",
                            "SAL-XLIFF-CORE-SECURITY-URI-RISK-001",
                        }
                        else ["xliff_2.0", "xliff_2.1"]
                    ),
                    "obligation_basis": (
                        "PRODUCTION_POLICY"
                        if obligation_id in _PRODUCTION_POLICY_EXPECTED_IDS
                        else "XLIFF_SPECIFICATION"
                    ),
                }
            )
    return sorted(rows, key=lambda item: item["obligation_id"])


_NORMATIVE_MODAL = re.compile(
    r"\b(?:must(?:\s+not)?|shall(?:\s+not)?|should(?:\s+not)?|"
    r"required|recommended|may|optional)\b",
    re.IGNORECASE,
)
_XSD_CANDIDATE_KINDS = frozenset(
    {
        "all",
        "any",
        "anyAttribute",
        "attribute",
        "choice",
        "complexType",
        "element",
        "enumeration",
        "extension",
        "field",
        "fractionDigits",
        "group",
        "import",
        "key",
        "keyref",
        "length",
        "list",
        "maxExclusive",
        "maxInclusive",
        "maxLength",
        "minExclusive",
        "minInclusive",
        "minLength",
        "pattern",
        "restriction",
        "selector",
        "sequence",
        "simpleType",
        "totalDigits",
        "union",
        "unique",
        "whiteSpace",
    }
)


def _element_local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _section_token(section: ET.Element) -> str:
    section_id = section.attrib.get("id") or section.attrib.get(_XML_ID)
    if section_id:
        return section_id
    title = next(
        (
            _normalized_text("".join(child.itertext()))
            for child in section
            if child.tag == "title"
        ),
        "",
    )
    if not title:
        raise ExtractionError("Core prose contains an unnamed section")
    return "title-" + re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")


def _candidate_occurrence(
    *,
    source_kind: str,
    profile: str,
    source: ProfileSource,
    member: str,
    member_bytes: bytes,
    locator: str,
    normalized_requirement: str,
) -> dict[str, str]:
    try:
        candidate_class = classify_candidate(
            source_kind=source_kind,
            semantic_location=locator,
            normalized_requirement=normalized_requirement,
        )
        return bind_occurrence(
            {
                "profile": profile,
                "source_id": source.source_id,
                "source_sha256": source.expected_sha256,
                "member": member,
                "member_sha256": _sha256(member_bytes),
                "location": locator,
                "candidate_class": candidate_class,
                "normalized_requirement": normalized_requirement,
            }
        )
    except CandidateBindingError as exc:
        raise ExtractionError(f"candidate content binding failed: {exc}") from exc


def _core_prose_candidate_occurrences(
    source: ProfileSource,
    members: Mapping[str, bytes],
) -> list[dict[str, str]]:
    member = source.prose_member
    if member not in members:
        raise ExtractionError(f"{source.source_id} lacks {member}")
    member_bytes = members[member]
    root = _parse_xml(
        member_bytes,
        location=f"{source.source_id}:{member}",
        allow_doctype=True,
    )
    core_sections = [
        node
        for node in root.iter("section")
        if (node.attrib.get("id") or node.attrib.get(_XML_ID)) == "core"
    ]
    if len(core_sections) != 1:
        raise ExtractionError(
            f"{source.source_id}:{member} requires exactly one Core section"
        )
    rows: list[dict[str, str]] = []
    candidate_ordinals: dict[tuple[tuple[str, ...], str], int] = {}

    def walk(node: ET.Element, section_path: tuple[str, ...]) -> None:
        current_path = section_path
        if node.tag == "section":
            current_path = (*section_path, _section_token(node))
        for child in node:
            normalized = _normalized_text("".join(child.itertext()))
            candidate = child.tag == "para" and bool(
                _NORMATIVE_MODAL.search(normalized)
            )
            if child.tag == "listitem" and _NORMATIVE_MODAL.search(normalized):
                candidate = not any(
                    descendant is not child
                    and descendant.tag in {"para", "listitem"}
                    and _NORMATIVE_MODAL.search(
                        _normalized_text("".join(descendant.itertext()))
                    )
                    for descendant in child.iter()
                )
            if candidate:
                ordinal_key = (current_path, child.tag)
                ordinal = candidate_ordinals.get(ordinal_key, 0) + 1
                candidate_ordinals[ordinal_key] = ordinal
                locator = (
                    "prose/"
                    + "/".join(current_path)
                    + f"/{child.tag}[{ordinal}]"
                )
                rows.append(
                    _candidate_occurrence(
                        source_kind="NORMATIVE_PROSE",
                        profile=source.profile,
                        source=source,
                        member=member,
                        member_bytes=member_bytes,
                        locator=locator,
                        normalized_requirement=normalized,
                    )
                )
            walk(child, current_path)

    walk(core_sections[0], ())
    if not rows:
        raise ExtractionError(
            f"{source.source_id}:{member} has no Core normative prose candidates"
        )
    return rows


def _core_non_modal_prose_candidate_occurrences(
    source: ProfileSource,
    members: Mapping[str, bytes],
) -> list[dict[str, str]]:
    """Enumerate every non-modal Core paragraph and leaf list item once."""

    member = source.prose_member
    if member not in members:
        raise ExtractionError(f"{source.source_id} lacks {member}")
    member_bytes = members[member]
    root = _parse_xml(
        member_bytes,
        location=f"{source.source_id}:{member}",
        allow_doctype=True,
    )
    core_sections = [
        node
        for node in root.iter("section")
        if (node.attrib.get("id") or node.attrib.get(_XML_ID)) == "core"
    ]
    if len(core_sections) != 1:
        raise ExtractionError(
            f"{source.source_id}:{member} requires exactly one Core section"
        )
    rows: list[dict[str, str]] = []
    candidate_ordinals: dict[tuple[tuple[str, ...], str], int] = {}

    def walk(node: ET.Element, section_path: tuple[str, ...]) -> None:
        current_path = section_path
        if node.tag == "section":
            current_path = (*section_path, _section_token(node))
        for child in node:
            normalized = _normalized_text("".join(child.itertext()))
            has_modal = bool(_NORMATIVE_MODAL.search(normalized))
            is_leaf_list_item = child.tag == "listitem" and not any(
                descendant is not child
                and descendant.tag in {"para", "listitem"}
                for descendant in child.iter()
            )
            candidate = (
                child.tag == "para" or is_leaf_list_item
            ) and bool(normalized) and not has_modal
            if candidate:
                ordinal_key = (current_path, child.tag)
                ordinal = candidate_ordinals.get(ordinal_key, 0) + 1
                candidate_ordinals[ordinal_key] = ordinal
                locator = (
                    "prose-nonmodal/"
                    + "/".join(current_path)
                    + f"/{child.tag}[{ordinal}]"
                )
                rows.append(
                    _candidate_occurrence(
                        source_kind="NON_MODAL_PROSE",
                        profile=source.profile,
                        source=source,
                        member=member,
                        member_bytes=member_bytes,
                        locator=locator,
                        normalized_requirement=normalized,
                    )
                )
            walk(child, current_path)

    walk(core_sections[0], ())
    return rows


def _core_xsd_candidate_occurrences(
    source: ProfileSource,
    members: Mapping[str, bytes],
) -> list[dict[str, str]]:
    member = "schemas/xliff_core_2.0.xsd"
    if member not in members:
        raise ExtractionError(f"{source.source_id} lacks {member}")
    member_bytes = members[member]
    root = _parse_xml(member_bytes, location=f"{source.source_id}:{member}")
    if root.tag != f"{{{_XSD_NS}}}schema":
        raise ExtractionError(f"{source.source_id}:{member} is not XSD")
    if root.attrib.get("targetNamespace") != _CORE_NAMESPACE:
        raise ExtractionError(
            f"{source.source_id}:{member} has the wrong Core namespace"
        )
    rows: list[dict[str, str]] = []

    def walk(node: ET.Element, path: tuple[str, ...]) -> None:
        ordinals: dict[str, int] = {}
        for child in node:
            kind = _element_local_name(child.tag)
            ordinals[kind] = ordinals.get(kind, 0) + 1
            identity = (
                child.attrib.get("name")
                or child.attrib.get("ref")
                or child.attrib.get("value")
                or str(ordinals[kind])
            )
            token = f"{kind}:{identity}"
            child_path = (*path, token)
            if kind in _XSD_CANDIDATE_KINDS:
                normalized = json.dumps(
                    {
                        "ancestors": list(path),
                        "attributes": dict(sorted(child.attrib.items())),
                        "kind": kind,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                rows.append(
                    _candidate_occurrence(
                        source_kind="CORE_XSD",
                        profile=source.profile,
                        source=source,
                        member=member,
                        member_bytes=member_bytes,
                        locator="xsd/" + "/".join(child_path),
                        normalized_requirement=normalized,
                    )
                )
            walk(child, child_path)

    walk(root, ())
    if not rows:
        raise ExtractionError(f"{source.source_id}:{member} has no XSD candidates")
    return rows


def _core_schematron_candidate_occurrences(
    source: ProfileSource,
    members: Mapping[str, bytes],
) -> list[dict[str, str]]:
    member = "schemas/xliff_core_2.1.sch"
    if member not in members:
        if source.profile == "xliff_2.0":
            return []
        raise ExtractionError(f"{source.source_id} lacks {member}")
    member_bytes = members[member]
    root = _parse_xml(
        member_bytes,
        location=f"{source.source_id}:{member}",
        allow_doctype=True,
        allow_internal_entities=True,
    )
    rows: list[dict[str, str]] = []
    rule_ordinal = 0
    for rule in root.iter(f"{{{_SCH_NS}}}rule"):
        rule_ordinal += 1
        context = rule.attrib.get("context", "")
        assertion_ordinal = 0
        for child in rule:
            kind = _element_local_name(child.tag)
            if kind not in {"assert", "report"}:
                continue
            assertion_ordinal += 1
            normalized = json.dumps(
                {
                    "context": context,
                    "kind": kind,
                    "message": _normalized_text("".join(child.itertext())),
                    "test": child.attrib.get("test", ""),
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            locator = (
                f"schematron/rule[{rule_ordinal}]"
                f"/{kind}[{assertion_ordinal}]"
            )
            rows.append(
                _candidate_occurrence(
                    source_kind="CORE_SCHEMATRON",
                    profile=source.profile,
                    source=source,
                    member=member,
                    member_bytes=member_bytes,
                    locator=locator,
                    normalized_requirement=normalized,
                )
            )
    if source.profile == "xliff_2.1" and not rows:
        raise ExtractionError(
            f"{source.source_id}:{member} has no Schematron assertions"
        )
    return rows


def _candidate_relation(occurrences: Sequence[Mapping[str, str]]) -> str:
    profiles = {str(row["profile"]) for row in occurrences}
    if profiles == {"xliff_2.0"}:
        return "REMOVED_IN_XLIFF_2_1"
    if profiles == {"xliff_2.1"}:
        return "ADDED_IN_XLIFF_2_1"
    if profiles != {"xliff_2.0", "xliff_2.1"}:
        raise ExtractionError(f"invalid candidate profile set: {sorted(profiles)}")
    requirements = {
        str(row["requirement_sha256"]) for row in occurrences
    }
    return "COMMON_IDENTICAL" if len(requirements) == 1 else "COMMON_CHANGED"


def _candidate_disposition(
    candidate: Mapping[str, Any],
    expected_ids: set[str],
) -> dict[str, Any]:
    text = " ".join(
        [
            str(candidate["semantic_location"]),
            *[
                str(row["normalized_requirement"])
                for row in candidate["occurrences"]
            ],
        ]
    ).casefold()
    source_kind = str(candidate["source_kind"])
    obligation_ids: set[str] = set()
    mapping_rule_ids: set[str] = set()

    keyword_rules: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
        (("skeleton", "href"), ("SAL-XLIFF-CORE-REFERENCE-SKELETON-HREF-001",)),
        (("substate",), ("SAL-XLIFF-CORE-STATE-SUBSTATE-001",)),
        (("state",), ("SAL-XLIFF-CORE-STATE-VALUE-001",)),
        (("canresegment",), ("SAL-XLIFF-CORE-SEGMENT-CANRESEGMENT-INHERIT-001",)),
        (("segmentation",), ("SAL-XLIFF-CORE-SEGMENT-SPLIT-001",)),
        (("datarefstart",), ("SAL-XLIFF-CORE-INLINE-DATAREF-001",)),
        (("datarefend",), ("SAL-XLIFF-CORE-INLINE-DATAREF-001",)),
        (("dataref",), ("SAL-XLIFF-CORE-REFERENCE-DATAREF-001",)),
        (("startref",), ("SAL-XLIFF-CORE-REFERENCE-STARTREF-001",)),
        (("copyof",), ("SAL-XLIFF-CORE-REFERENCE-COPYOF-001",)),
        (("cancopy",), ("SAL-XLIFF-CORE-INLINE-CANCOPY-001",)),
        (("candelete",), ("SAL-XLIFF-CORE-INLINE-CANDELETE-001",)),
        (("canreorder",), ("SAL-XLIFF-CORE-INLINE-CANREORDER-001",)),
        (("xml:space",), ("SAL-XLIFF-CORE-WHITESPACE-INHERIT-001",)),
        (("srcdir",), ("SAL-XLIFF-CORE-DIRECTION-SOURCE-001",)),
        (("trgdir",), ("SAL-XLIFF-CORE-DIRECTION-TARGET-001",)),
        (("srclang",), ("SAL-XLIFF-CORE-DOCUMENT-SOURCE-LANGUAGE-001",)),
        (("trglang",), ("SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001",)),
        (("translate",), ("SAL-XLIFF-CORE-INHERIT-TRANSLATE-001",)),
        (("version",), ("SAL-XLIFF-CORE-DOCUMENT-VERSION-001",)),
        (("anyattribute",), ("SAL-XLIFF-CORE-EXTENSION-NAMESPACE-001",)),
        (("\"kind\":\"any\"",), ("SAL-XLIFF-CORE-HIERARCHY-EXTENSION-POINTS-001",)),
        (("extension",), ("SAL-XLIFF-CORE-EXTENSION-PRESERVE-001",)),
        (("originaldata",), ("SAL-XLIFF-CORE-HIERARCHY-ORIGINAL-DATA-001",)),
        (("ignorable",), ("SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001",)),
        (("segment",), ("SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001",)),
        (("unit",), ("SAL-XLIFF-CORE-HIERARCHY-UNIT-CHILDREN-001",)),
        (("group",), ("SAL-XLIFF-CORE-HIERARCHY-GROUP-CHILDREN-001",)),
        (("file",), ("SAL-XLIFF-CORE-HIERARCHY-FILE-CHILDREN-001",)),
        (("target",), ("SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001",)),
        (("source",), ("SAL-XLIFF-CORE-SOURCE-REQUIRED-001",)),
        (("notes",), ("SAL-XLIFF-CORE-HIERARCHY-NOTES-001",)),
        (("inline",), ("SAL-XLIFF-CORE-AGENT-INLINE-001",)),
        (("pc",), ("SAL-XLIFF-CORE-INLINE-PC-001",)),
        (("ph",), ("SAL-XLIFF-CORE-INLINE-PH-001",)),
        (("sc",), ("SAL-XLIFF-CORE-INLINE-SC-001",)),
        (("ec",), ("SAL-XLIFF-CORE-INLINE-EC-001",)),
        (("mrk",), ("SAL-XLIFF-CORE-INLINE-MRK-001",)),
        (("sm",), ("SAL-XLIFF-CORE-INLINE-SM-001",)),
        (("em",), ("SAL-XLIFF-CORE-INLINE-EM-001",)),
        (("order",), ("SAL-XLIFF-CORE-HIERARCHY-ORDER-001",)),
    )
    for needles, ids in keyword_rules:
        if any(
            (
                bool(
                    re.search(
                        rf"(?<![a-z0-9]){re.escape(needle)}(?![a-z0-9])",
                        text,
                    )
                )
                if re.fullmatch(r"[a-z0-9]+", needle)
                else needle in text
            )
            for needle in needles
        ):
            obligation_ids.update(ids)
            mapping_rule_ids.add(
                "SEMANTIC_TOKEN:"
                + ",".join(
                    obligation_id.removeprefix("SAL-XLIFF-CORE-")
                    for obligation_id in ids
                )
            )

    candidate_class = str(candidate["candidate_class"])
    if source_kind == "CORE_SCHEMATRON":
        obligation_ids.add("SAL-XLIFF-CORE-AGENT-VALIDATOR-001")
        mapping_rule_ids.add(f"SEMANTIC_CLASS:{candidate_class}")
    elif source_kind == "CORE_XSD":
        obligation_ids.add("SAL-XLIFF-CORE-ROUNDTRIP-STRUCTURE-001")
        mapping_rule_ids.add(f"SEMANTIC_CLASS:{candidate_class}")
        if any(token in text for token in ("sequence", "choice", "all")):
            obligation_ids.add("SAL-XLIFF-CORE-WRITE-SCHEMA-ORDER-001")
            mapping_rule_ids.add("SEMANTIC_CLASS:XSD_COMPOSITOR_ORDER")
    elif source_kind == "NORMATIVE_PROSE":
        if "preserv" in text or "foreign" in text or "custom" in text:
            obligation_ids.add("SAL-XLIFF-CORE-EXTENSION-UNKNOWN-PRESERVE-001")
            mapping_rule_ids.add("SEMANTIC_CONTEXT:PROSE_PRESERVATION")
        if not obligation_ids:
            obligation_ids.add("SAL-XLIFF-CORE-AGENT-MODIFIER-001")
            mapping_rule_ids.add(f"SEMANTIC_CLASS:{candidate_class}")
    elif source_kind == "NON_MODAL_PROSE":
        if not obligation_ids:
            return {
                "kind": "NON_OBLIGATION",
                "reason_code": "INFORMATIVE_NON_MODAL_PROSE",
                "mapping_rule_ids": [f"SEMANTIC_CLASS:{candidate_class}"],
                "mapping_precision": "REASONED_NON_OBLIGATION_UNVERIFIED",
                "rationale": (
                    "The paragraph contains no normative modal and no "
                    "recognized constraint semantic. It remains source-located "
                    "and content-bound so a later authority review can "
                    "reclassify it without losing denominator accountability."
                ),
                "validation_status": (
                    "SOURCE_LOCATED_RULE_DISPOSITION_UNVERIFIED"
                ),
            }
        mapping_rule_ids.add(f"SEMANTIC_CLASS:{candidate_class}")
    else:
        raise ExtractionError(
            f"candidate {candidate['candidate_id']} has unsupported source kind"
        )

    unknown = sorted(obligation_ids - expected_ids)
    if unknown:
        raise ExtractionError(
            f"candidate disposition references unknown obligation IDs: {unknown}"
        )
    if not obligation_ids:
        raise ExtractionError(
            f"candidate {candidate['candidate_id']} has no disposition"
        )
    return {
        "kind": "MAP_EXPECTED_OBLIGATION",
        "obligation_ids": sorted(obligation_ids),
        "mapping_rule_ids": sorted(mapping_rule_ids),
        "mapping_precision": (
            "SEMANTIC_TOKEN_AND_STRUCTURAL_CLASS_MAPPING_UNVERIFIED"
            if any(
                rule.startswith(("SEMANTIC_TOKEN:", "SEMANTIC_CONTEXT:"))
                for rule in mapping_rule_ids
            )
            and any(
                rule.startswith("SEMANTIC_CLASS:")
                for rule in mapping_rule_ids
            )
            else (
                "SEMANTIC_TOKEN_MAPPING_UNVERIFIED"
                if any(
                    rule.startswith(("SEMANTIC_TOKEN:", "SEMANTIC_CONTEXT:"))
                    for rule in mapping_rule_ids
                )
                else "STRUCTURAL_CLASS_MAPPING_UNVERIFIED"
            )
        ),
        "rationale": (
            "Deterministic semantic routing binds this authority candidate to "
            "the named expected behavior surfaces. The mapping remains "
            "source-located and requires canonical SAL verification."
        ),
        "validation_status": "SOURCE_LOCATED_RULE_DISPOSITION_UNVERIFIED",
    }


def validate_xliff_core_authority_census(
    census: Mapping[str, Any],
    *,
    expected_obligation_inventory: Mapping[str, Any],
    profile_sources: Sequence[ProfileSource] | None = None,
    policy_sources: Sequence[PolicySource] = (),
) -> None:
    """Fail closed when a Core authority census is malformed or ambiguous.

    Structural validation proves internal consistency.  Supplying
    ``profile_sources`` additionally replays extraction from the pinned
    authority bytes, which is required before the artifact can be treated as
    source-authentic rather than merely self-consistent.
    """

    if census.get("schema") != "ff6/xliff-core-authority-census@2":
        raise ExtractionError("invalid XLIFF Core authority census schema")
    expected_rows, denominator_complete, _status = _validate_core_denominator(
        expected_obligation_inventory
    )
    if (
        census.get("authority_inputs")
        != expected_obligation_inventory.get("authority_inputs")
    ):
        raise ExtractionError(
            "Core census authority input projection contradicts denominator"
        )
    expected_ids = set(expected_rows)
    raw_candidates = census.get("candidates")
    if not isinstance(raw_candidates, Sequence) or isinstance(
        raw_candidates, (str, bytes)
    ):
        raise ExtractionError("Core census candidates must be a sequence")
    seen_candidate_ids: set[str] = set()
    mapped_ids: set[str] = set()
    kind_counts: dict[str, int] = {}
    relation_counts: dict[str, int] = {}
    for raw_candidate in raw_candidates:
        if not isinstance(raw_candidate, Mapping):
            raise ExtractionError("Core census candidate must be a mapping")
        candidate_id = str(raw_candidate.get("candidate_id", ""))
        source_kind = str(raw_candidate.get("source_kind", ""))
        semantic_location = str(raw_candidate.get("semantic_location", ""))
        if source_kind not in {
            "NORMATIVE_PROSE",
            "NON_MODAL_PROSE",
            "CORE_XSD",
            "CORE_SCHEMATRON",
        }:
            raise ExtractionError(
                f"{candidate_id or '<unknown>'} has invalid source kind"
            )
        expected_candidate_id = (
            "XLF-CAND-"
            + source_kind.replace("_", "-")
            + "-"
            + _sha256(
                json.dumps(
                    [source_kind, semantic_location],
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            )[:16].upper()
        )
        if candidate_id != expected_candidate_id:
            raise ExtractionError("Core census candidate ID is not deterministic")
        if candidate_id in seen_candidate_ids:
            raise ExtractionError(f"duplicate candidate ID: {candidate_id}")
        seen_candidate_ids.add(candidate_id)
        raw_occurrences = raw_candidate.get("occurrences")
        if not isinstance(raw_occurrences, Sequence) or isinstance(
            raw_occurrences, (str, bytes)
        ) or not raw_occurrences:
            raise ExtractionError(f"{candidate_id} has invalid occurrences")
        occurrence_profiles = [
            str(occurrence.get("profile", ""))
            for occurrence in raw_occurrences
            if isinstance(occurrence, Mapping)
        ]
        if len(occurrence_profiles) != len(raw_occurrences):
            raise ExtractionError(f"{candidate_id} occurrence must be a mapping")
        if (
            len(occurrence_profiles) != len(set(occurrence_profiles))
            or not set(occurrence_profiles)
            <= {"xliff_2.0", "xliff_2.1"}
        ):
            raise ExtractionError(f"{candidate_id} has invalid candidate profile")
        stable_profiles = raw_candidate.get("stable_profiles")
        if (
            not isinstance(stable_profiles, Sequence)
            or isinstance(stable_profiles, (str, bytes))
            or list(stable_profiles) != sorted(occurrence_profiles)
        ):
            raise ExtractionError(f"{candidate_id} has invalid candidate profile")
        relation = str(raw_candidate.get("profile_relation", ""))
        candidate_class = str(raw_candidate.get("candidate_class", ""))
        if candidate_class not in _CORE_CANDIDATE_CLASSES:
            raise ExtractionError(f"{candidate_id} has invalid candidate class")
        authority_inputs = census.get("authority_inputs")
        authority_member_inputs = census.get("authority_member_inputs")
        try:
            for occurrence in raw_occurrences:
                assert isinstance(occurrence, Mapping)
                validate_occurrence_authority(
                    occurrence,
                    authority_inputs=authority_inputs,
                    authority_member_inputs=authority_member_inputs,
                )
            expected_content_digest = candidate_content_sha256(raw_candidate)
        except (AssertionError, CandidateBindingError) as exc:
            raise ExtractionError(
                f"{candidate_id} candidate binding or digest validation failed: {exc}"
            ) from exc
        if raw_candidate.get("candidate_content_sha256") != expected_content_digest:
            raise ExtractionError(
                f"{candidate_id} candidate content digest mismatch"
            )
        if relation != _candidate_relation(
            [
                {
                    "profile": str(occurrence["profile"]),
                    "requirement_sha256": str(
                        occurrence["requirement_sha256"]
                    ),
                }
                for occurrence in raw_occurrences
            ]
        ):
            raise ExtractionError(f"{candidate_id} has invalid profile relation")
        if "disposition" not in raw_candidate:
            raise ExtractionError(f"{candidate_id} is missing disposition")
        disposition = raw_candidate["disposition"]
        if not isinstance(disposition, Mapping):
            raise ExtractionError(f"{candidate_id} disposition must be a mapping")
        kind = str(disposition.get("kind", ""))
        rationale = str(disposition.get("rationale", "")).strip()
        if not rationale:
            raise ExtractionError(f"{candidate_id} disposition lacks rationale")
        if kind == "MAP_EXPECTED_OBLIGATION":
            raw_ids = disposition.get("obligation_ids")
            if not isinstance(raw_ids, Sequence) or isinstance(
                raw_ids, (str, bytes)
            ) or not raw_ids:
                raise ExtractionError(
                    f"{candidate_id} has invalid obligation mapping"
                )
            obligation_ids = list(map(str, raw_ids))
            if len(obligation_ids) != len(set(obligation_ids)):
                raise ExtractionError(
                    f"{candidate_id} has duplicate obligation mapping"
                )
            unknown = sorted(set(obligation_ids) - expected_ids)
            if unknown:
                raise ExtractionError(
                    f"{candidate_id} maps unknown obligations: {unknown}"
                )
            raw_rule_ids = disposition.get("mapping_rule_ids")
            if not isinstance(raw_rule_ids, Sequence) or isinstance(
                raw_rule_ids, (str, bytes)
            ) or not raw_rule_ids:
                raise ExtractionError(
                    f"{candidate_id} lacks mapping rule identities"
                )
            precision = str(disposition.get("mapping_precision", ""))
            if precision not in {
                "SEMANTIC_TOKEN_MAPPING_UNVERIFIED",
                "STRUCTURAL_CLASS_MAPPING_UNVERIFIED",
                "SEMANTIC_TOKEN_AND_STRUCTURAL_CLASS_MAPPING_UNVERIFIED",
            }:
                raise ExtractionError(
                    f"{candidate_id} has invalid mapping precision"
                )
            mapped_ids.update(obligation_ids)
        elif kind == "NON_OBLIGATION":
            if not str(disposition.get("reason_code", "")).strip():
                raise ExtractionError(
                    f"{candidate_id} non-obligation lacks reason code"
                )
            if (
                disposition.get("mapping_precision")
                != "REASONED_NON_OBLIGATION_UNVERIFIED"
            ):
                raise ExtractionError(
                    f"{candidate_id} has invalid non-obligation precision"
                )
        else:
            raise ExtractionError(f"{candidate_id} has invalid disposition kind")
        expected_disposition = _candidate_disposition(
            raw_candidate,
            expected_ids,
        )
        if dict(disposition) != expected_disposition:
            raise ExtractionError(
                f"{candidate_id} contradicts its deterministic disposition"
            )
        kind_counts[source_kind] = kind_counts.get(source_kind, 0) + 1
        relation_counts[relation] = relation_counts.get(relation, 0) + 1

    if census.get("candidate_count") != len(raw_candidates):
        raise ExtractionError("Core census candidate_count drift")
    expected_member_inputs = [
        {
            "profile": profile,
            "source_id": source_id,
            "source_sha256": source_sha256,
            "member": member,
            "member_sha256": member_sha256,
        }
        for (
            profile,
            source_id,
            source_sha256,
            member,
            member_sha256,
        ) in sorted(
            {
                (
                    str(occurrence["profile"]),
                    str(occurrence["source_id"]),
                    str(occurrence["source_sha256"]),
                    str(occurrence["member"]),
                    str(occurrence["member_sha256"]),
                )
                for candidate in raw_candidates
                if isinstance(candidate, Mapping)
                for occurrence in candidate.get("occurrences", [])
                if isinstance(occurrence, Mapping)
            }
        )
    ]
    if census.get("authority_member_inputs") != expected_member_inputs:
        raise ExtractionError("Core census authority member projection drift")
    occurrence_counts = {
        profile: {
            source_kind: sum(
                1
                for candidate in raw_candidates
                if isinstance(candidate, Mapping)
                and candidate.get("source_kind") == source_kind
                for occurrence in candidate.get("occurrences", [])
                if isinstance(occurrence, Mapping)
                and occurrence.get("profile") == profile
            )
            for source_kind in (
                "NORMATIVE_PROSE",
                "NON_MODAL_PROSE",
                "CORE_XSD",
                "CORE_SCHEMATRON",
            )
        }
        for profile in ("xliff_2.0", "xliff_2.1")
    }
    if census.get("source_surface_occurrence_counts") != occurrence_counts:
        raise ExtractionError("Core census source occurrence counts drift")
    precision_values = sorted(
        {
            str(candidate["disposition"]["mapping_precision"])
            for candidate in raw_candidates
            if isinstance(candidate, Mapping)
            and isinstance(candidate.get("disposition"), Mapping)
        }
    )
    precision_counts = {
        precision: sum(
            isinstance(candidate, Mapping)
            and isinstance(candidate.get("disposition"), Mapping)
            and candidate["disposition"].get("mapping_precision") == precision
            for candidate in raw_candidates
        )
        for precision in precision_values
    }
    if census.get("disposition_precision_counts") != precision_counts:
        raise ExtractionError("Core census disposition precision counts drift")
    declared_kind_counts = census.get("candidate_count_by_source_kind")
    if declared_kind_counts != {
        kind: kind_counts.get(kind, 0)
        for kind in (
            "NORMATIVE_PROSE",
            "NON_MODAL_PROSE",
            "CORE_XSD",
            "CORE_SCHEMATRON",
        )
    }:
        raise ExtractionError("Core census source-kind counts drift")
    if census.get("candidate_scope_complete") is not True:
        raise ExtractionError("Core census authority scope is incomplete")
    if census.get("non_modal_prose_census_complete") is not True:
        raise ExtractionError("Core census non-modal prose enumeration is incomplete")
    if census.get("non_modal_prose_disposition_complete") is not True:
        raise ExtractionError("Core census non-modal prose disposition is incomplete")
    if census.get("non_modal_prose_classification_verified") is not False:
        raise ExtractionError(
            "Core census cannot claim verified non-modal prose classification"
        )
    unverified_disposition_count = sum(
        isinstance(candidate, Mapping)
        and isinstance(candidate.get("disposition"), Mapping)
        and candidate["disposition"].get("validation_status")
        == "SOURCE_LOCATED_RULE_DISPOSITION_UNVERIFIED"
        for candidate in raw_candidates
    )
    if census.get("unverified_disposition_count") != unverified_disposition_count:
        raise ExtractionError("Core census unverified disposition count drift")
    if (
        census.get("disposition_verification_complete")
        is not (unverified_disposition_count == 0)
    ):
        raise ExtractionError(
            "Core census disposition verification projection is contradictory"
        )
    declared_relation_counts = census.get("candidate_count_by_profile_relation")
    if declared_relation_counts != {
        relation: relation_counts.get(relation, 0)
        for relation in (
            "COMMON_IDENTICAL",
            "COMMON_CHANGED",
            "REMOVED_IN_XLIFF_2_1",
            "ADDED_IN_XLIFF_2_1",
        )
    }:
        raise ExtractionError("Core census profile-relation counts drift")
    if census.get("unmapped_candidate_count") != 0:
        raise ExtractionError("Core census declares unmapped candidates")
    if census.get("multiply_dispositioned_candidate_count") != 0:
        raise ExtractionError("Core census declares multiply dispositioned candidates")
    if census.get("mapped_expected_obligation_ids") != sorted(mapped_ids):
        raise ExtractionError("Core census mapped obligation projection drift")
    unresolved = sorted(expected_ids - mapped_ids)
    if census.get("unresolved_expected_obligation_ids") != unresolved:
        raise ExtractionError("Core census unresolved obligation projection drift")
    expected_complete = denominator_complete and not unresolved
    if (
        census.get("normative_obligation_inventory_complete")
        is not expected_complete
    ):
        raise ExtractionError("Core census completeness contradicts denominator")
    if profile_sources is not None:
        replayed = compile_xliff_core_authority_census(
            profile_sources,
            expected_obligation_inventory=expected_obligation_inventory,
            policy_sources=policy_sources,
        )
        observed = dict(census)
        observed.pop("denominator_input_sha256", None)
        if observed != replayed:
            raise ExtractionError(
                "Core census authority replay does not reproduce the artifact"
            )


def compile_xliff_core_authority_census(
    profile_sources: Sequence[ProfileSource],
    *,
    expected_obligation_inventory: Mapping[str, Any],
    policy_sources: Sequence[PolicySource] = (),
) -> dict[str, Any]:
    """Compile source candidates that must be dispositioned for XLIFF Core."""

    sources = {source.profile: source for source in profile_sources}
    if (
        set(sources) != {"xliff_2.0", "xliff_2.1"}
        or len(sources) != len(profile_sources)
    ):
        raise ExtractionError(
            "XLIFF Core census requires one authority for each stable profile"
        )
    expected_rows, denominator_complete, denominator_status = (
        _validate_core_denominator(expected_obligation_inventory)
    )
    current_denominator = compile_xliff_core_denominator(
        profile_sources,
        policy_sources=policy_sources,
    )
    if (
        expected_obligation_inventory.get("authority_inputs")
        != current_denominator["authority_inputs"]
    ):
        raise ExtractionError(
            "XLIFF Core census authority input closure does not match the "
            "current compiler inputs"
        )
    archives = {
        profile: _read_authority_archive(source)
        for profile, source in sorted(sources.items())
    }
    grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
    extractors = (
        ("NORMATIVE_PROSE", _core_prose_candidate_occurrences),
        ("NON_MODAL_PROSE", _core_non_modal_prose_candidate_occurrences),
        ("CORE_XSD", _core_xsd_candidate_occurrences),
        ("CORE_SCHEMATRON", _core_schematron_candidate_occurrences),
    )
    for profile, source in sorted(sources.items()):
        for source_kind, extractor in extractors:
            for occurrence in extractor(source, archives[profile]):
                key = (source_kind, occurrence["location"])
                grouped.setdefault(key, []).append(occurrence)

    candidates: list[dict[str, Any]] = []
    expected_ids = set(expected_rows)
    for (source_kind, semantic_location), occurrences in sorted(grouped.items()):
        profiles = [row["profile"] for row in occurrences]
        if len(profiles) != len(set(profiles)):
            raise ExtractionError(
                f"duplicate candidate occurrence at {semantic_location}"
            )
        identity = json.dumps(
            [source_kind, semantic_location],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        candidate_id = (
            "XLF-CAND-"
            + source_kind.replace("_", "-")
            + "-"
            + _sha256(identity.encode("utf-8"))[:16].upper()
        )
        candidate: dict[str, Any] = {
            "candidate_id": candidate_id,
            "source_kind": source_kind,
            "candidate_class": occurrences[0]["candidate_class"],
            "semantic_location": semantic_location,
            "profile_relation": _candidate_relation(occurrences),
            "stable_profiles": sorted(profiles),
            "occurrences": sorted(
                occurrences, key=lambda row: (row["profile"], row["source_id"])
            ),
        }
        if any(
            occurrence["candidate_class"] != candidate["candidate_class"]
            for occurrence in occurrences
        ):
            raise ExtractionError(
                f"candidate class differs across profiles at {semantic_location}"
            )
        try:
            candidate["candidate_content_sha256"] = candidate_content_sha256(
                candidate
            )
        except CandidateBindingError as exc:
            raise ExtractionError(
                f"candidate content binding failed at {semantic_location}: {exc}"
            ) from exc
        candidate["disposition"] = _candidate_disposition(
            candidate, expected_ids
        )
        candidates.append(candidate)

    candidate_ids = [str(row["candidate_id"]) for row in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ExtractionError("duplicate XLIFF Core census candidate ID")
    mapped_ids = sorted(
        {
            str(obligation_id)
            for candidate in candidates
            for obligation_id in candidate["disposition"].get(
                "obligation_ids", []
            )
        }
    )
    unresolved_ids = sorted(expected_ids - set(mapped_ids))
    kind_counts = {
        source_kind: sum(
            row["source_kind"] == source_kind for row in candidates
        )
        for source_kind, _extractor in extractors
    }
    relation_counts = {
        relation: sum(
            row["profile_relation"] == relation for row in candidates
        )
        for relation in (
            "COMMON_IDENTICAL",
            "COMMON_CHANGED",
            "REMOVED_IN_XLIFF_2_1",
            "ADDED_IN_XLIFF_2_1",
        )
    }
    precision_counts = {
        precision: sum(
            row["disposition"]["mapping_precision"] == precision
            for row in candidates
        )
        for precision in sorted(
            {
                str(row["disposition"]["mapping_precision"])
                for row in candidates
            }
        )
    }
    occurrence_counts = {
        profile: {
            source_kind: sum(
                1
                for candidate in candidates
                if candidate["source_kind"] == source_kind
                for occurrence in candidate["occurrences"]
                if occurrence["profile"] == profile
            )
            for source_kind, _extractor in extractors
        }
        for profile in ("xliff_2.0", "xliff_2.1")
    }
    authority_member_inputs = sorted(
        {
            (
                occurrence["profile"],
                occurrence["source_id"],
                occurrence["source_sha256"],
                occurrence["member"],
                occurrence["member_sha256"],
            )
            for candidate in candidates
            for occurrence in candidate["occurrences"]
        }
    )
    artifact = {
        "schema": "ff6/xliff-core-authority-census@2",
        "artifact_id": "FF6-XLIFF-CORE-AUTHORITY-CANDIDATE-CENSUS",
        "artifact_type": "authority_candidate_census",
        "visibility": "generated",
        "publish_allowed": False,
        "generated_by": "codex",
        "format_id": "xliff",
        "stable_profiles": ["xliff_2.0", "xliff_2.1"],
        "status": "CANDIDATE_SCOPE_RECONCILED_OBLIGATION_INVENTORY_OPEN",
        "candidate_scope_complete": True,
        "non_modal_prose_census_complete": True,
        "non_modal_prose_disposition_complete": True,
        "non_modal_prose_classification_verified": False,
        "disposition_verification_complete": False,
        "candidate_scope_definition": {
            "prose_selector": (
                "Every para with an RFC-style normative modal plus every "
                "modal listitem that has no modal para/listitem descendant, "
                "within the unique DocBook section id=core."
            ),
            "non_modal_prose_selector": (
                "Every non-empty Core para without an RFC-style normative "
                "modal plus every non-modal leaf listitem with no para or "
                "listitem descendant."
            ),
            "xsd_node_kinds": sorted(_XSD_CANDIDATE_KINDS),
            "schematron_node_kinds": ["assert", "report"],
            "ancestor_descendant_rule": (
                "A modal descendant para/listitem owns its prose candidate; "
                "the aggregate ancestor listitem is excluded."
            ),
            "profile_delta_rule": (
                "Equal source-kind and structural-location candidates are "
                "COMMON_IDENTICAL or COMMON_CHANGED by normalized digest; "
                "single-profile candidates are added or removed."
            ),
        },
        "candidate_scope_limitations": [
            (
                "Content-bound semantic dispositions are source-located but "
                "remain unverified until canonical SAL reconciliation."
            ),
            (
                "Production-policy obligations are denominator inputs, not "
                "OASIS authority candidates in this census."
            ),
        ],
        "normative_obligation_inventory_complete": (
            denominator_complete and not unresolved_ids
        ),
        "denominator_status": denominator_status,
        "authority_inputs": current_denominator["authority_inputs"],
        "authority_member_inputs": [
            {
                "profile": profile,
                "source_id": source_id,
                "source_sha256": source_sha256,
                "member": member,
                "member_sha256": member_sha256,
            }
            for (
                profile,
                source_id,
                source_sha256,
                member,
                member_sha256,
            ) in authority_member_inputs
        ],
        "candidate_count": len(candidates),
        "candidate_count_by_source_kind": kind_counts,
        "candidate_count_by_profile_relation": relation_counts,
        "disposition_precision_counts": precision_counts,
        "unverified_disposition_count": len(candidates),
        "source_surface_occurrence_counts": occurrence_counts,
        "unmapped_candidate_count": 0,
        "multiply_dispositioned_candidate_count": 0,
        "mapped_expected_obligation_ids": mapped_ids,
        "unresolved_expected_obligation_ids": unresolved_ids,
        "candidates": candidates,
        "truth_boundary": (
            "Modal and non-modal Core prose, Core XSD components and "
            "constraints, and Core Schematron assertions are deterministically "
            "enumerated, content-bound, and dispositioned without anonymous "
            "fallback labels. Structural-class and semantic-token mappings "
            "remain "
            "SOURCE_LOCATED_RULE_DISPOSITION_UNVERIFIED; this artifact does "
            "not prove the expected-ID denominator exhaustive, resolve "
            "canonical SAL verification, or close XLF-04."
        ),
    }
    validate_xliff_core_authority_census(
        artifact,
        expected_obligation_inventory=expected_obligation_inventory,
    )
    return artifact


def compile_xliff_core_denominator(
    profile_sources: Sequence[ProfileSource],
    *,
    policy_sources: Sequence[PolicySource],
) -> dict[str, Any]:
    """Compile the explicit but not-yet-exhaustive Core obligation denominator."""

    sources = {source.profile: source for source in profile_sources}
    if (
        set(sources) != {"xliff_2.0", "xliff_2.1"}
        or len(sources) != len(profile_sources)
    ):
        raise ExtractionError(
            "XLIFF Core denominator requires one authority for each stable profile"
        )
    authority_inputs: list[dict[str, str]] = []
    for profile, profile_source in sorted(sources.items()):
        _read_authority_archive(profile_source)
        authority_inputs.append(
            {
                "authority_class": "XLIFF_STANDARD_PACKAGE",
                "profile": profile,
                "source_id": profile_source.source_id,
                "source_sha256": profile_source.expected_sha256,
            }
        )
    seen_policy_ids: set[str] = set()
    for policy_source in sorted(
        policy_sources, key=lambda item: item.source_id
    ):
        if policy_source.source_id in seen_policy_ids:
            raise ExtractionError(
                f"duplicate Core policy source_id: {policy_source.source_id}"
            )
        seen_policy_ids.add(policy_source.source_id)
        digest, _rules = _policy_rule_index(policy_source)
        authority_inputs.append(
            {
                "authority_class": "PRODUCTION_POLICY",
                "source_id": policy_source.source_id,
                "source_sha256": digest,
            }
        )
    expectations = _default_core_obligation_expectations()
    expected_ids = [str(row["obligation_id"]) for row in expectations]
    if len(expected_ids) != len(set(expected_ids)):
        raise ExtractionError("duplicate default Core expectation ID")
    return {
        "schema": "ff6/xliff-core-obligation-denominator@1",
        "artifact_id": "FF6-XLIFF-CORE-OBLIGATION-DENOMINATOR",
        "artifact_type": "expected_obligation_denominator",
        "visibility": "generated",
        "publish_allowed": False,
        "generated_by": "codex",
        "format_id": "xliff",
        "status": "OPEN_AUTHORITY_CENSUS",
        "inventory_complete": False,
        "stable_profiles": ["xliff_2.0", "xliff_2.1"],
        "expected_obligation_count": len(expectations),
        "covered_categories": sorted(_XLIFF_CORE_CATEGORIES),
        "authority_inputs": authority_inputs,
        "open_census_reasons": [
            (
                "Every normative Core prose statement has not yet been "
                "dispositioned to an obligation or explicit non-obligation."
            ),
            (
                "Every Core XSD cardinality, ordering, type, attribute, and "
                "Schematron constraint has not yet been mapped exactly once."
            ),
            (
                "XLIFF 2.1 additions and changed processing requirements have "
                "not yet been proven complete against the 2.0 delta."
            ),
        ],
        "expectations": expectations,
        "truth_boundary": (
            "This independent expected-ID inventory creates durable missing-work "
            "edges, but remains OPEN_AUTHORITY_CENSUS. It cannot certify XLF-04 "
            "until every normative prose, XSD, Schematron, and production-policy "
            "candidate has an exact disposition and inventory_complete is true."
        ),
    }


def _validate_core_denominator(
    inventory: Mapping[str, Any],
) -> tuple[dict[str, Mapping[str, Any]], bool, str]:
    if inventory.get("schema") != "ff6/xliff-core-obligation-denominator@1":
        raise ExtractionError("invalid XLIFF Core denominator schema")
    status = str(inventory.get("status", ""))
    inventory_complete = inventory.get("inventory_complete")
    if status not in {"OPEN_AUTHORITY_CENSUS", "COMPLETE_AUTHORITY_CENSUS"}:
        raise ExtractionError("invalid XLIFF Core denominator status")
    if not isinstance(inventory_complete, bool):
        raise ExtractionError("Core denominator inventory_complete must be boolean")
    if (status == "COMPLETE_AUTHORITY_CENSUS") != inventory_complete:
        raise ExtractionError(
            "Core denominator status contradicts inventory_complete"
        )
    raw_rows = inventory.get("expectations")
    if not isinstance(raw_rows, Sequence) or isinstance(raw_rows, (str, bytes)):
        raise ExtractionError("Core denominator expectations must be a sequence")
    expected: dict[str, Mapping[str, Any]] = {}
    for raw in raw_rows:
        if not isinstance(raw, Mapping):
            raise ExtractionError("Core denominator expectation must be a mapping")
        if set(raw) != {
            "obligation_id",
            "category",
            "stable_profiles",
            "obligation_basis",
        }:
            raise ExtractionError("invalid Core denominator expectation fields")
        obligation_id = str(raw["obligation_id"])
        if not _CORE_OBLIGATION_ID.fullmatch(obligation_id):
            raise ExtractionError(
                f"invalid Core denominator obligation_id: {obligation_id}"
            )
        if obligation_id in expected:
            raise ExtractionError(
                f"duplicate Core denominator obligation_id: {obligation_id}"
            )
        category = str(raw["category"])
        if category not in _XLIFF_CORE_CATEGORIES:
            raise ExtractionError(
                f"{obligation_id} has unknown denominator category"
            )
        profiles = list(map(str, raw["stable_profiles"]))
        if (
            not profiles
            or len(profiles) != len(set(profiles))
            or not set(profiles) <= {"xliff_2.0", "xliff_2.1"}
        ):
            raise ExtractionError(
                f"{obligation_id} has invalid denominator stable_profiles"
            )
        basis = str(raw["obligation_basis"])
        if basis not in _CORE_OBLIGATION_BASES:
            raise ExtractionError(
                f"{obligation_id} has invalid denominator obligation_basis"
            )
        expected[obligation_id] = raw
    if not expected:
        raise ExtractionError("Core denominator cannot be empty")
    declared_count = inventory.get("expected_obligation_count")
    if declared_count != len(expected):
        raise ExtractionError("Core denominator expected_obligation_count drift")
    return expected, inventory_complete, status


def compile_xliff_core_obligations(
    profile_sources: Sequence[ProfileSource],
    *,
    obligation_seeds: Iterable[Mapping[str, Any]],
    batch_id: str,
    expected_obligation_ids: Iterable[str] | None = None,
    policy_sources: Sequence[PolicySource] = (),
    expected_obligation_inventory: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile a source-bound, explicitly partial XLIFF Core obligation batch."""

    sources = {source.profile: source for source in profile_sources}
    if (
        set(sources) != {"xliff_2.0", "xliff_2.1"}
        or len(sources) != len(profile_sources)
    ):
        raise ExtractionError(
            "XLIFF Core obligations require one authority for each stable profile"
        )
    if not re.fullmatch(r"XLF-04-BATCH-[0-9]{3}", batch_id):
        raise ExtractionError(f"invalid XLF-04 batch_id: {batch_id}")
    archives = {
        profile: _read_authority_archive(source)
        for profile, source in sorted(sources.items())
    }
    for profile, source in sources.items():
        if source.prose_member not in archives[profile]:
            raise ExtractionError(
                f"{source.source_id} lacks {source.prose_member}"
            )
    rows = _core_obligation_rows(
        obligation_seeds,
        sources,
        archives,
        batch_id=batch_id,
        policy_sources=policy_sources,
    )
    covered_categories = sorted({str(row["category"]) for row in rows})
    uncovered_categories = sorted(
        _XLIFF_CORE_CATEGORIES - set(covered_categories)
    )
    actual_ids = {str(row["obligation_id"]) for row in rows}
    denominator_status: str | None = None
    denominator_complete: bool | None = None
    missing_expected_by_category: dict[str, list[str]] = {}
    expected_ids: set[str] = set()
    missing_expected_ids: list[str] = []
    if (
        expected_obligation_ids is not None
        and expected_obligation_inventory is not None
    ):
        raise ExtractionError(
            "provide either expected_obligation_ids or "
            "expected_obligation_inventory, not both"
        )
    if expected_obligation_inventory is not None:
        expected_rows, denominator_complete, denominator_status = (
            _validate_core_denominator(expected_obligation_inventory)
        )
        current_denominator = compile_xliff_core_denominator(
            profile_sources,
            policy_sources=policy_sources,
        )
        if (
            expected_obligation_inventory.get("authority_inputs")
            != current_denominator["authority_inputs"]
        ):
            raise ExtractionError(
                "XLIFF Core denominator authority input closure does not "
                "match the current compiler inputs"
            )
        expected_ids = set(expected_rows)
        unexpected_ids = sorted(actual_ids - expected_ids)
        if unexpected_ids:
            raise ExtractionError(
                f"Core obligations outside expected denominator: {unexpected_ids}"
            )
        for row in rows:
            obligation_id = str(row["obligation_id"])
            expected = expected_rows[obligation_id]
            for field in ("category", "stable_profiles", "obligation_basis"):
                if row[field] != expected[field]:
                    raise ExtractionError(
                        f"{obligation_id} contradicts denominator {field}"
                    )
        missing_expected_ids = sorted(expected_ids - actual_ids)
        for obligation_id in missing_expected_ids:
            category = str(expected_rows[obligation_id]["category"])
            missing_expected_by_category.setdefault(category, []).append(
                obligation_id
            )
        remaining_categories = sorted(missing_expected_by_category)
        completeness_basis = (
            "EXPLICIT_EXPECTED_OBLIGATION_IDS"
            if denominator_complete
            else "EXPLICIT_EXPECTED_OBLIGATION_IDS_OPEN_CENSUS"
        )
        complete = (
            denominator_complete
            and not uncovered_categories
            and not missing_expected_ids
        )
    elif expected_obligation_ids is None:
        completeness_basis = "EXPECTED_OBLIGATION_DENOMINATOR_ABSENT"
        remaining_categories = uncovered_categories
        complete = False
    else:
        expected_values = list(map(str, expected_obligation_ids))
        expected_ids = set(expected_values)
        if (
            not expected_ids
            or len(expected_ids) != len(expected_values)
            or any(
                not _CORE_OBLIGATION_ID.fullmatch(obligation_id)
                for obligation_id in expected_ids
            )
        ):
            raise ExtractionError("invalid expected Core obligation denominator")
        unexpected_ids = sorted(actual_ids - expected_ids)
        if unexpected_ids:
            raise ExtractionError(
                f"Core obligations outside expected denominator: {unexpected_ids}"
            )
        missing_expected_ids = sorted(expected_ids - actual_ids)
        completeness_basis = "EXPLICIT_EXPECTED_OBLIGATION_IDS"
        remaining_categories = uncovered_categories
        denominator_status = "LEGACY_EXPLICIT_ID_SET"
        denominator_complete = True
        complete = not uncovered_categories and not missing_expected_ids
    return {
        "schema": "ff6/xliff-core-obligation-inventory@2",
        "artifact_id": (
            "FF6-XLIFF-CORE-OBLIGATIONS-"
            + batch_id.replace("XLF-04-BATCH-", "XLF04-BATCH")
        ),
        "artifact_type": "core_and_production_obligation_inventory",
        "visibility": "generated",
        "publish_allowed": False,
        "generated_by": "codex",
        "format_id": "xliff",
        "batch_id": batch_id,
        "status": (
            "SOURCE_LOCATED_COMPLETE"
            if complete
            else "SOURCE_LOCATED_PARTIAL"
        ),
        "stable_profiles": ["xliff_2.0", "xliff_2.1"],
        "obligation_count": len(rows),
        "covered_categories": covered_categories,
        "uncovered_categories": uncovered_categories,
        "remaining_categories": remaining_categories,
        "completeness_basis": completeness_basis,
        "expected_obligation_count": (
            len(expected_ids)
            if (
                expected_obligation_ids is not None
                or expected_obligation_inventory is not None
            )
            else None
        ),
        "resolved_expected_obligation_count": (
            len(actual_ids & expected_ids)
            if (
                expected_obligation_ids is not None
                or expected_obligation_inventory is not None
            )
            else None
        ),
        "missing_expected_obligation_ids": missing_expected_ids,
        "missing_expected_obligations_by_category": (
            {
                category: sorted(obligation_ids)
                for category, obligation_ids in sorted(
                    missing_expected_by_category.items()
                )
            }
            if expected_obligation_inventory is not None
            else {}
        ),
        "denominator_status": denominator_status,
        "denominator_complete": denominator_complete,
        "obligation_basis_counts": {
            basis: sum(
                1 for row in rows if row["obligation_basis"] == basis
            )
            for basis in sorted(_CORE_OBLIGATION_BASES)
        },
        "complete": complete,
        "obligations": rows,
        "truth_boundary": (
            "XLIFF specification obligations and production-policy duties are "
            "separate authority classes. Neither source binding nor category "
            "presence turns the 36 coarse XLF-03 anchors into complete Core "
            "semantics, product source, or certification."
        ),
    }


def _default_core_obligation_seeds(
    *,
    through_batch: str = "XLF-04-BATCH-003",
    verified_obligation_ids: set[str] | None = None,
    adjudication_evidence: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return the bounded, curated XLF-04 Core obligation batches."""

    def locations(
        section_id: str,
        source_anchor: str,
        *,
        profiles: Sequence[str] = ("xliff_2.0", "xliff_2.1"),
    ) -> list[dict[str, Any]]:
        return [
            {
                "profile": profile,
                "location_kind": "prose_paragraph",
                "member": (
                    "xliff-core-v2.0-os.xml"
                    if profile == "xliff_2.0"
                    else "xliff-core-v2.1-os.xml"
                ),
                "section_id": section_id,
                "source_anchor": source_anchor,
            }
            for profile in profiles
        ]

    common_evidence = {
        "positive": [
            "execute a conforming example against the eventual public behavior"
        ],
        "rejection": [
            "execute a discriminating non-conforming example and verify diagnostics"
        ],
    }
    note = (
        "First source-located XLF-04 batch. This identity remains stable while "
        "later batches add the uncaptured Core categories and finer rules."
    )
    seeds = [
        {
            "obligation_id": "SAL-XLIFF-CORE-DOCUMENT-ROOT-001",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:document",
            "category": "document_structure",
            "normalized_rule": (
                "Recognize the namespace-qualified xliff element as the root "
                "of every supported stable XLIFF document."
            ),
            "requirement_class": "STRUCTURAL_CONSTRAINT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "xliff", "Root element for XLIFF documents"
            ),
            "evidence_requirements": common_evidence,
            "interpretation_note": note,
        },
        {
            "obligation_id": "SAL-XLIFF-CORE-HIERARCHY-UNIT-001",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:hierarchy",
            "category": "hierarchy_cardinality",
            "normalized_rule": (
                "Require each unit to contain at least one segment and reject "
                "a unit that violates that minimum Core cardinality."
            ),
            "requirement_class": "CARDINALITY_CONSTRAINT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "unit", "must contain at least one"
            ),
            "evidence_requirements": common_evidence,
            "interpretation_note": note,
        },
        {
            "obligation_id": "SAL-XLIFF-CORE-INLINE-SPANNING-001",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:inline-code",
            "category": "inline_code_semantics",
            "normalized_rule": (
                "Represent a non-well-formed or orphan spanning inline code "
                "with source-located sc and ec boundary semantics."
            ),
            "requirement_class": "SEMANTIC_CONSTRAINT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "spanningcodeusage",
                "A spanning code must be represented using",
            ),
            "evidence_requirements": common_evidence,
            "interpretation_note": note,
        },
        {
            "obligation_id": "SAL-XLIFF-CORE-SEGMENT-SPLIT-001",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:segmentation",
            "category": "segmentation",
            "normalized_rule": (
                "Permit splitting a segment or ignorable only when its resolved "
                "canResegment value authorizes the operation."
            ),
            "requirement_class": "PROCESSING_REQUIREMENT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "segmentationModification",
                "may be split",
            ),
            "evidence_requirements": common_evidence,
            "interpretation_note": note,
        },
        {
            "obligation_id": "SAL-XLIFF-CORE-STATE-SUBSTATE-001",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:state",
            "category": "state",
            "normalized_rule": (
                "When a writer updates segment state, require it to update or "
                "remove the associated subState value consistently."
            ),
            "requirement_class": "PROCESSING_REQUIREMENT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "state", "must also update or delete subState"
            ),
            "evidence_requirements": common_evidence,
            "interpretation_note": note,
        },
        {
            "obligation_id": "SAL-XLIFF-CORE-EXTENSION-PRESERVE-001",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:extensions",
            "category": "extension_preservation",
            "normalized_rule": (
                "Preserve unsupported custom-namespace extension content "
                "without modification or false semantic-support claims."
            ),
            "requirement_class": "PRESERVATION_REQUIREMENT",
            "normative_level": "SHOULD",
            "authority_locations": locations(
                "extensions", "should preserve that extension without"
            ),
            "evidence_requirements": common_evidence,
            "interpretation_note": note,
        },
        {
            "obligation_id": "SAL-XLIFF-CORE-AGENT-INLINE-001",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:agents",
            "category": "agent_processing",
            "normalized_rule": (
                "Require processing agents to handle both paired-container and "
                "spanning inline-code representations without information loss."
            ),
            "requirement_class": "PROCESSING_REQUIREMENT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "spanningcodeusage", "Agents must be able to handle"
            ),
            "evidence_requirements": common_evidence,
            "interpretation_note": note,
        },
    ]
    for seed in seeds:
        seed["introduced_in_batch"] = "XLF-04-BATCH-001"
        seed["obligation_basis"] = "XLIFF_SPECIFICATION"

    batch_two_note = (
        "Second source-located XLF-04 batch covering stable identifier, "
        "inheritance, language, direction, whitespace, and source-target rules."
    )
    seeds.extend(
        [
            {
                "obligation_id": "SAL-XLIFF-CORE-ID-FILE-UNIQUE-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:identifiers",
                "category": "identifiers_references_inheritance",
                "normalized_rule": (
                    "Require every file id value to be unique among all file "
                    "identifiers in the enclosing XLIFF document."
                ),
                "requirement_class": "SEMANTIC_CONSTRAINT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "id",
                    "The value must be unique among all <file> id attribute "
                    "values",
                ),
                "evidence_requirements": {
                    "positive": [
                        "validate a document containing distinct file identifiers"
                    ],
                    "rejection": [
                        "reject duplicate file identifiers in one XLIFF document"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-REFERENCE-DATAREF-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:references",
                "category": "identifiers_references_inheritance",
                "normalized_rule": (
                    "Resolve every dataRef value to a data element identifier "
                    "declared in the same enclosing unit."
                ),
                "requirement_class": "SEMANTIC_CONSTRAINT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "dataref",
                    "must be the value of the id attribute of one of the "
                    "<data> element listed in the same <unit> element",
                ),
                "evidence_requirements": {
                    "positive": [
                        "resolve dataRef to a data element in the same unit"
                    ],
                    "rejection": [
                        "reject a dataRef that targets a missing or foreign-unit id"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": (
                    "SAL-XLIFF-CORE-REFERENCE-FRAGMENT-INHERIT-001"
                ),
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:references",
                "category": "identifiers_references_inheritance",
                "normalized_rule": (
                    "Resolve a relative fragment by inheriting omitted file, "
                    "group, or unit selectors from its immediate enclosure."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "fragid",
                    "Any unit, group or file selector missing to resolve the "
                    "relative reference is obtained from the immediate enclosing",
                ),
                "evidence_requirements": {
                    "positive": [
                        "resolve an omitted fragment selector from its enclosure"
                    ],
                    "rejection": [
                        "reject a relative fragment whose inherited path is invalid"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-INHERIT-TRANSLATE-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:inheritance",
                "category": "identifiers_references_inheritance",
                "normalized_rule": (
                    "When translate is absent, resolve its value from the "
                    "translate attribute of the immediate parent element."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "translate",
                    "The value of the translate attribute of its parent element",
                ),
                "evidence_requirements": {
                    "positive": [
                        "resolve an omitted translate value from the parent"
                    ],
                    "rejection": [
                        "reject behavior that ignores the inherited translate value"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-LANGUAGE-SOURCE-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:language",
                "category": "language_direction_whitespace",
                "normalized_rule": (
                    "Resolve an omitted source xml:lang value from the srcLang "
                    "attribute of the enclosing XLIFF element."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "xml_lang",
                    "The value set in the srcLang attribute",
                ),
                "evidence_requirements": {
                    "positive": [
                        "resolve source language from the enclosing srcLang"
                    ],
                    "rejection": [
                        "reject a source language resolution that contradicts srcLang"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-LANGUAGE-TARGET-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:language",
                "category": "language_direction_whitespace",
                "normalized_rule": (
                    "Resolve an omitted target xml:lang value from the trgLang "
                    "attribute of the enclosing XLIFF element."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "xml_lang",
                    "The value set in the trgLang attribute",
                ),
                "evidence_requirements": {
                    "positive": [
                        "resolve target language from the enclosing trgLang"
                    ],
                    "rejection": [
                        "reject a target language resolution that contradicts trgLang"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-DIRECTION-SOURCE-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:directionality",
                "category": "language_direction_whitespace",
                "normalized_rule": (
                    "When source direction is absent, inherit srcDir from the "
                    "immediate parent element."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "srcdir",
                    "The value of the srcDir attribute of its parent element",
                ),
                "evidence_requirements": {
                    "positive": [
                        "resolve source direction from the immediate parent"
                    ],
                    "rejection": [
                        "reject source-direction behavior that ignores inheritance"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-DIRECTION-TARGET-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:directionality",
                "category": "language_direction_whitespace",
                "normalized_rule": (
                    "When target direction is absent, inherit trgDir from the "
                    "immediate parent element."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "trgdir",
                    "The value of the trgDir attribute of its parent element",
                ),
                "evidence_requirements": {
                    "positive": [
                        "resolve target direction from the immediate parent"
                    ],
                    "rejection": [
                        "reject target-direction behavior that ignores inheritance"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-WHITESPACE-INHERIT-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:whitespace",
                "category": "language_direction_whitespace",
                "normalized_rule": (
                    "When xml:space is absent, inherit its whitespace handling "
                    "value from the immediate parent element."
                ),
                "requirement_class": "PRESERVATION_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "xml_space",
                    "The value of the xml:space attribute of its parent element",
                ),
                "evidence_requirements": {
                    "positive": [
                        "preserve whitespace according to inherited xml:space"
                    ],
                    "rejection": [
                        "reject normalization that violates inherited xml:space"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": (
                    "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001"
                ),
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:source-target",
                "category": "source_target_correspondence",
                "normalized_rule": (
                    "Require each segment to contain exactly one source and "
                    "allow at most one optional target element."
                ),
                "requirement_class": "CARDINALITY_CONSTRAINT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "segmentationRepresentation",
                    "Each <segment> element has one <source> element",
                ),
                "evidence_requirements": {
                    "positive": [
                        "parse segments with one source and zero or one target"
                    ],
                    "rejection": [
                        "reject a segment with missing source or multiple targets"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-TARGET-LANGUAGE-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:source-target",
                "category": "source_target_correspondence",
                "normalized_rule": (
                    "Require a target xml:lang value, whether explicit or "
                    "inherited, to equal the enclosing document trgLang."
                ),
                "requirement_class": "SEMANTIC_CONSTRAINT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "target",
                    "the explicit or inherited value of the optional xml:lang "
                    "must be equal to the value of the trgLang attribute",
                ),
                "evidence_requirements": {
                    "positive": [
                        "validate target language equal to the enclosing trgLang"
                    ],
                    "rejection": [
                        "reject target language different from enclosing trgLang"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-TARGET-ORDER-001",
                "introduced_in_batch": "XLF-04-BATCH-002",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:source-target",
                "category": "source_target_correspondence",
                "normalized_rule": (
                    "When target order is absent, derive its order from the "
                    "corresponding sibling source element."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": locations(
                    "order",
                    "When order is not explicitly set, the <target> order "
                    "corresponds to its sibling <source>",
                ),
                "evidence_requirements": {
                    "positive": [
                        "derive implicit target order from its sibling source"
                    ],
                    "rejection": [
                        "reject ordering behavior that loses source correspondence"
                    ],
                },
                "interpretation_note": batch_two_note,
            },
        ]
    )
    for seed in seeds:
        seed.setdefault("obligation_basis", "XLIFF_SPECIFICATION")

    batch_three_note = (
        "Third source-located XLF-04 batch. XLIFF conformance statements and "
        "Format Factory production-policy requirements retain distinct "
        "authority classes and conformance effects."
    )

    def policy_locations(*rule_ids: str) -> list[dict[str, str]]:
        return [
            {
                "location_kind": "policy_rule",
                "authority_source_id": "POLICY-SHARED-LIBRARY-CONTRACT",
                "rule_id": rule_id,
            }
            for rule_id in rule_ids
        ]

    seeds.extend(
        [
            {
                "obligation_id": "SAL-XLIFF-CORE-ROUNDTRIP-STRUCTURE-001",
                "obligation_basis": "XLIFF_SPECIFICATION",
                "introduced_in_batch": "XLF-04-BATCH-003",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:roundtrip",
                "category": "semantic_roundtrip_canonical_output",
                "normalized_rule": (
                    "Preserve the static file, group, and unit order established "
                    "by extraction throughout an XLIFF processing roundtrip."
                ),
                "requirement_class": "PRESERVATION_REQUIREMENT",
                "normative_level": "SHOULD",
                "authority_locations": locations(
                    "subflowsdesc",
                    "static structure encoded by <file>, <group>, and <unit> "
                    "elements is principally immutable",
                ),
                "evidence_requirements": {
                    "positive": [
                        "roundtrip nested file, group, and unit order semantically"
                    ],
                    "rejection": [
                        "detect or reject a write that silently changes static order"
                    ],
                },
                "interpretation_note": batch_three_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-SECURITY-URI-RISK-001",
                "obligation_basis": "XLIFF_SPECIFICATION",
                "introduced_in_batch": "XLF-04-BATCH-003",
                "stable_profiles": ["xliff_2.1"],
                "owner": "core:security",
                "category": "xml_security_resource_limits",
                "normalized_rule": (
                    "Expose the security risk of dereferencing URI and IRI "
                    "attributes, including file URI access, in the 2.1 profile."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "SHOULD",
                "authority_locations": [
                    {
                        "profile": "xliff_2.1",
                        "location_kind": "prose_paragraph",
                        "member": "xliff-core-v2.1-os.xml",
                        "section_id": "mediaType",
                        "source_anchor": (
                            "Direct external reference mechanisms: An XLIFF "
                            "document has a number of attributes"
                        ),
                    }
                ],
                "evidence_requirements": {
                    "positive": [
                        "report URI-bearing constructs without dereferencing them"
                    ],
                    "rejection": [
                        "prove default processing performs no implicit file or network access"
                    ],
                },
                "interpretation_note": batch_three_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-ROUNDTRIP-SEMANTIC-001",
                "obligation_basis": "PRODUCTION_POLICY",
                "introduced_in_batch": "XLF-04-BATCH-003",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:roundtrip",
                "category": "semantic_roundtrip_canonical_output",
                "normalized_rule": (
                    "Prove parse-save-parse semantic equivalence for every "
                    "supported stable Core construct."
                ),
                "requirement_class": "PRESERVATION_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": policy_locations("POL-SLC-QUALITY-02"),
                "evidence_requirements": {
                    "positive": [
                        "execute semantic roundtrips for every supported Core construct"
                    ],
                    "rejection": [
                        "detect semantic loss or mutation during parse-save-parse"
                    ],
                },
                "interpretation_note": batch_three_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-WRITE-DETERMINISTIC-001",
                "obligation_basis": "PRODUCTION_POLICY",
                "introduced_in_batch": "XLF-04-BATCH-003",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:writer",
                "category": "semantic_roundtrip_canonical_output",
                "normalized_rule": (
                    "Serialize an unchanged document to byte-identical output "
                    "across repeated writes in the same explicit output mode."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": policy_locations(
                    "POL-SLC-LIFECYCLE-06",
                    "POL-SLC-QUALITY-03",
                ),
                "evidence_requirements": {
                    "positive": [
                        "serialize the same document repeatedly and compare exact bytes"
                    ],
                    "rejection": [
                        "detect prefix, ordering, or formatting nondeterminism"
                    ],
                },
                "interpretation_note": batch_three_note,
            },
            {
                "obligation_id": (
                    "SAL-XLIFF-CORE-SECURITY-EXTERNAL-RESOLUTION-001"
                ),
                "obligation_basis": "PRODUCTION_POLICY",
                "introduced_in_batch": "XLF-04-BATCH-003",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:security",
                "category": "xml_security_resource_limits",
                "normalized_rule": (
                    "Disable XML external-entity expansion and implicit file or "
                    "network reference resolution unless the caller explicitly "
                    "enables a bounded resolver."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": policy_locations("POL-SLC-SEC-02"),
                "evidence_requirements": {
                    "positive": [
                        "parse safe documents with external resolution disabled"
                    ],
                    "rejection": [
                        "reject entity expansion and prove no implicit external I/O"
                    ],
                },
                "interpretation_note": batch_three_note,
            },
            {
                "obligation_id": "SAL-XLIFF-CORE-SECURITY-RESOURCE-LIMITS-001",
                "obligation_basis": "PRODUCTION_POLICY",
                "introduced_in_batch": "XLF-04-BATCH-003",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core:security",
                "category": "xml_security_resource_limits",
                "normalized_rule": (
                    "Enforce configurable safe defaults for input bytes, XML "
                    "nesting, element count, text size, and decoded payload size."
                ),
                "requirement_class": "PROCESSING_REQUIREMENT",
                "normative_level": "MUST",
                "authority_locations": policy_locations(
                    "POL-SLC-SEC-01",
                    "POL-SLC-SEC-05",
                ),
                "evidence_requirements": {
                    "positive": [
                        "accept inputs exactly at every configured resource boundary"
                    ],
                    "rejection": [
                        "reject inputs beyond every boundary without partial success"
                    ],
                },
                "interpretation_note": batch_three_note,
            },
        ]
    )
    batch_five_target_language_id = (
        "SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001"
    )
    batch_five_pairing_id = "SAL-XLIFF-CORE-INLINE-PAIRING-001"
    batch_five_pairing_candidate_ids = {
        "XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1",
        "XLF-CAND-CORE-SCHEMATRON-4BE479DD3F5875EF",
    }
    seeds.append(
        {
            "obligation_id": batch_five_target_language_id,
            "obligation_basis": "XLIFF_SPECIFICATION",
            "introduced_in_batch": "XLF-04-BATCH-005",
            "stable_profiles": ["xliff_2.0", "xliff_2.1"],
            "owner": "core:document",
            "category": "document_structure",
            "normalized_rule": (
                "Require the root trgLang attribute if and only if target "
                "elements occur as children of segment or ignorable elements."
            ),
            "requirement_class": "SEMANTIC_CONSTRAINT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "xliff",
                "if and only if the XLIFF Document contains",
            ),
            "evidence_requirements": {
                "positive": [
                    "accept a root trgLang when target children occur under "
                    "segment or ignorable"
                ],
                "rejection": [
                    "reject target content under segment or ignorable when "
                    "the root trgLang is absent"
                ],
            },
            "interpretation_note": (
                "Independent decision XLF-ADJ-CORE-SCHEMATRON-0001 and "
                "verified SAL fact SAL-XLIFF-00009 establish only the root "
                "target-language condition; incidental XPath context does "
                "not establish separate hierarchy or cardinality rules."
            ),
        }
    )
    seeds.append(
        {
            "obligation_id": batch_five_pairing_id,
            "obligation_basis": "XLIFF_SPECIFICATION",
            "introduced_in_batch": "XLF-04-BATCH-005",
            "stable_profiles": ["xliff_2.1"],
            "owner": "core:inline-code",
            "category": "inline_code_semantics",
            "normalized_rule": (
                "Represent well-formed paired container codes with pc and "
                "require subFlowsStart and subFlowsEnd to occur together "
                "whenever either attribute is present."
            ),
            "requirement_class": "SEMANTIC_CONSTRAINT",
            "normative_level": "MUST",
            "authority_locations": locations(
                "pc",
                "Represents a well-formed spanning original code",
                profiles=("xliff_2.1",),
            ),
            "adjudication_candidate_ids": sorted(
                batch_five_pairing_candidate_ids
            ),
            "evidence_requirements": {
                "positive": [
                    "accept pc content with both subFlowsStart and subFlowsEnd",
                    "accept pc content with neither subFlows attribute",
                ],
                "rejection": [
                    "reject pc content with only one of subFlowsStart or "
                    "subFlowsEnd"
                ],
            },
            "interpretation_note": (
                "Independent adjudications XLF-ADJ-CORE-SCHEMATRON-0002 and "
                "XLF-ADJ-CORE-SCHEMATRON-0003 bind this obligation to exact "
                "SAL-XLIFF-00005 proof. The reciprocal XLIFF 2.1 "
                "Schematron assertions require "
                "subFlowsStart and subFlowsEnd as a pair; the ancestor names "
                "in their XPath contexts do not establish hierarchy "
                "obligations."
            ),
        }
    )
    if not re.fullmatch(r"XLF-04-BATCH-[0-9]{3}", through_batch):
        raise ExtractionError(
            f"invalid default Core through_batch: {through_batch}"
        )
    maximum_sequence = int(through_batch.rsplit("-", 1)[-1])
    if verified_obligation_ids is None:
        verified_ids: set[str] = set()
    elif not isinstance(verified_obligation_ids, set) or any(
        not isinstance(obligation_id, str)
        for obligation_id in verified_obligation_ids
    ):
        raise ExtractionError(
            "verified_obligation_ids must be a set of obligation IDs"
        )
    else:
        verified_ids = set(verified_obligation_ids)
    expected_ids = {
        row["obligation_id"] for row in _default_core_obligation_expectations()
    }
    unknown_verified_ids = sorted(verified_ids - expected_ids)
    if unknown_verified_ids:
        raise ExtractionError(
            "verified_obligation_ids contains unknown Core obligations: "
            f"{unknown_verified_ids}"
        )
    if (
        maximum_sequence >= 5
        and batch_five_target_language_id not in verified_ids
    ):
        raise ExtractionError(
            "XLF-04-BATCH-005 requires an independently adjudicated "
            f"{batch_five_target_language_id} obligation"
        )
    if (
        maximum_sequence >= 5
        and batch_five_pairing_id in verified_ids
    ):
        accepted_candidates = (
            adjudication_evidence or {}
        ).get("accepted_obligation_candidate_ids", {})
        pairing_candidates = (
            accepted_candidates.get(batch_five_pairing_id, [])
            if isinstance(accepted_candidates, Mapping)
            else []
        )
        if not isinstance(pairing_candidates, Sequence) or isinstance(
            pairing_candidates,
            (str, bytes),
        ) or not batch_five_pairing_candidate_ids <= set(
            map(str, pairing_candidates)
        ):
            raise ExtractionError(
                "XLF-04-BATCH-005 requires both reciprocal Schematron "
                f"candidates for {batch_five_pairing_id}"
            )
    return [
        seed
        for seed in seeds
        if int(str(seed["introduced_in_batch"]).rsplit("-", 1)[-1])
        <= maximum_sequence
        and (
            seed["introduced_in_batch"] != "XLF-04-BATCH-005"
            or seed["obligation_id"] in verified_ids
        )
    ]


def _default_requirement_seeds() -> list[dict[str, Any]]:
    """Return the deterministic first-pass XLIFF 2.0/2.1 source matrix."""

    rows: list[dict[str, Any]] = []
    for matrix_id, section_id, requirement in _COMMON_CORE_REQUIREMENTS:
        rows.append(
            {
                "matrix_id": matrix_id,
                "primary_profile": "xliff_2.0",
                "member": "xliff-core-v2.0-os.xml",
                "section_id": section_id,
                "normalized_requirement": requirement,
                "affected_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core",
                "requirement_class": "COMMON_STABLE",
                "confidence": "high",
                "interpretation_note": (
                    "The same named Core section is present in both pinned "
                    "stable authorities; later semantic extraction may split "
                    "changed subordinate rules."
                ),
                "corroborating_profiles": ["xliff_2.1"],
            }
        )

    for profile, modules in sorted(_PROFILE_MODULES.items()):
        profile_token = profile.removeprefix("xliff_").replace(".", "")
        prose_member = (
            "xliff-core-v2.0-os.xml"
            if profile == "xliff_2.0"
            else "xliff-core-v2.1-os.xml"
        )
        for module_name, declaration in sorted(modules.items()):
            module_token = module_name.replace("_", "-").upper()
            module_label = _MODULE_LABELS[module_name]
            rows.append(
                {
                    "matrix_id": f"XLF-DELTA-{profile_token}-MOD-{module_token}",
                    "primary_profile": profile,
                    "member": prose_member,
                    "section_id": declaration["section_id"],
                    "schema_location": declaration["schema_members"][0],
                    "normalized_requirement": (
                        f"Treat the {module_label} module as a separately "
                        f"owned normative capability surface for {profile}."
                    ),
                    "affected_profiles": [profile],
                    "owner": f"module:{module_name}",
                    "requirement_class": "NORMATIVE_MODULE",
                    "confidence": "high",
                    "interpretation_note": (
                        "Applicability is deliberately profile-specific until "
                        "the detailed rule delta proves a broader stable set."
                    ),
                }
            )

    for profile in ("xliff_2.0", "xliff_2.1"):
        profile_token = profile.removeprefix("xliff_").replace(".", "")
        rows.append(
            {
                "matrix_id": f"XLF-DELTA-{profile_token}-VALIDATION-CORE-XSD",
                "primary_profile": profile,
                "member": "schemas/xliff_core_2.0.xsd",
                "schema_location": "schemas/xliff_core_2.0.xsd",
                "normalized_requirement": (
                    f"Validate the {profile} Core vocabulary against the "
                    "digest-bound official XML Schema surface."
                ),
                "affected_profiles": [profile],
                "owner": "core:validation",
                "requirement_class": "VALIDATION_LAYER",
                "confidence": "high",
                "interpretation_note": (
                    "Schema validity is necessary structural evidence but "
                    "does not satisfy semantic processing requirements."
                ),
            }
        )

    for module_name, declaration in sorted(_PROFILE_MODULES["xliff_2.1"].items()):
        for member in declaration.get("validation_members", []):
            module_token = module_name.replace("_", "-").upper()
            rows.append(
                {
                    "matrix_id": f"XLF-DELTA-21-VALIDATION-{module_token}-SCH",
                    "primary_profile": "xliff_2.1",
                    "member": member,
                    "schema_location": member,
                    "normalized_requirement": (
                        f"Apply the official {_MODULE_LABELS[module_name]} "
                        "Schematron layer in addition to XML Schema validation."
                    ),
                    "affected_profiles": ["xliff_2.1"],
                    "owner": f"module:{module_name}",
                    "requirement_class": "VALIDATION_LAYER",
                    "confidence": "high",
                    "interpretation_note": (
                        "This row inventories the shipped validation layer; "
                        "individual assertions remain separate obligations."
                    ),
                }
            )

    rows.extend(
        [
            {
                "matrix_id": "XLF-DELTA-21-VALIDATION-CORE-SCH",
                "primary_profile": "xliff_2.1",
                "member": "schemas/xliff_core_2.1.sch",
                "schema_location": "schemas/xliff_core_2.1.sch",
                "normalized_requirement": (
                    "Apply the official XLIFF 2.1 Core Schematron rules in "
                    "addition to XML Schema validation."
                ),
                "affected_profiles": ["xliff_2.1"],
                "owner": "core:validation",
                "requirement_class": "VALIDATION_LAYER",
                "confidence": "high",
                "interpretation_note": (
                    "Individual assertions and processing implications remain "
                    "separate detailed obligations."
                ),
            },
            {
                "matrix_id": "XLF-DELTA-21-VALIDATION-NVDL",
                "primary_profile": "xliff_2.1",
                "member": "schemas/xliff_2_advanced_validation.nvdl",
                "schema_location": "schemas/xliff_2_advanced_validation.nvdl",
                "normalized_requirement": (
                    "Route XLIFF 2.1 Core and module namespaces through the "
                    "official advanced NVDL validation layer."
                ),
                "affected_profiles": ["xliff_2.1"],
                "owner": "core:validation",
                "requirement_class": "VALIDATION_LAYER",
                "confidence": "high",
                "interpretation_note": (
                    "NVDL routing is an additional validation concern and not "
                    "evidence of semantic module support."
                ),
            },
            {
                "matrix_id": "XLF-DELTA-21-INFORMATIVE-CHANGE-TRACKING",
                "primary_profile": "xliff_2.1",
                "member": "xliff-core-v2.1-os.xml",
                "section_id": "changeTracking_module",
                "schema_location": (
                    "schemas/informativeCopiesOf3rdPartySchemas/extensions/"
                    "change_tracking.xsd"
                ),
                "normalized_requirement": (
                    "Inventory XLIFF 2.1 Change Tracking as an informative "
                    "extension without normative module conformance credit."
                ),
                "affected_profiles": ["xliff_2.1"],
                "owner": "none",
                "requirement_class": "INFORMATIVE_EXTENSION",
                "confidence": "high",
                "interpretation_note": (
                    "The schema is shipped under informative third-party "
                    "copies and cannot inflate the official module count."
                ),
            },
        ]
    )
    return rows


def compile_xliff_matrix(
    profile_sources: Sequence[ProfileSource],
    *,
    requirement_seeds: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compile a deterministic XLIFF 2.0/2.1 authority-surface matrix."""

    sources = {source.profile: source for source in profile_sources}
    if set(sources) != {"xliff_2.0", "xliff_2.1"}:
        raise ExtractionError(
            "XLIFF matrix requires exactly xliff_2.0 and xliff_2.1 authorities"
        )
    if len(sources) != len(profile_sources):
        raise ExtractionError("duplicate XLIFF profile authority")

    archives = {
        profile: _read_authority_archive(source)
        for profile, source in sorted(sources.items())
    }
    profiles: dict[str, Any] = {}
    sections: dict[str, list[dict[str, Any]]] = {}
    for profile, source in sorted(sources.items()):
        profiles[profile], sections[profile] = _profile_inventory(
            source, archives[profile]
        )

    return {
        "schema": "ff6/xliff-normative-delta-matrix@1",
        "format_id": "xliff",
        "status": "SOURCE_LOCATED",
        "generator": "tools/spec/extract_sal_facts.py",
        "digest_policy": {
            "algorithm": "sha256",
            "package_bytes": "exact",
            "archive_member_bytes": "exact_uncompressed",
            "prose_text": "whitespace_normalized_for_section_delta_only",
        },
        "profiles": profiles,
        "profile_boundaries": {
            "xliff_2.2_preview": {
                "status": "AUTHORITY_ABSENT_NOT_COMPILED",
                "stable_obligation_eligible": False,
                "interpretation_note": (
                    "No exact XLIFF 2.2 authority is pinned for this stable "
                    "contract compilation."
                ),
            },
            "xliff_1.2": {
                "status": "EXCLUDED_SEPARATE_COMPATIBILITY_MODEL",
                "stable_obligation_eligible": False,
                "interpretation_note": (
                    "XLIFF 1.2 is not an alias or tolerant mode of the 2.x model."
                ),
            },
        },
        "section_delta": _section_delta(sections),
        "normative_matrix": _requirement_matrix(
            requirement_seeds,
            sources,
            archives,
            sections,
        ),
        "truth_boundary": (
            "Source location and structural inventory are evidence for the "
            "contract denominator, not product implementation or certification."
        ),
    }


def matrix_bytes(matrix: Mapping[str, Any]) -> bytes:
    """Return stable LF-only UTF-8 YAML for a compiled matrix."""

    text = yaml.safe_dump(
        dict(matrix),
        sort_keys=False,
        allow_unicode=True,
        width=1000,
        line_break="\n",
    )
    return text.replace("\r\n", "\n").encode("utf-8")


def write_matrix(matrix: Mapping[str, Any], output: Path) -> str:
    """Atomically replace *output* with canonical matrix bytes."""

    output = Path(output)
    data = matrix_bytes(matrix)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{output.name}.",
            suffix=".tmp",
            dir=output.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(data)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, output)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return _sha256(data)


def check_matrix(matrix: Mapping[str, Any], output: Path) -> str:
    """Verify that *output* already equals the canonical compiled bytes."""

    output = Path(output)
    expected = matrix_bytes(matrix)
    observed = output.read_bytes() if output.is_file() else None
    if observed != expected:
        observed_digest = _sha256(observed) if observed is not None else "MISSING"
        raise MatrixDriftError(
            "matrix output drift: "
            f"expected {_sha256(expected)}, observed {observed_digest}"
        )
    return _sha256(expected)


def _argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compile a deterministic, digest-bound XLIFF 2.0/2.1 "
            "normative-surface matrix."
        )
    )
    parser.add_argument("--format-id", choices=("xliff",), required=True)
    parser.add_argument(
        "--artifact",
        choices=(
            "matrix",
            "core-denominator",
            "core-obligations",
            "core-census",
        ),
        default="matrix",
    )
    parser.add_argument("--source-20", type=Path, required=True)
    parser.add_argument("--source-20-id", required=True)
    parser.add_argument("--source-20-sha256", required=True)
    parser.add_argument(
        "--prose-member-20", default="xliff-core-v2.0-os.xml"
    )
    parser.add_argument("--source-21", type=Path, required=True)
    parser.add_argument("--source-21-id", required=True)
    parser.add_argument("--source-21-sha256", required=True)
    parser.add_argument(
        "--prose-member-21", default="xliff-core-v2.1-os.xml"
    )
    parser.add_argument(
        "--denominator",
        type=Path,
        help=(
            "tracked XLIFF Core expected-obligation denominator; required "
            "for the core-obligations and core-census artifacts"
        ),
    )
    parser.add_argument(
        "--batch-id",
        choices=("XLF-04-BATCH-003", "XLF-04-BATCH-005"),
        default="XLF-04-BATCH-003",
        help="bounded XLF-04 obligation batch for core-obligations",
    )
    parser.add_argument(
        "--adjudications",
        type=Path,
        help="content-addressed adjudication artifact required by Batch 005",
    )
    parser.add_argument(
        "--candidate-census",
        type=Path,
        help="candidate census bound by the Batch 005 adjudication",
    )
    parser.add_argument(
        "--sal-store",
        type=Path,
        help="canonical SAL store bound by the Batch 005 adjudication",
    )
    parser.add_argument(
        "--sal-manifest",
        type=Path,
        help="canonical SAL evidence manifest bound by the adjudication",
    )
    parser.add_argument(
        "--sal-receipt",
        type=Path,
        help="passing canonical SAL receipt bound by the adjudication",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the output does not already equal canonical bytes",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the XLIFF authority compiler CLI."""

    args = _argument_parser().parse_args(argv)
    profile_sources = [
        ProfileSource(
            profile="xliff_2.0",
            source_id=args.source_20_id,
            package_path=args.source_20,
            expected_sha256=args.source_20_sha256,
            prose_member=args.prose_member_20,
        ),
        ProfileSource(
            profile="xliff_2.1",
            source_id=args.source_21_id,
            package_path=args.source_21,
            expected_sha256=args.source_21_sha256,
            prose_member=args.prose_member_21,
        ),
    ]
    policy_sources = _default_core_policy_sources()
    adjudication_paths = {
        "--adjudications": args.adjudications,
        "--candidate-census": args.candidate_census,
        "--sal-store": args.sal_store,
        "--sal-manifest": args.sal_manifest,
        "--sal-receipt": args.sal_receipt,
    }
    if args.artifact != "core-obligations" and any(
        path is not None for path in adjudication_paths.values()
    ):
        raise ExtractionError(
            "adjudication inputs are valid only for core-obligations"
        )
    denominator = compile_xliff_core_denominator(
        profile_sources,
        policy_sources=policy_sources,
    )
    if args.artifact in {"core-obligations", "core-census"}:
        if args.denominator is None:
            raise ExtractionError(
                f"--denominator is required for {args.artifact}"
            )
        try:
            denominator_bytes = args.denominator.read_bytes()
            denominator_input = yaml.safe_load(denominator_bytes)
        except (OSError, yaml.YAMLError) as exc:
            raise ExtractionError(
                f"Core denominator is unreadable: {args.denominator}"
            ) from exc
        if not isinstance(denominator_input, Mapping):
            raise ExtractionError("Core denominator must be a YAML mapping")
        if args.artifact == "core-obligations":
            verified_obligation_ids: set[str] | None = None
            adjudication_evidence: dict[str, Any] | None = None
            if args.batch_id == "XLF-04-BATCH-005":
                missing_adjudication_inputs = [
                    name
                    for name, path in adjudication_paths.items()
                    if path is None
                ]
                if missing_adjudication_inputs:
                    raise ExtractionError(
                        "XLF-04-BATCH-005 requires validated adjudication "
                        "inputs: "
                        f"{missing_adjudication_inputs}"
                    )
                try:
                    (
                        verified_obligation_ids,
                        adjudication_evidence,
                    ) = (
                        _candidate_adjudication
                        .validated_obligation_ids_from_paths(
                            adjudications_path=args.adjudications,
                            candidate_census_path=args.candidate_census,
                            denominator_path=args.denominator,
                            sal_store_path=args.sal_store,
                            sal_manifest_path=args.sal_manifest,
                            sal_receipt_path=args.sal_receipt,
                        )
                    )
                except _candidate_adjudication.AdjudicationError as exc:
                    raise ExtractionError(
                        f"Batch 005 adjudication validation failed: {exc}"
                    ) from exc
            elif any(path is not None for path in adjudication_paths.values()):
                raise ExtractionError(
                    "adjudication inputs cannot alter the Batch 003 compiler"
                )
            artifact = compile_xliff_core_obligations(
                profile_sources,
                obligation_seeds=_default_core_obligation_seeds(
                    through_batch=args.batch_id,
                    verified_obligation_ids=verified_obligation_ids,
                    adjudication_evidence=adjudication_evidence,
                ),
                batch_id=args.batch_id,
                policy_sources=policy_sources,
                expected_obligation_inventory=denominator_input,
            )
            if adjudication_evidence is not None:
                artifact["adjudication_input"] = adjudication_evidence
            row_count = artifact["obligation_count"]
        else:
            artifact = compile_xliff_core_authority_census(
                profile_sources,
                expected_obligation_inventory=denominator_input,
                policy_sources=policy_sources,
            )
            row_count = artifact["candidate_count"]
        artifact["denominator_input_sha256"] = _sha256(denominator_bytes)
    elif args.artifact == "core-denominator":
        artifact = denominator
        row_count = artifact["expected_obligation_count"]
    else:
        artifact = compile_xliff_matrix(
            profile_sources,
            requirement_seeds=_default_requirement_seeds(),
        )
        row_count = len(artifact["normative_matrix"])
    digest = (
        check_matrix(artifact, args.output)
        if args.check
        else write_matrix(artifact, args.output)
    )
    result = {
        "artifact": args.artifact,
        "check": args.check,
        "digest": digest,
        "rows": row_count,
        "schema": artifact["schema"],
    }
    if args.artifact == "matrix":
        result.update(
            {
                "normative_matrix_rows": row_count,
                "profiles": sorted(artifact["profiles"]),
            }
        )
    elif args.artifact == "core-obligations":
        result.update(
            {
                "obligation_count": row_count,
                "stable_profiles": artifact["stable_profiles"],
            }
        )
    elif args.artifact == "core-census":
        result.update(
            {
                "candidate_count": row_count,
                "candidate_scope_complete": artifact[
                    "candidate_scope_complete"
                ],
                "unresolved_expected_obligation_count": len(
                    artifact["unresolved_expected_obligation_ids"]
                ),
            }
        )
    else:
        result.update(
            {
                "expected_obligation_count": row_count,
                "inventory_complete": artifact["inventory_complete"],
                "status": artifact["status"],
            }
        )
    print(
        json.dumps(
            result,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
