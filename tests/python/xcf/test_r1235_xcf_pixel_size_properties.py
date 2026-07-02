"""Tests for R1235: XcfDocument pixel count and image size classification properties.

Properties under test:
    pixel_count    — width * height
    megapixels     — pixel_count / 1_000_000
    is_large_image — pixel_count > 4_000_000

spec_fact_ref: FACT-XCF-001
"""

import types
import pytest
from xcf.models import XcfDocument


def _make_doc(width: int, height: int, layer_count: int = 1) -> XcfDocument:
    """Build an XcfDocument stub with given canvas dimensions."""
    parsed = types.SimpleNamespace(
        width=width,
        height=height,
        num_layers=layer_count,
        version="xcf v011",
        image_type=0,
        layer_names=[f"Layer {i}" for i in range(layer_count)],
        path="test.xcf",
    )
    return XcfDocument(parsed)


# ── pixel_count ───────────────────────────────────────────────────────────────

class TestPixelCount:
    def test_typical_image_pixel_count(self):
        doc = _make_doc(1920, 1080)
        assert doc.pixel_count == 1920 * 1080

    def test_square_image_pixel_count(self):
        doc = _make_doc(100, 100)
        assert doc.pixel_count == 10000

    def test_zero_width_pixel_count(self):
        doc = _make_doc(0, 1000)
        assert doc.pixel_count == 0

    def test_zero_height_pixel_count(self):
        doc = _make_doc(1000, 0)
        assert doc.pixel_count == 0

    def test_both_zero_pixel_count(self):
        doc = _make_doc(0, 0)
        assert doc.pixel_count == 0

    def test_single_pixel_image(self):
        doc = _make_doc(1, 1)
        assert doc.pixel_count == 1

    def test_4mp_boundary_pixel_count(self):
        doc = _make_doc(2000, 2000)
        assert doc.pixel_count == 4_000_000


# ── megapixels ────────────────────────────────────────────────────────────────

class TestMegapixels:
    def test_zero_image_megapixels(self):
        doc = _make_doc(0, 0)
        assert doc.megapixels == 0.0

    def test_1mp_image(self):
        doc = _make_doc(1000, 1000)
        assert doc.megapixels == pytest.approx(1.0)

    def test_4mp_image(self):
        doc = _make_doc(2000, 2000)
        assert doc.megapixels == pytest.approx(4.0)

    def test_full_hd_megapixels(self):
        doc = _make_doc(1920, 1080)
        assert doc.megapixels == pytest.approx(1920 * 1080 / 1_000_000)

    def test_large_image_megapixels(self):
        doc = _make_doc(4000, 3000)
        assert doc.megapixels == pytest.approx(12.0)


# ── is_large_image ────────────────────────────────────────────────────────────

class TestIsLargeImage:
    def test_over_4mp_is_large(self):
        doc = _make_doc(2001, 2000)  # 4_002_000 pixels
        assert doc.is_large_image is True

    def test_exactly_4mp_not_large(self):
        doc = _make_doc(2000, 2000)  # exactly 4_000_000 — not > 4_000_000
        assert doc.is_large_image is False

    def test_below_4mp_not_large(self):
        doc = _make_doc(1920, 1080)  # 2_073_600 pixels
        assert doc.is_large_image is False

    def test_zero_pixels_not_large(self):
        doc = _make_doc(0, 0)
        assert doc.is_large_image is False

    def test_single_pixel_not_large(self):
        doc = _make_doc(1, 1)
        assert doc.is_large_image is False

    def test_12mp_is_large(self):
        doc = _make_doc(4000, 3000)
        assert doc.is_large_image is True

    def test_boundary_one_over_4mp(self):
        doc = _make_doc(2000, 2001)  # 4_002_000 > 4_000_000
        assert doc.is_large_image is True


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_megapixels_consistent_with_pixel_count(self):
        doc = _make_doc(3000, 2000)
        assert doc.megapixels == pytest.approx(doc.pixel_count / 1_000_000)

    def test_large_image_has_high_pixel_count(self):
        doc = _make_doc(3000, 2000)
        assert doc.is_large_image is True
        assert doc.pixel_count > 4_000_000

    def test_small_image_not_large(self):
        doc = _make_doc(100, 100)
        assert doc.is_large_image is False
        assert doc.pixel_count == 10000

    def test_4mp_boundary_all_consistent(self):
        doc = _make_doc(2000, 2000)
        assert doc.pixel_count == 4_000_000
        assert doc.megapixels == pytest.approx(4.0)
        assert doc.is_large_image is False
