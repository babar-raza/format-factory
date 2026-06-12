"""
tests/python/xcf/test_r177_xcf_aspect_ratio.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT45-001
Tests for xcf_aspect_ratio() — width/height ratio of an XCF image.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_aspect_ratio

SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfAspectRatio:
    def test_1x1_red_rgb_aspect_ratio(self):
        result = xcf_aspect_ratio(SAMPLES / "1x1-red-rgb.xcf")
        assert result == 1.0

    def test_1x1_rgba_blue_aspect_ratio(self):
        result = xcf_aspect_ratio(SAMPLES / "1x1-rgba-blue.xcf")
        assert result == 1.0

    def test_2x2_gray_aspect_ratio(self):
        result = xcf_aspect_ratio(SAMPLES / "2x2-gray.xcf")
        assert result == 1.0

    def test_returns_float(self):
        result = xcf_aspect_ratio(SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(result, float)

    def test_aspect_ratio_is_positive(self):
        result = xcf_aspect_ratio(SAMPLES / "1x1-red-rgb.xcf")
        assert result > 0.0

    def test_exported_from_init(self):
        from src.python.xcf import xcf_aspect_ratio as fn
        result = fn(SAMPLES / "1x1-red-rgb.xcf")
        assert result == 1.0
