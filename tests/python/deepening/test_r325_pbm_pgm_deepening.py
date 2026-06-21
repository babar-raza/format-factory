"""Tests for pbm_black_pixel_percentage, pbm_aspect_ratio,
pgm_dark_pixel_percentage, pgm_aspect_ratio (Sprint 115, R325).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_black_pixel_percentage, pbm_aspect_ratio
from src.python.pgm.pgm_parser import pgm_dark_pixel_percentage, pgm_aspect_ratio

PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"
PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


def test_pbm_black_pct_1x1():
    assert abs(pbm_black_pixel_percentage(PBM / "1x1-black.pbm") - 100.0) < 0.1


def test_pbm_black_pct_checker():
    assert abs(pbm_black_pixel_percentage(PBM / "2x2-checker.pbm") - 50.0) < 0.1


def test_pbm_black_pct_pattern():
    assert abs(pbm_black_pixel_percentage(PBM / "3x2-pattern.pbm") - 50.0) < 0.1


def test_pbm_black_pct_returns_float():
    assert isinstance(pbm_black_pixel_percentage(PBM / "1x1-black.pbm"), float)


def test_pbm_black_pct_bounded():
    val = pbm_black_pixel_percentage(PBM / "1x1-black.pbm")
    assert 0.0 <= val <= 100.0


def test_pbm_aspect_1x1():
    assert abs(pbm_aspect_ratio(PBM / "1x1-black.pbm") - 1.0) < 0.01


def test_pbm_aspect_2x2():
    assert abs(pbm_aspect_ratio(PBM / "2x2-checker.pbm") - 1.0) < 0.01


def test_pbm_aspect_3x2():
    assert abs(pbm_aspect_ratio(PBM / "3x2-pattern.pbm") - 1.5) < 0.01


def test_pbm_aspect_returns_float():
    assert isinstance(pbm_aspect_ratio(PBM / "1x1-black.pbm"), float)


def test_pbm_aspect_positive():
    assert pbm_aspect_ratio(PBM / "1x1-black.pbm") > 0.0


def test_pgm_dark_pct_white():
    assert abs(pgm_dark_pixel_percentage(PGM / "1x1-white.pgm") - 0.0) < 0.1


def test_pgm_dark_pct_gradient():
    assert abs(pgm_dark_pixel_percentage(PGM / "2x2-gradient.pgm") - 50.0) < 0.1


def test_pgm_dark_pct_ramp():
    assert abs(pgm_dark_pixel_percentage(PGM / "3x1-ramp.pgm") - 33.33) < 0.1


def test_pgm_dark_pct_returns_float():
    assert isinstance(pgm_dark_pixel_percentage(PGM / "1x1-white.pgm"), float)


def test_pgm_dark_pct_bounded():
    val = pgm_dark_pixel_percentage(PGM / "1x1-white.pgm")
    assert 0.0 <= val <= 100.0


def test_pgm_aspect_1x1():
    assert abs(pgm_aspect_ratio(PGM / "1x1-white.pgm") - 1.0) < 0.01


def test_pgm_aspect_2x2():
    assert abs(pgm_aspect_ratio(PGM / "2x2-gradient.pgm") - 1.0) < 0.01


def test_pgm_aspect_3x1():
    assert abs(pgm_aspect_ratio(PGM / "3x1-ramp.pgm") - 3.0) < 0.01


def test_pgm_aspect_returns_float():
    assert isinstance(pgm_aspect_ratio(PGM / "1x1-white.pgm"), float)


def test_pgm_aspect_positive():
    assert pgm_aspect_ratio(PGM / "1x1-white.pgm") > 0.0
