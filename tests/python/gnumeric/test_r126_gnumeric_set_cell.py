"""
tests/python/gnumeric/test_r126_gnumeric_set_cell.py

Sprint: FORMAT-FACTORY-AUTONOMOUS-EXECUTION-SPINE-BROAD-PRODUCT-MEGA-TRAIN-001
TC-GNUMERIC-SET-CELL: set_cell_value() — immutable model mutation
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    set_cell_value,
    get_cell_value,
    GnumericError,
)


def _make_model(rows=None):
    sheets = [{"name": "Sheet1", "rows": rows or [["A", "B"], ["1", "2"]]}]
    return create_gnumeric(sheets)


class TestSetCellValue:
    def test_returns_dict(self):
        model = _make_model()
        result = set_cell_value(model, 0, 0, 0, "X")
        assert isinstance(result, dict)

    def test_value_set_correctly(self):
        model = _make_model()
        result = set_cell_value(model, 0, 0, 0, "Hello")
        assert get_cell_value(result, 0, 0, 0) == "Hello"

    def test_immutable_original_unchanged(self):
        model = _make_model()
        original_val = get_cell_value(model, 0, 0, 0)
        set_cell_value(model, 0, 0, 0, "Changed")
        assert get_cell_value(model, 0, 0, 0) == original_val

    def test_set_new_cell(self):
        model = _make_model()
        result = set_cell_value(model, 0, 5, 5, "NewCell")
        assert get_cell_value(result, 0, 5, 5) == "NewCell"

    def test_overwrite_existing_cell(self):
        model = _make_model()
        result = set_cell_value(model, 0, 0, 0, "First")
        result2 = set_cell_value(result, 0, 0, 0, "Second")
        assert get_cell_value(result2, 0, 0, 0) == "Second"

    def test_invalid_sheet_index_raises(self):
        model = _make_model()
        try:
            set_cell_value(model, 99, 0, 0, "X")
            assert 1 == 0, "Expected GnumericError"

        except GnumericError:
            pass

    def test_non_dict_model_raises_type_error(self):
        try:
            set_cell_value("not a model", 0, 0, 0, "X")
            assert 1 == 0, "Expected TypeError"

        except TypeError:
            pass

    def test_non_string_value_raises_type_error(self):
        model = _make_model()
        try:
            set_cell_value(model, 0, 0, 0, 42)
            assert 1 == 0, "Expected TypeError"

        except TypeError:
            pass

    def test_set_empty_string(self):
        model = _make_model()
        result = set_cell_value(model, 0, 0, 0, "")
        # Empty string set — no error
        assert isinstance(result, dict)

    def test_package_import(self):
        import gnumeric
        assert hasattr(gnumeric, "set_cell_value")

    def test_in_all(self):
        import gnumeric
        assert "set_cell_value" in gnumeric.__all__
