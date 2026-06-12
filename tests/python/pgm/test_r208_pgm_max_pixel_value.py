"""
Tests for pgm_max_pixel_value — sprint product-deepening-rnext77.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PGM_SAMPLES = REPO / "samples" / "by-format" / "pgm" / "valid"

sys.path.insert(0, str(REPO / "src" / "python"))

from pgm.pgm_parser import pgm_max_pixel_value


def test_import():
    assert callable(pgm_max_pixel_value)


def test_white_pixel_has_max_255():
    result = pgm_max_pixel_value(PGM_SAMPLES / "1x1-white.pgm")
    assert result == 255


def test_gradient_max_is_255():
    result = pgm_max_pixel_value(PGM_SAMPLES / "2x2-gradient.pgm")
    assert result == 255


def test_ramp_max_is_255():
    result = pgm_max_pixel_value(PGM_SAMPLES / "3x1-ramp.pgm")
    assert result == 255


def test_returns_int():
    result = pgm_max_pixel_value(PGM_SAMPLES / "1x1-white.pgm")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = pgm_max_pixel_value(PGM_SAMPLES / "2x2-gradient.pgm")
    assert result >= 0
