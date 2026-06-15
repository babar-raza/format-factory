"""
test_rnext_abw_search_replace_paragraph.py -- Dedicated test coverage for search_replace_paragraph.

Gap: GAP-ABW-FOSS-SEARCH_REPLA-001 (missing_test_coverage)
Tests: edge cases, case-insensitive mode, type errors, empty model, no-match, multi-occurrence.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    search_replace_paragraph,
)


def _model(*paragraphs: str) -> dict:
    return create_abw(list(paragraphs))


class TestSearchReplaceParagraphCore:
    def test_basic_replace(self):
        m = _model("Hello World")
        m2 = search_replace_paragraph(m, "World", "Earth")
        assert m2["paragraphs"][0] == "Hello Earth"

    def test_no_match_returns_unchanged(self):
        m = _model("Hello World")
        m2 = search_replace_paragraph(m, "Mars", "Venus")
        assert m2["paragraphs"][0] == "Hello World"

    def test_multiple_paragraphs_replaced(self):
        m = _model("aXb", "cXd", "eXf")
        m2 = search_replace_paragraph(m, "X", "Y")
        assert m2["paragraphs"] == ["aYb", "cYd", "eYf"]

    def test_multiple_occurrences_in_one_paragraph(self):
        m = _model("aa bb aa cc aa")
        m2 = search_replace_paragraph(m, "aa", "ZZ")
        assert m2["paragraphs"][0] == "ZZ bb ZZ cc ZZ"

    def test_replace_with_empty_string(self):
        m = _model("Hello World")
        m2 = search_replace_paragraph(m, "World", "")
        assert m2["paragraphs"][0] == "Hello "

    def test_empty_old_string_returns_copy(self):
        m = _model("Hello")
        m2 = search_replace_paragraph(m, "", "X")
        assert m2["paragraphs"][0] == "Hello"
        assert m2 is not m

    def test_empty_paragraphs(self):
        m = _model()
        m2 = search_replace_paragraph(m, "x", "y")
        assert m2["paragraphs"] == []

    def test_returns_new_model_immutable(self):
        m = _model("Hello")
        m2 = search_replace_paragraph(m, "Hello", "Bye")
        assert m["paragraphs"][0] == "Hello"
        assert m2["paragraphs"][0] == "Bye"


class TestSearchReplaceCaseInsensitive:
    def test_case_insensitive_replace(self):
        m = _model("Hello HELLO hello")
        m2 = search_replace_paragraph(m, "hello", "HI", case_sensitive=False)
        lo = m2["paragraphs"][0].lower()
        assert "hello" not in lo

    def test_case_sensitive_by_default(self):
        m = _model("Hello HELLO hello")
        m2 = search_replace_paragraph(m, "HELLO", "X")
        assert "Hello" in m2["paragraphs"][0]
        assert "X" in m2["paragraphs"][0]


class TestSearchReplaceErrors:
    def test_model_not_dict_raises(self):
        with pytest.raises(TypeError):
            search_replace_paragraph("not a dict", "a", "b")

    def test_old_not_str_raises(self):
        m = _model("Hello")
        with pytest.raises(TypeError):
            search_replace_paragraph(m, 123, "b")

    def test_new_not_str_raises(self):
        m = _model("Hello")
        with pytest.raises(TypeError):
            search_replace_paragraph(m, "a", 123)
