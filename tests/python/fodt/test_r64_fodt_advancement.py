"""
test_r64_fodt_advancement.py -- R64 Train H: FODT product advancement.

New capabilities added in R64:
1. document_table_cell_span_summary(document) -- colspan/rowspan cell stats
2. document_text_field_warnings(document)      -- text field warnings list

These extend R63 capabilities (document_heading_level_distribution,
document_table_cell_count) with cell span analysis and field detection.

R64 Sprint: Train H -- FODT product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_table_cell_span_summary,
    document_text_field_warnings,
)


# ---------------------------------------------------------------------------
# Minimal document builders
# ---------------------------------------------------------------------------

def _make_document(blocks=None, tables=None, lists=None) -> dict:
    return {
        "blocks": blocks or [],
        "tables": tables or [],
        "lists": lists or [],
        "warnings": [],
        "unsupported_features": [],
        "parse_errors": [],
    }


def _table_with_spans(rows: list) -> dict:
    """Build a table where each row is a list of cell dicts."""
    return {"rows": [{"cells": row} for row in rows]}


# ---------------------------------------------------------------------------
# document_table_cell_span_summary tests
# ---------------------------------------------------------------------------

class TestDocumentTableCellSpanSummary:
    """Tests for document_table_cell_span_summary()."""

    def test_empty_document(self):
        doc = _make_document()
        result = document_table_cell_span_summary(doc)
        assert result["total_cells"] == 0
        assert result["cells_with_colspan"] == 0
        assert result["cells_with_rowspan"] == 0

    def test_no_spans(self):
        table = _table_with_spans([
            [{"text": "a"}, {"text": "b"}],
            [{"text": "c"}, {"text": "d"}],
        ])
        doc = _make_document(tables=[table])
        result = document_table_cell_span_summary(doc)
        assert result["total_cells"] == 4
        assert result["cells_with_colspan"] == 0
        assert result["cells_with_rowspan"] == 0

    def test_cell_with_colspan(self):
        table = _table_with_spans([
            [{"text": "wide", "colspan": 3}, {"text": "normal"}],
        ])
        doc = _make_document(tables=[table])
        result = document_table_cell_span_summary(doc)
        assert result["total_cells"] == 2
        assert result["cells_with_colspan"] == 1

    def test_cell_with_rowspan(self):
        table = _table_with_spans([
            [{"text": "tall", "rowspan": 2}],
            [{"text": "normal"}],
        ])
        doc = _make_document(tables=[table])
        result = document_table_cell_span_summary(doc)
        assert result["cells_with_rowspan"] == 1

    def test_cell_with_odf_namespace_span(self):
        table = _table_with_spans([
            [{"text": "merged", "table:number-columns-spanned": 2,
              "table:number-rows-spanned": 3}],
        ])
        doc = _make_document(tables=[table])
        result = document_table_cell_span_summary(doc)
        assert result["cells_with_colspan"] == 1
        assert result["cells_with_rowspan"] == 1

    def test_span_of_1_not_counted(self):
        table = _table_with_spans([
            [{"text": "x", "colspan": 1, "rowspan": 1}],
        ])
        doc = _make_document(tables=[table])
        result = document_table_cell_span_summary(doc)
        assert result["cells_with_colspan"] == 0
        assert result["cells_with_rowspan"] == 0

    def test_multiple_tables(self):
        t1 = _table_with_spans([[{"text": "a", "colspan": 2}]])
        t2 = _table_with_spans([[{"text": "b", "rowspan": 2}]])
        doc = _make_document(tables=[t1, t2])
        result = document_table_cell_span_summary(doc)
        assert result["total_cells"] == 2
        assert result["cells_with_colspan"] == 1
        assert result["cells_with_rowspan"] == 1

    def test_returns_correct_keys(self):
        doc = _make_document()
        result = document_table_cell_span_summary(doc)
        for key in ["total_cells", "cells_with_colspan", "cells_with_rowspan"]:
            assert key in result


# ---------------------------------------------------------------------------
# document_text_field_warnings tests
# ---------------------------------------------------------------------------

class TestDocumentTextFieldWarnings:
    """Tests for document_text_field_warnings()."""

    def test_empty_document(self):
        doc = _make_document()
        result = document_text_field_warnings(doc)
        assert result == []

    def test_no_fields(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "plain text", "runs": []},
        ])
        result = document_text_field_warnings(doc)
        assert result == []

    def test_placeholder_field_in_fields_list(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "fields": [{"type": "placeholder"}]},
        ])
        result = document_text_field_warnings(doc)
        assert len(result) == 1
        assert "placeholder" in result[0].lower()

    def test_date_field_in_runs(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "runs": [
                {"text": "2026-01-01", "field_type": "date"},
            ]},
        ])
        result = document_text_field_warnings(doc)
        assert len(result) == 1
        assert "date" in result[0].lower()

    def test_page_number_field(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "runs": [
                {"text": "1", "field_type": "page-number"},
            ]},
        ])
        result = document_text_field_warnings(doc)
        assert len(result) == 1
        assert "page-number" in result[0].lower()

    def test_multiple_different_field_types(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "fields": [
                {"type": "placeholder"},
                {"type": "date"},
            ]},
        ])
        result = document_text_field_warnings(doc)
        assert len(result) == 2

    def test_duplicate_field_type_not_repeated(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "fields": [
                {"type": "date"},
            ]},
            {"type": "paragraph", "text": "", "fields": [
                {"type": "date"},
            ]},
        ])
        result = document_text_field_warnings(doc)
        assert len(result) == 1  # same type only warned once

    def test_warning_message_mentions_preservation(self):
        doc = _make_document(blocks=[
            {"type": "paragraph", "text": "", "fields": [{"type": "time"}]},
        ])
        result = document_text_field_warnings(doc)
        assert "preserved" in result[0].lower() or "export" in result[0].lower()


# ---------------------------------------------------------------------------
# API accessibility tests
# ---------------------------------------------------------------------------

class TestTrainHFodtApiAccess:
    """New R64 functions must be accessible from the fodt package."""

    def test_table_cell_span_summary_callable(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_table_cell_span_summary")
        assert callable(fodt.document_table_cell_span_summary)

    def test_text_field_warnings_callable(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_text_field_warnings")
        assert callable(fodt.document_text_field_warnings)

    def test_all_r64_new_apis_in_all(self):
        import src.python.fodt as fodt
        for api in ["document_table_cell_span_summary", "document_text_field_warnings"]:
            assert api in fodt.__all__, f"{api} must be in fodt.__all__"
