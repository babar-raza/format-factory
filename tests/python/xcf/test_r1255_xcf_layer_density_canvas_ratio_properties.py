"""Tests for R1255: XcfDocument layer density and canvas ratio properties.

Properties under test:
    layers_per_megapixel — layer_count / megapixels (0.0 if pixel_count == 0)
    is_grayscale_type    — image_type == 1
    long_edge            — max(width, height)

spec_fact_ref: SAL-XCF-00001
"""

import types
import pytest
from xcf.models import XcfDocument


def _make_doc(width: int, height: int, layer_count: int = 1,
              image_type: int = 0, version: str = "2.10") -> XcfDocument:
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        num_layers=layer_count,
        version=version,
        image_type=image_type,
        layer_names=[f"Layer {i}" for i in range(layer_count)],
        path="test.xcf",
    )
    return XcfDocument(parsed)


# ── layers_per_megapixel ──────────────────────────────────────────────────────

class TestLayersPerMegapixel:
    def test_zero_pixels_returns_zero(self):
        doc = _make_doc(0, 0)
        assert doc.layers_per_megapixel == pytest.approx(0.0)

    def test_one_layer_one_megapixel(self):
        doc = _make_doc(1000, 1000, layer_count=1)
        assert doc.layers_per_megapixel == pytest.approx(1.0)

    def test_ten_layers_one_megapixel(self):
        doc = _make_doc(1000, 1000, layer_count=10)
        assert doc.layers_per_megapixel == pytest.approx(10.0)

    def test_multilayer_large_canvas(self):
        doc = _make_doc(2000, 1000, layer_count=4)
        # pixel_count = 2_000_000, megapixels = 2.0, layers_per_mp = 2.0
        assert doc.layers_per_megapixel == pytest.approx(2.0)

    def test_single_pixel_canvas(self):
        doc = _make_doc(1, 1, layer_count=1)
        assert doc.layers_per_megapixel == pytest.approx(1.0 / (1 / 1_000_000))


# ── is_grayscale_type ─────────────────────────────────────────────────────────

class TestIsGrayscaleType:
    def test_image_type_1_is_grayscale(self):
        doc = _make_doc(100, 100, image_type=1)
        assert doc.is_grayscale_type is True

    def test_rgb_not_grayscale(self):
        doc = _make_doc(100, 100, image_type=0)
        assert doc.is_grayscale_type is False

    def test_indexed_not_grayscale(self):
        doc = _make_doc(100, 100, image_type=2)
        assert doc.is_grayscale_type is False

    def test_grayscale_is_not_rgb(self):
        doc = _make_doc(100, 100, image_type=1)
        assert doc.is_grayscale_type is True
        assert doc.is_rgb_type is False


# ── long_edge ─────────────────────────────────────────────────────────────────

class TestLongEdge:
    def test_landscape_long_edge_is_width(self):
        doc = _make_doc(1920, 1080)
        assert doc.long_edge == 1920

    def test_portrait_long_edge_is_height(self):
        doc = _make_doc(1080, 1920)
        assert doc.long_edge == 1920

    def test_square_long_edge_equals_either(self):
        doc = _make_doc(500, 500)
        assert doc.long_edge == 500

    def test_small_canvas(self):
        doc = _make_doc(10, 20)
        assert doc.long_edge == 20

    def test_one_pixel_wide(self):
        doc = _make_doc(1, 100)
        assert doc.long_edge == 100


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_long_edge_ge_short_edges(self):
        doc = _make_doc(640, 480)
        assert doc.long_edge >= doc.width
        assert doc.long_edge >= doc.height

    def test_grayscale_not_rgb(self):
        doc = _make_doc(200, 200, image_type=1)
        assert doc.is_grayscale_type is True
        assert doc.is_rgb_type is False

    def test_layers_per_mp_proportional_to_layer_count(self):
        d1 = _make_doc(1000, 1000, layer_count=2)
        d2 = _make_doc(1000, 1000, layer_count=4)
        assert d2.layers_per_megapixel == pytest.approx(2 * d1.layers_per_megapixel)
