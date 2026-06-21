"""Tests for FODT Sprint 57 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_WORD_PE-001   (Fodt Word Per Heading)
  GAP-FODT-FOSS-FODT_BLOCK_T-001   (Fodt Block Text Sum)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_word_per_heading, fodt_block_text_sum

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_LIST = str(_DIR / "list-basic.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_TABLE = str(_DIR / "table-basic.fodt")


class TestFodtWordPerHeading:
    def test_return_type(self):
        assert isinstance(fodt_word_per_heading(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert fodt_word_per_heading(_MINIMAL) == 0.0

    def test_zero_for_list(self):
        assert fodt_word_per_heading(_LIST) == 0.0

    def test_zero_for_table(self):
        assert fodt_word_per_heading(_TABLE) == 0.0

    def test_nonzero_for_headings(self):
        assert fodt_word_per_heading(_HEADINGS) == pytest.approx(2.333333, rel=1e-3)

    def test_nonnegative(self):
        assert fodt_word_per_heading(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_word_per_heading(_MINIMAL) == fodt_word_per_heading(_MINIMAL)


class TestFodtBlockTextSum:
    def test_return_type(self):
        assert isinstance(fodt_block_text_sum(_MINIMAL), int)

    def test_exact_13_for_minimal(self):
        assert fodt_block_text_sum(_MINIMAL) == 13

    def test_exact_42_for_list(self):
        assert fodt_block_text_sum(_LIST) == 42

    def test_exact_275_for_headings(self):
        assert fodt_block_text_sum(_HEADINGS) == 275

    def test_exact_41_for_table(self):
        assert fodt_block_text_sum(_TABLE) == 41

    def test_positive(self):
        assert fodt_block_text_sum(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_block_text_sum(_MINIMAL) == fodt_block_text_sum(_MINIMAL)
