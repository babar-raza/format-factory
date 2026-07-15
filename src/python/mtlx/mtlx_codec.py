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
    "shader_nodes",
    "inputs_outputs",
    "size_guard",
]

UNSUPPORTED_FEATURES = [
    "color_management",
    "geometry_bindings",
    "looks",
    "collections",
    "property_sets",
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

        if local == "surfacematerial":
            materials.append({
                "name": child.get("name", ""),
                "type": local,
                "inputs": _parse_inputs(child),
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
                    })
                else:
                    ng_nodes.append({
                        "name": ng_child.get("name", ""),
                        "type": ng_local,
                        "node_type": ng_child.get("type", ""),
                        "inputs": _parse_inputs(ng_child),
                    })

            node_graphs.append({
                "name": child.get("name", ""),
                "nodes": ng_nodes,
                "outputs": ng_outputs,
            })

        else:
            node_data: dict[str, Any] = {
                "name": child.get("name", ""),
                "type": local,
                "inputs": _parse_inputs(child),
                "outputs": _parse_outputs(child),
            }
            nodes.append(node_data)

    return {
        "version": version,
        "materials": materials,
        "node_graphs": node_graphs,
        "nodes": nodes,
    }


def write_mtlx(
    model: dict[str, Any],
    dest: Union[str, Path, None] = None,
) -> str:
    """Serialize a MaterialX model dict to XML string."""
    version = model.get("version", "1.39")

    root = ET.Element("materialx")
    root.set("version", version)

    for mat in model.get("materials", []):
        mat_elem = ET.SubElement(root, "surfacematerial")
        mat_elem.set("name", mat.get("name", ""))
        for inp in mat.get("inputs", []):
            inp_elem = ET.SubElement(mat_elem, "input")
            for k, v in inp.items():
                if v:
                    inp_elem.set(k, v)

    for ng in model.get("node_graphs", []):
        ng_elem = ET.SubElement(root, "nodegraph")
        ng_elem.set("name", ng.get("name", ""))
        for node in ng.get("nodes", []):
            node_elem = ET.SubElement(ng_elem, node.get("type", "node"))
            node_elem.set("name", node.get("name", ""))
            if node.get("node_type"):
                node_elem.set("type", node["node_type"])
            for inp in node.get("inputs", []):
                inp_elem = ET.SubElement(node_elem, "input")
                for k, v in inp.items():
                    if v:
                        inp_elem.set(k, v)
        for out in ng.get("outputs", []):
            out_elem = ET.SubElement(ng_elem, "output")
            for k, v in out.items():
                if v:
                    out_elem.set(k, v)

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
