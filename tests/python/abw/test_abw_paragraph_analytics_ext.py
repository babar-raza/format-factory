"""Tests for ABW paragraph analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_paragraph_analytics import (
    abw_paragraph_count,
    abw_section_count,
    abw_is_abw,
    abw_has_content,
    abw_first_paragraph,
    abw_total_word_count,
)

SAMPLES = Path("samples/by-format/abw")
MINIMAL = SAMPLES / "minimal-document.abw"
TWO_PARA = SAMPLES / "two-paragraphs.abw"
EMPTY = SAMPLES / "empty-section.abw"
# minimal-document.abw: 1 section, 1 paragraph ['Hello']
# two-paragraphs.abw: 1 section, 2 paragraphs ['First paragraph.', 'Second paragraph.']
# empty-section.abw: 1 section, 0 paragraphs


# --- abw_paragraph_count ---

def test_paragraph_count_minimal():
    assert abw_paragraph_count(MINIMAL) == 1


def test_paragraph_count_two():
    assert abw_paragraph_count(TWO_PARA) == 2


def test_paragraph_count_empty():
    assert abw_paragraph_count(EMPTY) == 0


def test_paragraph_count_returns_int():
    assert isinstance(abw_paragraph_count(MINIMAL), int)


# --- abw_section_count ---

def test_section_count_minimal():
    assert abw_section_count(MINIMAL) == 1


def test_section_count_two():
    assert abw_section_count(TWO_PARA) == 1


def test_section_count_returns_int():
    assert isinstance(abw_section_count(MINIMAL), int)


# --- abw_is_abw ---

def test_is_abw_minimal():
    assert abw_is_abw(MINIMAL) is True


def test_is_abw_empty():
    assert abw_is_abw(EMPTY) is True


def test_is_abw_returns_bool():
    assert isinstance(abw_is_abw(MINIMAL), bool)


# --- abw_has_content ---

def test_has_content_minimal():
    assert abw_has_content(MINIMAL) is True


def test_has_content_two():
    assert abw_has_content(TWO_PARA) is True


def test_has_content_empty():
    assert abw_has_content(EMPTY) is False


def test_has_content_returns_bool():
    assert isinstance(abw_has_content(MINIMAL), bool)


# --- abw_first_paragraph ---

def test_first_paragraph_minimal():
    assert abw_first_paragraph(MINIMAL) == "Hello"


def test_first_paragraph_two():
    assert abw_first_paragraph(TWO_PARA) == "First paragraph."


def test_first_paragraph_empty():
    assert abw_first_paragraph(EMPTY) == ""


def test_first_paragraph_returns_str():
    assert isinstance(abw_first_paragraph(MINIMAL), str)


# --- abw_total_word_count ---

def test_total_word_count_minimal():
    # 'Hello' => 1 word
    assert abw_total_word_count(MINIMAL) == 1


def test_total_word_count_two():
    # 'First paragraph.' + 'Second paragraph.' => 2+2=4 words
    assert abw_total_word_count(TWO_PARA) == 4


def test_total_word_count_empty():
    assert abw_total_word_count(EMPTY) == 0


def test_total_word_count_returns_int():
    assert isinstance(abw_total_word_count(MINIMAL), int)
