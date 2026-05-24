"""
test_r59_fodt_deepening.py — R59 Train G: FODT product deepening.

New capabilities tested:
1. document_heading_outline() — ordered heading list for TOC generation
2. document_text_content()    — full text extraction as single string

R59 Sprint: FORMAT-FACTORY-R59-CLEAN-RC-CLOSURE-PACKAGING-NORMALIZATION-PHASE10-PRODUCT-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from fodt.neutral_model import (
    document_heading_outline,
    document_text_content,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_document(blocks=None, lists=None, tables=None, content=None):
    doc = {
        "format_id": "fodt",
        "spec_version": "1.3",
        "odf_version_attr": "1.3",
        "mimetype": None,
        "blocks": blocks or [],
        "lists": lists or [],
        "tables": tables or [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }
    if content is not None:
        doc["content"] = content
    return doc


def _block(btype, text, level=None):
    b = {"type": btype, "text": text}
    if level is not None:
        b["heading_level"] = level
    return b


def _list(items):
    return {"items": [{"text": t, "level": 1} for t in items]}


def _table(rows):
    return {"rows": [{"cells": [{"text": c} for c in row]} for row in rows]}


# ---------------------------------------------------------------------------
# document_heading_outline tests
# ---------------------------------------------------------------------------

class TestDocumentHeadingOutline:

    def test_empty_document_returns_empty_outline(self):
        doc = _make_document()
        assert document_heading_outline(doc) == []

    def test_no_headings_returns_empty(self):
        doc = _make_document(blocks=[
            _block("paragraph", "Some text"),
            _block("paragraph", "More text"),
        ])
        assert document_heading_outline(doc) == []

    def test_single_heading(self):
        doc = _make_document(blocks=[_block("heading", "Introduction", level=1)])
        outline = document_heading_outline(doc)
        assert len(outline) == 1
        assert outline[0] == {"level": 1, "text": "Introduction", "index": 0}

    def test_multiple_headings_in_order(self):
        doc = _make_document(blocks=[
            _block("heading", "Chapter 1", level=1),
            _block("paragraph", "Some text"),
            _block("heading", "Section 1.1", level=2),
            _block("heading", "Chapter 2", level=1),
        ])
        outline = document_heading_outline(doc)
        assert len(outline) == 3
        assert outline[0] == {"level": 1, "text": "Chapter 1", "index": 0}
        assert outline[1] == {"level": 2, "text": "Section 1.1", "index": 1}
        assert outline[2] == {"level": 1, "text": "Chapter 2", "index": 2}

    def test_heading_indexes_are_sequential(self):
        doc = _make_document(blocks=[
            _block("heading", f"H{i}", level=1) for i in range(5)
        ])
        outline = document_heading_outline(doc)
        assert [o["index"] for o in outline] == list(range(5))

    def test_respects_content_list_order(self):
        """When content list present, headings come from content, not blocks."""
        content = [
            {"kind": "block", "data": _block("paragraph", "Intro")},
            {"kind": "block", "data": _block("heading", "From Content", level=2)},
            {"kind": "list", "data": _list(["item1"])},
        ]
        # Blocks list has a heading too — should NOT appear since content overrides
        doc = _make_document(
            blocks=[_block("heading", "From Blocks", level=1)],
            content=content,
        )
        outline = document_heading_outline(doc)
        assert len(outline) == 1
        assert outline[0]["text"] == "From Content"

    def test_paragraphs_excluded(self):
        """Paragraphs must not appear in outline."""
        doc = _make_document(blocks=[
            _block("paragraph", "Not a heading"),
            _block("heading", "Real Heading", level=3),
        ])
        outline = document_heading_outline(doc)
        assert len(outline) == 1
        assert outline[0]["level"] == 3

    def test_heading_levels_preserved(self):
        levels = [1, 2, 3, 4, 5, 6]
        blocks = [_block("heading", f"Level {l}", level=l) for l in levels]
        doc = _make_document(blocks=blocks)
        outline = document_heading_outline(doc)
        assert [o["level"] for o in outline] == levels


# ---------------------------------------------------------------------------
# document_text_content tests
# ---------------------------------------------------------------------------

class TestDocumentTextContent:

    def test_empty_document_returns_empty_string(self):
        doc = _make_document()
        assert document_text_content(doc) == ""

    def test_single_paragraph_text(self):
        doc = _make_document(blocks=[_block("paragraph", "Hello world")])
        assert document_text_content(doc) == "Hello world"

    def test_multiple_blocks_joined_by_newline(self):
        doc = _make_document(blocks=[
            _block("paragraph", "First"),
            _block("paragraph", "Second"),
        ])
        result = document_text_content(doc)
        assert "First" in result
        assert "Second" in result
        assert result == "First\nSecond"

    def test_custom_separator(self):
        doc = _make_document(blocks=[
            _block("paragraph", "A"),
            _block("paragraph", "B"),
        ])
        result = document_text_content(doc, separator=" | ")
        assert result == "A | B"

    def test_list_items_included(self):
        doc = _make_document(lists=[_list(["item1", "item2"])])
        result = document_text_content(doc)
        assert "item1" in result
        assert "item2" in result

    def test_table_cells_included(self):
        doc = _make_document(tables=[_table([["Cell A", "Cell B"], ["Cell C", "Cell D"]])])
        result = document_text_content(doc)
        assert "Cell A" in result
        assert "Cell D" in result

    def test_blocks_lists_tables_all_combined(self):
        doc = _make_document(
            blocks=[_block("paragraph", "Para text")],
            lists=[_list(["list item"])],
            tables=[_table([["table cell"]])],
        )
        result = document_text_content(doc)
        assert "Para text" in result
        assert "list item" in result
        assert "table cell" in result

    def test_respects_content_list(self):
        """When content list present, extracts from content, not separate lists."""
        content = [
            {"kind": "block", "data": _block("paragraph", "Content Para")},
            {"kind": "list", "data": _list(["Content Item"])},
        ]
        doc = _make_document(
            blocks=[_block("paragraph", "Legacy Para")],
            content=content,
        )
        result = document_text_content(doc)
        assert "Content Para" in result
        assert "Content Item" in result
        assert "Legacy Para" not in result

    def test_empty_texts_not_included(self):
        """Empty string text fields must not produce extra separators."""
        doc = _make_document(blocks=[
            _block("paragraph", ""),
            _block("paragraph", "Real"),
        ])
        result = document_text_content(doc)
        # Only "Real" should appear; empty block should be skipped
        assert result == "Real"
