"""
Sprint 35 — 5 new FODG analytics functions.
Tests: fodg_nonempty_shape_ratio, fodg_max_shape_text_length,
       fodg_shapes_with_text_count, fodg_nonempty_page_ratio,
       fodg_total_shapes_and_pages
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    fodg_nonempty_shape_ratio,
    fodg_max_shape_text_length,
    fodg_shapes_with_text_count,
    fodg_nonempty_page_ratio,
    fodg_total_shapes_and_pages,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_MINIMAL = str(_SAMPLES / "minimal-drawing.fodg")
_SHAPES = str(_SAMPLES / "shapes-basic.fodg")
_EMPTY = str(_SAMPLES / "empty-page.fodg")


# --- fodg_nonempty_shape_ratio ---

def test_nonempty_shape_ratio_minimal_is_float():
    result = fodg_nonempty_shape_ratio(_MINIMAL)
    assert isinstance(result, float)


def test_nonempty_shape_ratio_minimal_in_range():
    result = fodg_nonempty_shape_ratio(_MINIMAL)
    assert 0.0 <= result <= 1.0


def test_nonempty_shape_ratio_shapes_is_float():
    result = fodg_nonempty_shape_ratio(_SHAPES)
    assert isinstance(result, float)


def test_nonempty_shape_ratio_shapes_in_range():
    result = fodg_nonempty_shape_ratio(_SHAPES)
    assert 0.0 <= result <= 1.0


def test_nonempty_shape_ratio_empty_page_in_range():
    result = fodg_nonempty_shape_ratio(_EMPTY)
    assert 0.0 <= result <= 1.0


# --- fodg_max_shape_text_length ---

def test_max_shape_text_length_minimal_is_int():
    result = fodg_max_shape_text_length(_MINIMAL)
    assert isinstance(result, int)


def test_max_shape_text_length_minimal_nonnegative():
    result = fodg_max_shape_text_length(_MINIMAL)
    assert result >= 0


def test_max_shape_text_length_shapes_is_int():
    result = fodg_max_shape_text_length(_SHAPES)
    assert isinstance(result, int)


def test_max_shape_text_length_shapes_nonnegative():
    result = fodg_max_shape_text_length(_SHAPES)
    assert result >= 0


def test_max_shape_text_length_empty_is_zero():
    result = fodg_max_shape_text_length(_EMPTY)
    assert result == 0


# --- fodg_shapes_with_text_count ---

def test_shapes_with_text_count_minimal_is_int():
    result = fodg_shapes_with_text_count(_MINIMAL)
    assert isinstance(result, int)


def test_shapes_with_text_count_minimal_nonnegative():
    result = fodg_shapes_with_text_count(_MINIMAL)
    assert result >= 0


def test_shapes_with_text_count_shapes_is_int():
    result = fodg_shapes_with_text_count(_SHAPES)
    assert isinstance(result, int)


def test_shapes_with_text_count_empty_is_zero():
    result = fodg_shapes_with_text_count(_EMPTY)
    assert result == 0


# --- fodg_nonempty_page_ratio ---

def test_nonempty_page_ratio_minimal_is_float():
    result = fodg_nonempty_page_ratio(_MINIMAL)
    assert isinstance(result, float)


def test_nonempty_page_ratio_minimal_in_range():
    result = fodg_nonempty_page_ratio(_MINIMAL)
    assert 0.0 <= result <= 1.0


def test_nonempty_page_ratio_shapes_positive():
    result = fodg_nonempty_page_ratio(_SHAPES)
    assert result > 0.0


# --- fodg_total_shapes_and_pages ---

def test_total_shapes_and_pages_minimal_is_int():
    result = fodg_total_shapes_and_pages(_MINIMAL)
    assert isinstance(result, int)


def test_total_shapes_and_pages_minimal_positive():
    result = fodg_total_shapes_and_pages(_MINIMAL)
    assert result >= 1


def test_total_shapes_and_pages_shapes_greater_than_minimal():
    r_shapes = fodg_total_shapes_and_pages(_SHAPES)
    r_empty = fodg_total_shapes_and_pages(_EMPTY)
    assert r_shapes >= r_empty
