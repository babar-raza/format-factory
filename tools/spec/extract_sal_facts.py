"""Digest-bound specification extraction for the SAL ingestion pipeline.

The first supported extractor is the XLIFF 2.x profile-surface compiler. It
reads pinned authority archives without extracting them to disk. Additional
format extractors must preserve the same fail-closed digest and output rules.
"""

# generated_by: codex

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
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
_XML_ID = "{http://www.w3.org/XML/1998/namespace}id"


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


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalized_text(value: str) -> str:
    return " ".join(value.split())


def _safe_member_name(name: str) -> bool:
    pure = PurePosixPath(name)
    return (
        bool(name)
        and "\\" not in name
        and not pure.is_absolute()
        and ".." not in pure.parts
        and ":" not in pure.parts[0]
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


def _parse_xml(data: bytes, *, location: str) -> ET.Element:
    if b"<!ENTITY" in data.upper():
        raise ExtractionError(f"{location} contains a prohibited entity declaration")
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise ExtractionError(f"invalid XML in {location}: {exc}") from exc


def _section_inventory(
    data: bytes,
    *,
    source_id: str,
    source_sha256: str,
    member: str,
) -> list[dict[str, Any]]:
    root = _parse_xml(data, location=f"{source_id}:{member}")
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
    root = _parse_xml(data, location=location)
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
