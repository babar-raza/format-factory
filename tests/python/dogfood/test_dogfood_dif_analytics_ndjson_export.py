"""
Dogfood pipeline: DIF analytics → NDJSON export.
Covers: dif_is_rectangular, dif_data_density, dif_avg_cell_length,
        dif_is_single_column, dif_max_string_length, dif_all_numeric_column
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_is_rectangular,
    dif_data_density,
    dif_avg_cell_length,
    dif_is_single_column,
    dif_max_string_length,
    dif_all_numeric_column,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"


def _valid_dif_files():
    return sorted(_DIF_DIR.glob("*.dif"))


def test_dif_is_rectangular(tmp_path):
    path = str(_valid_dif_files()[0])
    result = dif_is_rectangular(path)
    assert isinstance(result, bool)
    assert result is True  # standard DIF files are rectangular

    record = {"format": "dif", "function": "dif_is_rectangular", "is_rectangular": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_rectangular"] is True
    assert json.dumps(loaded[0]) is not None


def test_dif_data_density(tmp_path):
    path = str(_valid_dif_files()[0])
    density = dif_data_density(path)
    assert isinstance(density, float)
    assert 0.0 <= density <= 1.0

    record = {"format": "dif", "function": "dif_data_density", "density": density}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_dif_avg_cell_length(tmp_path):
    path = str(_valid_dif_files()[0])
    avg = dif_avg_cell_length(path)
    assert isinstance(avg, float)
    assert avg >= 0.0

    record = {"format": "dif", "function": "dif_avg_cell_length", "avg": avg}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_dif_is_single_column(tmp_path):
    path = str(_valid_dif_files()[0])
    result = dif_is_single_column(path)
    assert isinstance(result, bool)

    record = {"format": "dif", "function": "dif_is_single_column", "is_single_column": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["is_single_column"], bool)
    assert json.dumps(loaded[0]) is not None


def test_dif_max_string_length(tmp_path):
    # Use minimal-2x2.dif which has string cells
    dif_files = _valid_dif_files()
    path = str(next(f for f in dif_files if "minimal" in f.name))
    length = dif_max_string_length(path)
    assert isinstance(length, int)
    assert length >= 0

    record = {"format": "dif", "function": "dif_max_string_length", "max_length": length}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["max_length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_all_numeric_column(tmp_path):
    # Use numeric-row.dif which has all numeric data
    dif_files = _valid_dif_files()
    path = str(next(f for f in dif_files if "numeric" in f.name))
    result = dif_all_numeric_column(path, 0)
    assert isinstance(result, bool)
    assert result is True  # numeric-row.dif column 0 is all numeric

    record = {"format": "dif", "function": "dif_all_numeric_column", "col": 0, "is_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_numeric"] is True
    assert json.dumps(loaded[0]) is not None
