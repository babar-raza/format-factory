"""Tests for odt_avg_chars_per_word and odt_is_content_rich (Sprint 60)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from odt.odt_parser import odt_avg_chars_per_word, odt_is_content_rich

ODT = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "odt" / "valid"


class TestOdtAvgCharsPerWord:
    def test_minimal_document(self):
        assert abs(odt_avg_chars_per_word(ODT / "minimal-document.odt") - 6.5) < 0.01

    def test_two_paragraphs(self):
        assert abs(odt_avg_chars_per_word(ODT / "two-paragraphs.odt") - 8.25) < 0.01

    def test_unicode_text(self):
        result = odt_avg_chars_per_word(ODT / "unicode-text.odt")
        assert abs(result - 4.33) < 0.01

    def test_returns_float(self):
        result = odt_avg_chars_per_word(ODT / "minimal-document.odt")
        assert isinstance(result, float)

    def test_positive(self):
        for f in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
            assert odt_avg_chars_per_word(ODT / f) > 0.0


class TestOdtIsContentRich:
    def test_minimal_not_rich(self):
        assert odt_is_content_rich(ODT / "minimal-document.odt") is False

    def test_two_paragraphs_is_rich(self):
        assert odt_is_content_rich(ODT / "two-paragraphs.odt") is True

    def test_unicode_is_rich(self):
        assert odt_is_content_rich(ODT / "unicode-text.odt") is True

    def test_returns_bool(self):
        result = odt_is_content_rich(ODT / "minimal-document.odt")
        assert isinstance(result, bool)

    def test_false_for_few_words(self):
        assert odt_is_content_rich(ODT / "minimal-document.odt") is False
