"""Tests for ABW Sprint 42 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_EMPTY_PA-001  (Abw Empty Paragraph Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_empty_paragraph_ratio

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")


class TestAbwEmptyParagraphRatio:
    def test_return_type(self):
        assert isinstance(abw_empty_paragraph_ratio(_MINIMAL), float)

    def test_zero_for_minimal(self):
        assert abw_empty_paragraph_ratio(_MINIMAL) == 0.0

    def test_zero_for_two_paragraphs(self):
        assert abw_empty_paragraph_ratio(_TWO_PARA) == 0.0

    def test_nonnegative(self):
        assert abw_empty_paragraph_ratio(_MINIMAL) >= 0.0

    def test_at_most_1(self):
        assert abw_empty_paragraph_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_empty_paragraph_ratio(_MINIMAL) == abw_empty_paragraph_ratio(_MINIMAL)
