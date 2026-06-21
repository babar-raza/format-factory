"""Tests for ABW Sprint 74 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_SHORTEST-001   (Abw Shortest Paragraph Chars)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_shortest_paragraph_chars

_DIR = _REPO / "samples" / "by-format" / "abw"
_EMPTY = str(_DIR / "empty-section.abw")
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO = str(_DIR / "two-paragraphs.abw")


class TestAbwShortestParagraphChars:
    def test_return_type(self):
        assert isinstance(abw_shortest_paragraph_chars(_EMPTY), int)

    def test_zero_for_empty(self):
        assert abw_shortest_paragraph_chars(_EMPTY) == 0

    def test_exact_5_for_minimal(self):
        assert abw_shortest_paragraph_chars(_MINIMAL) == 5

    def test_exact_16_for_two(self):
        assert abw_shortest_paragraph_chars(_TWO) == 16

    def test_nonnegative(self):
        assert abw_shortest_paragraph_chars(_EMPTY) >= 0

    def test_consistent_across_calls(self):
        assert abw_shortest_paragraph_chars(_EMPTY) == abw_shortest_paragraph_chars(_EMPTY)
