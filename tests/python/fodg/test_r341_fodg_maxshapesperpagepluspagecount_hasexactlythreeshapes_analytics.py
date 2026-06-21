"""
Sprint r341: FODG analytics — fodg_max_shapes_per_page_plus_page_count, fodg_has_exactly_three_shapes
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_max_shapes_per_page_plus_page_count,
    fodg_has_exactly_three_shapes,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"        # max_shapes=0, pages=1 → 1; shapes=0 → False
_MINIMAL = _FODG / "minimal-drawing.fodg"  # max_shapes=1, pages=1 → 2; shapes=1 → False
_SHAPES = _FODG / "shapes-basic.fodg"      # max_shapes=3, pages=1 → 4; shapes=3 → True


# --- fodg_max_shapes_per_page_plus_page_count ---

def test_max_plus_page_empty():
    assert fodg_max_shapes_per_page_plus_page_count(_EMPTY) == 1


def test_max_plus_page_minimal():
    assert fodg_max_shapes_per_page_plus_page_count(_MINIMAL) == 2


def test_max_plus_page_shapes():
    assert fodg_max_shapes_per_page_plus_page_count(_SHAPES) == 4


def test_max_plus_page_returns_int():
    assert isinstance(fodg_max_shapes_per_page_plus_page_count(_EMPTY), int)


def test_max_plus_page_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_max_shapes_per_page_plus_page_count(p) >= 0


def test_max_plus_page_all_distinct():
    vals = [fodg_max_shapes_per_page_plus_page_count(p) for p in (_EMPTY, _MINIMAL, _SHAPES)]
    assert len(set(vals)) == 3


# --- fodg_has_exactly_three_shapes ---

def test_exactly_three_shapes_empty():
    assert fodg_has_exactly_three_shapes(_EMPTY) is False


def test_exactly_three_shapes_minimal():
    assert fodg_has_exactly_three_shapes(_MINIMAL) is False


def test_exactly_three_shapes_shapes():
    assert fodg_has_exactly_three_shapes(_SHAPES) is True


def test_exactly_three_shapes_returns_bool():
    assert isinstance(fodg_has_exactly_three_shapes(_EMPTY), bool)


def test_exactly_three_shapes_true_case():
    assert fodg_has_exactly_three_shapes(_SHAPES) is True


def test_exactly_three_shapes_false_case():
    assert fodg_has_exactly_three_shapes(_EMPTY) is False
