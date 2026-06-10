"""Tests for get_unique_words() — ABW unique word extraction.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-ABW-UNIQUE-WORDS
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, get_unique_words


class TestGetUniqueWords:
    def test_basic_unique(self):
        model = create_abw(["Hello world", "hello again"])
        words = get_unique_words(model)
        assert "hello" in words
        assert "world" in words
        assert "again" in words

    def test_sorted(self):
        model = create_abw(["zebra apple mango"])
        words = get_unique_words(model)
        assert words == sorted(words)

    def test_no_duplicates(self):
        model = create_abw(["cat cat cat", "dog dog"])
        words = get_unique_words(model)
        assert words.count("cat") == 1
        assert words.count("dog") == 1

    def test_empty_model(self):
        model = create_abw([])
        assert get_unique_words(model) == []

    def test_single_paragraph(self):
        model = create_abw(["one two three"])
        words = get_unique_words(model)
        assert set(words) == {"one", "two", "three"}

    def test_lowercase_normalization(self):
        model = create_abw(["Hello HELLO hello"])
        words = get_unique_words(model)
        assert words == ["hello"]

    def test_multiple_paragraphs(self):
        model = create_abw(["alpha beta", "gamma delta"])
        words = get_unique_words(model)
        assert "alpha" in words
        assert "gamma" in words
        assert len(words) == 4

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            get_unique_words("not a dict")

    def test_returns_list(self):
        model = create_abw(["hello"])
        assert isinstance(get_unique_words(model), list)

    def test_whitespace_only_paragraph(self):
        model = {"is_abw": True, "section_count": 0, "paragraph_count": 1, "paragraphs": ["   "]}
        assert get_unique_words(model) == []
