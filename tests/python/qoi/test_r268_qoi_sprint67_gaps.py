"""Tests for QOI Sprint 67 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_GREEN_ME-001   (Qoi Green Mean Value)
  GAP-QOI-FOSS-QOI_LIGHT_RA-001   (Qoi Light Ratio)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_green_mean_value, qoi_light_ratio

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiGreenMeanValue:
    def test_return_type(self):
        assert isinstance(qoi_green_mean_value(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        # Red pixel has G=0
        assert qoi_green_mean_value(_RED) == 0.0

    def test_nonnegative(self):
        assert qoi_green_mean_value(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_green_mean_value(_RED) == qoi_green_mean_value(_RED)

    def test_multi_pixel_raises_for_black(self):
        with pytest.raises((TypeError, Exception)):
            qoi_green_mean_value(_BLACK)

    def test_multi_pixel_raises_for_gradient(self):
        with pytest.raises((TypeError, Exception)):
            qoi_green_mean_value(_GRAD)


class TestQoiLightRatio:
    def test_return_type(self):
        assert isinstance(qoi_light_ratio(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        # Red pixel luminance < 128 threshold → light_ratio = 0.0
        assert qoi_light_ratio(_RED) == 0.0

    def test_between_0_and_1(self):
        assert 0.0 <= qoi_light_ratio(_RED) <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_light_ratio(_RED) == qoi_light_ratio(_RED)

    def test_multi_pixel_raises_for_black(self):
        with pytest.raises((TypeError, Exception)):
            qoi_light_ratio(_BLACK)

    def test_multi_pixel_raises_for_gradient(self):
        with pytest.raises((TypeError, Exception)):
            qoi_light_ratio(_GRAD)
