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
PACKAGE_PATH = (
    REPO_ROOT / ".local" / "format-contracts" / "acquired" / "ubl" / "src-ubl-002.bin"
)
PACKAGE_SHA256 = "623bef8310db4d979ff28000a96bcc56dbcdda4f6206cf094c0aa79b75817970"
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
    assert root["content_type_node_id"] in {node["node_id"] for node in graph["nodes"]}


def test_graph_closes_offline_dependencies_and_global_references() -> None:
    compiler = _load_compiler()
    invoice_namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    aggregate_namespace = "urn:test:common:aggregate"
    invoice = (
        f'<xsd:schema xmlns="{invoice_namespace}" xmlns:xsd="{XS}" '
        f'xmlns:cac="{aggregate_namespace}" '
        f'targetNamespace="{invoice_namespace}" '
        'elementFormDefault="qualified">'
        f'<xsd:import namespace="{aggregate_namespace}" '
        'schemaLocation="../common/CommonAggregate.xsd"/>'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:sequence>'
        '<xsd:element ref="cac:Party"/>'
        "</xsd:sequence></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    aggregate = (
        f'<xsd:schema xmlns="{aggregate_namespace}" xmlns:xsd="{XS}" '
        f'xmlns:cac="{aggregate_namespace}" '
        f'targetNamespace="{aggregate_namespace}" '
        'elementFormDefault="qualified">'
        '<xsd:include schemaLocation="CommonAggregateExtra.xsd"/>'
        '<xsd:element name="Party" type="PartyType"/>'
        '<xsd:complexType name="PartyType"><xsd:sequence>'
        '<xsd:element ref="cac:Name"/>'
        "</xsd:sequence></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    aggregate_extra = (
        f'<xsd:schema xmlns="{aggregate_namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{aggregate_namespace}" '
        'elementFormDefault="qualified">'
        '<xsd:element name="Name" type="xsd:string"/>'
        "</xsd:schema>"
    ).encode()
    package = _package(
        {
            "xsd/maindoc/UBL-Invoice-2.3.xsd": invoice,
            "xsd/common/CommonAggregate.xsd": aggregate,
            "xsd/common/CommonAggregateExtra.xsd": aggregate_extra,
        }
    )

    graph = compiler.compile_ubl_reachable_schema_graph(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )

    assert graph["schema_dependency_edge_count"] == 2
    assert graph["schema_dependency_edge_counts"] == {
        "schema_import": 1,
        "schema_include": 1,
    }
    closure = graph["schema_closures"][0]
    assert closure["root_member"] == "xsd/maindoc/UBL-Invoice-2.3.xsd"
    assert closure["reachable_members"] == [
        "xsd/common/CommonAggregate.xsd",
        "xsd/common/CommonAggregateExtra.xsd",
        "xsd/maindoc/UBL-Invoice-2.3.xsd",
    ]
    assert graph["global_reference_use_count"] == 5
    assert graph["validation"]["unresolved_reference_count"] == 0
    assert graph["validation"]["ambiguous_reference_count"] == 0
    references = {
        (row["attribute"], row["lexical_qname"], row["target_kind"])
        for row in graph["global_reference_uses"]
    }
    assert ("ref", "cac:Party", "global_element") in references
    assert ("ref", "cac:Name", "global_element") in references
    assert ("type", "xsd:string", "xsd_builtin_type") in references


def test_graph_retains_local_particle_order_occurrence_and_element_rules() -> None:
    compiler = _load_compiler()
    invoice_namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    aggregate_namespace = "urn:test:common:aggregate"
    invoice = (
        f'<xsd:schema xmlns="{invoice_namespace}" xmlns:xsd="{XS}" '
        f'xmlns:cac="{aggregate_namespace}" '
        f'targetNamespace="{invoice_namespace}" '
        'elementFormDefault="qualified">'
        f'<xsd:import namespace="{aggregate_namespace}" '
        'schemaLocation="../common/CommonAggregate.xsd"/>'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType">'
        '<xsd:sequence minOccurs="0" maxOccurs="2">'
        '<xsd:element name="ID" type="xsd:string" nillable="true" '
        'default="draft"/>'
        '<xsd:choice minOccurs="0" maxOccurs="unbounded">'
        '<xsd:element ref="cac:Party" minOccurs="0"/>'
        '<xsd:element name="Note" type="xsd:string" minOccurs="0" '
        'maxOccurs="2" fixed="locked" form="unqualified"/>'
        "</xsd:choice>"
        "</xsd:sequence>"
        "</xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    aggregate = (
        f'<xsd:schema xmlns="{aggregate_namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{aggregate_namespace}" '
        'elementFormDefault="qualified">'
        '<xsd:element name="Party" type="xsd:string"/>'
        "</xsd:schema>"
    ).encode()
    package = _package(
        {
            "xsd/maindoc/UBL-Invoice-2.3.xsd": invoice,
            "xsd/common/CommonAggregate.xsd": aggregate,
        }
    )

    graph = compiler.compile_ubl_reachable_schema_graph(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )

    assert graph["particle_count"] == 5
    assert graph["particle_kind_counts"] == {
        "choice": 1,
        "element": 3,
        "sequence": 1,
    }
    assert graph["particle_owner_count"] == 1
    owner = f"complex-type::{{{invoice_namespace}}}InvoiceType"
    assert {row["owner_node_id"] for row in graph["particles"]} == {owner}
    projection = [
        {
            key: row[key]
            for key in (
                "kind",
                "order_path",
                "min_occurs",
                "max_occurs",
                "name",
                "ref_qname",
                "type_qname",
                "nillable",
                "default",
                "fixed",
                "form",
            )
        }
        for row in graph["particles"]
    ]
    assert projection == [
        {
            "kind": "sequence",
            "order_path": [1],
            "min_occurs": 0,
            "max_occurs": 2,
            "name": "",
            "ref_qname": "",
            "type_qname": "",
            "nillable": False,
            "default": None,
            "fixed": None,
            "form": "",
        },
        {
            "kind": "element",
            "order_path": [1, 1],
            "min_occurs": 1,
            "max_occurs": 1,
            "name": "ID",
            "ref_qname": "",
            "type_qname": f"{{{XS}}}string",
            "nillable": True,
            "default": "draft",
            "fixed": None,
            "form": "qualified",
        },
        {
            "kind": "choice",
            "order_path": [1, 2],
            "min_occurs": 0,
            "max_occurs": "unbounded",
            "name": "",
            "ref_qname": "",
            "type_qname": "",
            "nillable": False,
            "default": None,
            "fixed": None,
            "form": "",
        },
        {
            "kind": "element",
            "order_path": [1, 2, 1],
            "min_occurs": 0,
            "max_occurs": 1,
            "name": "",
            "ref_qname": f"{{{aggregate_namespace}}}Party",
            "type_qname": "",
            "nillable": False,
            "default": None,
            "fixed": None,
            "form": "",
        },
        {
            "kind": "element",
            "order_path": [1, 2, 2],
            "min_occurs": 0,
            "max_occurs": 2,
            "name": "Note",
            "ref_qname": "",
            "type_qname": f"{{{XS}}}string",
            "nillable": False,
            "default": None,
            "fixed": "locked",
            "form": "unqualified",
        },
    ]
    assert len({row["particle_id"] for row in graph["particles"]}) == 5
    assert graph["particle_identity"]["particles_sha256"]
    assert graph["completion"]["reachable_schema_graph_complete"] is False


@pytest.mark.parametrize(
    "all_body",
    [
        '<xsd:all maxOccurs="2"><xsd:element name="ID"/></xsd:all>',
        '<xsd:all><xsd:element name="ID" maxOccurs="2"/></xsd:all>',
        (
            "<xsd:all><xsd:choice>"
            '<xsd:element name="ID"/>'
            "</xsd:choice></xsd:all>"
        ),
    ],
)
def test_graph_rejects_invalid_all_group_particle_rules(all_body: str) -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}" elementFormDefault="qualified">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType">'
        f"{all_body}"
        "</xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    with pytest.raises(
        compiler.UblCensusError,
        match="all compositor",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


@pytest.mark.parametrize(
    "prohibited_attribute",
    ['nillable="true"', 'default="unsafe"', 'fixed="unsafe"'],
)
def test_graph_rejects_declaration_attributes_on_element_reference(
    prohibited_attribute: str,
) -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    common_namespace = "urn:test:common"
    invoice = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'xmlns:cac="{common_namespace}" targetNamespace="{namespace}">'
        f'<xsd:import namespace="{common_namespace}" '
        'schemaLocation="../common/Common.xsd"/>'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:sequence>'
        f'<xsd:element ref="cac:Party" {prohibited_attribute}/>'
        "</xsd:sequence></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    common = (
        f'<xsd:schema xmlns="{common_namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{common_namespace}">'
        '<xsd:element name="Party" type="xsd:string"/>'
        "</xsd:schema>"
    ).encode()
    package = _package(
        {
            "xsd/maindoc/UBL-Invoice-2.3.xsd": invoice,
            "xsd/common/Common.xsd": common,
        }
    )

    with pytest.raises(
        compiler.UblCensusError,
        match="referenced local element carries prohibited attributes",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


def test_graph_rejects_reference_visible_only_through_transitive_import() -> None:
    compiler = _load_compiler()
    namespace_a = "urn:test:a"
    namespace_b = "urn:test:b"
    namespace_c = "urn:test:c"
    schema_a = (
        f'<xsd:schema xmlns="{namespace_a}" xmlns:xsd="{XS}" '
        f'xmlns:c="{namespace_c}" targetNamespace="{namespace_a}">'
        f'<xsd:import namespace="{namespace_b}" '
        'schemaLocation="../common/B.xsd"/>'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:sequence>'
        '<xsd:element ref="c:Thing"/>'
        "</xsd:sequence></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    schema_b = (
        f'<xsd:schema xmlns="{namespace_b}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace_b}">'
        f'<xsd:import namespace="{namespace_c}" schemaLocation="C.xsd"/>'
        '<xsd:complexType name="BType"/>'
        "</xsd:schema>"
    ).encode()
    schema_c = (
        f'<xsd:schema xmlns="{namespace_c}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace_c}">'
        '<xsd:element name="Thing" type="xsd:string"/>'
        "</xsd:schema>"
    ).encode()
    package = _package(
        {
            "xsd/maindoc/UBL-Invoice-2.3.xsd": schema_a,
            "xsd/common/B.xsd": schema_b,
            "xsd/common/C.xsd": schema_c,
        }
    )

    with pytest.raises(
        compiler.UblCensusError,
        match="outside direct import/include visibility",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


def test_graph_rejects_duplicate_schema_dependency_identity() -> None:
    compiler = _load_compiler()
    invoice_namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    common_namespace = "urn:test:common"
    invoice = (
        f'<xsd:schema xmlns="{invoice_namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{invoice_namespace}">'
        f'<xsd:import namespace="{common_namespace}" '
        'schemaLocation="../common/Common.xsd"/>'
        f'<xsd:import namespace="{common_namespace}" '
        'schemaLocation="../common/Common.xsd"/>'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"/>'
        "</xsd:schema>"
    ).encode()
    common = (
        f'<xsd:schema xmlns="{common_namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{common_namespace}">'
        '<xsd:simpleType name="CodeType">'
        '<xsd:restriction base="xsd:string"/>'
        "</xsd:simpleType></xsd:schema>"
    ).encode()
    package = _package(
        {
            "xsd/maindoc/UBL-Invoice-2.3.xsd": invoice,
            "xsd/common/Common.xsd": common,
        }
    )

    with pytest.raises(
        compiler.UblCensusError,
        match="duplicate schema dependency",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


def test_real_package_closure_is_complete_deterministic_and_additive() -> None:
    compiler = _load_compiler()

    first = compiler.compile_ubl_reachable_schema_graph(
        PACKAGE_PATH,
        expected_package_sha256=PACKAGE_SHA256,
    )
    second = compiler.compile_ubl_reachable_schema_graph(
        PACKAGE_PATH,
        expected_package_sha256=PACKAGE_SHA256,
    )
    third = compiler.compile_ubl_reachable_schema_graph(
        PACKAGE_PATH,
        expected_package_sha256=PACKAGE_SHA256,
    )

    assert first == second == third
    assert first["schema_document_count"] == 106
    assert first["root_count"] == 91
    assert first["schema_dependency_edge_count"] == 297
    assert first["schema_dependency_edge_counts"] == {
        "schema_import": 295,
        "schema_include": 2,
    }
    assert first["global_component_count"] == 3_788
    assert first["global_reference_use_count"] == 8_926
    assert first["global_reference_attribute_counts"] == {
        "base": 1_178,
        "ref": 5_383,
        "type": 2_365,
    }
    assert first["global_reference_target_counts"] == {
        "complex_type": 3_347,
        "global_element": 5_383,
        "simple_type": 21,
        "xsd_builtin_type": 175,
    }
    assert (
        first["identity"]["graph_sha256"]
        == "7b754187690ce1bb04db62657cfb552653cb381a1bdd745a56856e58215af029"
    )
    assert (
        first["closure_identity"]["closure_sha256"]
        == "2e43a3e83b1ad96ce287299cd7e7c6d86a4a4a02cc3423d30e18f0c9b4ee9fc3"
    )
    assert (
        len({edge["edge_id"] for edge in first["schema_dependency_edges"]})
        == first["schema_dependency_edge_count"]
    )
    assert (
        len({row["use_id"] for row in first["global_reference_uses"]})
        == first["global_reference_use_count"]
    )
    namespace_imports = [
        edge
        for edge in first["schema_dependency_edges"]
        if edge["resolution_mode"] == "namespace_family"
    ]
    assert namespace_imports == [
        {
            **namespace_imports[0],
            "kind": "schema_import",
            "source_member": "xsd/common/UBL-xmldsig11-schema-2.3.xsd",
            "schema_location": "",
            "declared_namespace": "http://www.w3.org/2000/09/xmldsig#",
            "target_members": [
                "xsd/common/UBL-xmldsig-core-schema-2.3.xsd",
                "xsd/common/UBL-xmldsig1-schema-2.3.xsd",
            ],
        }
    ]
    assert first["completion"]["reachable_schema_graph_complete"] is False


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
    commented_package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": commented})

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
