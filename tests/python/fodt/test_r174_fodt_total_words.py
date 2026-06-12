"""Tests for FODT document_total_words function (rnext42)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import document_total_words


def _make_doc(blocks: list[dict]) -> dict:
    return {"format": "fodt", "blocks": blocks}


class TestDocumentTotalWords:
    def test_empty_document(self):
        doc = _make_doc([])
        assert document_total_words(doc) == 0

    def test_single_paragraph_single_word(self):
        doc = _make_doc([{"type": "paragraph", "text": "hello"}])
        assert document_total_words(doc) == 1

    def test_single_paragraph_multiple_words(self):
        doc = _make_doc([{"type": "paragraph", "text": "hello world foo"}])
        assert document_total_words(doc) == 3

    def test_multiple_paragraphs(self):
        doc = _make_doc([
            {"type": "paragraph", "text": "one two"},
            {"type": "paragraph", "text": "three four five"},
        ])
        assert document_total_words(doc) == 5

    def test_heading_counted(self):
        doc = _make_doc([{"type": "heading", "text": "Chapter One"}])
        assert document_total_words(doc) == 2

    def test_returns_int(self):
        doc = _make_doc([{"type": "paragraph", "text": "test"}])
        result = document_total_words(doc)
        assert isinstance(result, int)
