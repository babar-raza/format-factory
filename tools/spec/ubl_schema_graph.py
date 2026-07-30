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
import posixpath
import re
from typing import Any, cast
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"
XSD = f"{{{XSD_NAMESPACE}}}"
_FORBIDDEN_XML_DECLARATIONS = re.compile(rb"<!\s*(?:DOCTYPE|ENTITY)\b", re.I)
_XML_COMMENT = re.compile(rb"<!--.*?-->", re.S)
_MAINDOC = re.compile(r"^xsd/maindoc/UBL-(?P<name>[A-Za-z0-9]+)-2\.3\.xsd$")
_REFERENCE_ATTRIBUTES = (
    "base",
    "itemType",
    "memberTypes",
    "ref",
    "substitutionGroup",
    "type",
)
_XSD_BUILTIN_TYPES = frozenset(
    {
        "ENTITIES",
        "ENTITY",
        "ID",
        "IDREF",
        "IDREFS",
        "NCName",
        "NMTOKEN",
        "NMTOKENS",
        "NOTATION",
        "Name",
        "QName",
        "anyAtomicType",
        "anySimpleType",
        "anyType",
        "anyURI",
        "base64Binary",
        "boolean",
        "byte",
        "date",
        "dateTime",
        "dateTimeStamp",
        "dayTimeDuration",
        "decimal",
        "double",
        "duration",
        "float",
        "gDay",
        "gMonth",
        "gMonthDay",
        "gYear",
        "gYearMonth",
        "hexBinary",
        "int",
        "integer",
        "language",
        "long",
        "negativeInteger",
        "nonNegativeInteger",
        "nonPositiveInteger",
        "normalizedString",
        "positiveInteger",
        "short",
        "string",
        "time",
        "token",
        "unsignedByte",
        "unsignedInt",
        "unsignedLong",
        "unsignedShort",
        "yearMonthDuration",
    }
)


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
        raise UblSchemaGraphError(f"DOCTYPE or entity declaration prohibited: {member}")
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
                        f"namespace prefix rebound in {member}: {normalized_prefix!r}"
                    )
                namespaces[normalized_prefix] = namespace
            elif root is None:
                root = cast(ET.Element, value)
    except ET.ParseError as exc:
        raise UblSchemaGraphError(f"invalid XSD XML: {member}") from exc
    if root is None:
        raise UblSchemaGraphError(f"empty XSD XML: {member}")
    if root.tag != f"{XSD}schema":
        raise UblSchemaGraphError(f"member is not an XML Schema document: {member}")
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
        raise UblSchemaGraphError(f"empty QName in schema member: {document.member}")
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
            f"remote {dependency_kind} is prohibited in {owner_member}: {schema_location}"
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
            f"unresolved {dependency_kind} in {owner_member}: {schema_location}"
        )
    if not resolved.startswith("xsd/") or not resolved.endswith(".xsd"):
        raise UblSchemaGraphError(
            f"{dependency_kind} does not resolve to a package XSD in {owner_member}: {schema_location}"
        )
    return resolved


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
        raise UblSchemaGraphError(f"global {kind} lacks a name in {document.member}")
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
                raise UblSchemaGraphError(f"duplicate global {kind}: {node['qname']}")
            components[key] = node
            if kind in {"complex_type", "simple_type"}:
                prior = types.get(node["qname"])
                if prior is not None:
                    raise UblSchemaGraphError(f"ambiguous global type: {node['qname']}")
                types[node["qname"]] = node["node_id"]
            if len(components) > limits.max_graph_nodes:
                raise UblSchemaGraphError("graph node limit exceeded")
    return components, types


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
        raise UblSchemaGraphError(f"{kind} lacks schemaLocation in {source.member}")
    resolved = resolve_schema_location(
        owner_member=source.member,
        schema_location=schema_location,
        members=members,
        dependency_kind=kind,
    )
    if resolved != target.member:
        raise UblSchemaGraphError(
            f"{kind} resolver contradiction in {source.member}: {schema_location}"
        )
    declared_namespace = node.get("namespace")
    if kind == "import":
        if not declared_namespace:
            raise UblSchemaGraphError(
                f"import lacks namespace in {source.member}: {schema_location}"
            )
        if declared_namespace != target.target_namespace:
            raise UblSchemaGraphError(
                f"import namespace mismatch in {source.member}: {declared_namespace} != {target.target_namespace}"
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
                f"include namespace mismatch in {source.member}: {source.target_namespace} != {target.target_namespace}"
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
    value["edge_id"] = f"schema-edge::{_digest(value)}"
    value["sha256"] = _digest(value)
    return value


def _compile_schema_dependencies(
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
    document_by_member = {document.member: document for document in documents}
    dependency_edges: list[dict[str, Any]] = []
    adjacency: dict[str, set[str]] = {document.member: set() for document in documents}
    include_adjacency: dict[str, set[str]] = {
        document.member: set() for document in documents
    }
    direct_import_targets: dict[str, set[str]] = {
        document.member: set() for document in documents
    }
    pending_namespace_imports: list[tuple[SchemaDocument, ET.Element]] = []

    # Includes establish same-namespace schema families. Resolve them before
    # location-less imports, which can only be accepted when the namespace
    # identifies exactly one such family in the pinned package.
    for source in documents:
        for child in list(source.root):
            local_name = _local_name(child.tag)
            if child.tag != f"{XSD}include":
                continue
            schema_location = child.get("schemaLocation")
            if not schema_location:
                raise UblSchemaGraphError(
                    f"{local_name} lacks schemaLocation in {source.member}"
                )
            resolved = resolve_schema_location(
                owner_member=source.member,
                schema_location=schema_location,
                members=members,
                dependency_kind=local_name,
            )
            target = document_by_member.get(resolved)
            if target is None:
                raise UblSchemaGraphError(
                    f"{local_name} target is not a parsed XSD: {resolved}"
                )
            dependency_edges.append(
                _dependency_edge(
                    source=source,
                    target=target,
                    node=child,
                    kind=local_name,
                    members=members,
                )
            )
            adjacency[source.member].add(target.member)
            # Included documents contribute to one schema component space;
            # either document may legally refer to same-namespace declarations
            # contributed by the other.
            adjacency[target.member].add(source.member)
            include_adjacency[source.member].add(target.member)
            include_adjacency[target.member].add(source.member)
            if len(dependency_edges) > limits.max_graph_edges:
                raise UblSchemaGraphError("graph edge limit exceeded")

    include_families: dict[str, frozenset[str]] = {}
    for source_member in sorted(include_adjacency):
        pending = [source_member]
        family: set[str] = set()
        while pending:
            member = pending.pop()
            if member in family:
                continue
            family.add(member)
            pending.extend(sorted(include_adjacency[member] - family, reverse=True))
        frozen_family = frozenset(family)
        for member in family:
            include_families[member] = frozen_family

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
                f"unresolved namespace import in {source.member}: {declared_namespace}"
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
            document_by_member[member].member_sha256 for member in target_members
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
        namespace_edge["edge_id"] = f"schema-edge::{_digest(namespace_edge)}"
        namespace_edge["sha256"] = _digest(namespace_edge)
        dependency_edges.append(namespace_edge)
        adjacency[source.member].update(target_members)
        direct_import_targets[source.member].update(target_members)
        if len(dependency_edges) > limits.max_graph_edges:
            raise UblSchemaGraphError("graph edge limit exceeded")
    dependency_id_counts = Counter(str(edge["edge_id"]) for edge in dependency_edges)
    duplicate_dependency_ids = sorted(
        edge_id for edge_id, count in dependency_id_counts.items() if count != 1
    )
    if duplicate_dependency_ids:
        raise UblSchemaGraphError(
            "duplicate schema dependency identity: "
            + ", ".join(duplicate_dependency_ids)
        )
    dependency_edges.sort(key=lambda value: str(value["edge_id"]))

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
    root_closures: list[dict[str, Any]] = []
    for root_member in sorted(root_members):
        reachable_members = sorted(closures[root_member])
        value: dict[str, Any] = {
            "root_member": root_member,
            "reachable_member_count": len(reachable_members),
            "reachable_members": reachable_members,
        }
        value["sha256"] = _digest(value)
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


def _iter_schema_elements(
    root: ET.Element,
) -> Sequence[tuple[ET.Element, str]]:
    rows: list[tuple[ET.Element, str]] = []

    def visit(element: ET.Element, path: str) -> None:
        rows.append((element, path))
        sibling_counts: Counter[str] = Counter()
        for child in list(element):
            local_name = _local_name(child.tag)
            sibling_counts[local_name] += 1
            visit(
                child,
                f"{path}/{local_name}[{sibling_counts[local_name]}]",
            )

    visit(root, "/schema[1]")
    return rows


def _reference_target_kinds(element: ET.Element, attribute: str) -> tuple[str, ...]:
    if attribute in {"type", "base", "itemType", "memberTypes"}:
        return ("complex_type", "simple_type")
    if attribute == "substitutionGroup":
        return ("global_element",)
    if attribute == "ref":
        target_by_tag = {
            f"{XSD}attribute": "global_attribute",
            f"{XSD}attributeGroup": "attribute_group",
            f"{XSD}element": "global_element",
            f"{XSD}group": "model_group",
        }
        target = target_by_tag.get(element.tag)
        if target is None:
            raise UblSchemaGraphError(
                f"unsupported XSD ref owner: {_local_name(element.tag)}"
            )
        return (target,)
    raise UblSchemaGraphError(f"unsupported QName reference attribute: {attribute}")


def _compile_global_reference_uses(
    documents: Sequence[SchemaDocument],
    *,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
    reference_visibility: Mapping[str, frozenset[str]],
    limits: GraphLimits,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    uses: list[dict[str, Any]] = []
    builtin_nodes: dict[str, dict[str, Any]] = {}
    unresolved: list[str] = []
    for document in documents:
        for element, source_path in _iter_schema_elements(document.root):
            for attribute in _REFERENCE_ATTRIBUTES:
                lexical = element.get(attribute)
                if lexical is None:
                    continue
                values = lexical.split() if attribute == "memberTypes" else [lexical]
                if not values:
                    raise UblSchemaGraphError(
                        f"empty {attribute} reference in {document.member}: {source_path}"
                    )
                target_kinds = _reference_target_kinds(element, attribute)
                for position, lexical_qname in enumerate(values, start=1):
                    target_qname = _resolve_qname(
                        lexical_qname,
                        document=document,
                    )
                    namespace, local_name = target_qname[1:].split("}", 1)
                    target_kind: str
                    target_node_id: str
                    target_source_member: str
                    if namespace == XSD_NAMESPACE:
                        if target_kinds != ("complex_type", "simple_type"):
                            unresolved.append(
                                f"{document.member}:{source_path}@{attribute} cannot target XSD builtin {target_qname}"
                            )
                            continue
                        if local_name not in _XSD_BUILTIN_TYPES:
                            unresolved.append(
                                f"{document.member}:{source_path}@{attribute} unknown XSD builtin {target_qname}"
                            )
                            continue
                        target_kind = "xsd_builtin_type"
                        target_node_id = _node_id(target_kind, target_qname)
                        target_source_member = ""
                        if target_qname not in builtin_nodes:
                            builtin: dict[str, Any] = {
                                "node_id": target_node_id,
                                "kind": target_kind,
                                "qname": target_qname,
                                "local_name": local_name,
                                "namespace": XSD_NAMESPACE,
                            }
                            builtin["sha256"] = _digest(builtin)
                            builtin_nodes[target_qname] = builtin
                    else:
                        candidates = [
                            components[(kind, target_qname)]
                            for kind in target_kinds
                            if (kind, target_qname) in components
                        ]
                        if len(candidates) != 1:
                            unresolved.append(
                                f"{document.member}:{source_path}@{attribute} "
                                f"resolves {len(candidates)} times: {target_qname}"
                            )
                            continue
                        target = candidates[0]
                        target_source_member = str(target["source_member"])
                        if (
                            target_source_member
                            not in reference_visibility[document.member]
                        ):
                            unresolved.append(
                                f"{document.member}:{source_path}@{attribute} "
                                "target is outside direct import/include "
                                "visibility: "
                                f"{target_qname} in {target_source_member}"
                            )
                            continue
                        target_kind = str(target["kind"])
                        target_node_id = str(target["node_id"])
                    core: dict[str, Any] = {
                        "source_member": document.member,
                        "source_member_sha256": document.member_sha256,
                        "source_path": source_path,
                        "source_tag": _local_name(element.tag),
                        "attribute": attribute,
                        "attribute_position": position,
                        "lexical_qname": lexical_qname,
                        "target_qname": target_qname,
                        "target_kind": target_kind,
                        "target_node_id": target_node_id,
                        "target_source_member": target_source_member,
                    }
                    core["use_id"] = f"reference-use::{_digest(core)}"
                    core["sha256"] = _digest(core)
                    uses.append(core)
                    if (
                        len(components) + len(uses) + len(builtin_nodes)
                        > limits.max_graph_nodes
                    ):
                        raise UblSchemaGraphError("graph node limit exceeded")
                    if len(uses) > limits.max_graph_edges:
                        raise UblSchemaGraphError("graph edge limit exceeded")
    if unresolved:
        raise UblSchemaGraphError(
            "global reference closure failed: " + "; ".join(sorted(unresolved))
        )
    uses.sort(key=lambda value: str(value["use_id"]))
    builtins = [builtin_nodes[qname] for qname in sorted(builtin_nodes)]
    return uses, builtins


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
        name for name in members if name.startswith("xsd/") and name.endswith(".xsd")
    )
    if len(schema_member_names) > active_limits.max_schema_documents:
        raise UblSchemaGraphError("schema document limit exceeded")
    documents = [_parse_schema(name, members[name]) for name in schema_member_names]
    document_by_member = {document.member: document for document in documents}
    components, types = _index_global_components(
        documents,
        limits=active_limits,
    )
    (
        dependency_edges,
        schema_closures,
        _,
        reference_visibility,
    ) = _compile_schema_dependencies(
        documents,
        members=members,
        root_members=root_members,
        limits=active_limits,
    )
    reference_uses, builtin_nodes = _compile_global_reference_uses(
        documents,
        components=components,
        reference_visibility=reference_visibility,
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
            raise UblSchemaGraphError(f"root element lacks a declared type in {member}")
        root_qname = _canonical_qname(
            document.target_namespace,
            expected_name,
        )
        root_node = elements.get(root_qname)
        if root_node is None:
            raise UblSchemaGraphError(f"root element is not indexed: {root_qname}")
        type_qname = _resolve_qname(type_lexical, document=document)
        type_node_id = types.get(type_qname)
        if type_node_id is None:
            unresolved.append(f"{root_node['node_id']} -> {type_qname}")
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
    if (
        len(dependency_edges) + len(reference_uses) + len(edges)
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
    dependency_counts = Counter(str(edge["kind"]) for edge in dependency_edges)
    reference_attribute_counts = Counter(
        str(row["attribute"]) for row in reference_uses
    )
    reference_target_counts = Counter(str(row["target_kind"]) for row in reference_uses)
    graph_identity = {
        "package_sha256": package_sha256,
        "schemas_sha256": _digest(schema_rows),
        "nodes_sha256": _digest(nodes),
        "edges_sha256": _digest(edges),
        "roots_sha256": _digest(roots),
    }
    closure_identity = {
        "schema_dependencies_sha256": _digest(dependency_edges),
        "schema_closures_sha256": _digest(schema_closures),
        "global_components_sha256": _digest(global_components),
        "xsd_builtin_types_sha256": _digest(builtin_nodes),
        "global_reference_uses_sha256": _digest(reference_uses),
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
        "identity": {
            **graph_identity,
            "graph_sha256": _digest(graph_identity),
        },
        "closure_identity": {
            **closure_identity,
            "closure_sha256": _digest(closure_identity),
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
            "resolution. Local particle semantics, anonymous types, occurrence "
            "and order rules, facets, inheritance edges, wildcards, "
            "documentation, and complete reachability remain open."
        ),
    }
