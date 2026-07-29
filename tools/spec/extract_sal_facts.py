"""Digest-bound specification extraction for the SAL ingestion pipeline.

The first supported extractor is the XLIFF 2.x profile-surface compiler. It
reads pinned authority archives without extracting them to disk. Additional
format extractors must preserve the same fail-closed digest and output rules.
"""

# generated_by: codex

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any, Iterable, Mapping, NamedTuple, Sequence
import xml.etree.ElementTree as ET
import zipfile

import yaml


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
    matrix = compile_xliff_matrix(
        [
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
        ],
        requirement_seeds=_default_requirement_seeds(),
    )
    digest = (
        check_matrix(matrix, args.output)
        if args.check
        else write_matrix(matrix, args.output)
    )
    print(
        json.dumps(
            {
                "check": args.check,
                "digest": digest,
                "normative_matrix_rows": len(matrix["normative_matrix"]),
                "profiles": sorted(matrix["profiles"]),
                "schema": matrix["schema"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
