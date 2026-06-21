"""
Sprint 108 — XCF analytics round 4.
25 tests for 5 new analytics functions:
  xcf_layer_count_exceeds_one, xcf_width_plus_height, xcf_file_size_per_layer,
  xcf_is_landscape, xcf_pixel_count_per_layer
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_layer_count_exceeds_one,
    xcf_width_plus_height,
    xcf_file_size_per_layer,
    xcf_is_landscape,
    xcf_pixel_count_per_layer,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_SAMPLES / "1x1-red-rgb.xcf")
_GRAY = str(_SAMPLES / "2x2-gray.xcf")
_BLUE = str(_SAMPLES / "1x1-rgba-blue.xcf")


# --- xcf_layer_count_exceeds_one ---

class TestXcfLayerCountExceedsOne:
    def test_returns_bool(self):
        result = xcf_layer_count_exceeds_one(_RED)
        assert isinstance(result, bool)

    def test_single_layer_is_false(self):
        # minimal XCF files typically have 1 layer
        result = xcf_layer_count_exceeds_one(_RED)
        assert result is False

    def test_gray_bool(self):
        result = xcf_layer_count_exceeds_one(_GRAY)
        assert isinstance(result, bool)

    def test_blue_bool(self):
        result = xcf_layer_count_exceeds_one(_BLUE)
        assert isinstance(result, bool)

    def test_consistent_with_layer_count(self):
        from src.python.xcf import xcf_layer_count
        lc = xcf_layer_count(_RED)
        assert xcf_layer_count_exceeds_one(_RED) == (lc > 1)


# --- xcf_width_plus_height ---

class TestXcfWidthPlusHeight:
    def test_returns_int(self):
        result = xcf_width_plus_height(_RED)
        assert isinstance(result, int)

    def test_positive(self):
        result = xcf_width_plus_height(_RED)
        assert result > 0

    def test_1x1_is_two(self):
        result = xcf_width_plus_height(_RED)
        assert result == 2

    def test_2x2_is_four(self):
        result = xcf_width_plus_height(_GRAY)
        assert result == 4

    def test_blue_1x1_is_two(self):
        result = xcf_width_plus_height(_BLUE)
        assert result == 2


# --- xcf_file_size_per_layer ---

class TestXcfFileSizePerLayer:
    def test_returns_float(self):
        result = xcf_file_size_per_layer(_RED)
        assert isinstance(result, float)

    def test_positive(self):
        result = xcf_file_size_per_layer(_RED)
        assert result > 0.0

    def test_gray_positive(self):
        result = xcf_file_size_per_layer(_GRAY)
        assert result > 0.0

    def test_blue_positive(self):
        result = xcf_file_size_per_layer(_BLUE)
        assert result > 0.0

    def test_non_negative(self):
        result = xcf_file_size_per_layer(_RED)
        assert result >= 0.0


# --- xcf_is_landscape ---

class TestXcfIsLandscape:
    def test_returns_bool(self):
        result = xcf_is_landscape(_RED)
        assert isinstance(result, bool)

    def test_1x1_is_false(self):
        # 1x1: width == height → not landscape
        result = xcf_is_landscape(_RED)
        assert result is False

    def test_2x2_is_false(self):
        result = xcf_is_landscape(_GRAY)
        assert result is False

    def test_blue_1x1_is_false(self):
        result = xcf_is_landscape(_BLUE)
        assert result is False

    def test_is_bool_type(self):
        result = xcf_is_landscape(_GRAY)
        assert type(result) is bool


# --- xcf_pixel_count_per_layer ---

class TestXcfPixelCountPerLayer:
    def test_returns_float(self):
        result = xcf_pixel_count_per_layer(_RED)
        assert isinstance(result, float)

    def test_positive(self):
        result = xcf_pixel_count_per_layer(_RED)
        assert result > 0.0

    def test_1x1_one_layer_is_one(self):
        result = xcf_pixel_count_per_layer(_RED)
        assert abs(result - 1.0) < 0.01

    def test_2x2_one_layer_is_four(self):
        result = xcf_pixel_count_per_layer(_GRAY)
        assert abs(result - 4.0) < 0.01

    def test_non_negative(self):
        result = xcf_pixel_count_per_layer(_BLUE)
        assert result >= 0.0
