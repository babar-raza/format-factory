"""Tests for gnumeric_average_cells_per_sheet and gnumeric_numeric_density.

Product deepening: Gnumeric analytics — TC-H3-002-GNUMERIC / PDC-GNUMERIC-AVG-DENSITY-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    create_gnumeric,
    write_gnumeric,
    set_cell_value,
    add_sheet,
    gnumeric_average_cells_per_sheet,
    gnumeric_numeric_density,
)


def _make_gnumeric(tmp_path, name, sheets_data):
    sheet_dicts = [{"name": s[0]} for s in sheets_data]
    if not sheet_dicts:
        sheet_dicts = [{"name": "Sheet1"}]
    model = create_gnumeric(sheets=[sheet_dicts[0]])
    for sd in sheet_dicts[1:]:
        model = add_sheet(model, sd["name"])
    for i, (sheet_name, cells) in enumerate(sheets_data):
        for row, col, val in cells:
            model = set_cell_value(model, i, row, col, val)
    p = tmp_path / f"{name}.gnumeric"
    write_gnumeric(model, str(p))
    return p


class TestGnumericAverageCellsPerSheet:
    def test_single_sheet(self, tmp_path):
        p = _make_gnumeric(tmp_path, "single", [("Sheet1", [(0, 0, "a"), (0, 1, "b")])])
        result = gnumeric_average_cells_per_sheet(p)
        assert isinstance(result, float)
        assert result > 0

    def test_two_sheets(self, tmp_path):
        p = _make_gnumeric(tmp_path, "two", [
            ("Sheet1", [(0, 0, "a")]),
            ("Sheet2", [(0, 0, "x"), (0, 1, "y"), (1, 0, "z")]),
        ])
        result = gnumeric_average_cells_per_sheet(p)
        assert isinstance(result, float)
        assert result > 0

    def test_empty_sheet(self, tmp_path):
        p = _make_gnumeric(tmp_path, "empty", [("Sheet1", [])])
        result = gnumeric_average_cells_per_sheet(p)
        assert result == 0.0

    def test_returns_float(self, tmp_path):
        p = _make_gnumeric(tmp_path, "ft", [("Sheet1", [(0, 0, "v")])])
        assert isinstance(gnumeric_average_cells_per_sheet(p), float)

    def test_non_negative(self, tmp_path):
        p = _make_gnumeric(tmp_path, "nn", [("Sheet1", [(0, 0, "1")])])
        assert gnumeric_average_cells_per_sheet(p) >= 0.0


class TestGnumericNumericDensity:
    def test_all_numeric(self, tmp_path):
        p = _make_gnumeric(tmp_path, "allnum", [("Sheet1", [(0, 0, "10"), (0, 1, "20")])])
        result = gnumeric_numeric_density(p)
        assert isinstance(result, float)
        assert result > 0

    def test_mixed(self, tmp_path):
        p = _make_gnumeric(tmp_path, "mixed", [("Sheet1", [(0, 0, "10"), (0, 1, "abc")])])
        result = gnumeric_numeric_density(p)
        assert 0.0 < result < 1.0

    def test_no_numeric(self, tmp_path):
        p = _make_gnumeric(tmp_path, "nonum", [("Sheet1", [(0, 0, "hello"), (0, 1, "world")])])
        result = gnumeric_numeric_density(p)
        assert result == 0.0

    def test_empty(self, tmp_path):
        p = _make_gnumeric(tmp_path, "emptydn", [("Sheet1", [])])
        assert gnumeric_numeric_density(p) == 0.0

    def test_returns_float(self, tmp_path):
        p = _make_gnumeric(tmp_path, "ft2", [("Sheet1", [(0, 0, "5")])])
        assert isinstance(gnumeric_numeric_density(p), float)
