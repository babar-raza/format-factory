"""
tests/python/odt/test_r179_odt_heading_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT47-001
Tests for odt_heading_count() — count headings in an ODT document.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_heading_count

SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdtHeadingCount:
    def test_minimal_document_no_headings(self):
        result = odt_heading_count(SAMPLES / "minimal-document.odt")
        assert result == 0

    def test_two_paragraphs_no_headings(self):
        result = odt_heading_count(SAMPLES / "two-paragraphs.odt")
        assert result == 0

    def test_unicode_text_no_headings(self):
        result = odt_heading_count(SAMPLES / "unicode-text.odt")
        assert result == 0

    def test_returns_int(self):
        result = odt_heading_count(SAMPLES / "minimal-document.odt")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_heading_count(SAMPLES / "minimal-document.odt")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.odt import odt_heading_count as fn
        result = fn(SAMPLES / "minimal-document.odt")
        assert result == 0
