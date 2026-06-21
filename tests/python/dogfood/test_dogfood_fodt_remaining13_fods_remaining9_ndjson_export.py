"""
Dogfood pipeline: FODT remaining + FODS remaining -> NDJSON export.
Covers FODT: fodt_empty_paragraph_count, fodt_file_size_bytes, fodt_has_lists,
             fodt_has_more_words_than_unique, fodt_has_multiple_block_types, fodt_has_tables
Covers FODS: fods_has_formulas, fods_has_numeric_cells, fods_has_only_one_column,
             fods_is_all_string, fods_is_single_sheet, fods_max_cell_length
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
    fodt_empty_paragraph_count,
    fodt_file_size_bytes,
    fodt_has_lists,
    fodt_has_more_words_than_unique,
    fodt_has_multiple_block_types,
    fodt_has_tables,
)
from fods import parse_fods
from fods.neutral_model import (
    fods_has_formulas,
    fods_has_numeric_cells,
    fods_has_only_one_column,
    fods_is_all_string,
    fods_is_single_sheet,
    fods_max_cell_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"
_FODS_DIR = _REPO / "samples" / "by-format" / "fods"


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


# --- FODT ---

def test_fodt_empty_paragraph_count_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_empty_paragraph_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_empty_paragraph_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_file_size_bytes_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_file_size_bytes(path)
    assert isinstance(result, int)
    assert result > 0

    record = {"format": "fodt", "function": "fodt_file_size_bytes", "size": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["size"] > 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_has_lists_returns_bool(tmp_path):
    path = _fodt_file()
    result = fodt_has_lists(path)
    assert isinstance(result, bool)

    record = {"format": "fodt", "function": "fodt_has_lists", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodt_has_more_words_than_unique_returns_bool(tmp_path):
    path = _fodt_file()
    result = fodt_has_more_words_than_unique(path)
    assert isinstance(result, bool)

    record = {"format": "fodt", "function": "fodt_has_more_words_than_unique", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodt_has_multiple_block_types_returns_bool(tmp_path):
    path = _fodt_file()
    result = fodt_has_multiple_block_types(path)
    assert isinstance(result, bool)

    record = {"format": "fodt", "function": "fodt_has_multiple_block_types", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodt_has_tables_returns_bool(tmp_path):
    path = _fodt_file()
    result = fodt_has_tables(path)
    assert isinstance(result, bool)

    record = {"format": "fodt", "function": "fodt_has_tables", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


# --- FODS ---

def test_fods_has_formulas_returns_bool(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_has_formulas(workbook)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_has_formulas", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_has_numeric_cells_returns_bool(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_has_numeric_cells(workbook)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_has_numeric_cells", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_has_only_one_column_returns_bool(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_has_only_one_column(workbook)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_has_only_one_column", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_is_all_string_returns_bool(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_is_all_string(workbook)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_is_all_string", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_is_single_sheet_returns_bool(tmp_path):
    path = _fods_file()
    result = fods_is_single_sheet(os.path.abspath(path))
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_is_single_sheet", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["value"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fods_max_cell_length_returns_int(tmp_path):
    path = _fods_file()
    workbook = parse_fods(os.path.abspath(path))
    result = fods_max_cell_length(workbook)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_max_cell_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None
