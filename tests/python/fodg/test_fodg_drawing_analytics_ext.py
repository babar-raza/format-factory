"""Tests for extended FODG drawing analytics functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.drawing_document import (
    fodg_has_single_page,
    fodg_page_names,
    fodg_average_shape_count,
    fodg_pages_with_shapes_count,
    fodg_total_text_length,
    fodg_has_text_on_all_pages,
)

SAMPLES = Path("samples/by-format/fodg")
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"
EMPTY = SAMPLES / "empty-page.fodg"


# --- fodg_has_single_page ---

def test_has_single_page_minimal():
    assert fodg_has_single_page(MINIMAL) is True


def test_has_single_page_shapes():
    assert fodg_has_single_page(SHAPES) is True


def test_has_single_page_empty():
    assert fodg_has_single_page(EMPTY) is True


# --- fodg_page_names ---

def test_page_names_minimal():
    assert fodg_page_names(MINIMAL) == ["Page1"]


def test_page_names_shapes():
    assert fodg_page_names(SHAPES) == ["Page1"]


def test_page_names_returns_list():
    result = fodg_page_names(MINIMAL)
    assert isinstance(result, list)


def test_page_names_empty_doc():
    assert fodg_page_names(EMPTY) == ["Page1"]


# --- fodg_average_shape_count ---

def test_average_shape_count_minimal():
    assert fodg_average_shape_count(MINIMAL) == pytest.approx(1.0)


def test_average_shape_count_shapes():
    assert fodg_average_shape_count(SHAPES) == pytest.approx(3.0)


def test_average_shape_count_empty():
    assert fodg_average_shape_count(EMPTY) == pytest.approx(0.0)


def test_average_shape_count_is_float():
    result = fodg_average_shape_count(MINIMAL)
    assert isinstance(result, float)


# --- fodg_pages_with_shapes_count ---

def test_pages_with_shapes_minimal():
    assert fodg_pages_with_shapes_count(MINIMAL) == 1


def test_pages_with_shapes_shapes():
    assert fodg_pages_with_shapes_count(SHAPES) == 1


def test_pages_with_shapes_empty():
    assert fodg_pages_with_shapes_count(EMPTY) == 0


def test_pages_with_shapes_is_int():
    result = fodg_pages_with_shapes_count(MINIMAL)
    assert isinstance(result, int)


# --- fodg_total_text_length ---

def test_total_text_length_minimal():
    # text_content=['Rectangle'] → 9 chars
    assert fodg_total_text_length(MINIMAL) == 9


def test_total_text_length_shapes():
    # text_content=['Rect', 'Ellipse'] → 4 + 7 = 11
    assert fodg_total_text_length(SHAPES) == 11


def test_total_text_length_empty():
    assert fodg_total_text_length(EMPTY) == 0


def test_total_text_length_is_int():
    result = fodg_total_text_length(MINIMAL)
    assert isinstance(result, int)


# --- fodg_has_text_on_all_pages ---

def test_has_text_on_all_pages_minimal():
    assert fodg_has_text_on_all_pages(MINIMAL) is True


def test_has_text_on_all_pages_shapes():
    assert fodg_has_text_on_all_pages(SHAPES) is True


def test_has_text_on_all_pages_empty():
    assert fodg_has_text_on_all_pages(EMPTY) is False


def test_has_text_on_all_pages_returns_bool():
    result = fodg_has_text_on_all_pages(MINIMAL)
    assert isinstance(result, bool)
