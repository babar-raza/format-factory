"""MaterialX (.mtlx) analytics — statistics derived from parsed documents.

Each function operates on a freshly-loaded document (path, bytes, or string
source); none require a pre-built MtlxDocument model object. Every function
calls load_mtlx() internally to parse the source into the canonical model
dict, then computes a metric over the shading-network/material structure.

Spec references: FACT-MTLX-002 (node graphs), FACT-MTLX-003 (materials).
"""
from __future__ import annotations

from typing import Any

from mtlx.mtlx_codec import SourceType, load_mtlx

__all__ = [
    "mtlx_node_type_histogram",
    "mtlx_materials_with_shader_count",
    "mtlx_node_graph_size",
]


def _node_display_type(node: dict[str, Any]) -> str:
    """Return the node's function/category label for histogram grouping.

    MaterialX distinguishes a node's *category* (its function, e.g.
    ``fractal3d``, ``mix``, ``image`` -- what kind of node it is) from its
    *data type* (e.g. ``float``, ``color3`` -- what kind of value it
    produces). Two nodes of different categories can share a data type
    (a ``fractal3d`` and a ``noise2d`` may both output ``float``) and must
    not be merged in a node-type histogram; conversely the same category
    commonly appears with several data types (an ``image`` node can output
    ``float`` or ``color3``) and those instances belong together.

    Resolution order (FACT-MTLX-103):
      1. ``node_category`` -- the parsed ``node`` XML attribute on a
         generic ``<node type="..." node="category">`` element.
      2. ``type`` field -- for *named-form* nodes (tag name itself is the
         category, e.g. ``<standard_surface>``), this already holds the
         category. Not used when the tag is the generic literal tag name
         ``"node"`` and no ``node_category`` was captured, since that literal
         tag name carries no category information by itself.
      3. ``node_type`` -- the data-type attribute, used only as a last
         resort when no category information is available at all (e.g. a
         malformed generic node missing its ``node`` attribute).
      4. ``"unknown"``.
    """
    node_category = node.get("node_category") or ""
    if node_category:
        return str(node_category)

    tag_name = node.get("type") or ""
    if tag_name and tag_name != "node":
        return str(tag_name)

    node_type = node.get("node_type") or ""
    if node_type:
        return str(node_type)

    data_type = (node.get("attributes") or {}).get("type") or ""
    if data_type:
        return str(data_type)

    return "unknown"


def mtlx_node_type_histogram(source: SourceType) -> dict[str, int]:
    """Count nodes by type across all node graphs and top-level nodes.

    Counts every node found inside each ``<nodegraph>`` element plus every
    top-level node element (outside any node graph or material). Node graph
    ``<output>`` elements and ``<surfacematerial>`` elements are not counted
    -- only node definitions contribute to the histogram.

    Spec: MaterialX node definitions contain typed inputs and outputs
    (FACT-MTLX-002).

    Args:
        source: Path, bytes, or string source accepted by ``load_mtlx()``.

    Returns:
        Mapping of node type label to occurrence count. Empty dict if the
        document has no node graphs or top-level nodes.
    """
    model = load_mtlx(source)
    histogram: dict[str, int] = {}

    for node_graph in model.get("node_graphs", []):
        for node in node_graph.get("nodes", []):
            label = _node_display_type(node)
            histogram[label] = histogram.get(label, 0) + 1

    for node in model.get("nodes", []):
        label = _node_display_type(node)
        histogram[label] = histogram.get(label, 0) + 1

    return histogram


def mtlx_materials_with_shader_count(source: SourceType) -> int:
    """Count materials (surfacematerial or volumematerial) bound to a shader.

    A material "has a shader binding" via either MaterialX connection form:
      - Current form: an ``<input name="surfaceshader">`` (or
        ``name="volumeshader"``) child whose ``nodename`` attribute
        references a shader node. Materials that only declare the input
        without a ``nodename`` (an unset value, e.g. ``value=""``) are not
        counted as connected.
      - Legacy form (FACT-MTLX-104): a nested ``<shaderref>`` element,
        which always represents an actual shader binding when present.

    Spec: surfacematerial/volumematerial bind to a shader node via a
    surfaceshader/volumeshader input connection or a legacy shaderref
    (FACT-MTLX-003, FACT-MTLX-104).

    Args:
        source: Path, bytes, or string source accepted by ``load_mtlx()``.

    Returns:
        Count of materials with a connected shader. 0 if the document has
        no materials or none are connected.
    """
    model = load_mtlx(source)
    count = 0
    for material in model.get("materials", []):
        if material.get("shaderrefs"):
            count += 1
            continue
        for inp in material.get("inputs", []):
            if inp.get("name") in ("surfaceshader", "volumeshader") and inp.get("nodename"):
                count += 1
                break
    return count


def mtlx_node_graph_size(source: SourceType) -> dict[str, int]:
    """Return the node count for each node graph, keyed by node graph name.

    Spec: node graphs contain node definitions connected by edges
    (FACT-MTLX-002).

    Args:
        source: Path, bytes, or string source accepted by ``load_mtlx()``.

    Returns:
        Mapping of node graph name to number of nodes it contains. Empty
        dict if the document has no node graphs.
    """
    model = load_mtlx(source)
    return {
        node_graph.get("name", ""): len(node_graph.get("nodes", []))
        for node_graph in model.get("node_graphs", [])
    }
