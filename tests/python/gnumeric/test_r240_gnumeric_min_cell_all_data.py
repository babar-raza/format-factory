"""Tests for gnumeric_min_cell_length and gnumeric_all_sheets_have_data (Sprint 30)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric, write_gnumeric, set_cell_value, add_sheet,
    gnumeric_min_cell_length, gnumeric_all_sheets_have_data,
)


def _make_gnumeric(tmp_path, name, sheets_data):
    """sheets_data: list of (sheet_name, [(row, col, val), ...])"""
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
    return str(p)


class TestGnumericMinCellLength:
    def test_return_type(self, tmp_path):
        p = _make_gnumeric(tmp_path, "rt", [("S1", [(0, 0, "abc")])])
        assert isinstance(gnumeric_min_cell_length(p), int)

    def test_exact_min(self, tmp_path):
        # 'abc' (3) and 'de' (2) -> min = 2
        p = _make_gnumeric(tmp_path, "em", [("S1", [(0, 0, "abc"), (0, 1, "de")])])
        assert gnumeric_min_cell_length(p) == 2

    def test_single_cell(self, tmp_path):
        p = _make_gnumeric(tmp_path, "sc", [("S1", [(0, 0, "hello")])])
        assert gnumeric_min_cell_length(p) == 5

    def test_nonnegative(self, tmp_path):
        p = _make_gnumeric(tmp_path, "nn", [("S1", [(0, 0, "x")])])
        assert gnumeric_min_cell_length(p) >= 0

    def test_short_value_wins(self, tmp_path):
        # 'a' (1), 'longer' (6) -> min = 1
        p = _make_gnumeric(tmp_path, "sv", [("S1", [(0, 0, "a"), (0, 1, "longer")])])
        assert gnumeric_min_cell_length(p) == 1


class TestGnumericAllSheetsHaveData:
    def test_return_type(self, tmp_path):
        p = _make_gnumeric(tmp_path, "rt2", [("S1", [(0, 0, "x")])])
        assert isinstance(gnumeric_all_sheets_have_data(p), bool)

    def test_single_sheet_with_data(self, tmp_path):
        p = _make_gnumeric(tmp_path, "sd", [("S1", [(0, 0, "data")])])
        assert gnumeric_all_sheets_have_data(p) is True

    def test_two_sheets_both_have_data(self, tmp_path):
        p = _make_gnumeric(tmp_path, "ts", [("S1", [(0, 0, "a")]), ("S2", [(0, 0, "b")])])
        assert gnumeric_all_sheets_have_data(p) is True

    def test_empty_sheet_returns_false(self, tmp_path):
        # Sheet with no cells -> False
        model = create_gnumeric(sheets=[{"name": "S1"}])
        p = tmp_path / "empty.gnumeric"
        write_gnumeric(model, str(p))
        assert gnumeric_all_sheets_have_data(str(p)) is False

    def test_one_empty_among_nonempty_returns_false(self, tmp_path):
        # S1 has data, S2 is empty -> False
        model = create_gnumeric(sheets=[{"name": "S1"}])
        model = set_cell_value(model, 0, 0, 0, "data")
        model = add_sheet(model, "S2")
        p = tmp_path / "mixed.gnumeric"
        write_gnumeric(model, str(p))
        assert gnumeric_all_sheets_have_data(str(p)) is False
