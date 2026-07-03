"""
Dogfood pipeline: ODS remaining analytics + FODS remaining analytics → NDJSON export.
Covers ODS: ods_numeric_cell_count, ods_numeric_density, ods_numeric_sum,
            ods_numeric_sum_all, ods_string_cell_count, ods_string_density
Covers FODS: fods_avg_numeric_value, fods_has_string_cells, fods_nonempty_sheet_count,
             fods_numeric_cell_ratio, fods_total_row_count, fods_nonempty_row_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_analytics import ods_numeric_cell_count, ods_numeric_density, ods_numeric_sum, ods_numeric_sum_all, ods_string_cell_count, ods_string_density
from fods.neutral_model import (
    fods_avg_numeric_value,
    fods_has_string_cells,
    fods_nonempty_sheet_count,
    fods_numeric_cell_ratio,
    fods_total_row_count,
    fods_nonempty_row_ratio,
)
from fods.parser import parse_fods
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def test_ods_numeric_cell_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_numeric_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_numeric_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_numeric_density_returns_float(tmp_path):
    path = _ods_file()
    result = ods_numeric_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ods", "function": "ods_numeric_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_ods_numeric_sum_returns_float(tmp_path):
    path = _ods_file()
    result = ods_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "ods", "function": "ods_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ods_numeric_sum_all_returns_float(tmp_path):
    path = _ods_file()
    result = ods_numeric_sum_all(path)
    assert isinstance(result, (int, float))

    record = {"format": "ods", "function": "ods_numeric_sum_all", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ods_string_cell_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_string_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_string_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_string_density_returns_float(tmp_path):
    path = _ods_file()
    result = ods_string_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "ods", "function": "ods_string_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fods_avg_numeric_value_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_avg_numeric_value(model)
    assert isinstance(result, (int, float))

    record = {"format": "fods", "function": "fods_avg_numeric_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_fods_has_string_cells_returns_bool(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_has_string_cells(model)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_has_string_cells", "has_strings": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_strings"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_nonempty_sheet_count_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_nonempty_sheet_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_nonempty_sheet_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_numeric_cell_ratio_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_numeric_cell_ratio(model)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_numeric_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fods_total_row_count_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_total_row_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_total_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_nonempty_row_ratio_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_nonempty_row_ratio(model)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_nonempty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None
