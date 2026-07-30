"""Global QName-reference closure for UBL XML Schemas.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any
import xml.etree.ElementTree as ET

from tools.spec.ubl_schema_common import (
    GraphLimits,
    SchemaDocument,
    UblSchemaGraphError,
    XSD,
    XSD_NAMESPACE,
    digest,
    local_name,
    node_id,
    resolve_qname,
)


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


def _iter_schema_elements(
    root: ET.Element,
) -> Sequence[tuple[ET.Element, str]]:
    rows: list[tuple[ET.Element, str]] = []

    def visit(element: ET.Element, path: str) -> None:
        rows.append((element, path))
        sibling_counts: Counter[str] = Counter()
        for child in list(element):
            child_local_name = local_name(child.tag)
            sibling_counts[child_local_name] += 1
            visit(
                child,
                f"{path}/{child_local_name}"
                f"[{sibling_counts[child_local_name]}]",
            )

    visit(root, "/schema[1]")
    return rows


def _reference_target_kinds(
    element: ET.Element,
    attribute: str,
) -> tuple[str, ...]:
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
                f"unsupported XSD ref owner: {local_name(element.tag)}"
            )
        return (target,)
    raise UblSchemaGraphError(
        f"unsupported QName reference attribute: {attribute}"
    )


def compile_global_reference_uses(
    documents: Sequence[SchemaDocument],
    *,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
    reference_visibility: Mapping[str, frozenset[str]],
    limits: GraphLimits,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Resolve every supported QName-valued global reference exactly once."""

    uses: list[dict[str, Any]] = []
    builtin_nodes: dict[str, dict[str, Any]] = {}
    unresolved: list[str] = []
    for document in documents:
        for element, source_path in _iter_schema_elements(document.root):
            for attribute in _REFERENCE_ATTRIBUTES:
                lexical = element.get(attribute)
                if lexical is None:
                    continue
                values = (
                    lexical.split()
                    if attribute == "memberTypes"
                    else [lexical]
                )
                if not values:
                    raise UblSchemaGraphError(
                        f"empty {attribute} reference in "
                        f"{document.member}: {source_path}"
                    )
                target_kinds = _reference_target_kinds(element, attribute)
                for position, lexical_qname in enumerate(values, start=1):
                    target_qname = resolve_qname(
                        lexical_qname,
                        document=document,
                    )
                    namespace, target_local_name = target_qname[1:].split(
                        "}",
                        1,
                    )
                    target_kind: str
                    target_node_id: str
                    target_source_member: str
                    if namespace == XSD_NAMESPACE:
                        if target_kinds != ("complex_type", "simple_type"):
                            unresolved.append(
                                f"{document.member}:{source_path}@{attribute} "
                                f"cannot target XSD builtin {target_qname}"
                            )
                            continue
                        if target_local_name not in _XSD_BUILTIN_TYPES:
                            unresolved.append(
                                f"{document.member}:{source_path}@{attribute} "
                                f"unknown XSD builtin {target_qname}"
                            )
                            continue
                        target_kind = "xsd_builtin_type"
                        target_node_id = node_id(target_kind, target_qname)
                        target_source_member = ""
                        if target_qname not in builtin_nodes:
                            builtin: dict[str, Any] = {
                                "node_id": target_node_id,
                                "kind": target_kind,
                                "qname": target_qname,
                                "local_name": target_local_name,
                                "namespace": XSD_NAMESPACE,
                            }
                            builtin["sha256"] = digest(builtin)
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
                                f"resolves {len(candidates)} times: "
                                f"{target_qname}"
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
                                f"visibility: {target_qname} in "
                                f"{target_source_member}"
                            )
                            continue
                        target_kind = str(target["kind"])
                        target_node_id = str(target["node_id"])
                    core: dict[str, Any] = {
                        "source_member": document.member,
                        "source_member_sha256": document.member_sha256,
                        "source_path": source_path,
                        "source_tag": local_name(element.tag),
                        "attribute": attribute,
                        "attribute_position": position,
                        "lexical_qname": lexical_qname,
                        "target_qname": target_qname,
                        "target_kind": target_kind,
                        "target_node_id": target_node_id,
                        "target_source_member": target_source_member,
                    }
                    core["use_id"] = f"reference-use::{digest(core)}"
                    core["sha256"] = digest(core)
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
            "global reference closure failed: "
            + "; ".join(sorted(unresolved))
        )
    uses.sort(key=lambda value: str(value["use_id"]))
    builtins = [builtin_nodes[qname] for qname in sorted(builtin_nodes)]
    return uses, builtins
