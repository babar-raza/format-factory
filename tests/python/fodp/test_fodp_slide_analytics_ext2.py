"""Tests for FODP slide analytics extension functions (batch 2) in fodp_slide_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_slide_analytics import (
    fodp_slide_titles,
    fodp_has_multiple_slides,
    fodp_avg_shapes_per_slide,
    fodp_slides_with_shapes_count,
    fodp_all_text_items,
    fodp_slide_names_are_unique,
)

SAMPLES = Path("samples/by-format/fodp")
MINIMAL   = SAMPLES / "minimal-presentation.fodp"   # 1 slide, name='Slide1', title='Hello', shape=1
TWO_SLIDE = SAMPLES / "two-slides-basic.fodp"        # 2 slides: Slide1(2 shapes) Slide2(1 shape)
TITLE_ONLY = SAMPLES / "title-only.fodp"             # 0 slides


# fodp_slide_titles
def test_slide_titles_minimal():
    titles = fodp_slide_titles(MINIMAL)
    assert titles == ["Hello"]

def test_slide_titles_two_slides():
    titles = fodp_slide_titles(TWO_SLIDE)
    assert titles == ["Introduction", "Conclusion"]

def test_slide_titles_empty():
    assert fodp_slide_titles(TITLE_ONLY) == []

def test_slide_titles_returns_list():
    assert isinstance(fodp_slide_titles(MINIMAL), list)


# fodp_has_multiple_slides
def test_has_multiple_slides_minimal():
    assert fodp_has_multiple_slides(MINIMAL) is False

def test_has_multiple_slides_two():
    assert fodp_has_multiple_slides(TWO_SLIDE) is True

def test_has_multiple_slides_returns_bool():
    assert isinstance(fodp_has_multiple_slides(MINIMAL), bool)


# fodp_avg_shapes_per_slide
def test_avg_shapes_per_slide_minimal():
    # 1 slide, 1 shape → avg=1.0
    assert fodp_avg_shapes_per_slide(MINIMAL) == pytest.approx(1.0)

def test_avg_shapes_per_slide_two_slides():
    # slide1=2 shapes, slide2=1 shape → avg=1.5
    assert fodp_avg_shapes_per_slide(TWO_SLIDE) == pytest.approx(1.5)

def test_avg_shapes_per_slide_empty():
    assert fodp_avg_shapes_per_slide(TITLE_ONLY) == pytest.approx(0.0)

def test_avg_shapes_per_slide_returns_float():
    assert isinstance(fodp_avg_shapes_per_slide(MINIMAL), float)


# fodp_slides_with_shapes_count
def test_slides_with_shapes_minimal():
    assert fodp_slides_with_shapes_count(MINIMAL) == 1

def test_slides_with_shapes_two():
    assert fodp_slides_with_shapes_count(TWO_SLIDE) == 2

def test_slides_with_shapes_returns_int():
    assert isinstance(fodp_slides_with_shapes_count(MINIMAL), int)


# fodp_all_text_items
def test_all_text_items_minimal():
    items = fodp_all_text_items(MINIMAL)
    assert items == ["Hello"]

def test_all_text_items_two_slides():
    items = fodp_all_text_items(TWO_SLIDE)
    assert "Introduction" in items
    assert "First slide content." in items
    assert "Conclusion" in items

def test_all_text_items_returns_list():
    assert isinstance(fodp_all_text_items(MINIMAL), list)


# fodp_slide_names_are_unique
def test_slide_names_unique_minimal():
    assert fodp_slide_names_are_unique(MINIMAL) is True

def test_slide_names_unique_two_slides():
    assert fodp_slide_names_are_unique(TWO_SLIDE) is True

def test_slide_names_unique_returns_bool():
    assert isinstance(fodp_slide_names_are_unique(MINIMAL), bool)
