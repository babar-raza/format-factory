"""
Sprint ff-idempotent-spec-to-feature-swarm-20260617 — FODT analytics deepening.
Tests for two new analytics functions:
  fodt_paragraph_count_times_eighty_nine, fodt_word_count_times_eighty_nine
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    fodt_paragraph_count_times_eighty_nine,
    fodt_word_count_times_eighty_nine,
)

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_LIST = str(_DIR / "list-basic.fodt")


# --- fodt_paragraph_count_times_eighty_nine ---

class TestFodtParagraphCountTimesEightyNine:
    def test_returns_int_minimal(self):
        result = fodt_paragraph_count_times_eighty_nine(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative_minimal(self):
        result = fodt_paragraph_count_times_eighty_nine(_MINIMAL)
        assert result >= 0

    def test_divisible_by_89_minimal(self):
        result = fodt_paragraph_count_times_eighty_nine(_MINIMAL)
        assert result % 89 == 0

    def test_returns_int_headings(self):
        result = fodt_paragraph_count_times_eighty_nine(_HEADINGS)
        assert isinstance(result, int)

    def test_divisible_by_89_headings(self):
        result = fodt_paragraph_count_times_eighty_nine(_HEADINGS)
        assert result % 89 == 0

    def test_headings_gte_minimal(self):
        r_min = fodt_paragraph_count_times_eighty_nine(_MINIMAL)
        r_hd = fodt_paragraph_count_times_eighty_nine(_HEADINGS)
        assert r_hd >= r_min


# --- fodt_word_count_times_eighty_nine ---

class TestFodtWordCountTimesEightyNine:
    def test_returns_int_minimal(self):
        result = fodt_word_count_times_eighty_nine(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative_minimal(self):
        result = fodt_word_count_times_eighty_nine(_MINIMAL)
        assert result >= 0

    def test_divisible_by_89_minimal(self):
        result = fodt_word_count_times_eighty_nine(_MINIMAL)
        assert result % 89 == 0

    def test_returns_int_list(self):
        result = fodt_word_count_times_eighty_nine(_LIST)
        assert isinstance(result, int)

    def test_divisible_by_89_list(self):
        result = fodt_word_count_times_eighty_nine(_LIST)
        assert result % 89 == 0

    def test_returns_int_headings(self):
        result = fodt_word_count_times_eighty_nine(_HEADINGS)
        assert isinstance(result, int)

    def test_divisible_by_89_headings(self):
        result = fodt_word_count_times_eighty_nine(_HEADINGS)
        assert result % 89 == 0
