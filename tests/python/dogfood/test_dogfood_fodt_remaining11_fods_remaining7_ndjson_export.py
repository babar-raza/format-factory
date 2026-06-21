"""
Dogfood pipeline: FODT remaining + FODS remaining -> NDJSON export.
Covers FODT: fodt_all_words_unique, fodt_avg_heading_length, fodt_avg_paragraph_length,
             fodt_avg_run_count, fodt_avg_word_length, fodt_average_paragraph_length
Covers FODS: fods_avg_cell_text_length, fods_avg_row_count, fods_avg_string_cell_length,
             fods_boolean_cell_count, fods_cell_count_variance, fods_cell_type_variety
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
    fodt_all_words_unique,
    fodt_avg_heading_length,
    fodt_avg_paragraph_length,
    fodt_avg_run_count,
    fodt_avg_word_length,
    fodt_average_paragraph_length,
)
from fods import parse_fods
from fods.neutral_model import (
    fods_avg_cell_text_length,
    fods_avg_row_count,
    fods_avg_string_cell_length,
    fods_boolean_cell_count,
    fods_cell_count_variance,
    fods_cell_type_variety,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


# --- FODT ---

def test_fodt_all_words_unique_returns_bool(tmp_path):
    path = _fodt_file()
    result = fodt_all_words_unique(path)
    assert isinstance(result, bool)

    record = {"format": "fodt", "function": "fodt_all_words_unique", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodt_avg_heading_length_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_avg_heading_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_avg_heading_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_avg_paragraph_length_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_avg_paragraph_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_avg_paragraph_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_avg_run_count_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_avg_run_count(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_avg_run_count", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_avg_word_length_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_avg_word_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_avg_word_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_average_paragraph_length_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_average_paragraph_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_average_paragraph_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODS ---

def test_fods_avg_cell_text_length_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_avg_cell_text_length(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_avg_cell_text_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_avg_row_count_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_avg_row_count(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_avg_row_count", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_avg_string_cell_length_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_avg_string_cell_length(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_avg_string_cell_length", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_boolean_cell_count_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_boolean_cell_count(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_boolean_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_cell_count_variance_returns_float(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_cell_count_variance(workbook)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_cell_count_variance", "value": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_cell_type_variety_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_cell_type_variety(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_cell_type_variety", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
