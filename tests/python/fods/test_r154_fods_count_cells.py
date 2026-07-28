"""
test_r154_fods_count_cells.py

Sprint: FORMAT-FACTORY-AUTHORITY-GATED-PRODUCT-DOGFOOD-FEATURES-AND-BACKFILL-001
Added: 2026-06-09

Tests for FODS workbook_count_matching_cells() API.
Authority: P6 (SAL-FODS-00001: ODF 1.3 spreadsheet MIME type)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.fods.neutral_model import workbook_count_matching_cells


def _cell(value=None):
    return {"value": value}


def _row(cells):
    return {"cells": cells}


def _sheet(name, rows):
    return {"name": name, "rows": rows}


def _wb(sheets):
    return {"sheets": sheets}


class TestWorkbookCountMatchingCells:
    """workbook_count_matching_cells: count cells matching a value."""

    def test_empty_workbook_returns_zero(self):
        assert workbook_count_matching_cells(_wb([]), "x") == 0

    def test_single_match_returns_one(self):
        wb = _wb([_sheet("S", [_row([_cell("target")])])])
        assert workbook_count_matching_cells(wb, "target") == 1

    def test_multiple_matches_returns_correct_count(self):
        wb = _wb([_sheet("S", [
            _row([_cell("alpha"), _cell("beta"), _cell("alpha")]),
        ])])
        assert workbook_count_matching_cells(wb, "alpha") == 2

    def test_count_across_sheets(self):
        wb = _wb([
            _sheet("S1", [_row([_cell("x")])]),
            _sheet("S2", [_row([_cell("x")])]),
            _sheet("S3", [_row([_cell("y")])]),
        ])
        assert workbook_count_matching_cells(wb, "x") == 2

    def test_no_match_returns_zero(self):
        wb = _wb([_sheet("S", [_row([_cell("a"), _cell("b")])])])
        assert workbook_count_matching_cells(wb, "z") == 0

    def test_numeric_value(self):
        wb = _wb([_sheet("S", [_row([_cell(42), _cell(99), _cell(42)])])])
        assert workbook_count_matching_cells(wb, 42) == 2

    def test_case_insensitive_default(self):
        wb = _wb([_sheet("S", [_row([_cell("Hello"), _cell("HELLO"), _cell("hello")])])])
        assert workbook_count_matching_cells(wb, "hello") == 3

    def test_case_sensitive(self):
        wb = _wb([_sheet("S", [_row([_cell("Hello"), _cell("HELLO"), _cell("hello")])])])
        assert workbook_count_matching_cells(wb, "hello", case_sensitive=True) == 1

    def test_returns_int(self):
        wb = _wb([_sheet("S", [_row([_cell("a")])])])
        result = workbook_count_matching_cells(wb, "a")
        assert isinstance(result, int)

    def test_exported_from_package(self):
        from src.python.fods import workbook_count_matching_cells as wcc
        assert callable(wcc)
