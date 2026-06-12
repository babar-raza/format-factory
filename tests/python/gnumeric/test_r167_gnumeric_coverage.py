"""
test_r167_gnumeric_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT8-001
Added: 2026-06-11

Tests for Gnumeric core functions: probe_gnumeric, load, get_sheet_count,
sheet_names, get_cell_count, get_row_count, get_column_count, get_cell_value,
get_column_values, sum_column, export_to_csv, export_to_json, create_gnumeric,
write_gnumeric.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    probe_gnumeric,
    load,
    get_sheet_count,
    sheet_names,
    get_cell_count,
    get_row_count,
    get_column_count,
    get_cell_value,
    get_column_values,
    sum_column,
    export_to_csv,
    export_to_json,
    create_gnumeric,
    write_gnumeric,
    GnumericError,
    GnumericParseError,
)

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = _SAMPLES / "minimal-spreadsheet.gnumeric"
_MULTI = _SAMPLES / "multi-cell-basic.gnumeric"


# ── Error classes ─────────────────────────────────────────────────────────

class TestGnumericErrors:

    def test_gnumeric_error_is_exception(self):
        assert isinstance(GnumericError("x"), Exception)

    def test_gnumeric_parse_error_inherits(self):
        assert isinstance(GnumericParseError("x"), GnumericError)


# ── probe_gnumeric ────────────────────────────────────────────────────────

class TestProbeGnumeric:

    def test_returns_bool(self):
        result = probe_gnumeric(_MINIMAL)
        assert isinstance(result, bool)

    def test_valid_file_true(self):
        assert probe_gnumeric(_MINIMAL) is True

    def test_nonexistent_false(self, tmp_path):
        assert probe_gnumeric(tmp_path / "no_such.gnumeric") is False

    def test_multi_cell_detected(self):
        assert probe_gnumeric(_MULTI) is True


# ── load ──────────────────────────────────────────────────────────────────

class TestLoadGnumeric:

    def test_returns_dict(self):
        model = load(_MINIMAL)
        assert isinstance(model, dict)

    def test_has_sheets_key(self):
        model = load(_MINIMAL)
        assert "sheets" in model

    def test_has_sheet_count_key(self):
        model = load(_MINIMAL)
        assert "sheet_count" in model


# ── get_sheet_count / sheet_names ─────────────────────────────────────────

class TestSheetInfo:

    def test_get_sheet_count_int(self):
        assert isinstance(get_sheet_count(_MINIMAL), int)

    def test_get_sheet_count_positive(self):
        assert get_sheet_count(_MINIMAL) >= 1

    def test_sheet_names_list(self):
        model = load(_MINIMAL)
        result = sheet_names(model)
        assert isinstance(result, list)

    def test_sheet_names_nonempty(self):
        model = load(_MULTI)
        result = sheet_names(model)
        assert len(result) >= 1

    def test_sheet_names_strings(self):
        model = load(_MULTI)
        for name in sheet_names(model):
            assert isinstance(name, str)


# ── get_cell_count ────────────────────────────────────────────────────────

class TestCellCount:

    def test_returns_int(self):
        assert isinstance(get_cell_count(_MINIMAL), int)

    def test_multi_has_cells(self):
        count = get_cell_count(_MULTI)
        assert count >= 1

    def test_count_is_nonnegative(self):
        assert get_cell_count(_MINIMAL) >= 0


# ── get_row_count / get_column_count ──────────────────────────────────────

class TestRowColumnCounts:

    def test_get_row_count_int(self):
        model = load(_MULTI)
        assert isinstance(get_row_count(model, 0), int)

    def test_get_row_count_positive(self):
        model = load(_MULTI)
        assert get_row_count(model, 0) >= 1

    def test_get_column_count_int(self):
        model = load(_MULTI)
        assert isinstance(get_column_count(model, 0), int)

    def test_get_column_count_positive(self):
        model = load(_MULTI)
        assert get_column_count(model, 0) >= 1


# ── get_cell_value ────────────────────────────────────────────────────────

class TestGetCellValue:

    def test_returns_value(self):
        model = load(_MULTI)
        val = get_cell_value(model, 0, 0, 0)
        assert val is not None

    def test_value_is_string(self):
        model = load(_MULTI)
        val = get_cell_value(model, 0, 0, 0)
        assert isinstance(val, str)


# ── get_column_values / sum_column ────────────────────────────────────────

class TestColumnOps:

    def test_get_column_values_list(self):
        model = load(_MULTI)
        result = get_column_values(model, 0, 0)
        assert isinstance(result, list)

    def test_sum_column_float(self):
        model = load(_MULTI)
        result = sum_column(model, 0, 1)
        assert isinstance(result, float)


# ── export_to_csv ─────────────────────────────────────────────────────────

class TestExportToCsv:

    def test_returns_string(self):
        result = export_to_csv(_MULTI)
        assert isinstance(result, str)

    def test_has_comma(self):
        result = export_to_csv(_MULTI)
        assert "," in result

    def test_has_data(self):
        result = export_to_csv(_MULTI)
        assert len(result.strip()) > 0


# ── export_to_json ────────────────────────────────────────────────────────

class TestExportToJson:

    def test_returns_string(self):
        result = export_to_json(_MULTI)
        assert isinstance(result, str)

    def test_valid_json(self):
        import json
        result = json.loads(export_to_json(_MULTI))
        assert result is not None

    def test_has_sheets(self):
        import json
        result = json.loads(export_to_json(_MULTI))
        # JSON is a list of sheets
        assert isinstance(result, list)
        assert len(result) >= 1


# ── create_gnumeric / write_gnumeric ─────────────────────────────────────

class TestCreateAndWrite:

    def test_create_returns_dict(self):
        doc = create_gnumeric([])
        assert isinstance(doc, dict)

    def test_write_creates_file(self, tmp_path):
        model = load(_MULTI)
        dest = tmp_path / "out.gnumeric"
        write_gnumeric(model, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0
