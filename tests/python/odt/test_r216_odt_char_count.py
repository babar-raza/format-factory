"""Tests for odt_char_count().

Sprint: product-deepening-rnext86
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_char_count

ODT_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdtCharCount:
    def test_import(self):
        assert callable(odt_char_count)

    def test_minimal_document_char_count(self):
        assert odt_char_count(ODT_SAMPLES / "minimal-document.odt") == 13

    def test_two_paragraphs_char_count(self):
        assert odt_char_count(ODT_SAMPLES / "two-paragraphs.odt") == 33

    def test_unicode_text_char_count(self):
        assert odt_char_count(ODT_SAMPLES / "unicode-text.odt") == 13

    def test_returns_int(self):
        result = odt_char_count(ODT_SAMPLES / "minimal-document.odt")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in ODT_SAMPLES.iterdir():
            if sample.suffix == ".odt":
                assert odt_char_count(sample) >= 0
