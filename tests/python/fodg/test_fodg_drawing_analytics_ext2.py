"""Tests for FODG drawing analytics extension functions (second batch)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.drawing_document import (
    fodg_page_count,
    fodg_is_fodg,
    fodg_shapes_total,
    fodg_pages_without_shapes_count,
    fodg_text_items_per_page,
    fodg_has_mixed_content,
)

SAMPLES = Path("samples/by-format/fodg")
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"
EMPTY = SAMPLES / "empty-page.fodg"
# minimal-drawing.fodg: 1 page, 1 shape, text_content=['Rectangle']
# shapes-basic.fodg: 1 page, 3 shapes, text_content=['Rect', 'Ellipse']
# empty-page.fodg: 1 page, 0 shapes, text_content=[]


# --- fodg_page_count ---

def test_page_count_minimal():
    assert fodg_page_count(MINIMAL) == 1


def test_page_count_shapes():
    assert fodg_page_count(SHAPES) == 1


def test_page_count_empty():
    assert fodg_page_count(EMPTY) == 1


def test_page_count_returns_int():
    assert isinstance(fodg_page_count(MINIMAL), int)


# --- fodg_is_fodg ---

def test_is_fodg_minimal():
    assert fodg_is_fodg(MINIMAL) is True


def test_is_fodg_shapes():
    assert fodg_is_fodg(SHAPES) is True


def test_is_fodg_returns_bool():
    assert isinstance(fodg_is_fodg(MINIMAL), bool)


# --- fodg_shapes_total ---

def test_shapes_total_minimal():
    assert fodg_shapes_total(MINIMAL) == 1


def test_shapes_total_shapes():
    assert fodg_shapes_total(SHAPES) == 3


def test_shapes_total_empty():
    assert fodg_shapes_total(EMPTY) == 0


def test_shapes_total_returns_int():
    assert isinstance(fodg_shapes_total(MINIMAL), int)


# --- fodg_pages_without_shapes_count ---

def test_pages_without_shapes_minimal():
    # minimal has 1 shape => no page without shapes
    assert fodg_pages_without_shapes_count(MINIMAL) == 0


def test_pages_without_shapes_empty():
    # empty-page has 0 shapes => 1 page without shapes
    assert fodg_pages_without_shapes_count(EMPTY) == 1


def test_pages_without_shapes_shapes():
    # shapes-basic has 3 shapes => no page without shapes
    assert fodg_pages_without_shapes_count(SHAPES) == 0


def test_pages_without_shapes_returns_int():
    assert isinstance(fodg_pages_without_shapes_count(MINIMAL), int)


# --- fodg_text_items_per_page ---

def test_text_items_per_page_minimal():
    # minimal has 1 text item on its single page
    assert fodg_text_items_per_page(MINIMAL) == [1]


def test_text_items_per_page_shapes():
    # shapes-basic has 2 text items on its single page
    assert fodg_text_items_per_page(SHAPES) == [2]


def test_text_items_per_page_empty():
    # empty-page has 0 text items
    assert fodg_text_items_per_page(EMPTY) == [0]


def test_text_items_per_page_returns_list():
    assert isinstance(fodg_text_items_per_page(MINIMAL), list)


def test_text_items_per_page_length_matches_pages():
    result = fodg_text_items_per_page(MINIMAL)
    assert len(result) == fodg_page_count(MINIMAL)


# --- fodg_has_mixed_content ---

def test_has_mixed_content_minimal():
    # single page with shapes => not mixed
    assert fodg_has_mixed_content(MINIMAL) is False


def test_has_mixed_content_empty():
    # single page with no shapes => not mixed
    assert fodg_has_mixed_content(EMPTY) is False


def test_has_mixed_content_shapes():
    # single page with shapes => not mixed
    assert fodg_has_mixed_content(SHAPES) is False


def test_has_mixed_content_returns_bool():
    assert isinstance(fodg_has_mixed_content(MINIMAL), bool)
