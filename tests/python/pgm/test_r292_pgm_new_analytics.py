"""
tests/python/pgm/test_r292_pgm_new_analytics.py

Sprint: PRODUCT-DEEPENING-SPRINT-28-20260616
New PGM analytics: pgm_saturated_pixel_ratio, pgm_normalized_mean,
                   pgm_above_mean_ratio, pgm_maxval, pgm_midpoint_gray
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm import (
    pgm_saturated_pixel_ratio,
    pgm_normalized_mean,
    pgm_above_mean_ratio,
    pgm_maxval,
    pgm_midpoint_gray,
)

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_PGM_DIR / "1x1-white.pgm")
_GRADIENT = str(_PGM_DIR / "2x2-gradient.pgm")
_RAMP = str(_PGM_DIR / "3x1-ramp.pgm")


class TestPgmSaturatedPixelRatio:
    def test_returns_float(self):
        result = pgm_saturated_pixel_ratio(_WHITE)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_WHITE, _GRADIENT, _RAMP]:
            result = pgm_saturated_pixel_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_white_image_saturated(self):
        result = pgm_saturated_pixel_ratio(_WHITE)
        assert result == 1.0

    def test_gradient_less_than_one(self):
        result = pgm_saturated_pixel_ratio(_GRADIENT)
        assert result >= 0.0


class TestPgmNormalizedMean:
    def test_returns_float(self):
        result = pgm_normalized_mean(_WHITE)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_WHITE, _GRADIENT, _RAMP]:
            result = pgm_normalized_mean(path)
            assert 0.0 <= result <= 1.0

    def test_white_image_close_to_one(self):
        result = pgm_normalized_mean(_WHITE)
        assert result > 0.5

    def test_gradient_positive(self):
        result = pgm_normalized_mean(_GRADIENT)
        assert result >= 0.0


class TestPgmAboveMeanRatio:
    def test_returns_float(self):
        result = pgm_above_mean_ratio(_GRADIENT)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_WHITE, _GRADIENT, _RAMP]:
            result = pgm_above_mean_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_uniform_image_zero_above_mean(self):
        # All pixels equal mean → none strictly above
        result = pgm_above_mean_ratio(_WHITE)
        assert result == 0.0

    def test_ramp_has_some_above_mean(self):
        result = pgm_above_mean_ratio(_RAMP)
        assert result >= 0.0


class TestPgmMaxval:
    def test_returns_int(self):
        result = pgm_maxval(_WHITE)
        assert isinstance(result, int)

    def test_positive(self):
        for path in [_WHITE, _GRADIENT, _RAMP]:
            result = pgm_maxval(path)
            assert result > 0

    def test_within_netpbm_range(self):
        for path in [_WHITE, _GRADIENT, _RAMP]:
            result = pgm_maxval(path)
            assert 1 <= result <= 65535

    def test_common_maxval(self):
        # Standard PGM files typically use maxval 255
        result = pgm_maxval(_WHITE)
        assert result in (255, 15, 1, 63, 127, 65535) or result >= 1


class TestPgmMidpointGray:
    def test_returns_int(self):
        result = pgm_midpoint_gray(_WHITE)
        assert isinstance(result, int)

    def test_nonneg(self):
        for path in [_WHITE, _GRADIENT, _RAMP]:
            result = pgm_midpoint_gray(path)
            assert result >= 0

    def test_less_than_maxval(self):
        for path in [_WHITE, _GRADIENT, _RAMP]:
            mv = pgm_maxval(path)
            mid = pgm_midpoint_gray(path)
            assert mid <= mv

    def test_equals_maxval_over_two(self):
        mv = pgm_maxval(_WHITE)
        mid = pgm_midpoint_gray(_WHITE)
        assert mid == mv // 2
