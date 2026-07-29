"""Deterministic UBL 2.3 XML Schema component graph primitives.

The module consumes already security-checked package members. Archive security
and authority-digest validation remain in ``compile_ubl_schema_graph.py`` so
the schema graph cannot acquire bytes through a second path.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
from io import BytesIO
import json
import re
from typing import Any, cast
import xml.etree.ElementTree as ET


XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
XSD = f"{{{XSD_NAMESPACE}}}"
_FORBIDDEN_XML_DECLARATIONS = re.compile(br"<!\s*(?:DOCTYPE|ENTITY)\b", re.I)
_XML_COMMENT = re.compile(br"<!--.*?-->", re.S)
_MAINDOC = re.compile(r"^xsd/maindoc/UBL-(?P<name>[A-Za-z0-9]+)-2\.3\.xsd$")


class UblSchemaGraphError(ValueError):
    """Raised when XSD bytes cannot produce one exact component graph."""


@dataclass(frozen=True)
class GraphLimits:
    """Independent resource limits for graph compilation."""

    max_schema_documents: int = 1_000
    max_graph_nodes: int = 100_000
    max_graph_edges: int = 250_000
    max_documentation_bytes: int = 67_108_864

    def __post_init__(self) -> None:
        for name in (
            "max_schema_documents",
            "max_graph_nodes",
            "max_graph_edges",
            "max_documentation_bytes",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise UblSchemaGraphError(f"{name} must be a positive integer")

    def as_dict(self) -> dict[str, int]:
        """Return stable public limit values."""

        return {
            "max_schema_documents": self.max_schema_documents,
            "max_graph_nodes": self.max_graph_nodes,
            "max_graph_edges": self.max_graph_edges,
            "max_documentation_bytes": self.max_documentation_bytes,
        }


@dataclass(frozen=True)
class SchemaDocument:
    """Parsed schema plus the namespace declarations needed for QName values."""

    member: str
    member_sha256: str
    target_namespace: str
    element_form_default: str
    attribute_form_default: str
    namespaces: Mapping[str, str]
    root: ET.Element


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_json_bytes(value)).hexdigest()


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _canonical_qname(namespace: str, local_name: str) -> str:
    if not local_name:
        raise UblSchemaGraphError("QName local name is empty")
    return f"{{{namespace}}}{local_name}"


def _parse_schema(member: str, payload: bytes) -> SchemaDocument:
    declaration_surface = _XML_COMMENT.sub(b"", payload)
    if _FORBIDDEN_XML_DECLARATIONS.search(declaration_surface):
        raise UblSchemaGraphError(
            f"DOCTYPE or entity declaration prohibited: {member}"
        )
    namespaces: dict[str, str] = {}
    root: ET.Element | None = None
    try:
        parser = ET.iterparse(BytesIO(payload), events=("start-ns", "start"))
        for event, value in parser:
            if event == "start-ns":
                prefix, namespace = cast(tuple[str, str], value)
                normalized_prefix = prefix or ""
                previous = namespaces.get(normalized_prefix)
                if previous is not None and previous != namespace:
                    raise UblSchemaGraphError(
                        f"namespace prefix rebound in {member}: "
                        f"{normalized_prefix!r}"
                    )
                namespaces[normalized_prefix] = namespace
            elif root is None:
                root = cast(ET.Element, value)
    except ET.ParseError as exc:
        raise UblSchemaGraphError(f"invalid XSD XML: {member}") from exc
    if root is None:
        raise UblSchemaGraphError(f"empty XSD XML: {member}")
    if root.tag != f"{XSD}schema":
        raise UblSchemaGraphError(
            f"member is not an XML Schema document: {member}"
        )
    target_namespace = root.get("targetNamespace")
    if not target_namespace:
        raise UblSchemaGraphError(f"schema lacks target namespace: {member}")
    namespaces.setdefault("xml", "http://www.w3.org/XML/1998/namespace")
    namespaces.setdefault("xsd", XSD_NAMESPACE)
    return SchemaDocument(
        member=member,
        member_sha256=hashlib.sha256(payload).hexdigest(),
        target_namespace=target_namespace,
        element_form_default=root.get("elementFormDefault", "unqualified"),
        attribute_form_default=root.get("attributeFormDefault", "unqualified"),
        namespaces=dict(sorted(namespaces.items())),
        root=root,
    )


def _resolve_qname(
    lexical: str,
    *,
    document: SchemaDocument,
) -> str:
    value = lexical.strip()
    if not value:
        raise UblSchemaGraphError(
            f"empty QName in schema member: {document.member}"
        )
    if ":" in value:
        prefix, local_name = value.split(":", 1)
        namespace = document.namespaces.get(prefix)
        if namespace is None:
            raise UblSchemaGraphError(
                f"undeclared QName prefix in {document.member}: {value}"
            )
        return _canonical_qname(namespace, local_name)
    namespace = document.namespaces.get("", document.target_namespace)
    return _canonical_qname(namespace, value)


def _node_id(kind: str, qname: str) -> str:
    return f"{kind.replace('_', '-')}::{qname}"


def _edge(
    kind: str,
    source_node_id: str,
    target_node_id: str,
    *,
    source_member: str,
    lexical_qname: str,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "kind": kind,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "source_member": source_member,
        "lexical_qname": lexical_qname,
    }
    value["edge_id"] = f"edge::{_digest(value)}"
    value["sha256"] = _digest(value)
    return value


def _global_node(
    *,
    document: SchemaDocument,
    element: ET.Element,
    kind: str,
) -> dict[str, Any]:
    name = element.get("name")
    if not name:
        raise UblSchemaGraphError(
            f"global {kind} lacks a name in {document.member}"
        )
    qname = _canonical_qname(document.target_namespace, name)
    value: dict[str, Any] = {
        "node_id": _node_id(kind, qname),
        "kind": kind,
        "qname": qname,
        "local_name": name,
        "namespace": document.target_namespace,
        "source_member": document.member,
        "source_member_sha256": document.member_sha256,
        "abstract": element.get("abstract") == "true",
    }
    value["sha256"] = _digest(value)
    return value


def _index_global_components(
    documents: Sequence[SchemaDocument],
    *,
    limits: GraphLimits,
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, str]]:
    components: dict[tuple[str, str], dict[str, Any]] = {}
    types: dict[str, str] = {}
    tag_kinds = {
        f"{XSD}element": "global_element",
        f"{XSD}attribute": "global_attribute",
        f"{XSD}complexType": "complex_type",
        f"{XSD}simpleType": "simple_type",
        f"{XSD}group": "model_group",
        f"{XSD}attributeGroup": "attribute_group",
    }
    for document in documents:
        for child in list(document.root):
            kind = tag_kinds.get(child.tag)
            if kind is None or not child.get("name"):
                continue
            node = _global_node(
                document=document,
                element=child,
                kind=kind,
            )
            key = (kind, node["qname"])
            if key in components:
                raise UblSchemaGraphError(
                    f"duplicate global {kind}: {node['qname']}"
                )
            components[key] = node
            if kind in {"complex_type", "simple_type"}:
                prior = types.get(node["qname"])
                if prior is not None:
                    raise UblSchemaGraphError(
                        f"ambiguous global type: {node['qname']}"
                    )
                types[node["qname"]] = node["node_id"]
            if len(components) > limits.max_graph_nodes:
                raise UblSchemaGraphError("graph node limit exceeded")
    return components, types


def compile_reachable_schema_graph(
    members: Mapping[str, bytes],
    *,
    root_members: Sequence[str],
    package_sha256: str,
    limits: GraphLimits | None = None,
) -> dict[str, Any]:
    """Compile the root/type skeleton of a content-addressed XSD graph.

    Subsequent TDD increments extend this same graph with local particles,
    facets, inheritance, wildcards, and documentation. Even this first
    increment fails closed on duplicate or unresolved root type references.
    """

    active_limits = limits or GraphLimits()
    schema_member_names = sorted(
        name
        for name in members
        if name.startswith("xsd/") and name.endswith(".xsd")
    )
    if len(schema_member_names) > active_limits.max_schema_documents:
        raise UblSchemaGraphError("schema document limit exceeded")
    documents = [
        _parse_schema(name, members[name]) for name in schema_member_names
    ]
    document_by_member = {document.member: document for document in documents}
    components, types = _index_global_components(
        documents,
        limits=active_limits,
    )
    elements = {
        qname: node
        for (kind, qname), node in components.items()
        if kind == "global_element"
    }

    edges: list[dict[str, Any]] = []
    roots: list[dict[str, str]] = []
    reachable_ids: set[str] = set()
    unresolved: list[str] = []
    for member in sorted(root_members):
        document = document_by_member.get(member)
        if document is None:
            raise UblSchemaGraphError(f"root schema is absent: {member}")
        match = _MAINDOC.fullmatch(member)
        if match is None:
            raise UblSchemaGraphError(f"not a UBL maindoc schema: {member}")
        expected_name = match.group("name")
        declarations = [
            child
            for child in list(document.root)
            if child.tag == f"{XSD}element" and child.get("name") == expected_name
        ]
        if len(declarations) != 1:
            raise UblSchemaGraphError(
                f"root element must resolve exactly once in {member}"
            )
        declaration = declarations[0]
        type_lexical = declaration.get("type")
        if not type_lexical:
            raise UblSchemaGraphError(
                f"root element lacks a declared type in {member}"
            )
        root_qname = _canonical_qname(
            document.target_namespace,
            expected_name,
        )
        root_node = elements.get(root_qname)
        if root_node is None:
            raise UblSchemaGraphError(
                f"root element is not indexed: {root_qname}"
            )
        type_qname = _resolve_qname(type_lexical, document=document)
        type_node_id = types.get(type_qname)
        if type_node_id is None:
            unresolved.append(
                f"{root_node['node_id']} -> {type_qname}"
            )
            continue
        edge = _edge(
            "type_reference",
            root_node["node_id"],
            type_node_id,
            source_member=member,
            lexical_qname=type_lexical,
        )
        edges.append(edge)
        reachable_ids.update((root_node["node_id"], type_node_id))
        roots.append(
            {
                "schema_member": member,
                "root_qname": root_qname,
                "root_node_id": root_node["node_id"],
                "content_type_qname": type_qname,
                "content_type_node_id": type_node_id,
            }
        )
        if len(edges) > active_limits.max_graph_edges:
            raise UblSchemaGraphError("graph edge limit exceeded")
    if unresolved:
        raise UblSchemaGraphError(
            "unresolved root type reference: " + "; ".join(sorted(unresolved))
        )

    nodes_by_id = {
        node["node_id"]: node for node in components.values()
    }
    nodes = [nodes_by_id[node_id] for node_id in sorted(reachable_ids)]
    edges.sort(key=lambda value: value["edge_id"])
    roots.sort(key=lambda value: value["root_qname"])
    schema_rows: list[dict[str, Any]] = [
        {
            "member": document.member,
            "sha256": document.member_sha256,
            "target_namespace": document.target_namespace,
            "element_form_default": document.element_form_default,
            "attribute_form_default": document.attribute_form_default,
            "namespaces": dict(document.namespaces),
        }
        for document in documents
    ]
    schema_rows.sort(key=lambda value: str(value["member"]))
    node_counts = Counter(node["kind"] for node in nodes)
    graph_identity = {
        "package_sha256": package_sha256,
        "schemas_sha256": _digest(schema_rows),
        "nodes_sha256": _digest(nodes),
        "edges_sha256": _digest(edges),
        "roots_sha256": _digest(roots),
    }
    return {
        "schema": "ff6/ubl-reachable-schema-graph@1",
        "format_id": "ubl",
        "profile": "ubl_2.3",
        "authority": {
            "source_id": "SRC-UBL-002",
            "package_sha256": package_sha256,
        },
        "limits": active_limits.as_dict(),
        "schema_document_count": len(schema_rows),
        "schema_documents": schema_rows,
        "root_count": len(roots),
        "roots": roots,
        "node_count": len(nodes),
        "node_counts": dict(sorted(node_counts.items())),
        "nodes": nodes,
        "edge_count": len(edges),
        "edge_counts": {"type_reference": len(edges)},
        "edges": edges,
        "identity": {
            **graph_identity,
            "graph_sha256": _digest(graph_identity),
        },
        "validation": {
            "duplicate_component_count": 0,
            "unresolved_reference_count": 0,
            "ambiguous_reference_count": 0,
            "root_without_type_count": 0,
        },
        "completion": {
            "package_census_complete": True,
            "root_denominator_complete": True,
            "reachable_schema_graph_complete": False,
            "naming_contract_complete": False,
            "obligation_denominator_complete": False,
            "product_implementation_complete": False,
            "production_certification_complete": False,
        },
        "truth_boundary": (
            "This graph currently proves exact root-to-declared-type "
            "resolution only. Local particles, facets, inheritance, wildcards, "
            "documentation, and complete reachability remain open."
        ),
    }
