"""
r322 PBM analytics: pbm_total_pixels_minus_black, pbm_white_count_exceeds_row_count.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_total_pixels_minus_black, pbm_white_count_exceeds_row_count

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


# --- pbm_total_pixels_minus_black ---

def test_total_pixels_minus_black_1x1():
    assert pbm_total_pixels_minus_black(_PBM / "1x1-black.pbm") == 0

def test_total_pixels_minus_black_2x2():
    assert pbm_total_pixels_minus_black(_PBM / "2x2-checker.pbm") == 2

def test_total_pixels_minus_black_3x2():
    assert pbm_total_pixels_minus_black(_PBM / "3x2-pattern.pbm") == 3

def test_total_pixels_minus_black_returns_int():
    result = pbm_total_pixels_minus_black(_PBM / "1x1-black.pbm")
    assert isinstance(result, int)

def test_total_pixels_minus_black_nonnegative():
    for f in ["1x1-black.pbm", "2x2-checker.pbm", "3x2-pattern.pbm"]:
        assert pbm_total_pixels_minus_black(_PBM / f) >= 0

def test_total_pixels_minus_black_all_distinct():
    results = [
        pbm_total_pixels_minus_black(_PBM / "1x1-black.pbm"),
        pbm_total_pixels_minus_black(_PBM / "2x2-checker.pbm"),
        pbm_total_pixels_minus_black(_PBM / "3x2-pattern.pbm"),
    ]
    assert len(set(results)) == 3


# --- pbm_white_count_exceeds_row_count ---

def test_white_exceeds_row_1x1_false():
    assert pbm_white_count_exceeds_row_count(_PBM / "1x1-black.pbm") is False

def test_white_exceeds_row_2x2_false():
    assert pbm_white_count_exceeds_row_count(_PBM / "2x2-checker.pbm") is False

def test_white_exceeds_row_3x2_true():
    assert pbm_white_count_exceeds_row_count(_PBM / "3x2-pattern.pbm") is True

def test_white_exceeds_row_returns_bool():
    result = pbm_white_count_exceeds_row_count(_PBM / "1x1-black.pbm")
    assert isinstance(result, bool)

def test_white_exceeds_row_2x2_is_bool():
    result = pbm_white_count_exceeds_row_count(_PBM / "2x2-checker.pbm")
    assert isinstance(result, bool)

def test_white_exceeds_row_only_3x2_true():
    results = [
        pbm_white_count_exceeds_row_count(_PBM / "1x1-black.pbm"),
        pbm_white_count_exceeds_row_count(_PBM / "2x2-checker.pbm"),
        pbm_white_count_exceeds_row_count(_PBM / "3x2-pattern.pbm"),
    ]
    assert results.count(True) == 1
