"""
Sprint r308: Tests for pbm_white_per_row and pbm_is_single_row.
12 tests total (6 per function).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_white_per_row, pbm_is_single_row

_P = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1 = _P / "1x1-black.pbm"
_2X2 = _P / "2x2-checker.pbm"
_3X2 = _P / "3x2-pattern.pbm"


# --- pbm_white_per_row ---

def test_white_per_row_1x1_returns_float():
    assert isinstance(pbm_white_per_row(_1X1), float)

def test_white_per_row_1x1_is_0():
    # 1x1-black: 0 white pixels / 1 row = 0.0
    assert pbm_white_per_row(_1X1) == 0.0

def test_white_per_row_2x2_is_1():
    # 2x2-checker: 2 white pixels / 2 rows = 1.0
    assert pbm_white_per_row(_2X2) == 1.0

def test_white_per_row_3x2_is_1_5():
    # 3x2-pattern: 3 white pixels / 2 rows = 1.5
    assert pbm_white_per_row(_3X2) == 1.5

def test_white_per_row_all_distinct():
    vals = [pbm_white_per_row(p) for p in [_1X1, _2X2, _3X2]]
    assert len(set(vals)) == 3

def test_white_per_row_3x2_is_maximum():
    assert pbm_white_per_row(_3X2) > pbm_white_per_row(_2X2)
    assert pbm_white_per_row(_2X2) > pbm_white_per_row(_1X1)


# --- pbm_is_single_row ---

def test_is_single_row_1x1_returns_bool():
    assert isinstance(pbm_is_single_row(_1X1), bool)

def test_is_single_row_1x1_is_true():
    assert pbm_is_single_row(_1X1) is True

def test_is_single_row_2x2_is_false():
    assert pbm_is_single_row(_2X2) is False

def test_is_single_row_3x2_is_false():
    assert pbm_is_single_row(_3X2) is False

def test_is_single_row_only_1x1_is_true():
    results = [pbm_is_single_row(p) for p in [_1X1, _2X2, _3X2]]
    assert results.count(True) == 1
    assert results.count(False) == 2

def test_is_single_row_consistent_with_white_per_row():
    # 1x1-black is single row and has 0 white pixels per row
    assert pbm_is_single_row(_1X1) is True
    assert pbm_white_per_row(_1X1) == 0.0
