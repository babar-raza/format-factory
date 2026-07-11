"""Tests for ABW paragraph analytics extension functions (batch 2) in abw_paragraph_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_paragraph_analytics import (
    abw_has_sections,
    abw_last_paragraph,
    abw_is_single_paragraph,
    abw_paragraph_texts,
    abw_avg_word_count,
    abw_has_empty_paragraphs,
)

SAMPLES = Path("samples/by-format/abw")
MINIMAL   = SAMPLES / "minimal-document.abw"    # 1 para "Hello", 1 section
TWO_PARA  = SAMPLES / "two-paragraphs.abw"      # 2 paras "First paragraph." / "Second paragraph."
EMPTY_SEC = SAMPLES / "empty-section.abw"       # 0 paras, 1 section


# abw_has_sections
def test_has_sections_minimal():
    assert abw_has_sections(MINIMAL) is True

def test_has_sections_two_para():
    assert abw_has_sections(TWO_PARA) is True

def test_has_sections_empty_section():
    assert abw_has_sections(EMPTY_SEC) is True

def test_has_sections_returns_bool():
    assert isinstance(abw_has_sections(MINIMAL), bool)


# abw_last_paragraph
def test_last_paragraph_minimal():
    assert abw_last_paragraph(MINIMAL) == "Hello"

def test_last_paragraph_two_para():
    assert abw_last_paragraph(TWO_PARA) == "Second paragraph."

def test_last_paragraph_empty():
    assert abw_last_paragraph(EMPTY_SEC) == ""

def test_last_paragraph_returns_str():
    assert isinstance(abw_last_paragraph(MINIMAL), str)


# abw_is_single_paragraph
def test_is_single_paragraph_minimal():
    assert abw_is_single_paragraph(MINIMAL) is True

def test_is_single_paragraph_two_para():
    assert abw_is_single_paragraph(TWO_PARA) is False

def test_is_single_paragraph_empty():
    assert abw_is_single_paragraph(EMPTY_SEC) is False

def test_is_single_paragraph_returns_bool():
    assert isinstance(abw_is_single_paragraph(MINIMAL), bool)


# abw_paragraph_texts
def test_paragraph_texts_minimal():
    assert abw_paragraph_texts(MINIMAL) == ["Hello"]

def test_paragraph_texts_two_para():
    texts = abw_paragraph_texts(TWO_PARA)
    assert texts == ["First paragraph.", "Second paragraph."]

def test_paragraph_texts_returns_list():
    assert isinstance(abw_paragraph_texts(MINIMAL), list)


# abw_avg_word_count
def test_avg_word_count_minimal():
    # "Hello" = 1 word → avg=1.0
    assert abw_avg_word_count(MINIMAL) == pytest.approx(1.0)

def test_avg_word_count_two_para():
    # "First paragraph."=2w, "Second paragraph."=2w → avg=2.0
    assert abw_avg_word_count(TWO_PARA) == pytest.approx(2.0)

def test_avg_word_count_empty():
    assert abw_avg_word_count(EMPTY_SEC) == pytest.approx(0.0)

def test_avg_word_count_returns_float():
    assert isinstance(abw_avg_word_count(MINIMAL), float)


# abw_has_empty_paragraphs
def test_has_empty_paragraphs_minimal():
    # "Hello" is non-empty
    assert abw_has_empty_paragraphs(MINIMAL) is False

def test_has_empty_paragraphs_two_para():
    assert abw_has_empty_paragraphs(TWO_PARA) is False

def test_has_empty_paragraphs_returns_bool():
    assert isinstance(abw_has_empty_paragraphs(MINIMAL), bool)
