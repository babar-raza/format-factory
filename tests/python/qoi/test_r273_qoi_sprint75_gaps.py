"""Tests for QOI Sprint 75 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_RED_VARI-001   (Qoi Red Variance)
  GAP-QOI-FOSS-QOI_GREEN_VA-001   (Qoi Green Variance)
  GAP-QOI-FOSS-QOI_BLUE_VAR-001   (Qoi Blue Variance)
  GAP-QOI-FOSS-QOI_ENTROPY-001    (Qoi Entropy)
  GAP-QOI-FOSS-QOI_TOP_HALF-001   (Qoi Top Half Brightness)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_red_variance, qoi_green_variance, qoi_blue_variance, qoi_entropy, qoi_top_half_brightness

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiRedVariance:
    def test_return_type(self):
        assert isinstance(qoi_red_variance(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert qoi_red_variance(_RED) == 0.0

    def test_zero_for_black(self):
        assert qoi_red_variance(_BLACK) == 0.0

    def test_exact_9031_25_for_gradient(self):
        assert qoi_red_variance(_GRAD) == pytest.approx(9031.25)

    def test_nonnegative(self):
        assert qoi_red_variance(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_red_variance(_RED) == qoi_red_variance(_RED)


class TestQoiGreenVariance:
    def test_return_type(self):
        assert isinstance(qoi_green_variance(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert qoi_green_variance(_RED) == 0.0

    def test_zero_for_black(self):
        assert qoi_green_variance(_BLACK) == 0.0

    def test_exact_9031_25_for_gradient(self):
        assert qoi_green_variance(_GRAD) == pytest.approx(9031.25)

    def test_nonnegative(self):
        assert qoi_green_variance(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_green_variance(_RED) == qoi_green_variance(_RED)


class TestQoiBlueVariance:
    def test_return_type(self):
        assert isinstance(qoi_blue_variance(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert qoi_blue_variance(_RED) == 0.0

    def test_zero_for_black(self):
        assert qoi_blue_variance(_BLACK) == 0.0

    def test_exact_9031_25_for_gradient(self):
        assert qoi_blue_variance(_GRAD) == pytest.approx(9031.25)

    def test_nonnegative(self):
        assert qoi_blue_variance(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_blue_variance(_RED) == qoi_blue_variance(_RED)


class TestQoiEntropy:
    def test_return_type(self):
        assert isinstance(qoi_entropy(_RED), (int, float))

    def test_zero_for_1x1_red(self):
        assert qoi_entropy(_RED) == pytest.approx(0.0, abs=1e-9)

    def test_zero_for_black(self):
        assert qoi_entropy(_BLACK) == pytest.approx(0.0, abs=1e-9)

    def test_exact_2_0_for_gradient(self):
        assert qoi_entropy(_GRAD) == pytest.approx(2.0)

    def test_consistent_across_calls(self):
        assert qoi_entropy(_RED) == qoi_entropy(_RED)


class TestQoiTopHalfBrightness:
    def test_return_type(self):
        assert isinstance(qoi_top_half_brightness(_RED), (int, float))

    def test_approx_76_245_for_1x1_red(self):
        assert qoi_top_half_brightness(_RED) == pytest.approx(76.245, rel=1e-2)

    def test_zero_for_black(self):
        assert qoi_top_half_brightness(_BLACK) == 0.0

    def test_exact_127_5_for_gradient(self):
        assert qoi_top_half_brightness(_GRAD) == pytest.approx(127.5)

    def test_nonnegative(self):
        assert qoi_top_half_brightness(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_top_half_brightness(_RED) == qoi_top_half_brightness(_RED)
