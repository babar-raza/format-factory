"""Tests for FODT Sprint 56 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_MIN_BLO-001  (Fodt Min Block Text Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_min_block_text_length

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_LIST = str(_DIR / "list-basic.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")


class TestFodtMinBlockTextLength:
    def test_return_type(self):
        assert isinstance(fodt_min_block_text_length(_MINIMAL), int)

    def test_exact_13_for_minimal(self):
        assert fodt_min_block_text_length(_MINIMAL) == 13

    def test_exact_20_for_list(self):
        assert fodt_min_block_text_length(_LIST) == 20

    def test_exact_11_for_headings(self):
        assert fodt_min_block_text_length(_HEADINGS) == 11

    def test_positive(self):
        assert fodt_min_block_text_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_min_block_text_length(_MINIMAL) == fodt_min_block_text_length(_MINIMAL)
