"""
Sprint 93 — ODT analytics round 4.
25 tests for 5 new analytics functions:
  odt_vowel_count, odt_consonant_count, odt_max_paragraph_char_count,
  odt_short_word_count, odt_alpha_ratio
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt import (
    parse_odt,
    odt_vowel_count,
    odt_consonant_count,
    odt_max_paragraph_char_count,
    odt_short_word_count,
    odt_alpha_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-document.odt")
_TWO = str(_SAMPLES / "two-paragraphs.odt")
_UNICODE = str(_SAMPLES / "unicode-text.odt")


# --- odt_vowel_count ---

class TestOdtVowelCount:
    def test_returns_int(self):
        result = odt_vowel_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_vowel_count(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs_positive(self):
        result = odt_vowel_count(_TWO)
        assert result > 0

    def test_unicode_file(self):
        result = odt_vowel_count(_UNICODE)
        assert isinstance(result, int) and result >= 0

    def test_vowel_count_less_than_char_count(self):
        from src.python.odt import odt_total_char_count
        vowels = odt_vowel_count(_TWO)
        total = odt_total_char_count(_TWO)
        assert vowels <= total


# --- odt_consonant_count ---

class TestOdtConsonantCount:
    def test_returns_int(self):
        result = odt_consonant_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_consonant_count(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs_positive(self):
        result = odt_consonant_count(_TWO)
        assert result > 0

    def test_unicode_file(self):
        result = odt_consonant_count(_UNICODE)
        assert isinstance(result, int) and result >= 0

    def test_consonant_count_less_than_char_count(self):
        from src.python.odt import odt_total_char_count
        consonants = odt_consonant_count(_TWO)
        total = odt_total_char_count(_TWO)
        assert consonants <= total


# --- odt_max_paragraph_char_count ---

class TestOdtMaxParagraphCharCount:
    def test_returns_int(self):
        result = odt_max_paragraph_char_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_max_paragraph_char_count(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs_positive(self):
        result = odt_max_paragraph_char_count(_TWO)
        assert result > 0

    def test_unicode_file(self):
        result = odt_max_paragraph_char_count(_UNICODE)
        assert isinstance(result, int) and result >= 0

    def test_max_gte_min_length(self):
        from src.python.odt import odt_min_paragraph_length
        max_c = odt_max_paragraph_char_count(_TWO)
        min_c = odt_min_paragraph_length(_TWO)
        assert max_c >= min_c


# --- odt_short_word_count ---

class TestOdtShortWordCount:
    def test_returns_int(self):
        result = odt_short_word_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_short_word_count(_MINIMAL)
        assert result >= 0

    def test_two_paragraphs(self):
        result = odt_short_word_count(_TWO)
        assert isinstance(result, int) and result >= 0

    def test_unicode_file(self):
        result = odt_short_word_count(_UNICODE)
        assert isinstance(result, int) and result >= 0

    def test_zero_max_len(self):
        result = odt_short_word_count(_TWO, max_len=0)
        assert result == 0


# --- odt_alpha_ratio ---

class TestOdtAlphaRatio:
    def test_returns_float(self):
        result = odt_alpha_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = odt_alpha_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_two_paragraphs_positive(self):
        result = odt_alpha_ratio(_TWO)
        assert result > 0.0

    def test_unicode_file(self):
        result = odt_alpha_ratio(_UNICODE)
        assert 0.0 <= result <= 1.0

    def test_bounded_for_all_samples(self):
        for path in [_MINIMAL, _TWO, _UNICODE]:
            r = odt_alpha_ratio(path)
            assert 0.0 <= r <= 1.0
