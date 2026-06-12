"""
tests/python/ods/test_r202_ods_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT17-001
TASK-001 (part B): ODS advanced operations.

Covers: parse_ods, parse_ods_strict, probe_ods, get_capabilities, count_sheets,
get_sheet_names, get_row_count, get_column_count, get_cell_count,
ods_numeric_cell_count, ods_string_cell_count, ods_empty_cell_count,
get_cell_value, get_column_values, get_row_values, get_sheet_as_dict_list,
sum_column, sum_row, average_column, count_distinct_values, count_nonempty_cells,
get_all_values, ods_max_row_length, max_column_value, min_column_value,
OdsDocument.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    parse_ods, parse_ods_strict, probe_ods, get_capabilities,
    count_sheets, get_sheet_names, get_row_count, get_column_count,
    get_cell_count, ods_numeric_cell_count, ods_string_cell_count,
    ods_empty_cell_count, get_cell_value, get_column_values, get_row_values,
    get_sheet_as_dict_list, sum_column, sum_row, average_column,
    count_distinct_values, count_nonempty_cells, get_all_values,
    ods_max_row_length, max_column_value, min_column_value,
    OdsDocument,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.ods")
_NUMERIC = str(_SAMPLES / "numeric-row.ods")
_SINGLE = str(_SAMPLES / "single-cell.ods")


class TestOdsParseAndProbe:
    """parse_ods, parse_ods_strict, probe_ods, get_capabilities."""

    def test_parse_ods_returns_dict(self):
        result = parse_ods(_MINIMAL)
        assert isinstance(result, dict)

    def test_parse_ods_ok_true(self):
        result = parse_ods(_MINIMAL)
        assert result.get("ok") is True

    def test_parse_ods_sheet_count(self):
        result = parse_ods(_MINIMAL)
        assert result.get("sheet_count") == 1

    def test_parse_ods_has_sheets(self):
        result = parse_ods(_MINIMAL)
        assert isinstance(result.get("sheets"), list)
        assert len(result["sheets"]) == 1

    def test_parse_ods_strict_returns_odsdocument(self):
        doc = parse_ods_strict(_MINIMAL)
        assert isinstance(doc, OdsDocument)

    def test_probe_ods_returns_dict(self):
        result = probe_ods(_MINIMAL)
        assert isinstance(result, dict)

    def test_probe_ods_exists(self):
        result = probe_ods(_MINIMAL)
        assert result.get("exists") is True

    def test_probe_ods_valid_container(self):
        result = probe_ods(_MINIMAL)
        assert result.get("valid_container") is True

    def test_probe_ods_mimetype(self):
        result = probe_ods(_MINIMAL)
        assert "spreadsheet" in result.get("mimetype", "")

    def test_get_capabilities_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps.get("format") == "ods"

    def test_get_capabilities_has_supported(self):
        caps = get_capabilities()
        assert isinstance(caps.get("supported"), list)
        assert len(caps["supported"]) > 0


class TestOdsDimensions:
    """count_sheets, get_sheet_names, get_row_count, get_column_count, get_cell_count."""

    def test_count_sheets_minimal(self):
        assert count_sheets(_MINIMAL) == 1

    def test_get_sheet_names_list(self):
        names = get_sheet_names(_MINIMAL)
        assert isinstance(names, list)
        assert len(names) == 1

    def test_get_sheet_names_value(self):
        names = get_sheet_names(_MINIMAL)
        assert names[0] == "Sheet1"

    def test_get_row_count_minimal(self):
        assert get_row_count(_MINIMAL) == 2

    def test_get_column_count_minimal(self):
        assert get_column_count(_MINIMAL) == 2

    def test_get_cell_count_minimal(self):
        assert get_cell_count(_MINIMAL) == 4

    def test_ods_max_row_length_minimal(self):
        n = ods_max_row_length(_MINIMAL)
        assert isinstance(n, int)
        assert n == 2


class TestOdsCellOps:
    """get_cell_value, get_column_values, get_row_values, get_sheet_as_dict_list."""

    def test_get_cell_value_name(self):
        val = get_cell_value(_MINIMAL, 0, 0, 0)
        assert val == "Name"

    def test_get_cell_value_value_header(self):
        val = get_cell_value(_MINIMAL, 0, 0, 1)
        assert val == "Value"

    def test_get_cell_value_alpha(self):
        val = get_cell_value(_MINIMAL, 0, 1, 0)
        assert val == "Alpha"

    def test_get_cell_value_numeric(self):
        val = get_cell_value(_MINIMAL, 0, 1, 1)
        assert val == 42 or val == 42.0

    def test_get_column_values_first_col(self):
        vals = get_column_values(_MINIMAL, 0)
        assert isinstance(vals, list)
        assert "Name" in vals

    def test_get_row_values_first_row(self):
        vals = get_row_values(_MINIMAL, 0, 0)
        assert isinstance(vals, list)
        assert "Name" in vals and "Value" in vals

    def test_get_sheet_as_dict_list_returns_list(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert isinstance(result, list)

    def test_get_sheet_as_dict_list_one_row(self):
        # minimal-spreadsheet has header row + 1 data row
        result = get_sheet_as_dict_list(_MINIMAL)
        assert len(result) == 1

    def test_get_sheet_as_dict_list_has_name_key(self):
        result = get_sheet_as_dict_list(_MINIMAL)
        assert "Name" in result[0]

    def test_get_all_values_list(self):
        vals = get_all_values(_MINIMAL)
        assert isinstance(vals, list)
        assert len(vals) == 4


class TestOdsAnalytics:
    """ods_numeric_cell_count, ods_string_cell_count, ods_empty_cell_count,
    sum_column, sum_row, average_column, count_distinct_values, count_nonempty_cells,
    max_column_value, min_column_value."""

    def test_ods_numeric_cell_count_minimal(self):
        n = ods_numeric_cell_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 1

    def test_ods_string_cell_count_minimal(self):
        n = ods_string_cell_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 3

    def test_ods_empty_cell_count_minimal(self):
        n = ods_empty_cell_count(_MINIMAL)
        assert isinstance(n, int)
        assert n == 0

    def test_sum_column_numeric(self):
        # numeric-row col 0 has value 1.0, col 1 has 2.0, col 2 has 3.0
        total = sum_column(_NUMERIC, 0)
        assert isinstance(total, (int, float))
        assert total == 1.0

    def test_sum_row_numeric(self):
        # sum of row 0 in sheet 0 of numeric-row = 1+2+3 = 6
        total = sum_row(_NUMERIC, 0, 0)
        assert isinstance(total, (int, float))
        assert total == 6.0

    def test_average_column_numeric(self):
        avg = average_column(_NUMERIC, 1)
        assert isinstance(avg, (int, float))
        assert avg == 2.0

    def test_count_distinct_values(self):
        # col 0 of minimal: "Name", "Alpha" — 2 distinct
        n = count_distinct_values(_MINIMAL, 0)
        assert isinstance(n, int)
        assert n == 2

    def test_count_nonempty_cells(self):
        n = count_nonempty_cells(_MINIMAL)
        assert isinstance(n, int)
        assert n == 4

    def test_max_column_value_numeric(self):
        m = max_column_value(_NUMERIC, 0, 0)
        assert isinstance(m, (int, float))
        assert m == 1.0

    def test_min_column_value_numeric(self):
        m = min_column_value(_NUMERIC, 0, 0)
        assert isinstance(m, (int, float))
        assert m == 1.0
