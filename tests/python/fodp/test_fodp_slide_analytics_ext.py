"""Tests for FODP slide analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_slide_analytics import (
    fodp_slide_count,
    fodp_is_fodp,
    fodp_first_slide_title,
    fodp_slide_shape_counts,
    fodp_total_shape_count,
    fodp_has_text,
)

SAMPLES = Path("samples/by-format/fodp")
MINIMAL = SAMPLES / "minimal-presentation.fodp"
TITLE_ONLY = SAMPLES / "title-only.fodp"
TWO_SLIDES = SAMPLES / "two-slides-basic.fodp"
# minimal-presentation.fodp: 1 slide='Slide1', title='Hello', 1 shape
# title-only.fodp: 0 slides (no draw:page elements)
# two-slides-basic.fodp: 2 slides ['Introduction','Conclusion'], shapes=[2,1]


# --- fodp_slide_count ---

def test_slide_count_minimal():
    assert fodp_slide_count(MINIMAL) == 1


def test_slide_count_title_only():
    assert fodp_slide_count(TITLE_ONLY) == 0


def test_slide_count_two():
    assert fodp_slide_count(TWO_SLIDES) == 2


def test_slide_count_returns_int():
    assert isinstance(fodp_slide_count(MINIMAL), int)


# --- fodp_is_fodp ---

def test_is_fodp_minimal():
    assert fodp_is_fodp(MINIMAL) is True


def test_is_fodp_title_only():
    assert fodp_is_fodp(TITLE_ONLY) is True


def test_is_fodp_returns_bool():
    assert isinstance(fodp_is_fodp(MINIMAL), bool)


# --- fodp_first_slide_title ---

def test_first_slide_title_minimal():
    assert fodp_first_slide_title(MINIMAL) == "Hello"


def test_first_slide_title_two():
    assert fodp_first_slide_title(TWO_SLIDES) == "Introduction"


def test_first_slide_title_empty():
    # title-only has 0 slides
    assert fodp_first_slide_title(TITLE_ONLY) == ""


def test_first_slide_title_returns_str():
    assert isinstance(fodp_first_slide_title(MINIMAL), str)


# --- fodp_slide_shape_counts ---

def test_slide_shape_counts_minimal():
    assert fodp_slide_shape_counts(MINIMAL) == [1]


def test_slide_shape_counts_two():
    assert fodp_slide_shape_counts(TWO_SLIDES) == [2, 1]


def test_slide_shape_counts_empty():
    assert fodp_slide_shape_counts(TITLE_ONLY) == []


def test_slide_shape_counts_returns_list():
    assert isinstance(fodp_slide_shape_counts(MINIMAL), list)


# --- fodp_total_shape_count ---

def test_total_shape_count_minimal():
    assert fodp_total_shape_count(MINIMAL) == 1


def test_total_shape_count_two():
    assert fodp_total_shape_count(TWO_SLIDES) == 3


def test_total_shape_count_empty():
    assert fodp_total_shape_count(TITLE_ONLY) == 0


def test_total_shape_count_returns_int():
    assert isinstance(fodp_total_shape_count(MINIMAL), int)


# --- fodp_has_text ---

def test_has_text_minimal():
    assert fodp_has_text(MINIMAL) is True


def test_has_text_two():
    assert fodp_has_text(TWO_SLIDES) is True


def test_has_text_empty():
    assert fodp_has_text(TITLE_ONLY) is False


def test_has_text_returns_bool():
    assert isinstance(fodp_has_text(MINIMAL), bool)
