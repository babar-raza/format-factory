"""
tests/python/xcf/test_r180_xcf_is_square.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT48-001
Tests for xcf_is_square() — True if XCF image width == height.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_is_square

SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfIsSquare:
    def test_1x1_red_is_square(self):
        assert xcf_is_square(SAMPLES / "1x1-red-rgb.xcf") is True

    def test_1x1_rgba_is_square(self):
        assert xcf_is_square(SAMPLES / "1x1-rgba-blue.xcf") is True

    def test_2x2_gray_is_square(self):
        assert xcf_is_square(SAMPLES / "2x2-gray.xcf") is True

    def test_returns_bool(self):
        result = xcf_is_square(SAMPLES / "1x1-red-rgb.xcf")
        assert isinstance(result, bool)

    def test_consistent_with_dimensions(self):
        from src.python.xcf.xcf_parser import xcf_image_dimensions
        dims = xcf_image_dimensions(SAMPLES / "2x2-gray.xcf")
        expected = dims["width"] == dims["height"]
        assert xcf_is_square(SAMPLES / "2x2-gray.xcf") == expected

    def test_exported_from_init(self):
        from src.python.xcf import xcf_is_square as fn
        assert fn(SAMPLES / "1x1-red-rgb.xcf") is True
