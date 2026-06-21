"""
Dogfood pipeline: FODT remaining + FODS remaining -> NDJSON export.
Covers FODT: fodt_block_text_sum, fodt_block_type_count, fodt_char_count,
             fodt_consonant_ratio, fodt_digit_count, fodt_empty_block_count
Covers FODS: fods_column_count_variance, fods_column_density, fods_distinct_value_count,
             fods_empty_row_count, fods_empty_row_ratio, fods_formula_density
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import (
    fodt_block_text_sum,
    fodt_block_type_count,
    fodt_char_count,
    fodt_consonant_ratio,
    fodt_digit_count,
    fodt_empty_block_count,
)
from fods import parse_fods
from fods.neutral_model import (
    fods_column_count_variance,
    fods_column_density,
    fods_distinct_value_count,
    fods_empty_row_count,
    fods_empty_row_ratio,
    fods_formula_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


# --- FODT ---

def test_fodt_block_text_sum_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_block_text_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_block_text_sum", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_block_type_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_block_type_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_block_type_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_char_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_char_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_consonant_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_consonant_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fodt", "function": "fodt_consonant_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fodt_digit_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_digit_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_digit_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_empty_block_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_empty_block_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_empty_block_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODS ---

def test_fods_column_count_variance_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_column_count_variance(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_column_count_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_column_density_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_column_density(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_column_density", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_distinct_value_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_distinct_value_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_distinct_value_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_empty_row_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_empty_row_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_empty_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_empty_row_ratio_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_empty_row_ratio(workbook)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_empty_row_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fods_formula_density_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_formula_density(workbook)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_formula_density", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["value"] <= 1.0
    assert json.dumps(loaded[0]) is not None
