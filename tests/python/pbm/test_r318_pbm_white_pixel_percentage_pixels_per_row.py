"""Tests for pbm_white_pixel_percentage and pbm_pixels_per_row (Sprint 108, R318)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_white_pixel_percentage, pbm_pixels_per_row

PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


def test_white_pct_black():
    assert abs(pbm_white_pixel_percentage(PBM / "1x1-black.pbm") - 0.0) < 0.1


def test_white_pct_checker():
    assert abs(pbm_white_pixel_percentage(PBM / "2x2-checker.pbm") - 50.0) < 0.1


def test_white_pct_pattern():
    assert abs(pbm_white_pixel_percentage(PBM / "3x2-pattern.pbm") - 50.0) < 0.1


def test_white_pct_returns_float():
    assert isinstance(pbm_white_pixel_percentage(PBM / "1x1-black.pbm"), float)


def test_white_pct_bounded():
    pct = pbm_white_pixel_percentage(PBM / "2x2-checker.pbm")
    assert 0.0 <= pct <= 100.0


def test_ppr_1x1():
    assert abs(pbm_pixels_per_row(PBM / "1x1-black.pbm") - 1.0) < 0.01


def test_ppr_2x2():
    assert abs(pbm_pixels_per_row(PBM / "2x2-checker.pbm") - 2.0) < 0.01


def test_ppr_3x2():
    assert abs(pbm_pixels_per_row(PBM / "3x2-pattern.pbm") - 3.0) < 0.01


def test_ppr_returns_float():
    assert isinstance(pbm_pixels_per_row(PBM / "1x1-black.pbm"), float)


def test_ppr_positive():
    assert pbm_pixels_per_row(PBM / "2x2-checker.pbm") > 0.0
