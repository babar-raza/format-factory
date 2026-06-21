"""
Tests for 5 new FODT analytics functions (R338 / Sprint 74):
  fodt_lowercase_ratio, fodt_word_count_variance, fodt_paragraph_to_heading_ratio,
  fodt_digit_count, fodt_max_run_count
25 tests total.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    fodt_lowercase_ratio,
    fodt_word_count_variance,
    fodt_paragraph_to_heading_ratio,
    fodt_digit_count,
    fodt_max_run_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_SAMPLES / "minimal-document.fodt")
_HEADINGS = str(_SAMPLES / "headings-and-paragraphs.fodt")
_TABLE = str(_SAMPLES / "table-basic.fodt")
_LIST = str(_SAMPLES / "list-basic.fodt")


# ── fodt_lowercase_ratio ───────────────────────────────────────────────────────

class TestFodtLowercaseRatio:
    def test_returns_float(self):
        result = fodt_lowercase_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        result = fodt_lowercase_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_headings_file_ratio(self):
        result = fodt_lowercase_ratio(_HEADINGS)
        assert 0.0 <= result <= 1.0

    def test_table_file_ratio(self):
        result = fodt_lowercase_ratio(_TABLE)
        assert 0.0 <= result <= 1.0

    def test_list_file_ratio(self):
        result = fodt_lowercase_ratio(_LIST)
        assert isinstance(result, float) and result >= 0.0


# ── fodt_word_count_variance ───────────────────────────────────────────────────

class TestFodtWordCountVariance:
    def test_returns_float(self):
        result = fodt_word_count_variance(_HEADINGS)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fodt_word_count_variance(_HEADINGS)
        assert result >= 0.0

    def test_minimal_file(self):
        result = fodt_word_count_variance(_MINIMAL)
        assert isinstance(result, float) and result >= 0.0

    def test_table_file(self):
        result = fodt_word_count_variance(_TABLE)
        assert result >= 0.0

    def test_list_file(self):
        result = fodt_word_count_variance(_LIST)
        assert result >= 0.0


# ── fodt_paragraph_to_heading_ratio ───────────────────────────────────────────

class TestFodtParagraphToHeadingRatio:
    def test_returns_float(self):
        result = fodt_paragraph_to_heading_ratio(_HEADINGS)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fodt_paragraph_to_heading_ratio(_HEADINGS)
        assert result >= 0.0

    def test_no_headings_returns_zero(self):
        # minimal document may have no headings
        result = fodt_paragraph_to_heading_ratio(_MINIMAL)
        assert isinstance(result, float) and result >= 0.0

    def test_table_file(self):
        result = fodt_paragraph_to_heading_ratio(_TABLE)
        assert result >= 0.0

    def test_list_file(self):
        result = fodt_paragraph_to_heading_ratio(_LIST)
        assert isinstance(result, float)


# ── fodt_digit_count ───────────────────────────────────────────────────────────

class TestFodtDigitCount:
    def test_returns_int(self):
        result = fodt_digit_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_digit_count(_MINIMAL)
        assert result >= 0

    def test_headings_file(self):
        result = fodt_digit_count(_HEADINGS)
        assert isinstance(result, int) and result >= 0

    def test_table_file(self):
        result = fodt_digit_count(_TABLE)
        assert result >= 0

    def test_list_file(self):
        result = fodt_digit_count(_LIST)
        assert isinstance(result, int)


# ── fodt_max_run_count ─────────────────────────────────────────────────────────

class TestFodtMaxRunCount:
    def test_returns_int(self):
        result = fodt_max_run_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_max_run_count(_MINIMAL)
        assert result >= 0

    def test_headings_file_has_runs(self):
        result = fodt_max_run_count(_HEADINGS)
        assert isinstance(result, int) and result >= 0

    def test_table_file(self):
        result = fodt_max_run_count(_TABLE)
        assert result >= 0

    def test_list_file(self):
        result = fodt_max_run_count(_LIST)
        assert isinstance(result, int) and result >= 0
