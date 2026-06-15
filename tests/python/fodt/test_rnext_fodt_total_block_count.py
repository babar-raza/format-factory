"""Tests for fodt_total_block_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_total_block_count
from fodt.parser import parse_fodt_strict

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"


class TestFodtTotalBlockCount:
    def test_empty_document(self):
        doc = {"blocks": [], "lists": [], "tables": []}
        assert fodt_total_block_count(doc) == 0

    def test_blocks_only(self):
        doc = {"blocks": [{"type": "paragraph"}, {"type": "heading"}]}
        assert fodt_total_block_count(doc) == 2

    def test_all_types(self):
        doc = {
            "blocks": [{"type": "paragraph"}],
            "lists": [{"items": []}],
            "tables": [{"rows": []}],
        }
        assert fodt_total_block_count(doc) == 3

    def test_missing_keys(self):
        doc = {}
        assert fodt_total_block_count(doc) == 0

    def test_minimal_sample(self):
        doc = parse_fodt_strict(str(_SAMPLES / "minimal-document.fodt"))
        count = fodt_total_block_count(doc)
        assert isinstance(count, int)
        assert count >= 1

    def test_headings_sample(self):
        doc = parse_fodt_strict(str(_SAMPLES / "headings-and-paragraphs.fodt"))
        count = fodt_total_block_count(doc)
        assert count >= 2  # has both headings and paragraphs

    def test_table_sample(self):
        doc = parse_fodt_strict(str(_SAMPLES / "table-basic.fodt"))
        count = fodt_total_block_count(doc)
        assert count >= 1  # has at least the table

    def test_return_type(self):
        doc = {"blocks": [{"type": "paragraph"}]}
        assert isinstance(fodt_total_block_count(doc), int)

    def test_importable_from_package(self):
        from fodt import fodt_total_block_count as fn
        assert callable(fn)
