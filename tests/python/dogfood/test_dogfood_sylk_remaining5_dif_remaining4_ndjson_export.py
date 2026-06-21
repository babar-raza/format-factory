"""
Dogfood pipeline: SYLK remaining analytics + DIF remaining analytics → NDJSON export.
Covers SYLK: sylk_avg_cell_length_per_row, sylk_empty_cell_count, sylk_first_row_cell_count,
             sylk_has_empty_cells, sylk_max_cells_in_col, sylk_max_row_cell_count
Covers DIF: dif_max_numeric_length, dif_max_row_index, dif_min_column_sum,
            dif_min_row_index, dif_string_cell_ratio, dif_value_type_variance
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    sylk_avg_cell_length_per_row,
    sylk_empty_cell_count,
    sylk_first_row_cell_count,
    sylk_has_empty_cells,
    sylk_max_cells_in_col,
    sylk_max_row_cell_count,
)
from dif.dif_parser import (
    dif_max_numeric_length,
    dif_max_row_index,
    dif_min_column_sum,
    dif_min_row_index,
    dif_string_cell_ratio,
    dif_value_type_variance,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def test_sylk_avg_cell_length_per_row_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_avg_cell_length_per_row(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_avg_cell_length_per_row", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_empty_cell_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_empty_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_empty_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_first_row_cell_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_first_row_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_first_row_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_has_empty_cells_returns_bool(tmp_path):
    path = _sylk_file()
    result = sylk_has_empty_cells(path)
    assert isinstance(result, bool)

    record = {"format": "sylk", "function": "sylk_has_empty_cells", "has_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_empty"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_max_cells_in_col_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_max_cells_in_col(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_max_cells_in_col", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_max_row_cell_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_max_row_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_max_row_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_max_numeric_length_returns_int(tmp_path):
    path = _dif_file()
    result = dif_max_numeric_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_max_numeric_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_max_row_index_returns_int(tmp_path):
    path = _dif_file()
    result = dif_max_row_index(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_max_row_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["index"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_min_column_sum_returns_float(tmp_path):
    path = _dif_file()
    result = dif_min_column_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "dif_min_column_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_dif_min_row_index_returns_int(tmp_path):
    path = _dif_file()
    result = dif_min_row_index(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_min_row_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["index"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_string_cell_ratio_returns_float(tmp_path):
    path = _dif_file()
    result = dif_string_cell_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_string_cell_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_value_type_variance_returns_float(tmp_path):
    path = _dif_file()
    result = dif_value_type_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_value_type_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None
