"""
Dogfood pipeline: ODT remaining + Gnumeric remaining → NDJSON export.
Covers ODT: odt_words_per_heading, odt_avg_words_per_sentence, odt_shortest_paragraph_length
Covers Gnumeric: gnumeric_is_empty, gnumeric_max_column_count, gnumeric_avg_cell_length
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import (
    odt_words_per_heading,
    odt_avg_words_per_sentence,
    odt_shortest_paragraph_length,
)
from gnumeric.gnumeric_codec import (
    gnumeric_is_empty,
    gnumeric_max_column_count,
    gnumeric_avg_cell_length,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"
_GN_DIR = _REPO / "samples" / "by-format" / "gnumeric"


def _valid_odt():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def _valid_gnumeric():
    return str(next(f for f in sorted(_GN_DIR.glob("*.gnumeric")) if "minimal" in f.name))


def test_odt_words_per_heading_returns_float(tmp_path):
    path = _valid_odt()
    result = odt_words_per_heading(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "odt", "function": "odt_words_per_heading", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_avg_words_per_sentence_returns_float(tmp_path):
    path = _valid_odt()
    result = odt_avg_words_per_sentence(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "odt", "function": "odt_avg_words_per_sentence", "value": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["value"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_shortest_paragraph_length_returns_int(tmp_path):
    path = _valid_odt()
    result = odt_shortest_paragraph_length(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "odt", "function": "odt_shortest_paragraph_length", "length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_is_empty_returns_bool(tmp_path):
    path = _valid_gnumeric()
    result = gnumeric_is_empty(path)
    assert isinstance(result, bool)
    assert result is False  # minimal-spreadsheet has cells

    record = {"format": "gnumeric", "function": "gnumeric_is_empty", "is_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_empty"] is False
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_max_column_count_returns_int(tmp_path):
    path = _valid_gnumeric()
    result = gnumeric_max_column_count(path)
    assert isinstance(result, int)
    assert result >= 1

    record = {"format": "gnumeric", "function": "gnumeric_max_column_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_gnumeric_avg_cell_length_returns_float(tmp_path):
    path = _valid_gnumeric()
    result = gnumeric_avg_cell_length(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "gnumeric", "function": "gnumeric_avg_cell_length", "avg_length": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg_length"] >= 0.0
    assert json.dumps(loaded[0]) is not None
