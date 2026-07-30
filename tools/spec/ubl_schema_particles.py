"""Local particle, occurrence, and order graph for UBL XML Schemas.

The compiler records schema compositors and local element declarations as
content-addressed nodes. It deliberately does not flatten a compositor tree
into a bag of fields: parent identity and an explicit order path preserve the
sequence/choice structure needed by deterministic model generation.

generated_by: codex
visibility: internal
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any
import xml.etree.ElementTree as ET

from tools.spec.ubl_schema_common import (
    GraphLimits,
    SchemaDocument,
    UblSchemaGraphError,
    XSD,
    canonical_qname,
    digest,
    resolve_qname,
    schema_element_paths,
)


_PARTICLE_KINDS = {
    f"{XSD}all": "all",
    f"{XSD}any": "any",
    f"{XSD}choice": "choice",
    f"{XSD}element": "element",
    f"{XSD}group": "group_ref",
    f"{XSD}sequence": "sequence",
}
_OWNER_KINDS = {
    f"{XSD}complexType": "complex_type",
    f"{XSD}group": "model_group",
}
_WRAPPER_TAGS = {
    f"{XSD}complexContent",
    f"{XSD}extension",
    f"{XSD}restriction",
    f"{XSD}simpleContent",
}
_NON_NEGATIVE_INTEGER = re.compile(r"\+?[0-9]+")


def _occurrence(
    lexical: str | None,
    *,
    default: int,
    allow_unbounded: bool,
    document: SchemaDocument,
    source_path: str,
    attribute: str,
) -> int | str:
    if lexical is None:
        return default
    value = lexical.strip()
    if allow_unbounded and value == "unbounded":
        return value
    if _NON_NEGATIVE_INTEGER.fullmatch(value) is None:
        raise UblSchemaGraphError(
            f"invalid {attribute} in {document.member}:{source_path}: {lexical}"
        )
    return int(value)


def _boolean(
    lexical: str | None,
    *,
    default: bool,
    document: SchemaDocument,
    source_path: str,
    attribute: str,
) -> bool:
    if lexical is None:
        return default
    if lexical in {"true", "1"}:
        return True
    if lexical in {"false", "0"}:
        return False
    raise UblSchemaGraphError(
        f"invalid {attribute} in {document.member}:{source_path}: {lexical}"
    )


def _particle_roots(owner: ET.Element) -> list[ET.Element]:
    roots: list[ET.Element] = []

    def visit_wrapper(element: ET.Element) -> None:
        for child in list(element):
            if child.tag in _PARTICLE_KINDS:
                roots.append(child)
            elif child.tag in _WRAPPER_TAGS:
                visit_wrapper(child)

    visit_wrapper(owner)
    return roots


def _particle_fields(
    element: ET.Element,
    *,
    kind: str,
    document: SchemaDocument,
    source_path: str,
) -> dict[str, Any]:
    min_occurs = _occurrence(
        element.get("minOccurs"),
        default=1,
        allow_unbounded=False,
        document=document,
        source_path=source_path,
        attribute="minOccurs",
    )
    max_occurs = _occurrence(
        element.get("maxOccurs"),
        default=1,
        allow_unbounded=True,
        document=document,
        source_path=source_path,
        attribute="maxOccurs",
    )
    if not isinstance(min_occurs, int):
        raise AssertionError("minOccurs cannot be unbounded")
    if isinstance(max_occurs, int) and max_occurs < min_occurs:
        raise UblSchemaGraphError(
            f"maxOccurs is less than minOccurs in "
            f"{document.member}:{source_path}"
        )

    name = ""
    ref_qname = ""
    type_qname = ""
    nillable = False
    default_value: str | None = None
    fixed_value: str | None = None
    form = ""
    namespace_constraint = ""
    process_contents = ""

    if kind == "element":
        declared_name = element.get("name")
        lexical_ref = element.get("ref")
        if bool(declared_name) == bool(lexical_ref):
            raise UblSchemaGraphError(
                f"local element must declare exactly one of name or ref in "
                f"{document.member}:{source_path}"
            )
        lexical_type = element.get("type")
        nillable = _boolean(
            element.get("nillable"),
            default=False,
            document=document,
            source_path=source_path,
            attribute="nillable",
        )
        default_value = element.get("default")
        fixed_value = element.get("fixed")
        if default_value is not None and fixed_value is not None:
            raise UblSchemaGraphError(
                f"local element cannot declare both default and fixed in "
                f"{document.member}:{source_path}"
            )
        if lexical_ref:
            forbidden = [
                attribute
                for attribute in (
                    "abstract",
                    "block",
                    "default",
                    "final",
                    "fixed",
                    "form",
                    "name",
                    "nillable",
                    "type",
                )
                if element.get(attribute) is not None
            ]
            if forbidden:
                raise UblSchemaGraphError(
                    f"referenced local element carries prohibited attributes "
                    f"in {document.member}:{source_path}: "
                    + ", ".join(sorted(forbidden))
                )
            ref_qname = resolve_qname(lexical_ref, document=document)
        else:
            name = declared_name or ""
            explicit_form = element.get("form")
            if explicit_form not in {None, "qualified", "unqualified"}:
                raise UblSchemaGraphError(
                    f"invalid element form in "
                    f"{document.member}:{source_path}: {explicit_form}"
                )
            form = explicit_form or document.element_form_default
            if lexical_type:
                type_qname = resolve_qname(lexical_type, document=document)
    elif kind == "group_ref":
        lexical_ref = element.get("ref")
        if not lexical_ref or element.get("name"):
            raise UblSchemaGraphError(
                f"local group particle must declare one ref in "
                f"{document.member}:{source_path}"
            )
        ref_qname = resolve_qname(lexical_ref, document=document)
    elif kind == "any":
        namespace_constraint = element.get("namespace", "##any")
        process_contents = element.get("processContents", "strict")

    return {
        "min_occurs": min_occurs,
        "max_occurs": max_occurs,
        "name": name,
        "ref_qname": ref_qname,
        "type_qname": type_qname,
        "nillable": nillable,
        "default": default_value,
        "fixed": fixed_value,
        "form": form,
        "namespace_constraint": namespace_constraint,
        "process_contents": process_contents,
    }


def compile_local_particles(
    documents: Sequence[SchemaDocument],
    *,
    components: Mapping[tuple[str, str], Mapping[str, Any]],
    limits: GraphLimits,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Compile local particle trees without claiming full type reachability."""

    particles: list[dict[str, Any]] = []
    containment_edges: list[dict[str, Any]] = []

    def visit_particle(
        element: ET.Element,
        *,
        document: SchemaDocument,
        paths: Mapping[int, str],
        owner_node_id: str,
        parent_particle_id: str,
        parent_kind: str | None,
        order_path: tuple[int, ...],
    ) -> None:
        kind = _PARTICLE_KINDS[element.tag]
        source_path = paths[id(element)]
        fields = _particle_fields(
            element,
            kind=kind,
            document=document,
            source_path=source_path,
        )
        if kind == "all" and (
            fields["min_occurs"] not in {0, 1}
            or fields["max_occurs"] != 1
        ):
            raise UblSchemaGraphError(
                f"all compositor occurrence must be 0..1 or 1..1 in "
                f"{document.member}:{source_path}"
            )
        if parent_kind == "all" and (
            kind != "element"
            or fields["min_occurs"] not in {0, 1}
            or fields["max_occurs"] not in {0, 1}
        ):
            raise UblSchemaGraphError(
                f"all compositor children must be 0..1 or 1..1 elements in "
                f"{document.member}:{source_path}"
            )
        core: dict[str, Any] = {
            "kind": kind,
            "source_member": document.member,
            "source_member_sha256": document.member_sha256,
            "source_path": source_path,
            "owner_node_id": owner_node_id,
            "parent_particle_id": parent_particle_id,
            "order_path": list(order_path),
            **fields,
        }
        particle_sha256 = digest(core)
        particle_id = f"particle::{particle_sha256}"
        row = {
            **core,
            "particle_id": particle_id,
            "sha256": particle_sha256,
        }
        particles.append(row)
        edge_core: dict[str, Any] = {
            "kind": "contains_particle",
            "source_node_id": parent_particle_id,
            "target_node_id": particle_id,
            "owner_node_id": owner_node_id,
            "source_member": document.member,
            "order_path": list(order_path),
        }
        edge_sha256 = digest(edge_core)
        containment_edges.append(
            {
                **edge_core,
                "edge_id": f"particle-edge::{edge_sha256}",
                "sha256": edge_sha256,
            }
        )
        if len(particles) > limits.max_graph_nodes:
            raise UblSchemaGraphError("graph node limit exceeded")
        if len(containment_edges) > limits.max_graph_edges:
            raise UblSchemaGraphError("graph edge limit exceeded")

        child_position = 0
        for child in list(element):
            if child.tag not in _PARTICLE_KINDS:
                continue
            child_position += 1
            visit_particle(
                child,
                document=document,
                paths=paths,
                owner_node_id=owner_node_id,
                parent_particle_id=particle_id,
                parent_kind=kind,
                order_path=(*order_path, child_position),
            )

    for document in sorted(documents, key=lambda item: item.member):
        paths = schema_element_paths(document.root)
        for owner in list(document.root):
            owner_kind = _OWNER_KINDS.get(owner.tag)
            owner_name = owner.get("name")
            if owner_kind is None or not owner_name:
                continue
            owner_qname = canonical_qname(document.target_namespace, owner_name)
            owner_component = components.get((owner_kind, owner_qname))
            if owner_component is None:
                raise UblSchemaGraphError(
                    f"particle owner is not indexed: {owner_kind} {owner_qname}"
                )
            owner_node_id = str(owner_component["node_id"])
            for root_position, particle_root in enumerate(
                _particle_roots(owner),
                start=1,
            ):
                visit_particle(
                    particle_root,
                    document=document,
                    paths=paths,
                    owner_node_id=owner_node_id,
                    parent_particle_id=owner_node_id,
                    parent_kind=None,
                    order_path=(root_position,),
                )

    particles.sort(
        key=lambda row: (
            str(row["source_member"]),
            str(row["owner_node_id"]),
            list(row["order_path"]),
        )
    )
    containment_edges.sort(key=lambda row: str(row["edge_id"]))
    if len({str(row["particle_id"]) for row in particles}) != len(particles):
        raise UblSchemaGraphError("duplicate local particle identity")
    if len({str(row["edge_id"]) for row in containment_edges}) != len(
        containment_edges
    ):
        raise UblSchemaGraphError("duplicate particle containment edge")
    return particles, containment_edges
