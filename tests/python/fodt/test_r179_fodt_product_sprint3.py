"""
test_r179_fodt_product_sprint3.py -- Tests for 3 new FODT product functions.

Coverage:
  - document_paragraph_texts: returns list[str] of paragraph texts only
  - document_heading_texts: returns list[str] of heading texts in order
  - document_table_row_count: returns row count for specified table index

Sprint: FORMAT-FACTORY-SAL-PHASE3-PRODUCT-DEEPENING-SPRINT3-001
Closes gaps: GAP-FODT-FOSS-PARAGRAPH_TE-001, GAP-FODT-FOSS-HEADING_TE-001,
             GAP-FODT-COMM-TABLE_ROW_CO-001 (missing_test_coverage)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    parse_fodt,
    document_paragraph_texts,
    document_heading_texts,
    document_table_row_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_SAMPLES / "minimal-document.fodt")
_HEADINGS = str(_SAMPLES / "headings-and-paragraphs.fodt")
_TABLE = str(_SAMPLES / "table-basic.fodt")


def _make_doc(**kwargs):
    base = {"blocks": [], "lists": [], "tables": [], "warnings": []}
    base.update(kwargs)
    return base


def _make_block(btype, text, level=None):
    b = {"type": btype, "text": text}
    if level is not None:
        b["heading_level"] = level
    return b


# ---------------------------------------------------------------------------
# document_paragraph_texts tests
# ---------------------------------------------------------------------------

class TestDocumentParagraphTexts:
    def test_returns_list(self):
        doc = _make_doc()
        assert isinstance(document_paragraph_texts(doc), list)

    def test_empty_doc_returns_empty_list(self):
        doc = _make_doc()
        assert document_paragraph_texts(doc) == []

    def test_excludes_headings(self):
        doc = _make_doc(blocks=[
            _make_block("heading", "Title", level=1),
            _make_block("paragraph", "Para text"),
        ])
        result = document_paragraph_texts(doc)
        assert result == ["Para text"]
        assert "Title" not in result

    def test_multiple_paragraphs_in_order(self):
        doc = _make_doc(blocks=[
            _make_block("paragraph", "First"),
            _make_block("paragraph", "Second"),
            _make_block("paragraph", "Third"),
        ])
        assert document_paragraph_texts(doc) == ["First", "Second", "Third"]

    def test_mixed_blocks_only_paragraphs(self):
        doc = _make_doc(blocks=[
            _make_block("heading", "H1", level=1),
            _make_block("paragraph", "P1"),
            _make_block("heading", "H2", level=2),
            _make_block("paragraph", "P2"),
        ])
        assert document_paragraph_texts(doc) == ["P1", "P2"]

    def test_on_real_file(self):
        doc = parse_fodt(_MINIMAL)
        result = document_paragraph_texts(doc)
        assert isinstance(result, list)
        assert all(isinstance(t, str) for t in result)

    def test_runs_used_when_present(self):
        doc = _make_doc(blocks=[
            {"type": "paragraph", "text": "fallback", "runs": [
                {"text": "run1"}, {"text": " run2"}
            ]}
        ])
        result = document_paragraph_texts(doc)
        assert result == ["run1 run2"]


# ---------------------------------------------------------------------------
# document_heading_texts tests
# ---------------------------------------------------------------------------

class TestDocumentHeadingTexts:
    def test_returns_list(self):
        doc = _make_doc()
        assert isinstance(document_heading_texts(doc), list)

    def test_empty_doc_returns_empty_list(self):
        doc = _make_doc()
        assert document_heading_texts(doc) == []

    def test_excludes_paragraphs(self):
        doc = _make_doc(blocks=[
            _make_block("paragraph", "Para"),
            _make_block("heading", "Heading", level=1),
        ])
        result = document_heading_texts(doc)
        assert result == ["Heading"]
        assert "Para" not in result

    def test_multiple_headings_in_order(self):
        doc = _make_doc(blocks=[
            _make_block("heading", "Chapter 1", level=1),
            _make_block("paragraph", "Intro"),
            _make_block("heading", "Section 1.1", level=2),
        ])
        assert document_heading_texts(doc) == ["Chapter 1", "Section 1.1"]

    def test_on_headings_file(self):
        doc = parse_fodt(_HEADINGS)
        result = document_heading_texts(doc)
        assert isinstance(result, list)
        assert len(result) >= 1
        assert all(isinstance(t, str) for t in result)

    def test_headings_from_runs(self):
        doc = _make_doc(blocks=[
            {"type": "heading", "heading_level": 1, "text": "fallback",
             "runs": [{"text": "Run "}, {"text": "Heading"}]}
        ])
        result = document_heading_texts(doc)
        assert result == ["Run Heading"]


# ---------------------------------------------------------------------------
# document_table_row_count tests
# ---------------------------------------------------------------------------

class TestDocumentTableRowCount:
    def test_returns_int(self):
        doc = _make_doc(tables=[{"rows": [{"cells": [{"text": "A"}]}]}])
        assert isinstance(document_table_row_count(doc), int)

    def test_single_row(self):
        doc = _make_doc(tables=[{"rows": [{"cells": [{"text": "A"}]}]}])
        assert document_table_row_count(doc, 0) == 1

    def test_multiple_rows(self):
        rows = [{"cells": [{"text": f"R{i}"}]} for i in range(4)]
        doc = _make_doc(tables=[{"rows": rows}])
        assert document_table_row_count(doc, 0) == 4

    def test_no_tables_returns_zero(self):
        doc = _make_doc()
        assert document_table_row_count(doc, 0) == 0

    def test_out_of_range_returns_zero(self):
        doc = _make_doc(tables=[{"rows": [{"cells": [{"text": "X"}]}]}])
        assert document_table_row_count(doc, 5) == 0

    def test_negative_index_returns_zero(self):
        doc = _make_doc(tables=[{"rows": [{"cells": [{"text": "X"}]}]}])
        assert document_table_row_count(doc, -1) == 0

    def test_on_table_file(self):
        doc = parse_fodt(_TABLE)
        count = document_table_row_count(doc, 0)
        assert isinstance(count, int)
        assert count >= 1

    def test_second_table(self):
        rows1 = [{"cells": []}]
        rows2 = [{"cells": []}, {"cells": []}]
        doc = _make_doc(tables=[{"rows": rows1}, {"rows": rows2}])
        assert document_table_row_count(doc, 0) == 1
        assert document_table_row_count(doc, 1) == 2
