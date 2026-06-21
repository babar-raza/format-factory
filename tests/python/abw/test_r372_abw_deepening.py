"""Tests for ABW product deepening sprint 143.

New functions:
  abw_consonant_to_vowel_ratio  — consonants / vowels (0.0 if no vowels)
  abw_short_word_count          — count of words with <= 3 characters
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_consonant_to_vowel_ratio, abw_short_word_count

_EMPTY = str(_REPO / "samples" / "by-format" / "abw" / "empty-section.abw")
_MINIMAL = str(_REPO / "samples" / "by-format" / "abw" / "minimal-document.abw")
_TWO = str(_REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw")


class TestAbwConsonantToVowelRatio:
    def test_return_type(self):
        assert isinstance(abw_consonant_to_vowel_ratio(_MINIMAL), float)

    def test_zero_for_empty(self):
        assert abw_consonant_to_vowel_ratio(_EMPTY) == 0.0

    def test_exact_1_5_for_minimal(self):
        # "Hello": H,l,l = 3 consonants, e,o = 2 vowels → 3/2 = 1.5
        assert abw_consonant_to_vowel_ratio(_MINIMAL) == 1.5

    def test_exact_ratio_for_two_para(self):
        # "First paragraph. Second paragraph." → consonants=20, vowels=9 → 2.2222
        result = abw_consonant_to_vowel_ratio(_TWO)
        assert abs(result - 20 / 9) < 1e-9

    def test_nonnegative(self):
        assert abw_consonant_to_vowel_ratio(_MINIMAL) >= 0.0

    def test_consistent(self):
        assert abw_consonant_to_vowel_ratio(_TWO) == abw_consonant_to_vowel_ratio(_TWO)


class TestAbwShortWordCount:
    def test_return_type(self):
        assert isinstance(abw_short_word_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert abw_short_word_count(_EMPTY) == 0

    def test_zero_for_minimal(self):
        # "Hello" has 5 chars — not short
        assert abw_short_word_count(_MINIMAL) == 0

    def test_zero_for_two_para(self):
        # "First paragraph. Second paragraph." — all words > 3 chars
        assert abw_short_word_count(_TWO) == 0

    def test_nonnegative(self):
        assert abw_short_word_count(_MINIMAL) >= 0

    def test_consistent(self):
        assert abw_short_word_count(_TWO) == abw_short_word_count(_TWO)
