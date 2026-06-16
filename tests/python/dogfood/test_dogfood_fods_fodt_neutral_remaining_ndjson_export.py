"""
Dogfood pipeline: FODS neutral remaining + FODT neutral model → NDJSON export.
Covers: fods_data_density, fods_formula_count, fods_has_empty_sheets,
        document_count_tables, document_empty_paragraph_count, document_extract_headings
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods.neutral_model import fods_data_density, fods_formula_count, fods_has_empty_sheets
from fods.parser import parse_fods
from fodt.neutral_model import document_count_tables, document_empty_paragraph_count, document_extract_headings
from fodt.parser import parse_fodt
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODS_DIR = _REPO / "samples" / "by-format" / "fods"
_FODT_DIR = _REPO / "samples" / "by-format" / "fodt"


def _fods_file():
    return str(next(iter(sorted(_FODS_DIR.glob("*.fods")))))


def _fodt_file():
    return str(next(iter(sorted(_FODT_DIR.glob("*.fodt")))))


def test_fods_data_density_returns_float(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_data_density(model)
    assert isinstance(result, (int, float))
    assert 0.0 <= result <= 1.0

    record = {"format": "fods", "function": "fods_data_density", "density": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 0.0 <= loaded[0]["density"] <= 1.0
    assert json.dumps(loaded[0]) is not None


def test_fods_formula_count_returns_int(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_formula_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fods", "function": "fods_formula_count", "formula_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["formula_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fods_has_empty_sheets_returns_bool(tmp_path):
    path = _fods_file()
    model = parse_fods(path)
    result = fods_has_empty_sheets(model)
    assert isinstance(result, bool)

    record = {"format": "fods", "function": "fods_has_empty_sheets", "has_empty": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert isinstance(loaded[0]["has_empty"], bool)
    assert json.dumps(loaded[0]) is not None


def test_fodt_document_count_tables_returns_int(tmp_path):
    path = _fodt_file()
    model = parse_fodt(path)
    result = document_count_tables(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "document_count_tables", "table_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["table_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_document_empty_paragraph_count_returns_int(tmp_path):
    path = _fodt_file()
    model = parse_fodt(path)
    result = document_empty_paragraph_count(model)
    assert isinstance(result, int)
    assert result >= 0

    record = {"format": "fodt", "function": "document_empty_paragraph_count", "empty_para_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["empty_para_count"] >= 0
    assert json.dumps(loaded[0]) is not None


def test_fodt_document_extract_headings_returns_list(tmp_path):
    path = _fodt_file()
    model = parse_fodt(path)
    result = document_extract_headings(model)
    assert isinstance(result, list)

    record = {"format": "fodt", "function": "document_extract_headings", "heading_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["heading_count"] >= 0
    assert json.dumps(loaded[0]) is not None
