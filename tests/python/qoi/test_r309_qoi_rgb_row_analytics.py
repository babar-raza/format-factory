"""
Sprint r309: Tests for qoi_avg_rgb_per_pixel and qoi_is_multi_row.
12 tests total (6 per function).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_avg_rgb_per_pixel, qoi_is_multi_row

_Q = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = _Q / "1x1-red.qoi"
_BLACK = _Q / "2x2-black.qoi"
_GRADIENT = _Q / "4x1-gradient.qoi"


# --- qoi_avg_rgb_per_pixel ---

def test_avg_rgb_per_pixel_red_returns_float():
    assert isinstance(qoi_avg_rgb_per_pixel(_RED), float)

def test_avg_rgb_per_pixel_red_is_255():
    # 1x1-red: R=255,G=0,B=0 → sum=255, pixels=1 → 255.0
    assert qoi_avg_rgb_per_pixel(_RED) == 255.0

def test_avg_rgb_per_pixel_black_is_0():
    # 2x2-black: all zeros → 0.0
    assert qoi_avg_rgb_per_pixel(_BLACK) == 0.0

def test_avg_rgb_per_pixel_gradient_is_382_5():
    # 4x1-gradient: sum=1530, 4 pixels → 382.5
    assert qoi_avg_rgb_per_pixel(_GRADIENT) == 382.5

def test_avg_rgb_per_pixel_all_distinct():
    vals = [qoi_avg_rgb_per_pixel(p) for p in [_RED, _BLACK, _GRADIENT]]
    assert len(set(vals)) == 3

def test_avg_rgb_per_pixel_red_less_than_gradient():
    assert qoi_avg_rgb_per_pixel(_RED) < qoi_avg_rgb_per_pixel(_GRADIENT)


# --- qoi_is_multi_row ---

def test_is_multi_row_red_returns_bool():
    assert isinstance(qoi_is_multi_row(_RED), bool)

def test_is_multi_row_red_is_false():
    # 1x1-red: height=1 → False
    assert qoi_is_multi_row(_RED) is False

def test_is_multi_row_black_is_true():
    # 2x2-black: height=2 → True
    assert qoi_is_multi_row(_BLACK) is True

def test_is_multi_row_gradient_is_false():
    # 4x1-gradient: height=1 → False
    assert qoi_is_multi_row(_GRADIENT) is False

def test_is_multi_row_only_black_is_true():
    results = [qoi_is_multi_row(p) for p in [_RED, _BLACK, _GRADIENT]]
    assert results.count(True) == 1
    assert results.count(False) == 2

def test_is_multi_row_consistent_with_avg_rgb():
    # Only black (multi-row) has avg_rgb=0.0
    assert qoi_is_multi_row(_BLACK) is True
    assert qoi_avg_rgb_per_pixel(_BLACK) == 0.0
