"""
tests/python/odt/test_r185_odt_paragraph_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT55-001
Tests for odt_paragraph_count() — count paragraphs in an ODT document.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_paragraph_count

SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdtParagraphCount:
    def test_minimal_document_one_paragraph(self):
        result = odt_paragraph_count(SAMPLES / "minimal-document.odt")
        assert result == 1

    def test_two_paragraphs_returns_two(self):
        result = odt_paragraph_count(SAMPLES / "two-paragraphs.odt")
        assert result == 2

    def test_unicode_text_one_paragraph(self):
        result = odt_paragraph_count(SAMPLES / "unicode-text.odt")
        assert result == 1

    def test_returns_int(self):
        result = odt_paragraph_count(SAMPLES / "minimal-document.odt")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_paragraph_count(SAMPLES / "minimal-document.odt")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.odt import odt_paragraph_count as fn
        result = fn(SAMPLES / "two-paragraphs.odt")
        assert result == 2
