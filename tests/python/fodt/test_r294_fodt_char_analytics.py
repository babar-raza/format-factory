"""Tests for fodt_uppercase_char_count and fodt_lowercase_char_count (Sprint r294)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import fodt_uppercase_char_count, fodt_lowercase_char_count

_FODT = _REPO / "samples" / "by-format" / "fodt"


class TestFodtUppercaseCharCount:
    """Tests for fodt_uppercase_char_count."""

    def test_minimal_document_has_one_uppercase(self):
        """minimal-document.fodt has exactly 1 uppercase character."""
        result = fodt_uppercase_char_count(_FODT / "minimal-document.fodt")
        assert result == 1

    def test_headings_and_paragraphs_has_19_uppercase(self):
        """headings-and-paragraphs.fodt has 19 uppercase characters."""
        result = fodt_uppercase_char_count(_FODT / "headings-and-paragraphs.fodt")
        assert result == 19

    def test_list_basic_has_two_uppercase(self):
        """list-basic.fodt has 2 uppercase characters."""
        result = fodt_uppercase_char_count(_FODT / "list-basic.fodt")
        assert result == 2

    def test_table_basic_has_two_uppercase(self):
        """table-basic.fodt has 2 uppercase characters."""
        result = fodt_uppercase_char_count(_FODT / "table-basic.fodt")
        assert result == 2

    def test_returns_int(self):
        result = fodt_uppercase_char_count(_FODT / "minimal-document.fodt")
        assert isinstance(result, int)

    def test_headings_has_most_uppercase(self):
        r1 = fodt_uppercase_char_count(_FODT / "minimal-document.fodt")
        r2 = fodt_uppercase_char_count(_FODT / "headings-and-paragraphs.fodt")
        assert r2 > r1


class TestFodtLowercaseCharCount:
    """Tests for fodt_lowercase_char_count."""

    def test_minimal_document_has_nine_lowercase(self):
        """minimal-document.fodt has 9 lowercase characters."""
        result = fodt_lowercase_char_count(_FODT / "minimal-document.fodt")
        assert result == 9

    def test_headings_and_paragraphs_has_213_lowercase(self):
        """headings-and-paragraphs.fodt has 213 lowercase characters."""
        result = fodt_lowercase_char_count(_FODT / "headings-and-paragraphs.fodt")
        assert result == 213

    def test_list_basic_has_34_lowercase(self):
        """list-basic.fodt has 34 lowercase characters."""
        result = fodt_lowercase_char_count(_FODT / "list-basic.fodt")
        assert result == 34

    def test_table_basic_has_32_lowercase(self):
        """table-basic.fodt has 32 lowercase characters."""
        result = fodt_lowercase_char_count(_FODT / "table-basic.fodt")
        assert result == 32

    def test_returns_int(self):
        result = fodt_lowercase_char_count(_FODT / "minimal-document.fodt")
        assert isinstance(result, int)

    def test_lowercase_exceeds_uppercase(self):
        """Lowercase chars should exceed uppercase for natural language."""
        upper = fodt_uppercase_char_count(_FODT / "headings-and-paragraphs.fodt")
        lower = fodt_lowercase_char_count(_FODT / "headings-and-paragraphs.fodt")
        assert lower > upper
