"""Tests for ABW Sprint 56 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_LETTER_R-001  (Abw Letter Ratio)
  GAP-ABW-FOSS-ABW_VOWEL_CO-001  (Abw Vowel Count)
  GAP-ABW-FOSS-ABW_CONSONAN-001  (Abw Consonant Ratio)
  GAP-ABW-FOSS-ABW_NUMERIC_-001  (Abw Numeric Char Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_letter_ratio, abw_vowel_count, abw_consonant_ratio, abw_numeric_char_count

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_EMPTY = str(_DIR / "empty-section.abw")
_TWO = str(_DIR / "two-paragraphs.abw")


class TestAbwLetterRatio:
    def test_return_type(self):
        assert isinstance(abw_letter_ratio(_MINIMAL), (int, float))

    def test_exact_1_for_minimal(self):
        assert abw_letter_ratio(_MINIMAL) == 1.0

    def test_zero_for_empty(self):
        assert abw_letter_ratio(_EMPTY) == 0.0

    def test_in_range_0_to_1(self):
        assert 0.0 <= abw_letter_ratio(_TWO) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_letter_ratio(_MINIMAL) == abw_letter_ratio(_MINIMAL)


class TestAbwVowelCount:
    def test_return_type(self):
        assert isinstance(abw_vowel_count(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        assert abw_vowel_count(_MINIMAL) == 2

    def test_zero_for_empty(self):
        assert abw_vowel_count(_EMPTY) == 0

    def test_exact_9_for_two_paragraphs(self):
        assert abw_vowel_count(_TWO) == 9

    def test_nonnegative(self):
        assert abw_vowel_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_vowel_count(_MINIMAL) == abw_vowel_count(_MINIMAL)


class TestAbwConsonantRatio:
    def test_return_type(self):
        assert isinstance(abw_consonant_ratio(_MINIMAL), (int, float))

    def test_exact_0_6_for_minimal(self):
        assert abw_consonant_ratio(_MINIMAL) == 0.6

    def test_zero_for_empty(self):
        assert abw_consonant_ratio(_EMPTY) == 0.0

    def test_in_range_0_to_1(self):
        assert 0.0 <= abw_consonant_ratio(_TWO) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_consonant_ratio(_MINIMAL) == abw_consonant_ratio(_MINIMAL)


class TestAbwNumericCharCount:
    def test_return_type(self):
        assert isinstance(abw_numeric_char_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert abw_numeric_char_count(_MINIMAL) == 0

    def test_zero_for_empty(self):
        assert abw_numeric_char_count(_EMPTY) == 0

    def test_zero_for_two_paragraphs(self):
        assert abw_numeric_char_count(_TWO) == 0

    def test_nonnegative(self):
        assert abw_numeric_char_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_numeric_char_count(_MINIMAL) == abw_numeric_char_count(_MINIMAL)
