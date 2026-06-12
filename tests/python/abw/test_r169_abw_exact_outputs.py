"""R169 — ABW exact-output tests for average_paragraph_length and shortest_paragraph."""
from __future__ import annotations

import pytest
from src.python.abw.abw_codec import average_paragraph_length, shortest_paragraph


class TestAverageParagraphLengthExact:
    def test_two_paragraphs_exact(self):
        model = {"paragraphs": ["abc", "abcde"]}  # lengths 3, 5 → avg 4.0
        assert average_paragraph_length(model) == pytest.approx(4.0)

    def test_three_paragraphs_exact(self):
        model = {"paragraphs": ["a", "ab", "abc"]}  # lengths 1, 2, 3 → avg 2.0
        assert average_paragraph_length(model) == pytest.approx(2.0)

    def test_all_same_length(self):
        model = {"paragraphs": ["abc", "xyz", "def"]}  # all length 3
        assert average_paragraph_length(model) == pytest.approx(3.0)


class TestShortestParagraphExact:
    def test_exact_shortest(self):
        model = {"paragraphs": ["hello world", "hi", "goodbye"]}
        assert shortest_paragraph(model) == "hi"

    def test_empty_string_is_shortest(self):
        model = {"paragraphs": ["", "abc", "de"]}
        assert shortest_paragraph(model) == ""

    def test_single_word_shortest(self):
        model = {"paragraphs": ["the quick brown fox", "fox", "a longer sentence here"]}
        assert shortest_paragraph(model) == "fox"
