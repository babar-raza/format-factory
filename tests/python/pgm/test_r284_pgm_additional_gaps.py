"""
Tests for additional PGM analytics gap closure (9 FOSS gaps).
Closes: PGM_DARK_PIX, PGM_ROW_BRIG, PGM_CONTRAST, PGM_NORMALIZ,
        PGM_ABOVE_ME, PGM_MAXVAL, PGM_MIDPOINT, PGM_MEDIAN_B, PGM_PIXEL_VA
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_dark_pixel_ratio,
    pgm_row_brightness_variance,
    pgm_contrast_ratio,
    pgm_normalized_mean,
    pgm_above_mean_ratio,
    pgm_maxval,
    pgm_midpoint_gray,
    pgm_median_brightness,
    pgm_pixel_value_range,
)

_PGM_WHITE = _REPO / "samples/by-format/pgm/valid/1x1-white.pgm"
_PGM_RAMP = _REPO / "samples/by-format/pgm/valid/3x1-ramp.pgm"
_PGM_GRAD = _REPO / "samples/by-format/pgm/valid/2x2-gradient.pgm"


class TestPgmDarkPixelRatio:
    def test_returns_float(self):
        assert isinstance(pgm_dark_pixel_ratio(_PGM_WHITE), float)

    def test_white_is_not_dark(self):
        # 1x1-white: pixel=255 → no dark pixels → 0.0
        assert pgm_dark_pixel_ratio(_PGM_WHITE) == pytest.approx(0.0)

    def test_ramp_has_dark_pixels(self):
        # 3x1-ramp: [0, 128, 255] — pixel 0 is dark → ratio > 0
        assert pgm_dark_pixel_ratio(_PGM_RAMP) > 0.0

    def test_bounded(self):
        assert 0.0 <= pgm_dark_pixel_ratio(_PGM_GRAD) <= 1.0


class TestPgmRowBrightnessVariance:
    def test_returns_float(self):
        assert isinstance(pgm_row_brightness_variance(_PGM_WHITE), float)

    def test_nonnegative(self):
        assert pgm_row_brightness_variance(_PGM_WHITE) >= 0.0

    def test_single_row_zero_variance(self):
        # 1x1 and 3x1 have 1 row each → variance of 1 value = 0
        assert pgm_row_brightness_variance(_PGM_WHITE) == pytest.approx(0.0)

    def test_multirow_nonnegative(self):
        # 2x2-gradient has 2 rows with different avg brightness
        assert pgm_row_brightness_variance(_PGM_GRAD) >= 0.0


class TestPgmContrastRatio:
    def test_returns_float(self):
        assert isinstance(pgm_contrast_ratio(_PGM_WHITE), float)

    def test_white_zero_contrast(self):
        # 1x1-white: all same value → contrast = 0
        assert pgm_contrast_ratio(_PGM_WHITE) == pytest.approx(0.0)

    def test_ramp_high_contrast(self):
        # 3x1-ramp: [0, 128, 255] → range/maxval = 1.0
        assert pgm_contrast_ratio(_PGM_RAMP) == pytest.approx(1.0)

    def test_bounded(self):
        assert 0.0 <= pgm_contrast_ratio(_PGM_GRAD) <= 1.0


class TestPgmNormalizedMean:
    def test_returns_float(self):
        assert isinstance(pgm_normalized_mean(_PGM_WHITE), float)

    def test_white_is_one(self):
        assert pgm_normalized_mean(_PGM_WHITE) == pytest.approx(1.0)

    def test_bounded(self):
        assert 0.0 <= pgm_normalized_mean(_PGM_GRAD) <= 1.0

    def test_ramp_near_half(self):
        # 3x1-ramp: mean ≈ 127.67/255 ≈ 0.5
        assert pgm_normalized_mean(_PGM_RAMP) == pytest.approx(0.5, abs=0.01)


class TestPgmAboveMeanRatio:
    def test_returns_float(self):
        assert isinstance(pgm_above_mean_ratio(_PGM_WHITE), float)

    def test_white_zero_above_mean(self):
        # All pixels equal the mean → none above
        assert pgm_above_mean_ratio(_PGM_WHITE) == pytest.approx(0.0)

    def test_bounded(self):
        assert 0.0 <= pgm_above_mean_ratio(_PGM_RAMP) <= 1.0

    def test_ramp_has_some_above_mean(self):
        # 3x1-ramp [0, 128, 255]: mean≈127.67, above: 128, 255 → ratio = 2/3
        assert pgm_above_mean_ratio(_PGM_RAMP) == pytest.approx(2/3, rel=1e-3)


class TestPgmMaxval:
    def test_returns_int(self):
        assert isinstance(pgm_maxval(_PGM_WHITE), int)

    def test_white_maxval_255(self):
        assert pgm_maxval(_PGM_WHITE) == 255

    def test_ramp_maxval_255(self):
        assert pgm_maxval(_PGM_RAMP) == 255

    def test_positive(self):
        assert pgm_maxval(_PGM_WHITE) > 0


class TestPgmMidpointGray:
    def test_returns_int(self):
        assert isinstance(pgm_midpoint_gray(_PGM_WHITE), int)

    def test_white_midpoint_127(self):
        # midpoint = maxval // 2 = 127
        assert pgm_midpoint_gray(_PGM_WHITE) == 127

    def test_ramp_midpoint_127(self):
        assert pgm_midpoint_gray(_PGM_RAMP) == 127

    def test_nonnegative(self):
        assert pgm_midpoint_gray(_PGM_WHITE) >= 0


class TestPgmMedianBrightness:
    def test_returns_float(self):
        assert isinstance(pgm_median_brightness(_PGM_WHITE), float)

    def test_white_median_255(self):
        assert pgm_median_brightness(_PGM_WHITE) == pytest.approx(255.0)

    def test_ramp_median(self):
        # 3x1-ramp: [0, 128, 255] → median = 128.0
        assert pgm_median_brightness(_PGM_RAMP) == pytest.approx(128.0)

    def test_nonnegative(self):
        assert pgm_median_brightness(_PGM_GRAD) >= 0.0


class TestPgmPixelValueRange:
    def test_returns_int(self):
        assert isinstance(pgm_pixel_value_range(_PGM_WHITE), int)

    def test_white_zero_range(self):
        # 1x1-white: only one pixel value → range = 0
        assert pgm_pixel_value_range(_PGM_WHITE) == 0

    def test_ramp_full_range(self):
        # 3x1-ramp: [0, 128, 255] → range = 255
        assert pgm_pixel_value_range(_PGM_RAMP) == 255

    def test_nonnegative(self):
        assert pgm_pixel_value_range(_PGM_GRAD) >= 0
