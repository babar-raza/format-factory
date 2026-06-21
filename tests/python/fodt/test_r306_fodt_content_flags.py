"""Tests for fodt_is_text_only and fodt_total_content_blocks (Sprint r306)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import fodt_is_text_only, fodt_total_content_blocks

_FODT = _REPO / "samples" / "by-format" / "fodt"


class TestFodtIsTextOnly:
    """Tests for fodt_is_text_only."""

    def test_minimal_is_text_only(self):
        """minimal-document.fodt has no tables/lists → True."""
        assert fodt_is_text_only(_FODT / "minimal-document.fodt") is True

    def test_headings_is_text_only(self):
        """headings-and-paragraphs.fodt has no tables/lists → True."""
        assert fodt_is_text_only(_FODT / "headings-and-paragraphs.fodt") is True

    def test_list_is_not_text_only(self):
        """list-basic.fodt has lists → False."""
        assert fodt_is_text_only(_FODT / "list-basic.fodt") is False

    def test_table_is_not_text_only(self):
        """table-basic.fodt has a table → False."""
        assert fodt_is_text_only(_FODT / "table-basic.fodt") is False

    def test_returns_bool(self):
        assert isinstance(fodt_is_text_only(_FODT / "minimal-document.fodt"), bool)

    def test_text_only_true_table_false(self):
        r1 = fodt_is_text_only(_FODT / "minimal-document.fodt")
        r2 = fodt_is_text_only(_FODT / "table-basic.fodt")
        assert r1 is True and r2 is False


class TestFodtTotalContentBlocks:
    """Tests for fodt_total_content_blocks."""

    def test_minimal_has_one_block(self):
        """minimal-document.fodt: 1 para + 0 headings + 0 tables + 0 lists = 1."""
        assert fodt_total_content_blocks(_FODT / "minimal-document.fodt") == 1

    def test_headings_has_seven_blocks(self):
        """headings-and-paragraphs.fodt: 4 paras + 3 headings = 7."""
        assert fodt_total_content_blocks(_FODT / "headings-and-paragraphs.fodt") == 7

    def test_table_basic_has_three_blocks(self):
        """table-basic.fodt: 2 paras + 1 table = 3."""
        assert fodt_total_content_blocks(_FODT / "table-basic.fodt") == 3

    def test_returns_int(self):
        assert isinstance(fodt_total_content_blocks(_FODT / "minimal-document.fodt"), int)

    def test_headings_more_than_minimal(self):
        r1 = fodt_total_content_blocks(_FODT / "minimal-document.fodt")
        r2 = fodt_total_content_blocks(_FODT / "headings-and-paragraphs.fodt")
        assert r2 > r1

    def test_all_nonnegative(self):
        for f in ["minimal-document.fodt", "headings-and-paragraphs.fodt", "table-basic.fodt"]:
            assert fodt_total_content_blocks(_FODT / f) >= 0
