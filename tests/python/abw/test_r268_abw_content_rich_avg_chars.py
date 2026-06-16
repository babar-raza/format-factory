"""Tests for abw_is_content_rich and abw_avg_chars_per_word (Sprint 58)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from abw.abw_codec import abw_is_content_rich, abw_avg_chars_per_word

ABW = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "abw"


class TestAbwIsContentRich:
    def test_minimal_not_rich(self):
        assert abw_is_content_rich(ABW / "minimal-document.abw") is False

    def test_two_paragraphs_is_rich(self):
        assert abw_is_content_rich(ABW / "two-paragraphs.abw") is True

    def test_empty_not_rich(self):
        assert abw_is_content_rich(ABW / "empty-section.abw") is False

    def test_returns_bool(self):
        result = abw_is_content_rich(ABW / "minimal-document.abw")
        assert isinstance(result, bool)

    def test_true_when_multiple_unique_words(self):
        assert abw_is_content_rich(ABW / "two-paragraphs.abw") is True


class TestAbwAvgCharsPerWord:
    def test_minimal_five_chars(self):
        assert abw_avg_chars_per_word(ABW / "minimal-document.abw") == 5.0

    def test_two_paragraphs(self):
        result = abw_avg_chars_per_word(ABW / "two-paragraphs.abw")
        assert abs(result - 8.25) < 0.01

    def test_empty_returns_zero(self):
        assert abw_avg_chars_per_word(ABW / "empty-section.abw") == 0.0

    def test_returns_float(self):
        result = abw_avg_chars_per_word(ABW / "minimal-document.abw")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for f in ["minimal-document.abw", "two-paragraphs.abw", "empty-section.abw"]:
            assert abw_avg_chars_per_word(ABW / f) >= 0.0
