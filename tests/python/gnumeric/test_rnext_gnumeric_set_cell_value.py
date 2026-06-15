"""
test_rnext_gnumeric_set_cell_value.py -- Dedicated test coverage for set_cell_value.

Gap: GAP-Gnumeric-FOSS-SET_CELL_VAL-001 (missing_test_coverage)
Tests: basic set, immutability, overwrite, error handling, edge cells, multi-sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    set_cell_value,
    get_cell_value,
    GnumericError,
)


def _model(sheets=1, cells=None):
    """Create a minimal gnumeric model with N sheets."""
    sheet_dicts = [{"name": f"Sheet{i+1}"} for i in range(sheets)]
    m = create_gnumeric(sheet_dicts)
    if cells:
        for (si, r, c, v) in cells:
            m = set_cell_value(m, si, r, c, v)
    return m


class TestSetCellValueBasic:
    def test_set_and_read_back(self):
        m = _model()
        m2 = set_cell_value(m, 0, 0, 0, "hello")
        assert get_cell_value(m2, 0, 0, 0) == "hello"

    def test_set_different_cell(self):
        m = _model()
        m2 = set_cell_value(m, 0, 2, 3, "data")
        assert get_cell_value(m2, 0, 2, 3) == "data"

    def test_overwrite_cell(self):
        m = _model()
        m2 = set_cell_value(m, 0, 0, 0, "first")
        m3 = set_cell_value(m2, 0, 0, 0, "second")
        assert get_cell_value(m3, 0, 0, 0) == "second"

    def test_set_empty_string(self):
        m = _model()
        m2 = set_cell_value(m, 0, 0, 0, "data")
        m3 = set_cell_value(m2, 0, 0, 0, "")
        assert get_cell_value(m3, 0, 0, 0) == ""

    def test_numeric_string(self):
        m = _model()
        m2 = set_cell_value(m, 0, 0, 0, "42.5")
        assert get_cell_value(m2, 0, 0, 0) == "42.5"


class TestSetCellValueImmutability:
    def test_original_unchanged(self):
        m = _model()
        m2 = set_cell_value(m, 0, 0, 0, "new")
        orig_val = get_cell_value(m, 0, 0, 0)
        assert orig_val != "new" or orig_val is None or orig_val == ""

    def test_returns_new_model(self):
        m = _model()
        m2 = set_cell_value(m, 0, 0, 0, "val")
        assert m2 is not m


class TestSetCellValueMultiSheet:
    def test_set_on_second_sheet(self):
        m = _model(sheets=3)
        m2 = set_cell_value(m, 1, 0, 0, "sheet2")
        assert get_cell_value(m2, 1, 0, 0) == "sheet2"

    def test_different_sheets_independent(self):
        m = _model(sheets=2)
        m2 = set_cell_value(m, 0, 0, 0, "A")
        m3 = set_cell_value(m2, 1, 0, 0, "B")
        assert get_cell_value(m3, 0, 0, 0) == "A"
        assert get_cell_value(m3, 1, 0, 0) == "B"


class TestSetCellValueErrors:
    def test_model_not_dict_raises(self):
        with pytest.raises(TypeError):
            set_cell_value("not a dict", 0, 0, 0, "val")

    def test_value_not_str_raises(self):
        m = _model()
        with pytest.raises(TypeError):
            set_cell_value(m, 0, 0, 0, 123)

    def test_sheet_index_out_of_range_raises(self):
        m = _model(sheets=1)
        with pytest.raises(GnumericError):
            set_cell_value(m, 5, 0, 0, "val")

    def test_negative_sheet_index_raises(self):
        m = _model(sheets=1)
        with pytest.raises(GnumericError):
            set_cell_value(m, -1, 0, 0, "val")
