"""Tests for mtlx_analytics.py — node type histogram, shader connection count,
node graph size map.

Spec references: FACT-MTLX-002 (node graphs), FACT-MTLX-003 (materials),
FACT-MTLX-103 (node category vs. data-type histogram grouping).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from mtlx.mtlx_analytics import (
    mtlx_materials_with_shader_count,
    mtlx_node_graph_size,
    mtlx_node_type_histogram,
)
from mtlx.exceptions import MtlxParseError

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "mtlx"
VALID_DIR = SAMPLES / "valid"
INVALID_DIR = SAMPLES / "invalid"

# Synthetic sources exercise node-graph/material shapes that the checked-in
# sample corpus does not cover (e.g. connected shader inputs, top-level
# nodes) without inventing new sample files, per taskcard instructions.
_ONE_NODEGRAPH = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph_a">'
    b'<node name="n1" type="float" node="fractal3d"/>'
    b'<node name="n2" type="color3" node="mix"/>'
    b'<output name="out" type="color3" nodename="n2"/>'
    b"</nodegraph></materialx>"
)

_TWO_NODEGRAPHS = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph_a"><node name="n1" type="float"/></nodegraph>'
    b'<nodegraph name="graph_b">'
    b'<node name="n2" type="float"/><node name="n3" type="color3"/>'
    b"</nodegraph></materialx>"
)

_CONNECTED_MATERIAL = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<surfacematerial name="connected_mat">'
    b'<input name="surfaceshader" type="surfaceshader" nodename="shader1"/>'
    b"</surfacematerial></materialx>"
)

_UNCONNECTED_MATERIAL = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<surfacematerial name="stub_mat">'
    b'<input name="surfaceshader" type="surfaceshader" value=""/>'
    b"</surfacematerial></materialx>"
)

_MIXED_MATERIALS = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<surfacematerial name="connected_1">'
    b'<input name="surfaceshader" type="surfaceshader" nodename="shaderA"/>'
    b"</surfacematerial>"
    b'<surfacematerial name="connected_2">'
    b'<input name="surfaceshader" type="surfaceshader" nodename="shaderB"/>'
    b"</surfacematerial>"
    b'<surfacematerial name="unconnected">'
    b'<input name="surfaceshader" type="surfaceshader" value=""/>'
    b"</surfacematerial></materialx>"
)

_TOP_LEVEL_NODE = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<standard_surface name="ss1" type="surfaceshader"/>'
    b"</materialx>"
)

# FACT-MTLX-103: two nodes of the *same* category (image) but *different*
# data types (color3 vs float) -- must be merged under the category, proving
# the histogram groups by category rather than data type.
_SAME_CATEGORY_DIFFERENT_DATA_TYPE = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph_cat">'
    b'<node name="tex1" type="color3" node="image"/>'
    b'<node name="tex2" type="float" node="image"/>'
    b'<node name="m1" type="color3" node="mix"/>'
    b"</nodegraph></materialx>"
)

# FACT-MTLX-103: two nodes that *share* a data type (color3) but differ in
# category (image vs mix) -- must NOT be merged, proving data type alone
# cannot stand in for category.
_SAME_DATA_TYPE_DIFFERENT_CATEGORY = (
    b'<?xml version="1.0"?><materialx version="1.39">'
    b'<nodegraph name="graph_dt">'
    b'<node name="tex1" type="color3" node="image"/>'
    b'<node name="m1" type="color3" node="mix"/>'
    b"</nodegraph></materialx>"
)


class TestNodeTypeHistogram:
    def test_returns_dict(self):
        result = mtlx_node_type_histogram(VALID_DIR / "node-graph.mtlx")
        assert isinstance(result, dict)

    def test_counts_by_node_category_not_data_type(self):
        # FACT-MTLX-103 regression guard: _ONE_NODEGRAPH's nodes carry both a
        # data-type attribute (type="float"/"color3") and a category
        # attribute (node="fractal3d"/"mix"). The histogram must group by
        # category -- the previous (buggy) behavior grouped by data type and
        # produced {"float": 1, "color3": 1} instead.
        result = mtlx_node_type_histogram(_ONE_NODEGRAPH)
        assert result == {"fractal3d": 1, "mix": 1}

    def test_same_category_different_data_type_merged(self):
        result = mtlx_node_type_histogram(_SAME_CATEGORY_DIFFERENT_DATA_TYPE)
        assert result == {"image": 2, "mix": 1}

    def test_same_data_type_different_category_not_merged(self):
        result = mtlx_node_type_histogram(_SAME_DATA_TYPE_DIFFERENT_CATEGORY)
        assert result == {"image": 1, "mix": 1}
        assert "color3" not in result

    def test_counts_across_multiple_node_graphs(self):
        result = mtlx_node_type_histogram(_TWO_NODEGRAPHS)
        assert result == {"float": 2, "color3": 1}

    def test_accepts_bytes_source(self):
        result = mtlx_node_type_histogram(_ONE_NODEGRAPH)
        assert sum(result.values()) == 2

    def test_accepts_path_source(self):
        result = mtlx_node_type_histogram(VALID_DIR / "node-graph.mtlx")
        assert sum(result.values()) >= 1

    def test_accepts_string_path_source(self):
        result = mtlx_node_type_histogram(str(VALID_DIR / "node-graph.mtlx"))
        assert sum(result.values()) >= 1

    def test_counts_top_level_nodes(self):
        # Top-level (outside any nodegraph) nodes carry only a 'type' field
        # equal to the XML tag's local name -- the codec does not capture a
        # separate node_type attribute for them, unlike nodegraph children.
        result = mtlx_node_type_histogram(_TOP_LEVEL_NODE)
        assert result.get("standard_surface") == 1

    def test_zero_node_graphs_returns_empty_dict(self):
        result = mtlx_node_type_histogram(VALID_DIR / "simple-material.mtlx")
        assert result == {}

    def test_materials_do_not_pollute_histogram(self):
        result = mtlx_node_type_histogram(VALID_DIR / "multi-material.mtlx")
        assert "surfacematerial" not in result

    def test_raises_on_invalid_source(self):
        with pytest.raises(MtlxParseError):
            mtlx_node_type_histogram(INVALID_DIR / "wrong-root.mtlx")


class TestMaterialsWithShaderCount:
    def test_returns_int(self):
        result = mtlx_materials_with_shader_count(VALID_DIR / "simple-material.mtlx")
        assert isinstance(result, int)

    def test_connected_material_counted(self):
        assert mtlx_materials_with_shader_count(_CONNECTED_MATERIAL) == 1

    def test_unconnected_stub_input_not_counted(self):
        assert mtlx_materials_with_shader_count(_UNCONNECTED_MATERIAL) == 0

    def test_mixed_materials_counts_only_connected(self):
        assert mtlx_materials_with_shader_count(_MIXED_MATERIALS) == 2

    def test_zero_materials_returns_zero(self):
        assert mtlx_materials_with_shader_count(VALID_DIR / "node-graph.mtlx") == 0

    def test_sample_materials_have_no_nodename_stub(self):
        # The checked-in sample corpus declares surfaceshader inputs without
        # a nodename connection (value="" placeholders) -- confirms the
        # "declared but not connected" branch against real fixtures.
        assert mtlx_materials_with_shader_count(VALID_DIR / "multi-material.mtlx") == 0

    def test_accepts_bytes_source(self):
        assert mtlx_materials_with_shader_count(_CONNECTED_MATERIAL) >= 0

    def test_accepts_path_source(self):
        result = mtlx_materials_with_shader_count(VALID_DIR / "simple-material.mtlx")
        assert result == 0

    def test_raises_on_invalid_source(self):
        with pytest.raises(MtlxParseError):
            mtlx_materials_with_shader_count(INVALID_DIR / "wrong-root.mtlx")

    def test_raises_on_bad_xml(self):
        with pytest.raises(MtlxParseError):
            mtlx_materials_with_shader_count(b"<not>closed")


class TestNodeGraphSize:
    def test_returns_dict(self):
        result = mtlx_node_graph_size(VALID_DIR / "node-graph.mtlx")
        assert isinstance(result, dict)

    def test_single_node_graph_size(self):
        result = mtlx_node_graph_size(_ONE_NODEGRAPH)
        assert result == {"graph_a": 2}

    def test_multiple_node_graphs_sizes(self):
        result = mtlx_node_graph_size(_TWO_NODEGRAPHS)
        assert result == {"graph_a": 1, "graph_b": 2}

    def test_zero_node_graphs_returns_empty_dict(self):
        result = mtlx_node_graph_size(VALID_DIR / "simple-material.mtlx")
        assert result == {}

    def test_sample_node_graph_size_matches_load(self):
        from mtlx.mtlx_codec import load_mtlx

        model = load_mtlx(VALID_DIR / "node-graph.mtlx")
        result = mtlx_node_graph_size(VALID_DIR / "node-graph.mtlx")
        expected_name = model["node_graphs"][0]["name"]
        assert result[expected_name] == len(model["node_graphs"][0]["nodes"])

    def test_accepts_bytes_source(self):
        result = mtlx_node_graph_size(_ONE_NODEGRAPH)
        assert "graph_a" in result

    def test_accepts_string_path_source(self):
        result = mtlx_node_graph_size(str(VALID_DIR / "node-graph.mtlx"))
        assert isinstance(result, dict)

    def test_raises_on_invalid_source(self):
        with pytest.raises(MtlxParseError):
            mtlx_node_graph_size(INVALID_DIR / "wrong-root.mtlx")


class TestAnalyticsEdgeCases:
    """L3 edge-case coverage for malformed/boundary inputs across all three functions."""

    def test_histogram_nonexistent_file_raises(self):
        with pytest.raises(MtlxParseError):
            mtlx_node_type_histogram("/nonexistent/path.mtlx")

    def test_shader_count_nonexistent_file_raises(self):
        with pytest.raises(MtlxParseError):
            mtlx_materials_with_shader_count("/nonexistent/path.mtlx")

    def test_node_graph_size_nonexistent_file_raises(self):
        with pytest.raises(MtlxParseError):
            mtlx_node_graph_size("/nonexistent/path.mtlx")

    def test_histogram_empty_bytes_raises(self):
        with pytest.raises(MtlxParseError):
            mtlx_node_type_histogram(b"")

    def test_shader_count_empty_bytes_raises(self):
        with pytest.raises(MtlxParseError):
            mtlx_materials_with_shader_count(b"")

    def test_node_graph_with_only_output_no_nodes(self):
        xml = (
            b'<?xml version="1.0"?><materialx version="1.39">'
            b'<nodegraph name="empty_graph">'
            b'<output name="out" type="color3" nodename="missing"/>'
            b"</nodegraph></materialx>"
        )
        assert mtlx_node_graph_size(xml) == {"empty_graph": 0}
        assert mtlx_node_type_histogram(xml) == {}

    def test_histogram_and_node_graph_size_agree_on_totals(self):
        """Cross-check: sum of the size map equals sum of the histogram
        counts when every node lives inside a node graph (no top-level nodes)."""
        histogram = mtlx_node_type_histogram(_TWO_NODEGRAPHS)
        sizes = mtlx_node_graph_size(_TWO_NODEGRAPHS)
        assert sum(histogram.values()) == sum(sizes.values())
