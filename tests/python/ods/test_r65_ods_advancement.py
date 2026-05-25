"""
test_r65_ods_advancement.py -- R65 Train I: ODS format track advancement.

New capability: ods_formula_cell_count(ods_doc) -- count of cells containing formulas.

R65 Sprint: Train I -- ODS stats module expansion
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.ods.ods_stats import ods_formula_cell_count


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

def _make_ods(sheets_data: list) -> dict:
    """Build a minimal ODS document dict."""
    sheets = []
    for item in sheets_data:
        sheet = {"name": item["name"], "rows": []}
        for row_cells in item.get("rows", []):
            sheet["rows"].append({"cells": row_cells})
        sheets.append(sheet)
    return {"sheets": sheets}


# ---------------------------------------------------------------------------
# ods_formula_cell_count tests
# ---------------------------------------------------------------------------

class TestOdsFormulaCellCount:
    """Tests for ods_formula_cell_count()."""

    def test_empty_document(self):
        doc = {"sheets": []}
        assert ods_formula_cell_count(doc) == 0

    def test_no_formula_cells(self):
        doc = _make_ods([{
            "name": "Sheet1",
            "rows": [[{"value": 1}, {"value": "text"}]],
        }])
        assert ods_formula_cell_count(doc) == 0

    def test_one_formula_cell(self):
        doc = _make_ods([{
            "name": "Sheet1",
            "rows": [[{"value": 3, "formula": "=A1+A2"}, {"value": "text"}]],
        }])
        assert ods_formula_cell_count(doc) == 1

    def test_multiple_formula_cells(self):
        doc = _make_ods([{
            "name": "Sheet1",
            "rows": [
                [{"value": 3, "formula": "=A1+A2"}, {"value": 5, "formula": "=SUM(A1:A3)"}],
                [{"value": 10, "formula": "=B1*2"}],
            ],
        }])
        assert ods_formula_cell_count(doc) == 3

    def test_formula_across_sheets(self):
        doc = _make_ods([
            {"name": "S1", "rows": [[{"value": 1, "formula": "=1"}]]},
            {"name": "S2", "rows": [[{"value": 2, "formula": "=2"}]]},
        ])
        assert ods_formula_cell_count(doc) == 2

    def test_formula_none_not_counted(self):
        doc = _make_ods([{
            "name": "Sheet1",
            "rows": [[{"value": 1, "formula": None}, {"value": 2}]],
        }])
        assert ods_formula_cell_count(doc) == 0

    def test_mixed_formula_and_value_cells(self):
        doc = _make_ods([{
            "name": "Sheet1",
            "rows": [
                [{"value": "text"}, {"value": 10, "formula": "=SUM(A:A)"}, {"value": None}],
            ],
        }])
        assert ods_formula_cell_count(doc) == 1

    def test_returns_int(self):
        doc = _make_ods([{"name": "S1", "rows": [[{"value": 1}]]}])
        result = ods_formula_cell_count(doc)
        assert isinstance(result, int)
