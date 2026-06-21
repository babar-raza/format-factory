"""
Tests for PGM gap closure (2 FOSS functions).
Closes: GAP-PGM-FOSS-PGM_ENTROPY-001, GAP-PGM-FOSS-PGM_MODE_PIX-001

Known sample values:
  1x1-white.pgm: entropy=0.0, mode_pixel=255
  2x2-gradient.pgm: entropy=2.0, mode_pixel=0
  3x1-ramp.pgm: entropy≈1.585, mode_pixel=0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import pgm_entropy, pgm_mode_pixel_value

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = _PGM / "1x1-white.pgm"
_GRADIENT = _PGM / "2x2-gradient.pgm"
_RAMP = _PGM / "3x1-ramp.pgm"


class TestPgmEntropy:
    def test_returns_float(self):
        assert isinstance(pgm_entropy(_WHITE), float)

    def test_nonnegative(self):
        for p in [_WHITE, _GRADIENT, _RAMP]:
            assert pgm_entropy(p) >= 0.0

    def test_uniform_image_entropy_zero(self):
        # 1x1-white: single pixel → no variation → entropy=0.0
        assert pgm_entropy(_WHITE) == 0.0

    def test_gradient_entropy_approx(self):
        # 2x2-gradient: 4 unique values → entropy=2.0
        assert abs(pgm_entropy(_GRADIENT) - 2.0) < 0.01

    def test_ramp_entropy_approx(self):
        # 3x1-ramp: 3 unique values → entropy≈1.585
        assert abs(pgm_entropy(_RAMP) - 1.585) < 0.01

    def test_gradient_higher_entropy_than_white(self):
        assert pgm_entropy(_GRADIENT) > pgm_entropy(_WHITE)

    def test_all_return_float(self):
        for p in [_WHITE, _GRADIENT, _RAMP]:
            assert isinstance(pgm_entropy(p), float)

    def test_ramp_higher_entropy_than_white(self):
        assert pgm_entropy(_RAMP) > pgm_entropy(_WHITE)


class TestPgmModePixelValue:
    def test_returns_int(self):
        assert isinstance(pgm_mode_pixel_value(_WHITE), int)

    def test_bounded(self):
        for p in [_WHITE, _GRADIENT, _RAMP]:
            v = pgm_mode_pixel_value(p)
            assert 0 <= v <= 255

    def test_white_mode_is_255(self):
        assert pgm_mode_pixel_value(_WHITE) == 255

    def test_gradient_mode_is_zero(self):
        # all 4 values unique — mode picks smallest (0)
        assert pgm_mode_pixel_value(_GRADIENT) == 0

    def test_ramp_mode_is_zero(self):
        # ramp starts at 0 — mode is 0
        assert pgm_mode_pixel_value(_RAMP) == 0

    def test_all_return_int(self):
        for p in [_WHITE, _GRADIENT, _RAMP]:
            assert isinstance(pgm_mode_pixel_value(p), int)
