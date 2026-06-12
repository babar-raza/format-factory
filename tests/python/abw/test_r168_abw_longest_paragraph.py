"""R168 — ABW longest_paragraph tests.

Queue: sprint4-q-003
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.abw.abw_codec import load, longest_paragraph


class TestLongestParagraph:
    def test_returns_string(self):
        model = {"paragraphs": ["hello", "world longer paragraph"]}
        result = longest_paragraph(model)
        assert isinstance(result, str)

    def test_returns_longest(self):
        model = {"paragraphs": ["short", "much longer paragraph here", "medium text"]}
        result = longest_paragraph(model)
        assert result == "much longer paragraph here"

    def test_single_paragraph(self):
        model = {"paragraphs": ["only one"]}
        assert longest_paragraph(model) == "only one"

    def test_empty_paragraphs_list(self):
        model = {"paragraphs": []}
        assert longest_paragraph(model) == ""

    def test_no_paragraphs_key(self):
        model = {}
        assert longest_paragraph(model) == ""

    def test_non_dict_input(self):
        assert longest_paragraph("not a dict") == ""

    def test_with_real_file(self):
        model = load(Path("examples/python/abw/sample_meeting_notes.abw"))
        result = longest_paragraph(model)
        assert isinstance(result, str)
        assert len(result) >= 0

    def test_tied_returns_one(self):
        model = {"paragraphs": ["abc", "xyz"]}
        result = longest_paragraph(model)
        assert len(result) == 3
