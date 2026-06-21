"""Tests for FODT Sprint 41 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_PUNCTU-001  (Fodt Punctuation Count)
  GAP-FODT-FOSS-FODT_SECTIO-001  (Fodt Section Depth Max)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_punctuation_count, fodt_section_depth_max

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")


class TestFodtPunctuationCount:
    def test_return_type(self):
        assert isinstance(fodt_punctuation_count(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        assert fodt_punctuation_count(_MINIMAL) == 2

    def test_exact_6_for_headings(self):
        assert fodt_punctuation_count(_HEADINGS) == 6

    def test_nonnegative(self):
        assert fodt_punctuation_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_punctuation_count(_MINIMAL) == fodt_punctuation_count(_MINIMAL)


class TestFodtSectionDepthMax:
    def test_return_type(self):
        assert isinstance(fodt_section_depth_max(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert fodt_section_depth_max(_MINIMAL) == 0

    def test_zero_for_headings(self):
        assert fodt_section_depth_max(_HEADINGS) == 0

    def test_nonnegative(self):
        assert fodt_section_depth_max(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_section_depth_max(_MINIMAL) == fodt_section_depth_max(_MINIMAL)
