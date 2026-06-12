"""
Tests for pgm_dark_pixel_count — sprint product-deepening-rnext68.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PGM_SAMPLES = REPO / "samples" / "by-format" / "pgm" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from pgm.pgm_parser import pgm_dark_pixel_count


def test_import():
    assert callable(pgm_dark_pixel_count)


def test_white_image_has_no_dark_pixels():
    result = pgm_dark_pixel_count(PGM_SAMPLES / "1x1-white.pgm")
    assert result == 0


def test_gradient_has_one_dark_pixel():
    result = pgm_dark_pixel_count(PGM_SAMPLES / "2x2-gradient.pgm")
    assert result == 1


def test_ramp_has_one_dark_pixel():
    result = pgm_dark_pixel_count(PGM_SAMPLES / "3x1-ramp.pgm")
    assert result == 1


def test_returns_int():
    result = pgm_dark_pixel_count(PGM_SAMPLES / "1x1-white.pgm")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = pgm_dark_pixel_count(PGM_SAMPLES / "2x2-gradient.pgm")
    assert result >= 0
