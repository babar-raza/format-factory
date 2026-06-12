"""Tests for pgm_min_pixel_value().

Sprint: product-deepening-rnext81
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_min_pixel_value

PGM_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPgmMinPixelValue:
    def test_import(self):
        assert callable(pgm_min_pixel_value)

    def test_white_image_min_is_255(self):
        result = pgm_min_pixel_value(PGM_SAMPLES / "1x1-white.pgm")
        assert result == 255

    def test_gradient_min_is_zero(self):
        result = pgm_min_pixel_value(PGM_SAMPLES / "2x2-gradient.pgm")
        assert result == 0

    def test_ramp_min_is_zero(self):
        result = pgm_min_pixel_value(PGM_SAMPLES / "3x1-ramp.pgm")
        assert result == 0

    def test_returns_int(self):
        result = pgm_min_pixel_value(PGM_SAMPLES / "1x1-white.pgm")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in PGM_SAMPLES.iterdir():
            if sample.suffix == ".pgm":
                assert pgm_min_pixel_value(sample) >= 0
