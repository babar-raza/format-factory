"""Tests for PPM Sprint 73 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_RED_VARI-001   (Ppm Red Variance)
  GAP-PPM-FOSS-PPM_GREEN_VA-001   (Ppm Green Variance)
  GAP-PPM-FOSS-PPM_BLUE_VAR-001   (Ppm Blue Variance)
  GAP-PPM-FOSS-PPM_ENTROPY-001    (Ppm Entropy)
  GAP-PPM-FOSS-PPM_TOP_HALF-001   (Ppm Top Half Brightness)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_red_variance, ppm_green_variance, ppm_blue_variance, ppm_entropy, ppm_top_half_brightness

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")
_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmRedVariance:
    def test_return_type(self):
        assert isinstance(ppm_red_variance(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert ppm_red_variance(_RED) == 0.0

    def test_exact_16256_25_for_rgbw(self):
        assert ppm_red_variance(_RGBW) == pytest.approx(16256.25)

    def test_approx_10837_for_gradient(self):
        assert ppm_red_variance(_GRAD) == pytest.approx(10837.56, rel=1e-2)

    def test_nonnegative(self):
        assert ppm_red_variance(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_red_variance(_RED) == ppm_red_variance(_RED)


class TestPpmGreenVariance:
    def test_return_type(self):
        assert isinstance(ppm_green_variance(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert ppm_green_variance(_RED) == 0.0

    def test_exact_16256_25_for_rgbw(self):
        assert ppm_green_variance(_RGBW) == pytest.approx(16256.25)

    def test_approx_10837_for_gradient(self):
        assert ppm_green_variance(_GRAD) == pytest.approx(10837.56, rel=1e-2)

    def test_nonnegative(self):
        assert ppm_green_variance(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_green_variance(_RED) == ppm_green_variance(_RED)


class TestPpmBlueVariance:
    def test_return_type(self):
        assert isinstance(ppm_blue_variance(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert ppm_blue_variance(_RED) == 0.0

    def test_exact_16256_25_for_rgbw(self):
        assert ppm_blue_variance(_RGBW) == pytest.approx(16256.25)

    def test_approx_10837_for_gradient(self):
        assert ppm_blue_variance(_GRAD) == pytest.approx(10837.56, rel=1e-2)

    def test_nonnegative(self):
        assert ppm_blue_variance(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_blue_variance(_RED) == ppm_blue_variance(_RED)


class TestPpmEntropy:
    def test_return_type(self):
        assert isinstance(ppm_entropy(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert ppm_entropy(_RED) == pytest.approx(0.0, abs=1e-9)

    def test_approx_0_811_for_rgbw(self):
        assert ppm_entropy(_RGBW) == pytest.approx(0.8113, rel=1e-2)

    def test_approx_1_585_for_gradient(self):
        assert ppm_entropy(_GRAD) == pytest.approx(1.585, rel=1e-2)

    def test_consistent_across_calls(self):
        assert ppm_entropy(_RED) == ppm_entropy(_RED)


class TestPpmTopHalfBrightness:
    def test_return_type(self):
        assert isinstance(ppm_top_half_brightness(_RED), (int, float))

    def test_exact_85_for_1x1_red(self):
        assert ppm_top_half_brightness(_RED) == pytest.approx(85.0)

    def test_exact_85_for_rgbw(self):
        assert ppm_top_half_brightness(_RGBW) == pytest.approx(85.0)

    def test_approx_127_67_for_gradient(self):
        assert ppm_top_half_brightness(_GRAD) == pytest.approx(127.667, rel=1e-2)

    def test_nonnegative(self):
        assert ppm_top_half_brightness(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_top_half_brightness(_RED) == ppm_top_half_brightness(_RED)
