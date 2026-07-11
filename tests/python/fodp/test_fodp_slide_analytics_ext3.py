"""Tests for fodp_slide_analytics extension functions (ext3 batch)."""
from __future__ import annotations

from pathlib import Path

from fodp.fodp_slide_analytics import (
    fodp_last_slide_title,
    fodp_slide_text_counts,
    fodp_max_shape_count,
    fodp_min_shape_count,
    fodp_all_text_items_flat,
    fodp_slides_without_text_count,
)

SAMPLES = Path("samples/by-format/fodp")
MINIMAL = SAMPLES / "minimal-presentation.fodp"
MULTI = SAMPLES / "two-slides.fodp"


# --- fodp_last_slide_title ---

def test_last_slide_title_returns_str():
    assert isinstance(fodp_last_slide_title(MINIMAL), str)


def test_last_slide_title_minimal():
    result = fodp_last_slide_title(MINIMAL)
    assert isinstance(result, str)


# --- fodp_slide_text_counts ---

def test_slide_text_counts_returns_list():
    result = fodp_slide_text_counts(MINIMAL)
    assert isinstance(result, list)


def test_slide_text_counts_length():
    from fodp.fodp_slide_analytics import fodp_slide_count
    result = fodp_slide_text_counts(MINIMAL)
    assert len(result) == fodp_slide_count(MINIMAL)


def test_slide_text_counts_are_ints():
    result = fodp_slide_text_counts(MINIMAL)
    assert all(isinstance(v, int) for v in result)


# --- fodp_max_shape_count ---

def test_max_shape_count_returns_int():
    assert isinstance(fodp_max_shape_count(MINIMAL), int)


def test_max_shape_count_nonneg():
    assert fodp_max_shape_count(MINIMAL) >= 0


# --- fodp_min_shape_count ---

def test_min_shape_count_returns_int():
    assert isinstance(fodp_min_shape_count(MINIMAL), int)


def test_min_shape_count_leq_max():
    min_val = fodp_min_shape_count(MINIMAL)
    max_val = fodp_max_shape_count(MINIMAL)
    assert min_val <= max_val


# --- fodp_all_text_items_flat ---

def test_all_text_items_flat_returns_list():
    assert isinstance(fodp_all_text_items_flat(MINIMAL), list)


def test_all_text_items_flat_unique():
    result = fodp_all_text_items_flat(MINIMAL)
    assert len(result) == len(set(result))


# --- fodp_slides_without_text_count ---

def test_slides_without_text_count_returns_int():
    assert isinstance(fodp_slides_without_text_count(MINIMAL), int)


def test_slides_without_text_count_nonneg():
    assert fodp_slides_without_text_count(MINIMAL) >= 0


def test_slides_without_text_plus_with_text_eq_total():
    from fodp.fodp_slide_analytics import fodp_slides_with_text_count, fodp_slide_count
    without = fodp_slides_without_text_count(MINIMAL)
    with_text = fodp_slides_with_text_count(MINIMAL)
    total = fodp_slide_count(MINIMAL)
    assert without + with_text == total
