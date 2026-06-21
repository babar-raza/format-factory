"""Tests for fodg_page_count_plus_shape_count_times_three and fodg_shape_count_is_one (r364)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_page_count_plus_shape_count_times_three,
    fodg_shape_count_is_one,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_page_count_plus_shape_count_times_three
# empty-page:      page=1, shapes=0 => 1 + 0*3 = 1
# minimal-drawing: page=1, shapes=1 => 1 + 1*3 = 4
# shapes-basic:    page=1, shapes=3 => 1 + 3*3 = 10

def test_page_plus_shape_times_three_empty():
    assert fodg_page_count_plus_shape_count_times_three(_EMPTY) == 1


def test_page_plus_shape_times_three_minimal():
    assert fodg_page_count_plus_shape_count_times_three(_MINIMAL) == 4


def test_page_plus_shape_times_three_shapes():
    assert fodg_page_count_plus_shape_count_times_three(_SHAPES) == 10


def test_page_plus_shape_times_three_empty_is_int():
    assert isinstance(fodg_page_count_plus_shape_count_times_three(_EMPTY), int)


def test_page_plus_shape_times_three_minimal_is_int():
    assert isinstance(fodg_page_count_plus_shape_count_times_three(_MINIMAL), int)


def test_page_plus_shape_times_three_distinct():
    v1 = fodg_page_count_plus_shape_count_times_three(_EMPTY)
    v2 = fodg_page_count_plus_shape_count_times_three(_MINIMAL)
    v3 = fodg_page_count_plus_shape_count_times_three(_SHAPES)
    assert len({v1, v2, v3}) == 3


# fodg_shape_count_is_one
# empty-page:      shapes=0 => False
# minimal-drawing: shapes=1 => True
# shapes-basic:    shapes=3 => False

def test_shape_count_is_one_empty_is_false():
    assert fodg_shape_count_is_one(_EMPTY) is False


def test_shape_count_is_one_minimal_is_true():
    assert fodg_shape_count_is_one(_MINIMAL) is True


def test_shape_count_is_one_shapes_is_false():
    assert fodg_shape_count_is_one(_SHAPES) is False


def test_shape_count_is_one_empty_is_bool():
    assert isinstance(fodg_shape_count_is_one(_EMPTY), bool)


def test_shape_count_is_one_minimal_is_bool():
    assert isinstance(fodg_shape_count_is_one(_MINIMAL), bool)


def test_shape_count_is_one_both_true_and_false():
    results = [
        fodg_shape_count_is_one(_EMPTY),
        fodg_shape_count_is_one(_MINIMAL),
        fodg_shape_count_is_one(_SHAPES),
    ]
    assert True in results and False in results
