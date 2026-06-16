"""Tests for odt_unique_char_count and odt_nonspace_char_count (Sprint 66)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from odt.odt_parser import odt_unique_char_count, odt_nonspace_char_count

ODT = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "odt" / "valid"


class TestOdtUniqueCharCount:
    def test_minimal(self):
        assert odt_unique_char_count(ODT / "minimal-document.odt") == 10

    def test_two_paragraphs(self):
        assert odt_unique_char_count(ODT / "two-paragraphs.odt") == 17

    def test_unicode(self):
        assert odt_unique_char_count(ODT / "unicode-text.odt") == 11

    def test_returns_int(self):
        assert isinstance(odt_unique_char_count(ODT / "minimal-document.odt"), int)

    def test_nonnegative(self):
        for f in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
            assert odt_unique_char_count(ODT / f) >= 0


class TestOdtNonspaceCharCount:
    def test_minimal(self):
        assert odt_nonspace_char_count(ODT / "minimal-document.odt") == 12

    def test_two_paragraphs(self):
        assert odt_nonspace_char_count(ODT / "two-paragraphs.odt") == 31

    def test_unicode(self):
        assert odt_nonspace_char_count(ODT / "unicode-text.odt") == 11

    def test_returns_int(self):
        assert isinstance(odt_nonspace_char_count(ODT / "minimal-document.odt"), int)

    def test_nonnegative(self):
        for f in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
            assert odt_nonspace_char_count(ODT / f) >= 0
