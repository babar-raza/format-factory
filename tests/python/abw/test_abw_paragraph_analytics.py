"""Tests for ABW paragraph analytics module."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_paragraph_analytics import (
    abw_total_char_count,
    abw_unique_paragraph_count,
    abw_has_repeated_paragraphs,
    abw_max_paragraph_char_count,
    abw_min_paragraph_char_count,
    abw_avg_paragraph_char_count,
)

SAMPLES = Path("samples/by-format/abw")
MINIMAL = SAMPLES / "minimal-document.abw"   # paragraphs=['Hello']
TWO = SAMPLES / "two-paragraphs.abw"         # paragraphs=['First paragraph.', 'Second paragraph.']
EMPTY = SAMPLES / "empty-section.abw"        # paragraphs=[]


# --- abw_total_char_count ---

def test_total_char_count_minimal():
    assert abw_total_char_count(MINIMAL) == 5  # 'Hello'


def test_total_char_count_two():
    # 'First paragraph.' (16) + 'Second paragraph.' (17) = 33
    assert abw_total_char_count(TWO) == 33


def test_total_char_count_empty():
    assert abw_total_char_count(EMPTY) == 0


def test_total_char_count_is_int():
    assert isinstance(abw_total_char_count(MINIMAL), int)


# --- abw_unique_paragraph_count ---

def test_unique_paragraph_count_minimal():
    assert abw_unique_paragraph_count(MINIMAL) == 1


def test_unique_paragraph_count_two():
    assert abw_unique_paragraph_count(TWO) == 2


def test_unique_paragraph_count_empty():
    assert abw_unique_paragraph_count(EMPTY) == 0


def test_unique_paragraph_count_is_int():
    assert isinstance(abw_unique_paragraph_count(MINIMAL), int)


# --- abw_has_repeated_paragraphs ---

def test_has_repeated_paragraphs_minimal():
    assert abw_has_repeated_paragraphs(MINIMAL) is False


def test_has_repeated_paragraphs_two():
    assert abw_has_repeated_paragraphs(TWO) is False


def test_has_repeated_paragraphs_empty():
    assert abw_has_repeated_paragraphs(EMPTY) is False


def test_has_repeated_paragraphs_returns_bool():
    assert isinstance(abw_has_repeated_paragraphs(MINIMAL), bool)


# --- abw_max_paragraph_char_count ---

def test_max_paragraph_char_count_minimal():
    assert abw_max_paragraph_char_count(MINIMAL) == 5


def test_max_paragraph_char_count_two():
    assert abw_max_paragraph_char_count(TWO) == 17  # 'Second paragraph.'


def test_max_paragraph_char_count_empty():
    assert abw_max_paragraph_char_count(EMPTY) == 0


def test_max_paragraph_char_count_is_int():
    assert isinstance(abw_max_paragraph_char_count(MINIMAL), int)


# --- abw_min_paragraph_char_count ---

def test_min_paragraph_char_count_minimal():
    assert abw_min_paragraph_char_count(MINIMAL) == 5


def test_min_paragraph_char_count_two():
    assert abw_min_paragraph_char_count(TWO) == 16  # 'First paragraph.'


def test_min_paragraph_char_count_empty():
    assert abw_min_paragraph_char_count(EMPTY) == 0


def test_min_paragraph_char_count_is_int():
    assert isinstance(abw_min_paragraph_char_count(MINIMAL), int)


# --- abw_avg_paragraph_char_count ---

def test_avg_paragraph_char_count_minimal():
    assert abw_avg_paragraph_char_count(MINIMAL) == pytest.approx(5.0)


def test_avg_paragraph_char_count_two():
    assert abw_avg_paragraph_char_count(TWO) == pytest.approx(16.5)


def test_avg_paragraph_char_count_empty():
    assert abw_avg_paragraph_char_count(EMPTY) == pytest.approx(0.0)


def test_avg_paragraph_char_count_is_float():
    assert isinstance(abw_avg_paragraph_char_count(MINIMAL), float)
