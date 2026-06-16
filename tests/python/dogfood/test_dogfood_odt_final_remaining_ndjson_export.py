"""
Dogfood pipeline: ODT final remaining analytics → NDJSON export.
Covers: odt_max_paragraph_length, odt_has_lists, odt_sentence_density,
        odt_table_density, odt_nonempty_paragraph_count, odt_char_density
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import (
    odt_max_paragraph_length,
    odt_has_lists,
    odt_sentence_density,
    odt_table_density,
    odt_nonempty_paragraph_count,
    odt_char_density,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ODT_DIR = _REPO / "samples" / "by-format" / "odt" / "valid"


def _valid_odt_files():
    return sorted(_ODT_DIR.glob("*.odt"))


def test_odt_max_paragraph_length(tmp_path):
    path = str(_valid_odt_files()[0])
    length = odt_max_paragraph_length(path)
    assert isinstance(length, int)
    assert length >= 0

    record = {"format": "odt", "function": "odt_max_paragraph_length", "max_length": length}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["max_length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_has_lists(tmp_path):
    path = str(_valid_odt_files()[0])
    result = odt_has_lists(path)
    assert isinstance(result, bool)

    record = {"format": "odt", "function": "odt_has_lists", "has_lists": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_lists"], bool)
    assert json.dumps(loaded[0]) is not None


def test_odt_sentence_density(tmp_path):
    path = str(_valid_odt_files()[0])
    density = odt_sentence_density(path)
    assert isinstance(density, float)
    assert density >= 0.0

    record = {"format": "odt", "function": "odt_sentence_density", "density": density}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_table_density(tmp_path):
    path = str(_valid_odt_files()[0])
    density = odt_table_density(path)
    assert isinstance(density, float)
    assert density >= 0.0

    record = {"format": "odt", "function": "odt_table_density", "density": density}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_odt_nonempty_paragraph_count(tmp_path):
    path = str(_valid_odt_files()[0])
    count = odt_nonempty_paragraph_count(path)
    assert isinstance(count, int)
    assert count >= 0

    record = {"format": "odt", "function": "odt_nonempty_paragraph_count", "count": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_odt_char_density(tmp_path):
    path = str(_valid_odt_files()[0])
    density = odt_char_density(path)
    assert isinstance(density, float)
    assert density >= 0.0

    record = {"format": "odt", "function": "odt_char_density", "density": density}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None
