"""Tests for abw_digit_count (Sprint 40 batch 4).

Closes:
  GAP-ABW-FOSS-ABW_DIGIT_CO-001  (Abw Digit Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_digit_count

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")
_EMPTY_SECTION = str(_DIR / "empty-section.abw")


class TestAbwDigitCount:
    def test_return_type(self):
        assert isinstance(abw_digit_count(_MINIMAL), int)

    def test_zero_for_minimal_document(self):
        # minimal doc has no digits
        assert abw_digit_count(_MINIMAL) == 0

    def test_zero_for_two_paragraphs(self):
        assert abw_digit_count(_TWO_PARA) == 0

    def test_zero_for_empty_section(self):
        assert abw_digit_count(_EMPTY_SECTION) == 0

    def test_nonnegative(self):
        assert abw_digit_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_digit_count(_MINIMAL) == abw_digit_count(_MINIMAL)
