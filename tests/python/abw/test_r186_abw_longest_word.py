"""
tests/python/abw/test_r186_abw_longest_word.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT54-001
Tests for abw_longest_word() — longest word across all paragraphs.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_longest_word, load

SAMPLES = _REPO / "samples" / "by-format" / "abw"


class TestAbwLongestWord:
    def test_minimal_document_returns_hello(self):
        model = load(SAMPLES / "minimal-document.abw")
        result = abw_longest_word(model)
        assert result == "Hello"

    def test_inline_model_longest_word(self):
        model = {"paragraphs": ["cat elephant dog"]}
        result = abw_longest_word(model)
        assert result == "elephant"

    def test_empty_paragraphs_returns_empty_string(self):
        model = {"paragraphs": []}
        result = abw_longest_word(model)
        assert result == ""

    def test_returns_string(self):
        model = load(SAMPLES / "minimal-document.abw")
        result = abw_longest_word(model)
        assert isinstance(result, str)

    def test_non_empty_result(self):
        model = {"paragraphs": ["Hello world"]}
        result = abw_longest_word(model)
        assert len(result) > 0

    def test_exported_from_init(self):
        from src.python.abw import abw_longest_word as fn
        model = {"paragraphs": ["short longer longest"]}
        result = fn(model)
        assert result == "longest"
