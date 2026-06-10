"""
test_r163_fodt_text_table_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT25-001
Added: 2026-06-10

Tests for FODT APIs:
- document_to_text(document) -> str
- document_get_paragraph_text(document, index) -> str|None
- document_table_summary(document) -> list[dict]

Authority: P4 (FODT neutral model)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_to_text,
    document_get_paragraph_text,
    document_table_summary,
)


def _block(text, btype="paragraph", heading_level=None):
    b = {"type": btype, "text": text}
    if heading_level is not None:
        b["heading_level"] = heading_level
        b["level"] = heading_level
    return b


def _heading(text, level=1):
    return _block(text, btype="heading", heading_level=level)


def _doc(blocks=None, lists=None, tables=None):
    return {
        "format_id": "fodt",
        "blocks": blocks or [],
        "lists": lists or [],
        "tables": tables or [],
    }


# ── document_to_text ────────────────────────────────────────────────────

class TestDocumentToText:

    def test_empty_document(self):
        assert document_to_text(_doc()) == ""

    def test_single_paragraph(self):
        doc = _doc(blocks=[_block("Hello world")])
        assert document_to_text(doc) == "Hello world"

    def test_multiple_paragraphs(self):
        doc = _doc(blocks=[_block("A"), _block("B")])
        result = document_to_text(doc)
        assert "A" in result
        assert "B" in result
        assert "\n" in result

    def test_heading_prefixed(self):
        doc = _doc(blocks=[_heading("Title", 2)])
        result = document_to_text(doc)
        assert "## Title" in result

    def test_mixed_blocks(self):
        doc = _doc(blocks=[
            _heading("Intro", 1),
            _block("Some text"),
        ])
        result = document_to_text(doc)
        assert "# Intro" in result
        assert "Some text" in result


# ── document_get_paragraph_text ─────────────────────────────────────────

class TestDocumentGetParagraphText:

    def test_empty_document(self):
        assert document_get_paragraph_text(_doc(), 0) is None

    def test_first_paragraph(self):
        doc = _doc(blocks=[_block("First"), _block("Second")])
        assert document_get_paragraph_text(doc, 0) == "First"

    def test_second_paragraph(self):
        doc = _doc(blocks=[_block("First"), _block("Second")])
        assert document_get_paragraph_text(doc, 1) == "Second"

    def test_out_of_range(self):
        doc = _doc(blocks=[_block("Only")])
        assert document_get_paragraph_text(doc, 5) is None

    def test_negative_index(self):
        doc = _doc(blocks=[_block("X")])
        assert document_get_paragraph_text(doc, -1) is None

    def test_headings_not_counted(self):
        doc = _doc(blocks=[_heading("H1", 1), _block("Para")])
        assert document_get_paragraph_text(doc, 0) == "Para"

    def test_only_headings(self):
        doc = _doc(blocks=[_heading("H1"), _heading("H2")])
        assert document_get_paragraph_text(doc, 0) is None


# ── document_table_summary ──────────────────────────────────────────────

class TestDocumentTableSummary:

    def test_empty_document(self):
        assert document_table_summary(_doc()) == []

    def test_no_tables(self):
        doc = _doc(blocks=[_block("text")])
        assert document_table_summary(doc) == []

    def test_single_table(self):
        doc = _doc(tables=[
            {"rows": [
                {"cells": [{"text": "a"}, {"text": "b"}]},
                {"cells": [{"text": "c"}, {"text": "d"}]},
            ]},
        ])
        result = document_table_summary(doc)
        assert len(result) == 1
        assert result[0]["index"] == 0
        assert result[0]["row_count"] == 2
        assert result[0]["column_count"] == 2
        assert result[0]["cell_count"] == 4

    def test_multiple_tables(self):
        doc = _doc(tables=[
            {"rows": [{"cells": [{"text": "a"}]}]},
            {"rows": [
                {"cells": [{"text": "x"}, {"text": "y"}, {"text": "z"}]},
            ]},
        ])
        result = document_table_summary(doc)
        assert len(result) == 2
        assert result[0]["column_count"] == 1
        assert result[1]["column_count"] == 3

    def test_ragged_rows(self):
        doc = _doc(tables=[
            {"rows": [
                {"cells": [{"text": "a"}, {"text": "b"}]},
                {"cells": [{"text": "c"}]},
            ]},
        ])
        result = document_table_summary(doc)
        assert result[0]["column_count"] == 2
        assert result[0]["cell_count"] == 3

    def test_empty_table(self):
        doc = _doc(tables=[{"rows": []}])
        result = document_table_summary(doc)
        assert result[0]["row_count"] == 0
        assert result[0]["cell_count"] == 0
