"""
test_r176_abw_count_paragraphs_matching.py

Sprint: FORMAT-FACTORY-PRODUCT-ADVANCE-GOVERNANCE-DURABILITY-001
Added: 2026-06-12

Tests for ABW count_paragraphs_matching function.
Closes gap: GAP-ABW-COUNT-PARAGRAPHS-MATCHING-001
Authority: QUEUE_DISPATCHED_EXECUTION
spec_fact_refs: ABW-FOSS-LOAD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import count_paragraphs_matching


def _make_model(paragraphs):
    return {"paragraphs": paragraphs, "format": "abw"}


class TestCountParagraphsMatching:

    def test_returns_int(self):
        model = _make_model(["hello world", "goodbye"])
        result = count_paragraphs_matching(model, "hello")
        assert isinstance(result, int)

    def test_single_match(self):
        model = _make_model(["hello world", "goodbye", "nothing"])
        assert count_paragraphs_matching(model, "hello") == 1

    def test_multiple_matches(self):
        model = _make_model(["cats and dogs", "I love cats", "no animals here"])
        assert count_paragraphs_matching(model, "cats") == 2

    def test_zero_matches(self):
        model = _make_model(["hello world", "goodbye world"])
        assert count_paragraphs_matching(model, "python") == 0

    def test_all_paragraphs_match(self):
        model = _make_model(["abc 123", "abc xyz", "start abc end"])
        assert count_paragraphs_matching(model, "abc") == 3

    def test_empty_paragraphs(self):
        model = _make_model([])
        assert count_paragraphs_matching(model, "hello") == 0

    def test_case_sensitive_default(self):
        model = _make_model(["Hello World", "hello world"])
        # case_sensitive=True by default — "Hello" != "hello"
        assert count_paragraphs_matching(model, "Hello") == 1
        assert count_paragraphs_matching(model, "HELLO") == 0

    def test_case_insensitive(self):
        model = _make_model(["Hello World", "HELLO there", "world"])
        result = count_paragraphs_matching(model, "hello", case_sensitive=False)
        assert result == 2

    def test_empty_pattern_matches_all(self):
        model = _make_model(["para one", "para two", "para three"])
        # empty string is a substring of every string
        assert count_paragraphs_matching(model, "") == 3

    def test_invalid_model_returns_zero(self):
        assert count_paragraphs_matching(None, "test") == 0
        assert count_paragraphs_matching("not a dict", "test") == 0
        assert count_paragraphs_matching(42, "test") == 0

    def test_missing_paragraphs_key(self):
        model = {"format": "abw"}
        assert count_paragraphs_matching(model, "test") == 0

    def test_exact_substring_not_equal(self):
        model = _make_model(["The quick brown fox"])
        assert count_paragraphs_matching(model, "quick brown") == 1
        assert count_paragraphs_matching(model, "quick  brown") == 0  # double space

    def test_single_paragraph_match(self):
        model = _make_model(["only paragraph here"])
        assert count_paragraphs_matching(model, "only paragraph") == 1
        assert count_paragraphs_matching(model, "missing") == 0

    def test_unicode_pattern(self):
        model = _make_model(["中文内容", "English text", "混合 mixed"])
        assert count_paragraphs_matching(model, "中文") == 1
        assert count_paragraphs_matching(model, "mixed") == 1

    def test_numeric_pattern(self):
        model = _make_model(["value is 42", "value is 100", "no number here"])
        assert count_paragraphs_matching(model, "42") == 1

    def test_non_string_paragraphs_handled(self):
        model = _make_model([123, "hello 123", None])
        # Non-string paragraphs are str()-converted
        result = count_paragraphs_matching(model, "123")
        assert result == 2  # "123" and "hello 123" both match
