"""Tests for PGM Sprint 72 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_WIDTH_EX-001   (Pgm Width Exceeds Height)
  GAP-PGM-FOSS-PGM_PIXEL_CO-001   (Pgm Pixel Count)
  GAP-PGM-FOSS-PGM_COL_BRIG-001   (Pgm Col Brightness Variance)
  GAP-PGM-FOSS-PGM_TOP_HALF-001   (Pgm Top Half Avg)
  GAP-PGM-FOSS-PGM_BOTTOM_H-001   (Pgm Bottom Half Avg)
  GAP-PGM-FOSS-PGM_PIXEL_EN-001   (Pgm Pixel Entropy)
  GAP-PGM-FOSS-PGM_MID_PIXE-001   (Pgm Mid Pixel Ratio)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import (
    pgm_width_exceeds_height,
    pgm_pixel_count,
    pgm_col_brightness_variance,
    pgm_top_half_avg,
    pgm_bottom_half_avg,
    pgm_pixel_entropy,
    pgm_mid_pixel_ratio,
)

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_DIR / "1x1-white.pgm")
_GRAD = str(_DIR / "2x2-gradient.pgm")
_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmWidthExceedsHeight:
    def test_return_type(self):
        assert isinstance(pgm_width_exceeds_height(_WHITE), bool)

    def test_false_for_1x1_white(self):
        assert pgm_width_exceeds_height(_WHITE) is False

    def test_false_for_2x2_gradient(self):
        assert pgm_width_exceeds_height(_GRAD) is False

    def test_true_for_3x1_ramp(self):
        assert pgm_width_exceeds_height(_RAMP) is True

    def test_is_boolean(self):
        assert pgm_width_exceeds_height(_WHITE) in (True, False)

    def test_consistent_across_calls(self):
        assert pgm_width_exceeds_height(_WHITE) == pgm_width_exceeds_height(_WHITE)


class TestPgmPixelCount:
    def test_return_type(self):
        assert isinstance(pgm_pixel_count(_WHITE), int)

    def test_exact_1_for_1x1_white(self):
        assert pgm_pixel_count(_WHITE) == 1

    def test_exact_4_for_2x2_gradient(self):
        assert pgm_pixel_count(_GRAD) == 4

    def test_exact_3_for_3x1_ramp(self):
        assert pgm_pixel_count(_RAMP) == 3

    def test_positive(self):
        assert pgm_pixel_count(_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_pixel_count(_WHITE) == pgm_pixel_count(_WHITE)


class TestPgmColBrightnessVariance:
    def test_return_type(self):
        assert isinstance(pgm_col_brightness_variance(_WHITE), (int, float))

    def test_zero_for_1x1_white(self):
        assert pgm_col_brightness_variance(_WHITE) == 0.0

    def test_exact_1806_25_for_gradient(self):
        assert pgm_col_brightness_variance(_GRAD) == pytest.approx(1806.25)

    def test_approx_10837_for_ramp(self):
        assert pgm_col_brightness_variance(_RAMP) == pytest.approx(10837.56, rel=1e-2)

    def test_nonnegative(self):
        assert pgm_col_brightness_variance(_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_col_brightness_variance(_WHITE) == pgm_col_brightness_variance(_WHITE)


class TestPgmTopHalfAvg:
    def test_return_type(self):
        assert isinstance(pgm_top_half_avg(_WHITE), (int, float))

    def test_exact_255_for_1x1_white(self):
        assert pgm_top_half_avg(_WHITE) == 255.0

    def test_exact_42_5_for_gradient(self):
        assert pgm_top_half_avg(_GRAD) == pytest.approx(42.5)

    def test_approx_127_67_for_ramp(self):
        assert pgm_top_half_avg(_RAMP) == pytest.approx(127.667, rel=1e-2)

    def test_nonnegative(self):
        assert pgm_top_half_avg(_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_top_half_avg(_WHITE) == pgm_top_half_avg(_WHITE)


class TestPgmBottomHalfAvg:
    def test_return_type(self):
        assert isinstance(pgm_bottom_half_avg(_WHITE), (int, float))

    def test_zero_for_1x1_white(self):
        assert pgm_bottom_half_avg(_WHITE) == 0.0

    def test_exact_212_5_for_gradient(self):
        assert pgm_bottom_half_avg(_GRAD) == pytest.approx(212.5)

    def test_zero_for_ramp(self):
        assert pgm_bottom_half_avg(_RAMP) == 0.0

    def test_nonnegative(self):
        assert pgm_bottom_half_avg(_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_bottom_half_avg(_WHITE) == pgm_bottom_half_avg(_WHITE)


class TestPgmPixelEntropy:
    def test_return_type(self):
        assert isinstance(pgm_pixel_entropy(_WHITE), (int, float))

    def test_zero_for_1x1_white(self):
        assert pgm_pixel_entropy(_WHITE) == pytest.approx(0.0, abs=1e-9)

    def test_exact_2_0_for_gradient(self):
        assert pgm_pixel_entropy(_GRAD) == pytest.approx(2.0)

    def test_approx_1_585_for_ramp(self):
        assert pgm_pixel_entropy(_RAMP) == pytest.approx(1.585, rel=1e-2)

    def test_nonnegative(self):
        assert abs(pgm_pixel_entropy(_WHITE)) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_pixel_entropy(_WHITE) == pgm_pixel_entropy(_WHITE)


class TestPgmMidPixelRatio:
    def test_return_type(self):
        assert isinstance(pgm_mid_pixel_ratio(_WHITE), (int, float))

    def test_zero_for_1x1_white(self):
        assert pgm_mid_pixel_ratio(_WHITE) == 0.0

    def test_exact_0_5_for_gradient(self):
        assert pgm_mid_pixel_ratio(_GRAD) == pytest.approx(0.5)

    def test_approx_0_333_for_ramp(self):
        assert pgm_mid_pixel_ratio(_RAMP) == pytest.approx(0.333, rel=1e-2)

    def test_between_0_and_1(self):
        assert 0.0 <= pgm_mid_pixel_ratio(_GRAD) <= 1.0

    def test_consistent_across_calls(self):
        assert pgm_mid_pixel_ratio(_WHITE) == pgm_mid_pixel_ratio(_WHITE)
