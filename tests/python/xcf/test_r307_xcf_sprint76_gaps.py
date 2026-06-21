"""Tests for XCF Sprint 76 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_AREA_TO_-001   (Xcf Area To Layer Ratio)
  GAP-XCF-FOSS-XCF_MIN_SIDE-001   (Xcf Min Side Length)
  GAP-XCF-FOSS-XCF_AVG_LAYE-001   (Xcf Avg Layer Area)
  GAP-XCF-FOSS-XCF_HEIGHT_T-001   (Xcf Height To Layer Ratio)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_area_to_layer_ratio, xcf_min_side_length, xcf_avg_layer_area, xcf_height_to_layer_ratio

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_DIR / "1x1-red-rgb.xcf")
_BLUE = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY = str(_DIR / "2x2-gray.xcf")


class TestXcfAreaToLayerRatio:
    def test_return_type(self):
        assert isinstance(xcf_area_to_layer_ratio(_RED), (int, float))

    def test_exact_1_for_1x1_red(self):
        assert xcf_area_to_layer_ratio(_RED) == pytest.approx(1.0)

    def test_exact_1_for_1x1_blue(self):
        assert xcf_area_to_layer_ratio(_BLUE) == pytest.approx(1.0)

    def test_exact_4_for_2x2(self):
        assert xcf_area_to_layer_ratio(_GRAY) == pytest.approx(4.0)

    def test_nonnegative(self):
        assert xcf_area_to_layer_ratio(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert xcf_area_to_layer_ratio(_RED) == xcf_area_to_layer_ratio(_RED)


class TestXcfMinSideLength:
    def test_return_type(self):
        assert isinstance(xcf_min_side_length(_RED), (int, float))

    def test_exact_1_for_1x1_red(self):
        assert xcf_min_side_length(_RED) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_min_side_length(_BLUE) == 1

    def test_exact_2_for_2x2(self):
        assert xcf_min_side_length(_GRAY) == 2

    def test_positive(self):
        assert xcf_min_side_length(_RED) > 0

    def test_consistent_across_calls(self):
        assert xcf_min_side_length(_RED) == xcf_min_side_length(_RED)


class TestXcfAvgLayerArea:
    def test_return_type(self):
        assert isinstance(xcf_avg_layer_area(_RED), (int, float))

    def test_exact_1_for_1x1_red(self):
        assert xcf_avg_layer_area(_RED) == pytest.approx(1.0)

    def test_exact_1_for_1x1_blue(self):
        assert xcf_avg_layer_area(_BLUE) == pytest.approx(1.0)

    def test_exact_4_for_2x2(self):
        assert xcf_avg_layer_area(_GRAY) == pytest.approx(4.0)

    def test_nonnegative(self):
        assert xcf_avg_layer_area(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert xcf_avg_layer_area(_RED) == xcf_avg_layer_area(_RED)


class TestXcfHeightToLayerRatio:
    def test_return_type(self):
        assert isinstance(xcf_height_to_layer_ratio(_RED), (int, float))

    def test_exact_1_for_1x1_red(self):
        assert xcf_height_to_layer_ratio(_RED) == pytest.approx(1.0)

    def test_exact_1_for_1x1_blue(self):
        assert xcf_height_to_layer_ratio(_BLUE) == pytest.approx(1.0)

    def test_exact_2_for_2x2(self):
        assert xcf_height_to_layer_ratio(_GRAY) == pytest.approx(2.0)

    def test_nonnegative(self):
        assert xcf_height_to_layer_ratio(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert xcf_height_to_layer_ratio(_RED) == xcf_height_to_layer_ratio(_RED)
