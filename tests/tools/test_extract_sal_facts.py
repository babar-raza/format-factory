"""Tests for the authority-bound SAL specification extractor."""

# generated_by: codex

from __future__ import annotations

import hashlib
import importlib.util
from copy import deepcopy
from pathlib import Path
from types import ModuleType
from xml.sax.saxutils import escape
import zipfile

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "spec" / "extract_sal_facts.py"
ADJUDICATOR_PATH = (
    REPO_ROOT / "tools" / "spec" / "xliff_core_candidate_adjudication.py"
)
CANDIDATE_CENSUS_PATH = (
    REPO_ROOT / "reports" / "ff6" / "xliff-core-authority-candidate-census.yaml"
)
TARGET_LANGUAGE_CANDIDATE_ID = (
    "XLF-CAND-CORE-SCHEMATRON-B109E9507A685F90"
)
TARGET_LANGUAGE_OBLIGATION_ID = (
    "SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001"
)


def test_registered_extractor_implementation_exists() -> None:
    """The ingest-spec-sal skill must not point at a missing implementation."""

    assert MODULE_PATH.is_file(), (
        "ingest-spec-sal registers tools/spec/extract_sal_facts.py, "
        "but the implementation is missing"
    )


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "extract_sal_facts_under_test", MODULE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_adjudicator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "xliff_core_candidate_adjudication_for_extractor_test",
        ADJUDICATOR_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _xsd(namespace: str) -> bytes:
    return (
        '<?xml version="1.0"?>'
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" '
        f'targetNamespace="{namespace}">'
        '<xs:element name="example" type="xs:string"/>'
        "</xs:schema>"
    ).encode()


def _docbook(*sections: tuple[str, str]) -> bytes:
    body = "".join(
        f'<section id="{section_id}"><title>{title}</title>'
        f"<para>Normative surface for {title}.</para></section>"
        for section_id, title in sections
    )
    return f'<?xml version="1.0"?><article>{body}</article>'.encode()


def _write_archive(
    path: Path,
    *,
    profile: str,
    prose_member: str,
) -> str:
    if profile == "xliff_2.0":
        prose = _docbook(
            ("core", "The Core Specification"),
            ("xliff", "XLIFF Document Structure"),
            ("skeleton", "Skeleton"),
            ("inlineCodes", "Inline Codes"),
            ("segmentation", "Segmentation"),
            ("state", "State"),
            ("extensions", "Extension Mechanisms"),
            ("candidates", "Translation Candidates Module"),
            ("glossary-module", "Glossary Module"),
            ("fs-mod", "Format Style Module"),
            ("metadata_module", "Metadata Module"),
            ("resourceData_module", "Resource Data Module"),
            ("changeTracking_module", "Change Tracking Module"),
            ("size_restriction_module", "Size and Length Restriction Module"),
            ("validation_module", "Validation Module"),
        )
        members = {
            "schemas/xliff_core_2.0.xsd": _xsd(
                "urn:oasis:names:tc:xliff:document:2.0"
            ),
            "schemas/modules/matches.xsd": _xsd("urn:matches"),
            "schemas/modules/glossary.xsd": _xsd("urn:glossary"),
            "schemas/modules/fs.xsd": _xsd("urn:fs"),
            "schemas/modules/metadata.xsd": _xsd("urn:metadata"),
            "schemas/modules/resource_data.xsd": _xsd("urn:resource-data"),
            "schemas/modules/change_tracking.xsd": _xsd("urn:change-tracking"),
            "schemas/modules/size_restriction.xsd": _xsd("urn:size"),
            "schemas/modules/validation.xsd": _xsd("urn:validation"),
        }
    else:
        prose = _docbook(
            ("core", "The Core Specification"),
            ("xliff", "XLIFF Document Structure"),
            ("skeleton", "Skeleton"),
            ("inlineCodes", "Inline Codes"),
            ("segmentation", "Segmentation"),
            ("state", "State"),
            ("extensions", "Extension Mechanisms"),
            ("candidates", "Translation Candidates Module"),
            ("glossary-module", "Glossary Module"),
            ("fs-mod", "Format Style Module"),
            ("metadata_module", "Metadata Module"),
            ("resourceData_module", "Resource Data Module"),
            ("changeTracking_module", "Change Tracking Extension (Informative)"),
            ("size_restriction_module", "Size and Length Restriction Module"),
            ("validation_module", "Validation Module"),
            ("ITS-module", "ITS Module"),
        )
        members = {
            "schemas/xliff_core_2.0.xsd": _xsd(
                "urn:oasis:names:tc:xliff:document:2.0"
            ),
            "schemas/matches.xsd": _xsd("urn:matches"),
            "schemas/glossary.xsd": _xsd("urn:glossary"),
            "schemas/fs.xsd": _xsd("urn:fs"),
            "schemas/metadata.xsd": _xsd("urn:metadata"),
            "schemas/resource_data.xsd": _xsd("urn:resource-data"),
            "schemas/size_restriction.xsd": _xsd("urn:size"),
            "schemas/validation.xsd": _xsd("urn:validation"),
            "schemas/its.xsd": _xsd("urn:its"),
            "schemas/itsm.xsd": _xsd("urn:itsm"),
            "schemas/informativeCopiesOf3rdPartySchemas/extensions/"
            "change_tracking.xsd": _xsd("urn:change-tracking"),
            "schemas/xliff_2_advanced_validation.nvdl": (
                b'<rules xmlns="http://purl.oclc.org/dsdl/nvdl/ns/structure/1.0" '
                b'startMode="xlf-core"/>'
            ),
        }
        schematron = (
            b'<schema xmlns="http://purl.oclc.org/dsdl/schematron">'
            b'<pattern><rule context="/"><assert test="true()">ok</assert>'
            b"</rule></pattern></schema>"
        )
        for name in (
            "matches",
            "glossary",
            "fs",
            "metadata",
            "resource_data",
            "size_restriction",
            "validation",
            "its",
            "xliff_core_2.1",
        ):
            members[f"schemas/{name}.sch"] = schematron
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(prose_member, prose)
        for name, data in members.items():
            archive.writestr(name, data)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_xliff_matrix_distinguishes_profile_modules_and_section_delta(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    path20 = tmp_path / "xliff-20.zip"
    path21 = tmp_path / "xliff-21.zip"
    sha20 = _write_archive(
        path20, profile="xliff_2.0", prose_member="xliff-core-v2.0-os.xml"
    )
    sha21 = _write_archive(
        path21, profile="xliff_2.1", prose_member="xliff-core-v2.1-os.xml"
    )

    matrix = extractor.compile_xliff_matrix(
        [
            extractor.ProfileSource(
                profile="xliff_2.0",
                source_id="SRC-XLF-001",
                package_path=path20,
                expected_sha256=sha20,
                prose_member="xliff-core-v2.0-os.xml",
            ),
            extractor.ProfileSource(
                profile="xliff_2.1",
                source_id="SRC-XLF-002",
                package_path=path21,
                expected_sha256=sha21,
                prose_member="xliff-core-v2.1-os.xml",
            ),
        ],
        requirement_seeds=[
            {
                "matrix_id": "XLF-DELTA-TEST-001",
                "primary_profile": "xliff_2.0",
                "member": "xliff-core-v2.0-os.xml",
                "section_id": "core",
                "normalized_requirement": (
                    "Model the stable XLIFF Core separately from module vocabularies."
                ),
                "affected_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": "core",
                "requirement_class": "COMMON_STABLE",
                "confidence": "high",
                "interpretation_note": "Corroborated by the 2.1 Core section.",
                "corroborating_profiles": ["xliff_2.1"],
            }
        ],
    )

    profiles = matrix["profiles"]
    assert profiles["xliff_2.0"]["module_count"] == 8
    assert profiles["xliff_2.1"]["module_count"] == 8
    assert profiles["xliff_2.0"]["modules"]["change_tracking"]["status"] == (
        "NORMATIVE_MODULE"
    )
    assert "its" not in profiles["xliff_2.0"]["modules"]
    assert profiles["xliff_2.1"]["modules"]["its"]["schema_vocabularies"] == [
        "its",
        "itsm",
    ]
    assert profiles["xliff_2.1"]["informative_extensions"] == [
        "change_tracking"
    ]
    deltas = {row["section_id"]: row["delta_class"] for row in matrix["section_delta"]}
    assert deltas["ITS-module"] == "ADDED_IN_2.1"
    assert deltas["changeTracking_module"] == "CHANGED_IN_2.1"
    row = matrix["normative_matrix"][0]
    assert row["authority_source_id"] == "SRC-XLF-001"
    assert row["source_sha256"] == sha20
    assert row["section_id"] == "core"
    assert row["affected_profiles"] == ["xliff_2.0", "xliff_2.1"]
    assert row["corroborating_authorities"][0]["source_id"] == "SRC-XLF-002"
    assert yaml.safe_dump(matrix, sort_keys=False, allow_unicode=True)


def test_matrix_write_and_check_are_byte_deterministic(tmp_path: Path) -> None:
    extractor = _load_module()
    output = tmp_path / "matrix.yaml"
    matrix = {
        "schema": "ff6/xliff-normative-delta-matrix@1",
        "format_id": "xliff",
        "rows": [{"matrix_id": "XLF-DELTA-TEST-001", "profiles": ["2.0", "2.1"]}],
    }

    first_digest = extractor.write_matrix(matrix, output)
    first_bytes = output.read_bytes()
    second_digest = extractor.write_matrix(matrix, output)

    assert output.read_bytes() == first_bytes
    assert first_digest == second_digest == hashlib.sha256(first_bytes).hexdigest()
    assert extractor.check_matrix(matrix, output) == first_digest
    output.write_text("schema: stale\n", encoding="utf-8")
    with pytest.raises(extractor.MatrixDriftError, match="matrix output drift"):
        extractor.check_matrix(matrix, output)


def test_cli_writes_and_checks_default_xliff_matrix(tmp_path: Path) -> None:
    extractor = _load_module()
    path20 = tmp_path / "xliff-20.zip"
    path21 = tmp_path / "xliff-21.zip"
    output = tmp_path / "xliff-normative-delta-matrix.yaml"
    sha20 = _write_archive(
        path20, profile="xliff_2.0", prose_member="xliff-core-v2.0-os.xml"
    )
    sha21 = _write_archive(
        path21, profile="xliff_2.1", prose_member="xliff-core-v2.1-os.xml"
    )
    args = [
        "--format-id",
        "xliff",
        "--source-20",
        str(path20),
        "--source-20-id",
        "SRC-XLF-001",
        "--source-20-sha256",
        sha20,
        "--source-21",
        str(path21),
        "--source-21-id",
        "SRC-XLF-002",
        "--source-21-sha256",
        sha21,
        "--output",
        str(output),
    ]

    assert extractor.main(args) == 0
    matrix = yaml.safe_load(output.read_text(encoding="utf-8"))
    assert matrix["profiles"]["xliff_2.0"]["module_count"] == 8
    assert matrix["profiles"]["xliff_2.1"]["module_count"] == 8
    assert matrix["profile_boundaries"]["xliff_2.2_preview"]["status"] == (
        "AUTHORITY_ABSENT_NOT_COMPILED"
    )
    assert matrix["profile_boundaries"]["xliff_1.2"]["status"] == (
        "EXCLUDED_SEPARATE_COMPATIBILITY_MODEL"
    )
    rows = matrix["normative_matrix"]
    assert len(rows) >= 36
    assert len({row["matrix_id"] for row in rows}) == len(rows)
    owners = {row["owner"] for row in rows}
    assert "core" in owners
    assert {
        "module:translation_candidates",
        "module:glossary",
        "module:format_style",
        "module:metadata",
        "module:resource_data",
        "module:size_restriction",
        "module:validation",
        "module:its",
    } <= owners
    assert {
        "COMMON_STABLE",
        "NORMATIVE_MODULE",
        "INFORMATIVE_EXTENSION",
        "VALIDATION_LAYER",
    } <= {row["requirement_class"] for row in rows}
    assert extractor.main([*args, "--check"]) == 0


def test_archive_dot_member_fails_closed_as_unsafe_path(tmp_path: Path) -> None:
    extractor = _load_module()
    archive_path = tmp_path / "unsafe-dot-member.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(".", b"not a safe authority member")
    source = extractor.ProfileSource(
        profile="xliff_2.0",
        source_id="SRC-XLF-UNSAFE",
        package_path=archive_path,
        expected_sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        prose_member="xliff-core-v2.0-os.xml",
    )

    with pytest.raises(extractor.ExtractionError, match="unsafe member path"):
        extractor._read_authority_archive(source)


def test_external_doctype_is_rejected_before_xml_parsing() -> None:
    extractor = _load_module()
    xml = (
        b'<!DOCTYPE article SYSTEM "file:///authority-escape.dtd">'
        b"<article><section id=\"core\"><title>Core</title></section></article>"
    )

    with pytest.raises(extractor.ExtractionError, match="DOCTYPE"):
        extractor._parse_xml(xml, location="SRC-XLF-UNSAFE:prose.xml")


def test_digest_bound_docbook_prose_accepts_nonresolving_public_doctype() -> None:
    extractor = _load_module()
    xml = (
        b'<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook XML V4.5//EN" '
        b'"docbook/docbookx.dtd">'
        b'<article><section id="core"><title>Core</title>'
        b"<para>Normative Core surface.</para></section></article>"
    )

    rows = extractor._section_inventory(
        xml,
        source_id="SRC-XLF-PINNED",
        source_sha256="1" * 64,
        member="xliff-core.xml",
    )

    assert len(rows) == 1
    assert rows[0]["section_id"] == "core"


def test_docbook_inventory_ignores_entity_references_inside_comments() -> None:
    extractor = _load_module()
    xml = (
        b'<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook XML V4.5//EN" '
        b'"docbook/docbookx.dtd">'
        b'<article><section id="core"><title>Core</title>'
        b"<!-- disabled &undeclared; publishing text -->"
        b"<para>Normative Core surface.</para></section></article>"
    )

    rows = extractor._section_inventory(
        xml,
        source_id="SRC-XLF-PINNED",
        source_sha256="1" * 64,
        member="xliff-core.xml",
    )

    assert len(rows) == 1
    assert rows[0]["section_id"] == "core"


def test_digest_bound_schematron_accepts_bounded_internal_entities() -> None:
    extractor = _load_module()
    schematron = (
        b"<!DOCTYPE schematron ["
        b'<!ENTITY version "2.1">'
        b"]>"
        b'<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">'
        b"<sch:pattern><sch:rule context=\"/\">"
        b'<sch:assert test="true()">XLIFF &version;</sch:assert>'
        b"</sch:rule></sch:pattern></sch:schema>"
    )

    inventory = extractor._schematron_inventory(
        schematron,
        location="SRC-XLF-PINNED:schemas/core.sch",
    )

    assert inventory["assert_count"] == 1
    assert inventory["report_count"] == 0


@pytest.mark.parametrize(
    ("subset", "message"),
    [
        (
            b'<!ENTITY leak SYSTEM "file:///authority-escape.txt">',
            "unsupported DTD declaration",
        ),
        (
            b'<!ENTITY first "&second;"><!ENTITY second "&first;">',
            "recursive entity expansion",
        ),
        (
            b'<!ENTITY oversized "' + b"x" * 4097 + b'">',
            "exceeds the limit",
        ),
    ],
)
def test_schematron_rejects_external_recursive_and_oversized_entities(
    subset: bytes,
    message: str,
) -> None:
    extractor = _load_module()
    schematron = (
        b"<!DOCTYPE schematron ["
        + subset
        + b"]>"
        + b'<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron"/>'
    )

    with pytest.raises(extractor.ExtractionError, match=message):
        extractor._schematron_inventory(
            schematron,
            location="SRC-XLF-UNSAFE:schemas/core.sch",
        )


def test_authority_archive_digest_mismatch_is_rejected(tmp_path: Path) -> None:
    extractor = _load_module()
    archive_path = tmp_path / "xliff-20.zip"
    _write_archive(
        archive_path,
        profile="xliff_2.0",
        prose_member="xliff-core-v2.0-os.xml",
    )
    source = extractor.ProfileSource(
        profile="xliff_2.0",
        source_id="SRC-XLF-MISMATCH",
        package_path=archive_path,
        expected_sha256="0" * 64,
        prose_member="xliff-core-v2.0-os.xml",
    )

    with pytest.raises(extractor.ExtractionError, match="digest mismatch"):
        extractor._read_authority_archive(source)


@pytest.mark.parametrize(
    "member_names",
    [
        ("Schemas/Core.xsd", "schemas/core.xsd"),
        ("../authority-escape.xml",),
    ],
)
def test_duplicate_casefold_and_traversal_members_are_rejected(
    tmp_path: Path,
    member_names: tuple[str, ...],
) -> None:
    extractor = _load_module()
    archive_path = tmp_path / "unsafe-members.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for member_name in member_names:
            archive.writestr(member_name, b"unsafe")
    source = extractor.ProfileSource(
        profile="xliff_2.0",
        source_id="SRC-XLF-UNSAFE",
        package_path=archive_path,
        expected_sha256=hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        prose_member="xliff-core-v2.0-os.xml",
    )

    with pytest.raises(
        extractor.ExtractionError,
        match="duplicate member names|unsafe member path",
    ):
        extractor._read_authority_archive(source)


def test_entity_declaration_is_rejected_before_xml_parsing() -> None:
    extractor = _load_module()
    xml = (
        b'<!DOCTYPE article [<!ENTITY escape SYSTEM "file:///authority.txt">]>'
        b"<article>&escape;</article>"
    )

    with pytest.raises(extractor.ExtractionError, match="DOCTYPE"):
        extractor._parse_xml(xml, location="SRC-XLF-UNSAFE:prose.xml")


def test_missing_normative_module_schema_is_rejected(tmp_path: Path) -> None:
    extractor = _load_module()
    complete_path = tmp_path / "xliff-21-complete.zip"
    incomplete_path = tmp_path / "xliff-21-missing-fs.zip"
    _write_archive(
        complete_path,
        profile="xliff_2.1",
        prose_member="xliff-core-v2.1-os.xml",
    )
    with (
        zipfile.ZipFile(complete_path) as source_archive,
        zipfile.ZipFile(
            incomplete_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as target_archive,
    ):
        for info in source_archive.infolist():
            if info.filename != "schemas/fs.xsd":
                target_archive.writestr(info.filename, source_archive.read(info))
    source = extractor.ProfileSource(
        profile="xliff_2.1",
        source_id="SRC-XLF-MISSING",
        package_path=incomplete_path,
        expected_sha256=hashlib.sha256(incomplete_path.read_bytes()).hexdigest(),
        prose_member="xliff-core-v2.1-os.xml",
    )
    members = extractor._read_authority_archive(source)

    with pytest.raises(extractor.ExtractionError, match="lacks schemas/fs.xsd"):
        extractor._profile_inventory(source, members)


def test_requirement_rows_reject_malformed_duplicate_and_preview_profiles() -> None:
    extractor = _load_module()
    sources = {
        profile: extractor.ProfileSource(
            profile=profile,
            source_id=f"SRC-{profile}",
            package_path=Path("unused.zip"),
            expected_sha256="1" * 64,
            prose_member="prose.xml",
        )
        for profile in ("xliff_2.0", "xliff_2.1")
    }
    members = {
        profile: {"prose.xml": b"<article/>"}
        for profile in ("xliff_2.0", "xliff_2.1")
    }
    sections = {
        profile: [{"section_id": "core"}]
        for profile in ("xliff_2.0", "xliff_2.1")
    }
    valid = {
        "matrix_id": "XLF-DELTA-NEGATIVE-001",
        "primary_profile": "xliff_2.0",
        "member": "prose.xml",
        "section_id": "core",
        "normalized_requirement": (
            "A complete negative-control requirement with an exact stable profile."
        ),
        "affected_profiles": ["xliff_2.0"],
        "owner": "core",
        "requirement_class": "COMMON_STABLE",
        "confidence": "high",
        "interpretation_note": "Negative-control seed.",
    }
    malformed = dict(valid)
    del malformed["owner"]
    with pytest.raises(extractor.ExtractionError, match="missing fields"):
        extractor._requirement_matrix(
            [malformed],
            sources,
            members,
            sections,
        )
    with pytest.raises(extractor.ExtractionError, match="duplicate matrix_id"):
        extractor._requirement_matrix(
            [valid, valid],
            sources,
            members,
            sections,
        )
    preview = {**valid, "affected_profiles": ["xliff_2.2_preview"]}
    with pytest.raises(extractor.ExtractionError, match="invalid affected_profiles"):
        extractor._requirement_matrix(
            [preview],
            sources,
            members,
            sections,
        )


def _write_core_obligation_archive(
    path: Path,
    *,
    profile: str,
) -> tuple[str, str]:
    prose_member = f"xliff-core-v{profile.removeprefix('xliff_')}-os.xml"
    paragraphs: dict[str, tuple[str, ...]] = {
        "xliff": (
            (
                "Root element for XLIFF documents; it requires the version "
                "and srcLang attributes and one or more file children."
            ),
            (
                "The trgLang attribute is required if and only if the XLIFF "
                "Document contains target elements that are children of "
                "segment or ignorable."
            ),
        ),
        "unit": ("A unit must contain at least one segment element.",),
        "spanningcodeusage": ((
            "A spanning code must be represented using an sc element and an "
            "ec element when the code is not well-formed or is orphaned. "
            "Agents must be able to handle both paired-container and spanning "
            "inline code representations."
        ),),
        "segmentationModification": ((
            "Only segment or ignorable elements whose resolved canResegment "
            "value is yes may be split."
        ),),
        "state": ((
            "Writers must not advance state beyond initial when the segment "
            "does not contain a target child and must also update or delete "
            "subState when state changes."
        ),),
        "extensions": ((
            "Writers that do not support a custom namespace extension should "
            "preserve that extension without modification."
        ),),
        "inlineCodes": ((
            "Agents must be able to handle both paired-container and spanning "
            "inline code representations."
        ),),
        "id": (
            "The value must be unique among all <file> id attribute values "
            "within the enclosing <xliff> element.",
        ),
        "dataref": (
            "The value must be the value of the id attribute of one of the "
            "<data> element listed in the same <unit> element.",
        ),
        "fragid": (
            "Any unit, group or file selector missing to resolve the relative "
            "reference is obtained from the immediate enclosing unit, group "
            "or file elements.",
        ),
        "translate": (
            "The value of the translate attribute of its parent element.",
        ),
        "xml_lang": (
            "The value set in the srcLang attribute of the enclosing <xliff> "
            "element.",
            "The value set in the trgLang attribute of the enclosing <xliff> "
            "element.",
        ),
        "srcdir": (
            "The value of the srcDir attribute of its parent element.",
        ),
        "trgdir": (
            "The value of the trgDir attribute of its parent element.",
        ),
        "xml_space": (
            "The value of the xml:space attribute of its parent element.",
        ),
        "segmentationRepresentation": (
            "Each <segment> element has one <source> element that contains the "
            "source content and one optional <target> element that can be empty "
            "or contain the translation of the source content at a given state.",
        ),
        "target": (
            "When a <target> element is a child of <segment> or <ignorable>, "
            "the explicit or inherited value of the optional xml:lang must be "
            "equal to the value of the trgLang attribute of the enclosing "
            "<xliff> element.",
        ),
        "order": (
            "When order is not explicitly set, the <target> order corresponds "
            "to its sibling <source>.",
        ),
        "subflowsdesc": (
            "Please note that the static structure encoded by <file>, <group>, "
            "and <unit> elements is principally immutable in XLIFF Documents "
            "and hence the unit order initially set by the Extractor will be "
            "preserved throughout the roundtrip even in the special case of "
            "sub-flows.",
        ),
        "mediaType": (
            (
                "Direct external reference mechanisms: An XLIFF document has "
                "a number of attributes of the type URI or IRI, all of which "
                "may be dereferenced. Therefore, their security implications "
                "should be considered."
            ),
        ) if profile == "xliff_2.1" else (),
    }
    body = "".join(
        f'<section id="{section_id}"><title>{section_id}</title>'
        + "".join(
            f"<para>{escape(paragraph)}</para>"
            for paragraph in section_paragraphs
        )
        + "</section>"
        for section_id, section_paragraphs in paragraphs.items()
    )
    prose = f'<?xml version="1.0"?><article>{body}</article>'.encode()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(prose_member, prose)
    return prose_member, hashlib.sha256(path.read_bytes()).hexdigest()


def test_core_obligation_batch_is_source_bound_and_truthfully_partial(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    assert hasattr(extractor, "compile_xliff_core_obligations"), (
        "XLF-04 requires a separate fine-grained Core obligation compiler; "
        "the 36 coarse XLF-03 matrix anchors cannot satisfy this test"
    )

    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )

    seed_definitions = [
        (
            "SAL-XLIFF-CORE-DOCUMENT-ROOT-001",
            "document_structure",
            "xliff",
            "requires the version and srcLang attributes",
            "Model the XLIFF root, stable version, source language, and "
            "non-empty file collection as explicit document invariants.",
            "STRUCTURAL_CONSTRAINT",
            "core:document",
        ),
        (
            "SAL-XLIFF-CORE-HIERARCHY-UNIT-001",
            "hierarchy_cardinality",
            "unit",
            "must contain at least one segment",
            "Reject a unit that does not contain the minimum required segment "
            "content defined by the stable Core hierarchy.",
            "CARDINALITY_CONSTRAINT",
            "core:hierarchy",
        ),
        (
            "SAL-XLIFF-CORE-INLINE-SPANNING-001",
            "inline_code_semantics",
            "spanningcodeusage",
            "must be represented using an sc element and an ec element",
            "Preserve spanning inline-code identity and pair an sc start with "
            "its corresponding ec end representation.",
            "SEMANTIC_CONSTRAINT",
            "core:inline-code",
        ),
        (
            "SAL-XLIFF-CORE-SEGMENT-SPLIT-001",
            "segmentation",
            "segmentationModification",
            "resolved canResegment value is yes may be split",
            "Permit a segmentation split only when the resolved canResegment "
            "value authorizes that modification.",
            "PROCESSING_REQUIREMENT",
            "core:segmentation",
        ),
        (
            "SAL-XLIFF-CORE-STATE-TARGET-001",
            "state",
            "state",
            "must not advance state beyond initial",
            "Reject a non-initial segment state when no target translation is "
            "present, and keep sub-state synchronized with state changes.",
            "PROCESSING_REQUIREMENT",
            "core:state",
        ),
        (
            "SAL-XLIFF-CORE-EXTENSION-PRESERVE-001",
            "extension_preservation",
            "extensions",
            "should preserve that extension without modification",
            "Preserve unsupported custom-namespace extension content without "
            "silently claiming semantic support for the extension.",
            "PRESERVATION_REQUIREMENT",
            "core:extensions",
        ),
        (
            "SAL-XLIFF-CORE-AGENT-INLINE-001",
            "agent_processing",
            "inlineCodes",
            "Agents must be able to handle both",
            "Require processing agents to handle both paired-container and "
            "spanning inline-code representations without information loss.",
            "PROCESSING_REQUIREMENT",
            "core:agents",
        ),
    ]
    seeds = []
    for (
        obligation_id,
        category,
        section_id,
        source_anchor,
        normalized_rule,
        requirement_class,
        owner,
    ) in seed_definitions:
        seeds.append(
            {
                "obligation_id": obligation_id,
                "obligation_basis": "XLIFF_SPECIFICATION",
                "introduced_in_batch": "XLF-04-BATCH-001",
                "stable_profiles": ["xliff_2.0", "xliff_2.1"],
                "owner": owner,
                "category": category,
                "normalized_rule": normalized_rule,
                "requirement_class": requirement_class,
                "normative_level": "MUST",
                "authority_locations": [
                    {
                        "profile": profile,
                        "location_kind": "prose_paragraph",
                        "member": (
                            f"xliff-core-v{profile.removeprefix('xliff_')}-os.xml"
                        ),
                        "section_id": section_id,
                        "paragraph_index": 0,
                        "source_anchor": source_anchor,
                    }
                    for profile in ("xliff_2.0", "xliff_2.1")
                ],
                "evidence_requirements": {
                    "positive": ["execute the conforming behavior"],
                    "rejection": ["execute the discriminating invalid case"],
                },
                "interpretation_note": (
                    "Representative XLF-04 batch; later batches retain this "
                    "stable identity and add the remaining Core categories."
                ),
            }
        )

    inventory = extractor.compile_xliff_core_obligations(
        sources,
        obligation_seeds=seeds,
        batch_id="XLF-04-BATCH-001",
    )

    assert inventory["schema"] == "ff6/xliff-core-obligation-inventory@2"
    assert inventory["status"] == "SOURCE_LOCATED_PARTIAL"
    assert inventory["batch_id"] == "XLF-04-BATCH-001"
    assert inventory["obligation_count"] == 7
    assert inventory["complete"] is False
    assert inventory["covered_categories"] == sorted(
        definition[1] for definition in seed_definitions
    )
    assert "xml_security_resource_limits" in inventory["remaining_categories"]
    assert "semantic_roundtrip_canonical_output" in (
        inventory["remaining_categories"]
    )

    obligations = inventory["obligations"]
    assert len({row["obligation_id"] for row in obligations}) == len(obligations)
    for row in obligations:
        assert row["obligation_id"].startswith("SAL-XLIFF-CORE-")
        assert row["stable_profiles"] == ["xliff_2.0", "xliff_2.1"]
        assert [location["profile"] for location in row["authority_locations"]] == [
            "xliff_2.0",
            "xliff_2.1",
        ]
        assert all(
            len(location["source_text_sha256"]) == 64
            and len(location["source_sha256"]) == 64
            and len(location["member_sha256"]) == 64
            for location in row["authority_locations"]
        )
        assert row["evidence_requirements"]["positive"]
        assert row["evidence_requirements"]["rejection"]

    inline = next(
        row
        for row in obligations
        if row["obligation_id"] == "SAL-XLIFF-CORE-INLINE-SPANNING-001"
    )
    assert inline["owner"] == "core:inline-code"
    assert inline["requirement_class"] == "SEMANTIC_CONSTRAINT"
    assert inline["authority_locations"][0]["section_id"] == "spanningcodeusage"
    assert "36 coarse XLF-03 anchors" in inventory["truth_boundary"]


def test_cli_writes_and_checks_default_core_obligation_batch(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    assert hasattr(extractor, "_default_core_obligation_seeds"), (
        "XLF-04 requires curated, source-located Core seeds before its "
        "deterministic command can generate the first real obligation batch"
    )

    sources: dict[str, tuple[Path, str]] = {}
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        _member, digest = _write_core_obligation_archive(path, profile=profile)
        sources[profile] = (path, digest)
    denominator_output = tmp_path / "xliff-core-obligation-denominator.yaml"
    output = tmp_path / "xliff-core-obligation-inventory.yaml"
    common_args = [
        "--format-id",
        "xliff",
        "--source-20",
        str(sources["xliff_2.0"][0]),
        "--source-20-id",
        "SRC-XLF-001",
        "--source-20-sha256",
        sources["xliff_2.0"][1],
        "--source-21",
        str(sources["xliff_2.1"][0]),
        "--source-21-id",
        "SRC-XLF-002",
        "--source-21-sha256",
        sources["xliff_2.1"][1],
    ]
    assert extractor.main(
        [
            *common_args,
            "--artifact",
            "core-denominator",
            "--output",
            str(denominator_output),
        ]
    ) == 0
    args = [
        *common_args,
        "--artifact",
        "core-obligations",
        "--denominator",
        str(denominator_output),
        "--output",
        str(output),
    ]

    assert extractor.main(args) == 0
    first_bytes = output.read_bytes()
    inventory = yaml.safe_load(first_bytes)
    assert inventory["schema"] == "ff6/xliff-core-obligation-inventory@2"
    assert inventory["artifact_id"] == (
        "FF6-XLIFF-CORE-OBLIGATIONS-XLF04-BATCH003"
    )
    assert inventory["artifact_type"] == (
        "core_and_production_obligation_inventory"
    )
    assert inventory["visibility"] == "generated"
    assert inventory["publish_allowed"] is False
    assert inventory["generated_by"] == "codex"
    assert inventory["batch_id"] == "XLF-04-BATCH-003"
    assert inventory["status"] == "SOURCE_LOCATED_PARTIAL"
    assert inventory["obligation_count"] == 25
    assert inventory["uncovered_categories"] == []
    assert inventory["expected_obligation_count"] > 25
    assert inventory["denominator_status"] == "OPEN_AUTHORITY_CENSUS"
    assert inventory["denominator_input_sha256"] == hashlib.sha256(
        denominator_output.read_bytes()
    ).hexdigest()
    assert inventory["complete"] is False
    assert extractor.main([*args, "--check"]) == 0
    assert output.read_bytes() == first_bytes
    explicit_output = tmp_path / "explicit-batch-three.yaml"
    assert extractor.main(
        [
            *args[:-2],
            "--batch-id",
            "XLF-04-BATCH-003",
            "--output",
            str(explicit_output),
        ]
    ) == 0
    assert explicit_output.read_bytes() == first_bytes


def _batch_five_cli_inputs(
    extractor: ModuleType,
    tmp_path: Path,
) -> tuple[list[str], dict[str, Path], Path]:
    sources: dict[str, tuple[Path, str]] = {}
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        _member, digest = _write_core_obligation_archive(path, profile=profile)
        sources[profile] = (path, digest)
    denominator_path = tmp_path / "denominator.yaml"
    common_args = [
        "--format-id",
        "xliff",
        "--source-20",
        str(sources["xliff_2.0"][0]),
        "--source-20-id",
        "SRC-XLF-001",
        "--source-20-sha256",
        sources["xliff_2.0"][1],
        "--source-21",
        str(sources["xliff_2.1"][0]),
        "--source-21-id",
        "SRC-XLF-002",
        "--source-21-sha256",
        sources["xliff_2.1"][1],
    ]
    assert extractor.main(
        [
            *common_args,
            "--artifact",
            "core-denominator",
            "--output",
            str(denominator_path),
        ]
    ) == 0

    adjudicator = _load_adjudicator()
    census_path = tmp_path / "candidate-census.yaml"
    census_path.write_bytes(CANDIDATE_CENSUS_PATH.read_bytes())
    census = yaml.safe_load(census_path.read_bytes())
    denominator = yaml.safe_load(denominator_path.read_bytes())
    manifest_path = tmp_path / "sal-manifest.yaml"
    manifest_path.write_text(
        "schema: test-manifest\nformat_id: xliff\n",
        encoding="utf-8",
    )
    manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    claim = (
        "The trgLang attribute is required when target elements occur under "
        "segment or ignorable."
    )
    fact_proof_sha256 = "9" * 64
    receipt_path = tmp_path / "sal-receipt.yaml"
    receipt = {
        "format_id": "xliff",
        "result": "PASS",
        "manifest": {"sha256": manifest_sha256},
        "facts": [
            {
                "fact_id": "SAL-XLIFF-00009",
                "claim_sha256": hashlib.sha256(
                    claim.encode("utf-8")
                ).hexdigest(),
                "proof_sha256": fact_proof_sha256,
                "result": "PASS",
            }
        ],
    }
    receipt_path.write_text(
        yaml.safe_dump(receipt, sort_keys=False),
        encoding="utf-8",
    )
    receipt_sha256 = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    store_path = tmp_path / "sal-store.yaml"
    store = {
        "format_id": "xliff",
        "facts": [
            {
                "fact_id": "SAL-XLIFF-00009",
                "claim": claim,
                "verification_status": "verified",
                "provenance": {
                    "verification": {
                        "method": "declarative_authority_v1",
                        "manifest_sha256": manifest_sha256,
                        "receipt_sha256": receipt_sha256,
                        "fact_proof_sha256": fact_proof_sha256,
                    }
                },
            }
        ],
    }
    store_path.write_text(
        yaml.safe_dump(store, sort_keys=False),
        encoding="utf-8",
    )
    decision = {
        "decision_id": "XLF-ADJ-CORE-SCHEMATRON-0001",
        "candidate_id": TARGET_LANGUAGE_CANDIDATE_ID,
        "accepted_obligation_ids": [TARGET_LANGUAGE_OBLIGATION_ID],
        "rejected_obligations": [
            {
                "obligation_id": obligation_id,
                "reason_code": reason_code,
                "reason": (
                    "Independent reading of the exact Schematron assertion "
                    "does not establish this proposed behavior."
                ),
            }
            for obligation_id, reason_code in sorted(
                {
                    "SAL-XLIFF-CORE-AGENT-VALIDATOR-001": (
                        "DOWNSTREAM_CAPABILITY_NOT_DIRECT_SEMANTIC_OWNER"
                    ),
                    "SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001": (
                        "INCIDENTAL_XPATH_CONTEXT_TOKEN"
                    ),
                    "SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001": (
                        "INCIDENTAL_XPATH_CONTEXT_TOKEN"
                    ),
                    "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001": (
                        "TRIGGER_DOES_NOT_ESTABLISH_CARDINALITY"
                    ),
                }.items()
            )
        ],
        "sal_fact_ids": ["SAL-XLIFF-00009"],
        "authority_reason": (
            "The assertion directly requires the root trgLang for target "
            "content under segment or ignorable; those context names do not "
            "establish separate hierarchy or cardinality obligations."
        ),
    }
    artifact = adjudicator.compile_adjudication_artifact(
        candidate_census=census,
        candidate_census_sha256=hashlib.sha256(
            census_path.read_bytes()
        ).hexdigest(),
        denominator=denominator,
        denominator_sha256=hashlib.sha256(
            denominator_path.read_bytes()
        ).hexdigest(),
        sal_store=store,
        sal_store_sha256=hashlib.sha256(store_path.read_bytes()).hexdigest(),
        sal_manifest_sha256=manifest_sha256,
        sal_receipt=receipt,
        sal_receipt_sha256=receipt_sha256,
        decisions=[decision],
    )
    adjudications_path = tmp_path / "adjudications.yaml"
    adjudications_path.write_bytes(adjudicator.artifact_bytes(artifact))
    output_path = tmp_path / "batch-five-obligations.yaml"
    proof_paths = {
        "candidate_census": census_path,
        "denominator": denominator_path,
        "sal_store": store_path,
        "sal_manifest": manifest_path,
        "sal_receipt": receipt_path,
        "adjudications": adjudications_path,
    }
    args = [
        *common_args,
        "--artifact",
        "core-obligations",
        "--batch-id",
        "XLF-04-BATCH-005",
        "--denominator",
        str(denominator_path),
        "--output",
        str(output_path),
    ]
    return args, proof_paths, output_path


def _adjudication_cli_args(proof_paths: dict[str, Path]) -> list[str]:
    return [
        "--adjudications",
        str(proof_paths["adjudications"]),
        "--candidate-census",
        str(proof_paths["candidate_census"]),
        "--sal-store",
        str(proof_paths["sal_store"]),
        "--sal-manifest",
        str(proof_paths["sal_manifest"]),
        "--sal-receipt",
        str(proof_paths["sal_receipt"]),
    ]


def test_cli_batch_five_requires_validated_adjudications(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    args, _proof_paths, _output = _batch_five_cli_inputs(
        extractor,
        tmp_path,
    )

    with pytest.raises(
        extractor.ExtractionError,
        match="adjudication",
    ):
        extractor.main(args)


def test_cli_batch_five_compiles_only_validated_adjudication_ids(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    args, proof_paths, output = _batch_five_cli_inputs(extractor, tmp_path)
    complete_args = [*args, *_adjudication_cli_args(proof_paths)]

    assert extractor.main(complete_args) == 0
    first_bytes = output.read_bytes()
    inventory = yaml.safe_load(first_bytes)
    assert inventory["batch_id"] == "XLF-04-BATCH-005"
    assert inventory["obligation_count"] == 26
    assert inventory["resolved_expected_obligation_count"] == 26
    assert len(inventory["missing_expected_obligation_ids"]) == 79
    assert inventory["complete"] is False
    assert extractor.main([*complete_args, "--check"]) == 0
    assert output.read_bytes() == first_bytes


@pytest.mark.parametrize(
    "mutation",
    [
        "candidate_content",
        "occurrence",
        "authority_member",
        "denominator",
        "decision",
        "sal_store",
        "sal_manifest",
        "sal_receipt",
        "adjudicator",
    ],
)
def test_cli_batch_five_rejects_adjudication_dependency_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    extractor = _load_module()
    args, proof_paths, _output = _batch_five_cli_inputs(extractor, tmp_path)
    if mutation in {"candidate_content", "occurrence", "authority_member"}:
        census = yaml.safe_load(proof_paths["candidate_census"].read_bytes())
        candidate = next(
            row
            for row in census["candidates"]
            if row["candidate_id"] == TARGET_LANGUAGE_CANDIDATE_ID
        )
        if mutation == "candidate_content":
            candidate["candidate_content_sha256"] = "0" * 64
        elif mutation == "occurrence":
            candidate["occurrences"][0]["occurrence_sha256"] = "0" * 64
        else:
            candidate["occurrences"][0]["member_sha256"] = "0" * 64
        proof_paths["candidate_census"].write_text(
            yaml.safe_dump(census, sort_keys=False),
            encoding="utf-8",
        )
    elif mutation == "decision":
        artifact = yaml.safe_load(proof_paths["adjudications"].read_bytes())
        artifact["decisions"][0]["authority_reason"] += " changed"
        proof_paths["adjudications"].write_text(
            yaml.safe_dump(artifact, sort_keys=False),
            encoding="utf-8",
        )
    elif mutation == "adjudicator":
        monkeypatch.setattr(
            extractor._candidate_adjudication,
            "module_sha256",
            lambda: "0" * 64,
        )
    else:
        proof_paths[mutation].write_bytes(
            proof_paths[mutation].read_bytes() + b"\n"
        )

    with pytest.raises(
        extractor.ExtractionError,
        match="adjudication",
    ):
        extractor.main([*args, *_adjudication_cli_args(proof_paths)])


def test_core_obligation_seed_cannot_self_declare_verification(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    seed = dict(extractor._default_core_obligation_seeds()[0])
    seed["verification_status"] = "VERIFIED"

    with pytest.raises(
        extractor.ExtractionError,
        match="unsupported Core obligation seed fields",
    ):
        extractor.compile_xliff_core_obligations(
            sources,
            obligation_seeds=[seed],
            batch_id="XLF-04-BATCH-001",
        )


def test_core_paragraph_index_accepts_bounded_docbook_internal_entities() -> None:
    extractor = _load_module()
    xml = (
        b'<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook XML V4.5//EN" '
        b'"docbook/docbookx.dtd" [<!ENTITY product "XLIFF">]>'
        b'<article><section id="core"><title>Core</title>'
        b"<para>&product; processing requirement.</para>"
        b"</section></article>"
    )

    paragraphs = extractor._prose_paragraph_index(
        xml,
        location="SRC-XLF-PINNED:xliff-core.xml",
    )

    assert paragraphs == {"core": ["XLIFF processing requirement."]}


def test_category_presence_cannot_self_certify_core_completeness(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    seeds = extractor._default_core_obligation_seeds(
        through_batch="XLF-04-BATCH-002"
    )
    base = seeds[0]
    missing_categories = sorted(
        extractor._XLIFF_CORE_CATEGORIES
        - {str(seed["category"]) for seed in seeds}
    )
    for index, category in enumerate(missing_categories, 1):
        seed = dict(base)
        seed["obligation_id"] = f"SAL-XLIFF-CORE-COVERAGE-{index:03d}"
        seed["category"] = category
        seed["owner"] = "core:coverage-control"
        seed["normalized_rule"] = (
            f"Coverage-control placeholder for {category}; its presence must "
            "not establish completeness without an obligation denominator."
        )
        seeds.append(seed)

    inventory = extractor.compile_xliff_core_obligations(
        sources,
        obligation_seeds=seeds,
        batch_id="XLF-04-BATCH-002",
    )

    assert inventory["remaining_categories"] == []
    assert inventory["complete"] is False
    assert inventory["status"] == "SOURCE_LOCATED_PARTIAL"
    assert inventory["completeness_basis"] == (
        "EXPECTED_OBLIGATION_DENOMINATOR_ABSENT"
    )


def test_default_core_obligation_batch_two_extends_three_normative_families(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    batch_001_ids = {
        "SAL-XLIFF-CORE-AGENT-INLINE-001",
        "SAL-XLIFF-CORE-DOCUMENT-ROOT-001",
        "SAL-XLIFF-CORE-EXTENSION-PRESERVE-001",
        "SAL-XLIFF-CORE-HIERARCHY-UNIT-001",
        "SAL-XLIFF-CORE-INLINE-SPANNING-001",
        "SAL-XLIFF-CORE-SEGMENT-SPLIT-001",
        "SAL-XLIFF-CORE-STATE-SUBSTATE-001",
    }
    batch_002_ids = {
        "SAL-XLIFF-CORE-DIRECTION-SOURCE-001",
        "SAL-XLIFF-CORE-DIRECTION-TARGET-001",
        "SAL-XLIFF-CORE-ID-FILE-UNIQUE-001",
        "SAL-XLIFF-CORE-INHERIT-TRANSLATE-001",
        "SAL-XLIFF-CORE-LANGUAGE-SOURCE-001",
        "SAL-XLIFF-CORE-LANGUAGE-TARGET-001",
        "SAL-XLIFF-CORE-REFERENCE-DATAREF-001",
        "SAL-XLIFF-CORE-REFERENCE-FRAGMENT-INHERIT-001",
        "SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001",
        "SAL-XLIFF-CORE-TARGET-LANGUAGE-001",
        "SAL-XLIFF-CORE-TARGET-ORDER-001",
        "SAL-XLIFF-CORE-WHITESPACE-INHERIT-001",
    }
    seeds = extractor._default_core_obligation_seeds(
        through_batch="XLF-04-BATCH-002"
    )
    by_id = {str(seed["obligation_id"]): seed for seed in seeds}

    assert set(by_id) == batch_001_ids | batch_002_ids
    assert {
        by_id[obligation_id]["introduced_in_batch"]
        for obligation_id in batch_001_ids
    } == {"XLF-04-BATCH-001"}
    assert {
        by_id[obligation_id]["introduced_in_batch"]
        for obligation_id in batch_002_ids
    } == {"XLF-04-BATCH-002"}

    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )

    inventory = extractor.compile_xliff_core_obligations(
        sources,
        obligation_seeds=seeds,
        batch_id="XLF-04-BATCH-002",
    )

    assert inventory["artifact_id"] == (
        "FF6-XLIFF-CORE-OBLIGATIONS-XLF04-BATCH002"
    )
    assert inventory["batch_id"] == "XLF-04-BATCH-002"
    assert inventory["obligation_count"] == 19
    assert inventory["remaining_categories"] == [
        "semantic_roundtrip_canonical_output",
        "xml_security_resource_limits",
    ]
    assert inventory["complete"] is False
    assert inventory["completeness_basis"] == (
        "EXPECTED_OBLIGATION_DENOMINATOR_ABSENT"
    )

    rows = {row["obligation_id"]: row for row in inventory["obligations"]}
    assert {rows[item]["introduced_in_batch"] for item in batch_002_ids} == {
        "XLF-04-BATCH-002"
    }
    assert {
        rows[item]["category"] for item in batch_002_ids
    } == {
        "identifiers_references_inheritance",
        "language_direction_whitespace",
        "source_target_correspondence",
    }
    for obligation_id in batch_002_ids:
        assert len(rows[obligation_id]["authority_locations"]) == 2
        assert all(
            location["source_text_sha256"]
            for location in rows[obligation_id]["authority_locations"]
        )

    with pytest.raises(
        extractor.ExtractionError,
        match="introduced after requested batch",
    ):
        extractor.compile_xliff_core_obligations(
            sources,
            obligation_seeds=seeds,
            batch_id="XLF-04-BATCH-001",
        )


def test_default_core_obligation_batch_three_separates_spec_and_policy_authority(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )

    seeds = extractor._default_core_obligation_seeds(
        through_batch="XLF-04-BATCH-003"
    )
    batch_three_ids = {
        str(seed["obligation_id"])
        for seed in seeds
        if seed["introduced_in_batch"] == "XLF-04-BATCH-003"
    }
    assert batch_three_ids == {
        "SAL-XLIFF-CORE-ROUNDTRIP-SEMANTIC-001",
        "SAL-XLIFF-CORE-ROUNDTRIP-STRUCTURE-001",
        "SAL-XLIFF-CORE-SECURITY-EXTERNAL-RESOLUTION-001",
        "SAL-XLIFF-CORE-SECURITY-RESOURCE-LIMITS-001",
        "SAL-XLIFF-CORE-SECURITY-URI-RISK-001",
        "SAL-XLIFF-CORE-WRITE-DETERMINISTIC-001",
    }

    policy_sources = extractor._default_core_policy_sources()
    denominator = extractor.compile_xliff_core_denominator(
        sources,
        policy_sources=policy_sources,
    )
    inventory = extractor.compile_xliff_core_obligations(
        sources,
        obligation_seeds=seeds,
        batch_id="XLF-04-BATCH-003",
        policy_sources=policy_sources,
        expected_obligation_inventory=denominator,
    )

    assert inventory["obligation_count"] == 25
    assert inventory["uncovered_categories"] == []
    assert inventory["expected_obligation_count"] > inventory["obligation_count"]
    assert inventory["missing_expected_obligation_ids"]
    assert inventory["denominator_status"] == "OPEN_AUTHORITY_CENSUS"
    assert inventory["denominator_complete"] is False
    assert inventory["complete"] is False

    rows = {row["obligation_id"]: row for row in inventory["obligations"]}
    structure = rows["SAL-XLIFF-CORE-ROUNDTRIP-STRUCTURE-001"]
    assert structure["obligation_basis"] == "XLIFF_SPECIFICATION"
    assert structure["conformance_effect"] == "STANDARD_CONFORMANCE"
    assert {item["profile"] for item in structure["authority_locations"]} == {
        "xliff_2.0",
        "xliff_2.1",
    }

    uri_risk = rows["SAL-XLIFF-CORE-SECURITY-URI-RISK-001"]
    assert uri_risk["stable_profiles"] == ["xliff_2.1"]
    assert uri_risk["obligation_basis"] == "XLIFF_SPECIFICATION"

    for obligation_id in (
        "SAL-XLIFF-CORE-ROUNDTRIP-SEMANTIC-001",
        "SAL-XLIFF-CORE-SECURITY-EXTERNAL-RESOLUTION-001",
        "SAL-XLIFF-CORE-SECURITY-RESOURCE-LIMITS-001",
        "SAL-XLIFF-CORE-WRITE-DETERMINISTIC-001",
    ):
        row = rows[obligation_id]
        assert row["obligation_basis"] == "PRODUCTION_POLICY"
        assert row["conformance_effect"] == "PRODUCTION_PROFILE_ONLY"
        assert all(
            location["location_kind"] == "policy_rule"
            and location["authority_source_id"].startswith("POLICY-")
            and len(location["source_sha256"]) == 64
            and len(location["source_text_sha256"]) == 64
            for location in row["authority_locations"]
        )


def test_batch_five_compiles_only_the_independently_adjudicated_obligation(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    target_language_id = (
        "SAL-XLIFF-CORE-DOCUMENT-TARGET-LANGUAGE-001"
    )
    with pytest.raises(
        extractor.ExtractionError,
        match="independently adjudicated",
    ):
        extractor._default_core_obligation_seeds(
            through_batch="XLF-04-BATCH-005"
        )

    seeds = extractor._default_core_obligation_seeds(
        through_batch="XLF-04-BATCH-005",
        verified_obligation_ids={target_language_id},
    )
    batch_five = [
        seed
        for seed in seeds
        if seed["introduced_in_batch"] == "XLF-04-BATCH-005"
    ]
    assert [seed["obligation_id"] for seed in batch_five] == [
        target_language_id
    ]

    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    policy_sources = extractor._default_core_policy_sources()
    denominator = extractor.compile_xliff_core_denominator(
        sources,
        policy_sources=policy_sources,
    )
    inventory = extractor.compile_xliff_core_obligations(
        sources,
        obligation_seeds=seeds,
        batch_id="XLF-04-BATCH-005",
        policy_sources=policy_sources,
        expected_obligation_inventory=denominator,
    )

    assert inventory["obligation_count"] == 26
    assert inventory["resolved_expected_obligation_count"] == 26
    assert inventory["complete"] is False
    rows = {row["obligation_id"]: row for row in inventory["obligations"]}
    target_language = rows[target_language_id]
    assert target_language["introduced_in_batch"] == "XLF-04-BATCH-005"
    assert target_language["category"] == "document_structure"
    assert target_language["stable_profiles"] == ["xliff_2.0", "xliff_2.1"]
    assert {
        location["profile"]
        for location in target_language["authority_locations"]
    } == {"xliff_2.0", "xliff_2.1"}
    assert all(
        location["section_id"] == "xliff"
        and len(location["source_text_sha256"]) == 64
        for location in target_language["authority_locations"]
    )


def test_open_core_denominator_is_independent_and_cannot_certify_completion(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    policy_sources = extractor._default_core_policy_sources()
    denominator = extractor.compile_xliff_core_denominator(
        sources,
        policy_sources=policy_sources,
    )

    assert denominator["schema"] == "ff6/xliff-core-obligation-denominator@1"
    assert denominator["status"] == "OPEN_AUTHORITY_CENSUS"
    assert denominator["inventory_complete"] is False
    assert denominator["expected_obligation_count"] >= 60
    assert set(denominator["covered_categories"]) == set(
        extractor._XLIFF_CORE_CATEGORIES
    )
    assert "SAL-XLIFF-CORE-DOCUMENT-VERSION-001" in {
        row["obligation_id"] for row in denominator["expectations"]
    }

    seeds = extractor._default_core_obligation_seeds(
        through_batch="XLF-04-BATCH-003"
    )
    omitted_id = "SAL-XLIFF-CORE-DOCUMENT-ROOT-001"
    incomplete = extractor.compile_xliff_core_obligations(
        sources,
        obligation_seeds=[
            seed for seed in seeds if seed["obligation_id"] != omitted_id
        ],
        batch_id="XLF-04-BATCH-003",
        policy_sources=policy_sources,
        expected_obligation_inventory=denominator,
    )

    assert omitted_id in incomplete["missing_expected_obligation_ids"]
    assert incomplete["completeness_basis"] == (
        "EXPLICIT_EXPECTED_OBLIGATION_IDS_OPEN_CENSUS"
    )
    assert incomplete["complete"] is False


def test_core_denominator_authority_input_tampering_fails_closed(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_obligation_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    policy_sources = extractor._default_core_policy_sources()
    denominator = extractor.compile_xliff_core_denominator(
        sources,
        policy_sources=policy_sources,
    )
    tampered = deepcopy(denominator)
    tampered["authority_inputs"][0]["source_sha256"] = "0" * 64

    with pytest.raises(
        extractor.ExtractionError,
        match="denominator authority input closure",
    ):
        extractor.compile_xliff_core_obligations(
            sources,
            obligation_seeds=extractor._default_core_obligation_seeds(),
            batch_id="XLF-04-BATCH-003",
            policy_sources=policy_sources,
            expected_obligation_inventory=tampered,
        )


def test_core_authority_candidate_census_compiler_exists() -> None:
    extractor = _load_module()

    assert hasattr(extractor, "compile_xliff_core_authority_census"), (
        "XLF-04-BATCH-004 requires a fail-closed authority-candidate census; "
        "the open expected-ID denominator alone cannot prove source coverage"
    )


def _write_core_census_archive(
    path: Path,
    *,
    profile: str,
) -> tuple[str, str]:
    version = profile.removeprefix("xliff_")
    prose_member = f"xliff-core-v{version}-os.xml"
    changed_requirement = (
        "Agents must preserve foreign namespace content."
        if profile == "xliff_2.1"
        else "Agents should preserve foreign namespace content."
    )
    profile_only = (
        '<section id="legacySkeleton"><title>Legacy skeleton</title>'
        "<para>Writers must preserve an existing skeleton reference.</para>"
        "</section>"
        if profile == "xliff_2.0"
        else '<section id="state"><title>State</title>'
        "<para>Writers must keep subState consistent with state.</para>"
        "</section>"
    )
    prose = (
        '<?xml version="1.0"?><article><section id="core">'
        "<title>Core</title>"
        "<para>Agents must preserve unknown Core elements.</para>"
        '<section id="extensions"><title>Extensions</title>'
        f"<para>{changed_requirement}</para>"
        "<itemizedlist><listitem><para>Agents must preserve custom "
        "attributes.</para></listitem></itemizedlist>"
        "</section>"
        f"{profile_only}"
        "</section></article>"
    ).encode()
    xsd = (
        '<?xml version="1.0"?>'
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" '
        'targetNamespace="urn:oasis:names:tc:xliff:document:2.0">'
        '<xs:import namespace="urn:example" schemaLocation="example.xsd"/>'
        '<xs:simpleType name="stateType"><xs:restriction base="xs:string">'
        '<xs:enumeration value="initial"/></xs:restriction></xs:simpleType>'
        '<xs:element name="xliff"><xs:complexType><xs:sequence>'
        '<xs:element name="file" minOccurs="1" maxOccurs="unbounded"/>'
        '</xs:sequence><xs:attribute name="version" type="xs:string" '
        'use="required"/><xs:anyAttribute processContents="lax"/>'
        "</xs:complexType></xs:element></xs:schema>"
    ).encode()
    schematron = (
        b'<schema xmlns="http://purl.oclc.org/dsdl/schematron">'
        b'<pattern><rule context="xlf:segment">'
        b'<assert test="not(@subState) or @state">subState requires state</assert>'
        b"</rule></pattern></schema>"
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(prose_member, prose)
        archive.writestr("schemas/xliff_core_2.0.xsd", xsd)
        if profile == "xliff_2.1":
            archive.writestr("schemas/xliff_core_2.1.sch", schematron)
    return prose_member, hashlib.sha256(path.read_bytes()).hexdigest()


def test_core_authority_census_extracts_reconciled_profile_delta(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_census_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    policy_sources = extractor._default_core_policy_sources()
    denominator = extractor.compile_xliff_core_denominator(
        sources,
        policy_sources=policy_sources,
    )

    census = extractor.compile_xliff_core_authority_census(
        sources,
        expected_obligation_inventory=denominator,
        policy_sources=policy_sources,
    )

    assert census["schema"] == "ff6/xliff-core-authority-census@2"
    assert census["candidate_scope_complete"] is True
    assert census["non_modal_prose_census_complete"] is True
    assert census["non_modal_prose_disposition_complete"] is True
    assert census["non_modal_prose_classification_verified"] is False
    assert census["disposition_verification_complete"] is False
    assert census["unverified_disposition_count"] == census["candidate_count"]
    assert census["normative_obligation_inventory_complete"] is False
    assert census["candidate_scope_definition"]["prose_selector"]
    assert census["candidate_scope_definition"]["non_modal_prose_selector"]
    assert census["candidate_scope_definition"]["xsd_node_kinds"]
    assert census["candidate_scope_definition"]["schematron_node_kinds"] == [
        "assert",
        "report",
    ]
    assert census["candidate_scope_limitations"]
    assert census["unmapped_candidate_count"] == 0
    assert census["multiply_dispositioned_candidate_count"] == 0
    candidates = census["candidates"]
    assert sum(census["disposition_precision_counts"].values()) == len(candidates)
    assert sum(
        sum(profile_counts.values())
        for profile_counts in census[
            "source_surface_occurrence_counts"
        ].values()
    ) == sum(len(row["occurrences"]) for row in candidates)
    assert len({row["candidate_id"] for row in candidates}) == len(candidates)
    assert {row["source_kind"] for row in candidates} == {
        "NORMATIVE_PROSE",
        "CORE_XSD",
        "CORE_SCHEMATRON",
    }
    relations = {row["profile_relation"] for row in candidates}
    assert {
        "COMMON_IDENTICAL",
        "COMMON_CHANGED",
        "REMOVED_IN_XLIFF_2_1",
        "ADDED_IN_XLIFF_2_1",
    } <= relations
    custom_attribute_occurrences = [
        occurrence
        for row in candidates
        for occurrence in row["occurrences"]
        if "preserve custom attributes"
        in occurrence["normalized_requirement"].casefold()
    ]
    assert len(custom_attribute_occurrences) == 2, (
        "the enclosing listitem and its normative para must not both become "
        "candidates"
    )
    expected_ids = {
        row["obligation_id"] for row in denominator["expectations"]
    }
    for row in candidates:
        assert len(row["occurrences"]) in {1, 2}
        assert row["candidate_class"] in extractor._CORE_CANDIDATE_CLASSES
        assert len(row["candidate_content_sha256"]) == 64
        assert all(
            len(occurrence["occurrence_sha256"]) == 64
            for occurrence in row["occurrences"]
        )
        disposition = row["disposition"]
        assert disposition["kind"] in {
            "MAP_EXPECTED_OBLIGATION",
            "NON_OBLIGATION",
        }
        assert disposition["rationale"]
        assert disposition["mapping_rule_ids"]
        assert disposition["mapping_precision"] in {
            "SEMANTIC_TOKEN_MAPPING_UNVERIFIED",
            "STRUCTURAL_CLASS_MAPPING_UNVERIFIED",
            "SEMANTIC_TOKEN_AND_STRUCTURAL_CLASS_MAPPING_UNVERIFIED",
            "REASONED_NON_OBLIGATION_UNVERIFIED",
        }
        if disposition["kind"] == "MAP_EXPECTED_OBLIGATION":
            assert set(disposition["obligation_ids"]) <= expected_ids
            assert disposition["obligation_ids"]
        else:
            assert disposition["reason_code"]
    generic_xsd = next(
        row
        for row in candidates
        if row["semantic_location"] == "xsd/import:1"
    )
    assert not {
        "SAL-XLIFF-CORE-INLINE-SC-001",
        "SAL-XLIFF-CORE-INLINE-EC-001",
        "SAL-XLIFF-CORE-INLINE-EM-001",
    } & set(generic_xsd["disposition"]["obligation_ids"]), (
        "short inline element names must be routed as semantic tokens, not "
        "as substrings of schema vocabulary"
    )


def test_core_authority_census_authority_replay_rejects_rehashed_content(
    tmp_path: Path,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_census_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    policy_sources = extractor._default_core_policy_sources()
    denominator = extractor.compile_xliff_core_denominator(
        sources,
        policy_sources=policy_sources,
    )
    tampered = extractor.compile_xliff_core_authority_census(
        sources,
        expected_obligation_inventory=denominator,
        policy_sources=policy_sources,
    )
    candidate = next(
        row
        for row in tampered["candidates"]
        if len(row["occurrences"]) == 1
        and row["source_kind"] in {"NORMATIVE_PROSE", "NON_MODAL_PROSE"}
    )
    occurrence = candidate["occurrences"][0]
    base_fields = {
        key: occurrence[key]
        for key in (
            "profile",
            "source_id",
            "source_sha256",
            "member",
            "member_sha256",
            "location",
            "candidate_class",
            "normalized_requirement",
        )
    }
    base_fields["normalized_requirement"] += " forged but rehashed"
    candidate["occurrences"][0] = extractor.bind_occurrence(base_fields)
    candidate["candidate_content_sha256"] = extractor.candidate_content_sha256(
        candidate
    )
    candidate["disposition"] = extractor._candidate_disposition(
        candidate,
        {
            row["obligation_id"]
            for row in denominator["expectations"]
        },
    )

    with pytest.raises(extractor.ExtractionError, match="authority replay"):
        extractor.validate_xliff_core_authority_census(
            tampered,
            expected_obligation_inventory=denominator,
            profile_sources=sources,
            policy_sources=policy_sources,
        )


def test_cli_writes_and_checks_core_authority_census(tmp_path: Path) -> None:
    extractor = _load_module()
    sources: dict[str, tuple[Path, str]] = {}
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        _member, digest = _write_core_census_archive(path, profile=profile)
        sources[profile] = (path, digest)
    denominator = tmp_path / "denominator.yaml"
    output = tmp_path / "census.yaml"
    common_args = [
        "--format-id",
        "xliff",
        "--source-20",
        str(sources["xliff_2.0"][0]),
        "--source-20-id",
        "SRC-XLF-001",
        "--source-20-sha256",
        sources["xliff_2.0"][1],
        "--source-21",
        str(sources["xliff_2.1"][0]),
        "--source-21-id",
        "SRC-XLF-002",
        "--source-21-sha256",
        sources["xliff_2.1"][1],
    ]
    assert extractor.main(
        [
            *common_args,
            "--artifact",
            "core-denominator",
            "--output",
            str(denominator),
        ]
    ) == 0
    args = [
        *common_args,
        "--artifact",
        "core-census",
        "--denominator",
        str(denominator),
        "--output",
        str(output),
    ]

    assert extractor.main(args) == 0
    first_bytes = output.read_bytes()
    artifact = yaml.safe_load(first_bytes)
    assert artifact["candidate_count"] > 0
    assert artifact["denominator_input_sha256"] == hashlib.sha256(
        denominator.read_bytes()
    ).hexdigest()
    assert extractor.main([*args, "--check"]) == 0
    assert output.read_bytes() == first_bytes


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("unmapped", "missing disposition"),
        ("duplicate_obligation", "duplicate obligation"),
        ("preview_profile", "invalid candidate profile"),
        ("multiply_dispositioned", "disposition must be a mapping"),
    ],
)
def test_core_authority_census_validation_fails_closed(
    tmp_path: Path,
    mutation: str,
    message: str,
) -> None:
    extractor = _load_module()
    sources = []
    for profile in ("xliff_2.0", "xliff_2.1"):
        path = tmp_path / f"{profile}.zip"
        member, digest = _write_core_census_archive(path, profile=profile)
        sources.append(
            extractor.ProfileSource(
                profile=profile,
                source_id=f"SRC-{profile.upper()}",
                package_path=path,
                expected_sha256=digest,
                prose_member=member,
            )
        )
    policy_sources = extractor._default_core_policy_sources()
    denominator = extractor.compile_xliff_core_denominator(
        sources,
        policy_sources=policy_sources,
    )
    census = extractor.compile_xliff_core_authority_census(
        sources,
        expected_obligation_inventory=denominator,
        policy_sources=policy_sources,
    )
    tampered = deepcopy(census)
    candidate = tampered["candidates"][0]
    if mutation == "unmapped":
        candidate.pop("disposition")
    elif mutation == "duplicate_obligation":
        obligation_id = candidate["disposition"]["obligation_ids"][0]
        candidate["disposition"]["obligation_ids"].append(obligation_id)
    elif mutation == "preview_profile":
        candidate["stable_profiles"] = ["xliff_2.2_preview"]
    else:
        candidate["disposition"] = [
            candidate["disposition"],
            deepcopy(candidate["disposition"]),
        ]

    with pytest.raises(extractor.ExtractionError, match=message):
        extractor.validate_xliff_core_authority_census(
            tampered,
            expected_obligation_inventory=denominator,
        )
