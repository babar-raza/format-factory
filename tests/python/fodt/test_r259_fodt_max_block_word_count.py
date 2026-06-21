"""Tests for fodt_max_block_word_count (Sprint 40 batch 5).

Closes:
  GAP-FODT-FOSS-FODT_MAX_BLO-001  (Fodt Max Block Word Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_max_block_word_count

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_TABLE = str(_DIR / "table-basic.fodt")
_LIST = str(_DIR / "list-basic.fodt")


class TestFodtMaxBlockWordCount:
    def test_return_type(self):
        assert isinstance(fodt_max_block_word_count(_MINIMAL), int)

    def test_exact_2_for_minimal_document(self):
        assert fodt_max_block_word_count(_MINIMAL) == 2

    def test_exact_13_for_headings_and_paragraphs(self):
        assert fodt_max_block_word_count(_HEADINGS) == 13

    def test_exact_4_for_table_basic(self):
        assert fodt_max_block_word_count(_TABLE) == 4

    def test_positive(self):
        assert fodt_max_block_word_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_max_block_word_count(_HEADINGS) == fodt_max_block_word_count(_HEADINGS)
