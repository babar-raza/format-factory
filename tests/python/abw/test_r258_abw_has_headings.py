"""Tests for abw_has_headings (Sprint 40 batch 2).

Closes:
  GAP-ABW-FOSS-ABW_HAS_HEAD-001  (Abw Has Headings)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_has_headings

_DIR = _REPO / "samples" / "by-format" / "abw"
_EMPTY = str(_DIR / "empty-section.abw")
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARAS = str(_DIR / "two-paragraphs.abw")


class TestAbwHasHeadings:
    def test_return_type(self):
        assert isinstance(abw_has_headings(_MINIMAL), bool)

    def test_false_for_empty(self):
        assert abw_has_headings(_EMPTY) is False

    def test_false_for_minimal(self):
        assert abw_has_headings(_MINIMAL) is False

    def test_false_for_two_paragraphs(self):
        assert abw_has_headings(_TWO_PARAS) is False

    def test_consistent_across_calls(self):
        assert abw_has_headings(_MINIMAL) == abw_has_headings(_MINIMAL)
