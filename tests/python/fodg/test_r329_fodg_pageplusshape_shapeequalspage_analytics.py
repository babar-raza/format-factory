"""
Sprint r329: FODG analytics — fodg_page_count_plus_shape_count, fodg_shape_count_equals_page_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_page_count_plus_shape_count,
    fodg_shape_count_equals_page_count,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"    # pages=1, shapes=0 → sum=1, equal=False
_MINIMAL = _FODG / "minimal-drawing.fodg" # pages=1, shapes=1 → sum=2, equal=True
_BASIC   = _FODG / "shapes-basic.fodg"  # pages=1, shapes=3 → sum=4, equal=False


# --- fodg_page_count_plus_shape_count ---

def test_page_plus_shape_empty():
    assert fodg_page_count_plus_shape_count(_EMPTY) == 1


def test_page_plus_shape_minimal():
    assert fodg_page_count_plus_shape_count(_MINIMAL) == 2


def test_page_plus_shape_basic():
    assert fodg_page_count_plus_shape_count(_BASIC) == 4


def test_page_plus_shape_returns_int():
    assert isinstance(fodg_page_count_plus_shape_count(_EMPTY), int)


def test_page_plus_shape_positive():
    for p in (_EMPTY, _MINIMAL, _BASIC):
        assert fodg_page_count_plus_shape_count(p) > 0


def test_page_plus_shape_all_distinct():
    vals = [fodg_page_count_plus_shape_count(p) for p in (_EMPTY, _MINIMAL, _BASIC)]
    assert len(set(vals)) == 3


# --- fodg_shape_count_equals_page_count ---

def test_shape_equals_page_empty():
    assert fodg_shape_count_equals_page_count(_EMPTY) is False


def test_shape_equals_page_minimal():
    assert fodg_shape_count_equals_page_count(_MINIMAL) is True


def test_shape_equals_page_basic():
    assert fodg_shape_count_equals_page_count(_BASIC) is False


def test_shape_equals_page_returns_bool():
    assert isinstance(fodg_shape_count_equals_page_count(_EMPTY), bool)


def test_shape_equals_page_true_case():
    assert fodg_shape_count_equals_page_count(_MINIMAL) is True


def test_shape_equals_page_false_case():
    assert fodg_shape_count_equals_page_count(_EMPTY) is False
