"""
Sprint r340: FODG analytics — fodg_shape_count_times_three, fodg_has_no_shapes
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_times_three,
    fodg_has_no_shapes,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"        # shapes=0
_MINIMAL = _FODG / "minimal-drawing.fodg"  # shapes=1
_SHAPES = _FODG / "shapes-basic.fodg"      # shapes=3


# --- fodg_shape_count_times_three ---

def test_shape_times_three_empty():
    assert fodg_shape_count_times_three(_EMPTY) == 0


def test_shape_times_three_minimal():
    assert fodg_shape_count_times_three(_MINIMAL) == 3


def test_shape_times_three_shapes():
    assert fodg_shape_count_times_three(_SHAPES) == 9


def test_shape_times_three_returns_int():
    assert isinstance(fodg_shape_count_times_three(_EMPTY), int)


def test_shape_times_three_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_shape_count_times_three(p) >= 0


def test_shape_times_three_all_distinct():
    vals = [fodg_shape_count_times_three(p) for p in (_EMPTY, _MINIMAL, _SHAPES)]
    assert len(set(vals)) == 3


# --- fodg_has_no_shapes ---

def test_has_no_shapes_empty():
    assert fodg_has_no_shapes(_EMPTY) is True


def test_has_no_shapes_minimal():
    assert fodg_has_no_shapes(_MINIMAL) is False


def test_has_no_shapes_shapes():
    assert fodg_has_no_shapes(_SHAPES) is False


def test_has_no_shapes_returns_bool():
    assert isinstance(fodg_has_no_shapes(_EMPTY), bool)


def test_has_no_shapes_true_case():
    assert fodg_has_no_shapes(_EMPTY) is True


def test_has_no_shapes_false_case():
    assert fodg_has_no_shapes(_MINIMAL) is False
