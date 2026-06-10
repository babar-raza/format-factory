"""
test_r163_fods_col_style_validation.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT28-001
Added: 2026-06-10

Tests for FODS APIs:
- workbook_column_style_summary(workbook) -> dict[str, list[str]]
- workbook_style_family_list(workbook) -> list[dict]
- workbook_data_validation_summary(workbook) -> dict
- workbook_column_width_summary(workbook) -> list[dict]

Authority: P6 (FACT-FODS-001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import (
    workbook_column_style_summary,
    workbook_style_family_list,
    workbook_data_validation_summary,
    workbook_column_width_summary,
)


def _cell(value=None, value_type="string"):
    return {"value": value, "value_type": value_type}


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows, index=0, columns=None):
    s = {"name": name, "rows": rows, "index": index}
    if columns:
        s["columns"] = columns
    return s


def _workbook(sheets, **kwargs):
    wb = {"sheets": sheets}
    wb.update(kwargs)
    return wb


# ── workbook_column_style_summary ───────────────────────────────────────

class TestWorkbookColumnStyleSummary:

    def test_empty_workbook(self):
        assert workbook_column_style_summary(_workbook([])) == {}

    def test_no_column_styles(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        result = workbook_column_style_summary(wb)
        assert result["S1"] == []

    def test_explicit_column_styles(self):
        wb = _workbook([_sheet("S1", [], columns=[
            {"style": "col-bold"},
            {"style": "col-normal"},
        ])])
        result = workbook_column_style_summary(wb)
        assert result["S1"] == ["col-bold", "col-normal"]

    def test_fallback_cell_column_style(self):
        wb = _workbook([_sheet("S1", [
            _row([{**_cell("a"), "column_style": "cs1"}, _cell("b")]),
        ])])
        result = workbook_column_style_summary(wb)
        assert result["S1"] == ["cs1"]


# ── workbook_style_family_list ──────────────────────────────────────────

class TestWorkbookStyleFamilyList:

    def test_empty_workbook(self):
        assert workbook_style_family_list(_workbook([])) == []

    def test_no_style_metadata(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        assert workbook_style_family_list(wb) == []

    def test_auto_styles_list(self):
        wb = _workbook([], auto_styles=[
            {"family": "table-cell"},
            {"family": "table-cell"},
            {"family": "table"},
        ])
        result = workbook_style_family_list(wb)
        families = {r["family_name"]: r["style_count"] for r in result}
        assert families["table-cell"] == 2
        assert families["table"] == 1

    def test_styles_dict(self):
        wb = _workbook([], styles={"paragraph": 3, "text": 1})
        result = workbook_style_family_list(wb)
        families = {r["family_name"]: r["style_count"] for r in result}
        assert families["paragraph"] == 3
        assert families["text"] == 1


# ── workbook_data_validation_summary ────────────────────────────────────

class TestWorkbookDataValidationSummary:

    def test_empty_workbook(self):
        result = workbook_data_validation_summary(_workbook([]))
        assert result["validation_count"] == 0
        assert result["validated_cell_ranges"] == []

    def test_no_validations(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        result = workbook_data_validation_summary(wb)
        assert result["validation_count"] == 0

    def test_explicit_validations(self):
        wb = _workbook([], data_validations=[
            {"cell_range": "Sheet1.A1:A10"},
            {"cell_range": "Sheet1.B1:B5"},
        ])
        result = workbook_data_validation_summary(wb)
        assert result["validation_count"] == 2
        assert len(result["validated_cell_ranges"]) == 2

    def test_cell_level_validation(self):
        wb = _workbook([_sheet("S1", [
            _row([{**_cell("a"), "validation": "val1"}]),
        ])])
        result = workbook_data_validation_summary(wb)
        assert "val1" in result["validated_cell_ranges"]


# ── workbook_column_width_summary ───────────────────────────────────────

class TestWorkbookColumnWidthSummary:

    def test_empty_workbook(self):
        assert workbook_column_width_summary(_workbook([])) == []

    def test_no_columns(self):
        wb = _workbook([_sheet("S1", [_row([_cell("a")])])])
        result = workbook_column_width_summary(wb)
        assert len(result) == 1
        assert result[0]["column_count"] == 0
        assert result[0]["widths"] == []

    def test_with_widths(self):
        wb = _workbook([_sheet("S1", [], columns=[
            {"column_width": "2.5cm"},
            {"column_width": "3cm"},
        ])])
        result = workbook_column_width_summary(wb)
        assert result[0]["column_count"] == 2
        assert result[0]["widths"] == ["2.5cm", "3cm"]

    def test_mixed_widths(self):
        wb = _workbook([_sheet("S1", [], columns=[
            {"column_width": "2cm"},
            {},
        ])])
        result = workbook_column_width_summary(wb)
        assert result[0]["column_count"] == 1
        assert result[0]["widths"] == ["2cm", None]
