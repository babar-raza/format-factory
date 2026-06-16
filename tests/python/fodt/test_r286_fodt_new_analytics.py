"""Tests for 5 new FODT analytics functions.

Uses real sample files from samples/by-format/fodt/.
Covers: fodt_total_text_length, fodt_nonempty_paragraph_ratio,
    fodt_has_numeric_content, fodt_avg_sentence_length, fodt_longest_paragraph_index.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    fodt_total_text_length,
    fodt_nonempty_paragraph_ratio,
    fodt_has_numeric_content,
    fodt_avg_sentence_length,
    fodt_longest_paragraph_index,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
MINIMAL = _SAMPLES / "minimal-document.fodt"
HEADINGS = _SAMPLES / "headings-and-paragraphs.fodt"
TABLE = _SAMPLES / "table-basic.fodt"


class TestFodtTotalTextLength:
    def test_returns_int(self):
        result = fodt_total_text_length(MINIMAL)
        assert isinstance(result, int)

    def test_positive_for_data(self):
        result = fodt_total_text_length(MINIMAL)
        assert result > 0

    def test_headings_longer(self):
        r1 = fodt_total_text_length(MINIMAL)
        r2 = fodt_total_text_length(HEADINGS)
        assert r2 >= r1


class TestFodtNonemptyParagraphRatio:
    def test_returns_float(self):
        result = fodt_nonempty_paragraph_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = fodt_nonempty_paragraph_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_headings(self):
        result = fodt_nonempty_paragraph_ratio(HEADINGS)
        assert 0.0 <= result <= 1.0


class TestFodtHasNumericContent:
    def test_returns_bool(self):
        result = fodt_has_numeric_content(MINIMAL)
        assert isinstance(result, bool)

    def test_headings_file(self):
        result = fodt_has_numeric_content(HEADINGS)
        assert isinstance(result, bool)

    def test_table_file(self):
        result = fodt_has_numeric_content(TABLE)
        assert isinstance(result, bool)


class TestFodtAvgSentenceLength:
    def test_returns_float(self):
        result = fodt_avg_sentence_length(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = fodt_avg_sentence_length(MINIMAL)
        assert result >= 0.0

    def test_headings(self):
        result = fodt_avg_sentence_length(HEADINGS)
        assert isinstance(result, float)


class TestFodtLongestParagraphIndex:
    def test_returns_int(self):
        result = fodt_longest_paragraph_index(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg_for_data(self):
        result = fodt_longest_paragraph_index(MINIMAL)
        assert result >= 0

    def test_headings(self):
        result = fodt_longest_paragraph_index(HEADINGS)
        assert result >= 0
