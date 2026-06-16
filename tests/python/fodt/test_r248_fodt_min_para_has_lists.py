"""Tests for fodt_min_paragraph_length and fodt_has_lists (Sprint 38)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_min_paragraph_length, fodt_has_lists

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")               # 1 para "Hello, world." (13)
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")       # paras: 78,47,81,31 -> min=31
_LIST = str(_DIR / "list-basic.fodt")                        # 2 lists -> has_lists=True
_TABLE = str(_DIR / "table-basic.fodt")                      # 0 lists -> has_lists=False


class TestFodtMinParagraphLength:
    def test_return_type(self):
        assert isinstance(fodt_min_paragraph_length(_MINIMAL), int)

    def test_exact_13_for_minimal(self):
        # minimal-document.fodt has one para "Hello, world." -> len=13
        assert fodt_min_paragraph_length(_MINIMAL) == 13

    def test_exact_31_for_headings(self):
        # headings-and-paragraphs.fodt: para lengths [78,47,81,31] -> min=31
        assert fodt_min_paragraph_length(_HEADINGS) == 31

    def test_exact_20_for_list(self):
        # list-basic.fodt: para lengths [20, 22] -> min=20
        assert fodt_min_paragraph_length(_LIST) == 20

    def test_nonnegative(self):
        assert fodt_min_paragraph_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_min_paragraph_length(_MINIMAL) == fodt_min_paragraph_length(_MINIMAL)


class TestFodtHasLists:
    def test_return_type(self):
        assert isinstance(fodt_has_lists(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal-document.fodt has no lists
        assert fodt_has_lists(_MINIMAL) is False

    def test_true_for_list_basic(self):
        # list-basic.fodt has 2 lists
        assert fodt_has_lists(_LIST) is True

    def test_false_for_table_basic(self):
        # table-basic.fodt has tables but no lists
        assert fodt_has_lists(_TABLE) is False

    def test_false_for_headings(self):
        # headings-and-paragraphs.fodt has headings but no lists
        assert fodt_has_lists(_HEADINGS) is False

    def test_consistent_across_calls(self):
        assert fodt_has_lists(_MINIMAL) == fodt_has_lists(_MINIMAL)
