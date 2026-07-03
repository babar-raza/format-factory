"""
Dogfood pipeline: Gnumeric remaining model analytics + ODS remaining analytics → NDJSON export.
Covers Gnumeric: sum_column, sum_row, get_row_values, get_column_values,
                 gnumeric_is_all_numeric, gnumeric_nonempty_cell_ratio
Covers ODS: get_cell_value, get_column_values, get_row_values, get_sheet_as_dict_list,
            ods_average_cells_per_row, ods_avg_cells_per_sheet
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    sum_column,
    sum_row,
    get_row_values as gnumeric_get_row_values,
    get_column_values as gnumeric_get_column_values,
    gnumeric_is_all_numeric,
    gnumeric_nonempty_cell_ratio,
    get_cell_count,
    load as gnumeric_load,
)
from ods.ods_parser import (
    get_cell_value as ods_get_cell_value,
    get_column_values as ods_get_column_values,
    get_row_values as ods_get_row_values,
    get_sheet_as_dict_list,
)
from ods.ods_analytics import ods_average_cells_per_row, ods_avg_cells_per_sheet
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _gnumeric_file():
    for f in sorted(_GNUMERIC_DIR.glob("*.gnumeric")):
        if get_cell_count(str(f)) > 0:
            return str(f)
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_gnumeric_sum_column_returns_float(tmp_path):
    path = _gnumeric_file()
    model = gnumeric_load(path)
    result = sum_column(model, 0, 0)
    assert isinstance(result, (int, float))

    record = {"format": "gnumeric", "function": "sum_column", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_sum_row_returns_float(tmp_path):
    path = _gnumeric_file()
    model = gnumeric_load(path)
    result = sum_row(model, 0, 0)
    assert isinstance(result, (int, float))

    record = {"format": "gnumeric", "function": "sum_row", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_row_values_returns_list(tmp_path):
    path = _gnumeric_file()
    model = gnumeric_load(path)
    result = gnumeric_get_row_values(model, 0, 0)
    assert isinstance(result, list)

    record = {"format": "gnumeric", "function": "get_row_values", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_get_column_values_returns_list(tmp_path):
    path = _gnumeric_file()
    model = gnumeric_load(path)
    result = gnumeric_get_column_values(model, 0, 0)
    assert isinstance(result, list)

    record = {"format": "gnumeric", "function": "get_column_values", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_is_all_numeric_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_is_all_numeric(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_is_all_numeric", "all_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["all_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_nonempty_cell_ratio_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_nonempty_cell_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "gnumeric", "function": "gnumeric_nonempty_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ods_get_cell_value_returns_value(tmp_path):
    path = _ods_file()
    result = ods_get_cell_value(path, 0, 0, 0)
    # value may be anything

    record = {"format": "ods", "function": "get_cell_value", "value": str(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "value" in loaded[0]
    assert json.dumps(loaded[0]) is not None


def test_ods_get_column_values_returns_list(tmp_path):
    path = _ods_file()
    result = ods_get_column_values(path, 0)
    assert isinstance(result, list)

    record = {"format": "ods", "function": "get_column_values", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_get_row_values_returns_list(tmp_path):
    path = _ods_file()
    result = ods_get_row_values(path, 0, 0)
    assert isinstance(result, list)

    record = {"format": "ods", "function": "get_row_values", "cell_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["cell_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_get_sheet_as_dict_list_returns_list(tmp_path):
    path = _ods_file()
    result = get_sheet_as_dict_list(path, 0)
    assert isinstance(result, list)

    record = {"format": "ods", "function": "get_sheet_as_dict_list", "row_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_average_cells_per_row_returns_float(tmp_path):
    path = _ods_file()
    result = ods_average_cells_per_row(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_average_cells_per_row", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ods_avg_cells_per_sheet_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_cells_per_sheet(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_avg_cells_per_sheet", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None
