"""Tests for fodt_avg_chars_per_word and fodt_heading_ratio (Sprint 59)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fodt.neutral_model import fodt_avg_chars_per_word, fodt_heading_ratio

FODT = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodt"


class TestFodtAvgCharsPerWord:
    def test_minimal_document(self):
        assert abs(fodt_avg_chars_per_word(FODT / "minimal-document.fodt") - 6.5) < 0.01

    def test_headings_and_paragraphs(self):
        result = fodt_avg_chars_per_word(FODT / "headings-and-paragraphs.fodt")
        assert abs(result - 5.39) < 0.01

    def test_list_basic(self):
        assert abs(fodt_avg_chars_per_word(FODT / "list-basic.fodt") - 7.0) < 0.01

    def test_returns_float(self):
        result = fodt_avg_chars_per_word(FODT / "minimal-document.fodt")
        assert isinstance(result, float)

    def test_positive(self):
        for f in ["minimal-document.fodt", "headings-and-paragraphs.fodt", "list-basic.fodt"]:
            assert fodt_avg_chars_per_word(FODT / f) > 0.0


class TestFodtHeadingRatio:
    def test_minimal_no_headings(self):
        assert fodt_heading_ratio(FODT / "minimal-document.fodt") == 0.0

    def test_headings_and_paragraphs(self):
        result = fodt_heading_ratio(FODT / "headings-and-paragraphs.fodt")
        assert abs(result - 0.75) < 0.01

    def test_list_no_headings(self):
        assert fodt_heading_ratio(FODT / "list-basic.fodt") == 0.0

    def test_returns_float(self):
        result = fodt_heading_ratio(FODT / "minimal-document.fodt")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for f in ["minimal-document.fodt", "headings-and-paragraphs.fodt", "list-basic.fodt"]:
            assert fodt_heading_ratio(FODT / f) >= 0.0
