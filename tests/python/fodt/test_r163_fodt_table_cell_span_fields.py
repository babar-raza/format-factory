"""
test_r163_fodt_table_cell_span_fields.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT27-001
Added: 2026-06-10

Tests for FODT APIs:
- document_table_cell_count(document) -> dict
- document_table_cell_span_summary(document) -> dict
- document_text_field_warnings(document) -> list[str]
- document_paragraph_style_distribution(document) -> dict

Authority: P4 (FODT neutral model)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_table_cell_count,
    document_table_cell_span_summary,
    document_text_field_warnings,
    document_paragraph_style_distribution,
)


def _block(text, btype="paragraph", style=None, fields=None):
    b = {"type": btype, "text": text, "runs": [{"text": text}]}
    if style:
        b["style"] = style
    if fields:
        b["fields"] = fields
    return b


def _doc(blocks=None, lists=None, tables=None):
    return {
        "format_id": "fodt",
        "blocks": blocks or [],
        "lists": lists or [],
        "tables": tables or [],
    }


# ── document_table_cell_count ───────────────────────────────────────────

class TestDocumentTableCellCount:

    def test_empty_document(self):
        result = document_table_cell_count(_doc())
        assert result["total_cells"] == 0
        assert result["total_tables"] == 0
        assert result["per_table"] == []

    def test_single_table(self):
        doc = _doc(tables=[
            {"rows": [
                {"cells": [{"text": "a"}, {"text": "b"}]},
                {"cells": [{"text": "c"}, {"text": "d"}]},
            ]},
        ])
        result = document_table_cell_count(doc)
        assert result["total_cells"] == 4
        assert result["total_tables"] == 1
        assert result["per_table"][0]["cell_count"] == 4
        assert result["per_table"][0]["row_count"] == 2
        assert result["per_table"][0]["avg_cells_per_row"] == 2.0

    def test_multiple_tables(self):
        doc = _doc(tables=[
            {"rows": [{"cells": [{"text": "x"}]}]},
            {"rows": [{"cells": [{"text": "a"}, {"text": "b"}, {"text": "c"}]}]},
        ])
        result = document_table_cell_count(doc)
        assert result["total_cells"] == 4
        assert result["total_tables"] == 2

    def test_empty_table(self):
        doc = _doc(tables=[{"rows": []}])
        result = document_table_cell_count(doc)
        assert result["per_table"][0]["cell_count"] == 0
        assert result["per_table"][0]["avg_cells_per_row"] == 0.0


# ── document_table_cell_span_summary ────────────────────────────────────

class TestDocumentTableCellSpanSummary:

    def test_empty_document(self):
        result = document_table_cell_span_summary(_doc())
        assert result["total_cells"] == 0
        assert result["cells_with_colspan"] == 0
        assert result["cells_with_rowspan"] == 0

    def test_no_spans(self):
        doc = _doc(tables=[{"rows": [{"cells": [{"text": "a"}, {"text": "b"}]}]}])
        result = document_table_cell_span_summary(doc)
        assert result["total_cells"] == 2
        assert result["cells_with_colspan"] == 0

    def test_colspan(self):
        doc = _doc(tables=[{"rows": [{"cells": [
            {"text": "merged", "colspan": 2},
            {"text": "normal"},
        ]}]}])
        result = document_table_cell_span_summary(doc)
        assert result["cells_with_colspan"] == 1

    def test_rowspan(self):
        doc = _doc(tables=[{"rows": [{"cells": [
            {"text": "tall", "rowspan": 3},
        ]}]}])
        result = document_table_cell_span_summary(doc)
        assert result["cells_with_rowspan"] == 1

    def test_mixed_spans(self):
        doc = _doc(tables=[{"rows": [{"cells": [
            {"text": "a", "colspan": 2, "rowspan": 2},
            {"text": "b"},
        ]}]}])
        result = document_table_cell_span_summary(doc)
        assert result["cells_with_colspan"] == 1
        assert result["cells_with_rowspan"] == 1


# ── document_text_field_warnings ────────────────────────────────────────

class TestDocumentTextFieldWarnings:

    def test_empty_document(self):
        assert document_text_field_warnings(_doc()) == []

    def test_no_fields(self):
        doc = _doc(blocks=[_block("plain text")])
        assert document_text_field_warnings(doc) == []

    def test_with_fields(self):
        doc = _doc(blocks=[_block("text", fields=[{"type": "date"}])])
        result = document_text_field_warnings(doc)
        assert len(result) >= 1

    def test_multiple_field_types(self):
        doc = _doc(blocks=[
            _block("t1", fields=[{"type": "date"}]),
            _block("t2", fields=[{"type": "placeholder"}]),
        ])
        result = document_text_field_warnings(doc)
        assert len(result) >= 2


# ── document_paragraph_style_distribution ───────────────────────────────

class TestDocumentParagraphStyleDistribution:

    def test_empty_document(self):
        result = document_paragraph_style_distribution(_doc())
        assert result["style_count"] == 0

    def test_no_styles(self):
        doc = _doc(blocks=[_block("text")])
        result = document_paragraph_style_distribution(doc)
        assert result["style_count"] >= 1
        assert "Default" in result["distribution"]

    def test_with_styles(self):
        doc = _doc(blocks=[
            _block("a", style="Normal"),
            _block("b", style="Normal"),
            _block("c", style="Heading1"),
        ])
        result = document_paragraph_style_distribution(doc)
        assert result["distribution"]["Normal"] == 2
        assert result["distribution"]["Heading1"] == 1
        assert "Heading1" in result["heading_styles"]

    def test_unstyled_defaults(self):
        doc = _doc(blocks=[_block("no style"), _block("also no style")])
        result = document_paragraph_style_distribution(doc)
        assert result["distribution"]["Default"] == 2
