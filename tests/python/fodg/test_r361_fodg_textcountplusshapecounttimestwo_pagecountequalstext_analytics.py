"""Tests for fodg_text_count_plus_shape_count_times_two and fodg_page_count_equals_text_count (r361)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_text_count_plus_shape_count_times_two,
    fodg_page_count_equals_text_count,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_text_count_plus_shape_count_times_two
# empty-page:      text=0, shapes=0 => 0 + 0*2 = 0
# minimal-drawing: text=1, shapes=1 => 1 + 1*2 = 3
# shapes-basic:    text=2, shapes=3 => 2 + 3*2 = 8

def test_text_plus_shape_times_two_empty():
    assert fodg_text_count_plus_shape_count_times_two(_EMPTY) == 0


def test_text_plus_shape_times_two_minimal():
    assert fodg_text_count_plus_shape_count_times_two(_MINIMAL) == 3


def test_text_plus_shape_times_two_shapes():
    assert fodg_text_count_plus_shape_count_times_two(_SHAPES) == 8


def test_text_plus_shape_times_two_empty_is_int():
    assert isinstance(fodg_text_count_plus_shape_count_times_two(_EMPTY), int)


def test_text_plus_shape_times_two_minimal_is_int():
    assert isinstance(fodg_text_count_plus_shape_count_times_two(_MINIMAL), int)


def test_text_plus_shape_times_two_distinct():
    v1 = fodg_text_count_plus_shape_count_times_two(_EMPTY)
    v2 = fodg_text_count_plus_shape_count_times_two(_MINIMAL)
    v3 = fodg_text_count_plus_shape_count_times_two(_SHAPES)
    assert len({v1, v2, v3}) == 3


# fodg_page_count_equals_text_count
# empty-page:      page=1, text=0 => False
# minimal-drawing: page=1, text=1 => True
# shapes-basic:    page=1, text=2 => False

def test_page_count_equals_text_count_empty_is_false():
    assert fodg_page_count_equals_text_count(_EMPTY) is False


def test_page_count_equals_text_count_minimal_is_true():
    assert fodg_page_count_equals_text_count(_MINIMAL) is True


def test_page_count_equals_text_count_shapes_is_false():
    assert fodg_page_count_equals_text_count(_SHAPES) is False


def test_page_count_equals_text_count_empty_is_bool():
    assert isinstance(fodg_page_count_equals_text_count(_EMPTY), bool)


def test_page_count_equals_text_count_minimal_is_bool():
    assert isinstance(fodg_page_count_equals_text_count(_MINIMAL), bool)


def test_page_count_equals_text_count_both_true_and_false():
    results = [
        fodg_page_count_equals_text_count(_EMPTY),
        fodg_page_count_equals_text_count(_MINIMAL),
        fodg_page_count_equals_text_count(_SHAPES),
    ]
    assert True in results and False in results
