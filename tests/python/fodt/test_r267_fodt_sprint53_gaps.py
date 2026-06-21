"""Tests for FODT Sprint 53 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_AVG_BLO-001  (Fodt Avg Block Length)
  GAP-FODT-FOSS-FODT_MAX_BLO-001  (Fodt Max Block Text Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_avg_block_length, fodt_max_block_text_length

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_LIST = str(_DIR / "list-basic.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")


class TestFodtAvgBlockLength:
    def test_return_type(self):
        assert isinstance(fodt_avg_block_length(_MINIMAL), (int, float))

    def test_exact_13_for_minimal(self):
        assert fodt_avg_block_length(_MINIMAL) == 13.0

    def test_exact_21_for_list(self):
        assert fodt_avg_block_length(_LIST) == 21.0

    def test_positive_for_headings(self):
        assert fodt_avg_block_length(_HEADINGS) > 0

    def test_consistent_across_calls(self):
        assert fodt_avg_block_length(_MINIMAL) == fodt_avg_block_length(_MINIMAL)


class TestFodtMaxBlockTextLength:
    def test_return_type(self):
        assert isinstance(fodt_max_block_text_length(_MINIMAL), int)

    def test_exact_13_for_minimal(self):
        assert fodt_max_block_text_length(_MINIMAL) == 13

    def test_exact_22_for_list(self):
        assert fodt_max_block_text_length(_LIST) == 22

    def test_exact_81_for_headings(self):
        assert fodt_max_block_text_length(_HEADINGS) == 81

    def test_positive(self):
        assert fodt_max_block_text_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_max_block_text_length(_MINIMAL) == fodt_max_block_text_length(_MINIMAL)
