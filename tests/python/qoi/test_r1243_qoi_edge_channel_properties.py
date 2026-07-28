"""Tests for R1243: QoiDocument edge length and channel classification properties.

Properties under test:
    long_edge  — max(width, height)
    short_edge — min(width, height)
    is_rgba    — channels == 4

spec_fact_ref: SAL-QOI-00001
"""

import types
import pytest
from qoi.models import QoiDocument


def _make_doc(width: int, height: int, channels: int = 3, colorspace: int = 0) -> QoiDocument:
    """Build a QoiDocument stub with given dimensions and channels."""
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        channels=channels,
        colorspace=colorspace,
        pixels=[],
        path="test.qoi",
    )
    return QoiDocument(parsed)


# ── long_edge ─────────────────────────────────────────────────────────────────

class TestLongEdge:
    def test_landscape_long_edge_is_width(self):
        doc = _make_doc(1920, 1080)
        assert doc.long_edge == 1920

    def test_portrait_long_edge_is_height(self):
        doc = _make_doc(1080, 1920)
        assert doc.long_edge == 1920

    def test_square_long_edge_equals_width(self):
        doc = _make_doc(512, 512)
        assert doc.long_edge == 512

    def test_zero_dimensions_long_edge(self):
        doc = _make_doc(0, 0)
        assert doc.long_edge == 0

    def test_wide_image_long_edge(self):
        doc = _make_doc(4096, 256)
        assert doc.long_edge == 4096

    def test_tall_image_long_edge(self):
        doc = _make_doc(100, 2000)
        assert doc.long_edge == 2000


# ── short_edge ────────────────────────────────────────────────────────────────

class TestShortEdge:
    def test_landscape_short_edge_is_height(self):
        doc = _make_doc(1920, 1080)
        assert doc.short_edge == 1080

    def test_portrait_short_edge_is_width(self):
        doc = _make_doc(1080, 1920)
        assert doc.short_edge == 1080

    def test_square_short_edge_equals_width(self):
        doc = _make_doc(512, 512)
        assert doc.short_edge == 512

    def test_zero_dimensions_short_edge(self):
        doc = _make_doc(0, 0)
        assert doc.short_edge == 0

    def test_wide_image_short_edge(self):
        doc = _make_doc(4096, 256)
        assert doc.short_edge == 256

    def test_tall_image_short_edge(self):
        doc = _make_doc(100, 2000)
        assert doc.short_edge == 100


# ── is_rgba ───────────────────────────────────────────────────────────────────

class TestIsRgba:
    def test_4_channels_is_rgba(self):
        doc = _make_doc(100, 100, channels=4)
        assert doc.is_rgba is True

    def test_3_channels_not_rgba(self):
        doc = _make_doc(100, 100, channels=3)
        assert doc.is_rgba is False

    def test_rgba_inverse_of_rgb(self):
        doc_rgb = _make_doc(100, 100, channels=3)
        doc_rgba = _make_doc(100, 100, channels=4)
        assert doc_rgb.is_rgb is True
        assert doc_rgb.is_rgba is False
        assert doc_rgba.is_rgb is False
        assert doc_rgba.is_rgba is True

    def test_rgba_consistent_with_has_alpha(self):
        doc = _make_doc(100, 100, channels=4)
        assert doc.is_rgba is True
        assert doc.has_alpha is True

    def test_rgb_no_alpha(self):
        doc = _make_doc(100, 100, channels=3)
        assert doc.is_rgba is False
        assert doc.has_alpha is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_long_gte_short(self):
        doc = _make_doc(800, 600)
        assert doc.long_edge >= doc.short_edge

    def test_square_long_equals_short(self):
        doc = _make_doc(256, 256)
        assert doc.long_edge == doc.short_edge

    def test_rgba_with_landscape(self):
        doc = _make_doc(1920, 1080, channels=4)
        assert doc.is_rgba is True
        assert doc.is_landscape is True
        assert doc.long_edge == 1920
        assert doc.short_edge == 1080

    def test_rgb_with_portrait(self):
        doc = _make_doc(1080, 1920, channels=3)
        assert doc.is_rgb is True
        assert doc.is_rgba is False
        assert doc.is_portrait is True
        assert doc.long_edge == 1920
        assert doc.short_edge == 1080
