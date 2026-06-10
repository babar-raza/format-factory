"""Tests for ABW search_paragraph, get_word_count, search_replace_paragraph.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-2-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    search_paragraph,
    get_word_count,
    search_replace_paragraph,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_model():
    return create_abw(["Hello world", "Python is great", "Hello again", ""])


# ---------------------------------------------------------------------------
# search_paragraph
# ---------------------------------------------------------------------------

class TestSearchParagraph:
    def test_basic_match(self, simple_model):
        result = search_paragraph(simple_model, "Hello")
        assert result == [0, 2]

    def test_no_match(self, simple_model):
        result = search_paragraph(simple_model, "xyz_not_present")
        assert result == []

    def test_single_match(self, simple_model):
        result = search_paragraph(simple_model, "Python")
        assert result == [1]

    def test_empty_query_matches_all(self, simple_model):
        result = search_paragraph(simple_model, "")
        assert len(result) == 4  # all paragraphs contain empty string

    def test_case_sensitive_default(self, simple_model):
        result = search_paragraph(simple_model, "hello")
        assert result == []  # "Hello" != "hello" when case_sensitive=True

    def test_case_insensitive(self, simple_model):
        result = search_paragraph(simple_model, "hello", case_sensitive=False)
        assert result == [0, 2]

    def test_case_insensitive_no_match(self, simple_model):
        result = search_paragraph(simple_model, "xyz", case_sensitive=False)
        assert result == []

    def test_empty_document(self):
        model = create_abw([])
        result = search_paragraph(model, "anything")
        assert result == []

    def test_raises_on_non_dict_model(self):
        with pytest.raises(TypeError):
            search_paragraph(["not", "a", "dict"], "query")

    def test_raises_on_non_string_query(self, simple_model):
        with pytest.raises(TypeError):
            search_paragraph(simple_model, 42)

    def test_returns_list_of_ints(self, simple_model):
        result = search_paragraph(simple_model, "Hello")
        assert isinstance(result, list)
        assert all(isinstance(i, int) for i in result)

    def test_indices_are_zero_based(self):
        model = create_abw(["skip", "match here"])
        result = search_paragraph(model, "match")
        assert result == [1]


# ---------------------------------------------------------------------------
# get_word_count
# ---------------------------------------------------------------------------

class TestGetWordCount:
    def test_basic_count(self, simple_model):
        # "Hello world"=2, "Python is great"=3, "Hello again"=2, ""=0
        assert get_word_count(simple_model) == 7

    def test_empty_document(self):
        model = create_abw([])
        assert get_word_count(model) == 0

    def test_single_word(self):
        model = create_abw(["word"])
        assert get_word_count(model) == 1

    def test_empty_paragraph_contributes_zero(self):
        model = create_abw(["one two", "", "three"])
        assert get_word_count(model) == 3

    def test_multiple_spaces(self):
        model = create_abw(["  a  b  c  "])
        assert get_word_count(model) == 3

    def test_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            get_word_count("not a dict")

    def test_returns_int(self, simple_model):
        result = get_word_count(simple_model)
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# search_replace_paragraph
# ---------------------------------------------------------------------------

class TestSearchReplaceParagraph:
    def test_basic_replace(self, simple_model):
        new_model = search_replace_paragraph(simple_model, "Hello", "Hi")
        assert new_model["paragraphs"][0] == "Hi world"
        assert new_model["paragraphs"][2] == "Hi again"

    def test_does_not_mutate_original(self, simple_model):
        original_para = simple_model["paragraphs"][0]
        search_replace_paragraph(simple_model, "Hello", "Hi")
        assert simple_model["paragraphs"][0] == original_para

    def test_no_match_returns_unchanged(self, simple_model):
        new_model = search_replace_paragraph(simple_model, "notpresent", "X")
        assert new_model["paragraphs"] == simple_model["paragraphs"]

    def test_case_insensitive_replace(self, simple_model):
        new_model = search_replace_paragraph(
            simple_model, "hello", "Hi", case_sensitive=False
        )
        assert new_model["paragraphs"][0] == "Hi world"
        assert new_model["paragraphs"][2] == "Hi again"

    def test_empty_old_string_returns_copy(self, simple_model):
        new_model = search_replace_paragraph(simple_model, "", "X")
        assert new_model["paragraphs"] == simple_model["paragraphs"]

    def test_paragraph_count_updated(self):
        model = create_abw(["a", "b"])
        new_model = search_replace_paragraph(model, "a", "z")
        assert new_model["paragraph_count"] == 2

    def test_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            search_replace_paragraph("not a dict", "x", "y")

    def test_raises_on_non_string_old(self, simple_model):
        with pytest.raises(TypeError):
            search_replace_paragraph(simple_model, 42, "y")

    def test_raises_on_non_string_new(self, simple_model):
        with pytest.raises(TypeError):
            search_replace_paragraph(simple_model, "x", 42)

    def test_replace_all_occurrences_in_paragraph(self):
        model = create_abw(["the cat and the dog"])
        new_model = search_replace_paragraph(model, "the", "a")
        assert new_model["paragraphs"][0] == "a cat and a dog"
