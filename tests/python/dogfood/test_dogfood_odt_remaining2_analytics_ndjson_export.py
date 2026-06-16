"""
Dogfood pipeline: ODT remaining 2 analytics → NDJSON export.
Covers: get_capabilities, odt_average_word_length, odt_avg_paragraph_length,
        odt_char_count, odt_char_density, odt_empty_paragraph_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import (
    get_capabilities,
    odt_average_word_length,
    odt_avg_paragraph_length,
    odt_char_count,
    odt_char_density,
    odt_empty_paragraph_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _odt_file():
    return str(next(iter(sorted(_ODT_DIR.glob("*.odt")))))


def test_odt_get_capabilities_returns_dict(tmp_path):
    caps = get_capabilities()
    assert isinstance(caps, dict)
    assert caps.get("format") == "odt"
    record = {"format": "odt", "function": "get_capabilities", "gate": caps.get("gate")}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["format"] == "odt"
    assert json.dumps(loaded[0]) is not None


def test_odt_average_word_length_returns_float(tmp_path):
    path = _odt_file()
    result = odt_average_word_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "odt", "function": "odt_average_word_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_avg_paragraph_length_returns_float(tmp_path):
    path = _odt_file()
    result = odt_avg_paragraph_length(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "odt", "function": "odt_avg_paragraph_length", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_char_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_char_count(path)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "odt", "function": "odt_char_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_char_density_returns_float(tmp_path):
    path = _odt_file()
    result = odt_char_density(path)
    assert isinstance(result, (int, float))
    assert result >= 0.0
    record = {"format": "odt", "function": "odt_char_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_empty_paragraph_count_returns_int(tmp_path):
    path = _odt_file()
    result = odt_empty_paragraph_count(path)
    assert isinstance(result, int)
    assert result >= 0
    record = {"format": "odt", "function": "odt_empty_paragraph_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
