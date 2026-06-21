"""Tests for ABW Sprint 41 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_UPPERCAS-001  (Abw Uppercase Ratio)
  GAP-ABW-FOSS-ABW_MAX_PARA-001  (Abw Max Paragraph Length)
  GAP-ABW-FOSS-ABW_TOTAL_WO-001  (Abw Total Word Count)
  GAP-ABW-FOSS-ABW_SECTION_-001  (Abw Section Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_max_paragraph_length,
    abw_section_count,
    abw_total_word_count,
    abw_uppercase_ratio,
)

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")
_WITH_SECTIONS = str(_DIR / "with-sections.abw")


class TestAbwUppercaseRatio:
    def test_return_type(self):
        assert isinstance(abw_uppercase_ratio(_MINIMAL), float)

    def test_exact_0_2_for_minimal(self):
        assert abw_uppercase_ratio(_MINIMAL) == 0.2

    def test_nonnegative(self):
        assert abw_uppercase_ratio(_MINIMAL) >= 0.0

    def test_at_most_1(self):
        assert abw_uppercase_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_uppercase_ratio(_MINIMAL) == abw_uppercase_ratio(_MINIMAL)


class TestAbwMaxParagraphLength:
    def test_return_type(self):
        assert isinstance(abw_max_paragraph_length(_MINIMAL), int)

    def test_exact_5_for_minimal(self):
        assert abw_max_paragraph_length(_MINIMAL) == 5

    def test_exact_17_for_two_paragraphs(self):
        assert abw_max_paragraph_length(_TWO_PARA) == 17

    def test_nonnegative(self):
        assert abw_max_paragraph_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_max_paragraph_length(_MINIMAL) == abw_max_paragraph_length(_MINIMAL)


class TestAbwTotalWordCount:
    def test_return_type(self):
        assert isinstance(abw_total_word_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert abw_total_word_count(_MINIMAL) == 1

    def test_exact_4_for_two_paragraphs(self):
        assert abw_total_word_count(_TWO_PARA) == 4

    def test_nonnegative(self):
        assert abw_total_word_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_total_word_count(_MINIMAL) == abw_total_word_count(_MINIMAL)


class TestAbwSectionCount:
    def test_return_type(self):
        assert isinstance(abw_section_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert abw_section_count(_MINIMAL) == 0

    def test_nonnegative(self):
        assert abw_section_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_section_count(_MINIMAL) == abw_section_count(_MINIMAL)
