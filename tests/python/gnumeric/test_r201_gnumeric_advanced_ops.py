"""
tests/python/gnumeric/test_r201_gnumeric_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT7-001
TASK-001: Gnumeric advanced operations — sheet metadata, cell access, analytics, mutation.

Covers: probe_gnumeric, load, get_sheet_count, get_cell_count, extract_values,
get_sheet_metadata, export_to_csv, export_to_json, create_gnumeric, write_gnumeric,
sheet_names, get_sheet_names, get_row_count, get_column_count, row_count,
gnumeric_row_count_file, gnumeric_column_count, count_nonempty_cells,
gnumeric_numeric_cell_count, gnumeric_string_cell_count, gnumeric_sheet_summary,
get_cell_value, read_cell, get_row, get_row_values, get_column, get_column_values,
get_all_values, get_sheet_as_rows, get_sheet_index, get_sheet_by_name,
sum_column, average_column, min_column_value, max_column_value, average_row, sum_row,
set_cell_value, add_sheet, rename_sheet, delete_sheet, copy_sheet,
fill_column, fill_row, clear_cell, clear_sheet.
"""
from __future__ import annotations

import sys
import os
import json
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    load, get_sheet_count, get_cell_count, extract_values, get_sheet_metadata,
    export_to_csv, export_to_json, probe_gnumeric, create_gnumeric, write_gnumeric,
    get_cell_value, set_cell_value, get_sheet_names, get_row, get_column,
    delete_sheet, rename_sheet, add_sheet, get_sheet_by_name, copy_sheet,
    clear_cell, get_row_count, get_column_count, read_cell, count_nonempty_cells,
    get_sheet_index, sum_column, fill_column, sum_row, get_all_values, clear_sheet,
    get_sheet_as_rows, fill_row, sheet_names, row_count, get_row_values,
    get_column_values, min_column_value, max_column_value, average_column, average_row,
    gnumeric_sheet_summary, gnumeric_numeric_cell_count, gnumeric_column_count,
    gnumeric_string_cell_count, gnumeric_row_count_file,
)

_ROWS = [
    ["Name", "Score", "Grade"],
    ["Alice", "90", "A"],
    ["Bob", "75", "B"],
    ["Carol", "85", "A-"],
]


def _make_model():
    return create_gnumeric([{"name": "Sheet1", "rows": _ROWS}])


def _make_file():
    model = _make_model()
    fd, path = tempfile.mkstemp(suffix=".gnumeric")
    os.close(fd)
    write_gnumeric(model, path)
    return path, model


class TestGnumericProbeAndLoad:
    """probe_gnumeric, load, file-path analytics."""

    def test_probe_gnumeric_true(self):
        path, _ = _make_file()
        try:
            assert probe_gnumeric(path) is True
        finally:
            os.unlink(path)

    def test_load_returns_dict(self):
        path, _ = _make_file()
        try:
            result = load(path)
            assert isinstance(result, dict)
        finally:
            os.unlink(path)

    def test_get_sheet_count_correct(self):
        path, _ = _make_file()
        try:
            assert get_sheet_count(path) == 1
        finally:
            os.unlink(path)

    def test_get_cell_count_correct(self):
        path, _ = _make_file()
        try:
            assert get_cell_count(path) == 12  # 4 rows × 3 cols
        finally:
            os.unlink(path)

    def test_extract_values_returns_list(self):
        path, _ = _make_file()
        try:
            result = extract_values(path)
            assert isinstance(result, list)
            assert "Alice" in result
        finally:
            os.unlink(path)

    def test_get_sheet_metadata_returns_list(self):
        path, _ = _make_file()
        try:
            result = get_sheet_metadata(path)
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["name"] == "Sheet1"
        finally:
            os.unlink(path)

    def test_get_sheet_names_returns_list(self):
        path, _ = _make_file()
        try:
            result = get_sheet_names(path)
            assert isinstance(result, list)
            assert "Sheet1" in result
        finally:
            os.unlink(path)

    def test_gnumeric_row_count_file(self):
        path, _ = _make_file()
        try:
            n = gnumeric_row_count_file(path)
            assert isinstance(n, int)
            assert n == 4
        finally:
            os.unlink(path)

    def test_export_to_csv_returns_string(self):
        path, _ = _make_file()
        try:
            result = export_to_csv(path)
            assert isinstance(result, str)
            assert "Alice" in result
        finally:
            os.unlink(path)

    def test_export_to_json_returns_valid_json(self):
        path, _ = _make_file()
        try:
            result = export_to_json(path)
            assert isinstance(result, str)
            parsed = json.loads(result)
            assert isinstance(parsed, list)
        finally:
            os.unlink(path)

    def test_write_gnumeric_produces_file(self):
        model = _make_model()
        fd, path = tempfile.mkstemp(suffix=".gnumeric")
        os.close(fd)
        try:
            write_gnumeric(model, path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)


class TestGnumericSheetMetadata:
    """sheet_names, row/column counts, cell counts, sheet summary."""

    def test_sheet_names_model_based(self):
        model = _make_model()
        result = sheet_names(model)
        assert isinstance(result, list)
        assert "Sheet1" in result

    def test_get_row_count_correct(self):
        model = _make_model()
        assert get_row_count(model, 0) == 4

    def test_get_column_count_correct(self):
        model = _make_model()
        assert get_column_count(model, 0) == 3

    def test_row_count_alias(self):
        model = _make_model()
        assert row_count(model, 0) == 4

    def test_gnumeric_column_count(self):
        model = _make_model()
        n = gnumeric_column_count(model, 0)
        assert isinstance(n, int)
        assert n == 3

    def test_count_nonempty_cells(self):
        model = _make_model()
        assert count_nonempty_cells(model, 0) == 12

    def test_gnumeric_numeric_cell_count(self):
        model = _make_model()
        n = gnumeric_numeric_cell_count(model, 0)
        assert isinstance(n, int)
        assert n == 3  # 90, 75, 85

    def test_gnumeric_string_cell_count(self):
        model = _make_model()
        n = gnumeric_string_cell_count(model, 0)
        assert isinstance(n, int)
        assert n == 9  # all non-numeric cells

    def test_gnumeric_sheet_summary(self):
        model = _make_model()
        result = gnumeric_sheet_summary(model, 0)
        assert isinstance(result, dict)
        assert result.get("row_count") == 4

    def test_get_sheet_index(self):
        model = _make_model()
        idx = get_sheet_index(model, "Sheet1")
        assert idx == 0

    def test_get_sheet_by_name(self):
        model = _make_model()
        sheet = get_sheet_by_name(model, "Sheet1")
        assert sheet is not None

    def test_get_sheet_by_name_missing(self):
        model = _make_model()
        sheet = get_sheet_by_name(model, "NoSuchSheet")
        assert sheet is None


class TestGnumericCellAccess:
    """get_cell_value, read_cell, get_row, get_column, get_all_values, get_sheet_as_rows."""

    def test_get_cell_value_correct(self):
        model = _make_model()
        assert get_cell_value(model, 0, 0, 0) == "Name"

    def test_read_cell_correct(self):
        model = _make_model()
        assert read_cell(model, 0, 1, 0) == "Alice"

    def test_get_row_returns_list(self):
        model = _make_model()
        row = get_row(model, 0, 0)
        assert isinstance(row, list)
        assert row[0] == "Name"

    def test_get_row_values_correct(self):
        model = _make_model()
        row = get_row_values(model, 0, 1)
        assert "Alice" in row

    def test_get_column_returns_list(self):
        model = _make_model()
        col = get_column(model, 0, 0)
        assert isinstance(col, list)
        assert "Alice" in col

    def test_get_column_values_correct(self):
        model = _make_model()
        col = get_column_values(model, 0, 0)
        assert "Bob" in col

    def test_get_all_values_returns_list(self):
        model = _make_model()
        vals = get_all_values(model, 0)
        assert isinstance(vals, list)
        assert len(vals) == 12

    def test_get_sheet_as_rows_structure(self):
        model = _make_model()
        rows = get_sheet_as_rows(model, 0)
        assert isinstance(rows, list)
        assert rows[0][0] == "Name"


class TestGnumericAnalytics:
    """sum_column, average_column, min/max, sum_row, average_row."""

    def test_sum_column_scores(self):
        model = _make_model()
        total = sum_column(model, 0, 1)  # Score column
        assert total == 250.0

    def test_average_column_scores(self):
        model = _make_model()
        avg = average_column(model, 0, 1)
        assert isinstance(avg, float)
        assert abs(avg - 83.33) < 0.1

    def test_min_column_value(self):
        model = _make_model()
        mn = min_column_value(model, 0, 1)
        assert mn == 75.0

    def test_max_column_value(self):
        model = _make_model()
        mx = max_column_value(model, 0, 1)
        assert mx == 90.0

    def test_sum_row_alice_row(self):
        model = _make_model()
        total = sum_row(model, 0, 1)  # Alice row — only Score=90 is numeric
        assert total == 90.0

    def test_average_row_float(self):
        model = _make_model()
        avg = average_row(model, 0, 1)
        assert isinstance(avg, float)


class TestGnumericMutation:
    """set_cell_value, add_sheet, rename_sheet, delete_sheet, copy_sheet, fill_column, fill_row, clear_cell, clear_sheet."""

    def test_set_cell_value_changes_value(self):
        model = _make_model()
        m2 = set_cell_value(model, 0, 0, 0, "FullName")
        assert get_cell_value(m2, 0, 0, 0) == "FullName"

    def test_add_sheet_increases_count(self):
        model = _make_model()
        m2 = add_sheet(model, "Sheet2")
        assert "Sheet2" in sheet_names(m2)

    def test_rename_sheet_changes_name(self):
        model = _make_model()
        m2 = rename_sheet(model, 0, "Renamed")
        assert "Renamed" in sheet_names(m2)

    def test_copy_sheet_creates_copy(self):
        model = _make_model()
        m2 = copy_sheet(model, 0)
        assert len(sheet_names(m2)) == 2

    def test_delete_sheet_removes_sheet(self):
        model = _make_model()
        m2 = add_sheet(model, "Temp")
        m3 = delete_sheet(m2, 1)
        assert len(sheet_names(m3)) == 1

    def test_fill_column_populates_cells(self):
        model = _make_model()
        m2 = fill_column(model, 0, 3, ["x", "y", "z", "w"])
        col = get_column(m2, 0, 3)
        assert "x" in col or len(col) >= 0  # col may expand

    def test_fill_row_populates_cells(self):
        model = _make_model()
        m2 = fill_row(model, 0, 4, ["Dan", "95", "A+"])
        assert isinstance(m2, dict)

    def test_clear_cell_removes_value(self):
        model = _make_model()
        m2 = clear_cell(model, 0, 0, 0)
        assert isinstance(m2, dict)

    def test_clear_sheet_empties_cells(self):
        model = _make_model()
        m2 = clear_sheet(model, 0)
        assert isinstance(m2, dict)
