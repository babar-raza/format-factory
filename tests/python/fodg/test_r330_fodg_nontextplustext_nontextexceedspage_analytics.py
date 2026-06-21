"""
Sprint r330: FODG analytics — fodg_non_text_shape_count_plus_text_item_count,
             fodg_non_text_shape_count_exceeds_page_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_non_text_shape_count_plus_text_item_count,
    fodg_non_text_shape_count_exceeds_page_count,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"    # non_text=0, text=0, pages=1 → sum=0, exceeds=False
_MINIMAL = _FODG / "minimal-drawing.fodg" # non_text=0, text=1, pages=1 → sum=1, exceeds=False
_BASIC   = _FODG / "shapes-basic.fodg"  # non_text=2, text=2, pages=1 → sum=4, exceeds=True


# --- fodg_non_text_shape_count_plus_text_item_count ---

def test_non_text_plus_text_empty():
    assert fodg_non_text_shape_count_plus_text_item_count(_EMPTY) == 0


def test_non_text_plus_text_minimal():
    assert fodg_non_text_shape_count_plus_text_item_count(_MINIMAL) == 1


def test_non_text_plus_text_basic():
    assert fodg_non_text_shape_count_plus_text_item_count(_BASIC) == 4


def test_non_text_plus_text_returns_int():
    assert isinstance(fodg_non_text_shape_count_plus_text_item_count(_EMPTY), int)


def test_non_text_plus_text_nonnegative():
    for p in (_EMPTY, _MINIMAL, _BASIC):
        assert fodg_non_text_shape_count_plus_text_item_count(p) >= 0


def test_non_text_plus_text_all_distinct():
    vals = [fodg_non_text_shape_count_plus_text_item_count(p) for p in (_EMPTY, _MINIMAL, _BASIC)]
    assert len(set(vals)) == 3


# --- fodg_non_text_shape_count_exceeds_page_count ---

def test_non_text_exceeds_page_empty():
    assert fodg_non_text_shape_count_exceeds_page_count(_EMPTY) is False


def test_non_text_exceeds_page_minimal():
    assert fodg_non_text_shape_count_exceeds_page_count(_MINIMAL) is False


def test_non_text_exceeds_page_basic():
    assert fodg_non_text_shape_count_exceeds_page_count(_BASIC) is True


def test_non_text_exceeds_page_returns_bool():
    assert isinstance(fodg_non_text_shape_count_exceeds_page_count(_EMPTY), bool)


def test_non_text_exceeds_page_true_case():
    assert fodg_non_text_shape_count_exceeds_page_count(_BASIC) is True


def test_non_text_exceeds_page_false_case():
    assert fodg_non_text_shape_count_exceeds_page_count(_EMPTY) is False
