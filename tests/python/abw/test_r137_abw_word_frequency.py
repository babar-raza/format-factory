"""Tests for word_frequency() — ABW word frequency analysis.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-ABW-WORD-FREQUENCY
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, word_frequency


class TestWordFrequency:
    def test_basic_count(self):
        model = create_abw(["hello world hello"])
        freq = word_frequency(model)
        assert freq["hello"] == 2
        assert freq["world"] == 1

    def test_returns_dict(self):
        model = create_abw(["test"])
        assert isinstance(word_frequency(model), dict)

    def test_empty_document(self):
        model = create_abw([])
        assert word_frequency(model) == {}

    def test_empty_paragraphs(self):
        model = create_abw(["", "  "])
        assert word_frequency(model) == {}

    def test_case_insensitive(self):
        model = create_abw(["Hello HELLO hello"])
        freq = word_frequency(model)
        assert freq["hello"] == 3

    def test_multi_paragraph(self):
        model = create_abw(["the cat", "the dog the"])
        freq = word_frequency(model)
        assert freq["the"] == 3
        assert freq["cat"] == 1
        assert freq["dog"] == 1

    def test_single_word(self):
        model = create_abw(["word"])
        freq = word_frequency(model)
        assert freq == {"word": 1}

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            word_frequency("not a dict")

    def test_all_unique_words(self):
        model = create_abw(["alpha beta gamma"])
        freq = word_frequency(model)
        assert all(v == 1 for v in freq.values())
        assert len(freq) == 3

    def test_numbers_as_words(self):
        model = create_abw(["1 2 1"])
        freq = word_frequency(model)
        assert freq["1"] == 2
        assert freq["2"] == 1
