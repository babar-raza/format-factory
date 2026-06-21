"""Tests for xcf_width_plus_height and xcf_layer_pixel_count (Sprint r297)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_width_plus_height, xcf_layer_pixel_count

_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"


class TestXcfWidthPlusHeight:
    """Tests for xcf_width_plus_height."""

    def test_1x1_red_rgb_sum_is_2(self):
        """1x1-red-rgb.xcf: width=1, height=1 → sum=2."""
        result = xcf_width_plus_height(_XCF / "1x1-red-rgb.xcf")
        assert result == 2

    def test_1x1_rgba_blue_sum_is_2(self):
        """1x1-rgba-blue.xcf: width=1, height=1 → sum=2."""
        result = xcf_width_plus_height(_XCF / "1x1-rgba-blue.xcf")
        assert result == 2

    def test_2x2_gray_sum_is_4(self):
        """2x2-gray.xcf: width=2, height=2 → sum=4."""
        result = xcf_width_plus_height(_XCF / "2x2-gray.xcf")
        assert result == 4

    def test_returns_int(self):
        result = xcf_width_plus_height(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-red-rgb.xcf", "1x1-rgba-blue.xcf", "2x2-gray.xcf"]:
            assert xcf_width_plus_height(_XCF / f) >= 0

    def test_2x2_gray_larger_than_1x1(self):
        r1 = xcf_width_plus_height(_XCF / "1x1-red-rgb.xcf")
        r2 = xcf_width_plus_height(_XCF / "2x2-gray.xcf")
        assert r2 > r1


class TestXcfLayerPixelCount:
    """Tests for xcf_layer_pixel_count."""

    def test_1x1_red_rgb_layer_pixel_count_is_1(self):
        """1x1-red-rgb.xcf: 1 layer × 1×1 pixels = 1."""
        result = xcf_layer_pixel_count(_XCF / "1x1-red-rgb.xcf")
        assert result == 1

    def test_1x1_rgba_blue_layer_pixel_count_is_1(self):
        """1x1-rgba-blue.xcf: 1 layer × 1×1 pixels = 1."""
        result = xcf_layer_pixel_count(_XCF / "1x1-rgba-blue.xcf")
        assert result == 1

    def test_2x2_gray_layer_pixel_count_is_4(self):
        """2x2-gray.xcf: 1 layer × 2×2 pixels = 4."""
        result = xcf_layer_pixel_count(_XCF / "2x2-gray.xcf")
        assert result == 4

    def test_returns_int(self):
        result = xcf_layer_pixel_count(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-red-rgb.xcf", "1x1-rgba-blue.xcf", "2x2-gray.xcf"]:
            assert xcf_layer_pixel_count(_XCF / f) >= 0

    def test_2x2_gray_has_more_layer_pixels(self):
        r1 = xcf_layer_pixel_count(_XCF / "1x1-red-rgb.xcf")
        r2 = xcf_layer_pixel_count(_XCF / "2x2-gray.xcf")
        assert r2 > r1
