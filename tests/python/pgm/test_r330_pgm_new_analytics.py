"""
test_r330_pgm_new_analytics.py
Sprint 66 — 5 new PGM analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import (
    pgm_max_pixel_value,
    pgm_min_pixel_value,
    pgm_aspect_ratio,
    pgm_full_white_pixel_count,
    pgm_nonzero_pixel_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_SAMPLES / "1x1-white.pgm")
_GRADIENT = str(_SAMPLES / "2x2-gradient.pgm")
_RAMP = str(_SAMPLES / "3x1-ramp.pgm")


# --- pgm_max_pixel_value ---

class TestPgmMaxPixelValue:
    def test_returns_int(self):
        assert isinstance(pgm_max_pixel_value(_GRADIENT), int)

    def test_non_negative(self):
        assert pgm_max_pixel_value(_GRADIENT) >= 0

    def test_white_max(self):
        assert pgm_max_pixel_value(_WHITE) >= 1

    def test_ramp_positive(self):
        assert pgm_max_pixel_value(_RAMP) >= 0

    def test_gradient_positive(self):
        assert pgm_max_pixel_value(_GRADIENT) >= 0


# --- pgm_min_pixel_value ---

class TestPgmMinPixelValue:
    def test_returns_int(self):
        assert isinstance(pgm_min_pixel_value(_GRADIENT), int)

    def test_non_negative(self):
        assert pgm_min_pixel_value(_GRADIENT) >= 0

    def test_white_non_negative(self):
        assert pgm_min_pixel_value(_WHITE) >= 0

    def test_ramp_non_negative(self):
        assert pgm_min_pixel_value(_RAMP) >= 0

    def test_min_le_max(self):
        assert pgm_min_pixel_value(_GRADIENT) <= pgm_max_pixel_value(_GRADIENT)


# --- pgm_aspect_ratio ---

class TestPgmAspectRatio:
    def test_returns_float(self):
        assert isinstance(pgm_aspect_ratio(_GRADIENT), float)

    def test_white_square(self):
        # 1x1 image
        assert pgm_aspect_ratio(_WHITE) == 1.0

    def test_gradient_square(self):
        # 2x2 image
        assert pgm_aspect_ratio(_GRADIENT) == 1.0

    def test_ramp_wide(self):
        # 3x1 image: width=3, height=1 => 3.0
        assert pgm_aspect_ratio(_RAMP) == 3.0

    def test_non_negative(self):
        assert pgm_aspect_ratio(_GRADIENT) >= 0.0


# --- pgm_full_white_pixel_count ---

class TestPgmFullWhitePixelCount:
    def test_returns_int(self):
        assert isinstance(pgm_full_white_pixel_count(_WHITE), int)

    def test_non_negative(self):
        assert pgm_full_white_pixel_count(_WHITE) >= 0

    def test_white_is_max(self):
        assert pgm_full_white_pixel_count(_WHITE) >= 1

    def test_gradient_non_negative(self):
        assert pgm_full_white_pixel_count(_GRADIENT) >= 0

    def test_ramp_non_negative(self):
        assert pgm_full_white_pixel_count(_RAMP) >= 0


# --- pgm_nonzero_pixel_count ---

class TestPgmNonzeroPixelCount:
    def test_returns_int(self):
        assert isinstance(pgm_nonzero_pixel_count(_WHITE), int)

    def test_non_negative(self):
        assert pgm_nonzero_pixel_count(_WHITE) >= 0

    def test_white_has_nonzero(self):
        assert pgm_nonzero_pixel_count(_WHITE) >= 1

    def test_gradient_non_negative(self):
        assert pgm_nonzero_pixel_count(_GRADIENT) >= 0

    def test_ramp_non_negative(self):
        assert pgm_nonzero_pixel_count(_RAMP) >= 0
