"""Stable identity graph for anonymous XML Schema types.

Anonymous simple and complex types have no QName. Their durable identity is
therefore derived from the authority member and exact sibling-kind-indexed
schema path, never from traversal order or a generated Python name. Ownership
edges retain the declaration and enclosing type separately so later naming
and code-generation stages can make explicit, reproducible choices.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
import xml.etree.ElementTree as ET

from tools.spec.ubl_schema_common import (
    GraphLimits,
    SchemaDocument,
    UblSchemaGraphError,
    XSD,
    canonical_qname,
    digest,
    schema_element_paths,
)


_TYPE_KINDS = {
    f"{XSD}complexType": "anonymous_complex_type",
    f"{XSD}simpleType": "anonymous_simple_type",
}
_GLOBAL_COMPONENT_KINDS = {
    f"{XSD}attribute": "global_attribute",
    f"{XSD}attributeGroup": "attribute_group",
    f"{XSD}complexType": "complex_type",
    f"{XSD}element": "global_element",
    f"{XSD}group": "model_group",
    f"{XSD}simpleType": "simple_type",
}
_DECLARATION_TAGS = {
    f"{XSD}attribute": "attribute",
    f"{XSD}element": "element",
}


def _declaration_node_id(
    *,
    document: SchemaDocument,
    source_path: str,
    declaration_kind: str,
) -> str:
    identity = {
        "source_member": document.member,
        "source_path": source_path,
        "declaration_kind": declaration_kind,
    }
    return f"schema-declaration::{digest(identity)}"


def _global_component_owner(
    element: ET.Element,
    *,
    document: SchemaDocument,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[str, str] | None:
    kind = _GLOBAL_COMPONENT_KINDS.get(element.tag)
    name = element.get("name")
    if kind is None or not name:
        return None
    qname = canonical_qname(document.target_namespace, name)
    component = components.get((kind, qname))
    if component is None:
        return None
    return str(component["node_id"]), kind


def _declaration_owner(
    element: ET.Element,
    *,
    parent: ET.Element | None,
    document: SchemaDocument,
    source_path: str,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
    particles_by_path: Mapping[tuple[str, str], str],
) -> tuple[str, str]:
    declaration_kind = _DECLARATION_TAGS[element.tag]
    if parent is document.root:
        component = _global_component_owner(
            element,
            document=document,
            components=components,
        )
        if component is None:
            raise UblSchemaGraphError(
                f"global {declaration_kind} is not indexed in "
                f"{document.member}:{source_path}"
            )
        return component
    if declaration_kind == "element":
        particle_id = particles_by_path.get((document.member, source_path))
        if particle_id is not None:
            return particle_id, "local_element"
    return (
        _declaration_node_id(
            document=document,
            source_path=source_path,
            declaration_kind=f"local_{declaration_kind}",
        ),
        f"local_{declaration_kind}",
    )


def compile_anonymous_types(
    documents: Sequence[SchemaDocument],
    *,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
    particles: Sequence[Mapping[str, Any]],
    limits: GraphLimits,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Compile path-owned anonymous types and their exact ownership edges."""

    particles_by_path = {
        (str(row["source_member"]), str(row["source_path"])): str(
            row["particle_id"]
        )
        for row in particles
        if row.get("kind") == "element"
    }
    nodes: list[dict[str, Any]] = []
    ownership_edges: list[dict[str, Any]] = []

    for document in sorted(documents, key=lambda item: item.member):
        paths = schema_element_paths(document.root)

        def visit(
            element: ET.Element,
            *,
            parent: ET.Element | None,
            owner_node_id: str,
            owner_kind: str,
            owner_source_path: str,
            enclosing_type_node_id: str,
        ) -> None:
            source_path = paths[id(element)]
            next_owner_node_id = owner_node_id
            next_owner_kind = owner_kind
            next_owner_source_path = owner_source_path
            next_enclosing_type_node_id = enclosing_type_node_id

            declaration_kind = _DECLARATION_TAGS.get(element.tag)
            if declaration_kind is not None:
                inline_types = [
                    child for child in list(element) if child.tag in _TYPE_KINDS
                ]
                if len(inline_types) > 1:
                    raise UblSchemaGraphError(
                        f"declaration has multiple anonymous types in "
                        f"{document.member}:{source_path}"
                    )
                if inline_types and element.get("type") is not None:
                    raise UblSchemaGraphError(
                        f"declaration cannot combine type with an anonymous "
                        f"type in {document.member}:{source_path}"
                    )
                (
                    next_owner_node_id,
                    next_owner_kind,
                ) = _declaration_owner(
                    element,
                    parent=parent,
                    document=document,
                    source_path=source_path,
                    components=components,
                    particles_by_path=particles_by_path,
                )
                next_owner_source_path = source_path

            type_kind = _TYPE_KINDS.get(element.tag)
            type_name = element.get("name")
            if type_kind is not None and type_name:
                if parent is not document.root:
                    raise UblSchemaGraphError(
                        f"named type is not global in "
                        f"{document.member}:{source_path}"
                    )
                global_kind = type_kind.removeprefix("anonymous_")
                component = components.get(
                    (
                        global_kind,
                        canonical_qname(document.target_namespace, type_name),
                    )
                )
                if component is None:
                    raise UblSchemaGraphError(
                        f"named type is not indexed in "
                        f"{document.member}:{source_path}"
                    )
                next_owner_node_id = str(component["node_id"])
                next_owner_kind = global_kind
                next_owner_source_path = source_path
                next_enclosing_type_node_id = next_owner_node_id
            elif type_kind is not None:
                if not next_owner_node_id:
                    raise UblSchemaGraphError(
                        f"anonymous type lacks a stable owner in "
                        f"{document.member}:{source_path}"
                    )
                identity = {
                    "kind": type_kind,
                    "source_member": document.member,
                    "source_path": source_path,
                }
                node_id = (
                    f"{type_kind.replace('_', '-')}::{digest(identity)}"
                )
                core: dict[str, Any] = {
                    "node_id": node_id,
                    "kind": type_kind,
                    "target_namespace": document.target_namespace,
                    "source_member": document.member,
                    "source_member_sha256": document.member_sha256,
                    "source_path": source_path,
                    "owner_node_id": next_owner_node_id,
                    "owner_kind": next_owner_kind,
                    "owner_source_path": next_owner_source_path,
                    "enclosing_type_node_id": next_enclosing_type_node_id,
                }
                node_sha256 = digest(core)
                nodes.append({**core, "sha256": node_sha256})
                edge_core: dict[str, Any] = {
                    "kind": "owns_anonymous_type",
                    "source_node_id": next_owner_node_id,
                    "target_node_id": node_id,
                    "source_member": document.member,
                    "source_path": source_path,
                }
                edge_sha256 = digest(edge_core)
                ownership_edges.append(
                    {
                        **edge_core,
                        "edge_id": f"anonymous-type-edge::{edge_sha256}",
                        "sha256": edge_sha256,
                    }
                )
                if len(nodes) > limits.max_graph_nodes:
                    raise UblSchemaGraphError("graph node limit exceeded")
                if len(ownership_edges) > limits.max_graph_edges:
                    raise UblSchemaGraphError("graph edge limit exceeded")
                next_owner_node_id = node_id
                next_owner_kind = "anonymous_type"
                next_owner_source_path = source_path
                next_enclosing_type_node_id = node_id

            for child in list(element):
                visit(
                    child,
                    parent=element,
                    owner_node_id=next_owner_node_id,
                    owner_kind=next_owner_kind,
                    owner_source_path=next_owner_source_path,
                    enclosing_type_node_id=next_enclosing_type_node_id,
                )

        visit(
            document.root,
            parent=None,
            owner_node_id="",
            owner_kind="",
            owner_source_path="",
            enclosing_type_node_id="",
        )

    nodes.sort(
        key=lambda row: (
            str(row["source_member"]),
            str(row["source_path"]),
            str(row["node_id"]),
        )
    )
    ownership_edges.sort(key=lambda row: str(row["edge_id"]))
    if len({str(row["node_id"]) for row in nodes}) != len(nodes):
        raise UblSchemaGraphError("duplicate anonymous type identity")
    if len({str(row["edge_id"]) for row in ownership_edges}) != len(
        ownership_edges
    ):
        raise UblSchemaGraphError("duplicate anonymous type ownership edge")
    return nodes, ownership_edges
