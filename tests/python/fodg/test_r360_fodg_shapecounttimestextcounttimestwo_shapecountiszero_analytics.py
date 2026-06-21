"""Tests for fodg_shape_count_times_text_count_times_two and fodg_shape_count_is_zero (r360)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_times_text_count_times_two,
    fodg_shape_count_is_zero,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_shape_count_times_text_count_times_two
# empty-page:      shapes=0, text=0 => 0*0*2 = 0
# minimal-drawing: shapes=1, text=1 => 1*1*2 = 2
# shapes-basic:    shapes=3, text=2 => 3*2*2 = 12

def test_shape_times_text_times_two_empty():
    assert fodg_shape_count_times_text_count_times_two(_EMPTY) == 0


def test_shape_times_text_times_two_minimal():
    assert fodg_shape_count_times_text_count_times_two(_MINIMAL) == 2


def test_shape_times_text_times_two_shapes():
    assert fodg_shape_count_times_text_count_times_two(_SHAPES) == 12


def test_shape_times_text_times_two_empty_is_int():
    assert isinstance(fodg_shape_count_times_text_count_times_two(_EMPTY), int)


def test_shape_times_text_times_two_minimal_is_int():
    assert isinstance(fodg_shape_count_times_text_count_times_two(_MINIMAL), int)


def test_shape_times_text_times_two_distinct():
    v1 = fodg_shape_count_times_text_count_times_two(_EMPTY)
    v2 = fodg_shape_count_times_text_count_times_two(_MINIMAL)
    v3 = fodg_shape_count_times_text_count_times_two(_SHAPES)
    assert len({v1, v2, v3}) == 3


# fodg_shape_count_is_zero
# empty-page:      True  (shapes=0)
# minimal-drawing: False (shapes=1)
# shapes-basic:    False (shapes=3)

def test_shape_count_is_zero_empty_is_true():
    assert fodg_shape_count_is_zero(_EMPTY) is True


def test_shape_count_is_zero_minimal_is_false():
    assert fodg_shape_count_is_zero(_MINIMAL) is False


def test_shape_count_is_zero_shapes_is_false():
    assert fodg_shape_count_is_zero(_SHAPES) is False


def test_shape_count_is_zero_empty_is_bool():
    assert isinstance(fodg_shape_count_is_zero(_EMPTY), bool)


def test_shape_count_is_zero_minimal_is_bool():
    assert isinstance(fodg_shape_count_is_zero(_MINIMAL), bool)


def test_shape_count_is_zero_both_true_and_false():
    results = [
        fodg_shape_count_is_zero(_EMPTY),
        fodg_shape_count_is_zero(_MINIMAL),
        fodg_shape_count_is_zero(_SHAPES),
    ]
    assert True in results and False in results
