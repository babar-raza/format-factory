"""Tests for odt_total_char_count and odt_total_word_count (Sprint r301)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_total_char_count, odt_total_word_count

_ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


class TestOdtTotalCharCount:
    """Tests for odt_total_char_count."""

    def test_minimal_document_has_13_chars(self):
        """minimal-document.odt has 13 total characters."""
        result = odt_total_char_count(_ODT / "minimal-document.odt")
        assert result == 13

    def test_two_paragraphs_has_33_chars(self):
        """two-paragraphs.odt has 33 total characters."""
        result = odt_total_char_count(_ODT / "two-paragraphs.odt")
        assert result == 33

    def test_unicode_text_has_13_chars(self):
        """unicode-text.odt has 13 total characters."""
        result = odt_total_char_count(_ODT / "unicode-text.odt")
        assert result == 13

    def test_returns_int(self):
        result = odt_total_char_count(_ODT / "minimal-document.odt")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
            assert odt_total_char_count(_ODT / f) >= 0

    def test_two_paragraphs_more_chars_than_minimal(self):
        r1 = odt_total_char_count(_ODT / "minimal-document.odt")
        r2 = odt_total_char_count(_ODT / "two-paragraphs.odt")
        assert r2 > r1


class TestOdtTotalWordCount:
    """Tests for odt_total_word_count."""

    def test_minimal_document_has_2_words(self):
        """minimal-document.odt has 2 total words."""
        result = odt_total_word_count(_ODT / "minimal-document.odt")
        assert result == 2

    def test_two_paragraphs_has_4_words(self):
        """two-paragraphs.odt has 4 total words."""
        result = odt_total_word_count(_ODT / "two-paragraphs.odt")
        assert result == 4

    def test_unicode_text_has_3_words(self):
        """unicode-text.odt has 3 total words."""
        result = odt_total_word_count(_ODT / "unicode-text.odt")
        assert result == 3

    def test_returns_int(self):
        result = odt_total_word_count(_ODT / "minimal-document.odt")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
            assert odt_total_word_count(_ODT / f) >= 0

    def test_two_paragraphs_more_words_than_minimal(self):
        r1 = odt_total_word_count(_ODT / "minimal-document.odt")
        r2 = odt_total_word_count(_ODT / "two-paragraphs.odt")
        assert r2 > r1
