"""
Dogfood pipeline: FODS remaining + FODT remaining + ODT remaining -> NDJSON export.
Covers FODS: fods_cells_per_sheet_avg, fods_is_fully_numeric, fods_max_column_index
Covers FODT: fodt_avg_block_length, fodt_char_per_word, fodt_heading_word_ratio,
             fodt_inline_count, fodt_list_item_count, fodt_max_block_text_length,
             fodt_paragraph_variance, fodt_punctuation_density
Covers ODT: odt_total_word_count
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods
from fods.neutral_model import (
    fods_cells_per_sheet_avg,
    fods_is_fully_numeric,
    fods_max_column_index,
)
from fodt.neutral_model import (
    fodt_avg_block_length,
    fodt_char_per_word,
    fodt_heading_word_ratio,
    fodt_inline_count,
    fodt_list_item_count,
    fodt_max_block_text_length,
    fodt_paragraph_variance,
    fodt_punctuation_density,
)
from odt.odt_parser import odt_total_word_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


# --- FODS ---

def test_fods_cells_per_sheet_avg_returns_float(tmp_path):
    path = _fods_file()
    result = fods_cells_per_sheet_avg(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_cells_per_sheet_avg", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_is_fully_numeric_returns_bool(tmp_path):
    path = _fods_file()
    result = fods_is_fully_numeric(path)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_is_fully_numeric", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_max_column_index_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_max_column_index(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_max_column_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["index"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- FODT ---

def test_fodt_avg_block_length_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_avg_block_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_avg_block_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_char_per_word_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_char_per_word(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_char_per_word", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_heading_word_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_heading_word_ratio(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_heading_word_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["ratio"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_inline_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_inline_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_inline_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_list_item_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_list_item_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_list_item_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_max_block_text_length_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_max_block_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_max_block_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_paragraph_variance_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_paragraph_variance(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_paragraph_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_punctuation_density_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_punctuation_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_punctuation_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


# --- ODT ---

def test_odt_total_word_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_total_word_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_total_word_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
