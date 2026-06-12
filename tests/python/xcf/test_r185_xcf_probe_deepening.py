"""
test_r185_xcf_probe_deepening.py — XCF probe + metadata deepening tests

Sprint: PRODUCT-DEEPENING-RNEXT185-20260612-001
Gap closure: GAP-XCF-FOSS-PROBE_XCF-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import (
    probe_xcf,
    xcf_layer_count,
    xcf_image_dimensions,
    xcf_pixel_count,
    xcf_is_rgb,
    xcf_is_grayscale,
    xcf_is_square,
    xcf_aspect_ratio,
    xcf_version,
    xcf_image_type_name,
    xcf_file_size,
    xcf_summary,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED_RGB = _SAMPLES / "1x1-red-rgb.xcf"
_BLUE_RGBA = _SAMPLES / "1x1-rgba-blue.xcf"
_GRAY_2X2 = _SAMPLES / "2x2-gray.xcf"


class TestXcfProbe:
    def test_probe_returns_dict(self):
        result = probe_xcf(str(_RED_RGB))
        assert isinstance(result, dict)

    def test_probe_exists_true(self):
        result = probe_xcf(str(_RED_RGB))
        assert result["exists"] is True

    def test_probe_valid_header_true(self):
        result = probe_xcf(str(_RED_RGB))
        assert result["valid_header"] is True

    def test_probe_width_height_1x1(self):
        result = probe_xcf(str(_RED_RGB))
        assert result["width"] == 1
        assert result["height"] == 1

    def test_probe_image_type_rgb(self):
        result = probe_xcf(str(_RED_RGB))
        assert result["image_type_name"] == "RGB"

    def test_probe_file_size_positive(self):
        result = probe_xcf(str(_RED_RGB))
        assert result["file_size"] > 0


class TestXcfMetadata:
    def test_layer_count_1x1(self):
        assert xcf_layer_count(str(_RED_RGB)) >= 1

    def test_pixel_count_1x1(self):
        assert xcf_pixel_count(str(_RED_RGB)) == 1

    def test_pixel_count_2x2(self):
        assert xcf_pixel_count(str(_GRAY_2X2)) == 4

    def test_is_rgb_true(self):
        assert xcf_is_rgb(str(_RED_RGB)) is True

    def test_is_rgb_false_for_gray(self):
        assert xcf_is_rgb(str(_GRAY_2X2)) is False

    def test_is_grayscale_gray(self):
        assert xcf_is_grayscale(str(_GRAY_2X2)) is True

    def test_is_square_1x1(self):
        assert xcf_is_square(str(_RED_RGB)) is True

    def test_aspect_ratio_1x1_is_one(self):
        ratio = xcf_aspect_ratio(str(_RED_RGB))
        assert ratio == 1.0

    def test_version_is_string(self):
        v = xcf_version(str(_RED_RGB))
        assert isinstance(v, str)

    def test_image_type_name_rgb(self):
        assert xcf_image_type_name(str(_RED_RGB)) == "RGB"

    def test_file_size_positive(self):
        assert xcf_file_size(str(_RED_RGB)) > 0

    def test_summary_returns_dict(self):
        s = xcf_summary(str(_RED_RGB))
        assert isinstance(s, dict)
