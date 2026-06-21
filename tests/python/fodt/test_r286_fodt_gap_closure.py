"""
Tests for FODT gap closure (1 FOSS function).
Closes: GAP-FODT-FOSS-FODT_PUNCTUA-001

Known sample values (from fodt_punctuation_count):
  headings-and-paragraphs.fodt: 6
  list-basic.fodt: 2
  minimal-document.fodt: 2
  table-basic.fodt: 2
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_punctuation_count

_FODT = _REPO / "samples" / "by-format" / "fodt"
_HEADINGS = _FODT / "headings-and-paragraphs.fodt"
_LIST = _FODT / "list-basic.fodt"
_MINIMAL = _FODT / "minimal-document.fodt"
_TABLE = _FODT / "table-basic.fodt"


class TestFodtPunctuationCount:
    def test_returns_int(self):
        assert isinstance(fodt_punctuation_count(_MINIMAL), int)

    def test_nonnegative(self):
        for p in [_HEADINGS, _LIST, _MINIMAL, _TABLE]:
            assert fodt_punctuation_count(p) >= 0

    def test_headings_and_paragraphs_count(self):
        assert fodt_punctuation_count(_HEADINGS) == 6

    def test_list_count(self):
        assert fodt_punctuation_count(_LIST) == 2

    def test_minimal_count(self):
        assert fodt_punctuation_count(_MINIMAL) == 2

    def test_table_count(self):
        assert fodt_punctuation_count(_TABLE) == 2

    def test_headings_higher_than_minimal(self):
        # headings has more text → more punctuation
        assert fodt_punctuation_count(_HEADINGS) > fodt_punctuation_count(_MINIMAL)

    def test_all_return_int(self):
        for p in [_HEADINGS, _LIST, _MINIMAL, _TABLE]:
            assert isinstance(fodt_punctuation_count(p), int)
