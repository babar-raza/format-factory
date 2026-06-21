"""Tests for abw_alpha_char_count and abw_space_count (Sprint r298)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_alpha_char_count, abw_space_count

_ABW = _REPO / "samples" / "by-format" / "abw"


class TestAbwAlphaCharCount:
    """Tests for abw_alpha_char_count."""

    def test_empty_section_has_zero_alpha(self):
        """empty-section.abw has no paragraphs — 0 alphabetic characters."""
        result = abw_alpha_char_count(_ABW / "empty-section.abw")
        assert result == 0

    def test_minimal_document_has_five_alpha(self):
        """minimal-document.abw has 5 alphabetic characters ('Hello')."""
        result = abw_alpha_char_count(_ABW / "minimal-document.abw")
        assert result == 5

    def test_two_paragraphs_has_29_alpha(self):
        """two-paragraphs.abw has 29 alphabetic characters across both paragraphs."""
        result = abw_alpha_char_count(_ABW / "two-paragraphs.abw")
        assert result == 29

    def test_returns_int(self):
        result = abw_alpha_char_count(_ABW / "minimal-document.abw")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["empty-section.abw", "minimal-document.abw", "two-paragraphs.abw"]:
            assert abw_alpha_char_count(_ABW / f) >= 0

    def test_more_paragraphs_have_more_alpha(self):
        r1 = abw_alpha_char_count(_ABW / "minimal-document.abw")
        r2 = abw_alpha_char_count(_ABW / "two-paragraphs.abw")
        assert r2 > r1


class TestAbwSpaceCount:
    """Tests for abw_space_count."""

    def test_empty_section_has_zero_spaces(self):
        """empty-section.abw has no text — 0 spaces."""
        result = abw_space_count(_ABW / "empty-section.abw")
        assert result == 0

    def test_minimal_document_has_zero_spaces(self):
        """minimal-document.abw has one word with no spaces."""
        result = abw_space_count(_ABW / "minimal-document.abw")
        assert result == 0

    def test_two_paragraphs_has_two_spaces(self):
        """two-paragraphs.abw has 2 space characters across its paragraphs."""
        result = abw_space_count(_ABW / "two-paragraphs.abw")
        assert result == 2

    def test_returns_int(self):
        result = abw_space_count(_ABW / "two-paragraphs.abw")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["empty-section.abw", "minimal-document.abw", "two-paragraphs.abw"]:
            assert abw_space_count(_ABW / f) >= 0

    def test_two_paragraphs_has_more_spaces_than_minimal(self):
        r1 = abw_space_count(_ABW / "minimal-document.abw")
        r2 = abw_space_count(_ABW / "two-paragraphs.abw")
        assert r2 > r1
