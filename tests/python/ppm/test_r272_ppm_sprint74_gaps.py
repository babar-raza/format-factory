"""Tests for PPM Sprint 74 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_GREEN_ME-001   (Ppm Green Mean Value)
  GAP-PPM-FOSS-PPM_BLUE_MEA-001   (Ppm Blue Mean Value)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_green_mean_value, ppm_blue_mean_value

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")
_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmGreenMeanValue:
    def test_return_type(self):
        assert isinstance(ppm_green_mean_value(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert ppm_green_mean_value(_RED) == 0.0

    def test_exact_127_5_for_rgbw(self):
        assert ppm_green_mean_value(_RGBW) == pytest.approx(127.5)

    def test_approx_127_67_for_gradient(self):
        assert ppm_green_mean_value(_GRAD) == pytest.approx(127.667, rel=1e-2)

    def test_nonnegative(self):
        assert ppm_green_mean_value(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_green_mean_value(_RED) == ppm_green_mean_value(_RED)


class TestPpmBlueMeanValue:
    def test_return_type(self):
        assert isinstance(ppm_blue_mean_value(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert ppm_blue_mean_value(_RED) == 0.0

    def test_exact_127_5_for_rgbw(self):
        assert ppm_blue_mean_value(_RGBW) == pytest.approx(127.5)

    def test_approx_127_67_for_gradient(self):
        assert ppm_blue_mean_value(_GRAD) == pytest.approx(127.667, rel=1e-2)

    def test_nonnegative(self):
        assert ppm_blue_mean_value(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_blue_mean_value(_RED) == ppm_blue_mean_value(_RED)
