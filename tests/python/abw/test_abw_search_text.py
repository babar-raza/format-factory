"""
tests/python/abw/test_abw_search_text.py
Tests for search_text() added via QUEUE_DISPATCHED_EXECUTION.

Sprint: FORMAT-FACTORY-SELF-HEALING-QUEUE-PROFESSIONALIZE-RNEXT-001
Queue item: anl-q-001
"""

from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import search_text


MODEL = {
    "paragraphs": [
        "Hello world, this is a test.",
        "ABW codec handles AbiWord documents.",
        "Queue-dispatched execution proved here.",
        "Hello again, second occurrence.",
        "",
    ]
}


class TestSearchText:
    def test_returns_list(self) -> None:
        result = search_text(MODEL, "Hello")
        assert isinstance(result, list)

    def test_finds_single_match(self) -> None:
        result = search_text(MODEL, "ABW codec")
        assert result == [1]

    def test_finds_multiple_matches(self) -> None:
        result = search_text(MODEL, "Hello")
        assert 0 in result
        assert 3 in result
        assert len(result) == 2

    def test_no_match_returns_empty(self) -> None:
        result = search_text(MODEL, "nonexistent_xyz_token")
        assert result == []

    def test_empty_query_returns_empty(self) -> None:
        result = search_text(MODEL, "")
        assert result == []

    def test_case_sensitive(self) -> None:
        result_lower = search_text(MODEL, "hello")
        result_upper = search_text(MODEL, "Hello")
        assert result_lower != result_upper
        assert result_lower == []

    def test_non_dict_model_returns_empty(self) -> None:
        assert search_text([], "Hello") == []
        assert search_text(None, "Hello") == []
        assert search_text("string", "Hello") == []

    def test_empty_paragraphs_returns_empty(self) -> None:
        result = search_text({"paragraphs": []}, "Hello")
        assert result == []

    def test_model_without_paragraphs_returns_empty(self) -> None:
        result = search_text({}, "Hello")
        assert result == []

    def test_returns_sorted_indices(self) -> None:
        result = search_text(MODEL, "Hello")
        assert result == sorted(result)

    def test_finds_in_empty_paragraph(self) -> None:
        # Empty string contains empty string — but we short-circuit on empty query
        result = search_text({"paragraphs": ["", "a"]}, "a")
        assert result == [1]

    def test_partial_word_match(self) -> None:
        result = search_text(MODEL, "queue")
        assert result == []  # "Queue" with capital Q
        result2 = search_text(MODEL, "Queue")
        assert 2 in result2
