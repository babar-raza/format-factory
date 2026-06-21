"""Tests for FODT Sprint 52 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_CHAR_PE-001  (Fodt Char Per Word)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_char_per_word

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_LIST = str(_DIR / "list-basic.fodt")
_TABLE = str(_DIR / "table-basic.fodt")


class TestFodtCharPerWord:
    def test_return_type(self):
        assert isinstance(fodt_char_per_word(_MINIMAL), (int, float))

    def test_exact_6_for_minimal(self):
        assert fodt_char_per_word(_MINIMAL) == 6.0

    def test_positive_for_headings(self):
        assert fodt_char_per_word(_HEADINGS) > 0

    def test_positive_for_list(self):
        assert fodt_char_per_word(_LIST) > 0

    def test_positive_for_table(self):
        assert fodt_char_per_word(_TABLE) > 0

    def test_consistent_across_calls(self):
        assert fodt_char_per_word(_MINIMAL) == fodt_char_per_word(_MINIMAL)
