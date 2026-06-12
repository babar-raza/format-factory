"""R169 — ABW average_paragraph_length and shortest_paragraph tests."""
from __future__ import annotations

import pytest

from src.python.abw.abw_codec import average_paragraph_length, shortest_paragraph


class TestAverageParagraphLength:
    def test_returns_float(self):
        model = {"paragraphs": ["hello", "world"]}
        assert isinstance(average_paragraph_length(model), float)

    def test_average_correct(self):
        model = {"paragraphs": ["ab", "abcd"]}  # lengths 2 and 4
        result = average_paragraph_length(model)
        assert result == pytest.approx(3.0)

    def test_single_paragraph(self):
        model = {"paragraphs": ["hello"]}
        assert average_paragraph_length(model) == pytest.approx(5.0)

    def test_empty_paragraphs_returns_zero(self):
        model = {"paragraphs": []}
        assert average_paragraph_length(model) == 0.0

    def test_no_paragraphs_key_returns_zero(self):
        model = {}
        assert average_paragraph_length(model) == 0.0

    def test_non_dict_returns_zero(self):
        assert average_paragraph_length("not a dict") == 0.0

    def test_longer_paragraphs(self):
        model = {"paragraphs": ["a" * 10, "b" * 20, "c" * 30]}
        result = average_paragraph_length(model)
        assert result == pytest.approx(20.0)

    def test_empty_string_paragraphs(self):
        model = {"paragraphs": ["", ""]}
        assert average_paragraph_length(model) == 0.0


class TestShortestParagraph:
    def test_returns_string(self):
        model = {"paragraphs": ["hello", "hi"]}
        assert isinstance(shortest_paragraph(model), str)

    def test_returns_shortest(self):
        model = {"paragraphs": ["medium text", "hi", "the longest paragraph here"]}
        assert shortest_paragraph(model) == "hi"

    def test_single_paragraph(self):
        model = {"paragraphs": ["only one"]}
        assert shortest_paragraph(model) == "only one"

    def test_empty_paragraphs_returns_empty(self):
        model = {"paragraphs": []}
        assert shortest_paragraph(model) == ""

    def test_no_paragraphs_key_returns_empty(self):
        model = {}
        assert shortest_paragraph(model) == ""

    def test_non_dict_returns_empty(self):
        assert shortest_paragraph("not a dict") == ""

    def test_tied_returns_first(self):
        model = {"paragraphs": ["abc", "xyz"]}
        result = shortest_paragraph(model)
        assert len(result) == 3

    def test_empty_string_as_shortest(self):
        model = {"paragraphs": ["", "hello", "world"]}
        assert shortest_paragraph(model) == ""
