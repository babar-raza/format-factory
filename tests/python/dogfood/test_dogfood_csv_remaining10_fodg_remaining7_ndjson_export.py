"""
Dogfood pipeline: CSV remaining + FODG remaining -> NDJSON export.
Covers CSV: csv_avg_cell_length, csv_avg_field_text_length, csv_avg_numeric_value,
            csv_column_uniformity, csv_column_value_variance, csv_data_density
Covers FODG: fodg_all_pages_have_shapes, fodg_all_pages_have_text, fodg_avg_shapes_per_page,
             fodg_avg_text_per_page, fodg_empty_page_count, fodg_has_empty_pages
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_avg_cell_length,
    csv_avg_field_text_length,
    csv_avg_numeric_value,
    csv_column_uniformity,
    csv_column_value_variance,
    csv_data_density,
)
from fodg.fodg_codec import (
    fodg_all_pages_have_shapes,
    fodg_all_pages_have_text,
    fodg_avg_shapes_per_page,
    fodg_avg_text_per_page,
    fodg_empty_page_count,
    fodg_has_empty_pages,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_CSV_DIR = _REPO / "samples" / "by-format" / "csv"
_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"


def _csv_file():
    files = [f for f in sorted(_CSV_DIR.glob("*.csv")) if "invalid" not in f.name]
    return str(files[0])


def _fodg_file():
    return str(next(iter(sorted(_FODG_DIR.glob("*.fodg")))))


# --- CSV ---

def test_csv_avg_cell_length_returns_float(tmp_path):
    path = _csv_file()
    result = csv_avg_cell_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_avg_cell_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_avg_field_text_length_returns_float(tmp_path):
    path = _csv_file()
    result = csv_avg_field_text_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_avg_field_text_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_avg_numeric_value_returns_float(tmp_path):
    path = _csv_file()
    result = csv_avg_numeric_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "csv", "function": "csv_avg_numeric_value", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_csv_column_uniformity_returns_float(tmp_path):
    path = _csv_file()
    result = csv_column_uniformity(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_column_uniformity", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_csv_column_value_variance_returns_float(tmp_path):
    path = _csv_file()
    result = csv_column_value_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "csv", "function": "csv_column_value_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_csv_data_density_returns_float(tmp_path):
    path = _csv_file()
    result = csv_data_density(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "csv", "function": "csv_data_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


# --- FODG ---

def test_fodg_all_pages_have_shapes_returns_bool(tmp_path):
    path = _fodg_file()
    result = fodg_all_pages_have_shapes(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_all_pages_have_shapes", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodg_all_pages_have_text_returns_bool(tmp_path):
    path = _fodg_file()
    result = fodg_all_pages_have_text(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_all_pages_have_text", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodg_avg_shapes_per_page_returns_float(tmp_path):
    path = _fodg_file()
    result = fodg_avg_shapes_per_page(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_avg_shapes_per_page", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_avg_text_per_page_returns_float(tmp_path):
    path = _fodg_file()
    result = fodg_avg_text_per_page(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_avg_text_per_page", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_empty_page_count_returns_int(tmp_path):
    path = _fodg_file()
    result = fodg_empty_page_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodg", "function": "fodg_empty_page_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodg_has_empty_pages_returns_bool(tmp_path):
    path = _fodg_file()
    result = fodg_has_empty_pages(path)
    assert isinstance(result, bool)

    record = {"format": "fodg", "function": "fodg_has_empty_pages", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None
