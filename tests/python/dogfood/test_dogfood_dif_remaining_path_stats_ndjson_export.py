"""
Dogfood pipeline: DIF path-based remaining + DIF model stats → NDJSON export.
Covers: average_column, count_distinct_values, dif_all_numeric_column,
        dif_empty_row_count, dif_string_cell_count, dif_total_numeric_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import average_column, count_distinct_values, dif_all_numeric_column, parse_dif
from dif.dif_stats import dif_empty_row_count, dif_string_cell_count, dif_total_numeric_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def test_dif_average_column_returns_float(tmp_path):
    path = _dif_file()
    result = average_column(path, 0)
    assert isinstance(result, (int, float))
    record = {"format": "dif", "function": "average_column", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_dif_count_distinct_values_returns_int(tmp_path):
    path = _dif_file()
    result = count_distinct_values(path, 0)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "dif", "function": "count_distinct_values", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_all_numeric_column_returns_bool(tmp_path):
    path = _dif_file()
    result = dif_all_numeric_column(path, 0)
    assert isinstance(result, bool)
    record = {"format": "dif", "function": "dif_all_numeric_column", "all_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["all_numeric"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_empty_row_count_returns_int(tmp_path):
    path = _dif_file()
    doc = parse_dif(path)
    result = dif_empty_row_count(doc)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "dif", "function": "dif_empty_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_string_cell_count_returns_int(tmp_path):
    path = _dif_file()
    doc = parse_dif(path)
    result = dif_string_cell_count(doc)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "dif", "function": "dif_string_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_total_numeric_count_returns_int(tmp_path):
    path = _dif_file()
    doc = parse_dif(path)
    result = dif_total_numeric_count(doc)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "dif", "function": "dif_total_numeric_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
