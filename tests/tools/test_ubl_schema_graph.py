"""Production controls for the reachable UBL 2.3 XML Schema graph."""

# generated_by: codex

from __future__ import annotations

import hashlib
import importlib.util
from io import BytesIO
from pathlib import Path
from types import ModuleType
from zipfile import ZIP_DEFLATED, ZipFile

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPILER_PATH = REPO_ROOT / "tools" / "spec" / "compile_ubl_schema_graph.py"
XS = "http://www.w3.org/2001/XMLSchema"


def _load_compiler() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "compile_ubl_schema_graph_graph_under_test",
        COMPILER_PATH,
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _package(rows: dict[str, bytes]) -> bytes:
    stream = BytesIO()
    with ZipFile(stream, "w", compression=ZIP_DEFLATED) as archive:
        for name, payload in sorted(rows.items()):
            archive.writestr(name, payload)
    return stream.getvalue()


def test_graph_resolves_a_document_root_to_exactly_one_declared_type() -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}" elementFormDefault="qualified">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:sequence/></xsd:complexType>'
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    graph = compiler.compile_ubl_reachable_schema_graph(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )

    assert graph["schema"] == "ff6/ubl-reachable-schema-graph@1"
    assert graph["root_count"] == 1
    assert graph["validation"]["unresolved_reference_count"] == 0
    assert graph["validation"]["ambiguous_reference_count"] == 0
    root = graph["roots"][0]
    assert root["root_qname"] == f"{{{namespace}}}Invoice"
    assert root["content_type_qname"] == f"{{{namespace}}}InvoiceType"
    assert root["content_type_node_id"] in {
        node["node_id"] for node in graph["nodes"]
    }


def test_xml_declaration_guard_ignores_comments_but_rejects_active_doctype() -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema_body = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"/>'
        "</xsd:schema>"
    )
    commented = (
        "<!-- removed upstream declaration: <!DOCTYPE schema> -->" + schema_body
    ).encode()
    commented_package = _package(
        {"xsd/maindoc/UBL-Invoice-2.3.xsd": commented}
    )

    graph = compiler.compile_ubl_reachable_schema_graph(
        commented_package,
        expected_package_sha256=hashlib.sha256(commented_package).hexdigest(),
        expected_root_count=1,
    )
    assert graph["root_count"] == 1

    active = ("<!DOCTYPE schema>" + schema_body).encode()
    active_package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": active})
    with pytest.raises(compiler.UblCensusError, match="DOCTYPE"):
        compiler.compile_ubl_reachable_schema_graph(
            active_package,
            expected_package_sha256=hashlib.sha256(active_package).hexdigest(),
            expected_root_count=1,
        )
