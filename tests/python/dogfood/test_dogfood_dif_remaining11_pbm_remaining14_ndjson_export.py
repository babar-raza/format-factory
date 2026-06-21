"""
Dogfood pipeline: DIF remaining + PBM remaining -> NDJSON export.
Covers DIF: dif_numeric_column_count, dif_numeric_sum_per_cell, dif_row_cell_count_avg,
            dif_row_col_ratio, dif_string_length_sum, dif_value_text_total_length, dif_value_variance
Covers PBM: pbm_black_density_variance, pbm_bottom_half_density, pbm_col_black_variance,
            pbm_edge_black_ratio, pbm_grid_density
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_numeric_column_count,
    dif_numeric_sum_per_cell,
    dif_row_cell_count_avg,
    dif_row_col_ratio,
    dif_string_length_sum,
    dif_value_text_total_length,
    dif_value_variance,
)
from pbm.pbm_parser import (
    pbm_black_density_variance,
    pbm_bottom_half_density,
    pbm_col_black_variance,
    pbm_edge_black_ratio,
    pbm_grid_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_PBM_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def _pbm_file():
    return str(next(iter(sorted(_PBM_DIR.glob("*.pbm")))))


# --- DIF ---

def test_dif_numeric_column_count_returns_int(tmp_path):
    path = _dif_file()
    result = dif_numeric_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_numeric_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_sum_per_cell_returns_float(tmp_path):
    path = _dif_file()
    result = dif_numeric_sum_per_cell(path)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "dif_numeric_sum_per_cell", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_dif_row_cell_count_avg_returns_float(tmp_path):
    path = _dif_file()
    result = dif_row_cell_count_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_row_cell_count_avg", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_row_col_ratio_returns_float(tmp_path):
    path = _dif_file()
    result = dif_row_col_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_row_col_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_string_length_sum_returns_int(tmp_path):
    path = _dif_file()
    result = dif_string_length_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_string_length_sum", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_value_text_total_length_returns_int(tmp_path):
    path = _dif_file()
    result = dif_value_text_total_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_value_text_total_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_value_variance_returns_float(tmp_path):
    path = _dif_file()
    result = dif_value_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_value_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- PBM ---

def test_pbm_black_density_variance_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_black_density_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_black_density_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_bottom_half_density_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_bottom_half_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pbm", "function": "pbm_bottom_half_density", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_col_black_variance_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_col_black_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "pbm", "function": "pbm_col_black_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_pbm_edge_black_ratio_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_edge_black_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pbm", "function": "pbm_edge_black_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_pbm_grid_density_returns_float(tmp_path):
    path = _pbm_file()
    result = pbm_grid_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "pbm", "function": "pbm_grid_density", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None
