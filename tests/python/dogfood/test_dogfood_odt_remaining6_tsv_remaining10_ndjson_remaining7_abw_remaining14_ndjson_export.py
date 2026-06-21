"""
Dogfood pipeline: ODT remaining + TSV remaining + NDJSON remaining + ABW remaining -> NDJSON export.
Covers ODT: odt_numeric_word_count, odt_paragraph_word_variance, odt_unique_word_count, odt_word_count_variance
Covers TSV: tsv_distinct_value_count, tsv_empty_row_ratio, tsv_max_field_length, tsv_numeric_field_sum
Covers NDJSON: ndjson_numeric_field_count, ndjson_string_field_count, ndjson_total_field_count
Covers ABW: abw_avg_sentence_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from odt.odt_parser import (
    odt_numeric_word_count,
    odt_paragraph_word_variance,
    odt_unique_word_count,
    odt_word_count_variance,
)
from src.python.tsv.tsv_parser import (
    tsv_distinct_value_count,
    tsv_empty_row_ratio,
    tsv_max_field_length,
    tsv_numeric_field_sum,
)
from ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    ndjson_numeric_field_count,
    ndjson_string_field_count,
    ndjson_total_field_count,
)
from abw.abw_codec import abw_avg_sentence_length

_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"
_ABW_DIR = _REPO / "samples" / "by-format" / "abw"


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def _tsv_file():
    files = [f for f in sorted(_TSV_DIR.glob("*.tsv")) if "invalid" not in f.name]
    return str(files[0])


def _abw_file():
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


# --- ODT ---

def test_odt_numeric_word_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_numeric_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_numeric_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_paragraph_word_variance_returns_float(tmp_path):
    path = _odt_file()
    result = odt_paragraph_word_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "odt", "function": "odt_paragraph_word_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_unique_word_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_unique_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_unique_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_word_count_variance_returns_float(tmp_path):
    path = _odt_file()
    result = odt_word_count_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "odt", "function": "odt_word_count_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- TSV ---

def test_tsv_distinct_value_count_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_distinct_value_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_distinct_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_empty_row_ratio_returns_float(tmp_path):
    path = _tsv_file()
    result = tsv_empty_row_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "tsv", "function": "tsv_empty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_tsv_max_field_length_returns_int(tmp_path):
    path = _tsv_file()
    result = tsv_max_field_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "tsv", "function": "tsv_max_field_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_tsv_numeric_field_sum_returns_number(tmp_path):
    path = _tsv_file()
    result = tsv_numeric_field_sum(path)
    assert isinstance(result, (int, float))

    record = {"format": "tsv", "function": "tsv_numeric_field_sum", "total": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


# --- NDJSON ---

def test_ndjson_numeric_field_count_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": 1, "b": "hello"}, {"a": 2, "c": 3.14}], str(src))
    result = ndjson_numeric_field_count(str(src))
    assert isinstance(result, int)
    assert result == 3

    record = {"format": "ndjson", "function": "ndjson_numeric_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_string_field_count_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": "x", "b": 2}, {"a": "y", "c": "z"}], str(src))
    result = ndjson_string_field_count(str(src))
    assert isinstance(result, int)
    assert result == 3

    record = {"format": "ndjson", "function": "ndjson_string_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_total_field_count_returns_int(tmp_path):
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": 1, "b": 2}, {"c": 3}], str(src))
    result = ndjson_total_field_count(str(src))
    assert isinstance(result, int)
    assert result == 3

    record = {"format": "ndjson", "function": "ndjson_total_field_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


# --- ABW ---

def test_abw_avg_sentence_length_returns_float(tmp_path):
    path = _abw_file()
    result = abw_avg_sentence_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "abw", "function": "abw_avg_sentence_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None
