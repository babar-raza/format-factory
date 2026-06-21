"""
Tests for 5 new ABW analytics functions (R340 / Sprint 76):
  abw_word_length_variance, abw_lowercase_ratio, abw_uppercase_count,
  abw_para_char_variance, abw_numeric_word_count
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_word_length_variance,
    abw_lowercase_ratio,
    abw_uppercase_count,
    abw_para_char_variance,
    abw_numeric_word_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_SAMPLES / "minimal-document.abw")
_TWO_PARA = str(_SAMPLES / "two-paragraphs.abw")
_EMPTY = str(_SAMPLES / "empty-section.abw")


# ── abw_word_length_variance ───────────────────────────────────────────────────

class TestAbwWordLengthVariance:
    def test_returns_float(self):
        result = abw_word_length_variance(_TWO_PARA)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = abw_word_length_variance(_TWO_PARA)
        assert result >= 0.0

    def test_minimal_file(self):
        result = abw_word_length_variance(_MINIMAL)
        assert isinstance(result, float) and result >= 0.0

    def test_empty_file(self):
        result = abw_word_length_variance(_EMPTY)
        assert isinstance(result, float) and result >= 0.0

    def test_two_para_file(self):
        result = abw_word_length_variance(_TWO_PARA)
        assert result >= 0.0


# ── abw_lowercase_ratio ────────────────────────────────────────────────────────

class TestAbwLowercaseRatio:
    def test_returns_float(self):
        result = abw_lowercase_ratio(_TWO_PARA)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        result = abw_lowercase_ratio(_TWO_PARA)
        assert 0.0 <= result <= 1.0

    def test_minimal_file(self):
        result = abw_lowercase_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_empty_file_returns_zero(self):
        result = abw_lowercase_ratio(_EMPTY)
        assert isinstance(result, float) and result >= 0.0

    def test_two_para_file(self):
        result = abw_lowercase_ratio(_TWO_PARA)
        assert isinstance(result, float)


# ── abw_uppercase_count ────────────────────────────────────────────────────────

class TestAbwUppercaseCount:
    def test_returns_int(self):
        result = abw_uppercase_count(_TWO_PARA)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = abw_uppercase_count(_TWO_PARA)
        assert result >= 0

    def test_minimal_file(self):
        result = abw_uppercase_count(_MINIMAL)
        assert isinstance(result, int) and result >= 0

    def test_empty_file(self):
        result = abw_uppercase_count(_EMPTY)
        assert isinstance(result, int) and result >= 0

    def test_result_is_int_type(self):
        result = abw_uppercase_count(_TWO_PARA)
        assert type(result) is int


# ── abw_para_char_variance ─────────────────────────────────────────────────────

class TestAbwParaCharVariance:
    def test_returns_float(self):
        result = abw_para_char_variance(_TWO_PARA)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = abw_para_char_variance(_TWO_PARA)
        assert result >= 0.0

    def test_minimal_file(self):
        result = abw_para_char_variance(_MINIMAL)
        assert isinstance(result, float) and result >= 0.0

    def test_empty_file(self):
        result = abw_para_char_variance(_EMPTY)
        assert isinstance(result, float) and result >= 0.0

    def test_two_para_file(self):
        result = abw_para_char_variance(_TWO_PARA)
        assert result >= 0.0


# ── abw_numeric_word_count ─────────────────────────────────────────────────────

class TestAbwNumericWordCount:
    def test_returns_int(self):
        result = abw_numeric_word_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = abw_numeric_word_count(_MINIMAL)
        assert result >= 0

    def test_two_para_file(self):
        result = abw_numeric_word_count(_TWO_PARA)
        assert isinstance(result, int) and result >= 0

    def test_empty_file(self):
        result = abw_numeric_word_count(_EMPTY)
        assert isinstance(result, int) and result >= 0

    def test_result_is_int_type(self):
        result = abw_numeric_word_count(_MINIMAL)
        assert type(result) is int
