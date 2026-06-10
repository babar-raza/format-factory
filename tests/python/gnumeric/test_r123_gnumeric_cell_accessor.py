"""
tests/python/gnumeric/test_r123_gnumeric_cell_accessor.py

Sprint: FORMAT-FACTORY-EXPANDED-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
TC-GNUMERIC-CELL: get_cell_value()
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    get_cell_value,
    GnumericError,
)


def _make_model() -> dict:
    return create_gnumeric([
        {
            "name": "Sales",
            "rows": [
                ["Product", "Qty", "Price"],
                ["Apple", "10", "1.50"],
                ["Banana", "5", "0.75"],
            ],
        },
        {
            "name": "Summary",
            "rows": [["Total", "99"]],
        },
    ])


class TestGetCellValue:
    def test_returns_string(self):
        model = _make_model()
        result = get_cell_value(model, 0, 0, 0)
        assert isinstance(result, str)

    def test_first_cell(self):
        model = _make_model()
        assert get_cell_value(model, 0, 0, 0) == "Product"

    def test_second_sheet(self):
        model = _make_model()
        assert get_cell_value(model, 1, 0, 0) == "Total"

    def test_interior_cell(self):
        model = _make_model()
        assert get_cell_value(model, 0, 1, 1) == "10"

    def test_price_cell(self):
        model = _make_model()
        assert get_cell_value(model, 0, 2, 2) == "0.75"

    def test_missing_cell_returns_empty(self):
        model = _make_model()
        assert get_cell_value(model, 0, 99, 99) == ""

    def test_sheet_index_out_of_range_raises(self):
        model = _make_model()
        try:
            get_cell_value(model, 5, 0, 0)
            assert False, "Expected GnumericError"
        except GnumericError:
            pass

    def test_negative_sheet_index_raises(self):
        model = _make_model()
        try:
            get_cell_value(model, -1, 0, 0)
            assert False, "Expected GnumericError"
        except GnumericError:
            pass

    def test_type_error_not_dict(self):
        try:
            get_cell_value("not a dict", 0, 0, 0)
            assert False, "Expected TypeError"
        except TypeError:
            pass

    def test_empty_sheet(self):
        model = create_gnumeric([{"name": "Empty", "rows": []}])
        assert get_cell_value(model, 0, 0, 0) == ""

    def test_after_write_and_load(self):
        model = _make_model()
        tmp = Path(tempfile.mktemp(suffix=".gnumeric"))
        try:
            write_gnumeric(model, tmp)
            from gnumeric.gnumeric_codec import load
            loaded = load(tmp)
            assert get_cell_value(loaded, 0, 0, 0) == "Product"
            assert get_cell_value(loaded, 0, 1, 0) == "Apple"
        finally:
            tmp.unlink(missing_ok=True)

    def test_package_import(self):
        import gnumeric
        assert hasattr(gnumeric, "get_cell_value")

    def test_in_all(self):
        import gnumeric
        assert "get_cell_value" in gnumeric.__all__
