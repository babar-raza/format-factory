"""Tests for 6 new ODT analytics functions.

Uses real sample files from samples/by-format/odt/valid/.
Covers: odt_total_text_length, odt_nonempty_paragraph_ratio,
    odt_avg_sentence_length, odt_longest_paragraph_index,
    odt_has_numeric_content, odt_numeric_value_sum.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt import (
    odt_avg_sentence_length,
    odt_has_numeric_content,
    odt_longest_paragraph_index,
    odt_nonempty_paragraph_ratio,
    odt_numeric_value_sum,
    odt_total_text_length,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
MINIMAL = _SAMPLES / "minimal-document.odt"
TWO_PARA = _SAMPLES / "two-paragraphs.odt"
UNICODE = _SAMPLES / "unicode-text.odt"


class TestOdtTotalTextLength:
    def test_returns_int(self):
        result = odt_total_text_length(MINIMAL)
        assert isinstance(result, int)

    def test_positive_for_data(self):
        result = odt_total_text_length(MINIMAL)
        assert result > 0

    def test_two_para_longer_than_minimal(self):
        result1 = odt_total_text_length(MINIMAL)
        result2 = odt_total_text_length(TWO_PARA)
        assert result2 >= result1


class TestOdtNonemptyParagraphRatio:
    def test_returns_float(self):
        result = odt_nonempty_paragraph_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = odt_nonempty_paragraph_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_positive_for_data(self):
        result = odt_nonempty_paragraph_ratio(MINIMAL)
        assert result > 0.0


class TestOdtAvgSentenceLength:
    def test_returns_float(self):
        result = odt_avg_sentence_length(MINIMAL)
        assert isinstance(result, float)

    def test_nonnegative(self):
        result = odt_avg_sentence_length(MINIMAL)
        assert result >= 0.0

    def test_two_para(self):
        result = odt_avg_sentence_length(TWO_PARA)
        assert isinstance(result, float)


class TestOdtLongestParagraphIndex:
    def test_returns_int(self):
        result = odt_longest_paragraph_index(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg_for_data(self):
        result = odt_longest_paragraph_index(MINIMAL)
        assert result >= 0

    def test_two_para_valid_index(self):
        result = odt_longest_paragraph_index(TWO_PARA)
        assert result >= 0


class TestOdtHasNumericContent:
    def test_returns_bool(self):
        result = odt_has_numeric_content(MINIMAL)
        assert isinstance(result, bool)

    def test_consistent_type(self):
        assert isinstance(odt_has_numeric_content(TWO_PARA), bool)


class TestOdtNumericValueSum:
    def test_returns_float(self):
        result = odt_numeric_value_sum(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = odt_numeric_value_sum(MINIMAL)
        assert result >= 0.0

    def test_two_para(self):
        result = odt_numeric_value_sum(TWO_PARA)
        assert isinstance(result, float)
