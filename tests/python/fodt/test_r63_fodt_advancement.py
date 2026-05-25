"""
test_r63_fodt_advancement.py — R63 Train H: FODT product advancement.

New capabilities added in R63:
1. document_heading_level_distribution(document) — heading counts by level H1-H6
2. document_table_cell_count(document)            — total cell count across all tables

These extend the R62 capabilities (document_hyperlink_count, document_footnote_count)
with structural analysis for heading hierarchy and table density.

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
Train H — FODT product advancement
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fodt.neutral_model import (
    document_heading_level_distribution,
    document_table_cell_count,
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


def _heading(level: int, text: str) -> dict:
    return {"type": "heading", "heading_level": level, "text": text}


def _paragraph(text: str) -> dict:
    return {"type": "paragraph", "text": text}


def _table(rows: list) -> dict:
    return {
        "rows": [{"cells": [{"text": c} for c in row]} for row in rows]
    }


# ---------------------------------------------------------------------------
# document_heading_level_distribution tests
# ---------------------------------------------------------------------------

class TestDocumentHeadingLevelDistribution:
    """Tests for document_heading_level_distribution()."""

    def test_empty_document(self):
        doc = _make_document()
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 0
        assert result["by_level"] == {}
        assert result["deepest_level"] is None
        assert result["shallowest_level"] is None

    def test_single_h1(self):
        doc = _make_document(blocks=[_heading(1, "Title")])
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 1
        assert result["by_level"] == {1: 1}
        assert result["shallowest_level"] == 1
        assert result["deepest_level"] == 1

    def test_multiple_heading_levels(self):
        doc = _make_document(blocks=[
            _heading(1, "Chapter 1"),
            _heading(2, "Section 1.1"),
            _heading(2, "Section 1.2"),
            _heading(3, "Subsection 1.1.1"),
        ])
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 4
        assert result["by_level"] == {1: 1, 2: 2, 3: 1}
        assert result["shallowest_level"] == 1
        assert result["deepest_level"] == 3

    def test_paragraphs_not_counted(self):
        doc = _make_document(blocks=[
            _heading(1, "H1"),
            _paragraph("Some text"),
            _heading(2, "H2"),
        ])
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 2

    def test_all_six_levels(self):
        blocks = [_heading(i, f"H{i}") for i in range(1, 7)]
        doc = _make_document(blocks=blocks)
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 6
        assert result["by_level"] == {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1}
        assert result["shallowest_level"] == 1
        assert result["deepest_level"] == 6

    def test_repeated_headings_at_same_level(self):
        doc = _make_document(blocks=[
            _heading(2, "A"), _heading(2, "B"), _heading(2, "C")
        ])
        result = document_heading_level_distribution(doc)
        assert result["by_level"] == {2: 3}
        assert result["total_headings"] == 3

    def test_invalid_heading_level_skipped(self):
        """Heading blocks with invalid level should be skipped."""
        doc = _make_document(blocks=[
            {"type": "heading", "heading_level": 7, "text": "Invalid"},
            _heading(1, "Valid"),
        ])
        result = document_heading_level_distribution(doc)
        assert result["total_headings"] == 1  # level 7 skipped

    def test_returns_correct_keys(self):
        doc = _make_document()
        result = document_heading_level_distribution(doc)
        assert "by_level" in result
        assert "total_headings" in result
        assert "deepest_level" in result
        assert "shallowest_level" in result


# ---------------------------------------------------------------------------
# document_table_cell_count tests
# ---------------------------------------------------------------------------

class TestDocumentTableCellCount:
    """Tests for document_table_cell_count()."""

    def test_empty_document_no_tables(self):
        doc = _make_document()
        result = document_table_cell_count(doc)
        assert result["total_cells"] == 0
        assert result["total_tables"] == 0
        assert result["per_table"] == []

    def test_single_table_2x2(self):
        tables = [_table([["a", "b"], ["c", "d"]])]
        doc = _make_document(tables=tables)
        result = document_table_cell_count(doc)
        assert result["total_tables"] == 1
        assert result["total_cells"] == 4
        pt = result["per_table"][0]
        assert pt["row_count"] == 2
        assert pt["cell_count"] == 4
        assert pt["avg_cells_per_row"] == 2.0

    def test_single_row_table(self):
        tables = [_table([["x", "y", "z"]])]
        doc = _make_document(tables=tables)
        result = document_table_cell_count(doc)
        assert result["total_cells"] == 3
        assert result["per_table"][0]["row_count"] == 1

    def test_multiple_tables(self):
        tables = [
            _table([["a", "b"], ["c", "d"]]),          # 4 cells
            _table([["x"], ["y"], ["z"]]),              # 3 cells
        ]
        doc = _make_document(tables=tables)
        result = document_table_cell_count(doc)
        assert result["total_tables"] == 2
        assert result["total_cells"] == 7

    def test_empty_table(self):
        tables = [{"rows": []}]
        doc = _make_document(tables=tables)
        result = document_table_cell_count(doc)
        assert result["total_cells"] == 0
        pt = result["per_table"][0]
        assert pt["row_count"] == 0
        assert pt["cell_count"] == 0
        assert pt["avg_cells_per_row"] == 0.0

    def test_table_index_is_correct(self):
        tables = [_table([["a"]]), _table([["b", "c"]])]
        doc = _make_document(tables=tables)
        result = document_table_cell_count(doc)
        assert result["per_table"][0]["table_index"] == 0
        assert result["per_table"][1]["table_index"] == 1

    def test_avg_cells_per_row_calculated(self):
        tables = [_table([["a", "b", "c"], ["d", "e", "f"]])]
        doc = _make_document(tables=tables)
        result = document_table_cell_count(doc)
        assert result["per_table"][0]["avg_cells_per_row"] == 3.0

    def test_returns_correct_keys(self):
        doc = _make_document()
        result = document_table_cell_count(doc)
        assert "total_cells" in result
        assert "total_tables" in result
        assert "per_table" in result


# ---------------------------------------------------------------------------
# API accessibility tests
# ---------------------------------------------------------------------------

class TestTrainHFodtApiAccess:
    """New R63 functions must be accessible from the fodt package."""

    def test_heading_level_distribution_callable(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_heading_level_distribution")
        assert callable(fodt.document_heading_level_distribution)

    def test_table_cell_count_callable(self):
        import src.python.fodt as fodt
        assert hasattr(fodt, "document_table_cell_count")
        assert callable(fodt.document_table_cell_count)

    def test_all_r63_new_apis_in_all(self):
        import src.python.fodt as fodt
        for api in ["document_heading_level_distribution", "document_table_cell_count"]:
            assert api in fodt.__all__, f"{api} must be in fodt.__all__"
