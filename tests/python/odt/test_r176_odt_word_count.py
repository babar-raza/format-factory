"""
tests/python/odt/test_r176_odt_word_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT44-001
Tests for odt_word_count() — word count across all elements in an ODT file.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_word_count

SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdtWordCount:
    def test_minimal_document_word_count(self):
        # "Hello, world." -> 2 words
        result = odt_word_count(SAMPLES / "minimal-document.odt")
        assert result == 2

    def test_two_paragraphs_word_count(self):
        # "First paragraph." (2) + "Second paragraph." (2) -> 4 words
        result = odt_word_count(SAMPLES / "two-paragraphs.odt")
        assert result == 4

    def test_unicode_text_word_count(self):
        # "Café 中文 élève" -> 3 words
        result = odt_word_count(SAMPLES / "unicode-text.odt")
        assert result == 3

    def test_returns_int(self):
        result = odt_word_count(SAMPLES / "minimal-document.odt")
        assert isinstance(result, int)

    def test_word_count_is_non_negative(self):
        result = odt_word_count(SAMPLES / "minimal-document.odt")
        assert result >= 0

    def test_word_count_exported_from_init(self):
        from src.python.odt import odt_word_count as fn
        result = fn(SAMPLES / "minimal-document.odt")
        assert result == 2
