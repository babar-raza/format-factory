"""Tests for abw_unique_char_count and abw_nonspace_char_count (Sprint 67)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from abw.abw_codec import abw_unique_char_count, abw_nonspace_char_count

ABW = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "abw"


class TestAbwUniqueCharCount:
    def test_minimal(self):
        assert abw_unique_char_count(ABW / "minimal-document.abw") == 4

    def test_two_paragraphs(self):
        assert abw_unique_char_count(ABW / "two-paragraphs.abw") == 17

    def test_empty(self):
        assert abw_unique_char_count(ABW / "empty-section.abw") == 0

    def test_returns_int(self):
        assert isinstance(abw_unique_char_count(ABW / "minimal-document.abw"), int)

    def test_nonnegative(self):
        for f in ["minimal-document.abw", "two-paragraphs.abw", "empty-section.abw"]:
            assert abw_unique_char_count(ABW / f) >= 0


class TestAbwNonspaceCharCount:
    def test_minimal(self):
        assert abw_nonspace_char_count(ABW / "minimal-document.abw") == 5

    def test_two_paragraphs(self):
        assert abw_nonspace_char_count(ABW / "two-paragraphs.abw") == 31

    def test_empty(self):
        assert abw_nonspace_char_count(ABW / "empty-section.abw") == 0

    def test_returns_int(self):
        assert isinstance(abw_nonspace_char_count(ABW / "minimal-document.abw"), int)

    def test_nonnegative(self):
        for f in ["minimal-document.abw", "two-paragraphs.abw", "empty-section.abw"]:
            assert abw_nonspace_char_count(ABW / f) >= 0
