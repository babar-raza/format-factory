"""Tests for R1263: QoiDocument canvas geometry and density properties.

Properties under test:
    edge_ratio            — long_edge / short_edge (1.0 if short_edge is 0)
    is_narrow             — edge_ratio > 3.0
    bytes_per_pixel_estimate — channels (RGB=3, RGBA=4)

spec_fact_ref: FACT-QOI-001
"""

import types
import pytest
from qoi.models import QoiDocument


def _make_doc(width: int, height: int, channels: int = 3, colorspace: int = 0) -> QoiDocument:
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        channels=channels,
        colorspace=colorspace,
        pixel_count=width * height,
        has_alpha=channels == 4,
        path="test.qoi",
    )
    return QoiDocument(parsed)


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


# ── bytes_per_pixel_estimate ──────────────────────────────────────────────────

class TestBytesPerPixelEstimate:
    def test_rgb_is_3(self):
        doc = _make_doc(100, 100, channels=3)
        assert doc.bytes_per_pixel_estimate == 3

    def test_rgba_is_4(self):
        doc = _make_doc(100, 100, channels=4)
        assert doc.bytes_per_pixel_estimate == 4

    def test_consistent_with_channels(self):
        doc = _make_doc(100, 100, channels=3)
        assert doc.bytes_per_pixel_estimate == doc.channels


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_narrow_implies_ratio_gt_3(self):
        doc = _make_doc(500, 100)
        assert doc.is_narrow is True
        assert doc.edge_ratio > 3.0

    def test_rgba_bpp_4_channels_4(self):
        doc = _make_doc(100, 100, channels=4)
        assert doc.is_rgba is True
        assert doc.bytes_per_pixel_estimate == 4

    def test_rgb_not_rgba_bpp_3(self):
        doc = _make_doc(100, 100, channels=3)
        assert doc.is_rgba is False
        assert doc.bytes_per_pixel_estimate == 3
