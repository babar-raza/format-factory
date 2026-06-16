"""Tests for 5 new ABW analytics functions.

Uses real sample files from samples/by-format/abw/.
Covers: abw_total_text_length, abw_nonempty_paragraph_ratio,
    abw_has_numeric_content, abw_avg_sentence_length, abw_longest_paragraph_index.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_total_text_length,
    abw_nonempty_paragraph_ratio,
    abw_has_numeric_content,
    abw_avg_sentence_length,
    abw_longest_paragraph_index,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
MINIMAL = _SAMPLES / "minimal-document.abw"
TWO_PARA = _SAMPLES / "two-paragraphs.abw"
EMPTY = _SAMPLES / "empty-section.abw"


class TestAbwTotalTextLength:
    def test_returns_int(self):
        result = abw_total_text_length(MINIMAL)
        assert isinstance(result, int)

    def test_positive_for_data(self):
        result = abw_total_text_length(MINIMAL)
        assert result >= 0

    def test_two_para_longer_or_equal(self):
        r1 = abw_total_text_length(MINIMAL)
        r2 = abw_total_text_length(TWO_PARA)
        assert r2 >= r1

    def test_empty_nonneg(self):
        result = abw_total_text_length(EMPTY)
        assert result >= 0


class TestAbwNonemptyParagraphRatio:
    def test_returns_float(self):
        result = abw_nonempty_paragraph_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = abw_nonempty_paragraph_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_two_para(self):
        result = abw_nonempty_paragraph_ratio(TWO_PARA)
        assert 0.0 <= result <= 1.0


class TestAbwHasNumericContent:
    def test_returns_bool(self):
        result = abw_has_numeric_content(MINIMAL)
        assert isinstance(result, bool)

    def test_two_para(self):
        result = abw_has_numeric_content(TWO_PARA)
        assert isinstance(result, bool)

    def test_empty(self):
        result = abw_has_numeric_content(EMPTY)
        assert isinstance(result, bool)


class TestAbwAvgSentenceLength:
    def test_returns_float(self):
        result = abw_avg_sentence_length(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = abw_avg_sentence_length(MINIMAL)
        assert result >= 0.0

    def test_two_para(self):
        result = abw_avg_sentence_length(TWO_PARA)
        assert isinstance(result, float)


class TestAbwLongestParagraphIndex:
    def test_returns_int(self):
        result = abw_longest_paragraph_index(MINIMAL)
        assert isinstance(result, int)

    def test_two_para_valid(self):
        result = abw_longest_paragraph_index(TWO_PARA)
        assert result >= 0

    def test_consistent_type(self):
        result = abw_longest_paragraph_index(EMPTY)
        assert isinstance(result, int)
