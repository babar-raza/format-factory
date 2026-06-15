"""Tests for FODS domain classes (FodsDocument, FodsSheet, FodsCell).

TC-GAP-B01: Proves domain classes wrap the dict-based neutral model correctly.
"""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.models import FodsDocument, FodsSheet, FodsCell


def _sample_workbook():
    return {
        "format_id": "fods",
        "odf_version": "1.3",
        "warnings": [],
        "sheets": [
            {
                "name": "Sheet1",
                "rows": [
                    [
                        {"value": "Hello", "value_type": "string", "text": "Hello"},
                        {"value": 42.0, "value_type": "float", "text": "42"},
                    ],
                    [
                        {"value": True, "value_type": "boolean", "text": "TRUE"},
                        {"value": None, "value_type": "", "text": ""},
                    ],
                ],
            },
            {
                "name": "Sheet2",
                "rows": [],
            },
        ],
    }


class TestFodsDocument:
    def test_basic_properties(self):
        doc = FodsDocument(_sample_workbook())
        assert doc.format_id == "fods"
        assert doc.odf_version == "1.3"
        assert doc.sheet_count == 2

    def test_sheets_returns_sheet_objects(self):
        doc = FodsDocument(_sample_workbook())
        sheets = doc.sheets()
        assert len(sheets) == 2
        assert isinstance(sheets[0], FodsSheet)
        assert sheets[0].name == "Sheet1"

    def test_sheet_by_name(self):
        doc = FodsDocument(_sample_workbook())
        s = doc.sheet_by_name("Sheet2")
        assert s is not None
        assert s.name == "Sheet2"
        assert doc.sheet_by_name("Nonexistent") is None


class TestFodsSheet:
    def test_row_count_and_cells(self):
        sheet = FodsSheet(_sample_workbook()["sheets"][0])
        assert sheet.row_count == 2
        cells = list(sheet.cells())
        assert len(cells) == 4
        assert isinstance(cells[0], FodsCell)

    def test_cell_at(self):
        sheet = FodsSheet(_sample_workbook()["sheets"][0])
        c = sheet.cell_at(0, 1)
        assert c is not None
        assert c.value == 42.0
        assert sheet.cell_at(99, 99) is None


class TestFodsCell:
    def test_properties(self):
        cell = FodsCell({"value": "Hello", "value_type": "string", "text": "Hello"})
        assert cell.value == "Hello"
        assert cell.value_type == "string"
        assert cell.text == "Hello"
        assert cell.formula is None
        assert cell.repeated == 1
