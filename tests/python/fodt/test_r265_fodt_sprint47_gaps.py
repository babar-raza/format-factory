"""Tests for FODT Sprint 47 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_MIN_HEA-001  (Fodt Min Heading Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_min_heading_length

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_LIST = str(_DIR / "list-basic.fodt")


class TestFodtMinHeadingLength:
    def test_return_type(self):
        assert isinstance(fodt_min_heading_length(_MINIMAL), int)

    def test_zero_for_minimal_no_headings(self):
        assert fodt_min_heading_length(_MINIMAL) == 0

    def test_exact_11_for_headings(self):
        assert fodt_min_heading_length(_HEADINGS) == 11

    def test_zero_for_list(self):
        assert fodt_min_heading_length(_LIST) == 0

    def test_nonnegative(self):
        assert fodt_min_heading_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_min_heading_length(_MINIMAL) == fodt_min_heading_length(_MINIMAL)
