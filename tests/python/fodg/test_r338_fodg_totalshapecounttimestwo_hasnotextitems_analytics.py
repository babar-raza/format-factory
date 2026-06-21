"""
Sprint r338: FODG analytics — fodg_total_shape_count_times_two, fodg_has_no_text_items
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_total_shape_count_times_two,
    fodg_has_no_text_items,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"        # shapes=0, text_items=0
_MINIMAL = _FODG / "minimal-drawing.fodg"  # shapes=1, text_items=1
_SHAPES = _FODG / "shapes-basic.fodg"      # shapes=3, text_items=2


# --- fodg_total_shape_count_times_two ---

def test_shape_times_two_empty():
    assert fodg_total_shape_count_times_two(_EMPTY) == 0


def test_shape_times_two_minimal():
    assert fodg_total_shape_count_times_two(_MINIMAL) == 2


def test_shape_times_two_shapes():
    assert fodg_total_shape_count_times_two(_SHAPES) == 6


def test_shape_times_two_returns_int():
    assert isinstance(fodg_total_shape_count_times_two(_EMPTY), int)


def test_shape_times_two_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_total_shape_count_times_two(p) >= 0


def test_shape_times_two_all_distinct():
    vals = [fodg_total_shape_count_times_two(p) for p in (_EMPTY, _MINIMAL, _SHAPES)]
    assert len(set(vals)) == 3


# --- fodg_has_no_text_items ---

def test_no_text_empty():
    assert fodg_has_no_text_items(_EMPTY) is True


def test_no_text_minimal():
    assert fodg_has_no_text_items(_MINIMAL) is False


def test_no_text_shapes():
    assert fodg_has_no_text_items(_SHAPES) is False


def test_no_text_returns_bool():
    assert isinstance(fodg_has_no_text_items(_EMPTY), bool)


def test_no_text_true_case():
    assert fodg_has_no_text_items(_EMPTY) is True


def test_no_text_false_case():
    assert fodg_has_no_text_items(_MINIMAL) is False
