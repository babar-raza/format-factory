"""Offline import/include dependency closure for UBL XML Schemas.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import posixpath
from typing import Any
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from tools.spec.ubl_schema_common import (
    GraphLimits,
    SchemaDocument,
    UblSchemaGraphError,
    XSD,
    digest,
    local_name,
)


def resolve_schema_location(
    *,
    owner_member: str,
    schema_location: str,
    members: Mapping[str, bytes],
    dependency_kind: str = "schema dependency",
) -> str:
    """Resolve one package-local XSD location without network or path escape."""

    location = schema_location.strip()
    parsed = urlsplit(location)
    if (
        not location
        or "\\" in location
        or parsed.scheme
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or location.startswith("/")
    ):
        raise UblSchemaGraphError(
            f"remote {dependency_kind} is prohibited in "
            f"{owner_member}: {schema_location}"
        )
    owner_dir = posixpath.dirname(owner_member)
    resolved = posixpath.normpath(posixpath.join(owner_dir, location))
    if (
        resolved in {"", "."}
        or resolved == ".."
        or resolved.startswith("../")
        or resolved not in members
    ):
        raise UblSchemaGraphError(
            f"unresolved {dependency_kind} in "
            f"{owner_member}: {schema_location}"
        )
    if not resolved.startswith("xsd/") or not resolved.endswith(".xsd"):
        raise UblSchemaGraphError(
            f"{dependency_kind} does not resolve to a package XSD in "
            f"{owner_member}: {schema_location}"
        )
    return resolved


def _dependency_edge(
    *,
    source: SchemaDocument,
    target: SchemaDocument,
    node: ET.Element,
    kind: str,
    members: Mapping[str, bytes],
) -> dict[str, Any]:
    schema_location = node.get("schemaLocation")
    if not schema_location:
        raise UblSchemaGraphError(
            f"{kind} lacks schemaLocation in {source.member}"
        )
    resolved = resolve_schema_location(
        owner_member=source.member,
        schema_location=schema_location,
        members=members,
        dependency_kind=kind,
    )
    if resolved != target.member:
        raise UblSchemaGraphError(
            f"{kind} resolver contradiction in {source.member}: "
            f"{schema_location}"
        )
    declared_namespace = node.get("namespace")
    if kind == "import":
        if not declared_namespace:
            raise UblSchemaGraphError(
                f"import lacks namespace in {source.member}: {schema_location}"
            )
        if declared_namespace != target.target_namespace:
            raise UblSchemaGraphError(
                f"import namespace mismatch in {source.member}: "
                f"{declared_namespace} != {target.target_namespace}"
            )
        if declared_namespace == source.target_namespace:
            raise UblSchemaGraphError(
                f"same-namespace import must be an include in {source.member}"
            )
    else:
        if declared_namespace:
            raise UblSchemaGraphError(
                f"include declares a namespace in {source.member}"
            )
        if target.target_namespace != source.target_namespace:
            raise UblSchemaGraphError(
                f"include namespace mismatch in {source.member}: "
                f"{source.target_namespace} != {target.target_namespace}"
            )
    value: dict[str, Any] = {
        "kind": f"schema_{kind}",
        "source_member": source.member,
        "source_member_sha256": source.member_sha256,
        "schema_location": schema_location,
        "resolution_mode": "schema_location",
        "declared_namespace": declared_namespace or "",
        "target_member": target.member,
        "target_member_sha256": target.member_sha256,
        "target_members": [target.member],
        "target_member_sha256s": [target.member_sha256],
        "target_namespace": target.target_namespace,
    }
    value["edge_id"] = f"schema-edge::{digest(value)}"
    value["sha256"] = digest(value)
    return value


def _include_families(
    include_adjacency: Mapping[str, set[str]],
) -> dict[str, frozenset[str]]:
    families: dict[str, frozenset[str]] = {}
    for source_member in sorted(include_adjacency):
        pending = [source_member]
        family: set[str] = set()
        while pending:
            member = pending.pop()
            if member in family:
                continue
            family.add(member)
            pending.extend(
                sorted(include_adjacency[member] - family, reverse=True)
            )
        frozen_family = frozenset(family)
        for member in family:
            families[member] = frozen_family
    return families


def _transitive_closures(
    adjacency: Mapping[str, set[str]],
) -> dict[str, frozenset[str]]:
    closures: dict[str, frozenset[str]] = {}
    for source_member in sorted(adjacency):
        pending = [source_member]
        reachable: set[str] = set()
        while pending:
            member = pending.pop()
            if member in reachable:
                continue
            reachable.add(member)
            pending.extend(sorted(adjacency[member] - reachable, reverse=True))
        closures[source_member] = frozenset(reachable)
    return closures


def compile_schema_dependencies(
    documents: Sequence[SchemaDocument],
    *,
    members: Mapping[str, bytes],
    root_members: Sequence[str],
    limits: GraphLimits,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    Mapping[str, frozenset[str]],
    Mapping[str, frozenset[str]],
]:
    """Compile exact dependencies, closures, and QName visibility."""

    document_by_member = {document.member: document for document in documents}
    dependency_edges: list[dict[str, Any]] = []
    adjacency: dict[str, set[str]] = {
        document.member: set() for document in documents
    }
    include_adjacency: dict[str, set[str]] = {
        document.member: set() for document in documents
    }
    direct_import_targets: dict[str, set[str]] = {
        document.member: set() for document in documents
    }
    pending_namespace_imports: list[tuple[SchemaDocument, ET.Element]] = []

    for source in documents:
        for child in list(source.root):
            local = local_name(child.tag)
            if child.tag != f"{XSD}include":
                continue
            schema_location = child.get("schemaLocation")
            if not schema_location:
                raise UblSchemaGraphError(
                    f"{local} lacks schemaLocation in {source.member}"
                )
            resolved = resolve_schema_location(
                owner_member=source.member,
                schema_location=schema_location,
                members=members,
                dependency_kind=local,
            )
            target = document_by_member.get(resolved)
            if target is None:
                raise UblSchemaGraphError(
                    f"{local} target is not a parsed XSD: {resolved}"
                )
            dependency_edges.append(
                _dependency_edge(
                    source=source,
                    target=target,
                    node=child,
                    kind=local,
                    members=members,
                )
            )
            adjacency[source.member].add(target.member)
            adjacency[target.member].add(source.member)
            include_adjacency[source.member].add(target.member)
            include_adjacency[target.member].add(source.member)
            if len(dependency_edges) > limits.max_graph_edges:
                raise UblSchemaGraphError("graph edge limit exceeded")

    include_families = _include_families(include_adjacency)
    for source in documents:
        for child in list(source.root):
            if child.tag != f"{XSD}import":
                continue
            schema_location = child.get("schemaLocation")
            if not schema_location:
                pending_namespace_imports.append((source, child))
                continue
            resolved = resolve_schema_location(
                owner_member=source.member,
                schema_location=schema_location,
                members=members,
                dependency_kind="import",
            )
            target = document_by_member.get(resolved)
            if target is None:
                raise UblSchemaGraphError(
                    f"import target is not a parsed XSD: {resolved}"
                )
            dependency_edges.append(
                _dependency_edge(
                    source=source,
                    target=target,
                    node=child,
                    kind="import",
                    members=members,
                )
            )
            adjacency[source.member].add(target.member)
            direct_import_targets[source.member].add(target.member)
            if len(dependency_edges) > limits.max_graph_edges:
                raise UblSchemaGraphError("graph edge limit exceeded")

    for source, child in pending_namespace_imports:
        declared_namespace = child.get("namespace")
        if not declared_namespace:
            raise UblSchemaGraphError(
                f"import lacks namespace and schemaLocation in {source.member}"
            )
        if declared_namespace == source.target_namespace:
            raise UblSchemaGraphError(
                f"same-namespace import must be an include in {source.member}"
            )
        candidates = sorted(
            document.member
            for document in documents
            if document.target_namespace == declared_namespace
        )
        if not candidates:
            raise UblSchemaGraphError(
                f"unresolved namespace import in {source.member}: "
                f"{declared_namespace}"
            )
        families = sorted(
            {tuple(sorted(include_families[member])) for member in candidates}
        )
        if len(families) != 1:
            raise UblSchemaGraphError(
                f"ambiguous namespace import in {source.member}: "
                f"{declared_namespace} resolves to {len(families)} "
                "disconnected schema families"
            )
        target_members = list(families[0])
        target_hashes = [
            document_by_member[member].member_sha256
            for member in target_members
        ]
        namespace_edge: dict[str, Any] = {
            "kind": "schema_import",
            "source_member": source.member,
            "source_member_sha256": source.member_sha256,
            "schema_location": "",
            "resolution_mode": "namespace_family",
            "declared_namespace": declared_namespace,
            "target_members": target_members,
            "target_member_sha256s": target_hashes,
            "target_namespace": declared_namespace,
        }
        namespace_edge["edge_id"] = f"schema-edge::{digest(namespace_edge)}"
        namespace_edge["sha256"] = digest(namespace_edge)
        dependency_edges.append(namespace_edge)
        adjacency[source.member].update(target_members)
        direct_import_targets[source.member].update(target_members)
        if len(dependency_edges) > limits.max_graph_edges:
            raise UblSchemaGraphError("graph edge limit exceeded")

    dependency_id_counts = Counter(
        str(edge["edge_id"]) for edge in dependency_edges
    )
    duplicate_dependency_ids = sorted(
        edge_id
        for edge_id, count in dependency_id_counts.items()
        if count != 1
    )
    if duplicate_dependency_ids:
        raise UblSchemaGraphError(
            "duplicate schema dependency identity: "
            + ", ".join(duplicate_dependency_ids)
        )
    dependency_edges.sort(key=lambda value: str(value["edge_id"]))

    closures = _transitive_closures(adjacency)
    root_closures: list[dict[str, Any]] = []
    for root_member in sorted(root_members):
        reachable_members = sorted(closures[root_member])
        value: dict[str, Any] = {
            "root_member": root_member,
            "reachable_member_count": len(reachable_members),
            "reachable_members": reachable_members,
        }
        value["sha256"] = digest(value)
        root_closures.append(value)
    reference_visibility: dict[str, frozenset[str]] = {}
    for source_member in sorted(adjacency):
        source_family = include_families[source_member]
        visible = set(source_family)
        for family_member in source_family:
            for imported_member in direct_import_targets[family_member]:
                visible.update(include_families[imported_member])
        reference_visibility[source_member] = frozenset(visible)
    return dependency_edges, root_closures, closures, reference_visibility
