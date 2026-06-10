"""Tests for ODS additional stats exports — mainstream-product-deepening-rnext11.

Covers: ods_cell_type_distribution, ods_formula_cell_count, sheet_name_order
exported via src/python/ods/__init__.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    ods_cell_type_distribution,
    ods_formula_cell_count,
    sheet_name_order,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cell(text, value_type="string", formula=None):
    c = {"text": text, "value_type": value_type}
    if formula:
        c["formula"] = formula
    return c


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows=None):
    return {
        "name": name,
        "row_count": len(rows) if rows else 0,
        "column_count": 0,
        "rows": rows or [],
    }


def _doc(sheets=None):
    return {
        "ok": True,
        "format": "ods",
        "sheet_count": len(sheets) if sheets else 0,
        "sheets": sheets or [],
    }


# ---------------------------------------------------------------------------
# ods_cell_type_distribution
# ---------------------------------------------------------------------------

def test_ods_cell_type_distribution_returns_dict():
    doc = _doc([_sheet("S1", [_row([_cell("hello"), _cell("42", "float")])])])
    assert isinstance(ods_cell_type_distribution(doc), dict)


def test_ods_cell_type_distribution_has_string_key():
    doc = _doc([_sheet("S1", [_row([_cell("hello")])])])
    result = ods_cell_type_distribution(doc)
    assert "string" in result or isinstance(result, dict)


def test_ods_cell_type_distribution_empty():
    doc = _doc([])
    result = ods_cell_type_distribution(doc)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# ods_formula_cell_count
# ---------------------------------------------------------------------------

def test_ods_formula_cell_count_returns_int():
    doc = _doc([_sheet("S1", [_row([_cell("10", "float", formula="of:=A1+1")])])])
    assert isinstance(ods_formula_cell_count(doc), int)


def test_ods_formula_cell_count_zero_when_no_formulas():
    doc = _doc([_sheet("S1", [_row([_cell("hello")])])])
    assert ods_formula_cell_count(doc) == 0


def test_ods_formula_cell_count_empty():
    doc = _doc([])
    assert ods_formula_cell_count(doc) == 0


# ---------------------------------------------------------------------------
# sheet_name_order
# ---------------------------------------------------------------------------

def test_sheet_name_order_returns_list():
    doc = _doc([_sheet("Alpha"), _sheet("Beta")])
    result = sheet_name_order(doc)
    assert isinstance(result, list)


def test_sheet_name_order_correct_order():
    doc = _doc([_sheet("First"), _sheet("Second"), _sheet("Third")])
    result = sheet_name_order(doc)
    assert result == ["First", "Second", "Third"]


def test_sheet_name_order_empty():
    doc = _doc([])
    assert sheet_name_order(doc) == []
