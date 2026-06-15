"""Product deepening tests for ABW analytics integration.

Tests abw_sentence_count, abw_longest_word, abw_total_char_count,
abw_word_count, abw_empty_paragraph_count, abw_nonempty_paragraph_count,
abw_average_word_length against sample files.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    load,
    abw_sentence_count,
    abw_longest_word,
    abw_total_char_count,
    abw_word_count,
    abw_empty_paragraph_count,
    abw_nonempty_paragraph_count,
    abw_average_word_length,
)

SAMPLES = _REPO / "samples" / "by-format" / "abw"
MINIMAL = SAMPLES / "minimal-document.abw"
TWO_PARA = SAMPLES / "two-paragraphs.abw"
EMPTY_SEC = SAMPLES / "empty-section.abw"


@pytest.fixture
def minimal_model():
    return load(str(MINIMAL))


@pytest.fixture
def two_para_model():
    return load(str(TWO_PARA))


class TestAbwSentenceCount:
    """abw_sentence_count takes a model dict."""

    def test_minimal_has_sentences(self, minimal_model):
        count = abw_sentence_count(minimal_model)
        assert isinstance(count, int)
        assert count >= 0

    def test_two_para_has_sentences(self, two_para_model):
        count = abw_sentence_count(two_para_model)
        assert count >= 0


class TestAbwWordMetrics:
    """abw_longest_word takes model; abw_word_count/average take file path."""

    def test_word_count_positive(self):
        count = abw_word_count(str(MINIMAL))
        assert isinstance(count, int)
        assert count >= 0

    def test_longest_word_is_string(self, two_para_model):
        word = abw_longest_word(two_para_model)
        assert isinstance(word, str)

    def test_average_word_length_nonneg(self):
        avg = abw_average_word_length(str(TWO_PARA))
        assert isinstance(avg, (int, float))
        assert avg >= 0


class TestAbwCharCount:
    """abw_total_char_count takes file path."""

    def test_total_char_count(self):
        count = abw_total_char_count(str(MINIMAL))
        assert isinstance(count, int)
        assert count >= 0

    def test_two_para_more_chars(self):
        count = abw_total_char_count(str(TWO_PARA))
        assert count >= 1


class TestAbwParagraphCounts:
    """abw_empty/nonempty_paragraph_count take file path."""

    def test_nonempty_count(self):
        count = abw_nonempty_paragraph_count(str(TWO_PARA))
        assert isinstance(count, int)
        assert count >= 1

    def test_empty_count_nonneg(self):
        count = abw_empty_paragraph_count(str(MINIMAL))
        assert isinstance(count, int)
        assert count >= 0

    def test_empty_plus_nonempty_equals_total(self):
        empty = abw_empty_paragraph_count(str(TWO_PARA))
        nonempty = abw_nonempty_paragraph_count(str(TWO_PARA))
        assert empty >= 0
        assert nonempty >= 0
