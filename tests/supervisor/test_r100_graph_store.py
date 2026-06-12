"""
Tests for GraphStore: load/save JSONL, add nodes/edges, queries, graph hash determinism.
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001
"""
import tempfile
from pathlib import Path


# Import path setup
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.requirements_authority.models import GraphNode, GraphEdge
from tools.requirements_authority.graph_store import GraphStore


def _make_req_node(node_id="req:test:1", status="accepted") -> GraphNode:
    return GraphNode(
        node_id=node_id, node_type="ProductRequirement",
        label="Test requirement", status=status,
        metadata={"product_id": "test", "format_id": "test"},
        created_at="2026-06-01T00:00:00Z",
    )


def _make_claim_node(node_id="claim:test:1", status="candidate") -> GraphNode:
    return GraphNode(
        node_id=node_id, node_type="CapabilityClaim",
        label="Test claim", status=status,
        metadata={"product_id": "test", "operation": "export"},
        created_at="2026-06-01T00:00:00Z",
    )


def _make_edge(src, tgt, edge_type="derives_from") -> GraphEdge:
    return GraphEdge(
        edge_id=f"e:{src}:{edge_type}:{tgt}",
        edge_type=edge_type,
        source_node_id=src,
        target_node_id=tgt,
        metadata={},
    )


class TestGraphStoreAddAndQuery:
    def test_add_node(self):
        store = GraphStore()
        node = _make_req_node()
        store.add_node(node)
        assert store.get_node("req:test:1") is node

    def test_add_edge_dedup(self):
        store = GraphStore()
        store.add_node(_make_req_node())
        store.add_node(_make_claim_node())
        e = _make_edge("claim:test:1", "req:test:1")
        store.add_edge(e)
        store.add_edge(e)  # duplicate
        assert len(store.edges) == 1

    def test_get_outgoing(self):
        store = GraphStore()
        store.add_node(_make_req_node())
        store.add_node(_make_claim_node())
        e = _make_edge("claim:test:1", "req:test:1")
        store.add_edge(e)
        outgoing = store.get_outgoing("claim:test:1")
        assert len(outgoing) == 1
        assert outgoing[0].edge_type == "derives_from"

    def test_get_incoming(self):
        store = GraphStore()
        store.add_node(_make_req_node())
        store.add_node(_make_claim_node())
        e = _make_edge("claim:test:1", "req:test:1")
        store.add_edge(e)
        incoming = store.get_incoming("req:test:1")
        assert len(incoming) == 1

    def test_get_targets(self):
        store = GraphStore()
        store.add_node(_make_req_node())
        store.add_node(_make_claim_node())
        e = _make_edge("claim:test:1", "req:test:1", "derives_from")
        store.add_edge(e)
        targets = store.get_targets("claim:test:1", "derives_from")
        assert len(targets) == 1
        assert targets[0].node_id == "req:test:1"

    def test_nodes_by_type(self):
        store = GraphStore()
        store.add_node(_make_req_node("req:1"))
        store.add_node(_make_req_node("req:2"))
        store.add_node(_make_claim_node("claim:1"))
        reqs = store.nodes_by_type("ProductRequirement")
        assert len(reqs) == 2

    def test_get_node_missing(self):
        store = GraphStore()
        assert store.get_node("nonexistent") is None


class TestGraphStoreIO:
    def test_save_and_load_nodes(self):
        store = GraphStore()
        store.add_node(_make_req_node("req:a"))
        store.add_node(_make_claim_node("claim:a"))
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "nodes.jsonl"
            store.save_nodes(p)
            store2 = GraphStore()
            store2.load_nodes(p)
            assert "req:a" in store2.nodes
            assert "claim:a" in store2.nodes

    def test_save_and_load_edges(self):
        store = GraphStore()
        store.add_node(_make_req_node())
        store.add_node(_make_claim_node())
        e = _make_edge("claim:test:1", "req:test:1")
        store.add_edge(e)
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "edges.jsonl"
            store.save_edges(p)
            store2 = GraphStore()
            store2.load_edges(p)
            assert len(store2.edges) == 1
            assert store2.edges[0].edge_type == "derives_from"

    def test_load_from_dir(self):
        store = GraphStore()
        store.add_node(_make_req_node("req:dir:1"))
        store.add_node(_make_claim_node("claim:dir:1"))
        e = _make_edge("claim:dir:1", "req:dir:1")
        store.add_edge(e)
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            store.save_nodes(d / "nodes.jsonl")
            store.save_edges(d / "edges.jsonl")
            loaded = GraphStore.load_from_dir(d)
            assert "req:dir:1" in loaded.nodes
            assert len(loaded.edges) == 1


class TestGraphHashDeterminism:
    def test_same_inputs_same_hash(self):
        def build_store():
            s = GraphStore()
            s.add_node(_make_req_node("req:h:1"))
            s.add_node(_make_claim_node("claim:h:1"))
            s.add_edge(_make_edge("claim:h:1", "req:h:1"))
            return s

        hashes = [build_store().compute_graph_hash() for _ in range(3)]
        assert len(set(hashes)) == 1, f"Hash not deterministic: {hashes}"

    def test_different_nodes_different_hash(self):
        s1 = GraphStore()
        s1.add_node(_make_req_node("req:a"))
        s2 = GraphStore()
        s2.add_node(_make_req_node("req:b"))
        assert s1.compute_graph_hash() != s2.compute_graph_hash()

    def test_empty_store_hash(self):
        store = GraphStore()
        h = store.compute_graph_hash()
        assert len(h) == 64  # SHA-256 hex
