"""Tests for mtlx_graph.py — graph connection resolution.

Before this fix, nodename/interfacename attribute values were inert flat
strings: a caller had no way to actually traverse from a node's input to
the upstream node object it names. These tests prove resolve_connections
and get_connected_node turn those references into real structure.

Spec reference: FACT-MTLX-102.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from mtlx.exceptions import MtlxConnectionError
from mtlx.mtlx_codec import load_mtlx
from mtlx.mtlx_graph import get_connected_node, resolve_connections

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx"
VALID_DIR = SAMPLES / "valid"

_A_CONNECTS_TO_B = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph1">'
    b'<node name="B" type="float"><input name="seed" type="float" value="0.5"/></node>'
    b'<node name="A" type="color3"><input name="in1" type="float" nodename="B"/></node>'
    b'<output name="out" type="color3" nodename="A"/>'
    b"</nodegraph></materialx>"
)

_A_UNCONNECTED_INPUT = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph1">'
    b'<node name="A" type="color3"><input name="in1" type="float" value="1.0"/></node>'
    b"</nodegraph></materialx>"
)

_A_DANGLING_REFERENCE = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph1">'
    b'<node name="A" type="color3"><input name="in1" type="float" nodename="ghost"/></node>'
    b"</nodegraph></materialx>"
)

_INTERFACENAME_DOC = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph1">'
    b'<node name="paramA" type="float"/>'
    b'<node name="A" type="color3"><input name="in1" type="float" interfacename="paramA"/></node>'
    b"</nodegraph></materialx>"
)


def _node_graph(source: bytes) -> dict:
    model = load_mtlx(source)
    return model["node_graphs"][0]


class TestGetConnectedNode:
    def test_returns_actual_upstream_node_object(self):
        ng = _node_graph(_A_CONNECTS_TO_B)
        upstream = get_connected_node(ng, "A", "in1")
        assert upstream is not None
        assert isinstance(upstream, dict)
        assert upstream["name"] == "B"
        assert not isinstance(upstream, str)  # explicitly not the bare string reference

    def test_upstream_node_has_its_own_structure(self):
        ng = _node_graph(_A_CONNECTS_TO_B)
        upstream = get_connected_node(ng, "A", "in1")
        assert upstream["inputs"][0]["name"] == "seed"
        assert upstream["inputs"][0]["value"] == "0.5"

    def test_unconnected_input_returns_none(self):
        ng = _node_graph(_A_UNCONNECTED_INPUT)
        assert get_connected_node(ng, "A", "in1") is None

    def test_unknown_node_name_raises(self):
        ng = _node_graph(_A_CONNECTS_TO_B)
        with pytest.raises(MtlxConnectionError, match="No node named"):
            get_connected_node(ng, "does_not_exist", "in1")

    def test_unknown_input_name_raises(self):
        ng = _node_graph(_A_CONNECTS_TO_B)
        with pytest.raises(MtlxConnectionError, match="no input named"):
            get_connected_node(ng, "A", "does_not_exist")

    def test_dangling_nodename_reference_raises(self):
        """A reference to a name absent from the graph must be a deliberate,
        clearly-classified error -- not a silent None and not a crash."""
        ng = _node_graph(_A_DANGLING_REFERENCE)
        with pytest.raises(MtlxConnectionError, match="unknown upstream node"):
            get_connected_node(ng, "A", "in1")

    def test_interfacename_reference_also_resolves(self):
        ng = _node_graph(_INTERFACENAME_DOC)
        upstream = get_connected_node(ng, "A", "in1")
        assert upstream is not None
        assert upstream["name"] == "paramA"

    def test_real_sample_connection_resolves(self):
        """node-graph.mtlx: color_mix's 'mix' input connects via nodename to 'noise'."""
        ng = _node_graph((VALID_DIR / "node-graph.mtlx").read_bytes())
        upstream = get_connected_node(ng, "color_mix", "mix")
        assert upstream is not None
        assert upstream["name"] == "noise"


class TestResolveConnections:
    def test_returns_index_of_all_nodes(self):
        ng = _node_graph(_A_CONNECTS_TO_B)
        resolved = resolve_connections(ng)
        assert set(resolved.keys()) == {"A", "B"}

    def test_resolved_input_points_to_actual_node(self):
        ng = _node_graph(_A_CONNECTS_TO_B)
        resolved = resolve_connections(ng)
        a_inputs = resolved["A"]["resolved_inputs"]
        assert len(a_inputs) == 1
        assert a_inputs[0]["input_name"] == "in1"
        assert a_inputs[0]["upstream_name"] == "B"
        assert a_inputs[0]["upstream_node"]["name"] == "B"

    def test_node_with_no_connections_has_empty_resolved_inputs(self):
        ng = _node_graph(_A_CONNECTS_TO_B)
        resolved = resolve_connections(ng)
        assert resolved["B"]["resolved_inputs"] == []

    def test_dangling_reference_does_not_raise_reports_none(self):
        """Bulk resolution is inspection-oriented: it surfaces a dangling
        reference as upstream_node=None rather than raising, unlike the
        single-lookup get_connected_node."""
        ng = _node_graph(_A_DANGLING_REFERENCE)
        resolved = resolve_connections(ng)
        entry = resolved["A"]["resolved_inputs"][0]
        assert entry["upstream_name"] == "ghost"
        assert entry["upstream_node"] is None

    def test_empty_node_graph_returns_empty_index(self):
        ng = {"name": "empty", "nodes": [], "outputs": []}
        assert resolve_connections(ng) == {}
