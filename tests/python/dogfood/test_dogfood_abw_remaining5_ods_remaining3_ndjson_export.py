"""
Dogfood pipeline: ABW remaining analytics + ODS remaining analytics → NDJSON export.
Covers ABW: extract_text, get_paragraphs, get_unique_words, count_words, contains_text, first_paragraph
Covers ODS: ods_avg_numeric_value, ods_avg_row_length, ods_cell_density,
            ods_empty_cell_count, ods_empty_row_count, ods_has_empty_rows
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    extract_text,
    get_paragraphs,
    get_unique_words,
    count_words,
    contains_text,
    first_paragraph,
    load as abw_load,
    get_paragraph_count,
)
from ods.ods_analytics import ods_avg_numeric_value, ods_avg_row_length, ods_cell_density, ods_empty_cell_count, ods_empty_row_count, ods_has_empty_rows
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"


def _abw_file():
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if "invalid" not in f.name and get_paragraph_count(str(f)) > 0:
            return str(f)
    for f in sorted(_ABW_DIR.glob("*.abw")):
        if "invalid" not in f.name:
            return str(f)
    return str(next(iter(sorted(_ABW_DIR.glob("*.abw")))))


def _ods_file():
    return str(next(iter(sorted(_ODS_DIR.glob("*.ods")))))


def test_abw_extract_text_returns_list(tmp_path):
    path = _abw_file()
    result = extract_text(path)
    assert isinstance(result, list)

    record = {"format": "abw", "function": "extract_text", "paragraph_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["paragraph_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_get_paragraphs_returns_list(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = get_paragraphs(model)
    assert isinstance(result, list)

    record = {"format": "abw", "function": "get_paragraphs", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_get_unique_words_returns_list(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = get_unique_words(model)
    assert isinstance(result, list)

    record = {"format": "abw", "function": "get_unique_words", "unique_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["unique_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_count_words_returns_int(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = count_words(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "abw", "function": "count_words", "word_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["word_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_abw_contains_text_returns_bool(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = contains_text(model, "hello")
    assert isinstance(result, bool)

    record = {"format": "abw", "function": "contains_text", "found": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["found"], bool)
    assert json.dumps(loaded[0]) is not None


def test_abw_first_paragraph_returns_str(tmp_path):
    path = _abw_file()
    model = abw_load(path)
    result = first_paragraph(model)
    assert isinstance(result, str)

    record = {"format": "abw", "function": "first_paragraph", "length": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_avg_numeric_value_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_numeric_value(path)
    assert isinstance(result, (int, float))

    record = {"format": "ods", "function": "ods_avg_numeric_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["avg"], (int, float))
    assert json.dumps(loaded[0]) is not None


def test_ods_avg_row_length_returns_float(tmp_path):
    path = _ods_file()
    result = ods_avg_row_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_avg_row_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ods_cell_density_returns_float(tmp_path):
    path = _ods_file()
    result = ods_cell_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0

    record = {"format": "ods", "function": "ods_cell_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_ods_empty_cell_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_empty_cell_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_empty_cell_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_empty_row_count_returns_int(tmp_path):
    path = _ods_file()
    result = ods_empty_row_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "ods", "function": "ods_empty_row_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_ods_has_empty_rows_returns_bool(tmp_path):
    path = _ods_file()
    result = ods_has_empty_rows(path)
    assert isinstance(result, bool)

    record = {"format": "ods", "function": "ods_has_empty_rows", "has_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_empty"], bool)
    assert json.dumps(loaded[0]) is not None
