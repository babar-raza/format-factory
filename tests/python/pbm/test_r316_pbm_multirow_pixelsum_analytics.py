"""
Tests for Sprint r316: pbm_is_multi_row, pbm_pixel_sum.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_is_multi_row, pbm_pixel_sum

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"


# --- pbm_is_multi_row ---

def test_pbm_is_multi_row_1x1_false():
    assert pbm_is_multi_row(_PBM / "1x1-black.pbm") is False


def test_pbm_is_multi_row_2x2_true():
    assert pbm_is_multi_row(_PBM / "2x2-checker.pbm") is True


def test_pbm_is_multi_row_3x2_true():
    assert pbm_is_multi_row(_PBM / "3x2-pattern.pbm") is True


def test_pbm_is_multi_row_returns_bool_1x1():
    assert isinstance(pbm_is_multi_row(_PBM / "1x1-black.pbm"), bool)


def test_pbm_is_multi_row_returns_bool_2x2():
    assert isinstance(pbm_is_multi_row(_PBM / "2x2-checker.pbm"), bool)


def test_pbm_is_multi_row_all_three():
    results = [
        pbm_is_multi_row(_PBM / "1x1-black.pbm"),
        pbm_is_multi_row(_PBM / "2x2-checker.pbm"),
        pbm_is_multi_row(_PBM / "3x2-pattern.pbm"),
    ]
    assert results == [False, True, True]


# --- pbm_pixel_sum ---

def test_pbm_pixel_sum_1x1_one():
    # 1x1 all-black: pixel=[1] → sum=1
    assert pbm_pixel_sum(_PBM / "1x1-black.pbm") == 1


def test_pbm_pixel_sum_2x2_two():
    # 2x2 checker: [1,0,0,1] → sum=2
    assert pbm_pixel_sum(_PBM / "2x2-checker.pbm") == 2


def test_pbm_pixel_sum_3x2_three():
    # 3x2 pattern: [1,0,1,0,1,0] → sum=3
    assert pbm_pixel_sum(_PBM / "3x2-pattern.pbm") == 3


def test_pbm_pixel_sum_returns_int_1x1():
    assert isinstance(pbm_pixel_sum(_PBM / "1x1-black.pbm"), int)


def test_pbm_pixel_sum_returns_int_2x2():
    assert isinstance(pbm_pixel_sum(_PBM / "2x2-checker.pbm"), int)


def test_pbm_pixel_sum_all_three_distinct():
    results = [
        pbm_pixel_sum(_PBM / "1x1-black.pbm"),
        pbm_pixel_sum(_PBM / "2x2-checker.pbm"),
        pbm_pixel_sum(_PBM / "3x2-pattern.pbm"),
    ]
    assert results == [1, 2, 3]
