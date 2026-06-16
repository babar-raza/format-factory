"""
Dogfood pipeline: FODS remaining analytics + FODT remaining analytics → NDJSON export.
Covers FODS: fods_longest_row_index, fods_numeric_sum_all, fods_empty_column_count,
             fods_max_row_cell_count, fods_formula_cell_count, fods_sheet_row_variance
Covers FODT: fodt_avg_chars_per_word, fodt_heading_ratio, fodt_table_density,
             fodt_total_text_length, fodt_nonempty_paragraph_ratio, fodt_has_numeric_content
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import (
    fods_longest_row_index,
    fods_numeric_sum_all,
    fods_empty_column_count,
    fods_max_row_cell_count,
    fods_formula_cell_count,
    fods_sheet_row_variance,
)
from fods.parser import parse_fods
from fodt.neutral_model import (
    fodt_avg_chars_per_word,
    fodt_heading_ratio,
    fodt_table_density,
    fodt_total_text_length,
    fodt_nonempty_paragraph_ratio,
    fodt_has_numeric_content,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def test_fods_longest_row_index_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_longest_row_index(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_longest_row_index", "index": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["index"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_numeric_sum_all_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_numeric_sum_all(model)
    assert isinstance(result, (int, float))

    record = {"format": "fods", "function": "fods_numeric_sum_all", "sum": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["sum"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_fods_empty_column_count_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_empty_column_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_empty_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_max_row_cell_count_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_max_row_cell_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_max_row_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_formula_cell_count_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_formula_cell_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_formula_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_sheet_row_variance_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_sheet_row_variance(model)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fods", "function": "fods_sheet_row_variance", "variance": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["variance"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_avg_chars_per_word_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_avg_chars_per_word(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_avg_chars_per_word", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_heading_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_heading_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fodt", "function": "fodt_heading_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fodt_table_density_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_table_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_table_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_total_text_length_returns_int(tmp_path):
    path = _fodt_file()
    result = fodt_total_text_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_total_text_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_nonempty_paragraph_ratio_returns_float(tmp_path):
    path = _fodt_file()
    result = fodt_nonempty_paragraph_ratio(path)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fodt", "function": "fodt_nonempty_paragraph_ratio", "ratio": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["ratio"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fodt_has_numeric_content_returns_bool(tmp_path):
    path = _fodt_file()
    result = fodt_has_numeric_content(path)
    assert isinstance(result, bool)

    record = {"format": "fodt", "function": "fodt_has_numeric_content", "has_numeric": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_numeric"], bool)
    assert json.dumps(loaded[0]) is not None
