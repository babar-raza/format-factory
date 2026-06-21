"""Tests for ABW Sprint 61 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_VOWEL_RA-001   (Abw Vowel Ratio)
  GAP-ABW-FOSS-ABW_WORD_LEN-001   (Abw Word Length Variance)
  GAP-ABW-FOSS-ABW_LOWERCAS-001   (Abw Lowercase Ratio)
  GAP-ABW-FOSS-ABW_PARA_CHA-001   (Abw Para Char Variance)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_vowel_ratio, abw_word_length_variance, abw_lowercase_ratio, abw_para_char_variance

_DIR = _REPO / "samples" / "by-format" / "abw"
_EMPTY = str(_DIR / "empty-section.abw")
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")


class TestAbwVowelRatio:
    def test_return_type(self):
        assert isinstance(abw_vowel_ratio(_MINIMAL), (int, float))

    def test_zero_for_empty(self):
        assert abw_vowel_ratio(_EMPTY) == 0.0

    def test_exact_0_4_for_minimal(self):
        assert abw_vowel_ratio(_MINIMAL) == 0.4

    def test_approx_for_two_paragraphs(self):
        assert abw_vowel_ratio(_TWO_PARA) == pytest.approx(0.2647, rel=1e-3)

    def test_between_0_and_1(self):
        assert 0.0 <= abw_vowel_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_vowel_ratio(_MINIMAL) == abw_vowel_ratio(_MINIMAL)


class TestAbwWordLengthVariance:
    def test_return_type(self):
        assert isinstance(abw_word_length_variance(_MINIMAL), (int, float))

    def test_zero_for_empty(self):
        assert abw_word_length_variance(_EMPTY) == 0.0

    def test_zero_for_minimal(self):
        assert abw_word_length_variance(_MINIMAL) == 0.0

    def test_exact_5_1875_for_two_paragraphs(self):
        assert abw_word_length_variance(_TWO_PARA) == 5.1875

    def test_nonnegative(self):
        assert abw_word_length_variance(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_word_length_variance(_MINIMAL) == abw_word_length_variance(_MINIMAL)


class TestAbwLowercaseRatio:
    def test_return_type(self):
        assert isinstance(abw_lowercase_ratio(_MINIMAL), (int, float))

    def test_zero_for_empty(self):
        assert abw_lowercase_ratio(_EMPTY) == 0.0

    def test_exact_0_8_for_minimal(self):
        assert abw_lowercase_ratio(_MINIMAL) == 0.8

    def test_approx_0_93_for_two_paragraphs(self):
        assert abw_lowercase_ratio(_TWO_PARA) == pytest.approx(0.931, rel=1e-2)

    def test_between_0_and_1(self):
        assert 0.0 <= abw_lowercase_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_lowercase_ratio(_MINIMAL) == abw_lowercase_ratio(_MINIMAL)


class TestAbwParaCharVariance:
    def test_return_type(self):
        assert isinstance(abw_para_char_variance(_MINIMAL), (int, float))

    def test_zero_for_empty(self):
        assert abw_para_char_variance(_EMPTY) == 0.0

    def test_zero_for_minimal(self):
        assert abw_para_char_variance(_MINIMAL) == 0.0

    def test_exact_0_25_for_two_paragraphs(self):
        assert abw_para_char_variance(_TWO_PARA) == 0.25

    def test_nonnegative(self):
        assert abw_para_char_variance(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_para_char_variance(_MINIMAL) == abw_para_char_variance(_MINIMAL)
