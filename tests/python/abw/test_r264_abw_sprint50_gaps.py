"""Tests for ABW Sprint 50 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_HAS_SING-001  (Abw Has Single Paragraph)
  GAP-ABW-FOSS-ABW_DIGIT_RA-001  (Abw Digit Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_has_single_paragraph, abw_digit_ratio

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_EMPTY = str(_DIR / "empty-section.abw")
_TWO = str(_DIR / "two-paragraphs.abw")


class TestAbwHasSingleParagraph:
    def test_return_type(self):
        assert isinstance(abw_has_single_paragraph(_MINIMAL), bool)

    def test_true_for_minimal_one_paragraph(self):
        assert abw_has_single_paragraph(_MINIMAL) is True

    def test_false_for_empty_section(self):
        assert abw_has_single_paragraph(_EMPTY) is False

    def test_false_for_two_paragraphs(self):
        assert abw_has_single_paragraph(_TWO) is False

    def test_consistent_across_calls(self):
        assert abw_has_single_paragraph(_MINIMAL) == abw_has_single_paragraph(_MINIMAL)


class TestAbwDigitRatio:
    def test_return_type(self):
        assert isinstance(abw_digit_ratio(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert abw_digit_ratio(_MINIMAL) == 0.0

    def test_zero_for_empty_section(self):
        assert abw_digit_ratio(_EMPTY) == 0.0

    def test_zero_for_two_paragraphs(self):
        assert abw_digit_ratio(_TWO) == 0.0

    def test_in_range_0_to_1(self):
        assert 0.0 <= abw_digit_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_digit_ratio(_MINIMAL) == abw_digit_ratio(_MINIMAL)
