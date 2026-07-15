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
    """Return the most specific type label for a parsed node dict.

    Node-graph children carry a ``node_type`` field (the MaterialX data-type
    attribute, e.g. ``float``, ``color3``) in addition to a ``type`` field
    that holds the XML tag's local name. Top-level nodes only carry ``type``.
    The more specific ``node_type`` is preferred when present and non-empty.
    """
    node_type = node.get("node_type") or ""
    if node_type:
        return str(node_type)
    return str(node.get("type") or "unknown")


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
    """Count materials whose surfaceshader input is connected to a shader node.

    A ``<surfacematerial>`` "has a shader input connection" when it carries
    an ``<input name="surfaceshader">`` child whose ``nodename`` attribute
    references a shader node. Materials that only declare the input without
    a ``nodename`` (an unset value, e.g. ``value=""``) are not counted
    as connected.

    Spec: surfacematerial binds to a shader node via a surfaceshader input
    connection (FACT-MTLX-003).

    Args:
        source: Path, bytes, or string source accepted by ``load_mtlx()``.

    Returns:
        Count of materials with a connected surfaceshader input. 0 if the
        document has no materials or none are connected.
    """
    model = load_mtlx(source)
    count = 0
    for material in model.get("materials", []):
        for inp in material.get("inputs", []):
            if inp.get("name") == "surfaceshader" and inp.get("nodename"):
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
