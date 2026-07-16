"""
MaterialX structural element: materialx:nodegraph

Spec ref: Academy Software Foundation MaterialX Specification v1.39
Fact ref: FACT-MTLX-002
QName: materialx:nodegraph
Canonical class: NodeGraph
Facade: MtlxNodeGraph
"""
from __future__ import annotations
from typing import Any, ClassVar


class NodeGraph:
    """Canonical spec-shaped class for materialx:nodegraph (a <nodegraph> element)."""

    spec_qname: ClassVar[str] = "materialx:nodegraph"
    spec_fact_ref: ClassVar[str] = "FACT-MTLX-002"
    namespace_uri: ClassVar[str] = "urn:format:materialx:1.39"
    local_name: ClassVar[str] = "nodegraph"
    facade_names: ClassVar[list] = ["MtlxNodeGraph"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    @property
    def name(self) -> str:
        """Return the node graph's ``name`` attribute value."""
        return str(self._data.get("name", ""))

    @property
    def nodes(self) -> list[dict[str, Any]]:
        """Return the list of node dicts contained in this node graph."""
        return list(self._data.get("nodes", []))

    @property
    def outputs(self) -> list[dict[str, str]]:
        """Return the list of ``<output>`` child element dicts."""
        return list(self._data.get("outputs", []))

    @property
    def node_count(self) -> int:
        """Return the number of nodes contained in this node graph."""
        return len(self.nodes)

    @property
    def output_count(self) -> int:
        """Return the number of ``<output>`` child elements."""
        return len(self.outputs)

    @property
    def is_empty(self) -> bool:
        """Return True if this node graph contains no nodes."""
        return self.node_count == 0

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow copy of the underlying data as a dict."""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"NodeGraph(name={self.name!r}, nodes={self.node_count})"
