"""
Sprint r339: FODG analytics — fodg_max_shapes_per_page_times_two, fodg_has_at_least_two_shapes
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_max_shapes_per_page_times_two,
    fodg_has_at_least_two_shapes,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"        # max_shapes_per_page=0, shapes=0
_MINIMAL = _FODG / "minimal-drawing.fodg"  # max_shapes_per_page=1, shapes=1
_SHAPES = _FODG / "shapes-basic.fodg"      # max_shapes_per_page=3, shapes=3


# --- fodg_max_shapes_per_page_times_two ---

def test_max_shapes_times_two_empty():
    assert fodg_max_shapes_per_page_times_two(_EMPTY) == 0


def test_max_shapes_times_two_minimal():
    assert fodg_max_shapes_per_page_times_two(_MINIMAL) == 2


def test_max_shapes_times_two_shapes():
    assert fodg_max_shapes_per_page_times_two(_SHAPES) == 6


def test_max_shapes_times_two_returns_int():
    assert isinstance(fodg_max_shapes_per_page_times_two(_EMPTY), int)


def test_max_shapes_times_two_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_max_shapes_per_page_times_two(p) >= 0


def test_max_shapes_times_two_all_distinct():
    vals = [fodg_max_shapes_per_page_times_two(p) for p in (_EMPTY, _MINIMAL, _SHAPES)]
    assert len(set(vals)) == 3


# --- fodg_has_at_least_two_shapes ---

def test_at_least_two_shapes_empty():
    assert fodg_has_at_least_two_shapes(_EMPTY) is False


def test_at_least_two_shapes_minimal():
    assert fodg_has_at_least_two_shapes(_MINIMAL) is False


def test_at_least_two_shapes_shapes():
    assert fodg_has_at_least_two_shapes(_SHAPES) is True


def test_at_least_two_shapes_returns_bool():
    assert isinstance(fodg_has_at_least_two_shapes(_EMPTY), bool)


def test_at_least_two_shapes_true_case():
    assert fodg_has_at_least_two_shapes(_SHAPES) is True


def test_at_least_two_shapes_false_case():
    assert fodg_has_at_least_two_shapes(_MINIMAL) is False
