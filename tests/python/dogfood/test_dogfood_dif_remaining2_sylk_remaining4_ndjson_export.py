"""
Dogfood pipeline: DIF remaining analytics + SYLK remaining analytics → NDJSON export.
Covers DIF: dif_tuple_count, dif_is_multi_vector, dif_is_single_vector,
            dif_vector_length_variance, dif_numeric_sum, dif_is_single_row
Covers SYLK: sylk_is_multi_row, sylk_is_single_column, sylk_cell_count_variance,
             sylk_avg_cell_length, sylk_column_span, sylk_numeric_sum
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_tuple_count,
    dif_is_multi_vector,
    dif_is_single_vector,
    dif_vector_length_variance,
    dif_numeric_sum,
    dif_is_single_row,
)
from sylk.sylk_analytics import sylk_is_multi_row, sylk_is_single_column, sylk_cell_count_variance, sylk_avg_cell_length, sylk_column_span, sylk_numeric_sum
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def test_dif_tuple_count_returns_int(tmp_path):
    path = _dif_file()
    result = dif_tuple_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_tuple_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_is_multi_vector_returns_bool(tmp_path):
    path = _dif_file()
    result = dif_is_multi_vector(path)
    assert isinstance(result, bool)

    record = {"format": "dif", "function": "dif_is_multi_vector", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_is_single_vector_returns_bool(tmp_path):
    path = _dif_file()
    result = dif_is_single_vector(path)
    assert isinstance(result, bool)

    record = {"format": "dif", "function": "dif_is_single_vector", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_vector_length_variance_returns_float(tmp_path):
    path = _dif_file()
    result = dif_vector_length_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_vector_length_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_sum_returns_float(tmp_path):
    path = _dif_file()
    result = dif_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "dif_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_dif_is_single_row_returns_bool(tmp_path):
    path = _dif_file()
    result = dif_is_single_row(path)
    assert isinstance(result, bool)

    record = {"format": "dif", "function": "dif_is_single_row", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_is_multi_row_returns_bool(tmp_path):
    path = _sylk_file()
    result = sylk_is_multi_row(path)
    assert isinstance(result, bool)

    record = {"format": "sylk", "function": "sylk_is_multi_row", "is_multi": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_multi"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_is_single_column_returns_bool(tmp_path):
    path = _sylk_file()
    result = sylk_is_single_column(path)
    assert isinstance(result, bool)

    record = {"format": "sylk", "function": "sylk_is_single_column", "is_single": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_cell_count_variance_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_cell_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_cell_count_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_avg_cell_length_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_avg_cell_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_avg_cell_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_column_span_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_column_span(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_column_span", "span": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["span"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_numeric_sum_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_numeric_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "sylk", "function": "sylk_numeric_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None
