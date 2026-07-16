"""MaterialX (.mtlx) codec — probe, load, write.

XML format for materials and shading networks.
Detection: root element is ``materialx`` (case-insensitive).

Spec reference: FACT-MTLX-001
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Union

from mtlx.exceptions import MtlxParseError, MtlxWriteError

MAX_FILE_SIZE = 64 * 1024 * 1024  # 64 MiB guard

SUPPORTED_FEATURES = [
    "probe",
    "load",
    "write",
    "materials",
    "node_graphs",
    "surface_materials",
    "volume_materials",
    "legacy_shaderref_bindinput",
    "shader_nodes",
    "node_category",
    "inputs_outputs",
    "generic_element_preservation",
    "size_guard",
]

# Structural round-trip preservation of these elements is supported (see
# mtlx.mtlx_codec._serialize_nodes / _parse_generic_element -- FACT-MTLX-101):
# a nodedef, typedef, look, or propertyset survives load -> write unchanged.
# This also covers <nodegraph>-level attributes (nodedef/fileprefix/...) and
# non-input/output children of graph-internal nodes (e.g. <xpos>/<ypos>
# layout hints) as of TC-S6P4-PROD-002 (select-6 Phase 4, 2026-07-16) -- a
# prior gap here (D2) was found by an independent audit constructing a
# <nodegraph nodedef="..." fileprefix="..."> with an internal node carrying
# a non-input/output child, neither of which the original fix's own test
# suite happened to cover. A graph-internal <output> element's own extra
# attributes and non-structural children are likewise preserved as of
# TC-S6P4-FINAL-001a (2026-07-16) -- a second independent re-audit found
# PROD-002's fix had not extended to the <output> branch (the node branch's
# sibling), which still silently dropped anything beyond name/type/nodename.
# What remains unsupported is *semantic* interpretation of that structure --
# resolving a look's material assignments, validating a nodedef against the
# standard node library, or evaluating variant/collection membership.
UNSUPPORTED_FEATURES = [
    "color_management",
    "geometry_bindings",
    "look_semantic_resolution",
    "collection_semantic_resolution",
    "variant_semantic_resolution",
    "nodedef_library_validation",
    "xinclude_multi_file_resolution",
    "streaming_parse",
]

SourceType = Union[str, Path, bytes]


def _read_source(source: SourceType) -> bytes:
    """Read source into bytes."""
    if isinstance(source, bytes):
        return source
    path = Path(source)
    if not path.exists():
        raise MtlxParseError(f"File not found: {source}")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise MtlxParseError(f"File exceeds {MAX_FILE_SIZE} byte limit: {size} bytes")
    return path.read_bytes()


def _strip_ns(tag: str) -> str:
    """Remove namespace prefix from tag."""
    if tag.startswith("{"):
        return tag[tag.index("}") + 1 :]
    return tag


def probe_mtlx(source: SourceType) -> bool:
    """Return True if source is a valid MaterialX file. Never raises."""
    try:
        data = _read_source(source)
        root = ET.fromstring(data)
        return _strip_ns(root.tag).lower() == "materialx"
    except Exception:
        return False


def _parse_inputs(elem: ET.Element) -> list[dict[str, str]]:
    """Extract input elements from a node or material."""
    inputs: list[dict[str, str]] = []
    for child in elem:
        local = _strip_ns(child.tag)
        if local == "input":
            inputs.append({
                "name": child.get("name", ""),
                "type": child.get("type", ""),
                "value": child.get("value", ""),
                "nodename": child.get("nodename", ""),
                "interfacename": child.get("interfacename", ""),
                "output": child.get("output", ""),
            })
    return inputs


def _parse_outputs(elem: ET.Element) -> list[dict[str, str]]:
    """Extract output elements from a node."""
    outputs: list[dict[str, str]] = []
    for child in elem:
        local = _strip_ns(child.tag)
        if local == "output":
            outputs.append({
                "name": child.get("name", ""),
                "type": child.get("type", ""),
                "nodename": child.get("nodename", ""),
            })
    return outputs


# Material element tags recognized by MaterialX v1.39 (FACT-MTLX-104).
# ``volumematerial`` sits alongside ``surfacematerial`` as a first-class
# material type -- both bind a shader to geometry, differing only in the
# shading model (surface vs. volume) they connect to.
_MATERIAL_TAGS = ("surfacematerial", "volumematerial")

# Structural child tags that already receive dedicated, semantically-typed
# parsing (``_parse_inputs``/``_parse_outputs``). Anything else nested inside
# a generic top-level element is captured verbatim by ``_parse_generic_element``
# so it survives a write-back unchanged (FACT-MTLX-101).
_STRUCTURAL_CHILD_TAGS = ("input", "output")


def _parse_shaderrefs(elem: ET.Element) -> list[dict[str, Any]]:
    """Extract legacy ``<shaderref>``/``<bindinput>`` shader bindings (FACT-MTLX-104).

    Pre-1.38 MaterialX documents bind a material to its shader via a nested
    ``<shaderref>`` element (whose ``node`` attribute names the shader
    category) containing ``<bindinput>`` parameter bindings, instead of the
    newer ``<input name="surfaceshader" nodename="...">`` connection form.
    Both forms may appear on the same material; this only parses the legacy
    form so callers can detect and use whichever is present.
    """
    shaderrefs: list[dict[str, Any]] = []
    for child in elem:
        if _strip_ns(child.tag) != "shaderref":
            continue
        bindinputs: list[dict[str, str]] = []
        for bi in child:
            if _strip_ns(bi.tag) != "bindinput":
                continue
            bindinputs.append({
                "name": bi.get("name", ""),
                "type": bi.get("type", ""),
                "value": bi.get("value", ""),
                "output": bi.get("output", ""),
                "nodegraph": bi.get("nodegraph", ""),
            })
        shaderrefs.append({
            "name": child.get("name", ""),
            "node": child.get("node", ""),
            "bindinputs": bindinputs,
        })
    return shaderrefs


def _parse_generic_element(elem: ET.Element) -> dict[str, Any]:
    """Recursively capture an arbitrary XML element: tag, attributes, text, children.

    Used to preserve element kinds this codec does not model in dedicated
    structure (e.g. ``<materialassign>`` inside a ``<look>``, ``<property>``
    inside a ``<propertyset>``, ``<member>`` inside a ``<typedef>``) so that
    a load -> write round trip never silently drops them.
    """
    text = (elem.text or "").strip()
    return {
        "tag": _strip_ns(elem.tag),
        "attributes": dict(elem.attrib),
        "text": text,
        "children": [_parse_generic_element(child) for child in elem],
    }


def load_mtlx(source: SourceType) -> dict[str, Any]:
    """Parse a MaterialX file and return a canonical model dict."""
    data = _read_source(source)
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise MtlxParseError(f"Invalid XML: {exc}") from exc

    if _strip_ns(root.tag).lower() != "materialx":
        raise MtlxParseError(
            f"Not a MaterialX document: root element is '{_strip_ns(root.tag)}'"
        )

    version = root.get("version", "")

    materials: list[dict[str, Any]] = []
    node_graphs: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []

    for child in root:
        local = _strip_ns(child.tag)

        if local in _MATERIAL_TAGS:
            materials.append({
                "name": child.get("name", ""),
                "type": local,
                "inputs": _parse_inputs(child),
                "shaderrefs": _parse_shaderrefs(child),
            })

        elif local == "nodegraph":
            ng_nodes: list[dict[str, Any]] = []
            ng_outputs: list[dict[str, str]] = []

            for ng_child in child:
                ng_local = _strip_ns(ng_child.tag)
                if ng_local == "output":
                    ng_outputs.append({
                        "name": ng_child.get("name", ""),
                        "type": ng_child.get("type", ""),
                        "nodename": ng_child.get("nodename", ""),
                        # TC-S6P4-FINAL-001a (select-6 Phase 4 final re-audit,
                        # 2026-07-16): an independent adversarial re-check of
                        # TC-S6P4-PROD-002 (D2) found a graph-internal
                        # <output> element -- the sibling of the node branch
                        # this same taskcard already fixed -- still dropped
                        # any attribute beyond name/type/nodename and any
                        # non-structural child, the exact defect class one
                        # tag over. Captured generically here the same way
                        # the node branch already is, instead of adding a
                        # third hardcoded attribute name to the allowlist.
                        "attributes": {
                            k: v for k, v in ng_child.attrib.items()
                            if k not in ("name", "type", "nodename")
                        },
                        "children": [
                            _parse_generic_element(gc)
                            for gc in ng_child
                            if _strip_ns(gc.tag) not in _STRUCTURAL_CHILD_TAGS
                        ],
                    })
                else:
                    ng_nodes.append({
                        "name": ng_child.get("name", ""),
                        "type": ng_local,
                        "node_type": ng_child.get("type", ""),
                        "node_category": ng_child.get("node", ""),
                        "inputs": _parse_inputs(ng_child),
                        # TC-S6P4-PROD-002 (select-6 Phase 4, closes D2): a
                        # graph-internal node's non-input/output children
                        # (e.g. <xpos>/<ypos> UI-layout hints) used to be
                        # silently dropped -- capture them the same way a
                        # top-level node's children already are.
                        "children": [
                            _parse_generic_element(gc)
                            for gc in ng_child
                            if _strip_ns(gc.tag) not in _STRUCTURAL_CHILD_TAGS
                        ],
                    })

            node_graphs.append({
                "name": child.get("name", ""),
                # TC-S6P4-PROD-002 (closes D2): the <nodegraph> element's own
                # attributes beyond `name` (e.g. nodedef, fileprefix) used to
                # be silently dropped on write -- capture them here.
                "attributes": {
                    k: v for k, v in child.attrib.items() if k != "name"
                },
                "nodes": ng_nodes,
                "outputs": ng_outputs,
            })

        else:
            node_data: dict[str, Any] = {
                "name": child.get("name", ""),
                "type": local,
                "node_category": child.get("node", ""),
                "attributes": {
                    k: v for k, v in child.attrib.items() if k != "name"
                },
                "inputs": _parse_inputs(child),
                "outputs": _parse_outputs(child),
                "children": [
                    _parse_generic_element(gc)
                    for gc in child
                    if _strip_ns(gc.tag) not in _STRUCTURAL_CHILD_TAGS
                ],
            }
            nodes.append(node_data)

    return {
        "version": version,
        "materials": materials,
        "node_graphs": node_graphs,
        "nodes": nodes,
    }


def _serialize_generic_element(parent: ET.Element, data: dict[str, Any]) -> None:
    """Recursively write back an element captured by ``_parse_generic_element``."""
    elem = ET.SubElement(parent, data.get("tag", "unknown"))
    for k, v in data.get("attributes", {}).items():
        if v:
            elem.set(k, v)
    if data.get("text"):
        elem.text = data["text"]
    for child_data in data.get("children", []):
        _serialize_generic_element(elem, child_data)


def _serialize_nodes(root: ET.Element, nodes: list[dict[str, Any]]) -> None:
    """Serialize the generic top-level nodes bucket onto ``root`` (FACT-MTLX-101).

    Before this fix, ``write_mtlx`` only serialized ``model["materials"]``
    and ``model["node_graphs"]`` -- every other top-level construct
    (``nodedef``, ``typedef``, ``look``, ``propertyset``, plain node
    instances outside any node graph, all of which ``load_mtlx`` buckets
    into ``model["nodes"]``) was silently dropped on write. This restores
    them using the same attribute/input/output/children structure
    ``load_mtlx`` captured, so a load -> write -> load cycle is lossless.
    """
    for node in nodes:
        tag = node.get("type") or "node"
        node_elem = ET.SubElement(root, tag)
        node_elem.set("name", node.get("name", ""))
        for k, v in node.get("attributes", {}).items():
            if v and k != "name":
                node_elem.set(k, v)
        for inp in node.get("inputs", []):
            inp_elem = ET.SubElement(node_elem, "input")
            for k, v in inp.items():
                if v:
                    inp_elem.set(k, v)
        for out in node.get("outputs", []):
            out_elem = ET.SubElement(node_elem, "output")
            for k, v in out.items():
                if v:
                    out_elem.set(k, v)
        for child_data in node.get("children", []):
            _serialize_generic_element(node_elem, child_data)


def write_mtlx(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> str:
    """Serialize a MaterialX model dict to XML string."""
    version = model.get("version", "1.39")

    root = ET.Element("materialx")
    root.set("version", version)

    for mat in model.get("materials", []):
        mat_elem = ET.SubElement(root, mat.get("type") or "surfacematerial")
        mat_elem.set("name", mat.get("name", ""))
        for inp in mat.get("inputs", []):
            inp_elem = ET.SubElement(mat_elem, "input")
            for k, v in inp.items():
                if v:
                    inp_elem.set(k, v)
        for sr in mat.get("shaderrefs", []):
            sr_elem = ET.SubElement(mat_elem, "shaderref")
            sr_elem.set("name", sr.get("name", ""))
            if sr.get("node"):
                sr_elem.set("node", sr["node"])
            for bi in sr.get("bindinputs", []):
                bi_elem = ET.SubElement(sr_elem, "bindinput")
                for k, v in bi.items():
                    if v:
                        bi_elem.set(k, v)

    for ng in model.get("node_graphs", []):
        ng_elem = ET.SubElement(root, "nodegraph")
        ng_elem.set("name", ng.get("name", ""))
        # TC-S6P4-PROD-002 (closes D2): write back the graph's own extra
        # attributes (nodedef, fileprefix, ...) captured by load_mtlx.
        for k, v in ng.get("attributes", {}).items():
            if v and k != "name":
                ng_elem.set(k, v)
        for node in ng.get("nodes", []):
            node_elem = ET.SubElement(ng_elem, node.get("type", "node"))
            node_elem.set("name", node.get("name", ""))
            if node.get("node_type"):
                node_elem.set("type", node["node_type"])
            if node.get("node_category"):
                node_elem.set("node", node["node_category"])
            for inp in node.get("inputs", []):
                inp_elem = ET.SubElement(node_elem, "input")
                for k, v in inp.items():
                    if v:
                        inp_elem.set(k, v)
            # TC-S6P4-PROD-002 (closes D2): write back non-input/output
            # children of graph-internal nodes.
            for child_data in node.get("children", []):
                _serialize_generic_element(node_elem, child_data)
        for out in ng.get("outputs", []):
            out_elem = ET.SubElement(ng_elem, "output")
            for k in ("name", "type", "nodename"):
                if out.get(k):
                    out_elem.set(k, out[k])
            # TC-S6P4-FINAL-001a (closes the residual D2 gap found by the
            # final independent re-audit): write back a graph-internal
            # <output>'s extra attributes and non-structural children, the
            # same as the sibling node branch above.
            for k, v in out.get("attributes", {}).items():
                if v:
                    out_elem.set(k, v)
            for child_data in out.get("children", []):
                _serialize_generic_element(out_elem, child_data)

    _serialize_nodes(root, model.get("nodes", []))

    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    result = ET.tostring(root, encoding="unicode", xml_declaration=True)

    if dest is not None:
        path = Path(dest)
        try:
            path.write_text(result, encoding="utf-8")
        except OSError as exc:
            raise MtlxWriteError(f"Cannot write to {path}: {exc}") from exc

    return result


def get_material_count(model: dict[str, Any]) -> int:
    """Return number of materials."""
    return len(model.get("materials", []))


def get_node_graph_count(model: dict[str, Any]) -> int:
    """Return number of node graphs."""
    return len(model.get("node_graphs", []))


def roundtrip(source: SourceType, dest: Union[str, Path]) -> dict[str, Any]:
    """Load a MaterialX file, write it, and reload."""
    model = load_mtlx(source)
    write_mtlx(model, dest)
    return load_mtlx(dest)


def mtlx_installed_workflow(source: SourceType) -> dict[str, Any]:
    """Return format metadata for a MaterialX source (installed-package proof)."""
    model = load_mtlx(source)
    return {
        "format": "mtlx",
        "loaded": True,
        "version": model.get("version", ""),
        "material_count": get_material_count(model),
        "node_graph_count": get_node_graph_count(model),
    }
