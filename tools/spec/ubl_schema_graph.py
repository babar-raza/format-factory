"""Deterministic UBL 2.3 XML Schema graph orchestration.

Parsing, dependency closure, and QName-reference traversal are deliberately
split into focused sibling modules. This module preserves the original public
surface while assembling their immutable results into one canonical graph.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import re
from typing import Any

from tools.spec.ubl_schema_common import (
    GraphLimits,
    UblSchemaGraphError,
    XSD,
    canonical_qname,
    digest,
    edge,
    index_global_components,
    parse_schema,
    resolve_qname,
)
from tools.spec.ubl_schema_dependencies import (
    compile_schema_dependencies,
    resolve_schema_location,
)
from tools.spec.ubl_schema_anonymous_types import compile_anonymous_types
from tools.spec.ubl_schema_particles import compile_local_particles
from tools.spec.ubl_schema_references import compile_global_reference_uses


_MAINDOC = re.compile(r"^xsd/maindoc/UBL-(?P<name>[A-Za-z0-9]+)-2\.3\.xsd$")

__all__ = [
    "GraphLimits",
    "UblSchemaGraphError",
    "compile_reachable_schema_graph",
    "resolve_schema_location",
]


def compile_reachable_schema_graph(
    members: Mapping[str, bytes],
    *,
    root_members: Sequence[str],
    package_sha256: str,
    limits: GraphLimits | None = None,
) -> dict[str, Any]:
    """Compile the deterministic root/type and global-reference XSD graph."""

    active_limits = limits or GraphLimits()
    schema_member_names = sorted(
        name for name in members if name.startswith("xsd/") and name.endswith(".xsd")
    )
    if len(schema_member_names) > active_limits.max_schema_documents:
        raise UblSchemaGraphError("schema document limit exceeded")

    documents = [parse_schema(name, members[name]) for name in schema_member_names]
    document_by_member = {document.member: document for document in documents}
    components, types = index_global_components(documents, limits=active_limits)
    (
        dependency_edges,
        schema_closures,
        _,
        reference_visibility,
    ) = compile_schema_dependencies(
        documents,
        members=members,
        root_members=root_members,
        limits=active_limits,
    )
    reference_uses, builtin_nodes = compile_global_reference_uses(
        documents,
        components=components,
        reference_visibility=reference_visibility,
        limits=active_limits,
    )
    particles, particle_edges = compile_local_particles(
        documents,
        components=components,
        limits=active_limits,
    )
    anonymous_types, anonymous_type_edges = compile_anonymous_types(
        documents,
        components=components,
        particles=particles,
        limits=active_limits,
    )
    if (
        len(components)
        + len(builtin_nodes)
        + len(particles)
        + len(anonymous_types)
        > active_limits.max_graph_nodes
    ):
        raise UblSchemaGraphError("graph node limit exceeded")
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
            raise UblSchemaGraphError(f"root element lacks a declared type in {member}")
        root_qname = canonical_qname(document.target_namespace, expected_name)
        root_node = elements.get(root_qname)
        if root_node is None:
            raise UblSchemaGraphError(f"root element is not indexed: {root_qname}")
        type_qname = resolve_qname(type_lexical, document=document)
        type_node_id = types.get(type_qname)
        if type_node_id is None:
            unresolved.append(f"{root_node['node_id']} -> {type_qname}")
            continue
        root_edge = edge(
            "type_reference",
            root_node["node_id"],
            type_node_id,
            source_member=member,
            lexical_qname=type_lexical,
        )
        edges.append(root_edge)
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
    if (
        len(dependency_edges)
        + len(reference_uses)
        + len(edges)
        + len(particle_edges)
        + len(anonymous_type_edges)
        > active_limits.max_graph_edges
    ):
        raise UblSchemaGraphError("graph edge limit exceeded")

    nodes_by_id = {node["node_id"]: node for node in components.values()}
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
    global_components = sorted(
        components.values(),
        key=lambda value: str(value["node_id"]),
    )
    global_component_counts = Counter(str(node["kind"]) for node in global_components)
    dependency_counts = Counter(str(item["kind"]) for item in dependency_edges)
    reference_attribute_counts = Counter(
        str(row["attribute"]) for row in reference_uses
    )
    reference_target_counts = Counter(str(row["target_kind"]) for row in reference_uses)
    particle_kind_counts = Counter(str(row["kind"]) for row in particles)
    anonymous_type_kind_counts = Counter(
        str(row["kind"]) for row in anonymous_types
    )
    graph_identity = {
        "package_sha256": package_sha256,
        "schemas_sha256": digest(schema_rows),
        "nodes_sha256": digest(nodes),
        "edges_sha256": digest(edges),
        "roots_sha256": digest(roots),
    }
    closure_identity = {
        "schema_dependencies_sha256": digest(dependency_edges),
        "schema_closures_sha256": digest(schema_closures),
        "global_components_sha256": digest(global_components),
        "xsd_builtin_types_sha256": digest(builtin_nodes),
        "global_reference_uses_sha256": digest(reference_uses),
    }
    particle_identity = {
        "particles_sha256": digest(particles),
        "particle_edges_sha256": digest(particle_edges),
    }
    anonymous_type_identity = {
        "anonymous_types_sha256": digest(anonymous_types),
        "anonymous_type_edges_sha256": digest(anonymous_type_edges),
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
        "schema_dependency_edge_count": len(dependency_edges),
        "schema_dependency_edge_counts": dict(sorted(dependency_counts.items())),
        "schema_dependency_edges": dependency_edges,
        "schema_closures": schema_closures,
        "root_count": len(roots),
        "roots": roots,
        "node_count": len(nodes),
        "node_counts": dict(sorted(node_counts.items())),
        "nodes": nodes,
        "edge_count": len(edges),
        "edge_counts": {"type_reference": len(edges)},
        "edges": edges,
        "global_component_count": len(global_components),
        "global_component_counts": dict(sorted(global_component_counts.items())),
        "global_components": global_components,
        "xsd_builtin_type_count": len(builtin_nodes),
        "xsd_builtin_types": builtin_nodes,
        "global_reference_use_count": len(reference_uses),
        "global_reference_attribute_counts": dict(
            sorted(reference_attribute_counts.items())
        ),
        "global_reference_target_counts": dict(sorted(reference_target_counts.items())),
        "global_reference_uses": reference_uses,
        "particle_count": len(particles),
        "particle_kind_counts": dict(sorted(particle_kind_counts.items())),
        "particle_owner_count": len(
            {str(row["owner_node_id"]) for row in particles}
        ),
        "particles": particles,
        "particle_edge_count": len(particle_edges),
        "particle_edges": particle_edges,
        "anonymous_type_count": len(anonymous_types),
        "anonymous_type_kind_counts": dict(
            sorted(anonymous_type_kind_counts.items())
        ),
        "anonymous_type_owner_count": len(
            {str(row["owner_node_id"]) for row in anonymous_types}
        ),
        "anonymous_types": anonymous_types,
        "anonymous_type_edge_count": len(anonymous_type_edges),
        "anonymous_type_edges": anonymous_type_edges,
        "identity": {
            **graph_identity,
            "graph_sha256": digest(graph_identity),
        },
        "closure_identity": {
            **closure_identity,
            "closure_sha256": digest(closure_identity),
        },
        "particle_identity": {
            **particle_identity,
            "particle_graph_sha256": digest(particle_identity),
        },
        "anonymous_type_identity": {
            **anonymous_type_identity,
            "anonymous_type_graph_sha256": digest(
                anonymous_type_identity
            ),
        },
        "validation": {
            "duplicate_component_count": 0,
            "unresolved_schema_dependency_count": 0,
            "schema_namespace_mismatch_count": 0,
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
            "This graph currently proves exact root-to-declared-type binding, "
            "offline import/include closure, and unique global QName-reference "
            "resolution. It also preserves named-type compositor trees, local "
            "element occurrence/order, nillability, defaults, fixed values, "
            "and form. Anonymous types, complete group/wildcard semantics, "
            "facets, inheritance edges, documentation, and complete "
            "reachability remain open."
        ),
    }
