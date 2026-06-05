"""
Graph store: read/write JSONL nodes and edges, compute graph hash,
perform deterministic sort, query incoming/outgoing edges.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import GraphNode, GraphEdge


class GraphStore:
    """In-memory store for proof graph nodes and edges."""

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    # ── I/O ────────────────────────────────────────────────────────────────────

    def load_nodes(self, path: Path) -> None:
        """Load nodes from a JSONL file."""
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    d = json.loads(line)
                    node = GraphNode.from_dict(d)
                    self.nodes[node.node_id] = node

    def load_edges(self, path: Path) -> None:
        """Load edges from a JSONL file."""
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    d = json.loads(line)
                    self.edges.append(GraphEdge.from_dict(d))

    def save_nodes(self, path: Path) -> None:
        """Write nodes to a JSONL file (sorted by node_id for determinism)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: (n.node_type, n.node_id))
        with open(path, "w", encoding="utf-8") as f:
            for node in sorted_nodes:
                f.write(json.dumps(node.to_dict(), sort_keys=True) + "\n")

    def save_edges(self, path: Path) -> None:
        """Write edges to a JSONL file (sorted for determinism)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        sorted_edges = sorted(
            self.edges,
            key=lambda e: (e.edge_type, e.source_node_id, e.target_node_id)
        )
        with open(path, "w", encoding="utf-8") as f:
            for edge in sorted_edges:
                f.write(json.dumps(edge.to_dict(), sort_keys=True) + "\n")

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, edge: GraphEdge) -> None:
        # Deduplicate by edge_id
        existing_ids = {e.edge_id for e in self.edges}
        if edge.edge_id not in existing_ids:
            self.edges.append(edge)

    # ── Queries ────────────────────────────────────────────────────────────────

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_outgoing(self, node_id: str, edge_type: Optional[str] = None) -> List[GraphEdge]:
        """Return all edges with source=node_id, optionally filtered by type."""
        result = [e for e in self.edges if e.source_node_id == node_id]
        if edge_type:
            result = [e for e in result if e.edge_type == edge_type]
        return result

    def get_incoming(self, node_id: str, edge_type: Optional[str] = None) -> List[GraphEdge]:
        """Return all edges with target=node_id, optionally filtered by type."""
        result = [e for e in self.edges if e.target_node_id == node_id]
        if edge_type:
            result = [e for e in result if e.edge_type == edge_type]
        return result

    def get_targets(self, node_id: str, edge_type: str) -> List[GraphNode]:
        """Return target nodes for outgoing edges of given type from node_id."""
        targets = []
        for e in self.get_outgoing(node_id, edge_type):
            node = self.get_node(e.target_node_id)
            if node:
                targets.append(node)
        return targets

    def get_sources(self, node_id: str, edge_type: str) -> List[GraphNode]:
        """Return source nodes for incoming edges of given type to node_id."""
        sources = []
        for e in self.get_incoming(node_id, edge_type):
            node = self.get_node(e.source_node_id)
            if node:
                sources.append(node)
        return sources

    def nodes_by_type(self, node_type: str) -> List[GraphNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    # ── Graph hash ─────────────────────────────────────────────────────────────

    def compute_graph_hash(self) -> str:
        """
        Compute deterministic SHA-256 of sorted nodes+edges content.
        Same inputs always produce the same hash.
        """
        node_lines = sorted(
            json.dumps(n.to_dict(), sort_keys=True)
            for n in self.nodes.values()
        )
        edge_lines = sorted(
            json.dumps(e.to_dict(), sort_keys=True)
            for e in self.edges
        )
        content = "\n".join(node_lines + edge_lines)
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def load_from_dir(cls, graph_dir: Path) -> "GraphStore":
        """Load a GraphStore from a directory containing nodes.jsonl and edges.jsonl."""
        store = cls()
        nodes_path = graph_dir / "nodes.jsonl"
        edges_path = graph_dir / "edges.jsonl"
        if nodes_path.exists():
            store.load_nodes(nodes_path)
        if edges_path.exists():
            store.load_edges(edges_path)
        return store
