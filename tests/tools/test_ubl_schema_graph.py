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


def test_graph_assigns_stable_path_owned_anonymous_type_identities() -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}" elementFormDefault="qualified">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:sequence>'
        '<xsd:element name="Detail"><xsd:complexType>'
        '<xsd:sequence><xsd:element name="Value" type="xsd:string"/>'
        "</xsd:sequence>"
        '<xsd:attribute name="code"><xsd:simpleType>'
        '<xsd:restriction base="xsd:string"/>'
        "</xsd:simpleType></xsd:attribute>"
        "</xsd:complexType></xsd:element>"
        "</xsd:sequence></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    first = compiler.compile_ubl_reachable_schema_graph(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )
    second = compiler.compile_ubl_reachable_schema_graph(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )

    assert first["anonymous_type_count"] == 2
    assert first["anonymous_type_kind_counts"] == {
        "anonymous_complex_type": 1,
        "anonymous_simple_type": 1,
    }
    assert first["anonymous_type_edge_count"] == 2
    assert first["anonymous_types"] == second["anonymous_types"]
    assert first["anonymous_type_edges"] == second["anonymous_type_edges"]
    by_kind = {row["kind"]: row for row in first["anonymous_types"]}
    complex_type = by_kind["anonymous_complex_type"]
    simple_type = by_kind["anonymous_simple_type"]
    assert complex_type["source_path"] == (
        "/schema[1]/complexType[1]/sequence[1]/element[1]/complexType[1]"
    )
    assert complex_type["owner_kind"] == "local_element"
    assert complex_type["owner_node_id"].startswith("particle::")
    assert complex_type["enclosing_type_node_id"] == (
        f"complex-type::{{{namespace}}}InvoiceType"
    )
    assert simple_type["source_path"] == (
        "/schema[1]/complexType[1]/sequence[1]/element[1]/complexType[1]"
        "/attribute[1]/simpleType[1]"
    )
    assert simple_type["owner_kind"] == "local_attribute"
    assert simple_type["owner_node_id"].startswith("schema-declaration::")
    assert simple_type["enclosing_type_node_id"] == complex_type["node_id"]
    assert len({row["node_id"] for row in first["anonymous_types"]}) == 2
    assert first["anonymous_type_identity"]["anonymous_type_graph_sha256"]
    assert first["completion"]["reachable_schema_graph_complete"] is False


def test_graph_compiles_exact_derivation_and_inheritance_edges() -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}" elementFormDefault="qualified">'
        '<xsd:element name="Invoice" type="ExtendedComplex"/>'
        '<xsd:complexType name="BaseComplex"><xsd:sequence>'
        '<xsd:element name="ID" type="xsd:string" minOccurs="0"/>'
        "</xsd:sequence></xsd:complexType>"
        '<xsd:complexType name="ExtendedComplex"><xsd:complexContent>'
        '<xsd:extension base="BaseComplex"><xsd:sequence>'
        '<xsd:element name="Note" type="xsd:string" minOccurs="0"/>'
        "</xsd:sequence></xsd:extension>"
        "</xsd:complexContent></xsd:complexType>"
        '<xsd:complexType name="RestrictedComplex"><xsd:complexContent>'
        '<xsd:restriction base="BaseComplex"><xsd:sequence>'
        '<xsd:element name="ID" type="xsd:string" minOccurs="0"/>'
        "</xsd:sequence></xsd:restriction>"
        "</xsd:complexContent></xsd:complexType>"
        '<xsd:simpleType name="BaseSimple">'
        '<xsd:restriction base="xsd:string"/>'
        "</xsd:simpleType>"
        '<xsd:simpleType name="RestrictedSimple">'
        '<xsd:restriction base="BaseSimple"/>'
        "</xsd:simpleType>"
        '<xsd:complexType name="SimpleExtension"><xsd:simpleContent>'
        '<xsd:extension base="BaseSimple"/>'
        "</xsd:simpleContent></xsd:complexType>"
        '<xsd:complexType name="SimpleRestriction"><xsd:simpleContent>'
        '<xsd:restriction base="BaseSimple"/>'
        "</xsd:simpleContent></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    first = compiler.compile_ubl_reachable_schema_graph(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )
    second = compiler.compile_ubl_reachable_schema_graph(
        package,
        expected_package_sha256=hashlib.sha256(package).hexdigest(),
        expected_root_count=1,
    )

    assert first["derivation_edge_count"] == 6
    assert first["derivation_edge_counts"] == {
        "complex_content_extension": 1,
        "complex_content_restriction": 1,
        "simple_content_extension": 1,
        "simple_content_restriction": 1,
        "simple_type_restriction": 2,
    }
    assert first["derivation_edges"] == second["derivation_edges"]
    projection = {
        (
            row["kind"],
            row["source_node_id"],
            row["target_node_id"],
            row["lexical_base"],
        )
        for row in first["derivation_edges"]
    }
    assert projection == {
        (
            "complex_content_extension",
            f"complex-type::{{{namespace}}}ExtendedComplex",
            f"complex-type::{{{namespace}}}BaseComplex",
            "BaseComplex",
        ),
        (
            "complex_content_restriction",
            f"complex-type::{{{namespace}}}RestrictedComplex",
            f"complex-type::{{{namespace}}}BaseComplex",
            "BaseComplex",
        ),
        (
            "simple_content_extension",
            f"complex-type::{{{namespace}}}SimpleExtension",
            f"simple-type::{{{namespace}}}BaseSimple",
            "BaseSimple",
        ),
        (
            "simple_content_restriction",
            f"complex-type::{{{namespace}}}SimpleRestriction",
            f"simple-type::{{{namespace}}}BaseSimple",
            "BaseSimple",
        ),
        (
            "simple_type_restriction",
            f"simple-type::{{{namespace}}}BaseSimple",
            f"xsd-builtin-type::{{{XS}}}string",
            "xsd:string",
        ),
        (
            "simple_type_restriction",
            f"simple-type::{{{namespace}}}RestrictedSimple",
            f"simple-type::{{{namespace}}}BaseSimple",
            "BaseSimple",
        ),
    }
    assert len({row["edge_id"] for row in first["derivation_edges"]}) == 6
    assert first["derivation_identity"]["derivation_graph_sha256"]
    assert first["completion"]["reachable_schema_graph_complete"] is False


def test_graph_rejects_complex_content_with_simple_builtin_base() -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:complexContent>'
        '<xsd:extension base="xsd:string"/>'
        "</xsd:complexContent></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    with pytest.raises(
        compiler.UblCensusError,
        match="complex content has non-complex base",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


@pytest.mark.parametrize("method", ["extension", "restriction"])
def test_graph_rejects_content_derivation_without_base(method: str) -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:complexContent>'
        f"<xsd:{method}/>"
        "</xsd:complexContent></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    with pytest.raises(
        compiler.UblCensusError,
        match="derivation base must resolve exactly once",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


def test_graph_rejects_declared_and_anonymous_type_on_one_element() -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:sequence>'
        '<xsd:element name="Detail" type="xsd:string">'
        "<xsd:complexType/>"
        "</xsd:element>"
        "</xsd:sequence></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    with pytest.raises(
        compiler.UblCensusError,
        match="cannot combine type with an anonymous type",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


def test_graph_rejects_multiple_anonymous_types_on_one_declaration() -> None:
    compiler = _load_compiler()
    namespace = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
    schema = (
        f'<xsd:schema xmlns="{namespace}" xmlns:xsd="{XS}" '
        f'targetNamespace="{namespace}">'
        '<xsd:element name="Invoice" type="InvoiceType"/>'
        '<xsd:complexType name="InvoiceType"><xsd:sequence>'
        '<xsd:element name="Detail">'
        "<xsd:complexType/>"
        '<xsd:simpleType><xsd:restriction base="xsd:string"/></xsd:simpleType>'
        "</xsd:element>"
        "</xsd:sequence></xsd:complexType>"
        "</xsd:schema>"
    ).encode()
    package = _package({"xsd/maindoc/UBL-Invoice-2.3.xsd": schema})

    with pytest.raises(
        compiler.UblCensusError,
        match="multiple anonymous types",
    ):
        compiler.compile_ubl_reachable_schema_graph(
            package,
            expected_package_sha256=hashlib.sha256(package).hexdigest(),
            expected_root_count=1,
        )


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
    assert first["anonymous_type_count"] == 0
    assert first["anonymous_type_kind_counts"] == {}
    assert first["anonymous_type_owner_count"] == 0
    assert first["anonymous_type_edge_count"] == 0
    assert (
        first["anonymous_type_identity"]["anonymous_type_graph_sha256"]
        == "666634cb0d90f17b05e0b9fd4babe13fe5087f253ef2afb276bf6066d82eaf6e"
    )
    assert first["derivation_edge_count"] == 1_178
    assert first["derivation_edge_counts"] == {
        "complex_content_extension": 2,
        "complex_content_restriction": 2,
        "simple_content_extension": 36,
        "simple_content_restriction": 1_133,
        "simple_type_restriction": 5,
    }
    assert (
        first["derivation_identity"]["derivation_graph_sha256"]
        == "783506c4dcccaefbeb94960dcb5e6d7e0c54a6d8487ee1746eca082535b60e9f"
    )
    assert (
        len({row["edge_id"] for row in first["derivation_edges"]})
        == first["derivation_edge_count"]
    )
    reference_use_ids = {
        row["use_id"] for row in first["global_reference_uses"]
    }
    assert {
        row["reference_use_id"] for row in first["derivation_edges"]
    } <= reference_use_ids
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
