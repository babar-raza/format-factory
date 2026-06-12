"""
tests/python/gnumeric/test_r202_gnumeric_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT19-001
TASK-001: Gnumeric advanced operations.

Covers: load, probe_gnumeric, get_sheet_count, get_sheet_names, sheet_names,
get_row_count, get_column_count, get_cell_count, get_cell_value,
get_column_values, get_row_values, get_all_values, count_nonempty_cells,
sum_row, average_row, gnumeric_numeric_cell_count, gnumeric_string_cell_count,
gnumeric_row_count_file, gnumeric_column_count, gnumeric_sheet_summary,
export_to_csv, export_to_json, get_sheet_as_rows.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    load, probe_gnumeric, get_sheet_count, get_sheet_names, sheet_names,
    get_row_count, get_column_count, get_cell_count, get_cell_value,
    get_column_values, get_row_values, get_all_values, count_nonempty_cells,
    sum_row, average_row, gnumeric_numeric_cell_count, gnumeric_string_cell_count,
    gnumeric_row_count_file, gnumeric_column_count, gnumeric_sheet_summary,
    export_to_csv, export_to_json, get_sheet_as_rows,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.gnumeric")
_MULTI = str(_SAMPLES / "multi-cell-basic.gnumeric")


class TestGnumericParseAndProbe:
    """load, probe_gnumeric, get_sheet_count, get_sheet_names, sheet_names."""

    def test_load_returns_dict(self):
        model = load(_MINIMAL)
        assert isinstance(model, dict)

    def test_load_is_gnumeric(self):
        model = load(_MINIMAL)
        assert model.get("is_gnumeric") is True

    def test_load_has_sheets(self):
        model = load(_MINIMAL)
        assert isinstance(model.get("sheets"), list)

    def test_probe_gnumeric_true(self):
        result = probe_gnumeric(_MINIMAL)
        assert result is True

    def test_get_sheet_count_minimal(self):
        assert get_sheet_count(_MINIMAL) == 1

    def test_get_sheet_names_list(self):
        names = get_sheet_names(_MINIMAL)
        assert isinstance(names, list)
        assert len(names) == 1

    def test_get_sheet_names_value(self):
        names = get_sheet_names(_MINIMAL)
        assert names[0] == "Sheet1"

    def test_sheet_names_from_model(self):
        model = load(_MINIMAL)
        names = sheet_names(model)
        assert isinstance(names, list)
        assert "Sheet1" in names


class TestGnumericDimensions:
    """get_row_count, get_column_count, get_cell_count,
    gnumeric_row_count_file, gnumeric_column_count."""

    def test_get_row_count_minimal(self):
        model = load(_MINIMAL)
        assert get_row_count(model, 0) == 1

    def test_get_column_count_multi(self):
        model = load(_MULTI)
        assert get_column_count(model, 0) == 2

    def test_get_cell_count_minimal(self):
        # get_cell_count takes path
        assert get_cell_count(_MINIMAL) == 1

    def test_get_cell_count_multi(self):
        assert get_cell_count(_MULTI) == 4

    def test_gnumeric_row_count_file_multi(self):
        n = gnumeric_row_count_file(_MULTI)
        assert isinstance(n, int)
        assert n == 2

    def test_gnumeric_column_count_multi(self):
        model = load(_MULTI)
        n = gnumeric_column_count(model, 0)
        assert isinstance(n, int)
        assert n == 2


class TestGnumericCellOps:
    """get_cell_value, get_column_values, get_row_values, get_all_values,
    count_nonempty_cells, get_sheet_as_rows."""

    def test_get_cell_value_name(self):
        model = load(_MULTI)
        val = get_cell_value(model, 0, 0, 0)
        assert val == "Name"

    def test_get_cell_value_score_header(self):
        model = load(_MULTI)
        val = get_cell_value(model, 0, 0, 1)
        assert val == "Score"

    def test_get_column_values_first(self):
        model = load(_MULTI)
        vals = get_column_values(model, 0, 0)
        assert isinstance(vals, list)
        assert "Name" in vals

    def test_get_row_values_header(self):
        model = load(_MULTI)
        vals = get_row_values(model, 0, 0)
        assert isinstance(vals, list)
        assert "Name" in vals and "Score" in vals

    def test_get_all_values_list(self):
        model = load(_MULTI)
        vals = get_all_values(model, 0)
        assert isinstance(vals, list)
        assert len(vals) == 4

    def test_count_nonempty_cells(self):
        model = load(_MULTI)
        n = count_nonempty_cells(model, 0)
        assert isinstance(n, int)
        assert n == 4

    def test_get_sheet_as_rows_list(self):
        model = load(_MULTI)
        rows = get_sheet_as_rows(model, 0)
        assert isinstance(rows, list)
        assert len(rows) == 2

    def test_get_sheet_as_rows_header(self):
        model = load(_MULTI)
        rows = get_sheet_as_rows(model, 0)
        assert rows[0] == ["Name", "Score"]


class TestGnumericAnalytics:
    """sum_row, average_row, gnumeric_numeric_cell_count, gnumeric_string_cell_count,
    gnumeric_sheet_summary, export_to_csv, export_to_json."""

    def test_sum_row_data_row(self):
        # multi-cell row 1: Alice, 42 → numeric sum = 42.0
        model = load(_MULTI)
        total = sum_row(model, 0, 1)
        assert isinstance(total, (int, float))
        assert total == 42.0

    def test_average_row_data_row(self):
        model = load(_MULTI)
        avg = average_row(model, 0, 1)
        assert isinstance(avg, (int, float))
        assert avg == 42.0

    def test_gnumeric_numeric_cell_count(self):
        model = load(_MULTI)
        n = gnumeric_numeric_cell_count(model, 0)
        assert isinstance(n, int)
        assert n == 1

    def test_gnumeric_string_cell_count(self):
        model = load(_MULTI)
        n = gnumeric_string_cell_count(model, 0)
        assert isinstance(n, int)
        assert n == 3

    def test_gnumeric_sheet_summary_dict(self):
        model = load(_MULTI)
        summary = gnumeric_sheet_summary(model, 0)
        assert isinstance(summary, dict)

    def test_gnumeric_sheet_summary_counts(self):
        model = load(_MULTI)
        summary = gnumeric_sheet_summary(model, 0)
        assert summary.get("row_count") == 2
        assert summary.get("col_count") == 2
        assert summary.get("nonempty_cells") == 4

    def test_export_to_csv_str(self):
        result = export_to_csv(_MULTI)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_to_csv_has_data(self):
        result = export_to_csv(_MULTI)
        assert "Name" in result

    def test_export_to_json_str(self):
        result = export_to_json(_MULTI)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_to_json_has_sheet(self):
        result = export_to_json(_MULTI)
        assert "Sheet1" in result
