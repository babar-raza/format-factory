"""Tests for FODP slide analytics module."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_slide_analytics import (
    fodp_slide_name_list,
    fodp_total_text_items,
    fodp_slides_with_text_count,
    fodp_max_slide_text_items,
    fodp_min_slide_text_items,
    fodp_all_slides_have_titles,
)

SAMPLES = Path("samples/by-format/fodp")
MINIMAL = SAMPLES / "minimal-presentation.fodp"   # 1 slide, 1 text item: 'Hello'
TWO = SAMPLES / "two-slides-basic.fodp"            # 2 slides, 3 text items total
TITLE_ONLY = SAMPLES / "title-only.fodp"           # 0 slides


# --- fodp_slide_name_list ---

def test_slide_name_list_minimal():
    assert fodp_slide_name_list(MINIMAL) == ["Slide1"]


def test_slide_name_list_two():
    assert fodp_slide_name_list(TWO) == ["Slide1", "Slide2"]


def test_slide_name_list_title_only():
    assert fodp_slide_name_list(TITLE_ONLY) == []


def test_slide_name_list_returns_list():
    assert isinstance(fodp_slide_name_list(MINIMAL), list)


# --- fodp_total_text_items ---

def test_total_text_items_minimal():
    assert fodp_total_text_items(MINIMAL) == 1


def test_total_text_items_two():
    # Slide1: ['Introduction', 'First slide content.'] + Slide2: ['Conclusion'] = 3
    assert fodp_total_text_items(TWO) == 3


def test_total_text_items_title_only():
    assert fodp_total_text_items(TITLE_ONLY) == 0


def test_total_text_items_returns_int():
    assert isinstance(fodp_total_text_items(MINIMAL), int)


# --- fodp_slides_with_text_count ---

def test_slides_with_text_count_minimal():
    assert fodp_slides_with_text_count(MINIMAL) == 1


def test_slides_with_text_count_two():
    assert fodp_slides_with_text_count(TWO) == 2


def test_slides_with_text_count_title_only():
    assert fodp_slides_with_text_count(TITLE_ONLY) == 0


def test_slides_with_text_count_returns_int():
    assert isinstance(fodp_slides_with_text_count(MINIMAL), int)


# --- fodp_max_slide_text_items ---

def test_max_slide_text_items_minimal():
    assert fodp_max_slide_text_items(MINIMAL) == 1


def test_max_slide_text_items_two():
    assert fodp_max_slide_text_items(TWO) == 2


def test_max_slide_text_items_title_only():
    assert fodp_max_slide_text_items(TITLE_ONLY) == 0


def test_max_slide_text_items_returns_int():
    assert isinstance(fodp_max_slide_text_items(MINIMAL), int)


# --- fodp_min_slide_text_items ---

def test_min_slide_text_items_minimal():
    assert fodp_min_slide_text_items(MINIMAL) == 1


def test_min_slide_text_items_two():
    assert fodp_min_slide_text_items(TWO) == 1


def test_min_slide_text_items_title_only():
    assert fodp_min_slide_text_items(TITLE_ONLY) == 0


def test_min_slide_text_items_returns_int():
    assert isinstance(fodp_min_slide_text_items(MINIMAL), int)


# --- fodp_all_slides_have_titles ---

def test_all_slides_have_titles_minimal():
    assert fodp_all_slides_have_titles(MINIMAL) is True


def test_all_slides_have_titles_two():
    assert fodp_all_slides_have_titles(TWO) is True


def test_all_slides_have_titles_title_only():
    # No slides — vacuously True
    assert fodp_all_slides_have_titles(TITLE_ONLY) is True


def test_all_slides_have_titles_returns_bool():
    assert isinstance(fodp_all_slides_have_titles(MINIMAL), bool)
