"""
test_r162_fodt_list_item_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22-001
Added: 2026-06-12

Tests for FODT document_list_item_count function.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_list_item_count


def _make_doc(lists):
    return {"blocks": [], "lists": lists, "tables": []}


class TestDocumentListItemCount:
    def test_no_lists(self):
        doc = _make_doc([])
        assert document_list_item_count(doc) == 0

    def test_single_list_single_item(self):
        doc = _make_doc([{"items": [{"text": "item1"}]}])
        assert document_list_item_count(doc) == 1

    def test_single_list_three_items(self):
        doc = _make_doc([{"items": [{"text": "a"}, {"text": "b"}, {"text": "c"}]}])
        assert document_list_item_count(doc) == 3

    def test_multiple_lists(self):
        doc = _make_doc([
            {"items": [{"text": "a"}, {"text": "b"}]},
            {"items": [{"text": "c"}]},
        ])
        assert document_list_item_count(doc) == 3

    def test_returns_int(self):
        doc = _make_doc([{"items": [{"text": "x"}]}])
        result = document_list_item_count(doc)
        assert isinstance(result, int)

    def test_empty_list_items(self):
        doc = _make_doc([{"items": []}])
        assert document_list_item_count(doc) == 0
