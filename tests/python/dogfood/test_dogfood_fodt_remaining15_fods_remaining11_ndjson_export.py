"""
Dogfood pipeline: FODT remaining + FODS remaining -> NDJSON export.
Covers FODT: fodt_lowercase_ratio, fodt_max_heading_text_length, fodt_min_block_text_length,
             fodt_min_paragraph_text_length, fodt_paragraph_text_sum, fodt_paragraph_to_heading_ratio
Covers FODS: fods_cell_value_variance, fods_nonempty_cell_per_row, fods_nonempty_row_count,
             fods_row_density_avg, fods_sheet_cell_variance, fods_total_string_cell_count
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
    fodt_lowercase_ratio,
    fodt_max_heading_text_length,
    fodt_min_block_text_length,
    fodt_min_paragraph_text_length,
    fodt_paragraph_text_sum,
    fodt_paragraph_to_heading_ratio,
)
from fods import parse_fods
from fods.neutral_model import (
    fods_cell_value_variance,
    fods_nonempty_cell_per_row,
    fods_nonempty_row_count,
    fods_row_density_avg,
    fods_sheet_cell_variance,
    fods_total_string_cell_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


# --- FODT ---

def test_fodt_lowercase_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_lowercase_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fodt", "function": "fodt_lowercase_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fodt_max_heading_text_length_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_max_heading_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_max_heading_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_min_block_text_length_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_min_block_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_min_block_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_min_paragraph_text_length_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_min_paragraph_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_min_paragraph_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_paragraph_text_sum_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_paragraph_text_sum(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_paragraph_text_sum", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_paragraph_to_heading_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_paragraph_to_heading_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_paragraph_to_heading_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODS ---

def test_fods_cell_value_variance_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_cell_value_variance(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_cell_value_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_fods_nonempty_cell_per_row_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_nonempty_cell_per_row(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_nonempty_cell_per_row", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_nonempty_row_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_nonempty_row_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_nonempty_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_row_density_avg_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_row_density_avg(workbook)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_row_density_avg", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["value"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fods_sheet_cell_variance_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_sheet_cell_variance(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_sheet_cell_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert json.dumps(loaded[0]) is not None


def test_fods_total_string_cell_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_total_string_cell_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_total_string_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
