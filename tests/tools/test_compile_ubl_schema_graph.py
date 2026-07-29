"""Production controls for the UBL 2.3 authority package/root census."""

# generated_by: codex

from __future__ import annotations

import hashlib
import importlib.util
from collections.abc import Sequence
from io import BytesIO
from pathlib import Path
import stat
from types import ModuleType
from typing import Any, cast
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "spec" / "compile_ubl_schema_graph.py"
PACKAGE_PATH = (
    REPO_ROOT
    / ".local"
    / "format-contracts"
    / "acquired"
    / "ubl"
    / "src-ubl-002.bin"
)
PACKAGE_SHA256 = (
    "623bef8310db4d979ff28000a96bcc56dbcdda4f6206cf094c0aa79b75817970"
)
XS = "http://www.w3.org/2001/XMLSchema"


def _load_module() -> ModuleType:
    assert MODULE_PATH.is_file(), "UBL authority census compiler is not implemented"
    spec = importlib.util.spec_from_file_location(
        "compile_ubl_schema_graph_under_test",
        MODULE_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _root_schema(
    name: str,
    *,
    target_namespace: str | None = None,
    declared_type: bool = True,
    imports: tuple[str, ...] = (),
) -> bytes:
    namespace = (
        target_namespace
        or f"urn:oasis:names:specification:ubl:schema:xsd:{name}-2"
    )
    import_rows = "".join(
        (
            '<xs:import namespace="urn:test:common" '
            f'schemaLocation="{location}"/>'
        )
        for location in imports
    )
    type_row = (
        f'<xs:complexType name="{name}Type"><xs:sequence/></xs:complexType>'
        if declared_type
        else ""
    )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<xs:schema xmlns:xs="{XS}" '
        f'targetNamespace="{namespace}" elementFormDefault="qualified">'
        f"{import_rows}"
        f'<xs:element name="{name}" type="{name}Type"/>'
        f"{type_row}"
        f"</xs:schema>"
    ).encode()


def _zip_bytes(rows: Sequence[tuple[str | ZipInfo, bytes]]) -> bytes:
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in rows:
            archive.writestr(name, content)
    return stream.getvalue()


def _compile_fixture(
    module: ModuleType,
    rows: Sequence[tuple[str | ZipInfo, bytes]],
    *,
    expected_root_count: int = 1,
    limits: Any = None,
) -> dict[str, Any]:
    package = _zip_bytes(rows)
    return cast(
        dict[str, Any],
        module.compile_ubl_package_census(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=expected_root_count,
            limits=limits,
        ),
    )


def test_real_ubl_package_has_exact_authority_bound_root_denominator() -> None:
    compiler = _load_module()

    census = compiler.compile_ubl_package_census(
        PACKAGE_PATH,
        expected_package_sha256=PACKAGE_SHA256,
        expected_root_count=91,
    )

    assert census["schema"] == "ff6/ubl-package-root-census@1"
    assert census["authority"]["source_id"] == "SRC-UBL-002"
    assert census["authority"]["package_sha256"] == PACKAGE_SHA256
    assert census["authority"]["authority_class"] == "UBL_STANDARD_PACKAGE"
    assert census["member_count"] == 890
    assert len(census["members"]) == 890
    assert census["root_count"] == 91
    assert len(census["roots"]) == 91
    assert census["root_qname_count"] == 91
    assert (
        census["root_member_names_sha256"]
        == "f9ab3f16a0ac89dbcd42f4e93d1eb5e59a4709bc7d151aedd8b2577c3fc114a2"
    )
    assert census["duplicate_member_count"] == 0
    assert census["unsafe_member_count"] == 0
    assert census["remote_import_count"] == 0
    assert census["unresolved_import_count"] == 0
    assert census["root_validation"]["missing_declared_type_count"] == 0
    assert census["root_validation"]["duplicate_qname_count"] == 0
    assert census["role_counts"]["MAINDOC_XSD"] == 91
    assert census["role_counts"]["COMMON_XSD"] == 15
    assert census["role_counts"]["OFFICIAL_EXAMPLE"] == 76
    assert census["role_counts"]["CODE_LIST_RESOURCE"] == 14
    assert census["package_members_sha256"]

    qnames = {root["root_qname"] for root in census["roots"]}
    assert len(qnames) == 91
    for root in census["roots"]:
        assert root["schema_member"].startswith("xsd/maindoc/UBL-")
        assert root["schema_member"].endswith("-2.3.xsd")
        assert root["root_name"]
        assert root["root_qname"].startswith("{urn:oasis:names:specification:ubl:")
        assert root["content_type"]
        assert root["content_type_declared_in"] == root["schema_member"]
        assert root["imports"]
        assert all(edge["resolved_member"] for edge in root["imports"])

    reparsed = yaml.safe_load(compiler.canonical_yaml_bytes(census))
    assert reparsed == census
    assert (
        compiler.canonical_yaml_bytes(census)
        == compiler.canonical_yaml_bytes(
            compiler.compile_ubl_package_census(
                PACKAGE_PATH,
                expected_package_sha256=PACKAGE_SHA256,
                expected_root_count=91,
            )
        )
    )


def test_census_write_and_check_are_content_sensitive(tmp_path: Path) -> None:
    compiler = _load_module()
    package = _zip_bytes(
        [("xsd/maindoc/UBL-Invoice-2.3.xsd", _root_schema("Invoice"))]
    )
    census = compiler.compile_ubl_package_census(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )
    output = tmp_path / "census.yaml"

    compiler.write_census_atomic(census, output)
    compiler.check_census_file(census, output)
    first = output.read_bytes()
    compiler.write_census_atomic(census, output)
    assert output.read_bytes() == first

    output.write_bytes(first + b"# forged\n")
    with pytest.raises(compiler.UblCensusError, match="stale|differ"):
        compiler.check_census_file(census, output)


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        (
            [
                ("../escape.xsd", b"<xs:schema/>"),
                (
                    "xsd/maindoc/UBL-Invoice-2.3.xsd",
                    _root_schema("Invoice"),
                ),
            ],
            "unsafe",
        ),
        (
            [
                (
                    "xsd/maindoc/UBL-Invoice-2.3.xsd",
                    _root_schema(
                        "Invoice",
                        imports=("https://example.invalid/common.xsd",),
                    ),
                )
            ],
            "remote import",
        ),
        (
            [
                (
                    "xsd/maindoc/UBL-Invoice-2.3.xsd",
                    _root_schema("Invoice", imports=("../common/missing.xsd",)),
                )
            ],
            "unresolved import",
        ),
        (
            [
                (
                    "xsd/maindoc/UBL-Invoice-2.3.xsd",
                    _root_schema("Invoice", declared_type=False),
                )
            ],
            "declared type",
        ),
        (
            [
                (
                    "xsd/maindoc/UBL-Invoice-2.3.xsd",
                    b'<!DOCTYPE xs:schema [<!ENTITY x "unsafe">]>'
                    + _root_schema("Invoice"),
                )
            ],
            "DOCTYPE|entity",
        ),
    ],
)
def test_census_rejects_unsafe_or_incomplete_authority_packages(
    rows: list[tuple[str | ZipInfo, bytes]],
    message: str,
) -> None:
    compiler = _load_module()

    with pytest.raises(compiler.UblCensusError, match=message):
        _compile_fixture(compiler, rows)


def test_census_rejects_duplicate_members() -> None:
    compiler = _load_module()
    member = "xsd/maindoc/UBL-Invoice-2.3.xsd"

    with pytest.warns(UserWarning, match="Duplicate name"):
        package = _zip_bytes(
            [
                (member, _root_schema("Invoice")),
                (member, _root_schema("Invoice")),
            ]
        )
    with pytest.raises(compiler.UblCensusError, match="duplicate"):
        compiler.compile_ubl_package_census(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


def test_census_rejects_symlink_member() -> None:
    compiler = _load_module()
    link = ZipInfo("xsd/common/link.xsd")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16

    with pytest.raises(compiler.UblCensusError, match="symlink"):
        _compile_fixture(
            compiler,
            [
                (link, b"target"),
                (
                    "xsd/maindoc/UBL-Invoice-2.3.xsd",
                    _root_schema("Invoice"),
                ),
            ],
        )


def test_census_rejects_duplicate_root_qname_and_wrong_denominator() -> None:
    compiler = _load_module()
    duplicate_namespace = (
        "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    )
    rows = [
        (
            "xsd/maindoc/UBL-Invoice-2.3.xsd",
            _root_schema("Invoice", target_namespace=duplicate_namespace),
        ),
        (
            "xsd/maindoc/UBL-Order-2.3.xsd",
            _root_schema("Invoice", target_namespace=duplicate_namespace),
        ),
    ]

    # With filename/root-name coherence enabled, the second claimant is
    # rejected even earlier than the aggregate duplicate-QName check.
    with pytest.raises(
        compiler.UblCensusError,
        match="duplicate root QName|root element name contradicts",
    ):
        _compile_fixture(compiler, rows, expected_root_count=2)
    with pytest.raises(compiler.UblCensusError, match="expected 2.*found 1"):
        _compile_fixture(
            compiler,
            [
                (
                    "xsd/maindoc/UBL-Invoice-2.3.xsd",
                    _root_schema("Invoice"),
                )
            ],
            expected_root_count=2,
        )


def test_census_enforces_member_and_total_resource_limits() -> None:
    compiler = _load_module()
    rows = [
        (
            "xsd/maindoc/UBL-Invoice-2.3.xsd",
            _root_schema("Invoice"),
        )
    ]

    with pytest.raises(compiler.UblCensusError, match="member.*limit"):
        _compile_fixture(
            compiler,
            rows,
            limits=compiler.CensusLimits(max_member_uncompressed_bytes=32),
        )
    with pytest.raises(compiler.UblCensusError, match="total.*limit"):
        _compile_fixture(
            compiler,
            rows,
            limits=compiler.CensusLimits(max_total_uncompressed_bytes=32),
        )


def test_census_rejects_wrong_package_digest_before_parsing() -> None:
    compiler = _load_module()
    package = _zip_bytes(
        [("xsd/maindoc/UBL-Invoice-2.3.xsd", _root_schema("Invoice"))]
    )

    with pytest.raises(compiler.UblCensusError, match="package digest"):
        compiler.compile_ubl_package_census(
            package,
            expected_package_sha256="0" * 64,
            expected_root_count=1,
        )
