"""Tests for FODT Sprint 45 batch 2 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_HAS_MOR-001  (Fodt Has More Words Than Unique)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_has_more_words_than_unique

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_LIST = str(_DIR / "list-basic.fodt")


class TestFodtHasMoreWordsThanUnique:
    def test_return_type(self):
        assert isinstance(fodt_has_more_words_than_unique(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert fodt_has_more_words_than_unique(_MINIMAL) is False

    def test_true_for_headings(self):
        assert fodt_has_more_words_than_unique(_HEADINGS) is True

    def test_true_for_list(self):
        assert fodt_has_more_words_than_unique(_LIST) is True

    def test_consistent_across_calls(self):
        assert fodt_has_more_words_than_unique(_MINIMAL) == fodt_has_more_words_than_unique(_MINIMAL)
