"""
Tests for pgm_average_brightness — sprint product-deepening-rnext71.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PGM_SAMPLES = REPO / "samples" / "by-format" / "pgm" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from pgm.pgm_parser import pgm_average_brightness


def test_import():
    assert callable(pgm_average_brightness)


def test_white_image_is_255():
    result = pgm_average_brightness(PGM_SAMPLES / "1x1-white.pgm")
    assert result == 255.0


def test_gradient_is_127_5():
    result = pgm_average_brightness(PGM_SAMPLES / "2x2-gradient.pgm")
    assert result == 127.5


def test_ramp_is_approx_127_67():
    result = pgm_average_brightness(PGM_SAMPLES / "3x1-ramp.pgm")
    assert abs(result - 127.6667) < 0.001


def test_returns_float():
    result = pgm_average_brightness(PGM_SAMPLES / "1x1-white.pgm")
    assert isinstance(result, float)


def test_result_nonnegative():
    result = pgm_average_brightness(PGM_SAMPLES / "2x2-gradient.pgm")
    assert result >= 0.0
