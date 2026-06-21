"""Tests for FODT Sprint 41 batch 2 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_LIST_BL-001  (Fodt List Block Count)
  GAP-FODT-FOSS-FODT_TEXT_BL-001  (Fodt Text Block Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_list_block_count, fodt_text_block_ratio

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")


class TestFodtListBlockCount:
    def test_return_type(self):
        assert isinstance(fodt_list_block_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert fodt_list_block_count(_MINIMAL) == 0

    def test_zero_for_headings(self):
        assert fodt_list_block_count(_HEADINGS) == 0

    def test_nonnegative(self):
        assert fodt_list_block_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_list_block_count(_MINIMAL) == fodt_list_block_count(_MINIMAL)


class TestFodtTextBlockRatio:
    def test_return_type(self):
        assert isinstance(fodt_text_block_ratio(_MINIMAL), float)

    def test_exact_1_0_for_minimal(self):
        assert fodt_text_block_ratio(_MINIMAL) == 1.0

    def test_nonnegative(self):
        assert fodt_text_block_ratio(_MINIMAL) >= 0.0

    def test_at_most_1(self):
        assert fodt_text_block_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert fodt_text_block_ratio(_MINIMAL) == fodt_text_block_ratio(_MINIMAL)
