"""
test_xcf_layer_count_image_dimensions.py

Sprint: FORMAT-FACTORY-GAP-DRIVEN-PRODUCT-RNEXT-001
Gap IDs: GAP-XCF-FOSS-XCF_LAYER_CO-001, GAP-XCF-FOSS-XCF_IMAGE_DI-001

Focused tests for xcf_layer_count and xcf_image_dimensions.
Closes missing_test_coverage gaps for both functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_layer_count, xcf_image_dimensions, XcfError

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfLayerCount:
    def test_rgb_image_has_layers(self):
        count = xcf_layer_count(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(count, int)
        assert count >= 1

    def test_gray_image_has_layers(self):
        count = xcf_layer_count(_SAMPLES / "2x2-gray.xcf")
        assert isinstance(count, int)
        assert count >= 1

    def test_rgba_image_has_layers(self):
        count = xcf_layer_count(_SAMPLES / "1x1-rgba-blue.xcf")
        assert isinstance(count, int)
        assert count >= 1

    def test_missing_file_raises(self):
        with pytest.raises(XcfError):
            xcf_layer_count(_SAMPLES / "nonexistent.xcf")


class TestXcfImageDimensions:
    def test_1x1_rgb_dimensions(self):
        dims = xcf_image_dimensions(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(dims, dict)
        assert dims["width"] == 1
        assert dims["height"] == 1

    def test_2x2_gray_dimensions(self):
        dims = xcf_image_dimensions(_SAMPLES / "2x2-gray.xcf")
        assert isinstance(dims, dict)
        assert dims["width"] == 2
        assert dims["height"] == 2

    def test_dimensions_keys_present(self):
        dims = xcf_image_dimensions(_SAMPLES / "1x1-rgba-blue.xcf")
        assert "width" in dims
        assert "height" in dims

    def test_missing_file_raises(self):
        with pytest.raises(XcfError):
            xcf_image_dimensions(_SAMPLES / "ghost.xcf")
