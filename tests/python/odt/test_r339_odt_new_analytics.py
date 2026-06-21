"""
Tests for 5 new ODT analytics functions (R339 / Sprint 75):
  odt_paragraph_word_variance, odt_punctuation_count, odt_avg_heading_length,
  odt_word_count_variance, odt_numeric_word_count
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt import (
    odt_paragraph_word_variance,
    odt_punctuation_count,
    odt_avg_heading_length,
    odt_word_count_variance,
    odt_numeric_word_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-document.odt")
_TWO_PARA = str(_SAMPLES / "two-paragraphs.odt")
_UNICODE = str(_SAMPLES / "unicode-text.odt")


# ── odt_paragraph_word_variance ────────────────────────────────────────────────

class TestOdtParagraphWordVariance:
    def test_returns_float(self):
        result = odt_paragraph_word_variance(_TWO_PARA)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = odt_paragraph_word_variance(_TWO_PARA)
        assert result >= 0.0

    def test_minimal_file(self):
        result = odt_paragraph_word_variance(_MINIMAL)
        assert isinstance(result, float) and result >= 0.0

    def test_unicode_file(self):
        result = odt_paragraph_word_variance(_UNICODE)
        assert result >= 0.0

    def test_two_para_file(self):
        result = odt_paragraph_word_variance(_TWO_PARA)
        assert isinstance(result, float)


# ── odt_punctuation_count ──────────────────────────────────────────────────────

class TestOdtPunctuationCount:
    def test_returns_int(self):
        result = odt_punctuation_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_punctuation_count(_MINIMAL)
        assert result >= 0

    def test_two_para_file(self):
        result = odt_punctuation_count(_TWO_PARA)
        assert isinstance(result, int) and result >= 0

    def test_unicode_file(self):
        result = odt_punctuation_count(_UNICODE)
        assert result >= 0

    def test_result_is_int_type(self):
        result = odt_punctuation_count(_TWO_PARA)
        assert type(result) is int


# ── odt_avg_heading_length ─────────────────────────────────────────────────────

class TestOdtAvgHeadingLength:
    def test_returns_float(self):
        result = odt_avg_heading_length(_MINIMAL)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = odt_avg_heading_length(_MINIMAL)
        assert result >= 0.0

    def test_two_para_file(self):
        result = odt_avg_heading_length(_TWO_PARA)
        assert isinstance(result, float) and result >= 0.0

    def test_unicode_file(self):
        result = odt_avg_heading_length(_UNICODE)
        assert result >= 0.0

    def test_result_bounded(self):
        result = odt_avg_heading_length(_MINIMAL)
        assert result >= 0.0


# ── odt_word_count_variance ────────────────────────────────────────────────────

class TestOdtWordCountVariance:
    def test_returns_float(self):
        result = odt_word_count_variance(_TWO_PARA)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = odt_word_count_variance(_TWO_PARA)
        assert result >= 0.0

    def test_minimal_file(self):
        result = odt_word_count_variance(_MINIMAL)
        assert isinstance(result, float) and result >= 0.0

    def test_unicode_file(self):
        result = odt_word_count_variance(_UNICODE)
        assert result >= 0.0

    def test_matches_paragraph_word_variance(self):
        # both functions compute variance of per-paragraph word counts
        r1 = odt_paragraph_word_variance(_TWO_PARA)
        r2 = odt_word_count_variance(_TWO_PARA)
        assert abs(r1 - r2) < 1e-9


# ── odt_numeric_word_count ─────────────────────────────────────────────────────

class TestOdtNumericWordCount:
    def test_returns_int(self):
        result = odt_numeric_word_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = odt_numeric_word_count(_MINIMAL)
        assert result >= 0

    def test_two_para_file(self):
        result = odt_numeric_word_count(_TWO_PARA)
        assert isinstance(result, int) and result >= 0

    def test_unicode_file(self):
        result = odt_numeric_word_count(_UNICODE)
        assert result >= 0

    def test_result_is_int_type(self):
        result = odt_numeric_word_count(_MINIMAL)
        assert type(result) is int
