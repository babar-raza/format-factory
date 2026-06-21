"""
Dogfood pipeline: DIF remaining + SYLK remaining + Gnumeric remaining +
                  NDJSON remaining + ODT remaining -> NDJSON export.
Covers DIF: dif_min_row_width, dif_string_ratio
Covers SYLK: sylk_has_only_numeric, sylk_row_fill_rate, sylk_unique_cell_value_count, sylk_value_sum
Covers Gnumeric: gnumeric_sheets_with_data, gnumeric_total_numeric_count
Covers NDJSON: ndjson_array_field_count, ndjson_field_type_diversity
Covers ODT: odt_distinct_word_count, odt_empty_paragraph_ratio
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import dif_min_row_width, dif_string_ratio
from sylk.sylk_parser import (
    sylk_has_only_numeric,
    sylk_row_fill_rate,
    sylk_unique_cell_value_count,
    sylk_value_sum,
)
from gnumeric.gnumeric_codec import gnumeric_sheets_with_data, gnumeric_total_numeric_count
from ndjson.ndjson_codec import (
    ndjson_array_field_count,
    ndjson_field_type_diversity,
    write_ndjson,
    load_ndjson,
)
from odt.odt_parser import odt_distinct_word_count, odt_empty_paragraph_ratio

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_GNUMERIC_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _dif_file():
    return str(next(iter(sorted(_DIF_DIR.glob("*.dif")))))


def _sylk_file():
    return str(next(iter(sorted(_SYLK_DIR.glob("*.slk")))))


def _gnumeric_file():
    return str(next(iter(sorted(_GNUMERIC_DIR.glob("*.gnumeric")))))


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def test_dif_min_row_width_returns_int(tmp_path):
    path = _dif_file()
    result = dif_min_row_width(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "dif", "function": "dif_min_row_width", "width": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["width"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_dif_string_ratio_returns_float(tmp_path):
    path = _dif_file()
    result = dif_string_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "dif", "function": "dif_string_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_has_only_numeric_returns_bool(tmp_path):
    path = _sylk_file()
    result = sylk_has_only_numeric(path)
    assert isinstance(result, bool)

    record = {"format": "sylk", "function": "sylk_has_only_numeric", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_sylk_row_fill_rate_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_row_fill_rate(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_row_fill_rate", "rate": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["rate"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_unique_cell_value_count_returns_int(tmp_path):
    path = _sylk_file()
    result = sylk_unique_cell_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "sylk", "function": "sylk_unique_cell_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_sylk_value_sum_returns_float(tmp_path):
    path = _sylk_file()
    result = sylk_value_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "sylk", "function": "sylk_value_sum", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_sheets_with_data_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_sheets_with_data(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_sheets_with_data", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_total_numeric_count_returns_int(tmp_path):
    path = _gnumeric_file()
    result = gnumeric_total_numeric_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "gnumeric", "function": "gnumeric_total_numeric_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_array_field_count_returns_int(tmp_path):
    ndjson_path = tmp_path / "test.ndjson"
    records = [{"a": [1, 2], "b": "text"}, {"a": [3], "b": "more"}]
    write_ndjson(records, str(ndjson_path))

    result = ndjson_array_field_count(str(ndjson_path))
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_array_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_field_type_diversity_returns_int(tmp_path):
    ndjson_path = tmp_path / "test.ndjson"
    records = [{"x": 1, "y": "text", "z": True}, {"x": 2, "y": "more", "z": False}]
    write_ndjson(records, str(ndjson_path))

    result = ndjson_field_type_diversity(str(ndjson_path))
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ndjson", "function": "ndjson_field_type_diversity", "diversity": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["diversity"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_distinct_word_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_distinct_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_distinct_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_empty_paragraph_ratio_returns_float(tmp_path):
    path = _odt_file()
    result = odt_empty_paragraph_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "odt", "function": "odt_empty_paragraph_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None
