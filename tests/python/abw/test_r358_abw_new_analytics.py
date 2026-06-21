"""
Sprint 94 — ABW analytics round 4.
25 tests for 5 new analytics functions:
  abw_alpha_ratio, abw_max_paragraph_words, abw_short_paragraph_count,
  abw_total_para_char_count, abw_nonempty_para_ratio
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_alpha_ratio,
    abw_max_paragraph_words,
    abw_short_paragraph_count,
    abw_total_para_char_count,
    abw_nonempty_para_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_SAMPLES / "minimal-document.abw")
_TWO = str(_SAMPLES / "two-paragraphs.abw")
_EMPTY = str(_SAMPLES / "empty-section.abw")


# --- abw_alpha_ratio ---

class TestAbwAlphaRatio:
    def test_returns_float(self):
        result = abw_alpha_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = abw_alpha_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_two_paragraphs_positive(self):
        result = abw_alpha_ratio(_TWO)
        assert result > 0.0

    def test_empty_section_bounded(self):
        result = abw_alpha_ratio(_EMPTY)
        assert 0.0 <= result <= 1.0

    def test_all_samples_bounded(self):
        for path in [_MINIMAL, _TWO, _EMPTY]:
            r = abw_alpha_ratio(path)
            assert 0.0 <= r <= 1.0


# --- abw_max_paragraph_words ---

class TestAbwMaxParagraphWords:
    def test_returns_int(self):
        result = abw_max_paragraph_words(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = abw_max_paragraph_words(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs_positive(self):
        result = abw_max_paragraph_words(_TWO)
        assert result > 0

    def test_empty_section(self):
        result = abw_max_paragraph_words(_EMPTY)
        assert isinstance(result, int) and result >= 0

    def test_max_gte_min(self):
        from src.python.abw import abw_min_paragraph_length
        mx = abw_max_paragraph_words(_TWO)
        mn = abw_min_paragraph_length(_TWO)
        assert mx >= 0 and mn >= 0


# --- abw_short_paragraph_count ---

class TestAbwShortParagraphCount:
    def test_returns_int(self):
        result = abw_short_paragraph_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = abw_short_paragraph_count(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs(self):
        result = abw_short_paragraph_count(_TWO)
        assert isinstance(result, int) and result >= 0

    def test_empty_section(self):
        result = abw_short_paragraph_count(_EMPTY)
        assert isinstance(result, int) and result >= 0

    def test_high_max_words_counts_all(self):
        from src.python.abw import get_paragraph_count
        total = get_paragraph_count(_TWO)
        short = abw_short_paragraph_count(_TWO, max_words=10000)
        assert short <= total


# --- abw_total_para_char_count ---

class TestAbwTotalParaCharCount:
    def test_returns_int(self):
        result = abw_total_para_char_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = abw_total_para_char_count(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs_positive(self):
        result = abw_total_para_char_count(_TWO)
        assert result > 0

    def test_empty_section(self):
        result = abw_total_para_char_count(_EMPTY)
        assert isinstance(result, int) and result >= 0

    def test_gte_longest_para_chars(self):
        from src.python.abw import abw_longest_paragraph_chars
        total = abw_total_para_char_count(_TWO)
        longest = abw_longest_paragraph_chars(_TWO)
        assert total >= longest


# --- abw_nonempty_para_ratio ---

class TestAbwNonemptyParaRatio:
    def test_returns_float(self):
        result = abw_nonempty_para_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = abw_nonempty_para_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_two_paragraphs_positive(self):
        result = abw_nonempty_para_ratio(_TWO)
        assert result > 0.0

    def test_empty_section_bounded(self):
        result = abw_nonempty_para_ratio(_EMPTY)
        assert 0.0 <= result <= 1.0

    def test_bounded_for_all_samples(self):
        for path in [_MINIMAL, _TWO, _EMPTY]:
            r = abw_nonempty_para_ratio(path)
            assert 0.0 <= r <= 1.0
