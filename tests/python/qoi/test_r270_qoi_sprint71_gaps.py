"""Tests for QOI Sprint 71 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_CENTER_P-001   (Qoi Center Pixel Brightness)
  GAP-QOI-FOSS-QOI_EDGE_BRI-001   (Qoi Edge Brightness)
  GAP-QOI-FOSS-QOI_RED_GREE-001   (Qoi Red Green Diff)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_center_pixel_brightness, qoi_edge_brightness, qoi_red_green_diff

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiCenterPixelBrightness:
    def test_return_type(self):
        assert isinstance(qoi_center_pixel_brightness(_RED), (int, float))

    def test_exact_85_for_1x1_red(self):
        assert qoi_center_pixel_brightness(_RED) == pytest.approx(85.0)

    def test_zero_for_black(self):
        assert qoi_center_pixel_brightness(_BLACK) == 0.0

    def test_exact_170_for_gradient(self):
        assert qoi_center_pixel_brightness(_GRAD) == pytest.approx(170.0)

    def test_nonnegative(self):
        assert qoi_center_pixel_brightness(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_center_pixel_brightness(_RED) == qoi_center_pixel_brightness(_RED)


class TestQoiEdgeBrightness:
    def test_return_type(self):
        assert isinstance(qoi_edge_brightness(_RED), (int, float))

    def test_exact_85_for_1x1_red(self):
        assert qoi_edge_brightness(_RED) == pytest.approx(85.0)

    def test_zero_for_black(self):
        assert qoi_edge_brightness(_BLACK) == 0.0

    def test_approx_127_5_for_gradient(self):
        assert qoi_edge_brightness(_GRAD) == pytest.approx(127.5)

    def test_nonnegative(self):
        assert qoi_edge_brightness(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_edge_brightness(_RED) == qoi_edge_brightness(_RED)


class TestQoiRedGreenDiff:
    def test_return_type(self):
        assert isinstance(qoi_red_green_diff(_RED), (int, float))

    def test_exact_255_for_1x1_red(self):
        assert qoi_red_green_diff(_RED) == pytest.approx(255.0)

    def test_zero_for_black(self):
        assert qoi_red_green_diff(_BLACK) == 0.0

    def test_zero_for_gradient(self):
        assert qoi_red_green_diff(_GRAD) == 0.0

    def test_nonnegative(self):
        assert qoi_red_green_diff(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_red_green_diff(_RED) == qoi_red_green_diff(_RED)
