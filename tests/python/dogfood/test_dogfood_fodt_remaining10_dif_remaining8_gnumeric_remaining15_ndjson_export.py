"""
Dogfood pipeline: FODT remaining + DIF remaining + Gnumeric remaining -> NDJSON export.
Covers FODT: fodt_total_character_count
Covers DIF: dif_avg_string_length, dif_empty_row_ratio, dif_numeric_cell_sum,
            dif_numeric_ratio, dif_total_cell_value_count, dif_value_sum
Covers Gnumeric: gnumeric_cell_density_variance, gnumeric_formula_count, gnumeric_has_formula_cells,
                 gnumeric_max_col_index, gnumeric_max_row_index
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_total_character_count
from dif.dif_parser import (
    dif_avg_string_length,
    dif_empty_row_ratio,
    dif_numeric_cell_sum,
    dif_numeric_ratio,
    dif_total_cell_value_count,
    dif_value_sum,
)
from gnumeric.gnumeric_codec import (
    gnumeric_cell_density_variance,
    gnumeric_formula_count,
    gnumeric_has_formula_cells,
    gnumeric_max_col_index,
    gnumeric_max_row_index,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


# --- FODT ---

def test_fodt_total_character_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_total_character_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_total_character_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- DIF ---

def test_dif_avg_string_length_returns_float(tmp_path):
    path = _dif_file()
    result = dif_avg_string_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_avg_string_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_empty_row_ratio_returns_float(tmp_path):
    path = _dif_file()
    result = dif_empty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "dif", "function": "dif_empty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_cell_sum_returns_float(tmp_path):
    path = _dif_file()
    result = dif_numeric_cell_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "dif_numeric_cell_sum", "total": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_dif_numeric_ratio_returns_float(tmp_path):
    path = _dif_file()
    result = dif_numeric_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "dif", "function": "dif_numeric_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_dif_total_cell_value_count_returns_int(tmp_path):
    path = _dif_file()
    result = dif_total_cell_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_total_cell_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_value_sum_returns_float(tmp_path):
    path = _dif_file()
    result = dif_value_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "dif", "function": "dif_value_sum", "total": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


# --- Gnumeric ---

def test_gnumeric_cell_density_variance_returns_float(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_cell_density_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_cell_density_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_formula_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_formula_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_formula_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_has_formula_cells_returns_bool(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_has_formula_cells(path)
    assert isinstance(result, bool)

    record = {"format": "gnumeric", "function": "gnumeric_has_formula_cells", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_max_col_index_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_max_col_index(path)
    assert isinstance(result, int)

    record = {"format": "gnumeric", "function": "gnumeric_max_col_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["index"], int)
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_max_row_index_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_max_row_index(path)
    assert isinstance(result, int)

    record = {"format": "gnumeric", "function": "gnumeric_max_row_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["index"], int)
    assert json.dumps(loaded[0]) is not None
