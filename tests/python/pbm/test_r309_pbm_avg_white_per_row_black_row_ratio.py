"""Tests for pbm_avg_white_per_row and pbm_black_row_ratio (Sprint 99, R309)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_avg_white_per_row, pbm_black_row_ratio

PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


def test_avg_white_per_row_black():
    assert abs(pbm_avg_white_per_row(PBM / "1x1-black.pbm") - 0.0) < 0.01


def test_avg_white_per_row_checker():
    assert abs(pbm_avg_white_per_row(PBM / "2x2-checker.pbm") - 1.0) < 0.01


def test_avg_white_per_row_pattern():
    assert abs(pbm_avg_white_per_row(PBM / "3x2-pattern.pbm") - 1.5) < 0.01


def test_avg_white_per_row_returns_float():
    assert isinstance(pbm_avg_white_per_row(PBM / "1x1-black.pbm"), float)


def test_avg_white_per_row_nonnegative():
    assert pbm_avg_white_per_row(PBM / "1x1-black.pbm") >= 0.0


def test_black_row_ratio_black():
    assert abs(pbm_black_row_ratio(PBM / "1x1-black.pbm") - 1.0) < 0.01


def test_black_row_ratio_checker():
    assert abs(pbm_black_row_ratio(PBM / "2x2-checker.pbm") - 0.0) < 0.01


def test_black_row_ratio_pattern():
    assert abs(pbm_black_row_ratio(PBM / "3x2-pattern.pbm") - 0.0) < 0.01


def test_black_row_ratio_returns_float():
    assert isinstance(pbm_black_row_ratio(PBM / "1x1-black.pbm"), float)


def test_black_row_ratio_between_zero_and_one():
    val = pbm_black_row_ratio(PBM / "1x1-black.pbm")
    assert 0.0 <= val <= 1.0
