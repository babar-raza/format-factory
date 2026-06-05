"""
requirement_graph.py — Build requirement linkage graph from verified requirements.

Links:
  SpecRequirementRef → derived_from → ProductRequirement
  ProductRequirement → sourced_from → SpecSource

Stored as .local/spec-artifacts/{source_id}-req-graph.json
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SpecReqNode:
    node_id: str
    node_type: str  # SpecRequirementRef | ProductRequirement | SpecSource
    source_id: str
    format_id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "source_id": self.source_id,
            "format_id": self.format_id,
            "label": self.label,
            "properties": self.properties,
        }


@dataclass
class SpecReqEdge:
    edge_id: str
    edge_type: str  # derived_from | sourced_from | verified_by
    from_node: str
    to_node: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "edge_type": self.edge_type,
            "from_node": self.from_node,
            "to_node": self.to_node,
        }


@dataclass
class RequirementGraph:
    source_id: str
    format_id: str
    nodes: List[SpecReqNode] = field(default_factory=list)
    edges: List[SpecReqEdge] = field(default_factory=list)
    built_at: str = field(default_factory=_now_iso)

    def add_node(self, node: SpecReqNode) -> None:
        self.nodes.append(node)

    def add_edge(self, edge: SpecReqEdge) -> None:
        self.edges.append(edge)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "format_id": self.format_id,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "built_at": self.built_at,
        }


def build_requirement_graph(
    source_id: str,
    format_id: str,
    requirements: List[Dict[str, Any]],
    verified_results: Optional[List[Dict[str, Any]]] = None,
    artifacts_dir: Optional[str] = None,
) -> RequirementGraph:
    """
    Build a linkage graph from extracted and (optionally) verified requirements.
    """
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    art_root.mkdir(parents=True, exist_ok=True)

    # Build verification lookup
    verified_lookup: Dict[str, str] = {}
    if verified_results:
        for vr in verified_results:
            if isinstance(vr, dict):
                verified_lookup[vr.get("req_id", "")] = vr.get("status", "UNKNOWN")
            else:
                verified_lookup[vr.req_id] = vr.status

    graph = RequirementGraph(source_id=source_id, format_id=format_id)

    # SpecSource node
    source_node_id = f"SS-{source_id}"
    graph.add_node(SpecReqNode(
        node_id=source_node_id,
        node_type="SpecSource",
        source_id=source_id,
        format_id=format_id,
        label=f"SpecSource:{source_id}",
    ))

    for req in requirements:
        req_id = req.get("req_id", f"REQ-{uuid.uuid4().hex[:8]}")
        section_id = req.get("section_id", "")
        heading = req.get("heading", "")
        text = req.get("text_fragment", "")[:100]
        verification_status = verified_lookup.get(req_id, "UNVERIFIED")

        # SpecRequirementRef node
        sref_id = f"SREF-{req_id}"
        graph.add_node(SpecReqNode(
            node_id=sref_id,
            node_type="SpecRequirementRef",
            source_id=source_id,
            format_id=format_id,
            label=f"§{section_id}: {text[:50]}",
            properties={
                "req_id": req_id,
                "section_id": section_id,
                "heading": heading,
                "keyword": req.get("keyword", ""),
                "verification_status": verification_status,
            },
        ))

        # sourced_from edge: SpecRequirementRef → SpecSource
        graph.add_edge(SpecReqEdge(
            edge_id=f"E-{uuid.uuid4().hex[:8]}",
            edge_type="sourced_from",
            from_node=sref_id,
            to_node=source_node_id,
        ))

    # Store graph
    graph_path = art_root / f"{source_id}-req-graph.json"
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph.to_dict(), f, indent=2)

    return graph


def load_requirement_graph(source_id: str, artifacts_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load a stored requirement graph."""
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    graph_path = art_root / f"{source_id}-req-graph.json"
    if not graph_path.exists():
        return None
    with open(graph_path, "r", encoding="utf-8") as f:
        return json.load(f)
