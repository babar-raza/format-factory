"""Exact XML Schema derivation edges for the UBL 2.3 schema graph.

This compiler keeps inheritance semantics separate from generic QName uses.
Each edge is owned by one named or anonymous type and records whether the
authority declares complex-content extension/restriction, simple-content
extension/restriction, or simple-type restriction.

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


_TYPE_TAGS = {
    f"{XSD}complexType": "complex_type",
    f"{XSD}simpleType": "simple_type",
}
_CONTENT_TAGS = {
    f"{XSD}complexContent": "complex_content",
    f"{XSD}simpleContent": "simple_content",
}
_DERIVATION_TAGS = {
    f"{XSD}extension": "extension",
    f"{XSD}restriction": "restriction",
}


def _type_node_id(
    element: ET.Element,
    *,
    document: SchemaDocument,
    source_path: str,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
    anonymous_types_by_path: Mapping[tuple[str, str], Mapping[str, Any]],
) -> tuple[str, str]:
    type_kind = _TYPE_TAGS[element.tag]
    name = element.get("name")
    if name:
        if source_path.count("/") != 2:
            raise UblSchemaGraphError(
                f"named type is not global in {document.member}:{source_path}"
            )
        qname = canonical_qname(document.target_namespace, name)
        component = components.get((type_kind, qname))
        if component is None:
            raise UblSchemaGraphError(
                f"named type is not indexed in {document.member}:{source_path}"
            )
        return str(component["node_id"]), type_kind
    anonymous = anonymous_types_by_path.get((document.member, source_path))
    if anonymous is None:
        raise UblSchemaGraphError(
            f"anonymous type is not indexed in {document.member}:{source_path}"
        )
    return str(anonymous["node_id"]), str(anonymous["kind"])


def _base_reference(
    *,
    document: SchemaDocument,
    source_path: str,
    reference_uses_by_path: Mapping[
        tuple[str, str, str], Sequence[Mapping[str, Any]]
    ],
) -> Mapping[str, Any]:
    uses = reference_uses_by_path.get(
        (document.member, source_path, "base"),
        (),
    )
    if len(uses) != 1:
        raise UblSchemaGraphError(
            f"derivation base must resolve exactly once in "
            f"{document.member}:{source_path}"
        )
    return uses[0]


def _derivation_edge(
    *,
    kind: str,
    source_node_id: str,
    source_type_kind: str,
    document: SchemaDocument,
    source_path: str,
    reference: Mapping[str, Any],
) -> dict[str, Any]:
    core: dict[str, Any] = {
        "kind": kind,
        "derivation_method": kind.rsplit("_", 1)[-1],
        "content_model": kind.rsplit("_", 1)[0],
        "source_node_id": source_node_id,
        "source_type_kind": source_type_kind,
        "target_node_id": str(reference["target_node_id"]),
        "target_kind": str(reference["target_kind"]),
        "target_qname": str(reference["target_qname"]),
        "source_member": document.member,
        "source_member_sha256": document.member_sha256,
        "source_path": source_path,
        "lexical_base": str(reference["lexical_qname"]),
        "reference_use_id": str(reference["use_id"]),
    }
    edge_sha256 = digest(core)
    return {
        **core,
        "edge_id": f"derivation-edge::{edge_sha256}",
        "sha256": edge_sha256,
    }


def compile_derivation_edges(
    documents: Sequence[SchemaDocument],
    *,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
    anonymous_types: Sequence[Mapping[str, Any]],
    reference_uses: Sequence[Mapping[str, Any]],
    limits: GraphLimits,
) -> list[dict[str, Any]]:
    """Compile every QName-based extension and restriction edge."""

    anonymous_types_by_path = {
        (str(row["source_member"]), str(row["source_path"])): row
        for row in anonymous_types
    }
    reference_uses_by_path: dict[
        tuple[str, str, str], list[Mapping[str, Any]]
    ] = {}
    for row in reference_uses:
        key = (
            str(row["source_member"]),
            str(row["source_path"]),
            str(row["attribute"]),
        )
        reference_uses_by_path.setdefault(key, []).append(row)

    edges: list[dict[str, Any]] = []
    for document in sorted(documents, key=lambda item: item.member):
        paths = schema_element_paths(document.root)
        for type_element in document.root.iter():
            source_type_kind = _TYPE_TAGS.get(type_element.tag)
            if source_type_kind is None:
                continue
            type_path = paths[id(type_element)]
            source_node_id, source_type_kind = _type_node_id(
                type_element,
                document=document,
                source_path=type_path,
                components=components,
                anonymous_types_by_path=anonymous_types_by_path,
            )

            if type_element.tag == f"{XSD}simpleType":
                restrictions = [
                    child
                    for child in list(type_element)
                    if child.tag == f"{XSD}restriction"
                ]
                if len(restrictions) > 1:
                    raise UblSchemaGraphError(
                        f"simple type has multiple restrictions in "
                        f"{document.member}:{type_path}"
                    )
                if not restrictions:
                    continue
                derivation = restrictions[0]
                derivation_path = paths[id(derivation)]
                reference = _base_reference(
                    document=document,
                    source_path=derivation_path,
                    reference_uses_by_path=reference_uses_by_path,
                )
                if reference["target_kind"] not in {
                    "simple_type",
                    "xsd_builtin_type",
                }:
                    raise UblSchemaGraphError(
                        f"simple type restriction has non-simple base in "
                        f"{document.member}:{derivation_path}"
                    )
                edges.append(
                    _derivation_edge(
                        kind="simple_type_restriction",
                        source_node_id=source_node_id,
                        source_type_kind=source_type_kind,
                        document=document,
                        source_path=derivation_path,
                        reference=reference,
                    )
                )
                continue

            content_children = [
                child for child in list(type_element) if child.tag in _CONTENT_TAGS
            ]
            if len(content_children) > 1:
                raise UblSchemaGraphError(
                    f"complex type has multiple content derivations in "
                    f"{document.member}:{type_path}"
                )
            if not content_children:
                continue
            content = content_children[0]
            content_kind = _CONTENT_TAGS[content.tag]
            derivations = [
                child for child in list(content) if child.tag in _DERIVATION_TAGS
            ]
            if len(derivations) != 1:
                raise UblSchemaGraphError(
                    f"{content_kind} must contain exactly one extension or "
                    f"restriction in {document.member}:{paths[id(content)]}"
                )
            derivation = derivations[0]
            derivation_path = paths[id(derivation)]
            reference = _base_reference(
                document=document,
                source_path=derivation_path,
                reference_uses_by_path=reference_uses_by_path,
            )
            if content_kind == "complex_content" and not (
                reference["target_kind"] == "complex_type"
                or (
                    reference["target_kind"] == "xsd_builtin_type"
                    and reference["target_qname"] == f"{XSD}anyType"
                )
            ):
                raise UblSchemaGraphError(
                    f"complex content has non-complex base in "
                    f"{document.member}:{derivation_path}"
                )
            edges.append(
                _derivation_edge(
                    kind=f"{content_kind}_{_DERIVATION_TAGS[derivation.tag]}",
                    source_node_id=source_node_id,
                    source_type_kind=source_type_kind,
                    document=document,
                    source_path=derivation_path,
                    reference=reference,
                )
            )
            if len(edges) > limits.max_graph_edges:
                raise UblSchemaGraphError("graph edge limit exceeded")

    edges.sort(key=lambda row: str(row["edge_id"]))
    if len({str(row["edge_id"]) for row in edges}) != len(edges):
        raise UblSchemaGraphError("duplicate derivation edge identity")
    return edges
