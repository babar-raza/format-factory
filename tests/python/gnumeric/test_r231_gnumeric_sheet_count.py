"""Tests for gnumeric_sheet_count and gnumeric_has_multiple_sheets.

Product deepening: Gnumeric analytics — TC-H3-002-GNUMERIC / PDC-GNUMERIC-SHEET-COUNT-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    gnumeric_sheet_count,
    gnumeric_has_multiple_sheets,
    create_gnumeric,
    write_gnumeric,
)

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"


def _make_gnumeric(tmp_path, name, sheets_data):
    """Create a Gnumeric file with given sheets. sheets_data: list of (sheet_name, cells_dict)."""
    from src.python.gnumeric import add_sheet, set_cell_value
    sheet_dicts = [{"name": sn} for sn, _ in sheets_data] if sheets_data else [{"name": "Sheet1"}]
    model = create_gnumeric(sheet_dicts[:1])
    for sd in sheet_dicts[1:]:
        model = add_sheet(model, sd["name"])
    for idx, (_, cells) in enumerate(sheets_data):
        for (r, c), val in cells.items():
            model = set_cell_value(model, idx, r, c, val)
    path = tmp_path / f"{name}.gnumeric"
    write_gnumeric(model, str(path))
    return path


class TestGnumericSheetCount:
    def test_single_sheet(self, tmp_path):
        f = _make_gnumeric(tmp_path, "one", [("Sheet1", {(0, 0): "a"})])
        assert gnumeric_sheet_count(f) == 1

    def test_two_sheets(self, tmp_path):
        f = _make_gnumeric(tmp_path, "two", [
            ("Sheet1", {(0, 0): "a"}),
            ("Sheet2", {(0, 0): "b"}),
        ])
        assert gnumeric_sheet_count(f) == 2

    def test_three_sheets(self, tmp_path):
        f = _make_gnumeric(tmp_path, "three", [
            ("A", {(0, 0): "1"}),
            ("B", {(0, 0): "2"}),
            ("C", {(0, 0): "3"}),
        ])
        assert gnumeric_sheet_count(f) == 3

    def test_returns_int(self, tmp_path):
        f = _make_gnumeric(tmp_path, "type", [("S", {(0, 0): "x"})])
        assert isinstance(gnumeric_sheet_count(f), int)

    def test_from_sample(self):
        path = SAMPLES / "minimal-spreadsheet.gnumeric"
        if path.exists():
            result = gnumeric_sheet_count(path)
            assert isinstance(result, int)
            assert result >= 1

    def test_empty_sheet_sample(self):
        path = SAMPLES / "empty-sheet.gnumeric"
        if path.exists():
            result = gnumeric_sheet_count(path)
            assert isinstance(result, int)
            assert result >= 1


class TestGnumericHasMultipleSheets:
    def test_single_sheet_false(self, tmp_path):
        f = _make_gnumeric(tmp_path, "single", [("Sheet1", {(0, 0): "a"})])
        assert gnumeric_has_multiple_sheets(f) is False

    def test_two_sheets_true(self, tmp_path):
        f = _make_gnumeric(tmp_path, "multi", [
            ("Sheet1", {(0, 0): "a"}),
            ("Sheet2", {(0, 0): "b"}),
        ])
        assert gnumeric_has_multiple_sheets(f) is True

    def test_returns_bool(self, tmp_path):
        f = _make_gnumeric(tmp_path, "type2", [("S", {(0, 0): "x"})])
        assert isinstance(gnumeric_has_multiple_sheets(f), bool)

    def test_from_sample(self):
        path = SAMPLES / "minimal-spreadsheet.gnumeric"
        if path.exists():
            result = gnumeric_has_multiple_sheets(path)
            assert isinstance(result, bool)
