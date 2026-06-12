"""
tests/python/xcf/test_r202_xcf_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT13-001
TASK-001 (part A): XCF advanced operations.

Covers: parse_xcf, parse_xcf_strict, probe_xcf, get_capabilities,
xcf_layer_count, xcf_image_dimensions, xcf_version, xcf_image_type_name,
xcf_pixel_count, xcf_file_size, xcf_is_rgb, xcf_is_grayscale,
xcf_aspect_ratio, xcf_is_square, XcfImage.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import (
    parse_xcf, parse_xcf_strict, probe_xcf, get_capabilities,
    xcf_layer_count, xcf_image_dimensions, xcf_version, xcf_image_type_name,
    xcf_pixel_count, xcf_file_size, xcf_is_rgb, xcf_is_grayscale,
    xcf_aspect_ratio, xcf_is_square, XcfImage,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RGB_1X1 = str(_SAMPLES / "1x1-red-rgb.xcf")
_RGBA_1X1 = str(_SAMPLES / "1x1-rgba-blue.xcf")
_GRAY_2X2 = str(_SAMPLES / "2x2-gray.xcf")


class TestXcfParseAndProbe:
    """parse_xcf, parse_xcf_strict, probe_xcf, get_capabilities."""

    def test_parse_xcf_returns_dict(self):
        result = parse_xcf(_RGB_1X1)
        assert isinstance(result, dict)

    def test_parse_xcf_ok_true(self):
        result = parse_xcf(_RGB_1X1)
        assert result.get("ok") is True

    def test_parse_xcf_has_dimensions(self):
        result = parse_xcf(_RGB_1X1)
        assert result.get("width") == 1
        assert result.get("height") == 1

    def test_parse_xcf_rgb_type(self):
        result = parse_xcf(_RGB_1X1)
        assert result.get("image_type_name") == "RGB"

    def test_parse_xcf_grayscale_type(self):
        result = parse_xcf(_GRAY_2X2)
        assert result.get("image_type_name") == "Grayscale"

    def test_parse_xcf_2x2_dimensions(self):
        result = parse_xcf(_GRAY_2X2)
        assert result.get("width") == 2
        assert result.get("height") == 2

    def test_parse_xcf_strict_returns_xcfimage(self):
        result = parse_xcf_strict(_RGB_1X1)
        assert isinstance(result, XcfImage)

    def test_parse_xcf_strict_has_width(self):
        result = parse_xcf_strict(_RGB_1X1)
        assert result.width == 1

    def test_probe_xcf_dict(self):
        result = probe_xcf(_RGB_1X1)
        assert isinstance(result, dict)

    def test_probe_xcf_valid_header(self):
        result = probe_xcf(_RGB_1X1)
        assert result.get("valid_header") is True

    def test_probe_xcf_exists(self):
        result = probe_xcf(_RGB_1X1)
        assert result.get("exists") is True

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "xcf"

    def test_get_capabilities_has_supported(self):
        caps = get_capabilities()
        assert isinstance(caps.get("supported"), list)
        assert len(caps["supported"]) > 0


class TestXcfImageInfo:
    """xcf_layer_count, xcf_image_dimensions, xcf_version, xcf_image_type_name."""

    def test_xcf_layer_count_int(self):
        count = xcf_layer_count(_RGB_1X1)
        assert isinstance(count, int)
        assert count >= 1

    def test_xcf_image_dimensions_dict(self):
        dims = xcf_image_dimensions(_RGB_1X1)
        assert isinstance(dims, dict)
        assert dims.get("width") == 1
        assert dims.get("height") == 1

    def test_xcf_image_dimensions_2x2(self):
        dims = xcf_image_dimensions(_GRAY_2X2)
        assert dims.get("width") == 2
        assert dims.get("height") == 2

    def test_xcf_version_str(self):
        ver = xcf_version(_RGB_1X1)
        assert isinstance(ver, str)
        assert len(ver) > 0

    def test_xcf_image_type_name_rgb(self):
        name = xcf_image_type_name(_RGB_1X1)
        assert name == "RGB"

    def test_xcf_image_type_name_grayscale(self):
        name = xcf_image_type_name(_GRAY_2X2)
        assert name == "Grayscale"


class TestXcfAnalytics:
    """xcf_pixel_count, xcf_file_size, xcf_is_rgb, xcf_is_grayscale, xcf_aspect_ratio, xcf_is_square."""

    def test_xcf_pixel_count_1x1(self):
        count = xcf_pixel_count(_RGB_1X1)
        assert count == 1

    def test_xcf_pixel_count_2x2(self):
        count = xcf_pixel_count(_GRAY_2X2)
        assert count == 4

    def test_xcf_file_size_positive(self):
        size = xcf_file_size(_RGB_1X1)
        assert isinstance(size, int)
        assert size > 0

    def test_xcf_is_rgb_true(self):
        assert xcf_is_rgb(_RGB_1X1) is True

    def test_xcf_is_rgb_false_for_gray(self):
        assert xcf_is_rgb(_GRAY_2X2) is False

    def test_xcf_is_grayscale_true(self):
        assert xcf_is_grayscale(_GRAY_2X2) is True

    def test_xcf_is_grayscale_false_for_rgb(self):
        assert xcf_is_grayscale(_RGB_1X1) is False

    def test_xcf_aspect_ratio_square(self):
        ratio = xcf_aspect_ratio(_RGB_1X1)
        assert isinstance(ratio, float)
        assert ratio == 1.0

    def test_xcf_is_square_true(self):
        assert xcf_is_square(_RGB_1X1) is True

    def test_xcf_is_square_2x2(self):
        assert xcf_is_square(_GRAY_2X2) is True
