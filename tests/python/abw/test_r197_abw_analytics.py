"""
tests/python/abw/test_r197_abw_analytics.py

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
Tests for abw_sentence_count(), abw_longest_word(), abw_total_char_count(),
first_paragraph(), last_paragraph(), longest_paragraph(), has_paragraph().
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    load,
    abw_sentence_count,
    abw_longest_word,
    abw_total_char_count,
    first_paragraph,
    last_paragraph,
    longest_paragraph,
    has_paragraph,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_TWO_PARA = str(_SAMPLES / "two-paragraphs.abw")
_MINIMAL = str(_SAMPLES / "minimal-document.abw")


class TestAbwSentenceCount:
    def test_empty_model_returns_zero(self):
        model = {"paragraphs": []}
        assert abw_sentence_count(model) == 0

    def test_returns_int(self):
        model = load(_TWO_PARA)
        result = abw_sentence_count(model)
        assert isinstance(result, int)

    def test_two_sentences_counted(self):
        model = load(_TWO_PARA)
        result = abw_sentence_count(model)
        assert result >= 2

    def test_non_negative(self):
        model = load(_MINIMAL)
        assert abw_sentence_count(model) >= 0


class TestAbwLongestWord:
    def test_empty_model_returns_empty_string(self):
        model = {"paragraphs": []}
        result = abw_longest_word(model)
        assert result == ""

    def test_returns_string(self):
        model = load(_TWO_PARA)
        result = abw_longest_word(model)
        assert isinstance(result, str)

    def test_real_file_returns_non_empty(self):
        model = load(_TWO_PARA)
        result = abw_longest_word(model)
        assert len(result) > 0


class TestAbwTotalCharCount:
    def test_real_file_returns_positive_int(self):
        result = abw_total_char_count(_TWO_PARA)
        assert isinstance(result, int)
        assert result > 0

    def test_returns_integer(self):
        result = abw_total_char_count(_TWO_PARA)
        assert isinstance(result, int)


class TestAbwParagraphAccessors:
    def test_first_paragraph_returns_string(self):
        model = load(_TWO_PARA)
        result = first_paragraph(model)
        assert isinstance(result, str)

    def test_last_paragraph_returns_string(self):
        model = load(_TWO_PARA)
        result = last_paragraph(model)
        assert isinstance(result, str)

    def test_first_and_last_are_different(self):
        model = load(_TWO_PARA)
        assert first_paragraph(model) != last_paragraph(model)

    def test_longest_paragraph_returns_string(self):
        model = load(_TWO_PARA)
        result = longest_paragraph(model)
        assert isinstance(result, str)

    def test_has_paragraph_exact_match_found(self):
        model = load(_TWO_PARA)
        fp = first_paragraph(model)
        assert has_paragraph(model, fp) is True

    def test_has_paragraph_missing_returns_false(self):
        model = load(_TWO_PARA)
        assert has_paragraph(model, "DEFINITELY_NOT_IN_FILE_xyz123") is False
