"""
Tests for 5 new FODP analytics functions (R341 / Sprint 77):
  fodp_digit_count, fodp_lowercase_ratio, fodp_uppercase_count,
  fodp_word_length_variance, fodp_punctuation_count
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp import (
    fodp_digit_count,
    fodp_lowercase_ratio,
    fodp_uppercase_count,
    fodp_word_length_variance,
    fodp_punctuation_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodp"
_MINIMAL = str(_SAMPLES / "minimal-presentation.fodp")
_TITLE = str(_SAMPLES / "title-only.fodp")
_TWO = str(_SAMPLES / "two-slides-basic.fodp")


# ── fodp_digit_count ───────────────────────────────────────────────────────────

class TestFodpDigitCount:
    def test_returns_int(self):
        result = fodp_digit_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_digit_count(_MINIMAL)
        assert result >= 0

    def test_title_file(self):
        result = fodp_digit_count(_TITLE)
        assert isinstance(result, int) and result >= 0

    def test_two_slides_file(self):
        result = fodp_digit_count(_TWO)
        assert result >= 0

    def test_result_is_int_type(self):
        result = fodp_digit_count(_MINIMAL)
        assert type(result) is int


# ── fodp_lowercase_ratio ───────────────────────────────────────────────────────

class TestFodpLowercaseRatio:
    def test_returns_float(self):
        result = fodp_lowercase_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        result = fodp_lowercase_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_title_file(self):
        result = fodp_lowercase_ratio(_TITLE)
        assert 0.0 <= result <= 1.0

    def test_two_slides_file(self):
        result = fodp_lowercase_ratio(_TWO)
        assert 0.0 <= result <= 1.0

    def test_two_slides_is_float(self):
        result = fodp_lowercase_ratio(_TWO)
        assert isinstance(result, float)


# ── fodp_uppercase_count ───────────────────────────────────────────────────────

class TestFodpUppercaseCount:
    def test_returns_int(self):
        result = fodp_uppercase_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_uppercase_count(_MINIMAL)
        assert result >= 0

    def test_title_file(self):
        result = fodp_uppercase_count(_TITLE)
        assert isinstance(result, int) and result >= 0

    def test_two_slides_file(self):
        result = fodp_uppercase_count(_TWO)
        assert result >= 0

    def test_result_is_int_type(self):
        result = fodp_uppercase_count(_TWO)
        assert type(result) is int


# ── fodp_word_length_variance ──────────────────────────────────────────────────

class TestFodpWordLengthVariance:
    def test_returns_float(self):
        result = fodp_word_length_variance(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fodp_word_length_variance(_MINIMAL)
        assert result >= 0.0

    def test_title_file(self):
        result = fodp_word_length_variance(_TITLE)
        assert isinstance(result, float) and result >= 0.0

    def test_two_slides_file(self):
        result = fodp_word_length_variance(_TWO)
        assert result >= 0.0

    def test_two_slides_is_float(self):
        result = fodp_word_length_variance(_TWO)
        assert isinstance(result, float)


# ── fodp_punctuation_count ─────────────────────────────────────────────────────

class TestFodpPunctuationCount:
    def test_returns_int(self):
        result = fodp_punctuation_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_punctuation_count(_MINIMAL)
        assert result >= 0

    def test_title_file(self):
        result = fodp_punctuation_count(_TITLE)
        assert isinstance(result, int) and result >= 0

    def test_two_slides_file(self):
        result = fodp_punctuation_count(_TWO)
        assert result >= 0

    def test_result_is_int_type(self):
        result = fodp_punctuation_count(_TWO)
        assert type(result) is int
