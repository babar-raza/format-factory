"""Tests for R1275: XcfDocument canvas geometry ratio properties.

Properties under test:
    short_edge — min of width and height
    edge_ratio — long_edge / short_edge (1.0 if short_edge is 0)
    is_narrow  — edge_ratio > 3.0

spec_fact_ref: FACT-XCF-001
"""

import types
import pytest
from xcf.models import XcfDocument


def _make_doc(width: int, height: int, layers: int = 1) -> XcfDocument:
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        num_layers=layers,
        version="2.10",
        image_type=0,
        layer_names=[f"Layer {i}" for i in range(layers)],
        path="test.xcf",
    )
    return XcfDocument(parsed)


# ── short_edge ────────────────────────────────────────────────────────────────

class TestShortEdge:
    def test_landscape_short_is_height(self):
        doc = _make_doc(400, 200)
        assert doc.short_edge == 200

    def test_portrait_short_is_width(self):
        doc = _make_doc(200, 400)
        assert doc.short_edge == 200

    def test_square_short_equals_long(self):
        doc = _make_doc(300, 300)
        assert doc.short_edge == 300

    def test_zero_dimensions(self):
        doc = _make_doc(0, 0)
        assert doc.short_edge == 0

    def test_one_zero_dimension(self):
        doc = _make_doc(0, 500)
        assert doc.short_edge == 0


# ── edge_ratio ────────────────────────────────────────────────────────────────

class TestEdgeRatio:
    def test_square_ratio_one(self):
        doc = _make_doc(100, 100)
        assert doc.edge_ratio == pytest.approx(1.0)

    def test_landscape_ratio(self):
        doc = _make_doc(300, 100)
        assert doc.edge_ratio == pytest.approx(3.0)

    def test_portrait_ratio(self):
        doc = _make_doc(100, 400)
        assert doc.edge_ratio == pytest.approx(4.0)

    def test_zero_short_edge_returns_one(self):
        doc = _make_doc(0, 0)
        assert doc.edge_ratio == pytest.approx(1.0)

    def test_two_to_one(self):
        doc = _make_doc(200, 100)
        assert doc.edge_ratio == pytest.approx(2.0)


# ── is_narrow ─────────────────────────────────────────────────────────────────

class TestIsNarrow:
    def test_ratio_gt_3_is_narrow(self):
        doc = _make_doc(400, 100)
        assert doc.is_narrow is True

    def test_ratio_exactly_3_not_narrow(self):
        doc = _make_doc(300, 100)
        assert doc.is_narrow is False

    def test_square_not_narrow(self):
        doc = _make_doc(100, 100)
        assert doc.is_narrow is False

    def test_very_narrow_portrait(self):
        doc = _make_doc(10, 1000)
        assert doc.is_narrow is True

    def test_ratio_2_not_narrow(self):
        doc = _make_doc(200, 100)
        assert doc.is_narrow is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_narrow_implies_ratio_gt_3(self):
        doc = _make_doc(500, 100)
        assert doc.is_narrow is True
        assert doc.edge_ratio > 3.0

    def test_long_short_edge_bounds(self):
        doc = _make_doc(400, 100)
        assert doc.short_edge <= doc.long_edge

    def test_edge_ratio_consistent_with_long_short(self):
        doc = _make_doc(400, 200)
        assert doc.edge_ratio == pytest.approx(doc.long_edge / doc.short_edge)
