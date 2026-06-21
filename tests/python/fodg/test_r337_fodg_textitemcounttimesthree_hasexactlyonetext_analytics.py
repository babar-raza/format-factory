"""
Sprint r337: FODG analytics — fodg_text_item_count_times_three, fodg_has_exactly_one_text_item
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_text_item_count_times_three,
    fodg_has_exactly_one_text_item,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"        # text_items=0
_MINIMAL = _FODG / "minimal-drawing.fodg"  # text_items=1
_SHAPES = _FODG / "shapes-basic.fodg"      # text_items=2


# --- fodg_text_item_count_times_three ---

def test_text_times_three_empty():
    assert fodg_text_item_count_times_three(_EMPTY) == 0


def test_text_times_three_minimal():
    assert fodg_text_item_count_times_three(_MINIMAL) == 3


def test_text_times_three_shapes():
    assert fodg_text_item_count_times_three(_SHAPES) == 6


def test_text_times_three_returns_int():
    assert isinstance(fodg_text_item_count_times_three(_EMPTY), int)


def test_text_times_three_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_text_item_count_times_three(p) >= 0


def test_text_times_three_all_distinct():
    vals = [fodg_text_item_count_times_three(p) for p in (_EMPTY, _MINIMAL, _SHAPES)]
    assert len(set(vals)) == 3


# --- fodg_has_exactly_one_text_item ---

def test_exactly_one_text_empty():
    assert fodg_has_exactly_one_text_item(_EMPTY) is False


def test_exactly_one_text_minimal():
    assert fodg_has_exactly_one_text_item(_MINIMAL) is True


def test_exactly_one_text_shapes():
    assert fodg_has_exactly_one_text_item(_SHAPES) is False


def test_exactly_one_text_returns_bool():
    assert isinstance(fodg_has_exactly_one_text_item(_EMPTY), bool)


def test_exactly_one_text_true_case():
    assert fodg_has_exactly_one_text_item(_MINIMAL) is True


def test_exactly_one_text_false_case():
    assert fodg_has_exactly_one_text_item(_EMPTY) is False
