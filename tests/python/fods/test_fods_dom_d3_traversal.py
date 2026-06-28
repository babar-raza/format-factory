"""Tests for FODS DOM D3 traversal methods."""
from fods.models import FodsDocument, FodsSheet, FodsCell


def _make_workbook():
    return {
        "format_id": "fods",
        "sheets": [
            {
                "name": "Sheet1",
                "rows": [
                    {"cells": [{"value": "A1", "value_type": "string", "text": "A1"},
                               {"value": "B1", "value_type": "string", "text": "B1"}]},
                    {"cells": [{"value": 42, "value_type": "float", "text": "42"},
                               {"value": "A1", "value_type": "string", "text": "A1"}]},
                ],
            },
            {
                "name": "Sheet2",
                "rows": [
                    {"cells": [{"value": "X", "value_type": "string", "text": "X"}]},
                ],
            },
        ],
    }


def test_find_cells_by_value_returns_correct_cells():
    doc = FodsDocument(_make_workbook())
    sheet = doc.sheets()[0]
    matches = sheet.find_cells_by_value("A1")
    assert len(matches) == 2
    assert all(isinstance(c, FodsCell) for c in matches)
    assert all(c.value == "A1" for c in matches)


def test_find_cells_by_value_no_match():
    doc = FodsDocument(_make_workbook())
    sheet = doc.sheets()[0]
    matches = sheet.find_cells_by_value("nonexistent")
    assert matches == []


def test_iter_rows_yields_typed_cell_lists():
    doc = FodsDocument(_make_workbook())
    sheet = doc.sheets()[0]
    rows = list(sheet.iter_rows())
    assert len(rows) == 2
    assert len(rows[0]) == 2
    assert all(isinstance(c, FodsCell) for c in rows[0])
    assert rows[0][0].value == "A1"
    assert rows[1][0].value == 42


def test_find_sheet_by_index_returns_sheet():
    doc = FodsDocument(_make_workbook())
    sheet = doc.find_sheet_by_index(0)
    assert isinstance(sheet, FodsSheet)
    assert sheet.name == "Sheet1"


def test_find_sheet_by_index_second_sheet():
    doc = FodsDocument(_make_workbook())
    sheet = doc.find_sheet_by_index(1)
    assert isinstance(sheet, FodsSheet)
    assert sheet.name == "Sheet2"


def test_find_sheet_by_index_out_of_range():
    doc = FodsDocument(_make_workbook())
    assert doc.find_sheet_by_index(5) is None
    assert doc.find_sheet_by_index(-1) is None
