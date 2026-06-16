"""
Dogfood pipeline: FODS remaining + FODT remaining → NDJSON export.
Covers FODS: fods_max_col_count, fods_empty_sheet_count, export_fods_to_csv
Covers FODT: fodt_nonempty_paragraph_count, fodt_char_density, fodt_sentence_count
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods
from fods.neutral_model import fods_max_col_count, fods_empty_sheet_count
from fods.csv_exporter import export_fods_to_csv
from fodt.neutral_model import fodt_nonempty_paragraph_count, fodt_char_density, fodt_sentence_count
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _minimal_fods():
    return str(next(f for f in sorted(_FODS_DIR.glob("*.fods")) if "minimal" in f.name))


def _fodt_with_paragraphs():
    return str(next(f for f in sorted(_FODT_DIR.glob("*.fodt")) if "heading" in f.name or "paragraph" in f.name))


def test_fods_max_col_count_returns_int(tmp_path):
    path = _minimal_fods()
    model = parse_fods(path)
    result = fods_max_col_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_max_col_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_empty_sheet_count_returns_int(tmp_path):
    path = _minimal_fods()
    model = parse_fods(path)
    result = fods_empty_sheet_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_empty_sheet_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_export_fods_to_csv_returns_str(tmp_path):
    path = _minimal_fods()
    model = parse_fods(path)
    result = export_fods_to_csv(model)
    assert isinstance(result, str)
    assert len(result) >= 0

    record = {"format": "fods", "function": "export_fods_to_csv", "length": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["length"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_nonempty_paragraph_count_returns_int(tmp_path):
    path = _fodt_with_paragraphs()
    result = fodt_nonempty_paragraph_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_nonempty_paragraph_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_char_density_returns_float(tmp_path):
    path = _fodt_with_paragraphs()
    result = fodt_char_density(path)
    assert isinstance(result, float)
    assert result >= 0.0

    record = {"format": "fodt", "function": "fodt_char_density", "density": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["density"] >= 0.0
    assert json.dumps(loaded[0]) is not None


def test_fodt_sentence_count_returns_int(tmp_path):
    path = _fodt_with_paragraphs()
    result = fodt_sentence_count(path)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "fodt_sentence_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] >= 0
    assert json.dumps(loaded[0]) is not None
