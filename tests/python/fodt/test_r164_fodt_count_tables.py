"""Tests for FODT document_count_tables function (rnext34)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_count_tables


class TestDocumentCountTables:
    def _doc(self, blocks):
        return {"blocks": blocks}

    def test_no_tables(self):
        doc = self._doc([{"type": "paragraph", "text": "Hello"}])
        assert document_count_tables(doc) == 0

    def test_one_table(self):
        doc = self._doc([
            {"type": "paragraph", "text": "Before"},
            {"type": "table", "rows": []},
        ])
        assert document_count_tables(doc) == 1

    def test_multiple_tables(self):
        doc = self._doc([
            {"type": "table", "rows": []},
            {"type": "paragraph", "text": "Between"},
            {"type": "table", "rows": []},
            {"type": "table", "rows": []},
        ])
        assert document_count_tables(doc) == 3

    def test_empty_document(self):
        assert document_count_tables({"blocks": []}) == 0

    def test_no_blocks_key(self):
        assert document_count_tables({}) == 0

    def test_mixed_block_types(self):
        doc = self._doc([
            {"type": "heading", "level": 1, "text": "H"},
            {"type": "table", "rows": []},
            {"type": "list", "items": []},
        ])
        assert document_count_tables(doc) == 1
