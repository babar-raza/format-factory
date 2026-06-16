"""
Tests for PGM analytics gap closure (3 FOSS gaps).
Closes: GAP-PGM-FOSS-PGM_IS_HIGH-001, GAP-PGM-FOSS-PGM_AVG_RO-001,
        GAP-PGM-FOSS-PGM_IS_BRIG-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_is_high_contrast,
    pgm_avg_row_brightness,
    pgm_is_bright,
)

_PGM_1x1 = _REPO / "samples/by-format/pgm/valid/1x1-white.pgm"
_PGM_2x2 = _REPO / "samples/by-format/pgm/valid/2x2-gradient.pgm"
_PGM_RAMP = _REPO / "samples/by-format/pgm/valid/3x1-ramp.pgm"


class TestPgmIsHighContrast:
    def test_returns_bool(self):
        assert isinstance(pgm_is_high_contrast(_PGM_1x1), bool)

    def test_single_pixel_not_high_contrast(self):
        # 1x1-white: lo=255, hi=255 → range 0 → not > maxval*0.5 → False
        assert pgm_is_high_contrast(_PGM_1x1) is False

    def test_ramp_is_high_contrast(self):
        # 3x1-ramp: pixels=[0,128,255] → range=255 > 255*0.5=127.5 → True
        assert pgm_is_high_contrast(_PGM_RAMP) is True

    def test_gradient_result_is_bool(self):
        # 2x2-gradient: pixels=[0,85,170,255] → range=255 > 127.5 → True
        assert pgm_is_high_contrast(_PGM_2x2) is True


class TestPgmAvgRowBrightness:
    def test_returns_list(self):
        result = pgm_avg_row_brightness(_PGM_2x2)
        assert isinstance(result, list)

    def test_list_length_equals_height(self):
        # 2x2-gradient.pgm has height=2 → exactly 2 row averages
        result = pgm_avg_row_brightness(_PGM_2x2)
        assert len(result) == 2

    def test_single_row_for_3x1(self):
        # 3x1-ramp.pgm has height=1 → exactly 1 row average
        result = pgm_avg_row_brightness(_PGM_RAMP)
        assert len(result) == 1

    def test_values_are_floats(self):
        result = pgm_avg_row_brightness(_PGM_RAMP)
        for v in result:
            assert isinstance(v, float)

    def test_ramp_avg_row_value(self):
        # 3x1-ramp: pixels=[0,128,255] → avg = (0+128+255)/3 ≈ 127.67
        result = pgm_avg_row_brightness(_PGM_RAMP)
        assert result == pytest.approx([127.6666666], abs=0.01)

    def test_white_pixel_row_brightness_is_255(self):
        # 1x1-white: single pixel=255 → avg row = [255.0]
        result = pgm_avg_row_brightness(_PGM_1x1)
        assert len(result) == 1
        assert result[0] == pytest.approx(255.0)


class TestPgmIsBright:
    def test_returns_bool(self):
        assert isinstance(pgm_is_bright(_PGM_1x1), bool)

    def test_white_pixel_is_bright(self):
        # 1x1-white: mean=255 > 200 → True
        assert pgm_is_bright(_PGM_1x1) is True

    def test_ramp_is_not_bright(self):
        # 3x1-ramp: mean=(0+128+255)/3 ≈ 127.67 ≤ 200 → False
        assert pgm_is_bright(_PGM_RAMP) is False

    def test_consistent_result(self):
        r1 = pgm_is_bright(_PGM_2x2)
        r2 = pgm_is_bright(_PGM_2x2)
        assert r1 == r2
