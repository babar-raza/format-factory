"""
Sprint r336: FODG analytics — fodg_text_item_count_times_two, fodg_has_more_shapes_than_text_items
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_text_item_count_times_two,
    fodg_has_more_shapes_than_text_items,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"        # text_items=0, shapes=0
_MINIMAL = _FODG / "minimal-drawing.fodg"  # text_items=1, shapes=1
_SHAPES = _FODG / "shapes-basic.fodg"      # text_items=2, shapes=3


# --- fodg_text_item_count_times_two ---

def test_text_times_two_empty():
    assert fodg_text_item_count_times_two(_EMPTY) == 0


def test_text_times_two_minimal():
    assert fodg_text_item_count_times_two(_MINIMAL) == 2


def test_text_times_two_shapes():
    assert fodg_text_item_count_times_two(_SHAPES) == 4


def test_text_times_two_returns_int():
    assert isinstance(fodg_text_item_count_times_two(_EMPTY), int)


def test_text_times_two_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_text_item_count_times_two(p) >= 0


def test_text_times_two_all_distinct():
    vals = [fodg_text_item_count_times_two(p) for p in (_EMPTY, _MINIMAL, _SHAPES)]
    assert len(set(vals)) == 3


# --- fodg_has_more_shapes_than_text_items ---

def test_more_shapes_empty():
    assert fodg_has_more_shapes_than_text_items(_EMPTY) is False


def test_more_shapes_minimal():
    assert fodg_has_more_shapes_than_text_items(_MINIMAL) is False


def test_more_shapes_shapes():
    assert fodg_has_more_shapes_than_text_items(_SHAPES) is True


def test_more_shapes_returns_bool():
    assert isinstance(fodg_has_more_shapes_than_text_items(_EMPTY), bool)


def test_more_shapes_true_case():
    assert fodg_has_more_shapes_than_text_items(_SHAPES) is True


def test_more_shapes_false_case():
    assert fodg_has_more_shapes_than_text_items(_MINIMAL) is False
