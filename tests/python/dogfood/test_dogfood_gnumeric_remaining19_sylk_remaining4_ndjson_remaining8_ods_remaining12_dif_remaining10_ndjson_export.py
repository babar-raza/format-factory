"""
Dogfood pipeline: Gnumeric remaining + SYLK remaining + NDJSON remaining + ODS remaining + DIF remaining -> NDJSON export.
Covers Gnumeric: gnumeric_string_cell_variance, gnumeric_total_cells_exceed_sheets
Covers SYLK: sylk_cell_count_per_row_avg, sylk_text_cell_ratio
Covers NDJSON: ndjson_array_field_total, ndjson_key_count_total
Covers ODS: ods_avg_numeric_per_sheet, ods_fill_rate, ods_nonempty_column_count, ods_row_density
Covers DIF: dif_cell_text_variance, dif_numeric_col_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    gnumeric_string_cell_variance,
    gnumeric_total_cells_exceed_sheets,
)
from sylk.sylk_parser import (
    sylk_cell_count_per_row_avg,
    sylk_text_cell_ratio,
)
from ndjson.ndjson_codec import (
    ndjson_array_field_total,
    ndjson_key_count_total,
    write_ndjson,
    load_ndjson,
)
from ods.ods_parser import (
    ods_avg_numeric_per_sheet,
    ods_fill_rate,
    ods_nonempty_column_count,
    ods_row_density,
)
from dif.dif_parser import (
    dif_cell_text_variance,
    dif_numeric_col_ratio,
)

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


# --- Gnumeric ---

def test_gnumeric_string_cell_variance_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_string_cell_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_string_cell_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_total_cells_exceed_sheets_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_total_cells_exceed_sheets(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_total_cells_exceed_sheets", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- SYLK ---

def test_sylk_cell_count_per_row_avg_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_cell_count_per_row_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_cell_count_per_row_avg", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_text_cell_ratio_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_text_cell_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "sylk", "function": "sylk_text_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- NDJSON ---

def test_ndjson_array_field_total_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": [1, 2], "b": "x"}, {"a": [3], "b": [4, 5, 6]}], str(src))
    result = ndjson_array_field_total(str(src))
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_array_field_total", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_key_count_total_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": 1, "b": 2}, {"c": 3}], str(src))
    result = ndjson_key_count_total(str(src))
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_key_count_total", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ODS ---

def test_ods_avg_numeric_per_sheet_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_numeric_per_sheet(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ods", "function": "ods_avg_numeric_per_sheet", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_fill_rate_returns_float(tmp_path):
    path = _ods_file()
    result = ods_fill_rate(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ods", "function": "ods_fill_rate", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ods_nonempty_column_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_nonempty_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_nonempty_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_row_density_returns_float(tmp_path):
    path = _ods_file()
    result = ods_row_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ods", "function": "ods_row_density", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- DIF ---

def test_dif_cell_text_variance_returns_float(tmp_path):
    path = _dif_file()
    result = dif_cell_text_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_cell_text_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_col_ratio_returns_float(tmp_path):
    path = _dif_file()
    result = dif_numeric_col_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "dif", "function": "dif_numeric_col_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None
