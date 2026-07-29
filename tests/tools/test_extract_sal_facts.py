"""Tests for the authority-bound SAL specification extractor."""

# generated_by: codex

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType
import zipfile

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "spec" / "extract_sal_facts.py"


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
