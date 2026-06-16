"""Tests for 5 new FODP analytics functions.

Uses real sample files from samples/by-format/fodp/.
Covers: fodp_total_text_length, fodp_nonempty_slide_ratio,
    fodp_has_numeric_content, fodp_longest_slide_index, fodp_avg_sentence_length.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp import (
    fodp_total_text_length,
    fodp_nonempty_slide_ratio,
    fodp_has_numeric_content,
    fodp_longest_slide_index,
    fodp_avg_sentence_length,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodp"
MINIMAL = _SAMPLES / "minimal-presentation.fodp"
TWO_SLIDES = _SAMPLES / "two-slides-basic.fodp"
TITLE_ONLY = _SAMPLES / "title-only.fodp"


class TestFodpTotalTextLength:
    def test_returns_int(self):
        result = fodp_total_text_length(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg(self):
        result = fodp_total_text_length(MINIMAL)
        assert result >= 0

    def test_two_slides_nonneg(self):
        result = fodp_total_text_length(TWO_SLIDES)
        assert result >= 0

    def test_title_only(self):
        result = fodp_total_text_length(TITLE_ONLY)
        assert isinstance(result, int)


class TestFodpNonemptySlideRatio:
    def test_returns_float(self):
        result = fodp_nonempty_slide_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_in_range(self):
        result = fodp_nonempty_slide_ratio(MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_two_slides(self):
        result = fodp_nonempty_slide_ratio(TWO_SLIDES)
        assert 0.0 <= result <= 1.0


class TestFodpHasNumericContent:
    def test_returns_bool(self):
        result = fodp_has_numeric_content(MINIMAL)
        assert isinstance(result, bool)

    def test_two_slides(self):
        result = fodp_has_numeric_content(TWO_SLIDES)
        assert isinstance(result, bool)

    def test_title_only(self):
        result = fodp_has_numeric_content(TITLE_ONLY)
        assert isinstance(result, bool)


class TestFodpLongestSlideIndex:
    def test_returns_int(self):
        result = fodp_longest_slide_index(MINIMAL)
        assert isinstance(result, int)

    def test_nonneg_for_data(self):
        result = fodp_longest_slide_index(MINIMAL)
        assert result >= 0

    def test_two_slides(self):
        result = fodp_longest_slide_index(TWO_SLIDES)
        assert result >= 0


class TestFodpAvgSentenceLength:
    def test_returns_float(self):
        result = fodp_avg_sentence_length(MINIMAL)
        assert isinstance(result, float)

    def test_nonneg(self):
        result = fodp_avg_sentence_length(MINIMAL)
        assert result >= 0.0

    def test_two_slides(self):
        result = fodp_avg_sentence_length(TWO_SLIDES)
        assert isinstance(result, float)
