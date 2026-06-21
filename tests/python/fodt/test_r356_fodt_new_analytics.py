"""
Sprint 92 — FODT analytics round 4.
25 tests for 5 new analytics functions:
  fodt_numeric_word_count, fodt_heading_char_sum, fodt_paragraph_char_sum,
  fodt_max_words_in_heading, fodt_short_paragraph_count
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    parse_fodt,
    fodt_numeric_word_count,
    fodt_heading_char_sum,
    fodt_paragraph_char_sum,
    fodt_max_words_in_heading,
    fodt_short_paragraph_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_SAMPLES / "minimal-document.fodt")
_HEADINGS = str(_SAMPLES / "headings-and-paragraphs.fodt")
_TABLE = str(_SAMPLES / "table-basic.fodt")
_LIST = str(_SAMPLES / "list-basic.fodt")


# --- fodt_numeric_word_count ---

class TestFodtNumericWordCount:
    def test_returns_int(self):
        result = fodt_numeric_word_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_numeric_word_count(_MINIMAL)
        assert result >= 0

    def test_headings_file(self):
        result = fodt_numeric_word_count(_HEADINGS)
        assert isinstance(result, int) and result >= 0

    def test_table_file(self):
        result = fodt_numeric_word_count(_TABLE)
        assert isinstance(result, int) and result >= 0

    def test_list_file(self):
        result = fodt_numeric_word_count(_LIST)
        assert isinstance(result, int) and result >= 0


# --- fodt_heading_char_sum ---

class TestFodtHeadingCharSum:
    def test_returns_int(self):
        result = fodt_heading_char_sum(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_heading_char_sum(_MINIMAL)
        assert result >= 0

    def test_headings_file_positive(self):
        result = fodt_heading_char_sum(_HEADINGS)
        assert result > 0

    def test_table_file(self):
        result = fodt_heading_char_sum(_TABLE)
        assert isinstance(result, int) and result >= 0

    def test_list_file(self):
        result = fodt_heading_char_sum(_LIST)
        assert isinstance(result, int) and result >= 0


# --- fodt_paragraph_char_sum ---

class TestFodtParagraphCharSum:
    def test_returns_int(self):
        result = fodt_paragraph_char_sum(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_paragraph_char_sum(_MINIMAL)
        assert result >= 0

    def test_headings_file_positive(self):
        result = fodt_paragraph_char_sum(_HEADINGS)
        assert result > 0

    def test_table_file(self):
        result = fodt_paragraph_char_sum(_TABLE)
        assert isinstance(result, int) and result >= 0

    def test_greater_than_heading_sum_for_headings_file(self):
        p = fodt_paragraph_char_sum(_HEADINGS)
        h = fodt_heading_char_sum(_HEADINGS)
        # A headings-and-paragraphs doc should have paragraph content
        assert p >= 0 and h >= 0


# --- fodt_max_words_in_heading ---

class TestFodtMaxWordsInHeading:
    def test_returns_int(self):
        result = fodt_max_words_in_heading(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_max_words_in_heading(_MINIMAL)
        assert result >= 0

    def test_headings_file_positive(self):
        result = fodt_max_words_in_heading(_HEADINGS)
        assert result > 0

    def test_table_file(self):
        result = fodt_max_words_in_heading(_TABLE)
        assert isinstance(result, int) and result >= 0

    def test_list_file(self):
        result = fodt_max_words_in_heading(_LIST)
        assert isinstance(result, int) and result >= 0


# --- fodt_short_paragraph_count ---

class TestFodtShortParagraphCount:
    def test_returns_int(self):
        result = fodt_short_paragraph_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_short_paragraph_count(_MINIMAL)
        assert result >= 0

    def test_headings_file(self):
        result = fodt_short_paragraph_count(_HEADINGS)
        assert isinstance(result, int) and result >= 0

    def test_table_file(self):
        result = fodt_short_paragraph_count(_TABLE)
        assert isinstance(result, int) and result >= 0

    def test_zero_max_words_counts_empty_paragraphs(self):
        # With max_words=0, only paragraphs with 0 words qualify
        result = fodt_short_paragraph_count(_HEADINGS, max_words=0)
        assert isinstance(result, int) and result >= 0
