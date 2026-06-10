"""
test_r163_fodt_stats_wordcount.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT25-001
Added: 2026-06-10

Tests for FODT APIs:
- document_stats(document) -> dict
- document_word_count(document) -> dict
- document_text_content(document, separator) -> str
- document_heading_outline(document) -> list[dict]

Authority: P4 (FODT neutral model)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_stats,
    document_word_count,
    document_text_content,
    document_heading_outline,
)


def _block(text, btype="paragraph", style=None, lang=None, heading_level=None):
    b = {"type": btype, "text": text, "runs": [{"text": text}]}
    if style:
        b["style"] = style
    if lang:
        b["language"] = lang
    if heading_level is not None:
        b["heading_level"] = heading_level
    return b


def _heading(text, level=1):
    return _block(text, btype="heading", heading_level=level)


def _doc(blocks=None, lists=None, tables=None, meta=None):
    d = {
        "format_id": "fodt",
        "blocks": blocks or [],
        "lists": lists or [],
        "tables": tables or [],
    }
    if meta:
        d["meta"] = meta
    return d


# ── document_stats ──────────────────────────────────────────────────────

class TestDocumentStats:

    def test_empty_document(self):
        result = document_stats(_doc())
        assert result["block_count"] == 0
        assert result["paragraph_count"] == 0
        assert result["heading_count"] == 0
        assert result["list_count"] == 0
        assert result["table_count"] == 0
        assert result["total_text_length"] == 0

    def test_paragraphs_counted(self):
        doc = _doc(blocks=[_block("Hello"), _block("World")])
        result = document_stats(doc)
        assert result["block_count"] == 2
        assert result["paragraph_count"] == 2
        assert result["heading_count"] == 0

    def test_headings_counted(self):
        doc = _doc(blocks=[_heading("Title", 1), _heading("Sub", 2)])
        result = document_stats(doc)
        assert result["heading_count"] == 2
        assert result["block_count"] == 2

    def test_text_length(self):
        doc = _doc(blocks=[_block("Hello")])
        result = document_stats(doc)
        assert result["total_text_length"] == 5

    def test_lists_counted(self):
        doc = _doc(lists=[
            {"items": [{"text": "item1"}, {"text": "item2"}]},
        ])
        result = document_stats(doc)
        assert result["list_count"] == 1
        assert result["list_item_count"] == 2

    def test_tables_counted(self):
        doc = _doc(tables=[
            {"rows": [{"cells": [{"text": "a"}, {"text": "b"}]}]},
        ])
        result = document_stats(doc)
        assert result["table_count"] == 1
        assert result["table_cell_count"] == 2

    def test_hyperlinks_counted(self):
        doc = _doc(blocks=[{
            "type": "paragraph",
            "text": "click here",
            "runs": [{"text": "click here", "href": "http://example.com"}],
        }])
        result = document_stats(doc)
        assert result["hyperlink_count"] == 1

    def test_mixed_content(self):
        doc = _doc(
            blocks=[_block("para"), _heading("title", 1)],
            lists=[{"items": [{"text": "a"}]}],
            tables=[{"rows": [{"cells": [{"text": "c"}]}]}],
        )
        result = document_stats(doc)
        assert result["paragraph_count"] == 1
        assert result["heading_count"] == 1
        assert result["list_count"] == 1
        assert result["table_count"] == 1


# ── document_word_count ─────────────────────────────────────────────────

class TestDocumentWordCount:

    def test_empty_document(self):
        result = document_word_count(_doc())
        assert result["total_words"] == 0
        assert result["block_words"] == 0
        assert result["list_words"] == 0
        assert result["table_words"] == 0

    def test_block_words(self):
        doc = _doc(blocks=[_block("hello world foo")])
        result = document_word_count(doc)
        assert result["block_words"] == 3
        assert result["total_words"] == 3

    def test_list_words(self):
        doc = _doc(lists=[{"items": [{"text": "one two"}, {"text": "three"}]}])
        result = document_word_count(doc)
        assert result["list_words"] == 3

    def test_table_words(self):
        doc = _doc(tables=[{"rows": [{"cells": [{"text": "a b c"}]}]}])
        result = document_word_count(doc)
        assert result["table_words"] == 3

    def test_total_is_sum(self):
        doc = _doc(
            blocks=[_block("one two")],
            lists=[{"items": [{"text": "three"}]}],
            tables=[{"rows": [{"cells": [{"text": "four five"}]}]}],
        )
        result = document_word_count(doc)
        assert result["total_words"] == 5
        assert result["block_words"] == 2
        assert result["list_words"] == 1
        assert result["table_words"] == 2

    def test_empty_text(self):
        doc = _doc(blocks=[_block("")])
        result = document_word_count(doc)
        assert result["block_words"] == 0


# ── document_text_content ───────────────────────────────────────────────

class TestDocumentTextContent:

    def test_empty_document(self):
        assert document_text_content(_doc()) == ""

    def test_single_paragraph(self):
        doc = _doc(blocks=[_block("Hello world")])
        assert "Hello world" in document_text_content(doc)

    def test_separator(self):
        doc = _doc(blocks=[_block("A"), _block("B")])
        result = document_text_content(doc, separator=" | ")
        assert " | " in result

    def test_includes_list_text(self):
        doc = _doc(lists=[{"items": [{"text": "item1"}]}])
        assert "item1" in document_text_content(doc)

    def test_includes_table_text(self):
        doc = _doc(tables=[{"rows": [{"cells": [{"text": "cell1"}]}]}])
        assert "cell1" in document_text_content(doc)


# ── document_heading_outline ────────────────────────────────────────────

class TestDocumentHeadingOutline:

    def test_empty_document(self):
        assert document_heading_outline(_doc()) == []

    def test_no_headings(self):
        doc = _doc(blocks=[_block("just a paragraph")])
        assert document_heading_outline(doc) == []

    def test_single_heading(self):
        doc = _doc(blocks=[_heading("Title", 1)])
        result = document_heading_outline(doc)
        assert len(result) == 1
        assert result[0]["level"] == 1
        assert result[0]["text"] == "Title"
        assert result[0]["index"] == 0

    def test_multiple_headings(self):
        doc = _doc(blocks=[
            _heading("H1", 1),
            _block("paragraph"),
            _heading("H2", 2),
            _heading("H3", 3),
        ])
        result = document_heading_outline(doc)
        assert len(result) == 3
        assert result[0]["text"] == "H1"
        assert result[1]["text"] == "H2"
        assert result[2]["text"] == "H3"
        assert result[0]["index"] == 0
        assert result[1]["index"] == 1
        assert result[2]["index"] == 2

    def test_heading_levels_preserved(self):
        doc = _doc(blocks=[_heading("A", 3), _heading("B", 1)])
        result = document_heading_outline(doc)
        assert result[0]["level"] == 3
        assert result[1]["level"] == 1
