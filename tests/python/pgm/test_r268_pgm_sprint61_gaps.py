"""Tests for PGM Sprint 61 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_CENTER_B-001   (Pgm Center Brightness)
  GAP-PGM-FOSS-PGM_GRADIENT-001   (Pgm Gradient Magnitude)
  GAP-PGM-FOSS-PGM_PERCENTI-001   (Pgm Percentile Value)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_center_brightness, pgm_gradient_magnitude, pgm_percentile_value

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1 = str(_DIR / "1x1-white.pgm")
_2X2 = str(_DIR / "2x2-gradient.pgm")
_3X1 = str(_DIR / "3x1-ramp.pgm")


class TestPgmCenterBrightness:
    def test_return_type(self):
        assert isinstance(pgm_center_brightness(_1X1), (int, float))

    def test_zero_for_1x1(self):
        assert pgm_center_brightness(_1X1) == 0.0

    def test_zero_for_2x2(self):
        assert pgm_center_brightness(_2X2) == 0.0

    def test_zero_for_3x1(self):
        assert pgm_center_brightness(_3X1) == 0.0

    def test_nonnegative(self):
        assert pgm_center_brightness(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_center_brightness(_1X1) == pgm_center_brightness(_1X1)


class TestPgmGradientMagnitude:
    def test_return_type(self):
        assert isinstance(pgm_gradient_magnitude(_1X1), (int, float))

    def test_zero_for_1x1(self):
        assert pgm_gradient_magnitude(_1X1) == 0.0

    def test_exact_85_for_2x2(self):
        assert pgm_gradient_magnitude(_2X2) == 85.0

    def test_exact_127_5_for_3x1(self):
        assert pgm_gradient_magnitude(_3X1) == 127.5

    def test_nonnegative(self):
        assert pgm_gradient_magnitude(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_gradient_magnitude(_1X1) == pgm_gradient_magnitude(_1X1)


class TestPgmPercentileValue:
    def test_return_type(self):
        assert isinstance(pgm_percentile_value(_1X1), int)

    def test_exact_255_for_1x1_white(self):
        assert pgm_percentile_value(_1X1) == 255

    def test_exact_170_for_2x2_gradient(self):
        assert pgm_percentile_value(_2X2) == 170

    def test_exact_128_for_3x1_ramp(self):
        assert pgm_percentile_value(_3X1) == 128

    def test_between_0_and_255(self):
        assert 0 <= pgm_percentile_value(_1X1) <= 255

    def test_consistent_across_calls(self):
        assert pgm_percentile_value(_1X1) == pgm_percentile_value(_1X1)
