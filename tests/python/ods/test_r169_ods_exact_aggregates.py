"""R169 — ODS average/min/max column and dict-list exact-output hardening tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.python.ods.ods_parser import (
    average_column,
    min_column_value,
    max_column_value,
    get_sheet_as_dict_list,
)


_MINIMAL = Path("samples/by-format/ods/valid/minimal-spreadsheet.ods")
_NUMERIC = Path("samples/by-format/ods/valid/numeric-row.ods")


class TestOdsAverageColumnExact:
    def test_average_numeric_row_col0(self):
        """numeric-row.ods has values [1.0, 2.0, 3.0] in row 0 — col 0 is 1.0."""
        result = average_column(_NUMERIC, col=0)
        assert result == pytest.approx(1.0)

    def test_average_numeric_row_col1(self):
        result = average_column(_NUMERIC, col=1)
        assert result == pytest.approx(2.0)

    def test_average_numeric_row_col2(self):
        result = average_column(_NUMERIC, col=2)
        assert result == pytest.approx(3.0)

    def test_average_out_of_range_col_returns_zero(self):
        result = average_column(_NUMERIC, col=99)
        assert result == 0.0


class TestOdsMinMaxColumnExact:
    def test_min_numeric_col0_is_1(self):
        result = min_column_value(_NUMERIC, col=0)
        assert result == pytest.approx(1.0)

    def test_max_numeric_col2_is_3(self):
        result = max_column_value(_NUMERIC, col=2)
        assert result == pytest.approx(3.0)

    def test_min_lte_max(self):
        mn = min_column_value(_NUMERIC, col=1)
        mx = max_column_value(_NUMERIC, col=1)
        assert mn <= mx


class TestOdsDictListExact:
    def test_minimal_first_row_name_alpha(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert result[0]["Name"] == "Alpha"

    def test_minimal_first_row_value_42(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert result[0]["Value"] == pytest.approx(42.0)

    def test_dict_list_length_one(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert len(result) == 1
