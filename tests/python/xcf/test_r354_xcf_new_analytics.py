"""
Sprint 90 — XCF analytics round 3.
25 tests for 5 new analytics functions:
  xcf_avg_layer_area, xcf_layer_name_count, xcf_width_to_layer_ratio,
  xcf_height_to_layer_ratio, xcf_perimeter
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_avg_layer_area,
    xcf_layer_name_count,
    xcf_width_to_layer_ratio,
    xcf_height_to_layer_ratio,
    xcf_perimeter,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_1X1_RGB = str(_SAMPLES / "1x1-red-rgb.xcf")
_1X1_RGBA = str(_SAMPLES / "1x1-rgba-blue.xcf")
_2X2 = str(_SAMPLES / "2x2-gray.xcf")


# --- xcf_avg_layer_area ---

class TestXcfAvgLayerArea:
    def test_returns_float(self):
        result = xcf_avg_layer_area(_1X1_RGB)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = xcf_avg_layer_area(_1X1_RGB)
        assert result >= 0.0

    def test_1x1_rgb(self):
        result = xcf_avg_layer_area(_1X1_RGB)
        assert result >= 0.0

    def test_2x2(self):
        result = xcf_avg_layer_area(_2X2)
        assert isinstance(result, float) and result >= 0.0

    def test_1x1_rgba(self):
        result = xcf_avg_layer_area(_1X1_RGBA)
        assert result >= 0.0


# --- xcf_layer_name_count ---

class TestXcfLayerNameCount:
    def test_returns_int(self):
        result = xcf_layer_name_count(_1X1_RGB)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_layer_name_count(_1X1_RGB)
        assert result >= 0

    def test_equals_num_layers(self):
        from src.python.xcf import xcf_layer_count
        result = xcf_layer_name_count(_1X1_RGB)
        layers = xcf_layer_count(_1X1_RGB)
        assert result == layers

    def test_2x2(self):
        result = xcf_layer_name_count(_2X2)
        assert result >= 0

    def test_rgba(self):
        result = xcf_layer_name_count(_1X1_RGBA)
        assert result >= 0


# --- xcf_width_to_layer_ratio ---

class TestXcfWidthToLayerRatio:
    def test_returns_float(self):
        result = xcf_width_to_layer_ratio(_1X1_RGB)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = xcf_width_to_layer_ratio(_1X1_RGB)
        assert result >= 0.0

    def test_2x2(self):
        result = xcf_width_to_layer_ratio(_2X2)
        assert isinstance(result, float) and result >= 0.0

    def test_1x1_rgb(self):
        result = xcf_width_to_layer_ratio(_1X1_RGB)
        assert result >= 0.0

    def test_rgba(self):
        result = xcf_width_to_layer_ratio(_1X1_RGBA)
        assert result >= 0.0


# --- xcf_height_to_layer_ratio ---

class TestXcfHeightToLayerRatio:
    def test_returns_float(self):
        result = xcf_height_to_layer_ratio(_1X1_RGB)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = xcf_height_to_layer_ratio(_1X1_RGB)
        assert result >= 0.0

    def test_2x2(self):
        result = xcf_height_to_layer_ratio(_2X2)
        assert isinstance(result, float) and result >= 0.0

    def test_1x1_rgb(self):
        result = xcf_height_to_layer_ratio(_1X1_RGB)
        assert result >= 0.0

    def test_rgba(self):
        result = xcf_height_to_layer_ratio(_1X1_RGBA)
        assert result >= 0.0


# --- xcf_perimeter ---

class TestXcfPerimeter:
    def test_returns_int(self):
        result = xcf_perimeter(_1X1_RGB)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_perimeter(_1X1_RGB)
        assert result >= 0

    def test_1x1_is_4(self):
        result = xcf_perimeter(_1X1_RGB)
        assert result == 4

    def test_2x2_is_8(self):
        result = xcf_perimeter(_2X2)
        assert result == 8

    def test_rgba(self):
        result = xcf_perimeter(_1X1_RGBA)
        assert result >= 0
