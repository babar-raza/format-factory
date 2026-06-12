"""
tests/python/abw/test_r180_abw_sentence_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT48-001
Tests for abw_sentence_count() — approximate sentence count via punctuation.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_sentence_count, load

SAMPLES = _REPO / "samples" / "by-format" / "abw"


class TestAbwSentenceCount:
    def test_minimal_document_no_sentences(self):
        model = load(SAMPLES / "minimal-document.abw")
        result = abw_sentence_count(model)
        assert result == 0

    def test_two_paragraphs_two_sentences(self):
        model = load(SAMPLES / "two-paragraphs.abw")
        result = abw_sentence_count(model)
        assert result == 2

    def test_returns_int(self):
        model = load(SAMPLES / "minimal-document.abw")
        result = abw_sentence_count(model)
        assert isinstance(result, int)

    def test_non_negative(self):
        model = load(SAMPLES / "two-paragraphs.abw")
        result = abw_sentence_count(model)
        assert result >= 0

    def test_inline_model(self):
        model = {"paragraphs": ["Hello world! How are you? Fine."]}
        result = abw_sentence_count(model)
        assert result == 3

    def test_exported_from_init(self):
        from src.python.abw import abw_sentence_count as fn
        model = {"paragraphs": ["Test."]}
        assert fn(model) == 1
