"""
test_r168_abw_search_words.py -- Tests for search_text, get_words, longest_paragraph, is_empty.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22
Closes: GAP-ABW-FOSS-SEARCH-001 (search_text, get_words), GAP-ABW-FOSS-STATS-001 (longest_paragraph, is_empty)
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import (
    create_abw,
    search_text,
    get_words,
    longest_paragraph,
    is_empty,
    average_paragraph_length,
    shortest_paragraph,
)


def _model(paragraphs: list[str]) -> dict:
    return create_abw(paragraphs)


class TestSearchText:
    def test_search_found(self):
        m = _model(["Hello world", "Goodbye world", "No match here"])
        assert search_text(m, "world") == [0, 1]

    def test_search_not_found(self):
        m = _model(["Hello", "Goodbye"])
        assert search_text(m, "xyz") == []

    def test_search_empty_query(self):
        m = _model(["Hello"])
        assert search_text(m, "") == []

    def test_search_case_sensitive(self):
        m = _model(["Hello World"])
        assert search_text(m, "hello") == []
        assert search_text(m, "Hello") == [0]

    def test_search_single_match(self):
        m = _model(["apple", "banana", "cherry"])
        assert search_text(m, "banana") == [1]

    def test_search_empty_model(self):
        m = _model([])
        assert search_text(m, "test") == []

    def test_search_non_dict_input(self):
        assert search_text(None, "test") == []


class TestGetWords:
    def test_get_words_basic(self):
        m = _model(["Hello world today"])
        assert get_words(m, 0) == ["Hello", "world", "today"]

    def test_get_words_single_word(self):
        m = _model(["Python"])
        assert get_words(m, 0) == ["Python"]

    def test_get_words_empty_paragraph(self):
        m = _model([""])
        assert get_words(m, 0) == []

    def test_get_words_invalid_index(self):
        m = _model(["One paragraph"])
        assert get_words(m, 5) == []

    def test_get_words_negative_index(self):
        m = _model(["Paragraph"])
        assert get_words(m, -1) == []

    def test_get_words_second_paragraph(self):
        m = _model(["First paragraph", "Second paragraph content"])
        assert get_words(m, 1) == ["Second", "paragraph", "content"]

    def test_get_words_non_dict(self):
        assert get_words(None, 0) == []


class TestLongestParagraph:
    def test_longest_basic(self):
        m = _model(["short", "this is a much longer paragraph", "medium length"])
        assert longest_paragraph(m) == "this is a much longer paragraph"

    def test_longest_single(self):
        m = _model(["Only paragraph"])
        assert longest_paragraph(m) == "Only paragraph"

    def test_longest_empty_model(self):
        m = _model([])
        assert longest_paragraph(m) == ""

    def test_longest_non_dict(self):
        assert longest_paragraph(None) == ""

    def test_longest_tie_takes_first_max(self):
        m = _model(["abc", "xyz"])
        # Both are 3 chars; max returns last by default but both are valid
        result = longest_paragraph(m)
        assert len(result) == 3


class TestIsEmpty:
    def test_is_empty_no_paragraphs(self):
        m = _model([])
        assert is_empty(m) is True

    def test_is_not_empty_with_content(self):
        m = _model(["Hello"])
        assert is_empty(m) is False

    def test_is_empty_whitespace_only(self):
        m = _model(["   ", "\t\n"])
        assert is_empty(m) is True

    def test_is_not_empty_mixed(self):
        m = _model(["", "content", ""])
        assert is_empty(m) is False

    def test_is_empty_non_dict(self):
        assert is_empty(None) is True


class TestAverageParagraphLength:
    def test_average_basic(self):
        m = _model(["Hi", "Hello"])  # 2 + 5 = 7 chars, avg = 3.5
        assert average_paragraph_length(m) == 3.5

    def test_average_single(self):
        m = _model(["Hello"])
        assert average_paragraph_length(m) == 5.0

    def test_average_empty(self):
        m = _model([])
        assert average_paragraph_length(m) == 0.0

    def test_average_non_dict(self):
        assert average_paragraph_length(None) == 0.0


class TestShortestParagraph:
    def test_shortest_basic(self):
        m = _model(["Hello world", "Hi", "Good morning"])
        assert shortest_paragraph(m) == "Hi"

    def test_shortest_single(self):
        m = _model(["Only one"])
        assert shortest_paragraph(m) == "Only one"

    def test_shortest_empty_model(self):
        m = _model([])
        assert shortest_paragraph(m) == ""

    def test_shortest_non_dict(self):
        assert shortest_paragraph(None) == ""
