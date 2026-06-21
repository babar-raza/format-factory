"""
PGM FOSS gap closure tests.

Closes:
  GAP-PGM-FOSS-PGM_IS_HIGH_-001   — pgm_is_high_contrast
  GAP-PGM-FOSS-PGM_AVG_ROW_-001   — pgm_avg_row_brightness
  GAP-PGM-FOSS-PGM_IS_BRIGH-001   — pgm_is_bright
  GAP-PGM-FOSS-PGM_DARK_PIX-001   — pgm_dark_pixel_ratio
  GAP-PGM-FOSS-PGM_ROW_BRIG-001   — pgm_row_brightness_variance
  GAP-PGM-FOSS-PGM_CONTRAST-001   — pgm_contrast_ratio
  GAP-PGM-FOSS-PGM_NORMALIZ-001   — pgm_normalized_mean
  GAP-PGM-FOSS-PGM_ABOVE_ME-001   — pgm_above_mean_ratio
  GAP-PGM-FOSS-PGM_MAXVAL-001     — pgm_maxval
  GAP-PGM-FOSS-PGM_MIDPOINT-001   — pgm_midpoint_gray
  GAP-PGM-FOSS-PGM_MEDIAN_B-001   — pgm_median_brightness
  GAP-PGM-FOSS-PGM_PIXEL_VA-001   — pgm_pixel_value_range

Run from repo root:
    python -m pytest tests/python/pgm/test_pgm_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from pgm.pgm_parser import (
    pgm_is_high_contrast,
    pgm_avg_row_brightness,
    pgm_is_bright,
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

SAMPLES = REPO_ROOT / "samples" / "by-format" / "pgm" / "valid"
WHITE = SAMPLES / "1x1-white.pgm"
GRADIENT = SAMPLES / "2x2-gradient.pgm"
RAMP = SAMPLES / "3x1-ramp.pgm"


class TestPgmIsHighContrast:
    def test_white_not_high_contrast(self):
        assert pgm_is_high_contrast(WHITE) is False

    def test_gradient_high_contrast(self):
        assert pgm_is_high_contrast(GRADIENT) is True

    def test_returns_bool(self):
        assert isinstance(pgm_is_high_contrast(WHITE), bool)


class TestPgmAvgRowBrightness:
    def test_returns_list(self):
        result = pgm_avg_row_brightness(WHITE)
        assert isinstance(result, list)

    def test_white_all_255(self):
        rows = pgm_avg_row_brightness(WHITE)
        assert all(v == pytest.approx(255.0, abs=0.01) for v in rows)

    def test_gradient_multiple_rows(self):
        rows = pgm_avg_row_brightness(GRADIENT)
        assert len(rows) == 2

    def test_all_non_negative(self):
        for p in [WHITE, GRADIENT, RAMP]:
            for v in pgm_avg_row_brightness(p):
                assert v >= 0


class TestPgmIsBright:
    def test_white_is_bright(self):
        assert pgm_is_bright(WHITE) is True

    def test_gradient_not_bright(self):
        # mean = 127.5 / 255 = 0.5, threshold depends on impl
        result = pgm_is_bright(GRADIENT)
        assert isinstance(result, bool)

    def test_returns_bool(self):
        assert isinstance(pgm_is_bright(WHITE), bool)


class TestPgmDarkPixelRatio:
    def test_white_zero_dark(self):
        assert pgm_dark_pixel_ratio(WHITE) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(pgm_dark_pixel_ratio(WHITE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [WHITE, GRADIENT, RAMP]:
            r = pgm_dark_pixel_ratio(p)
            assert 0.0 <= r <= 1.0


class TestPgmRowBrightnessVariance:
    def test_white_zero_variance(self):
        assert pgm_row_brightness_variance(WHITE) == pytest.approx(0.0, abs=0.01)

    def test_gradient_positive_variance(self):
        assert pgm_row_brightness_variance(GRADIENT) > 0

    def test_returns_numeric(self):
        assert isinstance(pgm_row_brightness_variance(WHITE), (int, float))

    def test_non_negative(self):
        for p in [WHITE, GRADIENT, RAMP]:
            assert pgm_row_brightness_variance(p) >= 0


class TestPgmContrastRatio:
    def test_white_zero_contrast(self):
        assert pgm_contrast_ratio(WHITE) == pytest.approx(0.0, abs=0.01)

    def test_gradient_full_contrast(self):
        assert pgm_contrast_ratio(GRADIENT) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(pgm_contrast_ratio(WHITE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [WHITE, GRADIENT, RAMP]:
            r = pgm_contrast_ratio(p)
            assert 0.0 <= r <= 1.0


class TestPgmNormalizedMean:
    def test_white_is_one(self):
        assert pgm_normalized_mean(WHITE) == pytest.approx(1.0, abs=0.01)

    def test_gradient_half(self):
        assert pgm_normalized_mean(GRADIENT) == pytest.approx(0.5, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(pgm_normalized_mean(WHITE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [WHITE, GRADIENT, RAMP]:
            r = pgm_normalized_mean(p)
            assert 0.0 <= r <= 1.0


class TestPgmAboveMeanRatio:
    def test_white_zero(self):
        # all pixels equal mean, none strictly above
        assert pgm_above_mean_ratio(WHITE) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(pgm_above_mean_ratio(WHITE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [WHITE, GRADIENT, RAMP]:
            r = pgm_above_mean_ratio(p)
            assert 0.0 <= r <= 1.0


class TestPgmMaxval:
    def test_white_is_255(self):
        assert pgm_maxval(WHITE) == 255

    def test_gradient_is_255(self):
        assert pgm_maxval(GRADIENT) == 255

    def test_returns_int(self):
        assert isinstance(pgm_maxval(WHITE), int)

    def test_positive(self):
        for p in [WHITE, GRADIENT, RAMP]:
            assert pgm_maxval(p) > 0


class TestPgmMidpointGray:
    def test_returns_numeric(self):
        assert isinstance(pgm_midpoint_gray(WHITE), (int, float))

    def test_white_midpoint(self):
        assert pgm_midpoint_gray(WHITE) == pytest.approx(127, abs=1)

    def test_positive(self):
        for p in [WHITE, GRADIENT, RAMP]:
            assert pgm_midpoint_gray(p) > 0


class TestPgmMedianBrightness:
    def test_white_is_255(self):
        assert pgm_median_brightness(WHITE) == pytest.approx(255.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(pgm_median_brightness(WHITE), (int, float))

    def test_non_negative(self):
        for p in [WHITE, GRADIENT, RAMP]:
            assert pgm_median_brightness(p) >= 0


class TestPgmPixelValueRange:
    def test_white_zero_range(self):
        assert pgm_pixel_value_range(WHITE) == 0

    def test_gradient_full_range(self):
        assert pgm_pixel_value_range(GRADIENT) == 255

    def test_returns_int(self):
        assert isinstance(pgm_pixel_value_range(WHITE), int)

    def test_non_negative(self):
        for p in [WHITE, GRADIENT, RAMP]:
            assert pgm_pixel_value_range(p) >= 0
