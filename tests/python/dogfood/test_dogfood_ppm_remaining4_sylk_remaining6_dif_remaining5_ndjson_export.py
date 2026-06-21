"""
Dogfood pipeline: PPM remaining + SYLK remaining + DIF remaining → NDJSON export.
Covers PPM: ppm_min_channel_avg, ppm_pure_color_count, ppm_warm_pixel_count
Covers SYLK: sylk_max_value_count, sylk_nonempty_row_ratio, sylk_numeric_cell_count,
             sylk_numeric_column_count, sylk_numeric_variance, sylk_string_column_count
Covers DIF: dif_has_string_cells, dif_numeric_cell_count, dif_vectors_tuples_sum
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import (
    ppm_min_channel_avg,
    ppm_pure_color_count,
    ppm_warm_pixel_count,
)
from sylk.sylk_parser import (
    sylk_max_value_count,
    sylk_nonempty_row_ratio,
    sylk_numeric_cell_count,
    sylk_numeric_column_count,
    sylk_numeric_variance,
    sylk_string_column_count,
)
from dif.dif_parser import (
    dif_has_string_cells,
    dif_numeric_cell_count,
    dif_vectors_tuples_sum,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _ppm_file():
    return str(next(iter(sorted(_PPM_DIR.glob("*.ppm")))))


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def test_ppm_min_channel_avg_returns_float(tmp_path):
    path = _ppm_file()
    result = ppm_min_channel_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_min_channel_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_pure_color_count_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_pure_color_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_pure_color_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ppm_warm_pixel_count_returns_int(tmp_path):
    path = _ppm_file()
    result = ppm_warm_pixel_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ppm", "function": "ppm_warm_pixel_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_max_value_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_max_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_max_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_nonempty_row_ratio_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_nonempty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "sylk", "function": "sylk_nonempty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_sylk_numeric_cell_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_numeric_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_numeric_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_numeric_column_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_numeric_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_numeric_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_numeric_variance_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_numeric_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_numeric_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_string_column_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_string_column_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_string_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_has_string_cells_returns_bool(tmp_path):
    path = _dif_file()
    result = dif_has_string_cells(path)
    assert isinstance(result, bool)

    record = {"format": "dif", "function": "dif_has_string_cells", "has_string": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_string"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_cell_count_returns_int(tmp_path):
    path = _dif_file()
    result = dif_numeric_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_numeric_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_vectors_tuples_sum_returns_int(tmp_path):
    path = _dif_file()
    result = dif_vectors_tuples_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_vectors_tuples_sum", "total": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["total"] >= 0
    assert json.dumps(loaded[0]) is not None
