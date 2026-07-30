"""Shared deterministic primitives for the UBL 2.3 schema graph.

This module owns schema parsing, QName normalization, graph identities, and
global component indexing. Dependency and reference traversal live in
dedicated sibling modules so later schema-surface work does not recreate a
monolith.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

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
_FORBIDDEN_XML_DECLARATIONS = re.compile(rb"<!\s*(?:DOCTYPE|ENTITY)\b", re.I)
_XML_COMMENT = re.compile(rb"<!--.*?-->", re.S)


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


def canonical_json_bytes(value: object) -> bytes:
    """Encode a graph value as deterministic LF-terminated JSON."""

    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def digest(value: object) -> str:
    """Return the canonical JSON SHA-256 identity for a graph value."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def local_name(tag: str) -> str:
    """Return the local component of an expanded XML name."""

    return tag.rsplit("}", 1)[-1]


def canonical_qname(namespace: str, local: str) -> str:
    """Return one validated Clark-notation QName."""

    if not local:
        raise UblSchemaGraphError("QName local name is empty")
    return f"{{{namespace}}}{local}"


def parse_schema(member: str, payload: bytes) -> SchemaDocument:
    """Parse one security-checked XSD member and retain namespace bindings."""

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
                root = value
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


def resolve_qname(lexical: str, *, document: SchemaDocument) -> str:
    """Resolve one lexical QName against a schema document's bindings."""

    value = lexical.strip()
    if not value:
        raise UblSchemaGraphError(
            f"empty QName in schema member: {document.member}"
        )
    if ":" in value:
        prefix, local = value.split(":", 1)
        namespace = document.namespaces.get(prefix)
        if namespace is None:
            raise UblSchemaGraphError(
                f"undeclared QName prefix in {document.member}: {value}"
            )
        return canonical_qname(namespace, local)
    namespace = document.namespaces.get("", document.target_namespace)
    return canonical_qname(namespace, value)


def node_id(kind: str, qname: str) -> str:
    """Return a stable graph node identifier."""

    return f"{kind.replace('_', '-')}::{qname}"


def edge(
    kind: str,
    source_node_id: str,
    target_node_id: str,
    *,
    source_member: str,
    lexical_qname: str,
) -> dict[str, Any]:
    """Create one content-addressed component edge."""

    value: dict[str, Any] = {
        "kind": kind,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "source_member": source_member,
        "lexical_qname": lexical_qname,
    }
    value["edge_id"] = f"edge::{digest(value)}"
    value["sha256"] = digest(value)
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
    qname = canonical_qname(document.target_namespace, name)
    value: dict[str, Any] = {
        "node_id": node_id(kind, qname),
        "kind": kind,
        "qname": qname,
        "local_name": name,
        "namespace": document.target_namespace,
        "source_member": document.member,
        "source_member_sha256": document.member_sha256,
        "abstract": element.get("abstract") == "true",
    }
    value["sha256"] = digest(value)
    return value


def index_global_components(
    documents: Sequence[SchemaDocument],
    *,
    limits: GraphLimits,
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, str]]:
    """Index every named global component and enforce unique type ownership."""

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
