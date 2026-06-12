"""
test_xcf_summary.py

Sprint: FORMAT-FACTORY-GAP-DRIVEN-PRODUCT-RNEXT-001
Product feature test for xcf_summary (Lane D).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_summary, XcfError

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfSummary:
    def test_returns_dict(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(result, dict)

    def test_required_keys_present(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        for key in ("path", "version", "width", "height", "image_type_name", "num_layers", "pixel_count", "file_size_bytes"):
            assert key in result, f"Missing key: {key}"

    def test_1x1_dimensions(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        assert result["width"] == 1
        assert result["height"] == 1

    def test_pixel_count_equals_width_times_height(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        assert result["pixel_count"] == result["width"] * result["height"]

    def test_2x2_pixel_count(self):
        result = xcf_summary(_SAMPLES / "2x2-gray.xcf")
        assert result["pixel_count"] == 4

    def test_image_type_name_is_string(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(result["image_type_name"], str)
        assert result["image_type_name"] in ("RGB", "Grayscale", "Indexed")

    def test_rgb_image_type_name(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        assert result["image_type_name"] == "RGB"

    def test_gray_image_type_name(self):
        result = xcf_summary(_SAMPLES / "2x2-gray.xcf")
        assert result["image_type_name"] == "Grayscale"

    def test_file_size_positive(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        assert result["file_size_bytes"] > 0

    def test_num_layers_positive(self):
        result = xcf_summary(_SAMPLES / "1x1-red-rgb.xcf")
        assert result["num_layers"] >= 1

    def test_missing_file_raises(self):
        with pytest.raises(XcfError):
            xcf_summary(_SAMPLES / "ghost.xcf")
